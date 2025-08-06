import sys
import json
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QSplitter,
    QTabWidget,
    QLabel,
)
from PySide6.QtCore import Qt

# 导入标签页创建函数
from components.prompts_tab import create_prompts_tab
from components.prompts_tab_edit import PromptsTabEditor
from components.merged_settings_edit import MergedSettingsEditor
from components.merged_settings import create_merged_settings


class MainComponent(QWidget):
    def __init__(
        self, parent=None, open_callback=None, save_callback=None, save_as_callback=None
    ):
        super().__init__(parent)
        self.json_data = {}
        self.file_path = None
        self.open_callback = open_callback
        self.save_callback = save_callback
        self.save_as_callback = save_as_callback
        # 创建提示词标签页编辑器实例
        self.prompts_tab_editor = PromptsTabEditor(self)
        # 创建设置标签页编辑器实例
        self.merged_settings_editor = MergedSettingsEditor(self)
        self.init_ui()

    def init_ui(self):
        # 创建主工作区
        self.create_main_area()

    def create_toolbar(self, toolbar_layout):
        # 创建工具栏按钮
        open_btn = QPushButton("打开")
        open_btn.clicked.connect(self.open_file)
        toolbar_layout.addWidget(open_btn)

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_file)
        toolbar_layout.addWidget(save_btn)

        save_as_btn = QPushButton("另存为")
        save_as_btn.clicked.connect(self.save_as_file)
        toolbar_layout.addWidget(save_as_btn)

    def create_main_area(self):
        layout = QVBoxLayout()

        # 创建工具栏
        toolbar_layout = QHBoxLayout()
        self.create_toolbar(toolbar_layout)
        layout.addLayout(toolbar_layout)

        # 创建标签页
        tab_widget = QTabWidget()

        # 提示词管理标签页（包含提示词列表和顺序管理）
        prompts_tab = create_prompts_tab(self)
        tab_widget.addTab(prompts_tab, "提示词管理")

        # 基本设置和文本设置标签页（合并在一个tabs中）
        settings_tab = create_merged_settings(self)
        tab_widget.addTab(settings_tab, "设置")

        layout.addWidget(tab_widget)

        # 创建状态栏
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet(
            "background-color: #f0f0f0; padding: 5px; border: 1px solid #ccc;"
        )
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def update_status(self, message):
        """更新状态栏信息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status_label.setText(f"{timestamp} - {message}")

    def open_file(self):
        if self.open_callback:
            self.open_callback(self)
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "打开JSON文件", "", "JSON Files (*.json)"
            )
            if file_path:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        self.json_data = json.load(f)
                    self.populate_fields()
                    self.file_path = file_path
                    self.update_status(f"已打开文件: {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"无法打开文件: {str(e)}")
                    self.update_status(f"打开文件失败: {str(e)}")

    def save_file(self):
        if self.save_callback:
            self.save_callback(self)
        else:
            if not self.file_path:
                self.save_as_file()
            else:
                self.update_json_data()
                try:
                    with open(self.file_path, "w", encoding="utf-8") as f:
                        json.dump(self.json_data, f, ensure_ascii=False, indent=4)
                    self.update_status(f"已保存文件: {self.file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"无法保存文件: {str(e)}")
                    self.update_status(f"保存文件失败: {str(e)}")

    def save_as_file(self):
        if self.save_as_callback:
            self.save_as_callback(self)
        else:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存JSON文件", "", "JSON Files (*.json)"
            )
            if file_path:
                self.file_path = file_path
                self.update_json_data()
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(self.json_data, f, ensure_ascii=False, indent=4)
                    self.update_status(f"已另存为文件: {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"无法保存文件: {str(e)}")
                    self.update_status(f"另存为文件失败: {str(e)}")

    def populate_fields(self):
        # 使用MergedSettingsEditor填充设置字段
        self.merged_settings_editor.populate_settings_fields(self.json_data)

        # 使用PromptsTabEditor填充提示词字段
        self.prompts_tab_editor.populate_prompts_fields(self.json_data)

    def update_json_data(self):
        # 使用MergedSettingsEditor更新设置数据
        self.merged_settings_editor.update_settings_data(self.json_data)

        # 使用PromptsTabEditor更新提示词数据
        self.prompts_tab_editor.update_prompts_data(self.json_data)


class JSONEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.json_data = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("预设管理器")

        # 创建主组件
        self.main_component = MainComponent()
        self.setCentralWidget(self.main_component)

        # 创建状态栏
        self.statusBar().showMessage("就绪")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开JSON文件", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.json_data = json.load(f)
                self.main_component.json_data = self.json_data
                self.main_component.populate_fields()
                self.main_component.file_path = file_path
                self.statusBar().showMessage(f"已打开文件: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法打开文件: {str(e)}")

    def save_file(self):
        if not hasattr(self, "current_file_path") or not self.current_file_path:
            self.save_as_file()
        else:
            self.main_component.update_json_data()
            try:
                with open(self.current_file_path, "w", encoding="utf-8") as f:
                    json.dump(
                        self.main_component.json_data, f, ensure_ascii=False, indent=4
                    )
                self.statusBar().showMessage(f"已保存文件: {self.current_file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法保存文件: {str(e)}")

    def save_as_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存JSON文件", "", "JSON Files (*.json)"
        )
        if file_path:
            self.current_file_path = file_path
            self.main_component.update_json_data()
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(
                        self.main_component.json_data, f, ensure_ascii=False, indent=4
                    )
                self.statusBar().showMessage(f"已保存文件: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法保存文件: {str(e)}")


def main():
    app = QApplication(sys.argv)
    editor = JSONEditor()

    # 如果提供了命令行参数，尝试打开指定的文件
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                editor.json_data = json.load(f)
            editor.main_component.json_data = editor.json_data
            editor.main_component.populate_fields()
            editor.current_file_path = file_path
            editor.statusBar().showMessage(f"已打开文件: {file_path}")
        except Exception as e:
            QMessageBox.critical(editor, "错误", f"无法打开文件: {str(e)}")

    # 修复窗口几何形状设置问题
    # 先显示窗口，然后再最大化，避免几何形状冲突
    editor.show()
    # 延迟一点时间确保窗口完全初始化后再最大化
    from PySide6.QtCore import QTimer

    QTimer.singleShot(100, editor.showMaximized)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
