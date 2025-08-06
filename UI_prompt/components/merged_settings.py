from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QCheckBox,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QLabel,
    QLineEdit,
    QTextEdit,
)


def create_basic_tab(parent):
    widget = QWidget()
    layout = QVBoxLayout()

    # 模型参数组
    model_group = QGroupBox("模型参数")
    model_layout = QFormLayout()

    parent.temperature_spin = QDoubleSpinBox()
    parent.temperature_spin.setRange(0.0, 2.0)
    parent.temperature_spin.setSingleStep(0.01)
    parent.temperature_spin.setValue(1.0)  # 默认值为1
    model_layout.addRow("温度:", parent.temperature_spin)

    parent.frequency_penalty_spin = QDoubleSpinBox()
    parent.frequency_penalty_spin.setRange(-2.0, 2.0)
    parent.frequency_penalty_spin.setSingleStep(0.01)
    parent.frequency_penalty_spin.setValue(0.0)  # 默认值为0
    model_layout.addRow("频率惩罚:", parent.frequency_penalty_spin)

    parent.presence_penalty_spin = QDoubleSpinBox()
    parent.presence_penalty_spin.setRange(-2.0, 2.0)
    parent.presence_penalty_spin.setSingleStep(0.01)
    parent.presence_penalty_spin.setValue(0.0)  # 默认值为0
    model_layout.addRow("存在惩罚:", parent.presence_penalty_spin)

    parent.top_p_spin = QDoubleSpinBox()
    parent.top_p_spin.setRange(0.0, 1.0)
    parent.top_p_spin.setSingleStep(0.01)
    parent.top_p_spin.setValue(1.0)  # 默认值为1
    model_layout.addRow("Top P:", parent.top_p_spin)

    parent.top_k_spin = QSpinBox()
    parent.top_k_spin.setRange(0, 1000)
    model_layout.addRow("Top K:", parent.top_k_spin)

    parent.top_a_spin = QDoubleSpinBox()
    parent.top_a_spin.setRange(0.0, 1.0)
    parent.top_a_spin.setSingleStep(0.01)
    model_layout.addRow("Top A:", parent.top_a_spin)

    parent.min_p_spin = QDoubleSpinBox()
    parent.min_p_spin.setRange(0.0, 1.0)
    parent.min_p_spin.setSingleStep(0.01)
    model_layout.addRow("Min P:", parent.min_p_spin)

    parent.repetition_penalty_spin = QDoubleSpinBox()
    parent.repetition_penalty_spin.setRange(0.0, 2.0)
    parent.repetition_penalty_spin.setSingleStep(0.01)
    model_layout.addRow("重复惩罚:", parent.repetition_penalty_spin)

    parent.openai_max_context_spin = QSpinBox()
    parent.openai_max_context_spin.setRange(512, 2000000)
    parent.openai_max_context_spin.setValue(250000)  # 默认值为250000
    model_layout.addRow("最大上下文:", parent.openai_max_context_spin)

    parent.openai_max_tokens_spin = QSpinBox()
    parent.openai_max_tokens_spin.setRange(1, 65536)
    parent.openai_max_tokens_spin.setValue(65536)  # 默认值为65536
    model_layout.addRow("最大输出内容:", parent.openai_max_tokens_spin)

    parent.seed_spin = QSpinBox()
    parent.seed_spin.setRange(-1, 999999)
    parent.seed_spin.setValue(-1)  # 默认值为-1
    model_layout.addRow("种子:", parent.seed_spin)

    model_group.setLayout(model_layout)
    layout.addWidget(model_group)

    # 布尔值参数组
    bool_group = QGroupBox("布尔值参数")
    bool_layout = QVBoxLayout()

    parent.wrap_in_quotes_check = QCheckBox("用引号包裹")
    bool_layout.addWidget(parent.wrap_in_quotes_check)

    parent.max_context_unlocked_check = QCheckBox("解锁最大上下文")
    parent.max_context_unlocked_check.setChecked(True)
    bool_layout.addWidget(parent.max_context_unlocked_check)

    parent.stream_openai_check = QCheckBox("流式传输")
    bool_layout.addWidget(parent.stream_openai_check)

    parent.show_external_models_check = QCheckBox("Show External Models")
    bool_layout.addWidget(parent.show_external_models_check)

    parent.claude_use_sysprompt_check = QCheckBox("Claude使用系统提示")
    bool_layout.addWidget(parent.claude_use_sysprompt_check)

    parent.squash_system_messages_check = QCheckBox("压缩系统消息")
    bool_layout.addWidget(parent.squash_system_messages_check)

    parent.image_inlining_check = QCheckBox("发送图片")
    bool_layout.addWidget(parent.image_inlining_check)

    parent.bypass_status_check_check = QCheckBox("Bypass Status Check")
    bool_layout.addWidget(parent.bypass_status_check_check)

    parent.continue_prefill_check = QCheckBox("Continue Prefill")
    bool_layout.addWidget(parent.continue_prefill_check)

    bool_group.setLayout(bool_layout)
    layout.addWidget(bool_group)

    # 其他参数组
    other_group = QGroupBox("其他参数")
    other_layout = QFormLayout()

    parent.bias_preset_combo = QComboBox()
    parent.bias_preset_combo.addItem("Default (none)")
    parent.bias_preset_combo.addItem("Low")
    parent.bias_preset_combo.addItem("Medium")
    parent.bias_preset_combo.addItem("High")
    other_layout.addRow("Bias Preset Selected:", parent.bias_preset_combo)

    parent.names_behavior_spin = QSpinBox()
    parent.names_behavior_spin.setRange(0, 10)
    other_layout.addRow("Names Behavior:", parent.names_behavior_spin)

    parent.n_spin = QSpinBox()
    parent.n_spin.setRange(1, 10)
    other_layout.addRow("N:", parent.n_spin)

    other_group.setLayout(other_layout)
    layout.addWidget(other_group)

    # 添加弹性空间
    layout.addStretch()

    widget.setLayout(layout)
    return widget


