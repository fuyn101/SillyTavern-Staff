#!/bin/bash

# ==============================================================================
#
# GCP 项目 API 密钥清理脚本 v1.0
#
# - 该脚本用于删除所有GCP项目中创建的API密钥。
# - 基于原始密钥管理器脚本提取。
#
# ==============================================================================

# ===== 全局配置 =====
TIMESTAMP=$(date +%s)
MAX_PARALLEL_JOBS=40
MAX_RETRY_ATTEMPTS=3
SECONDS=0

# 文件和目录配置
CLEANUP_LOG="api_keys_cleanup_$(date +%Y%m%d_%H%M%S).log"
TEMP_DIR="/tmp/gcp_script_cleanup_${TIMESTAMP}"
HEARTBEAT_PID=""

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

# 心跳机制
start_heartbeat() {
    local message="$1"
    local interval="${2:-20}"
    stop_heartbeat
    (
        while true; do
            log "HEARTBEAT" "${message:-"操作进行中，请耐心等待..."}"
            sleep "$interval"
        done
    ) &
    HEARTBEAT_PID=$!
}

stop_heartbeat() {
    if [[ -n "$HEARTBEAT_PID" && -e /proc/$HEARTBEAT_PID ]]; then
        kill "$HEARTBEAT_PID" 2>/dev/null
        wait "$HEARTBEAT_PID" 2>/dev/null || true
    fi
    HEARTBEAT_PID=""
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

generate_report() {
    local success=$1 failed=$2 total=$3 operation=${4:-"处理"}; local success_rate=0
    if (( total > 0 )); then success_rate=$(awk "BEGIN {printf \"%.2f\", $success * 100 / $total}"); fi
    local duration=$SECONDS h=$((duration/3600)) m=$(((duration%3600)/60)) s=$((duration%60))
    echo; echo "======================== 执 行 报 告 ========================";
    printf "  操作类型    : %s\n" "$operation"; printf "  总计尝试    : %d\n" "$total"; printf "  成功数量    : %d\n" "$success";
    printf "  失败数量    : %d\n" "$failed"; printf "  成功率      : %.2f%%\n" "$success_rate"; printf "  总执行时间  : %d小时 %d分钟 %d秒\n" "$h" "$m" "$s"
    echo "================================================================"
}

# ===== 健壮的任务函数 =====

task_cleanup_keys() {
    local project_id="$1"; local success_file="$2"; local key_names; readarray -t key_names < <(gcloud services api-keys list --project="$project_id" --format="value(name)" --quiet)
    if [ ${#key_names[@]} -eq 0 ]; then
        (flock 200; echo "$project_id" >> "$success_file";) 200>"${success_file}.lock"; return 0
    fi
    local all_success=true
    for key_name in "${key_names[@]}"; do
        if ! retry_with_backoff 2 "gcloud services api-keys delete \"$key_name\" --quiet"; then all_success=false; fi
        sleep 0.5
    done
    if $all_success; then (flock 200; echo "$project_id" >> "$success_file";) 200>"${success_file}.lock"; return 0; else return 1; fi
}

cleanup_resources() {
    log "INFO" "执行退出清理..."; stop_heartbeat; pkill -P $$ &>/dev/null; rm -rf "$TEMP_DIR";
}

# ===== 并行执行与报告 =====

run_parallel() {
    local task_func="$1"; local description="$2"; local success_file="$3"; shift 3; local items=("$@"); local total_items=${#items[@]}
    if (( total_items == 0 )); then log "INFO" "在 '$description' 阶段无项目处理。"; return; fi
    log "INFO" "开始并行执行 '$description' (最大并发: $MAX_PARALLEL_JOBS)..."
    local pids=(); local completed_count=0
    export -f log retry_with_backoff show_progress "$task_func"; export MAX_RETRY_ATTEMPTS TEMP_DIR
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

# ===== 主要功能函数 =====

cleanup_project_api_keys() {
    SECONDS=0; log "INFO" "==================== 功能: 清理所有项目中的API密钥 ===================="
    local project_list; project_list=$(gcloud projects list --format='value(projectId)' --filter='projectId!~^sys-' --quiet)
    if [ -z "$project_list" ]; then log "INFO" "未找到任何用户项目。"; return 0; fi
    local projects_array; readarray -t projects_array <<< "$project_list"; log "WARN" "将清理 ${#projects_array[@]} 个项目中所有的API密钥。"
    read -p "确认继续吗? [y/N]: " r; [[ "$r" =~ ^[Yy]$ ]] || { log "INFO" "操作取消。"; return 1; }
    echo "API密钥清理日志 - $(date)" > "$CLEANUP_LOG"; local CLEANED_FILE="${TEMP_DIR}/cleaned.txt"
    run_parallel task_cleanup_keys "清理API密钥" "$CLEANED_FILE" "${projects_array[@]}"
    local success_count; success_count=$(wc -l < "$CLEANED_FILE" | xargs); generate_report "$success_count" $((${#projects_array[@]} - success_count)) "${#projects_array[@]}" "清理API密钥"
}

check_prerequisites() {
    log "INFO" "执行前置检查..."; if ! command -v gcloud &> /dev/null; then log "ERROR" "未找到 'gcloud' 命令。"; return 1; fi
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "."; then log "WARN" "未检测到活跃GCP账号，请先登录。"; gcloud auth login || return 1; fi
    log "INFO" "前置检查通过。"; return 0
}

# ===== 程序入口 =====
trap cleanup_resources EXIT SIGINT SIGTERM
if ! check_prerequisites; then 
    log "ERROR" "前置检查失败，程序退出。"
    exit 1
fi

log "INFO" "API密钥清理脚本已启动！"
cleanup_project_api_keys
log "INFO" "脚本执行完毕。"
exit 0
