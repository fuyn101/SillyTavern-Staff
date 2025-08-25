import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QTabWidget, QLineEdit, QTextEdit,
                               QListWidget, QListWidgetItem, QPushButton,
                               QLabel, QFileDialog, QMessageBox, QScrollArea,
                               QGroupBox, QSplitter, QTableWidget, QTableWidgetItem,
                               QHeaderView, QAbstractItemView, QComboBox)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QAction


class JsonEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.data = None
        self.init_ui()
        self.new_file()
        
    def init_ui(self):
        self.setWindowTitle("CharacterCardV3 Editor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create tabs for different sections
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create basic info tab
        self.basic_info_tab = QWidget()
        self.basic_info_layout = QVBoxLayout(self.basic_info_tab)
        self.create_basic_info_section()
        self.tabs.addTab(self.basic_info_tab, "Basic Info")
        
        # Create messages tab
        self.messages_tab = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_tab)
        self.create_messages_section()
        self.tabs.addTab(self.messages_tab, "Messages")
        
        # Create extensions tab
        self.extensions_tab = QWidget()
        self.extensions_layout = QVBoxLayout(self.extensions_tab)
        self.create_extensions_section()
        self.tabs.addTab(self.extensions_tab, "Extensions")
        
        # Create lorebook tab
        self.lorebook_tab = QWidget()
        self.lorebook_layout = QVBoxLayout(self.lorebook_tab)
        self.create_lorebook_section()
        self.tabs.addTab(self.lorebook_tab, "Lorebook")
        
        # Create assets tab
        self.assets_tab = QWidget()
        self.assets_layout = QVBoxLayout(self.assets_tab)
        self.create_assets_section()
        self.tabs.addTab(self.assets_tab, "Assets")
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
    def create_basic_info_section(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Spec fields
        spec_group = QGroupBox("Specification")
        spec_layout = QVBoxLayout(spec_group)
        
        self.spec_edit = QLineEdit()
        self.spec_edit.setPlaceholderText("chara_card_v3")
        spec_layout.addWidget(QLabel("Spec:"))
        spec_layout.addWidget(self.spec_edit)
        
        self.spec_version_edit = QLineEdit()
        self.spec_version_edit.setPlaceholderText("3.0")
        spec_layout.addWidget(QLabel("Spec Version:"))
        spec_layout.addWidget(self.spec_version_edit)
        
        scroll_layout.addWidget(spec_group)
        
        # Basic info fields
        basic_group = QGroupBox("Basic Information")
        basic_layout = QVBoxLayout(basic_group)
        
        self.name_edit = QLineEdit()
        basic_layout.addWidget(QLabel("Name:"))
        basic_layout.addWidget(self.name_edit)
        
        self.creator_edit = QLineEdit()
        basic_layout.addWidget(QLabel("Creator:"))
        basic_layout.addWidget(self.creator_edit)
        
        self.character_version_edit = QLineEdit()
        basic_layout.addWidget(QLabel("Character Version:"))
        basic_layout.addWidget(self.character_version_edit)
        
        self.nickname_edit = QLineEdit()
        basic_layout.addWidget(QLabel("Nickname:"))
        basic_layout.addWidget(self.nickname_edit)
        
        scroll_layout.addWidget(basic_group)
        
        # Description fields
        desc_group = QGroupBox("Descriptions")
        desc_layout = QVBoxLayout(desc_group)
        
        self.description_edit = QTextEdit()
        desc_layout.addWidget(QLabel("Description:"))
        desc_layout.addWidget(self.description_edit)
        
        self.personality_edit = QTextEdit()
        desc_layout.addWidget(QLabel("Personality:"))
        desc_layout.addWidget(self.personality_edit)
        
        self.scenario_edit = QTextEdit()
        desc_layout.addWidget(QLabel("Scenario:"))
        desc_layout.addWidget(self.scenario_edit)
        
        scroll_layout.addWidget(desc_group)
        
        # Tags
        tags_group = QGroupBox("Tags")
        tags_layout = QVBoxLayout(tags_group)
        
        self.tags_list = QListWidget()
        self.tags_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        tags_layout.addWidget(self.tags_list)
        
        tags_buttons_layout = QHBoxLayout()
        add_tag_btn = QPushButton("Add Tag")
        add_tag_btn.clicked.connect(self.add_tag)
        tags_buttons_layout.addWidget(add_tag_btn)
        
        remove_tag_btn = QPushButton("Remove Selected")
        remove_tag_btn.clicked.connect(self.remove_tags)
        tags_buttons_layout.addWidget(remove_tag_btn)
        
        tags_layout.addLayout(tags_buttons_layout)
        scroll_layout.addWidget(tags_group)
        
        scroll_area.setWidget(scroll_content)
        self.basic_info_layout.addWidget(scroll_area)
        
    def create_messages_section(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # System prompt
        system_group = QGroupBox("System Prompt")
        system_layout = QVBoxLayout(system_group)
        
        self.system_prompt_edit = QTextEdit()
        system_layout.addWidget(self.system_prompt_edit)
        scroll_layout.addWidget(system_group)
        
        # Post history instructions
        post_history_group = QGroupBox("Post History Instructions")
        post_history_layout = QVBoxLayout(post_history_group)
        
        self.post_history_instructions_edit = QTextEdit()
        post_history_layout.addWidget(self.post_history_instructions_edit)
        scroll_layout.addWidget(post_history_group)
        
        # First message
        first_mes_group = QGroupBox("First Message")
        first_mes_layout = QVBoxLayout(first_mes_group)
        
        self.first_mes_edit = QTextEdit()
        first_mes_layout.addWidget(self.first_mes_edit)
        scroll_layout.addWidget(first_mes_group)
        
        # Message examples
        mes_example_group = QGroupBox("Message Example")
        mes_example_layout = QVBoxLayout(mes_example_group)
        
        self.mes_example_edit = QTextEdit()
        mes_example_layout.addWidget(self.mes_example_edit)
        scroll_layout.addWidget(mes_example_group)
        
        # Alternate greetings
        alt_greetings_group = QGroupBox("Alternate Greetings")
        alt_greetings_layout = QVBoxLayout(alt_greetings_group)
        
        self.alternate_greetings_list = QListWidget()
        alt_greetings_layout.addWidget(self.alternate_greetings_list)
        
        alt_greetings_buttons_layout = QHBoxLayout()
        add_alt_greeting_btn = QPushButton("Add Greeting")
        add_alt_greeting_btn.clicked.connect(self.add_alternate_greeting)
        alt_greetings_buttons_layout.addWidget(add_alt_greeting_btn)
        
        remove_alt_greeting_btn = QPushButton("Remove Selected")
        remove_alt_greeting_btn.clicked.connect(self.remove_alternate_greetings)
        alt_greetings_buttons_layout.addWidget(remove_alt_greeting_btn)
        
        alt_greetings_layout.addLayout(alt_greetings_buttons_layout)
        scroll_layout.addWidget(alt_greetings_group)
        
        # Group only greetings
        group_greetings_group = QGroupBox("Group Only Greetings")
        group_greetings_layout = QVBoxLayout(group_greetings_group)
        
        self.group_only_greetings_list = QListWidget()
        group_greetings_layout.addWidget(self.group_only_greetings_list)
        
        group_greetings_buttons_layout = QHBoxLayout()
        add_group_greeting_btn = QPushButton("Add Greeting")
        add_group_greeting_btn.clicked.connect(self.add_group_only_greeting)
        group_greetings_buttons_layout.addWidget(add_group_greeting_btn)
        
        remove_group_greeting_btn = QPushButton("Remove Selected")
        remove_group_greeting_btn.clicked.connect(self.remove_group_only_greetings)
        group_greetings_buttons_layout.addWidget(remove_group_greeting_btn)
        
        group_greetings_layout.addLayout(group_greetings_buttons_layout)
        scroll_layout.addWidget(group_greetings_group)
        
        scroll_area.setWidget(scroll_content)
        self.messages_layout.addWidget(scroll_area)
        
    def create_extensions_section(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Creator notes
        creator_notes_group = QGroupBox("Creator Notes")
        creator_notes_layout = QVBoxLayout(creator_notes_group)
        
        self.creator_notes_edit = QTextEdit()
        creator_notes_layout.addWidget(self.creator_notes_edit)
        scroll_layout.addWidget(creator_notes_group)
        
        # Multilingual creator notes
        multilingual_notes_group = QGroupBox("Multilingual Creator Notes")
        multilingual_notes_layout = QVBoxLayout(multilingual_notes_group)
        
        self.multilingual_notes_table = QTableWidget()
        self.multilingual_notes_table.setColumnCount(2)
        self.multilingual_notes_table.setHorizontalHeaderLabels(["Language", "Notes"])
        self.multilingual_notes_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        multilingual_notes_layout.addWidget(self.multilingual_notes_table)
        
        multilingual_buttons_layout = QHBoxLayout()
        add_multilingual_btn = QPushButton("Add Note")
        add_multilingual_btn.clicked.connect(self.add_multilingual_note)
        multilingual_buttons_layout.addWidget(add_multilingual_btn)
        
        remove_multilingual_btn = QPushButton("Remove Selected")
        remove_multilingual_btn.clicked.connect(self.remove_multilingual_notes)
        multilingual_buttons_layout.addWidget(remove_multilingual_btn)
        
        multilingual_notes_layout.addLayout(multilingual_buttons_layout)
        scroll_layout.addWidget(multilingual_notes_group)
        
        # Sources
        sources_group = QGroupBox("Sources")
        sources_layout = QVBoxLayout(sources_group)
        
        self.sources_list = QListWidget()
        sources_layout.addWidget(self.sources_list)
        
        sources_buttons_layout = QHBoxLayout()
        add_source_btn = QPushButton("Add Source")
        add_source_btn.clicked.connect(self.add_source)
        sources_buttons_layout.addWidget(add_source_btn)
        
        remove_source_btn = QPushButton("Remove Selected")
        remove_source_btn.clicked.connect(self.remove_sources)
        sources_buttons_layout.addWidget(remove_source_btn)
        
        sources_layout.addLayout(sources_buttons_layout)
        scroll_layout.addWidget(sources_group)
        
        scroll_area.setWidget(scroll_content)
        self.extensions_layout.addWidget(scroll_area)
        
    def create_lorebook_section(self):
        label = QLabel("Lorebook editor will be implemented here")
        label.setAlignment(Qt.AlignCenter)
        self.lorebook_layout.addWidget(label)
        
    def create_assets_section(self):
        label = QLabel("Assets editor will be implemented here")
        label.setAlignment(Qt.AlignCenter)
        self.assets_layout.addWidget(label)
        
    def new_file(self):
        self.file_path = None
        self.data = {
            "spec": "chara_card_v3",
            "spec_version": "3.0",
            "data": {
                "name": "",
                "description": "",
                "tags": [],
                "creator": "",
                "character_version": "",
                "mes_example": "",
                "extensions": {},
                "system_prompt": "",
                "post_history_instructions": "",
                "first_mes": "",
                "alternate_greetings": [],
                "personality": "",
                "scenario": "",
                "creator_notes": "",
                "group_only_greetings": [],
                "creation_date": int(datetime.now().timestamp()),
                "modification_date": int(datetime.now().timestamp())
            }
        }
        self.load_data_to_ui()
        self.statusBar().showMessage("New file created")
        
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open JSON File", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                self.file_path = file_path
                self.load_data_to_ui()
                self.statusBar().showMessage(f"Opened: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")
                
    def save_file(self):
        if self.file_path is None:
            self.save_as_file()
        else:
            try:
                self.update_data_from_ui()
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
                self.statusBar().showMessage(f"Saved: {self.file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
                
    def save_as_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save JSON File", "", "JSON Files (*.json)"
        )
        if file_path:
            self.file_path = file_path
            self.save_file()
            
    def load_data_to_ui(self):
        # Basic info
        self.spec_edit.setText(self.data.get("spec", ""))
        self.spec_version_edit.setText(self.data.get("spec_version", ""))
        
        data = self.data.get("data", {})
        self.name_edit.setText(data.get("name", ""))
        self.creator_edit.setText(data.get("creator", ""))
        self.character_version_edit.setText(data.get("character_version", ""))
        self.nickname_edit.setText(data.get("nickname", ""))
        self.description_edit.setText(data.get("description", ""))
        self.personality_edit.setText(data.get("personality", ""))
        self.scenario_edit.setText(data.get("scenario", ""))
        
        # Tags
        self.tags_list.clear()
        for tag in data.get("tags", []):
            self.tags_list.addItem(tag)
            
        # Messages
        self.system_prompt_edit.setText(data.get("system_prompt", ""))
        self.post_history_instructions_edit.setText(data.get("post_history_instructions", ""))
        self.first_mes_edit.setText(data.get("first_mes", ""))
        self.mes_example_edit.setText(data.get("mes_example", ""))
        
        # Alternate greetings
        self.alternate_greetings_list.clear()
        for greeting in data.get("alternate_greetings", []):
            self.alternate_greetings_list.addItem(greeting)
            
        # Group only greetings
        self.group_only_greetings_list.clear()
        for greeting in data.get("group_only_greetings", []):
            self.group_only_greetings_list.addItem(greeting)
            
        # Extensions
        self.creator_notes_edit.setText(data.get("creator_notes", ""))
        
        # Multilingual notes
        self.multilingual_notes_table.setRowCount(0)
        multilingual_notes = data.get("creator_notes_multilingual", {})
        for lang, notes in multilingual_notes.items():
            row = self.multilingual_notes_table.rowCount()
            self.multilingual_notes_table.insertRow(row)
            self.multilingual_notes_table.setItem(row, 0, QTableWidgetItem(lang))
            self.multilingual_notes_table.setItem(row, 1, QTableWidgetItem(notes))
            
        # Sources
        self.sources_list.clear()
        for source in data.get("source", []):
            self.sources_list.addItem(source)
            
    def update_data_from_ui(self):
        # Basic info
        self.data["spec"] = self.spec_edit.text()
        self.data["spec_version"] = self.spec_version_edit.text()
        
        data = self.data.get("data", {})
        data["name"] = self.name_edit.text()
        data["creator"] = self.creator_edit.text()
        data["character_version"] = self.character_version_edit.text()
        data["nickname"] = self.nickname_edit.text()
        data["description"] = self.description_edit.toPlainText()
        data["personality"] = self.personality_edit.toPlainText()
        data["scenario"] = self.scenario_edit.toPlainText()
        
        # Tags
        data["tags"] = []
        for i in range(self.tags_list.count()):
            data["tags"].append(self.tags_list.item(i).text())
            
        # Messages
        data["system_prompt"] = self.system_prompt_edit.toPlainText()
        data["post_history_instructions"] = self.post_history_instructions_edit.toPlainText()
        data["first_mes"] = self.first_mes_edit.toPlainText()
        data["mes_example"] = self.mes_example_edit.toPlainText()
        
        # Alternate greetings
        data["alternate_greetings"] = []
        for i in range(self.alternate_greetings_list.count()):
            data["alternate_greetings"].append(self.alternate_greetings_list.item(i).text())
            
        # Group only greetings
        data["group_only_greetings"] = []
        for i in range(self.group_only_greetings_list.count()):
            data["group_only_greetings"].append(self.group_only_greetings_list.item(i).text())
            
        # Extensions
        data["creator_notes"] = self.creator_notes_edit.toPlainText()
        
        # Multilingual notes
        multilingual_notes = {}
        for row in range(self.multilingual_notes_table.rowCount()):
            lang_item = self.multilingual_notes_table.item(row, 0)
            notes_item = self.multilingual_notes_table.item(row, 1)
            if lang_item and notes_item:
                multilingual_notes[lang_item.text()] = notes_item.text()
        data["creator_notes_multilingual"] = multilingual_notes
        
        # Sources
        data["source"] = []
        for i in range(self.sources_list.count()):
            data["source"].append(self.sources_list.item(i).text())
            
        # Update modification date
        data["modification_date"] = int(datetime.now().timestamp())
        
    @Slot()
    def add_tag(self):
        text, ok = QInputDialog.getText(self, "Add Tag", "Enter tag:")
        if ok and text:
            self.tags_list.addItem(text)
            
    @Slot()
    def remove_tags(self):
        for item in self.tags_list.selectedItems():
            self.tags_list.takeItem(self.tags_list.row(item))
            
    @Slot()
    def add_alternate_greeting(self):
        text, ok = QInputDialog.getText(self, "Add Alternate Greeting", "Enter greeting:")
        if ok and text:
            self.alternate_greetings_list.addItem(text)
            
    @Slot()
    def remove_alternate_greetings(self):
        for item in self.alternate_greetings_list.selectedItems():
            self.alternate_greetings_list.takeItem(self.alternate_greetings_list.row(item))
            
    @Slot()
    def add_group_only_greeting(self):
        text, ok = QInputDialog.getText(self, "Add Group Only Greeting", "Enter greeting:")
        if ok and text:
            self.group_only_greetings_list.addItem(text)
            
    @Slot()
    def remove_group_only_greetings(self):
        for item in self.group_only_greetings_list.selectedItems():
            self.group_only_greetings_list.takeItem(self.group_only_greetings_list.row(item))
            
    @Slot()
    def add_multilingual_note(self):
        lang, ok1 = QInputDialog.getText(self, "Add Multilingual Note", "Enter language code:")
        if ok1 and lang:
            notes, ok2 = QInputDialog.getText(self, "Add Multilingual Note", "Enter notes:")
            if ok2:
                row = self.multilingual_notes_table.rowCount()
                self.multilingual_notes_table.insertRow(row)
                self.multilingual_notes_table.setItem(row, 0, QTableWidgetItem(lang))
                self.multilingual_notes_table.setItem(row, 1, QTableWidgetItem(notes or ""))
                
    @Slot()
    def remove_multilingual_notes(self):
        for item in self.multilingual_notes_table.selectedItems():
            self.multilingual_notes_table.removeRow(item.row())
            
    @Slot()
    def add_source(self):
        text, ok = QInputDialog.getText(self, "Add Source", "Enter source:")
        if ok and text:
            self.sources_list.addItem(text)
            
    @Slot()
    def remove_sources(self):
        for item in self.sources_list.selectedItems():
            self.sources_list.takeItem(self.sources_list.row(item))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    editor = JsonEditor()
    editor.show()
    
    sys.exit(app.exec())