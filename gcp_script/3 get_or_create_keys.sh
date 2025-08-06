#!/bin/bash

# ==============================================================================
#
# 密钥管理器 - 提取或创建版 v1.0
#
# - 该脚本基于 密钥管理器修改版 v1.3
# - 功能: 遍历所有GCP项目。如果项目已有API密钥，则读取并记录；如果没有，则为其创建一个新的API密钥。
# - 作者: momo & ddddd1996 & KKTsN (原始作者), Cline (修改)
#
# ==============================================================================

# ===== 全局配置 =====
TIMESTAMP=$(date +%s)
SECONDS=0

# 文件和目录配置
KEY_CSV_FILE="key_all_projects.csv"
TEMP_DIR="/tmp/gcp_script_${TIMESTAMP}"
HEARTBEAT_PID=""

# 启动时创建临时目录
mkdir -p "$TEMP_DIR"

# ===== 工具函数 =====


# 检查并安装jq
check_and_install_jq() {
    if command -v jq &>/dev/null; then
        echo "jq已安装，将使用jq进行JSON解析"
        return 0
    fi
    
    echo "未检测到jq，尝试自动安装..."
    
    # 检测操作系统并尝试安装
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &>/dev/null; then
            echo "检测到Debian/Ubuntu系统，使用apt-get安装jq..."
            if sudo apt-get update && sudo apt-get install -y jq; then
                echo "jq安装成功"
                return 0
            fi
        elif command -v yum &>/dev/null; then
            echo "检测到RHEL/CentOS系统，使用yum安装jq..."
            if sudo yum install -y jq; then
                echo "jq安装成功"
                return 0
            fi
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &>/dev/null; then
            echo "检测到macOS系统，使用Homebrew安装jq..."
            if brew install jq; then
                echo "jq安装成功"
                return 0
            fi
        fi
    fi
    
    echo "jq安装失败，将使用备用的sed/grep方法解析JSON"
    return 1
}

# 初始化时检查jq
check_and_install_jq


# 优化版JSON解析函数
parse_json() {
    local json_input="$1"
    local field="$2"
    local value=""
    if command -v jq &>/dev/null; then
        value=$(echo "$json_input" | jq -r "$field // \"\"")
    else
        echo "jq not found. Using simplified parser which may fail for nested data."
        local simple_field=$(basename "$field")
        value=$(echo "$json_input" | grep -o "\"$simple_field\": *\"[^\"]*\"" | head -n 1 | cut -d'"' -f4)
    fi
    if [[ -n "$value" && "$value" != "null" ]]; then
        echo "$value"; return 0;
    else
        return 1;
    fi
}

# 文件写入函数 (带文件锁)
write_keys_to_files() {
    local project_id="$1"
    local api_key="$2"
    if [[ -z "$project_id" || -z "$api_key" ]]; then return 1; fi
    (
        if flock -w 10 200; then
            # 如果文件不存在或为空，写入表头
            if [[ ! -f "$KEY_CSV_FILE" || ! -s "$KEY_CSV_FILE" ]]; then
                echo "projectid,keys" > "$KEY_CSV_FILE"
            fi
            # 写入项目ID和密钥
            echo "$project_id,$api_key" >> "$KEY_CSV_FILE"
        else
            echo "写入文件失败: 获取文件锁超时"
            return 1
        fi
    ) 200>"${TEMP_DIR}/key_files.lock"
}



generate_report() {
    local success=$1 failed=$2 total=$3 operation=${4:-"处理"}; local success_rate=0
    if (( total > 0 )); then success_rate=$(awk "BEGIN {printf \"%.2f\", $success * 100 / $total}"); fi
    local duration=$SECONDS h=$((duration/3600)) m=$(((duration%3600)/60)) s=$((duration%60))
    echo; echo "======================== 执 行 报 告 ========================";
    printf "  操作类型    : %s\n" "$operation"; printf "  总计尝试    : %d\n" "$total"; printf "  成功数量    : %d\n" "$success";
    printf "  失败数量    : %d\n" "$failed"; printf "  成功率      : %.2f%%\n" "$success_rate"; printf "  总执行时间  : %d小时 %d分钟 %d秒\n" "$h" "$m" "$s"
    if (( success > 0 )) && [[ "$operation" == *"密钥"* ]]; then
        local key_count; key_count=$(wc -l < "$KEY_CSV_FILE" 2>/dev/null || echo 0)
        if (( key_count > 1 )); then
            key_count=$((key_count - 1))  # 减去表头行
        fi
        echo; echo "  输出文件:"; echo "  - CSV密钥文件   : $KEY_CSV_FILE ($key_count 个密钥)"
    fi
    echo "================================================================"
}

# ===== 健壮的任务函数 =====


task_create_key() {
    local project_id="$1"; local success_file="$2"; local create_output
    create_output=$(gcloud services api-keys create --project="$project_id" --display-name="Gemini-API-Key" --format=json --quiet)
    if [[ -z "$create_output" ]]; then echo "为项目 $project_id 创建密钥失败 (无输出)。"; return 1; fi
    local gcp_error_msg; gcp_error_msg=$(parse_json "$create_output" ".error.message")
    if [[ -n "$gcp_error_msg" ]]; then echo "为项目 $project_id 创建密钥时GCP返回错误: $gcp_error_msg"; echo "GCP错误详情: $create_output"; return 1; fi
    
    local api_key; api_key=$(parse_json "$create_output" ".response.keyString")

    if [[ -n "$api_key" ]]; then
        write_keys_to_files "$project_id" "$api_key"; (flock 200; echo "$project_id" >> "$success_file";) 200>"${success_file}.lock"; return 0
    else
        echo "为项目 $project_id 提取密钥失败 (无法解析 .response.keyString)。"; echo "gcloud返回内容: $create_output"; return 1
    fi
}

