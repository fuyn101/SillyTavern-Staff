# 预设管理器综合文档

## 概述

预设管理器是一个基于PySide6的桌面应用程序，用于创建和管理AI模型的预设配置。该应用程序提供了完整的GUI界面，用于管理AI模型的提示词（Prompts）和各种参数设置。

应用程序包含以下主要功能模块：
1. **主窗口管理** - 应用程序的主界面和核心逻辑
2. **提示词管理** - 创建和管理AI模型的提示词
3. **设置管理** - 配置AI模型的各种参数

## 主窗口结构

### JSONEditor 类

主窗口类 `JSONEditor` 继承自 `QMainWindow`，是整个应用程序的核心。

#### 主要功能
- 创建主窗口界面
- 管理文件的打开、保存和另存为操作
- 协调各个组件之间的数据交互

#### 初始化方法
```python
def __init__(self):
    super().__init__()
    self.json_data = {}
    self.init_ui()
```

#### UI初始化
```python
def init_ui(self):
    self.setWindowTitle("预设管理器")
    
    # 创建主组件
    self.main_component = MainComponent()
    self.setCentralWidget(self.main_component)
    
    # 创建状态栏
    self.statusBar().showMessage("就绪")
```

#### 文件操作方法
- `open_file()` - 打开JSON文件
- `save_file()` - 保存JSON文件
- `save_as_file()` - 另存为JSON文件

### MainComponent 类

`MainComponent` 类是主窗口的核心组件，继承自 `QWidget`。

#### 初始化方法
```python
def __init__(
    self, parent=None, open_callback=None, save_callback=None, save_as_callback=None
):
    super().__init__(parent)
    self.json_data = {}
    self.file_path = None
    self.open_callback = open_callback
    self.save_callback = save_callback
    self.save_as_callback = save_as_callback
    # 创建提示词标签页编辑器实例
    self.prompts_tab_editor = PromptsTabEditor(self)
    # 创建设置标签页编辑器实例
    self.merged_settings_editor = MergedSettingsEditor(self)
    self.init_ui()
```

#### UI创建
- `create_toolbar()` - 创建工具栏（打开、保存、另存为按钮）
- `create_main_area()` - 创建主工作区，包含标签页

#### 数据管理方法
- `populate_fields()` - 根据JSON数据填充字段
- `update_json_data()` - 将当前数据更新到JSON对象

## 提示词管理模块

### 概述

提示词管理模块用于创建和管理应用程序中提示词（Prompts）的PySide6模块。该模块提供了完整的GUI组件功能，用于管理AI模型的提示词，包括界面创建和数据管理两个方面。

模块包含两个主要部分：
1. **界面创建** (`prompts_tab.py`) - 创建提示词管理界面的GUI组件
2. **数据管理** (`prompts_tab_edit.py`) - 管理提示词数据与UI控件之间的双向同步

### 界面创建组件

#### create_prompts_tab(parent)

创建并返回提示词标签页的主控件。

##### UI 结构

采用水平布局，分为左右两个主要区域：

```
+-----------------------------------------------------+
| 提示词标签页                                         |
+----------------------+----------------------------+
| 左侧：提示词列表      | 右侧：提示词编辑和变量信息   |
|                      |                              |
| +----------------+   | +-------------------------+  |
| | 提示词列表     |   | | 提示词详情              |  |
| | - 提示词1      |   | | Name: [输入框]          |  |
| | - 提示词2      |   | | System Prompt: [ ]      |  |
| | ...            |   | | Role: [输入框]          |  |
| +----------------+   | | Identifier: [输入框]    |  |
| [添加] [删除] 按钮   | | 启用: [ ]               |  |
|                      | | Content: [文本编辑器]   |  |
|                      | | Marker: [ ] [说明]      |  |
|                      | | [保存提示词] 按钮       |  |
|                      | +-------------------------+  |
|                      | +-------------------------+  |
|                      | | 变量信息                |  |
|                      | | [变量信息表格]          |  |
|                      | +-------------------------+  |
+----------------------+----------------------------+
```

##### 左侧区域 - 提示词列表

- **QListWidget**: 显示所有提示词列表
  - 支持内部拖拽重新排序
  - 连接 `currentRowChanged` 事件到 `on_prompt_selected` 处理函数
- **操作按钮**:
  - 添加按钮：连接到 `add_prompt` 方法
  - 删除按钮：连接到 `delete_prompt` 方法

##### 右侧区域 - 提示词编辑

###### 提示词详情编辑