def create_text_tab(parent):
    widget = QWidget()
    layout = QVBoxLayout()

    # 使用表单布局来组织文本参数
    form_layout = QFormLayout()

    # 文本参数
    parent.send_if_empty_edit = QLineEdit()
    form_layout.addRow("Send If Empty:", parent.send_if_empty_edit)

    parent.assistant_prefill_edit = QLineEdit()
    form_layout.addRow("Assistant Prefill:", parent.assistant_prefill_edit)

    parent.assistant_impersonation_edit = QLineEdit()
    form_layout.addRow("Assistant Impersonation:", parent.assistant_impersonation_edit)

    parent.continue_postfix_edit = QLineEdit()
    form_layout.addRow("Continue Postfix:", parent.continue_postfix_edit)

    layout.addLayout(form_layout)

    # 多行文本参数
    parent.impersonation_prompt_edit = QTextEdit()
    parent.impersonation_prompt_edit.setMaximumHeight(100)
    parent.impersonation_prompt_edit.setPlainText(
        "[Write your next reply from the point of view of {{user}}, using the chat history so far as a guideline for the writing style of {{user}}. Write 1 reply only in internet RP style. Don't write as {{char}} or system. Don't describe actions of {{char}}.]"
    )
    layout.addWidget(QLabel("Impersonation Prompt:"))
    layout.addWidget(parent.impersonation_prompt_edit)

    parent.new_chat_prompt_edit = QTextEdit()
    parent.new_chat_prompt_edit.setMaximumHeight(100)
    layout.addWidget(QLabel("New Chat Prompt:"))
    layout.addWidget(parent.new_chat_prompt_edit)

    parent.new_group_chat_prompt_edit = QTextEdit()
    parent.new_group_chat_prompt_edit.setMaximumHeight(100)
    parent.new_group_chat_prompt_edit.setPlainText(
        "[Start a new group chat. Group members: {{group}}]"
    )
    layout.addWidget(QLabel("New Group Chat Prompt:"))
    layout.addWidget(parent.new_group_chat_prompt_edit)

    parent.new_example_chat_prompt_edit = QTextEdit()
    parent.new_example_chat_prompt_edit.setMaximumHeight(100)
    parent.new_example_chat_prompt_edit.setPlainText("[Example Chat]")
    layout.addWidget(QLabel("New Example Chat Prompt:"))
    layout.addWidget(parent.new_example_chat_prompt_edit)

    parent.continue_nudge_prompt_edit = QTextEdit()
    parent.continue_nudge_prompt_edit.setMaximumHeight(100)
    parent.continue_nudge_prompt_edit.setPlainText(
        "[Continue the following message. Do not include ANY parts of the original message. Use capitalization and punctuation as if your reply is a part of the original message: {{lastChatMessage}}]"
    )
    layout.addWidget(QLabel("Continue Nudge Prompt:"))
    layout.addWidget(parent.continue_nudge_prompt_edit)

    parent.group_nudge_prompt_edit = QTextEdit()
    parent.group_nudge_prompt_edit.setMaximumHeight(100)
    parent.group_nudge_prompt_edit.setPlainText(
        "[Write the next reply only as {{char}}.]"
    )
    layout.addWidget(QLabel("Group Nudge Prompt:"))
    layout.addWidget(parent.group_nudge_prompt_edit)

    widget.setLayout(layout)
    return widget


def create_merged_settings(parent):
    widget = QWidget()
    layout = QHBoxLayout()  # 使用水平布局实现左右划分

    # 创建基本设置面板
    basic_tab = create_basic_tab(parent)

    # 创建文本设置面板
    text_tab = create_text_tab(parent)

    # 将两个面板添加到水平布局中，实现左右划分
    layout.addWidget(basic_tab)
    layout.addWidget(text_tab)

    widget.setLayout(layout)
    return widget
