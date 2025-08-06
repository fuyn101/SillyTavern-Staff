#!/bin/bash

# ==============================================================================
#
# GCP 项目 API 启用脚本 v2.0
#
# - 该脚本会自动查找您账户下的所有GCP项目，并为它们启用指定的API。
# - 作者: momo & ddddd1996 & KKTsN & Cline
#
# ==============================================================================

# ===== 全局配置 =====
TIMESTAMP=$(date +%s)
SECONDS=0
MAX_PARALLEL_JOBS=10
# 需要启用的API列表
APIS_TO_ENABLE=(
    "generativelanguage.googleapis.com"
    "geminicloudassist.googleapis.com"
    "cloudaicompanion.googleapis.com"
)
export APIS_TO_ENABLE

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
    # 同时输出到控制台和日志文件
    echo "[$timestamp] [$level] $msg" | tee -a "${TEMP_DIR}/script.log"
}

# ===== 任务函数 =====

cleanup_resources() {
    log "INFO" "执行退出清理..."; pkill -P $$ &>/dev/null; rm -rf "$TEMP_DIR";
}

check_prerequisites() {
    log "INFO" "执行前置检查...";
    if ! command -v gcloud &> /dev/null; then
        log "ERROR" "未找到 'gcloud' 命令。请确保GCloud SDK已安装并位于您的PATH中。"
        return 1
    fi
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "."; then
        log "WARN" "未检测到活跃GCP账号，请先登录。"
        gcloud auth login || return 1
    fi
    log "INFO" "前置检查通过。"
    return 0
}

# 为单个项目启用API的任务函数
task_enable_apis_for_project() {
    local project_id="$1"
    local success_file="$2"
    local failure_file="$3"

    log "INFO" "正在为项目 '$project_id' 启用API..."
    if gcloud services enable "${APIS_TO_ENABLE[@]}" --project="$project_id" --quiet; then
        log "INFO" "成功为项目 '$project_id' 启用API。"
        echo "$project_id" >> "$success_file"
    else
        log "ERROR" "为项目 '$project_id' 启用API失败。"
        echo "$project_id" >> "$failure_file"
    fi
}

# ===== 主功能函数 =====

main() {
    SECONDS=0
    log "INFO" "======================================================"
    log "INFO" "功能: 为所有项目启用API"
    log "INFO" "======================================================"

    # 检查是否在交互式终端中运行
    if ! [ -t 0 ]; then
        log "ERROR" "此脚本只能在交互式终端中运行。"
        return 1
    fi

    log "INFO" "正在获取所有项目列表..."
    local project_list
    project_list=$(gcloud projects list --format='value(projectId)' --filter='projectId!~^sys-' --quiet)
    if [ -z "$project_list" ]; then
        log "WARN" "未找到任何用户项目可供操作。"
        return 0
    fi

    local ALL_PROJECT_IDS
    readarray -t ALL_PROJECT_IDS <<< "$project_list"
    local total_projects=${#ALL_PROJECT_IDS[@]}

    log "INFO" "将为找到的 $total_projects 个项目自动启用API。"
    log "INFO" "在 3 秒后开始执行... (按 Ctrl+C 取消)"; sleep 3

    local SUCCESS_FILE="${TEMP_DIR}/success.txt"
    local FAILED_FILE="${TEMP_DIR}/failed.txt"
    touch "$SUCCESS_FILE" "$FAILED_FILE"

    log "INFO" "开始并行启用API (最多 ${MAX_PARALLEL_JOBS} 个并行任务)..."
    
    local job_count=0
    for project_id in "${ALL_PROJECT_IDS[@]}"; do
        task_enable_apis_for_project "$project_id" "$SUCCESS_FILE" "$FAILED_FILE" &
        ((job_count++))
        if [ "$job_count" -ge "$MAX_PARALLEL_JOBS" ]; then
            wait -n
            ((job_count--))
        fi
    done

    wait # 等待所有剩余的后台任务完成

    local success_count
    success_count=$(wc -l < "$SUCCESS_FILE")
    local failed_projects
    readarray -t failed_projects < "$FAILED_FILE"
    local failed_count=${#failed_projects[@]}

    # 生成报告
    log "INFO" "==================== 执行完毕 ===================="
    log "INFO" "总共处理项目数: $total_projects"
    log "INFO" "成功启用API的项目数: $success_count"
    log "INFO" "失败的项目数: $failed_count"
    if [ $failed_count -gt 0 ]; then
        log "WARN" "以下项目启用API失败:"
        for project_id in "${failed_projects[@]}"; do
            log "WARN" "  - $project_id"
        done
    fi
    log "INFO" "=================================================="
}

# ===== 程序入口 =====
trap cleanup_resources EXIT SIGINT SIGTERM

# 导出函数以供子进程使用
export -f log task_enable_apis_for_project

if ! check_prerequisites; then
    log "ERROR" "前置检查失败，程序退出。"
    exit 1
fi

main

log "INFO" "脚本执行完毕。"
exit 0
