from PySide6.QtWidgets import QTableWidget, QHeaderView, QApplication
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag


class OrderTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setEditTriggers(QTableWidget.NoEditTriggers)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (
            event.pos() - self.drag_start_position
        ).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText("OrderTableRow")
        drag.setMimeData(mime_data)

        drag.exec(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text() == "OrderTableRow":
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text() == "OrderTableRow":
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text() == "OrderTableRow":
            # 获取拖拽的行和放置的位置
            source_row = self.currentRow()
            drop_row = self.rowAt(event.position().toPoint().y())

            if source_row != -1 and drop_row != -1 and source_row != drop_row:
                # 移动行
                self.move_row(source_row, drop_row)
                event.acceptProposedAction()

    def move_row(self, source_row, target_row):
        # 获取源行的数据
        source_items = []
        for column in range(self.columnCount()):
            item = self.takeItem(source_row, column)
            source_items.append(item)

        # 移动行
        if source_row < target_row:
            # 向下移动
            for row in range(source_row, target_row):
                for column in range(self.columnCount()):
                    item = self.takeItem(row + 1, column)
                    self.setItem(row, column, item)
        else:
            # 向上移动
            for row in range(source_row, target_row, -1):
                for column in range(self.columnCount()):
                    item = self.takeItem(row - 1, column)
                    self.setItem(row, column, item)

        # 插入源行到目标位置
        for column, item in enumerate(source_items):
            self.setItem(target_row, column, item)

        # 通知父窗口更新提示词列表
        if hasattr(self.parent(), "on_order_table_row_moved"):
            self.parent().on_order_table_row_moved()
