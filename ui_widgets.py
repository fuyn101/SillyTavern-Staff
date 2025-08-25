#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ui_widgets.py
包含应用中可重用的PySide6 UI控件。
"""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QListWidget, QListWidgetItem,
    QTabWidget, QGroupBox, QDialog
)

class MarkdownEditorWidget(QWidget):
    """Markdown编辑器，带有编辑和预览选项卡"""
    
    def __init__(self, placeholder_text: str = ""):
        super().__init__()
        self.placeholder_text = placeholder_text
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 编辑选项卡
        self.edit_tab = QWidget()
        edit_layout = QVBoxLayout(self.edit_tab)
        self.edit_text = QTextEdit()
        self.edit_text.setPlaceholderText(self.placeholder_text)
        self.edit_text.textChanged.connect(self.update_preview)
        edit_layout.addWidget(self.edit_text)
        self.tab_widget.addTab(self.edit_tab, "编辑")
        
        # 预览选项卡
        self.preview_tab = QWidget()
        preview_layout = QVBoxLayout(self.preview_tab)
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        self.tab_widget.addTab(self.preview_tab, "预览")
        
        layout.addWidget(self.tab_widget)
        
    def setPlainText(self, text: str):
        """设置文本内容"""
        self.edit_text.setPlainText(text)
        self.update_preview()
        
    def toPlainText(self) -> str:
        """获取文本内容"""
        return self.edit_text.toPlainText()
        
    def update_preview(self):
        """更新Markdown预览"""
        from markdown import markdown
        try:
            md_text = self.edit_text.toPlainText()
            html = markdown(md_text)
            self.preview_text.setHtml(html)
        except Exception as e:
            self.preview_text.setPlainText(f"渲染错误: {str(e)}")


class TagListWidget(QWidget):
    """标签列表编辑器"""
    
    def __init__(self, title: str, items: Optional[List[str]] = None):
        super().__init__()
        self.title = title
        self.items = items or []
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 添加新项目
        add_layout = QHBoxLayout()
        self.new_item_edit = QLineEdit()
        self.new_item_edit.setPlaceholderText(f"添加新的{self.title}")
        add_btn = QPushButton("添加")
        add_btn.clicked.connect(self.add_item)
        self.new_item_edit.returnPressed.connect(self.add_item)
        
        add_layout.addWidget(self.new_item_edit)
        add_layout.addWidget(add_btn)
        layout.addLayout(add_layout)
        
        # 列表
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.edit_item)
        layout.addWidget(self.list_widget)
        
        # 删除按钮
        remove_btn = QPushButton("删除选中项")
        remove_btn.clicked.connect(self.remove_item)
        layout.addWidget(remove_btn)
        
        # 加载现有项目
        self.load_items()
        
    def load_items(self):
        """加载现有项目"""
        self.list_widget.clear()
        for item in self.items:
            self.list_widget.addItem(str(item))
            
    def add_item(self):
        """添加新项目"""
        text = self.new_item_edit.text().strip()
        if text and text not in self.items:
            self.items.append(text)
            self.list_widget.addItem(text)
            self.new_item_edit.clear()
            
    def remove_item(self):
        """删除选中项目"""
        current_item = self.list_widget.currentItem()
        if current_item:
            text = current_item.text()
            if text in self.items:
                self.items.remove(text)
            self.list_widget.takeItem(self.list_widget.row(current_item))
            
    def edit_item(self, item: QListWidgetItem):
        """编辑项目"""
        old_text = item.text()
        new_text, ok = QLineEdit().text(), True  # 简化的编辑
        # 这里可以添加更复杂的编辑对话框
        
    def get_items(self) -> List[str]:
        """获取所有项目"""
        return self.items.copy()


class MarkdownTagListWidget(QWidget):
    """支持Markdown的标签列表编辑器"""
    
    def __init__(self, title: str, items: Optional[List[str]] = None):
        super().__init__()
        self.title = title
        self.items = items or []
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 添加新项目区域
        add_group = QGroupBox("添加新项目")
        add_layout = QVBoxLayout(add_group)
        
        self.new_item_editor = MarkdownEditorWidget(f"添加新的{self.title}")
        add_layout.addWidget(self.new_item_editor)
        
        add_btn = QPushButton("添加")
        add_btn.clicked.connect(self.add_item)
        add_layout.addWidget(add_btn)
        
        layout.addWidget(add_group)
        
        # 列表
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.edit_item)
        layout.addWidget(self.list_widget)
        
        # 编辑/删除按钮区域
        button_layout = QHBoxLayout()
        
        edit_btn = QPushButton("编辑选中项")
        edit_btn.clicked.connect(self.edit_selected_item)
        button_layout.addWidget(edit_btn)
        
        remove_btn = QPushButton("删除选中项")
        remove_btn.clicked.connect(self.remove_item)
        button_layout.addWidget(remove_btn)
        
        layout.addLayout(button_layout)
        
        # 加载现有项目
        self.load_items()
        
    def load_items(self):
        """加载现有项目"""
        self.list_widget.clear()
        for item in self.items:
            # 显示前100个字符作为预览
            preview = item[:100] + "..." if len(item) > 100 else item
            self.list_widget.addItem(preview)
            
    def add_item(self):
        """添加新项目"""
        text = self.new_item_editor.toPlainText().strip()
        if text and text not in self.items:
            self.items.append(text)
            self.load_items()
            self.new_item_editor.setPlainText("")
            
    def remove_item(self):
        """删除选中项目"""
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            del self.items[current_row]
            self.load_items()
            
    def edit_selected_item(self):
        """编辑选中项目"""
        current_row = self.list_widget.currentRow()
        if current_row >= 0 and current_row < len(self.items):
            # 创建编辑对话框
            dialog = QDialog(self)
            dialog.setWindowTitle(f"编辑{self.title}")
            dialog.setModal(True)
            dialog.setMinimumSize(600, 400)
            
            layout = QVBoxLayout(dialog)
            
            editor = MarkdownEditorWidget()
            editor.setPlainText(self.items[current_row])
            layout.addWidget(editor)
            
            button_layout = QHBoxLayout()
            save_btn = QPushButton("保存")
            cancel_btn = QPushButton("取消")
            
            def save_changes():
                self.items[current_row] = editor.toPlainText()
                self.load_items()
                dialog.accept()
                
            save_btn.clicked.connect(save_changes)
            cancel_btn.clicked.connect(dialog.reject)
            
            button_layout.addWidget(save_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            dialog.exec()
            
    def edit_item(self, item: QListWidgetItem):
        """双击编辑项目"""
        self.edit_selected_item()
        
    def get_items(self) -> List[str]:
        """获取所有项目"""
        return self.items.copy()


class AssetsWidget(QWidget):
    """资源文件编辑器"""
    
    def __init__(self, assets: Optional[List[Dict[str, str]]] = None):
        super().__init__()
        self.assets = assets or []
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title_label = QLabel("Assets (资源文件)")
        title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 添加资源
        add_layout = QHBoxLayout()
        self.type_edit = QLineEdit()
        self.type_edit.setPlaceholderText("类型 (如: image, audio)")
        self.uri_edit = QLineEdit()
        self.uri_edit.setPlaceholderText("URI路径")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("名称")
        self.ext_edit = QLineEdit()
        self.ext_edit.setPlaceholderText("扩展名")
        
        add_btn = QPushButton("添加资源")
        add_btn.clicked.connect(self.add_asset)
        
        add_layout.addWidget(QLabel("类型:"))
        add_layout.addWidget(self.type_edit)
        add_layout.addWidget(QLabel("URI:"))
        add_layout.addWidget(self.uri_edit)
        add_layout.addWidget(QLabel("名称:"))
        add_layout.addWidget(self.name_edit)
        add_layout.addWidget(QLabel("扩展名:"))
        add_layout.addWidget(self.ext_edit)
        add_layout.addWidget(add_btn)
        
        layout.addLayout(add_layout)
        
        # 资源列表
        self.assets_list = QListWidget()
        layout.addWidget(self.assets_list)
        
        # 删除按钮
        remove_btn = QPushButton("删除选中资源")
        remove_btn.clicked.connect(self.remove_asset)
        layout.addWidget(remove_btn)
        
        self.load_assets()
        
    def load_assets(self):
        """加载资源列表"""
        self.assets_list.clear()
        for asset in self.assets:
            display_text = f"{asset.get('type', '')}: {asset.get('name', '')} ({asset.get('uri', '')})"
            self.assets_list.addItem(display_text)
            
    def add_asset(self):
        """添加资源"""
        asset_type = self.type_edit.text().strip()
        uri = self.uri_edit.text().strip()
        name = self.name_edit.text().strip()
        ext = self.ext_edit.text().strip()
        
        if asset_type and uri:
            asset = {
                "type": asset_type,
                "uri": uri,
                "name": name,
                "ext": ext
            }
            self.assets.append(asset)
            self.load_assets()
            
            # 清空输入框
            self.type_edit.clear()
            self.uri_edit.clear()
            self.name_edit.clear()
            self.ext_edit.clear()
            
    def remove_asset(self):
        """删除资源"""
        current_row = self.assets_list.currentRow()
        if current_row >= 0:
            del self.assets[current_row]
            self.load_assets()
            
    def get_assets(self) -> List[Dict[str, str]]:
        """获取资源列表"""
        return self.assets.copy()