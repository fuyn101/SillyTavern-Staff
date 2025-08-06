# TwoPage 应用程序文档

## 概述

TwoPage 是一个基于 PySide6 的双页面 GUI 应用程序，用于管理和编辑 AI 模型的提示词和设置。该应用程序采用左右双面板设计，允许用户同时编辑两个不同的 JSON 配置文件，便于对比和同步配置。

应用程序主要依赖两个核心组件：
1. **提示词管理模块** - 用于创建和管理 AI 模型的提示词
2. **设置管理模块** - 用于配置 AI 模型的各种参数

## 应用程序结构

### 主要类

#### MainComponent 类
`MainComponent` 是应用程序的核心组件类，代表一个完整的编辑界面。每个 MainComponent 实例包含以下功能：

- **文件操作工具栏**：打开、保存、另存为功能
- **标签页界面**：
  - 提示词管理标签页：用于管理 AI 模型的提示词
  - 设置标签页：用于配置模型参数和文本参数

##### 属性
- `json_data`：当前加载的 JSON 数据
- `file_path`：当前文件路径
- `prompts_tab_editor`：提示词标签页编辑器实例
- `merged_settings_editor`：设置标签页编辑器实例

##### 主要方法
- `init_ui()`：初始化用户界面
- `create_toolbar(toolbar_layout)`：创建工具栏按钮
- `create_main_area()`：创建主工作区
- `open_file()`：打开 JSON 文件
- `save_file()`：保存 JSON 文件
- `save_as_file()`：另存为 JSON 文件
- `populate_fields()`：根据 JSON 数据填充界面字段
- `update_json_data()`：将界面数据更新到 JSON 对象中

#### TwoMainComponentsEditor 类
`TwoMainComponentsEditor` 是主窗口类，管理左右两个 `MainComponent` 实例。

##### 属性
- `left_component`：左侧主组件
- `right_component`：右侧主组件
- `left_json_data`：左侧组件的 JSON 数据
- `right_json_data`：右侧组件的 JSON 数据

##### 主要方法
- `init_ui()`：初始化用户界面
- `create_main_area()`：创建主工作区，包含左右两个组件
- `open_file_callback(component)`：打开文件的回调函数
- `save_file_callback(component)`：保存文件的回调函数
- `save_as_file_callback(component)`：另存为文件的回调函数

## 界面布局

应用程序采用水平分割布局，左右两个面板分别包含一个完整的 `MainComponent` 实例。

```
+-------------------------------------------------------------+
| 双主组件编辑器                                               |
+----------------------+-------------------+------------------+
| 工具栏               |                   |                  |
| [打开] [保存] [另存为] |                   |                  |
+----------------------+-------------------+------------------+
|                      |                   |                  |
| +------------------+ | +---------------+ | +--------------+ |
| | 左侧主组件        | | | 提示词管理标签页 | | | 设置标签页    | |
| |                  | | +---------------+ | | +------------+ | |
| |                  | |                   | |              | |
| |                  | | +---------------+ | | +------------+ | |
| |                  | | | 设置标签页     | | |              | |
| +------------------+ | +---------------+ | |              | |
|                      |                   |                  |
| +------------------+ | +---------------+ | | +--------------+ |
| | 右侧主组件        | | | 提示词管理标签页 | | | 设置标签页    | |
| |                  | | +---------------+ | | +------------+ | |
| |                  | |                   | |              | |
| |                  | | +---------------+ | | +------------+ | |
| |                  | | | 设置标签页     | | |              | |
| +------------------+ | +---------------+ | |              | |
+----------------------+-------------------+------------------+
| 状态栏：就绪                                               |
+-------------------------------------------------------------+
```

### 工具栏功能

每个主组件都包含一个工具栏，提供以下功能：
- **打开**：加载 JSON 配置文件
- **保存**：保存当前编辑的 JSON 文件
- **另存为**：将当前配置保存为新的 JSON 文件

### 标签页功能

#### 提示词管理标签页
基于 `components.prompts_tab` 模块创建，包含：
- 提示词列表：显示所有提示词，支持拖拽排序
- 提示词编辑区域：编辑提示词的详细信息
- 变量信息表格：显示提示词中使用的变量

提示词对象包含以下字段：
- `name`：提示词名称
- `system_prompt`：是否为系统提示词
- `role`：提示词角色
- `content`：提示词内容
- `identifier`：唯一标识符
- `enabled`：是否启用
- `marker`：是否有标记

#### 设置标签页
基于 `components.merged_settings` 模块创建，包含：
- 基本参数设置：模型参数、布尔值参数和其他参数
- 文本参数设置：各种文本输入参数

基本参数包括：
- 模型参数：Temperature、Frequency Penalty、Presence Penalty 等
- 布尔值参数：Wrap in Quotes、Stream OpenAI 等
- 其他参数：Bias Preset Selected、Names Behavior 等

文本参数包括：
- 单行文本：Send If Empty、Assistant Prefill 等
- 多行文本：Impersonation Prompt、New Chat Prompt 等

## 数据管理

### JSON 数据结构

应用程序使用 JSON 格式存储配置数据，包含提示词和设置两部分信息。

### 数据同步

每个 `MainComponent` 实例通过以下两个编辑器类管理数据同步：

1. **PromptsTabEditor**：管理提示词数据与界面控件的同步
2. **MergedSettingsEditor**：管理设置数据与界面控件的同步

## 使用方法

### 启动应用程序

```python
from TwoPage import TwoMainComponentsEditor
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
editor = TwoMainComponentsEditor()
editor.showMaximized()
sys.exit(app.exec())
```

### 文件操作

1. 点击"打开"按钮加载 JSON 配置文件
2. 编辑提示词或设置参数
3. 点击"保存"按钮保存更改，或点击"另存为"保存为新文件

### 提示词管理

1. 在提示词列表中选择一个提示词进行编辑
2. 修改提示词的名称、内容等信息
3. 点击"保存提示词"按钮保存更改
4. 使用"添加"和"删除"按钮管理提示词列表

### 设置管理

1. 在设置标签页中调整模型参数
2. 修改文本参数内容
3. 所有更改会自动同步到 JSON 数据中

## 依赖组件

### 主要依赖
- PySide6.QtWidgets
- PySide6.QtCore
- components.prompts_tab
- components.prompts_tab_edit
- components.merged_settings
- components.merged_settings_edit

### 第三方库
- sys
- json

## 注意事项

1. 应用程序支持同时编辑两个不同的 JSON 配置文件
2. 所有数据更改都会实时同步到内存中的 JSON 对象
3. 提示词管理支持变量功能，可以定义和使用变量
4. 设置参数具有合理的数值范围限制
5. 应用程序会在状态栏显示操作状态信息
6. 错误处理机制会在出现异常时显示错误消息框
