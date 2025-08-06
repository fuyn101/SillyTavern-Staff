# GCP 项目管理脚本

一组用于批量管理 Google Cloud Platform (GCP) 项目、API 和密钥的 Shell 脚本。

## 功能

*   **菜单驱动:** 提供一个交互式菜单 (`test.sh`) 来访问所有功能。
*   **批量项目管理:** 批量创建和删除 GCP 项目。
*   **API 批量启用:** 为所有项目批量启用指定的 API (例如 Gemini API)。
*   **API 密钥管理:** 智能提取或创建 API 密钥，并保存到 CSV 文件。同时提供一键清理所有密钥的功能。
*   **并行执行:** 所有耗时操作都采用并行处理，显著提高执行效率。
*   **健壮性:** 包含自动重试和错误处理机制。

## 前置要求

1.  **Google Cloud SDK:** 需要安装 `gcloud` 命令行工具。
    *   安装教程: [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)
2.  **用户认证:** 需要登录您的 GCP 账号。
    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```
3.  **jq (可选但推荐):** 为了更可靠地解析 JSON，建议安装 `jq`。脚本在检测到 `jq` 未安装时会尝试自动安装。
    ```bash
    # Debian/Ubuntu
    sudo apt-get install jq
    # RHEL/CentOS
    sudo yum install jq
    # macOS (Homebrew)
    brew install jq
    ```
4.  **运行环境:** 需要在 `bash` 环境下运行 (例如 Linux, macOS, WSL on Windows)。

## 快速开始 (推荐)

推荐使用集成了所有功能的菜单驱动脚本 `test.sh`。

```bash
# 赋予执行权限
chmod +x gcp_script/test.sh

# 运行主菜单脚本
./gcp_script/test.sh
```

之后，根据菜单提示选择您需要的功能。

## 脚本说明

### `test.sh` (主脚本)

交互式主菜单，整合了所有功能，是推荐的入口点。

### `0 delete_all_api_keys.sh`

清理脚本。遍历您账户下的所有 GCP 项目，并删除其中创建的所有 API 密钥。**这是一个危险操作，请谨慎使用。**

### `1 create_random_projects.sh`

项目创建脚本。根据您的输入（默认为 75 个）批量创建 GCP 项目。项目名称是随机生成的，以避免冲突。此脚本只创建项目，不进行其他操作。

### `2 enable_all_projects_api.sh`

API 启用脚本。为账户下的所有项目批量启用 Gemini API (`generativelanguage.googleapis.com`, `geminicloudassist.googleapis.com`, `cloudaicompanion.googleapis.com`)。

### `3 get_or_create_keys.sh`

密钥提取/创建脚本。遍历所有项目：
*   如果项目已有 API 密钥，则直接读取并记录。
*   如果项目没有 API 密钥，则先为该项目启用 `generativelanguage.googleapis.com` API，然后创建一个新的 API 密钥。
*   所有获取到的密钥最终会保存在 `key_all_projects.csv` 文件中。

## 远程执行

您可以通过 `curl` 直接从 GitHub 远程执行这些脚本。

**⚠️ 安全警告: 从互联网直接通过管道执行脚本可能存在安全风险。请确保您信任脚本的来源 (`fuyn101/SillyTavern-Staff`)。**

**注意:** 当前仓库中的脚本文件名包含数字前缀和空格。以下是正确的远程执行命令。

```bash
# 远程执行主菜单脚本 (推荐)
# 文件名: test.sh
curl -sSL "https://raw.githubusercontent.com/fuyn101/SillyTavern-Staff/main/gcp_script/test.sh" | bash

# 远程执行密钥清理脚本 (危险)
# 文件名: 0 delete_all_api_keys.sh
curl -sSL "https://raw.githubusercontent.com/fuyn101/SillyTavern-Staff/main/gcp_script/0%20delete_all_api_keys.sh" | bash

# 远程执行项目创建脚本
# 文件名: 1 create_random_projects.sh
curl -sSL "https://raw.githubusercontent.com/fuyn101/SillyTavern-Staff/main/gcp_script/1%20create_random_projects.sh" | bash

# 远程执行 API 启用脚本
# 文件名: 2 enable_all_projects_api.sh
curl -sSL "https://raw.githubusercontent.com/fuyn101/SillyTavern-Staff/main/gcp_script/2%20enable_all_projects_api.sh" | bash

# 远程执行密钥提取/创建脚本
# 文件名: 3 get_or_create_keys.sh
curl -sSL "https://raw.githubusercontent.com/fuyn101/SillyTavern-Staff/main/gcp_script/3%20get_or_create_keys.sh" | bash


```
**注意:** 远程执行时，脚本将在您的本地环境中运行，并使用您当前的 `gcloud` 身份验证信息。生成的文件（如 `key_all_projects.csv`）也会保存在您执行命令的当前目录。
