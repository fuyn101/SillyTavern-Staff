from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QCheckBox,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QTableWidget,
    QHeaderView,
    QComboBox,
    QSpinBox,
    QTabWidget,
)
from PySide6.QtCore import Qt
from .order_table import OrderTable


def on_variable_cell_clicked(parent, row, column):
    # 获取被点击单元格的数据
    item = parent.variables_table.item(row, column)
    if item is not None:
        # 从单元格数据中获取提示词标识符和名称
        data = item.data(Qt.UserRole)
        if data is not None:
            prompt_identifier, prompt_name = data

            # 在提示词列表中查找对应的提示词
            for i in range(parent.prompts_list.count()):
                list_item = parent.prompts_list.item(i)
                prompt = list_item.data(Qt.UserRole)
                if prompt.get("identifier") == prompt_identifier:
                    # 选择对应的提示词
                    parent.prompts_list.setCurrentRow(i)
                    break


def create_prompts_tab(parent):
    widget = QWidget()
    main_layout = QVBoxLayout()

    # 创建水平布局，包含提示词列表和提示词编辑
    h_layout = QHBoxLayout()

    # 左侧：提示词列表（包含启用状态）
    left_layout = QVBoxLayout()
    left_layout.addWidget(QLabel("提示词列表:"))

    parent.prompts_list = QListWidget()
    parent.prompts_list.currentRowChanged.connect(
        parent.prompts_tab_editor.on_prompt_selected
    )
    left_layout.addWidget(parent.prompts_list)

    # 添加/删除按钮
    btn_layout = QHBoxLayout()
    add_btn = QPushButton("添加")
    add_btn.clicked.connect(parent.prompts_tab_editor.add_prompt)
    delete_btn = QPushButton("删除")
    delete_btn.clicked.connect(parent.prompts_tab_editor.delete_prompt)
    btn_layout.addWidget(add_btn)
    btn_layout.addWidget(delete_btn)
    left_layout.addLayout(btn_layout)

    # 右侧：提示词编辑（包含启用状态）
    right_layout = QVBoxLayout()

    # 右侧上部分：提示词详情+content marker
    right_top_layout = QVBoxLayout()
    right_top_layout.addWidget(QLabel("提示词详情:"))

    # 使用两列布局来组织提示词参数
    prompt_details_layout = QHBoxLayout()

    # 左列
    left_column_layout = QFormLayout()
    parent.prompt_name_edit = QLineEdit()
    left_column_layout.addRow("提示词名称:", parent.prompt_name_edit)

    parent.prompt_system_prompt_check = QCheckBox("是否为标准模版默认提示词")
    left_column_layout.addRow(parent.prompt_system_prompt_check)

    # Role下拉选项
    parent.prompt_role_combo = QComboBox()
    parent.prompt_role_combo.addItems(["system", "assistant", "user"])
    left_column_layout.addRow("Role:", parent.prompt_role_combo)

    parent.prompt_identifier_edit = QLineEdit()
    left_column_layout.addRow("Identifier:", parent.prompt_identifier_edit)

    # 添加启用状态复选框
    parent.prompt_add_to_order_check = QCheckBox("是否在列表里")
    left_column_layout.addRow(parent.prompt_add_to_order_check)

    parent.prompt_enabled_check = QCheckBox("是否在列表里开启")
    left_column_layout.addRow(parent.prompt_enabled_check)

    parent.prompt_marker_check = QCheckBox("是否是图钉提示词")
    left_column_layout.addRow(parent.prompt_marker_check)
    # 右列
    right_column_layout = QFormLayout()

    parent.prompt_injection_position = QComboBox()
    parent.prompt_injection_position.addItems(["0 (相对)", "1 (深度)"])
    right_column_layout.addRow("注入位置:", parent.prompt_injection_position)

    parent.prompt_injection_depth = QSpinBox()
    parent.prompt_injection_depth.setRange(0, 100)  # 设置合理的范围
    right_column_layout.addRow("注入深度（1时使用）:", parent.prompt_injection_depth)

    parent.prompt_injection_order = QSpinBox()
    parent.prompt_injection_order.setRange(0, 9999)  # 设置合理的范围
    right_column_layout.addRow("注入顺序（1时使用）:", parent.prompt_injection_order)

    parent.prompt_forbid_overrides_check = QCheckBox("Forbid Overrides")
    right_column_layout.addRow(parent.prompt_forbid_overrides_check)

    # 将两列添加到提示词详情布局中
    prompt_details_layout.addLayout(left_column_layout)
    prompt_details_layout.addLayout(right_column_layout)
    right_top_layout.addLayout(prompt_details_layout)

    right_top_layout.addWidget(QLabel("Content:"))
    parent.prompt_content_edit = QTextEdit()
    right_top_layout.addWidget(parent.prompt_content_edit)

    save_btn = QPushButton("(编辑提示词后必须点！)      保存提示词")
    save_btn.clicked.connect(parent.prompts_tab_editor.save_prompt)
    right_top_layout.addWidget(save_btn)

    # 右侧下部分：显示变量信息和Order排序
    right_bottom_layout = QVBoxLayout()
    right_bottom_layout.addWidget(QLabel("变量信息和Order排序:"))

    # 创建Tab控件
    tab_widget = QTabWidget()

    # 创建变量信息tab
    variables_tab = QWidget()
    variables_layout = QVBoxLayout()

    # 添加筛选输入框
    filter_layout = QHBoxLayout()
    filter_layout.addWidget(QLabel("变量名筛选:"))
    parent.variable_filter_edit = QLineEdit()
    parent.variable_filter_edit.setPlaceholderText("输入变量名进行筛选...")
    # 连接文本变化事件，实现实时筛选
    parent.variable_filter_edit.textChanged.connect(
        lambda text: parent.prompts_tab_editor.filter_variables(text)
    )
    filter_layout.addWidget(parent.variable_filter_edit)

    # 添加清空筛选按钮
    clear_filter_btn = QPushButton("清空")
    clear_filter_btn.clicked.connect(lambda: parent.variable_filter_edit.clear())
    filter_layout.addWidget(clear_filter_btn)

    variables_layout.addLayout(filter_layout)

    # 创建表格来显示变量信息
    parent.variables_table = QTableWidget()
    parent.variables_table.setColumnCount(4)
    parent.variables_table.setHorizontalHeaderLabels(
        ["所在提示词", "变量名", "类型", "变量内容"]
    )
    # 设置表格为只读模式
    parent.variables_table.setEditTriggers(QTableWidget.NoEditTriggers)
    # 连接表格点击事件
    parent.variables_table.cellClicked.connect(
        lambda row, column: on_variable_cell_clicked(parent, row, column)
    )
    # 锁定列宽
    parent.variables_table.horizontalHeader().setSectionResizeMode(
        0, QHeaderView.Interactive
    )  # 所在提示词
    parent.variables_table.horizontalHeader().setSectionResizeMode(
        1, QHeaderView.Interactive
    )  # 变量名
    parent.variables_table.horizontalHeader().setSectionResizeMode(
        2, QHeaderView.Interactive
    )  # 类型
    parent.variables_table.horizontalHeader().setSectionResizeMode(
        3, QHeaderView.Interactive
    )  # 变量内容
    # 初始化变量表格列宽
    parent.variables_table.setColumnWidth(0, 200)  # 所在提示词列
    parent.variables_table.setColumnWidth(1, 200)  # 变量名列
    parent.variables_table.setColumnWidth(2, 100)  # 类型列
    parent.variables_table.setColumnWidth(3, 300)  # 变量内容列
    variables_layout.addWidget(parent.variables_table)
    variables_tab.setLayout(variables_layout)
    tab_widget.addTab(variables_tab, "变量信息")

    # 创建Order排序tab
    order_tab = QWidget()
    order_layout = QVBoxLayout()

    # 创建表格来显示Order排序
    parent.order_table = OrderTable(parent)
    parent.order_table.setColumnCount(3)
    parent.order_table.setHorizontalHeaderLabels(["提示词名称", "是否启用", "顺序"])
    # 设置表格为只读模式
    parent.order_table.setEditTriggers(QTableWidget.NoEditTriggers)
    # 锁定列宽
    parent.order_table.horizontalHeader().setSectionResizeMode(
        0, QHeaderView.Interactive
    )  # 提示词名称
    parent.order_table.horizontalHeader().setSectionResizeMode(
        1, QHeaderView.Interactive
    )  # 是否启用
    parent.order_table.horizontalHeader().setSectionResizeMode(
        2, QHeaderView.Interactive
    )  # 顺序
    # 初始化Order表格列宽
    parent.order_table.setColumnWidth(0, 200)  # 提示词名称列
    parent.order_table.setColumnWidth(1, 100)  # 是否启用列
    parent.order_table.setColumnWidth(2, 100)  # 顺序列

    # 创建"应用当前排序"按钮
    apply_order_btn = QPushButton("应用当前排序")
    apply_order_btn.clicked.connect(parent.prompts_tab_editor.apply_order_sorting)

    order_layout.addWidget(parent.order_table)
    order_layout.addWidget(apply_order_btn)
    order_tab.setLayout(order_layout)
    tab_widget.addTab(order_tab, "Order排序")

    right_bottom_layout.addWidget(tab_widget)

    # 组合右侧布局
    right_widget_top = QWidget()
    right_widget_top.setLayout(right_top_layout)
    right_widget_bottom = QWidget()
    right_widget_bottom.setLayout(right_bottom_layout)

    right_layout.addWidget(right_widget_top)
    right_layout.addWidget(right_widget_bottom)

    # 组合布局
    left_widget = QWidget()
    left_widget.setLayout(left_layout)
    right_widget = QWidget()
    right_widget.setLayout(right_layout)

    h_layout.addWidget(left_widget)
    h_layout.addWidget(right_widget)

    main_layout.addLayout(h_layout)
    widget.setLayout(main_layout)
    return widget
