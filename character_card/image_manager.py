import sys
import csv
import os
import uuid
import requests
import json
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QLabel,
    QMessageBox,
    QDialog,
    QScrollArea,
    QSizePolicy,
    QCompleter,
    QComboBox,
)
from PySide6.QtCore import QThread, Signal, Qt, QStringListModel
from PySide6.QtGui import QPixmap

# 导入角色卡读取模块
import read_character_card_v2
import read_character_card_v3
from read_character_card_v3 import read_character_card_v3_keys


class TagsDelegate(QTableWidgetItem):
    """自定义委托类，用于处理Tags列的编辑"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tags_model = QStringListModel()
        self.tags_model.setStringList(["a", "b"])  # 默认标签列表

    def createEditor(self, parent, option, index):
        """创建编辑器"""
        if index.column() == 2:  # Tags列
            combo = QComboBox(parent)
            combo.setEditable(True)
            combo.setModel(self.tags_model)
            combo.setCompleter(QCompleter(self.tags_model, combo))
            return combo
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        """设置编辑器数据"""
        if index.column() == 2 and isinstance(editor, QComboBox):
            value = index.model().data(index, Qt.EditRole)
            editor.setCurrentText(value)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        """设置模型数据"""
        if index.column() == 2 and isinstance(editor, QComboBox):
            model.setData(index, editor.currentText(), Qt.EditRole)
        else:
            super().setModelData(editor, model, index)


class DownloadThread(QThread):
    """下载线程类，避免界面卡顿"""

    finished = Signal(str, str)  # 信号：文件路径，错误信息
    progress = Signal(int)  # 进度信号

    def __init__(self, url, file_path):
        super().__init__()
        self.url = url
        self.file_path = file_path

    def run(self):
        try:
            response = requests.get(self.url, timeout=30)
            response.raise_for_status()

            # 保存文件
            with open(self.file_path, "wb") as f:
                f.write(response.content)

            self.finished.emit(self.file_path, "")
        except Exception as e:
            self.finished.emit("", str(e))


class ImageManager(QMainWindow):
    def __init__(self, csv_file="图片.csv"):
        super().__init__()
        self.csv_file = csv_file
        self.data = []
        self.download_threads = []

        self.init_ui()
        self.load_csv()
        self.update_table()

    def closeEvent(self, event):
        """关闭事件处理，确保线程正确退出"""
        # 等待所有下载线程完成
        for thread in self.download_threads:
            if thread.isRunning():
                thread.quit()
                thread.wait()
        event.accept()

    def init_ui(self):
        self.setWindowTitle("图片管理器")
        # self.setGeometry(100, 100, 20, 700)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QHBoxLayout(central_widget)

        # 左侧布局（表格和控制按钮）
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        main_layout.addWidget(left_widget, 1)  # 占据1/3的宽度

        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["期望名称", "URL", "Tags", "本地名称", "下载操作", "查看图片"]
        )
        # 允许编辑期望名称和Tags列
        self.table.setEditTriggers(
            QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed
        )
        self.table.horizontalHeader().setStretchLastSection(False)
        # 设置列宽
        self.table.setColumnWidth(0, 200)  # 期望名称
        self.table.setColumnWidth(1, 120)  # URL
        self.table.setColumnWidth(2, 60)  # Tags
        self.table.setColumnWidth(3, 80)  # 本地名称
        self.table.setColumnWidth(4, 60)  # 下载操作
        self.table.setColumnWidth(5, 60)  # 查看图片

        # 创建Tags委托实例
        self.tags_delegate = TagsDelegate()

        # 连接单元格更改信号
        self.table.cellChanged.connect(self.on_cell_changed)

        left_layout.addWidget(self.table)

        # 添加新行的控件
        add_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.url_input = QLineEdit()
        self.tags_input = QLineEdit()
        self.name_input.setPlaceholderText("输入期望名称")
        self.url_input.setPlaceholderText("输入图片URL")
        self.tags_input.setPlaceholderText("输入标签(可选)")

        add_btn = QPushButton("添加新行")
        add_btn.clicked.connect(self.add_new_row)

        add_layout.addWidget(QLabel("期望名称:"))
        add_layout.addWidget(self.name_input)
        add_layout.addWidget(QLabel("URL:"))
        add_layout.addWidget(self.url_input)
        add_layout.addWidget(QLabel("Tags:"))
        add_layout.addWidget(self.tags_input)
        add_layout.addWidget(add_btn)

        left_layout.addLayout(add_layout)

        # 保存按钮
        save_btn = QPushButton("保存数据")
        save_btn.clicked.connect(self.save_data)
        left_layout.addWidget(save_btn)

        # 中间布局（图片预览和默认JSON信息）
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        middle_widget.setMinimumWidth(300)
        main_layout.addWidget(middle_widget, 1)  # 占据1/3的宽度

        # 图片预览标题
        preview_label = QLabel("图片预览")
        preview_label.setAlignment(Qt.AlignCenter)
        middle_layout.addWidget(preview_label)

        # 图片预览区域
        self.preview_area = QScrollArea()
        self.preview_area.setWidgetResizable(True)
        middle_layout.addWidget(self.preview_area, 1)  # 分配1份空间

        # 图片标签
        self.preview_label = QLabel("请选择图片进行预览")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_area.setWidget(self.preview_label)

        # 默认JSON信息显示区域
        default_json_label = QLabel("JSON信息")
        default_json_label.setAlignment(Qt.AlignCenter)
        middle_layout.addWidget(default_json_label)

        # 默认JSON信息显示区域
        self.json_area = QScrollArea()
        self.json_area.setWidgetResizable(True)
        middle_layout.addWidget(self.json_area, 1)  # 分配1份空间

        # JSON信息标签
        self.json_label = QLabel("请选择图片查看JSON信息")
        self.json_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.json_label.setWordWrap(True)
        self.json_label.setTextFormat(Qt.RichText)  # 支持富文本
        self.json_label.setScaledContents(False)  # 不缩放内容
        self.json_area.setWidget(self.json_label)

        # 右侧布局（V3角色卡信息）
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_widget.setMinimumWidth(300)
        main_layout.addWidget(right_widget, 1)  # 占据1/3的宽度

        # V3角色卡信息栏
        self.v3_info_widget = QWidget()
        self.v3_info_layout = QVBoxLayout(self.v3_info_widget)
        self.v3_info_widget.setVisible(False)  # 默认隐藏
        right_layout.addWidget(self.v3_info_widget)

        # V3信息标题
        v3_info_label = QLabel("角色卡信息")
        v3_info_label.setAlignment(Qt.AlignCenter)
        self.v3_info_layout.addWidget(v3_info_label)

        # V3信息显示区域
        self.v3_info_area = QScrollArea()
        self.v3_info_area.setWidgetResizable(True)
        self.v3_info_layout.addWidget(self.v3_info_area, 1)  # 分配1份空间

        # V3信息标签
        self.v3_info_label = QLabel("")
        self.v3_info_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.v3_info_label.setWordWrap(True)
        self.v3_info_label.setTextFormat(Qt.RichText)  # 支持富文本
        self.v3_info_area.setWidget(self.v3_info_label)

        # 导出data.json按钮
        self.export_data_btn = QPushButton("导出data.json")
        self.export_data_btn.clicked.connect(self.export_data_json)
        self.export_data_btn.setVisible(False)  # 默认隐藏
        self.v3_info_layout.addWidget(self.export_data_btn)

    def detect_encoding(self, file_path):
        """检测文件编码，优先UTF-8，回退GBK"""
        # 优先尝试UTF-8
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                f.read()
            return "utf-8"
        except UnicodeDecodeError:
            pass

        # 回退到GBK
        try:
            with open(file_path, "r", encoding="gbk") as f:
                f.read()
            return "gbk"
        except UnicodeDecodeError:
            pass

        # 如果都不行，使用chardet检测
        import chardet

        with open(file_path, "rb") as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result["encoding"]

    def load_csv(self):
        """加载CSV文件"""
        if not os.path.exists(self.csv_file):
            # 如果文件不存在，创建带标题的空文件
            with open(self.csv_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["期望名称", "url", "tags", "本地名称"])
            self.data = []
            return

        # 检测编码
        try:
            encoding = self.detect_encoding(self.csv_file)
        except:
            encoding = "utf-8"

        self.data = []
        try:
            with open(self.csv_file, "r", encoding=encoding, newline="") as f:
                reader = csv.reader(f)
                headers = next(reader)  # 读取标题行

                # 确保有四列
                if len(headers) < 4:
                    headers.extend([""] * (4 - len(headers)))

                # 检查标题是否正确
                headers_valid = (
                    headers[0] == "期望名称"
                    and headers[1] == "url"
                    and headers[2] == "tags"
                    and (len(headers) <= 3 or headers[3] == "本地名称")
                )

                # 如果标题不正确，我们需要重新格式化文件
                if not headers_valid:
                    # 读取所有数据
                    all_rows = [headers]
                    for row in reader:
                        if len(row) < 4:
                            row.extend([""] * (4 - len(row)))
                        all_rows.append(row)

                    # 重新写入文件，确保有正确的标题
                    with open(self.csv_file, "w", encoding="utf-8", newline="") as wf:
                        writer = csv.writer(wf)
                        writer.writerow(["期望名称", "url", "tags", "本地名称"])
                        # 写入数据行（跳过原来的标题行）
                        for row in all_rows[1:]:
                            writer.writerow(row)

                    # 重新读取文件
                    f.seek(0)
                    reader = csv.reader(f)
                    next(reader)  # 跳过标题行

                # 读取数据行
                for row in reader:
                    if len(row) < 4:
                        row.extend([""] * (4 - len(row)))
                    self.data.append(row)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"读取CSV文件时出错: {str(e)}")
            self.data = []

    def save_csv(self):
        """保存CSV文件"""
        try:
            with open(self.csv_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["期望名称", "url", "tags", "本地名称"])
                writer.writerows(self.data)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存CSV文件时出错: {str(e)}")

    def update_table(self):
        """更新表格显示"""
        self.table.setRowCount(len(self.data))

        for i, row in enumerate(self.data):
            # 确保行有足够的列
            while len(row) < 4:
                row.append("")

            # 添加数据到表格
            for j in range(4):
                item = QTableWidgetItem(row[j])
                self.table.setItem(i, j, item)

            # 添加下载操作按钮
            download_btn_widget = QWidget()
            download_btn_layout = QHBoxLayout(download_btn_widget)
            download_btn_layout.setContentsMargins(0, 0, 0, 0)

            download_btn = QPushButton("下载")
            # 使用默认参数修复lambda表达式的问题
            download_btn.clicked.connect(
                lambda checked=False, idx=i: self.download_image(idx)
            )

            # 检查本地文件是否存在
            local_name = row[3] if len(row) > 3 else ""
            if local_name and os.path.exists(local_name):
                download_btn.setEnabled(False)
                download_btn.setText("已下载")
            else:
                # 如果本地名称不存在或文件不存在，清空本地名称
                if local_name:
                    row[3] = ""
                    if len(row) > 3:
                        self.table.item(i, 3).setText("")

            download_btn_layout.addWidget(download_btn)
            self.table.setCellWidget(i, 4, download_btn_widget)

            # 添加查看图片按钮
            view_btn_widget = QWidget()
            view_btn_layout = QHBoxLayout(view_btn_widget)
            view_btn_layout.setContentsMargins(0, 0, 0, 0)

            view_btn = QPushButton("查看图片")
            # 使用默认参数修复lambda表达式的问题
            view_btn.clicked.connect(lambda checked=False, idx=i: self.view_image(idx))

            # 检查本地文件是否存在，如果不存在则禁用按钮
            local_name = row[3] if len(row) > 3 else ""
            if not local_name or not os.path.exists(local_name):
                view_btn.setEnabled(False)
                view_btn.setText("文件不存在")
            else:
                view_btn.setEnabled(True)
                view_btn.setText("查看图片")

            view_btn_layout.addWidget(view_btn)
            self.table.setCellWidget(i, 5, view_btn_widget)

    def add_new_row(self):
        """添加新行"""
        name = self.name_input.text().strip()
        url = self.url_input.text().strip()
        tags = self.tags_input.text().strip()

        if not name or not url:
            QMessageBox.warning(self, "警告", "请填写完整的名称和URL")
            return

        # 添加到数据中
        self.data.append([name, url, tags, ""])

        # 清空输入框
        self.name_input.clear()
        self.url_input.clear()
        self.tags_input.clear()

        # 更新表格
        self.update_table()

    def download_image(self, row_index):
        """下载图片"""
        if row_index >= len(self.data):
            return

        row = self.data[row_index]
        url = row[1]

        if not url:
            QMessageBox.warning(self, "警告", "URL为空")
            return

        # 生成UUID文件名
        file_uuid = str(uuid.uuid4())
        # 尝试从URL获取文件扩展名
        ext = ".png"  # 默认扩展名
        if "." in url:
            ext = "." + url.split(".")[-1].split("?")[0]
            if len(ext) > 10:  # 如果扩展名太长，可能是错误的
                ext = ".png"

        file_name = file_uuid + ext

        # 创建下载线程
        thread = DownloadThread(url, file_name)
        # 使用默认参数值修复lambda表达式的问题
        thread.finished.connect(
            lambda path="",
            error="",
            idx=row_index,
            fname=file_name: self.on_download_finished(idx, fname, path, error)
        )
        thread.start()

        # 保存线程引用
        self.download_threads.append(thread)

        # 更新按钮状态
        btn_widget = self.table.cellWidget(row_index, 3)
        if btn_widget:
            btn_layout = btn_widget.layout()
            if btn_layout.count() > 0:
                btn = btn_layout.itemAt(0).widget()
                if btn:
                    btn.setText("下载中...")
                    btn.setEnabled(False)

    def on_download_finished(self, row_index, file_name, file_path, error):
        """下载完成回调"""
        if row_index >= len(self.data):
            return

        # 更新数据
        if error:
            QMessageBox.warning(self, "下载失败", f"下载失败: {error}")
            # 恢复按钮状态
            btn_widget = self.table.cellWidget(row_index, 3)
            if btn_widget:
                btn_layout = btn_widget.layout()
                if btn_layout.count() > 0:
                    btn = btn_layout.itemAt(0).widget()
                    if btn:
                        btn.setText("下载")
                        btn.setEnabled(True)
        else:
            # 更新本地名称
            self.data[row_index][2] = file_name
            self.table.item(row_index, 2).setText(file_name)

            # 更新按钮状态
            btn_widget = self.table.cellWidget(row_index, 3)
            if btn_widget:
                btn_layout = btn_widget.layout()
                if btn_layout.count() > 0:
                    btn = btn_layout.itemAt(0).widget()
                    if btn:
                        btn.setText("已下载")
                        btn.setEnabled(False)

    def view_image(self, row_index):
        """查看图片"""
        if row_index >= len(self.data):
            return

        row = self.data[row_index]
        local_name = row[3] if len(row) > 3 else ""

        if not local_name or not os.path.exists(local_name):
            QMessageBox.warning(self, "错误", "图片文件不存在")
            return

        # 在右侧预览区域显示图片
        self.display_image(local_name)

    def display_image(self, image_path):
        """在预览区域显示图片和JSON信息"""
        # 显示图片
        try:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                self.preview_label.setText("无法加载图片")
            else:
                # 缩放图片以适应预览区域
                scaled_pixmap = pixmap.scaled(
                    self.preview_area.width() - 20,
                    self.preview_area.height() - 20,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
                self.preview_label.setPixmap(scaled_pixmap)
                self.preview_label.resize(scaled_pixmap.width(), scaled_pixmap.height())
        except Exception as e:
            self.preview_label.setText(f"加载图片时出错: {str(e)}")

        # 显示JSON信息
        self.display_json_info(image_path)

        # 如果是PNG文件，尝试读取角色卡信息并显示part1
        _, ext = os.path.splitext(image_path)
        if ext.lower() == ".png":
            # 尝试读取V3格式的角色卡
            character_card_v3 = read_character_card_v3.read_character_card_v3_from_png(
                image_path
            )
            if character_card_v3:
                # 显示part1在图片下方
                self.display_part1(character_card_v3)

    def display_json_info(self, image_path):
        """显示图片相关的JSON信息"""
        # 隐藏V3信息栏
        self.v3_info_widget.setVisible(False)

        # 检查文件扩展名
        _, ext = os.path.splitext(image_path)

        # 如果是PNG文件，尝试读取角色卡信息
        if ext.lower() == ".png":
            # 尝试读取V3格式的角色卡
            character_card_v3 = read_character_card_v3.read_character_card_v3_from_png(
                image_path
            )
            if character_card_v3:
                # 显示V3角色卡信息栏
                self.display_v3_info(character_card_v3)
                return

            # 尝试读取V2格式的角色卡
            character_card_v2 = read_character_card_v2.read_character_card_v2_from_png(
                image_path
            )
            if character_card_v2:
                # 显示V2角色卡信息
                formatted_json = json.dumps(
                    character_card_v2, ensure_ascii=False, indent=2
                )
                self.json_label.setText(f"Character Card V2:\n{formatted_json}")
                self.json_area.setVisible(True)
                return

        # 检查是否存在同名的JSON文件
        json_path = os.path.splitext(image_path)[0] + ".json"
        self.json_area.setVisible(True)

        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                    # 格式化JSON数据显示
                    formatted_json = json.dumps(json_data, ensure_ascii=False, indent=2)
                    self.json_label.setText(formatted_json)
            except Exception as e:
                self.json_label.setText(f"加载JSON文件时出错: {str(e)}")
        else:
            # 如果没有JSON文件，显示SPEC_V3.md中的相关信息
            spec_info = """Character Card V3 规范摘要:

