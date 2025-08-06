#!/bin/bash

# ==============================================================================
#
# 自动启用所有GCP项目Gemini相关API脚本
#
# - 该脚本会自动查找您账户下的所有GCP项目，并为它们启用以下API:
#   - generativelanguage.googleapis.com
#   - geminicloudassist.googleapis.com
#   - cloudaicompanion.googleapis.com
#
# - 用法:
#   - 直接运行: ./enable_gemini_apis.sh
#   - 脚本将全自动执行，无需任何参数。
#
# ==============================================================================

# ===== 全局配置 =====
MAX_RETRY_ATTEMPTS=3
MAX_PARALLEL_JOBS=4

# ===== 工具函数 =====

# 统一日志函数
log() {
    local level="$1"
    local msg="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $msg"
}

# 改进的重试函数
retry_with_backoff() {
    local max_attempts=$1; shift; local cmd_str="$1"; local attempt=1; local base_timeout=5
    while (( attempt <= max_attempts )); do
        local output; local error_msg;
        exec 3>&1
        error_msg=$({ output=$(eval "$cmd_str" 2>&1 >&3); } 2>&1)
        exec 3>&-
        local exit_code=$?
        if (( exit_code == 0 )); then echo "$output"; return 0; fi
        log "WARN" "命令失败 (尝试 $attempt/$max_attempts): $(echo "$cmd_str" | cut -d' ' -f1-4)..."
        log "WARN" "--> 错误详情: $error_msg"
        if [[ "$error_msg" == *"Permission denied"* || "$error_msg" == *"INVALID_ARGUMENT"* || "$error_msg" == *"already exists"* ]]; then
            log "ERROR" "检测到不可重试错误，停止。"; return $exit_code;
        fi
        if [[ "$error_msg" == *"Quota exceeded"* || "$error_msg" == *"RESOURCE_EXHAUSTED"* ]]; then
            local sleep_time=$((base_timeout * attempt * 2)); log "WARN" "检测到配额限制，等待 ${sleep_time}s"; sleep "$sleep_time"
        elif (( attempt < max_attempts )); then
            local sleep_time=$((base_timeout * attempt)); log "INFO" "等待 ${sleep_time}s 后重试..."; sleep "$sleep_time"
        fi
        ((attempt++))
    done
    log "ERROR" "命令在 $max_attempts 次尝试后最终失败: $cmd_str"; return 1
}

# 启用API的任务函数
task_enable_api() {
    local project_id="$1"
    local success_file="$2"
    log "INFO" "--------------------------------------------------"
    log "INFO" "正在为项目 '$project_id' 启用API..."
    local result_output
    if result_output=$(retry_with_backoff "$MAX_RETRY_ATTEMPTS" "gcloud services enable generativelanguage.googleapis.com geminicloudassist.googleapis.com cloudaicompanion.googleapis.com --project=\"$project_id\" --quiet"); then
        log "INFO" "成功为项目 '$project_id' 启用API。"
        if [[ -n "$result_output" ]]; then
            log "DEBUG" "gcloud命令输出: $result_output"
        fi
        # 将成功结果写入文件
        (flock 200; echo "$project_id" >> "$success_file") 200>"${success_file}.lock"
        return 0
    else
        log "ERROR" "为项目 '$project_id' 启用API失败。详细错误已在上方日志中显示。"
        return 1
    fi
}

# 检查先决条件
check_prerequisites() {
    log "INFO" "执行前置检查...";
    if ! command -v gcloud > /dev/null; then
        log "ERROR" "未找到 'gcloud' 命令。请确保gcloud SDK已安装并位于您的PATH中。"
        return 1
    fi
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "."; then
        log "WARN" "未检测到活跃GCP账号，将尝试自动登录..."
        gcloud auth login || return 1
    fi
    local current_account
    current_account=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -n1)
    log "INFO" "前置检查通过。当前活跃账号: $current_account";
    return 0
}

# ===== 程序入口 =====
main() {
    if ! check_prerequisites; then
        log "ERROR" "前置检查失败，程序退出。"
        exit 1
    fi

    log "INFO" "正在获取所有项目列表并自动启用API..."
    local project_list
    project_list=$(gcloud projects list --format='value(projectId)' --filter='projectId!~^sys-' --quiet)
    if [ -z "$project_list" ]; then
        log "INFO" "未找到任何用户项目可供操作。"
        exit 0
    fi

    local ALL_PROJECT_IDS
    readarray -t ALL_PROJECT_IDS <<< "$project_list"
    local total_projects=${#ALL_PROJECT_IDS[@]}

    local TEMP_DIR="/tmp/gcp_script_$(date +%s)"
    mkdir -p "$TEMP_DIR"
    local SUCCESS_FILE="${TEMP_DIR}/success.txt"
    > "$SUCCESS_FILE"

    # 导出函数和变量，以便在子shell中可用
    export -f log retry_with_backoff task_enable_api
    export MAX_RETRY_ATTEMPTS

    echo
    log "INFO" "将为找到的 $total_projects 个项目自动启用API (并发数: $MAX_PARALLEL_JOBS)。"
    log "INFO" "3秒后开始执行... (按 Ctrl+C 取消)"
    sleep 3

    local pids=()
    for project_id in "${ALL_PROJECT_IDS[@]}"; do
        if (( ${#pids[@]} >= MAX_PARALLEL_JOBS )); then
            wait -n "${pids[@]}"
            # 清理已完成的进程ID
            local new_pids=()
            for pid in "${pids[@]}"; do
                if kill -0 "$pid" 2>/dev/null; then
                    new_pids+=("$pid")
                fi
            done
            pids=("${new_pids[@]}")
        fi
        ( task_enable_api "$project_id" "$SUCCESS_FILE" ) & pids+=($!)
    done

    # 等待所有剩余的后台作业完成
    wait "${pids[@]}"

    local success_ids=()
    if [ -f "$SUCCESS_FILE" ]; then
        mapfile -t success_ids < "$SUCCESS_FILE"
    fi
    
    local success_count=${#success_ids[@]}
    local failed_count=$((total_projects - success_count))
    
    # 找出失败的项目
    local failed_projects=()
    local success_map=()
    for id in "${success_ids[@]}"; do success_map["$id"]=1; done
    for id in "${ALL_PROJECT_IDS[@]}"; do
        if [[ -z "${success_map[$id]}" ]]; then
            failed_projects+=("$id")
        fi
    done

    echo
    log "INFO" "==================== 执行完毕 ===================="
    log "INFO" "总共处理项目数: $total_projects"
    log "INFO" "成功启用API的项目数: $success_count"
    log "INFO" "失败的项目数: $failed_count"
    if [ $failed_count -gt 0 ]; then
        log "ERROR" "以下项目启用API失败:"
        for project_id in "${failed_projects[@]}"; do
            log "ERROR" "  - $project_id"
        done
    fi
    log "INFO" "=================================================="
    
    # 清理临时文件
    rm -rf "$TEMP_DIR"
}

main "$@"
