#!/bin/bash

# ==============================================================================
#
# 密钥管理器 - 分类处理版 v2.0
#
# - 功能: 遍历所有GCP项目。
#   1. 如果项目已有API密钥，则记录项目ID。
#   2. 如果没有，则为其创建一个新的API密钥并记录。
# - 作者: momo & ddddd1996 & KKTsN (原始作者), Cline (修改)
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

# 检查并安装jq
check_and_install_jq() {
    if command -v jq &>/dev/null; then
        echo "jq已安装，将使用jq进行JSON解析"
        return 0
    fi
    echo "未检测到jq，将使用备用的sed/grep方法解析JSON"
    return 1
}

# 初始化时检查jq
check_and_install_jq

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

# 新密钥写入函数
write_new_key_to_csv() {
    local project_id="$1"
    local api_key="$2"
    if [[ -z "$project_id" || -z "$api_key" ]]; then return 1; fi
    (
        flock -w 10 200
        if [[ ! -f "$NEW_KEYS_CSV_FILE" || ! -s "$NEW_KEYS_CSV_FILE" ]]; then
            echo "projectid,keys" > "$NEW_KEYS_CSV_FILE"
        fi
        echo "$project_id,$api_key" >> "$NEW_KEYS_CSV_FILE"
    ) 200>"${TEMP_DIR}/new_keys.lock"
}

# 记录已有密钥的项目
log_existing_key_project() {
    local project_id="$1"
    if [[ -z "$project_id" ]]; then return 1; fi
    (
        flock -w 10 201
        echo "$project_id" >> "$EXISTING_KEYS_LOG_FILE"
    ) 201>"${TEMP_DIR}/existing_keys.lock"
}

# 报告生成函数
generate_report() {
    local existing_keys_count=$1
    local new_keys_success=$2
    local new_keys_failed=$3
    local total_to_create=$4
    
    local duration=$SECONDS
    local h=$((duration/3600))
    local m=$(((duration%3600)/60))
    local s=$((duration%60))

    echo
    echo "======================== 执 行 报 告 ========================"
    printf "  总执行时间  : %d小时 %d分钟 %d秒\n" "$h" "$m" "$s"
    echo
    echo "--- 已有密钥的项目 ---"
    printf "  已找到      : %d 个\n" "$existing_keys_count"
    if (( existing_keys_count > 0 )); then
        printf "  详情列表    : %s\n" "$EXISTING_KEYS_LOG_FILE"
    fi
    
    echo
    echo "--- 新建密钥的项目 ---"
    printf "  尝试创建    : %d 个\n" "$total_to_create"
    printf "  成功数量    : %d 个\n" "$new_keys_success"
    printf "  失败数量    : %d 个\n" "$new_keys_failed"
    if (( new_keys_success > 0 )); then
        local key_count=$(($(wc -l < "$NEW_KEYS_CSV_FILE" 2>/dev/null || echo 1) - 1))
        printf "  输出文件    : %s (%d 个新密钥)\n" "$NEW_KEYS_CSV_FILE" "$key_count"
    fi
    echo "================================================================"
}

# ===== 核心任务函数 =====

task_create_key() {
    local project_id="$1"
    local create_output
    create_output=$(gcloud services api-keys create --project="$project_id" --display-name="Gemini-API-Key" --format=json --quiet)
    if [[ -z "$create_output" ]]; then
        echo "为项目 $project_id 创建密钥失败 (无输出)。"
        return 1
    fi
    
    local gcp_error_msg
    gcp_error_msg=$(parse_json "$create_output" ".error.message")
    if [[ -n "$gcp_error_msg" ]]; then
        echo "为项目 $project_id 创建密钥时GCP返回错误: $gcp_error_msg"
        return 1
    fi
    
    local api_key
    api_key=$(parse_json "$create_output" ".response.keyString")
    if [[ -n "$api_key" ]]; then
        write_new_key_to_csv "$project_id" "$api_key"
        return 0
    else
        echo "为项目 $project_id 提取密钥失败 (无法解析 .response.keyString)。"
        return 1
    fi
}

cleanup_resources() {
    echo "执行退出清理..."
    pkill -P $$ &>/dev/null
    rm -rf "$TEMP_DIR"
}

