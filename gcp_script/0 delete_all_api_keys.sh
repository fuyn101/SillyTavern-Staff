#!/bin/bash

# ==============================================================================
#
# GCP 项目 API 密钥清理脚本 (精简版) v2.0
#
# - 该脚本用于删除所有GCP项目中创建的API密钥。
# - 并行执行以提高效率。
#
# ==============================================================================

# ===== 配置 =====
MAX_PARALLEL_JOBS=40

# ===== 工具函数 =====
# (无)

# ===== 核心任务函数 =====

# 清理单个项目中的API密钥
task_cleanup_keys_for_project() {
    local project_id="$1"
    echo "INFO: 开始处理项目: $project_id"

    local key_names
    readarray -t key_names < <(gcloud services api-keys list --project="$project_id" --format="value(name)" --quiet)

    if [ ${#key_names[@]} -eq 0 ]; then
        echo "INFO: 项目 '$project_id' 中没有找到API密钥。"
        return 0
    fi

    echo "INFO: 在项目 '$project_id' 中找到 ${#key_names[@]} 个密钥，准备删除..."

    local all_success=true
    for key_name in "${key_names[@]}"; do
        echo "  - 正在删除密钥: $key_name"
        if ! gcloud services api-keys delete "$key_name" --quiet; then
            all_success=false
            echo "ERROR: 删除密钥 '$key_name' 失败。"
        fi
        sleep 0.2 # 轻微延迟以防触发速率限制
    done

    if $all_success; then
        echo "SUCCESS: 项目 '$project_id' 中的所有密钥已成功删除。"
        return 0
    else
        echo "WARN: 项目 '$project_id' 中有部分密钥删除失败。"
        return 1
    fi
}

# ===== 主函数 =====

main() {
    SECONDS=0
    echo "INFO: ==================== 开始清理所有项目中的API密钥 ===================="

    echo "INFO: 1. 执行前置检查..."
    if ! command -v gcloud &> /dev/null; then
        echo "ERROR: 未找到 'gcloud' 命令。请确保GCP SDK已安装并配置在PATH中。"
        return 1
    fi
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "."; then
        echo "WARN: 未检测到活跃GCP账号，请先运行 'gcloud auth login'。"
        gcloud auth login || return 1
    fi
    echo "INFO: 前置检查通过。"

    echo "INFO: 2. 正在获取项目列表..."
    local project_list
    project_list=$(gcloud projects list --format='value(projectId)' --filter='projectId!~^sys-' --quiet)

    if [ -z "$project_list" ]; then
        echo "INFO: 未找到任何用户项目，无需操作。"
        return 0
    fi

    local projects_array
    readarray -t projects_array <<< "$project_list"
    echo "WARN: 将清理 ${#projects_array[@]} 个项目中所有的API密钥。此操作不可逆！"
    read -p "确认要继续吗? [y/N]: " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "INFO: 操作已取消。"
        return 1
    fi

    echo "INFO: 3. 开始并行删除API密钥 (最大并发: $MAX_PARALLEL_JOBS)..."
    export -f task_cleanup_keys_for_project
    
    local pids=()
    for project in "${projects_array[@]}"; do
        if (( ${#pids[@]} >= MAX_PARALLEL_JOBS )); then
            wait -n "${pids[@]}"
            # 清理已完成的PID
            pids=($(jobs -p | grep -v '^Done$'))
        fi
        task_cleanup_keys_for_project "$project" &
        pids+=($!)
    done

    wait
    
    local duration=$SECONDS
    echo "INFO: ==================== 所有项目的API密钥清理完毕 ===================="
    echo "总耗时: $((duration / 60)) 分钟 $((duration % 60)) 秒。"
}

# ===== 程序入口 =====
main "$@"
exit 0
