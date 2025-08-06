#!/bin/bash

# ==============================================================================
#
# GCP 项目创建脚本 v1.0
#
# - 该脚本用于批量创建GCP项目，项目名称随机生成。
# - 基于 密钥管理器修改版 v1.3
# - 作者: momo & ddddd1996 & KKTsN & Cline
#
# ==============================================================================

# ===== 全局配置 =====
TIMESTAMP=$(date +%s)
RANDOM_CHARS=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 4 | head -n 1)
EMAIL_USERNAME="${RANDOM_CHARS}${TIMESTAMP:(-4)}"
# 生成随机的项目前缀
RANDOM_PREFIX_PART=$(cat /dev/urandom | tr -dc 'a-z' | fold -w 5 | head -n 1)
RANDOM_SUFFIX_PART=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 3 | head -n 1)
PROJECT_PREFIX="${RANDOM_PREFIX_PART}Vul${RANDOM_SUFFIX_PART}"
TOTAL_PROJECTS=75
MAX_PARALLEL_JOBS=40
MAX_RETRY_ATTEMPTS=3
SECONDS=0

# 文件和目录配置
TEMP_DIR="/tmp/gcp_script_${TIMESTAMP}"

# 启动时创建临时目录
mkdir -p "$TEMP_DIR"

# ===== 工具函数 =====