1. 基本信息字段:
   - name: 角色名称
   - description: 角色描述
   - personality: 角色个性
   - scenario: 场景设定
   - first_mes: 初始消息
   - mes_example: 对话示例

2. 扩展字段:
   - creator: 创建者
   - version: 角色版本
   - tags: 标签列表
   - system_prompt: 系统提示
   - alternate_greetings: 备选问候语

3. 资源字段:
   - assets: 资源列表(图标、背景等)
   - character_book: 角色知识库

4. 其他字段:
   - creator_notes: 创建者笔记
   - nickname: 昵称
   - group_only_greetings: 群聊专用问候语"""

            self.json_label.setText(spec_info)

    def on_cell_changed(self, row, column):
        """处理单元格数据更改"""
        if row < len(self.data) and column < len(self.data[row]):
            # 获取新的值
            item = self.table.item(row, column)
            if item:
                new_value = item.text()
                # 更新数据
                self.data[row][column] = new_value

    def save_data(self):
        """保存数据"""
        try:
            self.save_csv()
            QMessageBox.information(self, "成功", "数据已保存")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存数据时出错: {str(e)}")

    def refresh_data(self):
        """刷新数据"""
        self.load_csv()
        self.update_table()

    def display_part1(self, character_card_v3):
        """在图片下方显示part1信息"""
        # 获取part1和part2
        part1, part2 = read_character_card_v3_keys(character_card_v3)

        # 格式化part1信息显示
        info_text = "<html><head/><body>"
        for key, value in part1.items():
            info_text += f"<p><b>{key}:</b> {value}</p>"
        info_text += "</body></html>"

        # 在图片下方显示part1信息
        self.json_label.setText(info_text)
        self.json_area.setVisible(True)

    def display_v3_info(self, character_card_v3):
        """在右侧显示part2信息"""
        # 显示V3信息栏
        self.v3_info_widget.setVisible(True)
        self.json_area.setVisible(False)  # 隐藏JSON区域
        self.export_data_btn.setVisible(True)  # 显示导出按钮

        # 保存当前的角色卡信息，供导出使用
        self.current_character_card = character_card_v3

        # 获取part1和part2
        part1, part2 = read_character_card_v3_keys(character_card_v3)

        # 格式化part2信息显示
        if part2:
            # 格式化JSON数据显示
            formatted_json = json.dumps(part2, ensure_ascii=False, indent=2)
            self.v3_info_label.setText(formatted_json)
        else:
            self.v3_info_label.setText("Part2 无数据")

    def export_data_json(self):
        """导出data.json文件"""
        if hasattr(self, "current_character_card"):
            # 获取part1和part2
            part1, part2 = read_character_card_v3_keys(self.current_character_card)

            if part2:
                # 生成文件名
                file_name = "data.json"

                try:
                    # 保存part2数据到JSON文件
                    with open(file_name, "w", encoding="utf-8") as f:
                        json.dump(part2, f, ensure_ascii=False, indent=2)

                    QMessageBox.information(self, "成功", f"数据已导出到 {file_name}")
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"导出数据时出错: {str(e)}")
            else:
                QMessageBox.warning(self, "警告", "没有数据可以导出")
        else:
            QMessageBox.warning(self, "警告", "没有选中的角色卡")


def main():
    app = QApplication(sys.argv)
    window = ImageManager()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
