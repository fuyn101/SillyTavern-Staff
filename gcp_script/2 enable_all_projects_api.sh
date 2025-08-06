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

# ===== 程序入口 =====
main() {
    echo "正在获取所有项目列表并自动启用API..."
    local project_list
    project_list=$(gcloud projects list --format='value(projectId)' --filter='projectId!~^sys-' --quiet)
    if [ -z "$project_list" ]; then
        echo "未找到任何用户项目可供操作。"
        exit 0
    fi

    local ALL_PROJECT_IDS
    readarray -t ALL_PROJECT_IDS <<< "$project_list"
    local total_projects=${#ALL_PROJECT_IDS[@]}

    echo
    echo "将为找到的 $total_projects 个项目自动启用API。"
    echo "3秒后开始执行... (按 Ctrl+C 取消)"
    sleep 3

    local success_count=0
    local failed_projects=()

    for project_id in "${ALL_PROJECT_IDS[@]}"; do
        echo "--------------------------------------------------"
        echo "正在为项目 '$project_id' 启用API..."
        if gcloud services enable generativelanguage.googleapis.com geminicloudassist.googleapis.com cloudaicompanion.googleapis.com --project="$project_id" --quiet; then
            echo "成功为项目 '$project_id' 启用API。"
            ((success_count++))
        else
            echo "为项目 '$project_id' 启用API失败。"
            failed_projects+=("$project_id")
        fi
    done

    local failed_count=${#failed_projects[@]}

    echo
    echo "==================== 执行完毕 ===================="
    echo "总共处理项目数: $total_projects"
    echo "成功启用API的项目数: $success_count"
    echo "失败的项目数: $failed_count"
    if [ $failed_count -gt 0 ]; then
        echo "以下项目启用API失败:"
        for project_id in "${failed_projects[@]}"; do
            echo "  - $project_id"
        done
    fi
    echo "=================================================="
}

main "$@"
