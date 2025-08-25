# CharacterCardV3 可视化编辑器

这是一个使用 Python 3.12、PySide6 和 `uv` 构建的桌面应用程序，旨在提供一个用户友好的图形界面，用于创建和编辑 `CharacterCardV3` 格式的 JSON 文件。

## 核心功能

- **完整的V3规范支持**: 提供对 `CharacterCardV3` 所有标准字段的可视化编辑，包括名称、描述、问候语、系统提示等。
- **世界书 (Character Book) 管理**: 内置强大的世界书编辑器，允许用户创建、编辑和管理世界书条目，包括关键字、内容和各种高级设置。
- **Markdown 编辑与预览**: 对于 `first_mes`, `mes_example` 等支持 Markdown 的字段，提供了分栏的实时编辑和预览功能。
- **实时 JSON 预览**: 在编辑时，可以实时查看生成的 JSON 数据结构，确保格式的正确性。
- **文件操作**: 支持新建、加载、保存和另存为角色卡文件。
- **自动保存**: 开启了自动保存功能，防止意外关闭导致数据丢失。
- **模块化UI**: 界面元素被拆分为可重用的组件，便于维护和扩展。

## 模块化组件

项目采用了模块化的设计，将不同的UI功能拆分到独立的模块中：

- **`main_edit.py`**: 主应用程序窗口，整合了所有UI组件和核心逻辑。
- **`ui_widgets.py`**: 包含一系列可重用的UI控件：
    - `MarkdownEditorWidget`: 支持Markdown预览的文本编辑器。
    - `TagListWidget`: 用于管理简单的字符串列表（如标签、来源）。
    - `MarkdownTagListWidget`: 用于管理支持Markdown内容的列表（如备选问候语）。
    - `AssetsWidget`: 用于管理角色的资源文件列表。
- **`CharacterBookWidget.py`**: 实现了世界书的整体管理界面，包括条目列表和与条目编辑器的联动。
- **`BookEntryEditorWidget.py`**: 实现了世界书单个条目的详细编辑器，包含了所有基础、扩展和匹配设置。

## 如何运行

1.  **环境要求**:
    - 确保已安装 Python 3.12 或更高版本。
    - 确保已安装 `uv` 包管理器。

2.  **安装依赖**:
    - 在项目根目录下，运行 `uv sync` 来创建虚拟环境并安装 `PySide6` 等依赖。

3.  **启动应用**:
    - 使用以下命令启动编辑器：
      ```shell
      uv run python main_edit.py
      ```

## CharacterCardV3 格式参考

```typescript
interface CharacterCardV3 {
  spec: 'chara_card_v3'
  spec_version: '3.0'
  data: {
    // fields from CCV2
    name: string
    description: string
    tags: Array<string>
    creator: string
    character_version: string
    mes_example: string
    extensions: Record<string, any>
    system_prompt: string
    post_history_instructions: string
    first_mes: string
    alternate_greetings: Array<string>
    personality: string
    scenario: string

    //Changes from CCV2
    creator_notes: string
    character_book?: Lorebook

    //New fields in CCV3
    assets?: Array<{
      type: string
      uri: string
      name: string
      ext: string
    }>
    nickname?: string
    creator_notes_multilingual?: Record<string, string>
    source?: string[]
    group_only_greetings: Array<string>
    creation_date?: number
    modification_date?: number
  }
}