cleanup_resources() {
    echo "执行退出清理..."; pkill -P $$ &>/dev/null; rm -rf "$TEMP_DIR";
}

# ===== 并行执行与报告 =====


check_prerequisites() {
    echo "执行前置检查..."; if ! command -v gcloud &> /dev/null; then echo "未找到 'gcloud' 命令。"; return 1; fi
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "."; then echo "未检测到活跃GCP账号，请先登录。"; gcloud auth login || return 1; fi
    if ! command -v jq &>/dev/null; then echo "强烈建议安装 'jq' 以获得最可靠的JSON解析！"; fi
    echo "前置检查通过。"; return 0
}

# ===== 主要逻辑 =====

get_or_create_keys() {
    SECONDS=0
    echo "==================== 功能: 提取或创建所有项目的密钥 ===================="
    echo "正在获取项目列表..."
    
    local project_list
    project_list=$(gcloud projects list --format='value(projectId)' --filter='projectId!~^sys-' --quiet)
    if [ -z "$project_list" ]; then
        echo "未找到任何用户项目。"
        return 0
    fi
    
    local projects_array
    readarray -t projects_array <<< "$project_list"
    
    # 清空并初始化密钥文件
    > "$KEY_CSV_FILE"
    echo "projectid,keys" > "$KEY_CSV_FILE"
    
    local projects_to_create_for=()
    local projects_with_keys=0
    local projects_permission_denied=0
    local total_projects=${#projects_array[@]}
    local checked_count=0

    echo "找到 ${total_projects} 个项目。开始检查现有密钥..."

    for project_id in "${projects_array[@]}"; do
        local error_log="${TEMP_DIR}/list_keys_${project_id}_error.log"
        local key_string
        
        # 尝试获取密钥，并将错误重定向到日志文件
        key_string=$(gcloud services api-keys list --project="$project_id" --format="value(keyString)" --limit=1 --quiet 2>"$error_log")
        
        if [ -n "$key_string" ]; then
            # 成功获取到密钥
            echo "项目 $project_id: 找到密钥。"
            write_keys_to_files "$project_id" "$key_string"
            ((projects_with_keys++))
        else
            # 未获取到密钥，检查原因
            if grep -q "PERMISSION_DENIED" "$error_log" 2>/dev/null || grep -q "service is not enabled" "$error_log" 2>/dev/null; then
                # 如果是权限问题或API未启用，则加入待创建列表
                echo "项目 $project_id: 无密钥或API未启用，将尝试创建。"
                projects_to_create_for+=("$project_id")
            elif [ -s "$error_log" ]; then
                # 其他错误
                echo "项目 $project_id: 检查时发生未知错误。"
                ((projects_permission_denied++))
            else
                # 没有错误，但也没有密钥
                echo "项目 $project_id: 未找到密钥，将进行创建。"
                projects_to_create_for+=("$project_id")
            fi
        fi
        rm -f "$error_log"
        ((checked_count++))
    done
    
    echo
    echo "检查完成。已有密钥的项目: $projects_with_keys, 检查出错的项目: $projects_permission_denied"

    local projects_to_create_count=${#projects_to_create_for[@]}
    if [ $projects_to_create_count -eq 0 ]; then
        echo "所有项目均已处理或无需创建新密钥。"
        generate_report "$projects_with_keys" 0 "$total_projects" "检查密钥"
        return 0
    fi

    echo "将为 ${projects_to_create_count} 个项目创建新密钥。"
    read -p "确认继续吗? [y/N]: " r
    [[ "$r" =~ ^[Yy]$ ]] || { echo "操作已取消。"; return 1; }

    # 阶段1: 启用API
    echo "开始为需要创建密钥的项目启用API..."
    local enabled_project_ids=()
    for project_id in "${projects_to_create_for[@]}"; do
        echo "正在为项目 $project_id 启用API..."
        if gcloud services enable generativelanguage.googleapis.com --project="$project_id" --quiet; then
            echo "项目 $project_id API启用成功。"
            enabled_project_ids+=("$project_id")
        else
            echo "项目 $project_id API启用失败。"
        fi
    done
    
    if [ ${#enabled_project_ids[@]} -eq 0 ]; then
        echo "API启用阶段完全失败。"
        return 1
    fi

    # 阶段2: 创建密钥
    echo "开始为已启用API的项目创建密钥..."
    local successful_keys=0
    for project_id in "${enabled_project_ids[@]}"; do
        echo "正在为项目 $project_id 创建密钥..."
        if task_create_key "$project_id" /dev/null; then
            echo "项目 $project_id 密钥创建成功。"
            ((successful_keys++))
        else
            echo "项目 $project_id 密钥创建失败。"
        fi
    done
    generate_report "$successful_keys" $((${#projects_to_create_for[@]} - successful_keys)) "${#projects_to_create_for[@]}" "创建新密钥"

    echo "所有操作完成。"
    local final_key_count
    final_key_count=$(($(wc -l < "$KEY_CSV_FILE") - 1))
    echo "最终在 $KEY_CSV_FILE 文件中共有 $final_key_count 个密钥。"
}


# ===== 程序入口 =====
trap cleanup_resources EXIT SIGINT SIGTERM
if ! check_prerequisites; then
    echo "前置检查失败，程序退出。"
    exit 1
fi

get_or_create_keys

echo "脚本执行完毕。"
exit 0