# 统一日志函数
log() {
    local level="$1"
    local msg="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $msg" | tee -a "${TEMP_DIR}/script.log"
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


# 进度条显示函数
show_progress() {
    local completed=$1; local total=$2; local op_name=${3:-"进度"}
    if (( total <= 0 )); then return; fi; if (( completed > total )); then completed=$total; fi
    local percent=$((completed * 100 / total)); local bar_len=40
    local filled_len=$((bar_len * percent / 100)); local bar; printf -v bar '%*s' "$filled_len" ''; bar=${bar// /█}
    local empty; printf -v empty '%*s' "$((bar_len - filled_len))" ''; empty=${empty// /░}
    printf "\r%-80s" " "; printf "\r[%s%s] %d%% (%d/%d) - %s" "$bar" "$empty" "$percent" "$completed" "$total" "$op_name"
}

# ===== 任务函数 =====

task_create_project() {
    local project_id="$1"; local success_file="$2"
    if retry_with_backoff "$MAX_RETRY_ATTEMPTS" "gcloud projects create \"$project_id\" --name=\"$project_id\" --no-set-as-default --quiet"; then
        (flock 200; echo "$project_id" >> "$success_file";) 200>"${success_file}.lock"; return 0
    else return 1; fi
}

cleanup_resources() {
    log "INFO" "执行退出清理..."; pkill -P $$ &>/dev/null; rm -rf "$TEMP_DIR";
}

# ===== 并行执行 =====

run_parallel() {
    local task_func="$1"; local description="$2"; local success_file="$3"; shift 3; local items=("$@"); local total_items=${#items[@]}
    if (( total_items == 0 )); then log "INFO" "在 '$description' 阶段无项目处理。"; return; fi
    log "INFO" "开始并行执行 '$description' (最大并发: $MAX_PARALLEL_JOBS)..."
    local pids=(); local completed_count=0
    export -f log retry_with_backoff "$task_func" show_progress; export MAX_RETRY_ATTEMPTS TEMP_DIR
    > "$success_file"
    for i in "${!items[@]}"; do
        if (( ${#pids[@]} >= MAX_PARALLEL_JOBS )); then
            wait -n "${pids[@]}"; for j in "${!pids[@]}"; do if ! kill -0 "${pids[j]}" 2>/dev/null; then unset 'pids[j]'; ((completed_count++)); fi; done
            show_progress "$completed_count" "$total_items" "$description"
        fi
        ( "$task_func" "${items[i]}" "$success_file" ) & pids+=($!)
    done
    for pid in "${pids[@]}"; do wait "$pid"; ((completed_count++)); show_progress "$completed_count" "$total_items" "$description"; done
    wait; show_progress "$total_items" "$total_items" "$description 完成"
    local success_count; success_count=$(wc -l < "$success_file" | xargs); local fail_count=$((total_items - success_count))
    echo; log "INFO" "阶段 '$description' 完成。总数: $total_items, 成功: $success_count, 失败: $fail_count"
}

# ===== 主功能函数 =====

create_projects_only() {
    SECONDS=0
    log "INFO" "======================================================"
    log "INFO" "功能: 仅创建项目（不提取API密钥）"
    log "INFO" "======================================================"
    log "INFO" "使用随机生成的用户名: ${EMAIL_USERNAME}"
    
    # 询问要创建的项目数量
    read -p "请输入要创建的项目数量 (1-75，默认为$TOTAL_PROJECTS): " custom_count
    custom_count=${custom_count:-$TOTAL_PROJECTS}
    
    if ! [[ "$custom_count" =~ ^[1-9][0-9]*$ ]] || [ "$custom_count" -gt 75 ]; then
        log "ERROR" "无效的项目数量。请输入1-75之间的数字。"
        return 1
    fi
    
    log "INFO" "将创建 $custom_count 个项目"
    log "INFO" "在 3 秒后开始执行..."; sleep 3
    
    local projects_to_create=()
    for i in $(seq 1 $custom_count); do
        local project_num=$(printf "%03d" $i)
        local base_id="${PROJECT_PREFIX}-${EMAIL_USERNAME}-${project_num}"
        local project_id=$(echo "$base_id" | tr -cd 'a-z0-9-' | cut -c 1-30 | sed 's/-$//')
        if ! [[ "$project_id" =~ ^[a-z] ]]; then
            project_id="g${project_id:1}"
            project_id=$(echo "$project_id" | cut -c 1-30 | sed 's/-$//')
        fi
        projects_to_create+=("$project_id")
    done
    
    # 创建项目
    local CREATED_PROJECTS_FILE="${TEMP_DIR}/created_projects_only.txt"
    > "$CREATED_PROJECTS_FILE"
    
    export -f task_create_project log retry_with_backoff
    export TEMP_DIR MAX_RETRY_ATTEMPTS
    
    run_parallel task_create_project "创建项目" "$CREATED_PROJECTS_FILE" "${projects_to_create[@]}"
    
    local created_project_ids=()
    if [ -f "$CREATED_PROJECTS_FILE" ]; then
        mapfile -t created_project_ids < "$CREATED_PROJECTS_FILE"
    fi
    
    local success_count=${#created_project_ids[@]}
    local failed_count=$((custom_count - success_count))
    
    # 生成报告
    echo ""
    echo "========== 创建项目报告 =========="
    echo "计划创建: $custom_count 个项目"
    echo "成功创建: $success_count 个项目"
    echo "创建失败: $failed_count 个项目"
    
    if [ $success_count -gt 0 ]; then
        echo ""
        echo "成功创建的项目ID:"
        for project_id in "${created_project_ids[@]}"; do
            echo "  - $project_id"
        done
    fi
    
    echo "=========================="
    
    log "INFO" "======================================================"
    log "INFO" "项目创建完成。"
    log "INFO" "======================================================"
}

check_prerequisites() {
    log "INFO" "执行前置检查..."; if ! command -v gcloud &> /dev/null; then log "ERROR" "未找到 'gcloud' 命令。请确保GCloud SDK已安装并位于您的PATH中。"; return 1; fi
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "."; then log "WARN" "未检测到活跃GCP账号，请先登录。"; gcloud auth login || return 1; fi
    log "INFO" "前置检查通过。"; return 0
}

# ===== 程序入口 =====
trap cleanup_resources EXIT SIGINT SIGTERM
if ! check_prerequisites; then 
    log "ERROR" "前置检查失败，程序退出。"
    exit 1
fi

create_projects_only

log "INFO" "脚本执行完毕。"
exit 0
