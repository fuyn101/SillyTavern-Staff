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
MAX_PARALLEL_JOBS=10
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

# ===== 任务函数 =====

cleanup_resources() {
    log "INFO" "执行退出清理..."; pkill -P $$ &>/dev/null; rm -rf "$TEMP_DIR";
}

# 创建单个项目的任务函数
task_create_project() {
    local project_id="$1"
    local created_projects_file="$2"
    
    log "INFO" "正在创建项目: $project_id"
    if gcloud projects create "$project_id" --name="$project_id" --no-set-as-default --quiet; then
        log "INFO" "成功创建项目: $project_id"
        echo "$project_id" >> "$created_projects_file"
    else
        log "ERROR" "创建项目失败: $project_id"
    fi
}

# ===== 主功能函数 =====

main() {
    SECONDS=0
    log "INFO" "======================================================"
    log "INFO" "功能: 仅创建项目（不提取API密钥）"
    log "INFO" "======================================================"
    log "INFO" "使用随机生成的用户名: ${EMAIL_USERNAME}"
    
    # 检查是否在交互式终端中运行
    if ! [ -t 0 ]; then
        log "ERROR" "此脚本只能在交互式终端中运行。"
        return 1
    fi
    
    # 询问要创建的项目数量
    read -p "请输入要创建的项目数量 (1-75，默认为$TOTAL_PROJECTS): " custom_count < /dev/tty
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
    export CREATED_PROJECTS_FILE
    > "$CREATED_PROJECTS_FILE"
    
    log "INFO" "开始并行创建项目 (最多 ${MAX_PARALLEL_JOBS} 个并行任务)..."
    
    local job_count=0
    for project_id in "${projects_to_create[@]}"; do
        task_create_project "$project_id" "$CREATED_PROJECTS_FILE" &
        ((job_count++))
        if [ "$job_count" -ge "$MAX_PARALLEL_JOBS" ]; then
            wait -n
            ((job_count--))
        fi
    done

    wait # 等待所有剩余的后台任务完成
    
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

# 导出函数以供子进程使用
export -f log task_create_project

if ! check_prerequisites; then 
    log "ERROR" "前置检查失败，程序退出。"
    exit 1
fi

main

log "INFO" "脚本执行完毕。"
exit 0