check_prerequisites() {
    echo "执行前置检查..."
    if ! command -v gcloud &> /dev/null; then echo "未找到 'gcloud' 命令。"; return 1; fi
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "."; then echo "未检测到活跃GCP账号，请先登录。"; gcloud auth login || return 1; fi
    echo "前置检查通过。"
    return 0
}

# ===== 主要逻辑 =====

main() {
    SECONDS=0
    echo "==================== 功能: 检查并按需创建项目密钥 ===================="
    
    # 清空并初始化输出文件
    > "$NEW_KEYS_CSV_FILE"
    > "$EXISTING_KEYS_LOG_FILE"
    
    echo "正在获取项目列表..."
    local project_list
    project_list=$(gcloud projects list --format='value(projectId)' --filter='projectId!~^sys-' --quiet)
    if [ -z "$project_list" ]; then
        echo "未找到任何用户项目。"
        return 0
    fi
    
    local projects_array
    readarray -t projects_array <<< "$project_list"
    
    local projects_to_create_for=()
    local projects_with_keys=0
    local total_projects=${#projects_array[@]}

    echo "找到 ${total_projects} 个项目。开始检查现有密钥..."

    for project_id in "${projects_array[@]}"; do
        local error_log="${TEMP_DIR}/list_keys_${project_id}_error.log"
        local key_string
        
        key_string=$(gcloud services api-keys list --project="$project_id" --format="value(keyString)" --limit=1 --quiet 2>"$error_log")
        
        if [ -n "$key_string" ]; then
            echo "项目 $project_id: 找到现有密钥。"
            log_existing_key_project "$project_id"
            ((projects_with_keys++))
        else
            echo "项目 $project_id: 未找到密钥，将进行创建。"
            projects_to_create_for+=("$project_id")
        fi
        rm -f "$error_log"
    done
    
    echo
    echo "检查完成。发现 ${projects_with_keys} 个项目已有密钥。"

    local projects_to_create_count=${#projects_to_create_for[@]}
    if [ $projects_to_create_count -eq 0 ]; then
        echo "没有需要创建新密钥的项目。"
        generate_report "$projects_with_keys" 0 0 0
        return 0
    fi

    echo "将为 ${projects_to_create_count} 个项目创建新密钥。"

    # 阶段1: 启用API
    echo "开始为需要创建密钥的项目启用API..."
    local enabled_project_ids=()
    local failed_enable_api=()
    for project_id in "${projects_to_create_for[@]}"; do
        echo "正在为项目 $project_id 启用API..."
        if gcloud services enable generativelanguage.googleapis.com --project="$project_id" --quiet; then
            echo "项目 $project_id API启用成功。"
            enabled_project_ids+=("$project_id")
        else
            echo "项目 $project_id API启用失败。"
            failed_enable_api+=("$project_id")
        fi
    done
    
    if [ ${#enabled_project_ids[@]} -eq 0 ]; then
        echo "API启用阶段完全失败。"
        generate_report "$projects_with_keys" 0 ${#failed_enable_api[@]} ${projects_to_create_count}
        return 1
    fi

    # 阶段2: 创建密钥
    echo "开始为已启用API的项目创建密钥..."
    local successful_keys=0
    for project_id in "${enabled_project_ids[@]}"; do
        echo "正在为项目 $project_id 创建密钥..."
        if task_create_key "$project_id"; then
            echo "项目 $project_id 密钥创建成功。"
            ((successful_keys++))
        else
            echo "项目 $project_id 密钥创建失败。"
        fi
    done
    
    local failed_keys_count=$((${#enabled_project_ids[@]} - successful_keys))
    local total_failed=$((${#failed_enable_api[@]} + failed_keys_count))
    
    generate_report "$projects_with_keys" "$successful_keys" "$total_failed" "$projects_to_create_count"

    echo "所有操作完成。"
}

# ===== 程序入口 =====
trap cleanup_resources EXIT SIGINT SIGTERM
if ! check_prerequisites; then
    echo "前置检查失败，程序退出。"
    exit 1
fi

main

echo "脚本执行完毕。"
exit 0