使用 QFormLayout 组织的表单布局，包含以下字段：

- **Name**: 提示词名称（QLineEdit）
- **System Prompt**: 系统提示复选框（QCheckBox）
- **Role**: 角色信息（QLineEdit）
- **Identifier**: 唯一标识符（QLineEdit）
- **启用**: 启用状态复选框（QCheckBox）
- **Content**: 提示词内容文本编辑器（QTextEdit）
- **Marker**: 特殊标记复选框（QCheckBox）及说明文本

###### 保存功能

- **保存提示词按钮**: 连接到 `save_prompt` 方法

###### 变量信息展示

- **QTableWidget**: 显示提示词中使用的变量信息
  - 列名：所在提示词、变量名、类型、变量内容
  - 设置为只读模式
  - 连接 `cellClicked` 事件到 `on_variable_cell_clicked` 处理函数
  - 列宽固定设置

#### on_variable_cell_clicked(parent, row, column)

处理变量信息表格单元格点击事件，用于导航到对应的提示词。

##### 参数
- `parent`: 父级窗口对象
- `row`: 被点击的行索引
- `column`: 被点击的列索引

##### 功能
1. 获取被点击单元格的数据
2. 从数据中提取提示词标识符和名称
3. 在提示词列表中查找并选中对应的提示词

### 数据管理组件

#### PromptsTabEditor 类

`PromptsTabEditor` 类是用于管理提示词（prompts）编辑功能的核心组件。它提供了添加、删除、编辑和保存提示词的功能，以及管理提示词变量和显示顺序的功能。

##### 构造函数

```python
class PromptsTabEditor:
    def __init__(self, main_window):
        self.main_window = main_window
```

**参数**:
- `main_window`: 主窗口对象，包含所有UI组件和数据

##### on_prompt_selected(index)
当用户在提示词列表中选择一个提示词时调用此方法。

**参数**:
- `index` (int): 选中的提示词在列表中的索引

**功能**:
- 将选中提示词的数据显示在编辑界面中
- 更新变量信息表格

##### add_prompt()
添加一个新的提示词到列表中。

**功能**:
- 创建一个包含默认值的新提示词
- 为提示词生成唯一的UUID标识符
- 将新提示词添加到列表中并选中它
- 更新变量信息表格

##### delete_prompt()
删除当前选中的提示词。

**功能**:
- 弹出确认对话框
- 如果用户确认，则从列表中移除选中的提示词
- 更新变量信息表格

##### save_prompt()
保存当前编辑的提示词。

**功能**:
- 将编辑界面中的数据保存到提示词对象中
- 更新列表项的显示文本
- 更新变量信息表格

##### update_variables_table()
更新变量信息表格，显示所有提示词中使用的变量。

**功能**:
- 提取所有提示词中的 `setvar` 和 `getvar` 变量
- 在表格中显示变量信息，包括变量类型、名称、值和所属提示词

##### populate_prompts_fields(json_data)
根据JSON数据填充提示词字段。

**参数**:
- `json_data` (dict): 包含提示词数据的JSON对象

**功能**:
- 根据 `character_id = 100001` 的顺序信息排列提示词
- 将提示词数据显示在列表中

##### update_prompts_data(json_data)
将当前提示词数据更新到JSON数据中。

**参数**:
- `json_data` (dict): 要更新的JSON对象

**功能**:
- 将当前提示词列表保存到JSON数据中
- 更新提示词顺序信息

### 数据结构

#### 提示词对象
每个提示词包含以下字段：

- `name` (str): 提示词名称
- `system_prompt` (bool): 是否为系统提示词
- `role` (str): 提示词角色（如 "system"）
- `content` (str): 提示词内容
- `identifier` (str): 唯一标识符（UUID格式）
- `enabled` (bool): 是否启用
- `marker` (bool): 是否有标记

#### 变量信息表格数据

表格每行包含以下信息：
- 所在提示词: 包含该变量的提示词名称
- 变量名: 变量的名称
- 类型: 变量的类型
- 变量内容: 变量的具体内容

#### 变量管理

该类支持两种类型的变量：

1. **setvar**: 定义变量，格式为 `{{setvar::变量名::变量值}}`
2. **getvar**: 使用变量，格式为 `{{getvar::变量名}}`

变量信息会显示在专门的表格中，方便用户查看和管理。

### 使用方法

#### 创建提示词标签页

