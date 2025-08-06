#!/bin/bash

# ==============================================================================
#
# GCP 密钥管理器脚本 v3.0
#
# - 功能: 遍历所有GCP项目，检查并按需创建API密钥。
#   1. 如果项目已有API密钥，则记录项目ID。
#   2. 如果没有，则为其创建一个新的API密钥并记录。
# - 作者: momo & ddddd1996 & KKTsN & Cline
#
# ==============================================================================

# ===== 全局配置 =====
TIMESTAMP=$(date +%s)
SECONDS=0

# 文件和目录配置
NEW_KEYS_CSV_FILE="newly_created_keys.csv"
EXISTING_KEYS_LOG_FILE="projects_with_existing_keys.txt"
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

# JSON解析函数
parse_json() {
    local json_input="$1"
    local field="$2"
    local value=""
    if command -v jq &>/dev/null; then
        value=$(echo "$json_input" | jq -r "$field // \"\"")
    else
        local simple_field=$(basename "$field")
        value=$(echo "$json_input" | grep -o "\"$simple_field\": *\"[^\"]*\"" | head -n 1 | cut -d'"' -f4)
    fi
    if [[ -n "$value" && "$value" != "null" ]]; then
        echo "$value"; return 0
    else
        return 1
    fi
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

task_create_key() {
    local project_id="$1"
    local create_output
    create_output=$(gcloud services api-keys create --project="$project_id" --display-name="Gemini-API-Key" --format=json --quiet)
    if [[ -z "$create_output" ]]; then
        log "ERROR" "为项目 $project_id 创建密钥失败 (无输出)。"
        return 1
    fi

    local gcp_error_msg
    gcp_error_msg=$(parse_json "$create_output" ".error.message")
    if [[ -n "$gcp_error_msg" ]]; then
        log "ERROR" "为项目 $project_id 创建密钥时GCP返回错误: $gcp_error_msg"
        return 1
    fi

    local api_key
    api_key=$(parse_json "$create_output" ".response.keyString")
    if [[ -n "$api_key" ]]; then
        # 写入CSV文件
        (
            flock -w 10 200
            if [[ ! -f "$NEW_KEYS_CSV_FILE" || ! -s "$NEW_KEYS_CSV_FILE" ]]; then
                echo "projectid,keys" > "$NEW_KEYS_CSV_FILE"
            fi
            echo "$project_id,$api_key" >> "$NEW_KEYS_CSV_FILE"
        ) 200>"${TEMP_DIR}/new_keys.lock"
        return 0
    else
        log "ERROR" "为项目 $project_id 提取密钥失败 (无法解析 .response.keyString)。"
        return 1
    fi
}

# ===== 主功能函数 =====

main() {
    SECONDS=0
    log "INFO" "======================================================"
    log "INFO" "功能: 检查并按需创建项目密钥"
    log "INFO" "======================================================"

    # 检查是否在交互式终端中运行
    if ! [ -t 0 ]; then
        log "ERROR" "此脚本只能在交互式终端中运行。"
        return 1
    fi

    # 清空并初始化输出文件
    > "$NEW_KEYS_CSV_FILE"
    > "$EXISTING_KEYS_LOG_FILE"

    log "INFO" "正在获取项目列表..."
    local project_list
    project_list=$(gcloud projects list --format='value(projectId)' --filter='projectId!~^sys-' --quiet)
    if [ -z "$project_list" ]; then
        log "WARN" "未找到任何用户项目。"
        return 0
    fi

    local projects_array
    readarray -t projects_array <<< "$project_list"

    local projects_to_create_for=()
    local projects_with_keys=0
    local total_projects=${#projects_array[@]}

    log "INFO" "找到 ${total_projects} 个项目。开始检查现有密钥..."

    for project_id in "${projects_array[@]}"; do
        local key_string
        key_string=$(gcloud services api-keys list --project="$project_id" --format="value(keyString)" --limit=1 --quiet 2>/dev/null)

        if [ -n "$key_string" ]; then
            log "INFO" "项目 $project_id: 找到现有密钥。"
            echo "$project_id" >> "$EXISTING_KEYS_LOG_FILE"
            ((projects_with_keys++))
        else
            log "INFO" "项目 $project_id: 未找到密钥，将进行创建。"
            projects_to_create_for+=("$project_id")
        fi
    done

    log "INFO" "检查完成。发现 ${projects_with_keys} 个项目已有密钥。"

    local projects_to_create_count=${#projects_to_create_for[@]}
    if [ $projects_to_create_count -eq 0 ]; then
        log "INFO" "没有需要创建新密钥的项目。"
    else
        log "INFO" "将为 ${projects_to_create_count} 个项目创建新密钥。"
        local successful_keys=0
        for project_id in "${projects_to_create_for[@]}"; do
            log "INFO" "正在为项目 $project_id 创建密钥..."
            if task_create_key "$project_id"; then
                log "INFO" "项目 $project_id 密钥创建成功。"
                ((successful_keys++))
            else
                log "ERROR" "项目 $project_id 密钥创建失败。"
            fi
        done
    fi

    # 生成报告
    local duration=$SECONDS
    local h=$((duration/3600)); local m=$(((duration%3600)/60)); local s=$((duration%60))
    local new_keys_success=$(($(wc -l < "$NEW_KEYS_CSV_FILE" 2>/dev/null || echo 1) - 1))
    if (( new_keys_success < 0 )); then new_keys_success=0; fi
    local new_keys_failed=$((projects_to_create_count - new_keys_success))

    log "INFO" "======================== 执 行 报 告 ========================"
    log "INFO" "  总执行时间  : ${h}小时 ${m}分钟 ${s}秒"
    log "INFO" "--- 已有密钥的项目 ---"
    log "INFO" "  已找到      : $projects_with_keys 个"
    if (( projects_with_keys > 0 )); then
        log "INFO" "  详情列表    : $EXISTING_KEYS_LOG_FILE"
    fi
    log "INFO" "--- 新建密钥的项目 ---"
    log "INFO" "  尝试创建    : $projects_to_create_count 个"
    log "INFO" "  成功数量    : $new_keys_success 个"
    log "INFO" "  失败数量    : $new_keys_failed 个"
    if (( new_keys_success > 0 )); then
        log "INFO" "  输出文件    : $NEW_KEYS_CSV_FILE"
    fi
    log "INFO" "================================================================"
}

# ===== 程序入口 =====
trap cleanup_resources EXIT SIGINT SIGTERM
if ! check_prerequisites; then
    log "ERROR" "前置检查失败，程序退出。"
    exit 1
fi

main

log "INFO" "脚本执行完毕。"
exit 0
