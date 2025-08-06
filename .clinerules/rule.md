### 项目开发规范

1.  **终端环境**:
    *   请使用 `PowerShell` 作为开发终端。

2.  **包管理器**:
    *   项目使用 `Yarn` 进行依赖管理。

3.  **技术栈**:
    *   前端框架: `Vue 3`
    *   构建工具: `Vite`
    *   编程语言: `TypeScript`
    *   UI 库: `Naive UI`

4.  **编码风格**:
    *   强制使用组合式 API (`Composition API`)。
    *   为了便于维护，建议将功能复杂的 Vue 组件拆分成更小的、单一职责的组件。

5.  **项目结构**:
    *   `src/assets`: 存放静态资源，如图片 (`vue.svg`)、全局样式表 (`main.css`) 和默认数据 (`default.json`)。
    *   `src/components`: 存放可复用的 UI 组件，按功能模块划分。
        *   `character/`: 角色卡预览与展示相关组件 (`CharacterPreview.vue`)。
        *   `common/`: 通用基础组件目录。
        *   `editor/`: 核心编辑器相关组件，如 `CharacterEditor.vue`, `PresetEditor.vue` 等。
            *   `tabs/`: 编辑器内的具体功能标签页，如 `CharacterBasicData.vue`, `CharacterBook.vue`, `CharacterExtensions.vue`。
        *   `prompt/`: 提示词管理相关组件 (`PromptsTab.vue`)。
        *   `settings/`: 设置页面相关组件 (`MergedSettings.vue`)。
    *   `src/views`: 存放页面级组件，通常一个文件对应一个路由页面。例如 `HomeView.vue`, `CharacterEditorView.vue`, `PresetEditorView.vue`, `FileManagerView.vue`。
    *   `src/store`: 存放使用 Pinia 进行状态管理的相关模块。目前包含 `dataManager.ts` 用于处理核心数据。
    *   `src/router`: 存放 Vue Router 的路由配置 (`index.ts`)。
    *   `src/main.ts`: 应用入口文件，负责初始化 Vue 实例和路由。
    *   `src/App.vue`: 应用的根组件，负责包裹整个应用，提供 Naive UI 的全局配置（如主题、消息、对话框等），并包含顶部导航栏和路由视图。
    *   `src/style.css`: 全局基础样式。
    *   `src/vite-env.d.ts`: Vite 客户端类型定义文件。

6.  **路径别名与自动导入**:
    *   使用 `@` 作为 `src` 目录的路径别名。
    *   项目已配置 `unplugin-auto-import` 插件，可自动导入 Vue 及 Naive UI 的核心 API (如 `useDialog`, `useMessage` 等)，无需手动 `import`。
    *   项目已配置 `unplugin-vue-components` 插件，并启用了 `NaiveUiResolver`，因此 Naive UI 组件会被按需自动加载，在模板中使用时无需手动导入和注册。
