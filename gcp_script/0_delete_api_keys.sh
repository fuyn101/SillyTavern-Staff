#!/bin/bash

# ==============================================================================
#
# GCP 项目 API 密钥清理脚本 v3.0
#
# - 该脚本用于删除所有GCP项目中创建的API密钥。
# - 串行执行以确保稳定性。
# - 作者: momo & ddddd1996 & KKTsN & Cline
#
# ==============================================================================

# ===== 全局配置 =====
TIMESTAMP=$(date +%s)
SECONDS=0

# 文件和目录配置
MAX_PARALLEL_JOBS=10
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

# 清理单个项目中的API密钥
task_cleanup_keys_for_project() {
    local project_id="$1"
    log "INFO" "开始处理项目: $project_id"

    local key_names
    readarray -t key_names < <(gcloud services api-keys list --project="$project_id" --format="value(name)" --quiet 2>/dev/null)

    if [ ${#key_names[@]} -eq 0 ]; then
        log "INFO" "项目 '$project_id' 中没有找到API密钥。"
        return 0
    fi

    log "INFO" "在项目 '$project_id' 中找到 ${#key_names[@]} 个密钥，准备删除..."

    local all_success=true
    for key_name in "${key_names[@]}"; do
        log "INFO" "  - 正在删除密钥: $key_name"
        if ! gcloud services api-keys delete "$key_name" --project="$project_id" --quiet; then
            all_success=false
            log "ERROR" "删除密钥 '$key_name' 失败。"
        fi
    done

    if $all_success; then
        log "INFO" "项目 '$project_id' 中的所有密钥已成功删除。"
        return 0
    else
        log "WARN" "项目 '$project_id' 中有部分密钥删除失败。"
        return 1
    fi
}

# ===== 主功能函数 =====

main() {
    SECONDS=0
    log "INFO" "======================================================"
    log "INFO" "功能: 清理所有项目中的API密钥"
    log "INFO" "======================================================"

    log "INFO" "正在获取项目列表..."
    local project_list
    project_list=$(gcloud projects list --format='value(projectId)' --filter='projectId!~^sys-' --quiet)

    if [ -z "$project_list" ]; then
        log "INFO" "未找到任何用户项目，无需操作。"
        return 0
    fi

    local projects_array
    readarray -t projects_array <<< "$project_list"
    log "WARN" "将清理 ${#projects_array[@]} 个项目中所有的API密钥。此操作不可逆！"
    
    # 检查是否在交互式终端中运行
    if ! [ -t 0 ]; then
        log "ERROR" "此脚本只能在交互式终端中运行，以进行安全确认。"
        return 1
    fi

    read -p "确认要继续吗? [y/N]: " confirm < /dev/tty
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        log "INFO" "操作已取消。"
        return 1
    fi


    log "INFO" "开始并行删除API密钥 (最多 ${MAX_PARALLEL_JOBS} 个并行任务)..."
    
    local job_count=0
    for project_id in "${projects_array[@]}"; do
        task_cleanup_keys_for_project "$project_id" &
        ((job_count++))
        if [ "$job_count" -ge "$MAX_PARALLEL_JOBS" ]; then
            wait -n
            ((job_count--))
        fi
    done

    wait # 等待所有剩余的后台任务完成

    local duration=$SECONDS
    log "INFO" "======================================================"
    log "INFO" "所有项目的API密钥清理完毕"
    log "INFO" "总耗时: $((duration / 60)) 分钟 $((duration % 60)) 秒。"
    log "INFO" "======================================================"
}

# ===== 程序入口 =====
trap cleanup_resources EXIT SIGINT SIGTERM

# 导出函数以供子进程使用
export -f log task_cleanup_keys_for_project

if ! check_prerequisites; then
    log "ERROR" "前置检查失败，程序退出。"
    exit 1
fi

main

log "INFO" "脚本执行完毕。"
exit 0