```python
# 在主窗口中创建提示词标签页
from components.prompts_tab import create_prompts_tab

prompts_tab = create_prompts_tab(self)
tab_widget.addTab(prompts_tab, "提示词")

# 需要确保 parent 对象具有以下属性和方法：
# - prompts_tab_editor: 包含 on_prompt_selected, add_prompt, delete_prompt, save_prompt 方法的对象
```

#### 管理提示词数据

```python
# 创建编辑器实例
editor = PromptsTabEditor(main_window)

# 添加新提示词
editor.add_prompt()

# 保存当前提示词
editor.save_prompt()

# 删除选中的提示词
editor.delete_prompt()

# 填充提示词字段
editor.populate_prompts_fields(json_data)

# 更新提示词数据
editor.update_prompts_data(json_data)
```

### 依赖组件

#### UI 控件

- QWidget
- QVBoxLayout, QHBoxLayout, QFormLayout
- QLabel
- QLineEdit
- QTextEdit
- QCheckBox
- QPushButton
- QListWidget
- QTableWidget
- QHeaderView
- QMessageBox

#### 事件处理

- `parent.prompts_tab_editor.on_prompt_selected`: 提示词选择事件
- `parent.prompts_tab_editor.add_prompt`: 添加提示词事件
- `parent.prompts_tab_editor.delete_prompt`: 删除提示词事件
- `parent.prompts_tab_editor.save_prompt`: 保存提示词事件

### 注意事项

1. 所有控件都作为父对象的属性创建，便于在其他地方访问和修改
2. 提示词对象使用UUID格式的identifier确保唯一性
3. 提示词列表支持拖拽排序
4. 变量信息表格为只读模式，点击可导航到对应的提示词
5. 数据管理类依赖于主窗口对象包含相应的UI控件
6. 提示词顺序信息使用 character_id = 100001 进行管理

## 设置管理模块

### 概述

设置管理模块是一个用于创建和管理AI模型设置界面的PySide6模块。该模块提供了完整的GUI组件功能，用于配置AI模型的各种参数，包括界面创建和数据管理两个方面。

模块包含两个主要部分：
1. **界面创建** (`merged_settings.py`) - 创建模型参数设置和文本参数设置的GUI组件
2. **数据管理** (`merged_settings_edit.py`) - 管理设置数据与UI控件之间的双向同步

### 界面创建组件

该部分包含三个主要函数：

1. `create_basic_tab(parent)` - 创建基本参数设置标签页
2. `create_text_tab(parent)` - 创建文本参数设置标签页
3. `create_merged_settings(parent)` - 合并基本和文本设置的主函数

#### create_basic_tab(parent)

创建包含模型参数、布尔值参数和其他参数的基本设置标签页。

##### 参数组

###### 模型参数组
包含以下数值型参数：
- **Temperature**: 控制输出的随机性，范围 0.0-2.0
- **Frequency Penalty**: 控制重复词频率惩罚，范围 -2.0-2.0
- **Presence Penalty**: 控制重复话题惩罚，范围 -2.0-2.0
- **Top P**: 核采样参数，范围 0.0-1.0
- **Top K**: 限制考虑的词汇数量，范围 0-1000
- **Top A**: 自适应采样参数，范围 0.0-1.0
- **Min P**: 最小概率阈值，范围 0.0-1.0
- **Repetition Penalty**: 重复惩罚因子，范围 0.0-2.0
- **OpenAI Max Context**: OpenAI 最大上下文长度，范围 0-9999999
- **OpenAI Max Tokens**: OpenAI 最大令牌数，范围 0-999999
- **Seed**: 随机种子，范围 -1-999999

###### 布尔值参数组
包含以下复选框选项：
- **Wrap in Quotes**: 是否用引号包装内容
- **Max Context Unlocked**: 是否解锁最大上下文限制
- **Stream OpenAI**: 是否流式传输 OpenAI 响应
- **Show External Models**: 是否显示外部模型
- **Claude Use Sysprompt**: Claude 是否使用系统提示
- **Squash System Messages**: 是否压缩系统消息
- **Image Inlining**: 是否内联图像
- **Bypass Status Check**: 是否绕过状态检查
- **Continue Prefill**: 是否继续预填充

###### 其他参数组
包含以下特殊参数：
- **Bias Preset Selected**: 偏置预设选择（默认/低/中/高）
- **Names Behavior**: 名称行为设置，范围 0-10
- **N**: 生成数量，范围 1-10

#### create_text_tab(parent)

创建包含各种文本输入参数的设置标签页。

##### 文本参数
- **Send If Empty**: 当输入为空时发送的内容
- **Assistant Prefill**: 助手预填充内容
- **Assistant Impersonation**: 助手模拟内容
- **Continue Postfix**: 继续后缀内容

