#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BookEntryEditorWidget.py
世界书条目编辑器
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QGroupBox, QFormLayout,
    QLineEdit, QTextEdit, QSpinBox, QCheckBox, QComboBox, QLabel
)
from PySide6.QtCore import Qt
from typing import Any, Dict, Optional

# 导入主应用中的自定义控件
# 从共享UI控件模块导入
from ui_widgets import MarkdownEditorWidget, TagListWidget


class BookEntryEditorWidget(QWidget):
    """单个世界书条目的编辑器"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.entry_data: Dict[str, Any] = {}
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 滚动区域，以容纳所有控件
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)
        layout = QVBoxLayout(container)

        # --- 基础设置 ---
        basic_group = QGroupBox("基础设置")
        basic_layout = QFormLayout(basic_group)

        self.comment_edit = QLineEdit()
        self.content_editor = MarkdownEditorWidget("条目内容")
        self.keys_widget = TagListWidget("主要关键字 (Keys)")
        self.secondary_keys_widget = TagListWidget("次要关键字 (Secondary Keys)")
        self.insertion_order_spinbox = QSpinBox()
        self.insertion_order_spinbox.setRange(0, 10000)
        self.position_combobox = QComboBox()
        self.position_combobox.addItems(["before_char", "after_char"]) # 根据spec
        self.enabled_checkbox = QCheckBox("启用")
        self.constant_checkbox = QCheckBox("设为常数 (Constant)")
        self.selective_checkbox = QCheckBox("设为选择性 (Selective)")
        self.use_regex_checkbox = QCheckBox("使用正则表达式")

        basic_layout.addRow("注释 (Comment):", self.comment_edit)
        basic_layout.addRow(self.keys_widget)
        basic_layout.addRow(self.secondary_keys_widget)
        basic_layout.addRow("内容 (Content):", self.content_editor)
        basic_layout.addRow("插入顺序 (Insertion Order):", self.insertion_order_spinbox)
        basic_layout.addRow("位置 (Position):", self.position_combobox)
        basic_layout.addRow(self.enabled_checkbox)
        basic_layout.addRow(self.constant_checkbox)
        basic_layout.addRow(self.selective_checkbox)
        basic_layout.addRow(self.use_regex_checkbox)
        
        layout.addWidget(basic_group)

        # --- 扩展设置 (Extensions) ---
        ext_group = QGroupBox("扩展设置 (Extensions)")
        ext_layout = QFormLayout(ext_group)

        self.depth_spinbox = QSpinBox()
        self.depth_spinbox.setRange(1, 100)
        self.probability_spinbox = QSpinBox()
        self.probability_spinbox.setRange(0, 100)
        self.use_probability_checkbox = QCheckBox("使用概率")
        self.prevent_recursion_checkbox = QCheckBox("防止递归")
        self.delay_until_recursion_checkbox = QCheckBox("延迟到递归")
        self.exclude_recursion_checkbox = QCheckBox("排除递归")
        self.role_combobox = QComboBox()
        self.role_combobox.addItems(["System", "User", "AI"]) # 0, 1, 2
        self.ignore_budget_checkbox = QCheckBox("忽略预算")

        ext_layout.addRow("扫描深度 (Depth):", self.depth_spinbox)
        ext_layout.addRow("概率 (Probability):", self.probability_spinbox)
        ext_layout.addRow(self.use_probability_checkbox)
        ext_layout.addRow(self.prevent_recursion_checkbox)
        ext_layout.addRow(self.delay_until_recursion_checkbox)
        ext_layout.addRow(self.exclude_recursion_checkbox)
        ext_layout.addRow("角色 (Role):", self.role_combobox)
        ext_layout.addRow(self.ignore_budget_checkbox)

        layout.addWidget(ext_group)

        # --- 匹配设置 (Matching) ---
        match_group = QGroupBox("匹配设置 (Matching Extensions)")
        match_layout = QFormLayout(match_group)

        self.match_persona_desc_checkbox = QCheckBox("匹配角色描述 (Persona Description)")
        self.match_char_desc_checkbox = QCheckBox("匹配人物描述 (Character Description)")
        self.match_char_pers_checkbox = QCheckBox("匹配人物个性 (Character Personality)")
        self.match_char_depth_checkbox = QCheckBox("匹配深度提示 (Character Depth Prompt)")
        self.match_scenario_checkbox = QCheckBox("匹配场景 (Scenario)")
        self.match_creator_notes_checkbox = QCheckBox("匹配创建者注释 (Creator Notes)")

        match_layout.addRow(self.match_persona_desc_checkbox)
        match_layout.addRow(self.match_char_desc_checkbox)
        match_layout.addRow(self.match_char_pers_checkbox)
        match_layout.addRow(self.match_char_depth_checkbox)
        match_layout.addRow(self.match_scenario_checkbox)
        match_layout.addRow(self.match_creator_notes_checkbox)

        layout.addWidget(match_group)

    def load_entry(self, entry_data: Dict[str, Any]):
        """将条目数据加载到UI"""
        self.entry_data = entry_data
        ext = self.entry_data.get("extensions", {})

        # 加载基础设置
        self.comment_edit.setText(self.entry_data.get("comment", ""))
        self.content_editor.setPlainText(self.entry_data.get("content", ""))
        self.keys_widget.items = self.entry_data.get("keys", []).copy()
        self.keys_widget.load_items()
        self.secondary_keys_widget.items = self.entry_data.get("secondary_keys", []).copy()
        self.secondary_keys_widget.load_items()
        self.insertion_order_spinbox.setValue(self.entry_data.get("insertion_order", 100))
        self.position_combobox.setCurrentText(self.entry_data.get("position", "before_char"))
        self.enabled_checkbox.setChecked(self.entry_data.get("enabled", True))
        self.constant_checkbox.setChecked(self.entry_data.get("constant", False))
        self.selective_checkbox.setChecked(self.entry_data.get("selective", True))
        self.use_regex_checkbox.setChecked(self.entry_data.get("use_regex", True))

        # 加载扩展设置
        self.depth_spinbox.setValue(ext.get("depth", 4))
        self.probability_spinbox.setValue(ext.get("probability", 100))
        self.use_probability_checkbox.setChecked(ext.get("useProbability", True))
        self.prevent_recursion_checkbox.setChecked(ext.get("prevent_recursion", False))
        self.delay_until_recursion_checkbox.setChecked(ext.get("delay_until_recursion", False))
        self.exclude_recursion_checkbox.setChecked(ext.get("exclude_recursion", False))
        self.role_combobox.setCurrentIndex(ext.get("role", 0))
        self.ignore_budget_checkbox.setChecked(ext.get("ignore_budget", False))

        # 加载匹配设置
        self.match_persona_desc_checkbox.setChecked(ext.get("match_persona_description", False))
        self.match_char_desc_checkbox.setChecked(ext.get("match_character_description", False))
        self.match_char_pers_checkbox.setChecked(ext.get("match_character_personality", False))
        self.match_char_depth_checkbox.setChecked(ext.get("match_character_depth_prompt", False))
        self.match_scenario_checkbox.setChecked(ext.get("match_scenario", False))
        self.match_creator_notes_checkbox.setChecked(ext.get("match_creator_notes", False))

    def get_entry_data(self) -> Dict[str, Any]:
        """从UI收集条目数据"""
        if not self.entry_data:
            return {}

        # 收集基础设置
        self.entry_data["comment"] = self.comment_edit.text()
        self.entry_data["content"] = self.content_editor.toPlainText()
        self.entry_data["keys"] = self.keys_widget.get_items()
        self.entry_data["secondary_keys"] = self.secondary_keys_widget.get_items()
        self.entry_data["insertion_order"] = self.insertion_order_spinbox.value()
        self.entry_data["position"] = self.position_combobox.currentText()
        self.entry_data["enabled"] = self.enabled_checkbox.isChecked()
        self.entry_data["constant"] = self.constant_checkbox.isChecked()
        self.entry_data["selective"] = self.selective_checkbox.isChecked()
        self.entry_data["use_regex"] = self.use_regex_checkbox.isChecked()

        # 收集扩展设置
        ext = self.entry_data.get("extensions", {})
        ext["depth"] = self.depth_spinbox.value()
        ext["probability"] = self.probability_spinbox.value()
        ext["useProbability"] = self.use_probability_checkbox.isChecked()
        ext["prevent_recursion"] = self.prevent_recursion_checkbox.isChecked()
        ext["delay_until_recursion"] = self.delay_until_recursion_checkbox.isChecked()
        ext["exclude_recursion"] = self.exclude_recursion_checkbox.isChecked()
        ext["role"] = self.role_combobox.currentIndex()
        ext["ignore_budget"] = self.ignore_budget_checkbox.isChecked()

        # 收集匹配设置
        ext["match_persona_description"] = self.match_persona_desc_checkbox.isChecked()
        ext["match_character_description"] = self.match_char_desc_checkbox.isChecked()
        ext["match_character_personality"] = self.match_char_pers_checkbox.isChecked()
        ext["match_character_depth_prompt"] = self.match_char_depth_checkbox.isChecked()
        ext["match_scenario"] = self.match_scenario_checkbox.isChecked()
        ext["match_creator_notes"] = self.match_creator_notes_checkbox.isChecked()
        
        self.entry_data["extensions"] = ext
        return self.entry_data