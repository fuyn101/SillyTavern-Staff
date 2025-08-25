#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CharacterBookWidget.py
世界书管理界面
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QSplitter, QLabel, QLineEdit, QGroupBox
)
from PySide6.QtCore import Qt
from typing import Any, Dict, List, Optional

from BookEntryEditorWidget import BookEntryEditorWidget

class CharacterBookWidget(QWidget):
    """世界书管理界面"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.book_data: Dict[str, Any] = {}
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        
        # 世界书名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("世界书名称:"))
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        main_layout.addLayout(name_layout)

        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # 左侧：条目列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.entry_list = QListWidget()
        self.entry_list.itemClicked.connect(self.on_entry_selected)
        left_layout.addWidget(self.entry_list)

        # 条目操作按钮
        entry_button_layout = QHBoxLayout()
        add_entry_btn = QPushButton("添加条目")
        add_entry_btn.clicked.connect(self.add_entry)
        remove_entry_btn = QPushButton("删除条目")
        remove_entry_btn.clicked.connect(self.remove_entry)
        entry_button_layout.addWidget(add_entry_btn)
        entry_button_layout.addWidget(remove_entry_btn)
        left_layout.addLayout(entry_button_layout)

        splitter.addWidget(left_widget)

        # 右侧：条目编辑器
        self.entry_editor = BookEntryEditorWidget()
        splitter.addWidget(self.entry_editor)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

    def load_book(self, book_data: Optional[Dict[str, Any]]):
        """加载世界书数据"""
        self.book_data = book_data or {"name": "", "entries": []}
        self.name_edit.setText(self.book_data.get("name", ""))
        self.refresh_entry_list()

    def refresh_entry_list(self):
        """刷新条目列表"""
        self.entry_list.clear()
        for i, entry in enumerate(self.book_data.get("entries", [])):
            comment = entry.get("comment", f"条目 {i+1}")
            item = QListWidgetItem(comment)
            self.entry_list.addItem(item)

    def on_entry_selected(self, item: QListWidgetItem):
        """当一个条目被选中时"""
        # 保存当前正在编辑的条目
        self.save_current_entry()
        
        row = self.entry_list.row(item)
        if 0 <= row < len(self.book_data.get("entries", [])):
            entry_data = self.book_data["entries"][row]
            self.entry_editor.load_entry(entry_data)

    def save_current_entry(self):
        """保存当前在编辑器中的条目"""
        current_row = self.entry_list.currentRow()
        if 0 <= current_row < len(self.book_data.get("entries", [])):
            updated_data = self.entry_editor.get_entry_data()
            self.book_data["entries"][current_row] = updated_data
            # 更新列表中的显示文本
            item = self.entry_list.item(current_row)
            if item:
                item.setText(updated_data.get("comment", f"条目 {current_row + 1}"))

    def add_entry(self):
        """添加一个新条目"""
        self.save_current_entry() # 保存上一个
        
        new_entry = self.get_default_entry()
        if "entries" not in self.book_data:
            self.book_data["entries"] = []
        self.book_data["entries"].append(new_entry)
        
        self.refresh_entry_list()
        self.entry_list.setCurrentRow(len(self.book_data["entries"]) - 1)
        self.entry_editor.load_entry(new_entry)

    def remove_entry(self):
        """删除选中的条目"""
        current_row = self.entry_list.currentRow()
        if 0 <= current_row < len(self.book_data.get("entries", [])):
            del self.book_data["entries"][current_row]
            self.refresh_entry_list()
            # 清空编辑器
            self.entry_editor.load_entry({})

    def get_book_data(self) -> Dict[str, Any]:
        """获取完整的世界书数据"""
        self.save_current_entry() # 确保最后一个编辑的条目被保存
        self.book_data["name"] = self.name_edit.text()
        return self.book_data

    def get_default_entry(self) -> Dict[str, Any]:
        """获取一个默认的条目结构"""
        return {
            "id": len(self.book_data.get("entries", [])),
            "keys": [],
            "secondary_keys": [],
            "comment": "新条目",
            "content": "",
            "constant": False,
            "selective": True,
            "insertion_order": 100,
            "enabled": True,
            "position": "before_char",
            "use_regex": True,
            "extensions": {
                "position": 0,
                "exclude_recursion": False,
                "display_index": 0,
                "probability": 100,
                "useProbability": True,
                "depth": 4,
                "selectiveLogic": 0,
                "group": "",
                "group_override": False,
                "group_weight": 100,
                "prevent_recursion": False,
                "delay_until_recursion": False,
                "scan_depth": None,
                "match_whole_words": None,
                "use_group_scoring": False,
                "case_sensitive": None,
                "automation_id": "",
                "role": 0,
                "vectorized": False,
                "sticky": 0,
                "cooldown": 0,
                "delay": 0,
                "match_persona_description": False,
                "match_character_description": False,
                "match_character_personality": False,
                "match_character_depth_prompt": False,
                "match_scenario": False,
                "match_creator_notes": False,
                "triggers": [],
                "ignore_budget": False
            }
        }