##### 多行文本参数
- **Impersonation Prompt**: 模拟提示词（多行文本）
- **New Chat Prompt**: 新聊天提示词（多行文本）
- **New Group Chat Prompt**: 新群聊提示词（多行文本）
- **New Example Chat Prompt**: 新示例聊天提示词（多行文本）
- **Continue Nudge Prompt**: 继续提示词（多行文本）
- **Group Nudge Prompt**: 群组提示词（多行文本）

#### create_merged_settings(parent)

主函数，将基本设置和文本设置合并到一个水平布局中，创建完整的设置界面。

### 数据管理组件

#### MergedSettingsEditor 类

`MergedSettingsEditor` 是一个用于管理应用程序设置的编辑器类。它负责将 JSON 格式的设置数据与用户界面控件进行双向同步。

##### 构造函数

```python
class MergedSettingsEditor:
    def __init__(self, main_window):
        self.main_window = main_window
```

**参数**:
- `main_window`: 主窗口对象，包含所有需要同步的UI控件

##### populate_settings_fields(json_data)

将JSON数据填充到UI控件中。

**参数**:
- `json_data` (dict): 包含设置数据的字典

**功能**:
1. 设置所有数值型参数（temperature, frequency_penalty, presence_penalty等）
2. 设置所有布尔型参数（复选框状态）
3. 设置所有文本参数（单行和多行文本）
4. 设置下拉选择和其他特殊参数

##### update_settings_data(json_data)

从UI控件收集数据并更新JSON对象。

**参数**:
- `json_data` (dict): 要更新的设置数据字典

**功能**:
与 `populate_settings_fields` 相反，此方法从UI控件中读取值并更新传入的JSON对象。

### 使用方法

#### 创建设置界面

```python
# 在主窗口或父组件中
from components.merged_settings import create_merged_settings

# 创建设置界面
settings_widget = create_merged_settings(self)

# 将设置界面添加到主布局中
main_layout.addWidget(settings_widget)
```

#### 管理设置数据

```python
# 创建编辑器实例
editor = MergedSettingsEditor(main_window)

# 填充设置
editor.populate_settings_fields(settings_dict)

# 更新设置
editor.update_settings_data(settings_dict)
```

### 依赖

- PySide6.QtWidgets

### 注意事项

1. 所有控件都作为父对象的属性创建，便于在其他地方访问和修改
2. 所有数值输入都有合理的范围限制
3. 多行文本框设置了最大高度以优化界面布局
4. 使用了水平布局来并排显示基本设置和文本设置
5. 数据管理类依赖于主窗口对象包含相应的UI控件

## 数据流和交互

### 应用程序启动流程
1. 创建 QApplication 实例
2. 创建 JSONEditor 主窗口
3. 解析命令行参数（如果有的话）并尝试打开指定文件
4. 显示主窗口并启动事件循环

### 文件操作流程
1. **打开文件**:
   - 用户点击"打开"按钮或通过命令行参数指定文件
   - 读取JSON文件内容
   - 调用 `populate_fields()` 方法填充UI控件
   - 更新状态栏显示当前文件路径

2. **保存文件**:
   - 用户点击"保存"按钮
   - 调用 `update_json_data()` 方法从UI控件收集数据
   - 将数据写入当前文件（如果存在）或调用另存为功能

3. **另存为文件**:
   - 用户点击"另存为"按钮
   - 显示文件保存对话框
   - 调用 `update_json_data()` 方法从UI控件收集数据
   - 将数据写入用户选择的文件

### 数据同步机制
1. **从JSON到UI**:
   - 使用 `populate_fields()` 方法
   - 该方法调用 `merged_settings_editor.populate_settings_fields()` 和 `prompts_tab_editor.populate_prompts_fields()`

2. **从UI到JSON**:
   - 使用 `update_json_data()` 方法
   - 该方法调用 `merged_settings_editor.update_settings_data()` 和 `prompts_tab_editor.update_prompts_data()`

## 错误处理

应用程序包含基本的错误处理机制：
- 文件操作时使用 try/except 块捕获异常
- 使用 QMessageBox 显示错误信息
- 在状态栏显示操作状态

## 扩展性

该应用程序设计具有良好的扩展性：
1. 模块化设计，各个功能模块相对独立
2. 使用回调机制处理自定义文件操作
3. UI组件和数据管理分离，便于维护和扩展
4. 遵循面向对象设计原则，易于添加新功能
