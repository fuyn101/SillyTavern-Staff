#!/usr/bin/env python3
"""
CharacterCardV3 JSON Editor
使用 PySide6 创建的可视化编辑器
支持编辑和保存 CharacterCardV3 格式的JSON文件
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QAction, QTextCursor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QListWidget, QListWidgetItem,
    QTabWidget, QScrollArea, QGroupBox, QSpinBox, QMessageBox, QFileDialog,
    QSplitter, QFrame, QDialog
)

# 从共享模块导入UI控件
from ui_widgets import MarkdownEditorWidget, TagListWidget, MarkdownTagListWidget, AssetsWidget
from CharacterBookWidget import CharacterBookWidget


class CharacterCardEditor(QMainWindow):
    """CharacterCardV3 编辑器主窗口"""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.data = self.get_default_data()
        self.setup_ui()
        self.setup_menu()
        self.new_file()  # 启动时创建一个新文件
        
    def get_default_data(self) -> Dict[str, Any]:
        """获取默认的角色卡数据"""
        return {
            "spec": "chara_card_v3",
            "spec_version": "3.0",
            "data": {
                "name": "",
                "description": "",
                "tags": [],
                "creator": "",
                "character_version": "1.0",
                "mes_example": "",
                "extensions": {},
                "system_prompt": "",
                "post_history_instructions": "",
                "first_mes": "",
                "alternate_greetings": [],
                "personality": "",
                "scenario": "",
                "creator_notes": "",
                "nickname": "",
                "source": [],
                "group_only_greetings": [],
                "creation_date": int(datetime.now().timestamp()),
                "modification_date": int(datetime.now().timestamp()),
                "assets": [],
                "character_book": {
                    "name": "",
                    "entries": []
                }
            }
        }
        
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("CharacterCardV3 JSON Editor")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧编辑区域
        edit_widget = self.create_edit_widget()
        splitter.addWidget(edit_widget)
        
        # 右侧JSON预览
        preview_widget = self.create_preview_widget()
        splitter.addWidget(preview_widget)
        
        # 设置分割比例
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
        # 自动保存计时器
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(30000)  # 30秒自动保存
        
    def create_edit_widget(self) -> QWidget:
        """创建编辑区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 基本信息选项卡
        self.basic_tab = self.create_basic_tab()
        self.tab_widget.addTab(self.basic_tab, "基本信息")
        
        # 对话内容选项卡
        self.dialog_tab = self.create_dialog_tab()
        self.tab_widget.addTab(self.dialog_tab, "对话内容")
        
        # 高级选项选项卡
        self.advanced_tab = self.create_advanced_tab()
        self.tab_widget.addTab(self.advanced_tab, "高级选项")

        # 世界书选项卡
        self.book_tab = CharacterBookWidget()
        self.tab_widget.addTab(self.book_tab, "世界书")
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_file)
        
        self.load_btn = QPushButton("加载")
        self.load_btn.clicked.connect(self.load_file)
        
        self.new_btn = QPushButton("新建")
        self.new_btn.clicked.connect(self.new_file)
        
        button_layout.addWidget(self.new_btn)
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        return widget
        
    def create_basic_tab(self) -> QWidget:
        """创建基本信息选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 基本字段
        self.name_edit = QLineEdit()
        self.creator_edit = QLineEdit()
        self.character_version_edit = QLineEdit()
        self.nickname_edit = QLineEdit()
        
        scroll_layout.addWidget(QLabel("角色名称:"))
        scroll_layout.addWidget(self.name_edit)
        scroll_layout.addWidget(QLabel("创建者:"))
        scroll_layout.addWidget(self.creator_edit)
        scroll_layout.addWidget(QLabel("角色版本:"))
        scroll_layout.addWidget(self.character_version_edit)
        scroll_layout.addWidget(QLabel("昵称:"))
        scroll_layout.addWidget(self.nickname_edit)
        
        # 描述
        scroll_layout.addWidget(QLabel("角色描述:"))
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        scroll_layout.addWidget(self.description_edit)
        
        # 个性
        scroll_layout.addWidget(QLabel("个性:"))
        self.personality_edit = QTextEdit()
        self.personality_edit.setMaximumHeight(100)
        scroll_layout.addWidget(self.personality_edit)
        
        # 标签和来源
        self.tags_widget = TagListWidget("标签")
        scroll_layout.addWidget(self.tags_widget)
        
        self.source_widget = TagListWidget("来源")
        scroll_layout.addWidget(self.source_widget)
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        return widget
        
    def create_dialog_tab(self) -> QWidget:
        """创建对话内容选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 场景
        scroll_layout.addWidget(QLabel("场景设定:"))
        self.scenario_edit = QTextEdit()
        self.scenario_edit.setMaximumHeight(80)
        scroll_layout.addWidget(self.scenario_edit)
        
        # 第一条消息
        scroll_layout.addWidget(QLabel("第一条消息:"))
        self.first_mes_editor = MarkdownEditorWidget("输入角色的第一条消息")
        scroll_layout.addWidget(self.first_mes_editor)
        
        # 示例对话
        scroll_layout.addWidget(QLabel("示例对话:"))
        self.mes_example_editor = MarkdownEditorWidget("输入示例对话内容")
        scroll_layout.addWidget(self.mes_example_editor)
        
        # 备选问候语
        self.alternate_greetings_widget = MarkdownTagListWidget("备选问候语")
        scroll_layout.addWidget(self.alternate_greetings_widget)
        
        # 群聊专用问候语
        self.group_only_greetings_widget = MarkdownTagListWidget("群聊专用问候语")
        scroll_layout.addWidget(self.group_only_greetings_widget)
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        return widget
        
    def create_advanced_tab(self) -> QWidget:
        """创建高级选项选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 系统提示
        scroll_layout.addWidget(QLabel("系统提示:"))
        self.system_prompt_edit = QTextEdit()
        self.system_prompt_edit.setMaximumHeight(80)
        scroll_layout.addWidget(self.system_prompt_edit)
        
        # 历史后指令
        scroll_layout.addWidget(QLabel("历史后指令:"))
        self.post_history_instructions_edit = QTextEdit()
        self.post_history_instructions_edit.setMaximumHeight(80)
        scroll_layout.addWidget(self.post_history_instructions_edit)
        
        # 创建者注释
        scroll_layout.addWidget(QLabel("创建者注释:"))
        self.creator_notes_edit = QTextEdit()
        self.creator_notes_edit.setMaximumHeight(80)
        scroll_layout.addWidget(self.creator_notes_edit)
        
        # 资源文件
        self.assets_widget = AssetsWidget()
        scroll_layout.addWidget(self.assets_widget)
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        return widget
        
    def create_preview_widget(self) -> QWidget:
        """创建JSON预览区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("JSON 预览:"))
        
        self.json_preview = QTextEdit()
        self.json_preview.setReadOnly(True)
        self.json_preview.setFont(QFont("Consolas", 10))
        layout.addWidget(self.json_preview)
        
        # 更新预览按钮
        update_btn = QPushButton("更新预览")
        update_btn.clicked.connect(self.update_preview)
        layout.addWidget(update_btn)
        
        return widget
        
    def setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        new_action = QAction('新建', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction('打开', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.load_file)
        file_menu.addAction(open_action)
        
        save_action = QAction('保存', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction('另存为', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
    def load_data_to_ui(self):
        """将数据加载到UI"""
        data = self.data.get('data', {})
        
        # 基本信息
        self.name_edit.setText(data.get('name', ''))
        self.creator_edit.setText(data.get('creator', ''))
        self.character_version_edit.setText(data.get('character_version', ''))
        self.nickname_edit.setText(data.get('nickname', ''))
        self.description_edit.setPlainText(data.get('description', ''))
        self.personality_edit.setPlainText(data.get('personality', ''))
        
        # 对话内容
        self.scenario_edit.setPlainText(data.get('scenario', ''))
        self.first_mes_editor.setPlainText(data.get('first_mes', ''))
        self.mes_example_editor.setPlainText(data.get('mes_example', ''))
        
        # 高级选项
        self.system_prompt_edit.setPlainText(data.get('system_prompt', ''))
        self.post_history_instructions_edit.setPlainText(data.get('post_history_instructions', ''))
        self.creator_notes_edit.setPlainText(data.get('creator_notes', ''))
        
        # 列表数据
        self.tags_widget.items = data.get('tags', []).copy()
        self.tags_widget.load_items()
        
        self.source_widget.items = data.get('source', []).copy()
        self.source_widget.load_items()
        
        self.alternate_greetings_widget.items = data.get('alternate_greetings', []).copy()
        self.alternate_greetings_widget.load_items()
        
        self.group_only_greetings_widget.items = data.get('group_only_greetings', []).copy()
        self.group_only_greetings_widget.load_items()
        
        # 资源
        self.assets_widget.assets = data.get('assets', []).copy()
        self.assets_widget.load_assets()

        # 世界书
        self.book_tab.load_book(data.get('character_book'))
        
        self.update_preview()
        
    def collect_data_from_ui(self) -> Dict[str, Any]:
        """从UI收集数据"""
        data = self.data.copy()
        
        # 更新修改时间
        data['data']['modification_date'] = int(datetime.now().timestamp())
        
        # 基本信息
        data['data']['name'] = self.name_edit.text()
        data['data']['creator'] = self.creator_edit.text()
        data['data']['character_version'] = self.character_version_edit.text()
        data['data']['nickname'] = self.nickname_edit.text()
        data['data']['description'] = self.description_edit.toPlainText()
        data['data']['personality'] = self.personality_edit.toPlainText()
        
        # 对话内容
        data['data']['scenario'] = self.scenario_edit.toPlainText()
        data['data']['first_mes'] = self.first_mes_editor.toPlainText()
        data['data']['mes_example'] = self.mes_example_editor.toPlainText()
        
        # 高级选项
        data['data']['system_prompt'] = self.system_prompt_edit.toPlainText()
        data['data']['post_history_instructions'] = self.post_history_instructions_edit.toPlainText()
        data['data']['creator_notes'] = self.creator_notes_edit.toPlainText()
        
        # 列表数据
        data['data']['tags'] = self.tags_widget.get_items()
        data['data']['source'] = self.source_widget.get_items()
        data['data']['alternate_greetings'] = self.alternate_greetings_widget.get_items()
        data['data']['group_only_greetings'] = self.group_only_greetings_widget.get_items()
        data['data']['assets'] = self.assets_widget.get_assets()
        
        # 世界书
        data['data']['character_book'] = self.book_tab.get_book_data()

        return data
        
    def update_preview(self):
        """更新JSON预览"""
        try:
            current_data = self.collect_data_from_ui()
            json_str = json.dumps(current_data, ensure_ascii=False, indent=2)
            self.json_preview.setPlainText(json_str)
        except Exception as e:
            self.json_preview.setPlainText(f"JSON预览错误: {str(e)}")
            
    def new_file(self):
        """新建文件"""
        self.data = self.get_default_data()
        self.current_file = None
        self.load_data_to_ui()
        self.statusBar().showMessage("已创建新文件")
        
    def load_file(self):
        """加载文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载角色卡文件", "", "JSON files (*.json);;All files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                self.current_file = file_path
                self.load_data_to_ui()
                self.statusBar().showMessage(f"已加载: {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"加载文件失败: {str(e)}")
                
    def _write_to_file(self, file_path: str) -> bool:
        """将当前UI数据写入指定文件。"""
        try:
            current_data = self.collect_data_from_ui()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(current_data, f, ensure_ascii=False, indent=2)
            
            self.data = current_data
            self.current_file = file_path
            return True
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存文件失败: {str(e)}")
            return False

    def save_file(self):
        """保存文件"""
        if not self.current_file:
            self.save_file_as()
            return
        
        if self._write_to_file(self.current_file):
            self.statusBar().showMessage(f"已保存: {self.current_file}")
            
    def save_file_as(self):
        """另存为"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存角色卡文件", "", "JSON files (*.json);;All files (*.*)"
        )
        
        if file_path:
            if self._write_to_file(file_path):
                self.statusBar().showMessage(f"已保存: {file_path}")
                
    def auto_save(self):
        """自动保存"""
        if self.current_file:
            try:
                # 使用一个简化的保存逻辑，避免在自动保存时弹出对话框
                current_data = self.collect_data_from_ui()
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    json.dump(current_data, f, ensure_ascii=False, indent=2)
                self.data = current_data
                self.statusBar().showMessage(f"自动保存于 {datetime.now().strftime('%H:%M:%S')}")
            except Exception as e:
                self.statusBar().showMessage(f"自动保存失败: {e}")
                
    def closeEvent(self, event):
        """关闭事件，确保在关闭前保存"""
        if self.current_file:
            self._write_to_file(self.current_file)
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("CharacterCardV3 Editor")
    app.setApplicationVersion("1.0.0")
    
    # 设置应用图标（如果有的话）
    # app.setWindowIcon(QIcon("icon.png"))
    
    window = CharacterCardEditor()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()