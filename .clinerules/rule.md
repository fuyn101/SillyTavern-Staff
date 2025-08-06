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
    *   `src/assets`: 存放静态资源，如图片、全局样式表等。
    *   `src/components`: 存放可复用的 UI 组件。
        *   `common/`: 通用基础组件。
        *   按功能模块划分目录，例如 `editor/`, `char/`。
    *   `src/views`: 存放页面级组件，通常一个文件对应一个路由页面。
    *   `src/store`: 存放使用 Pinia 进行状态管理的相关模块。
    *   `src/router`: 存放 Vue Router 的路由配置。
