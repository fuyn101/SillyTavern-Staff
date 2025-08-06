import uuid
import re
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem, QMessageBox, QTableWidgetItem


class PromptDataManager:
    """专门负责数据管理"""

    def __init__(self):
        self.prompts_data = []
        self.current_selection_index = -1

    def find_prompt_by_identifier(self, identifier):
        """根据标识符查找提示词"""
        for prompt in self.prompts_data:
            if prompt.get("identifier") == identifier:
                return prompt
        return None

    def get_current_prompt(self):
        """获取当前选中的提示词"""
        if 0 <= self.current_selection_index < len(self.prompts_data):
            return self.prompts_data[self.current_selection_index]
        return None

    def add_prompt(self, prompt_data=None):
        """添加新提示词"""
        if prompt_data is None:
            prompt_data = {
                "name": "New Prompt",
                "system_prompt": False,
                "role": "user",
                "content": "",
                "identifier": str(uuid.uuid4()),
                "enabled": True,
                "marker": False,
                "injection_position": 0,
                "injection_depth": 4,
                "injection_order": 100,
                "forbid_overrides": False,
            }

        self.prompts_data.append(prompt_data)
        self.current_selection_index = len(self.prompts_data) - 1
        return self.current_selection_index

    def delete_prompt(self, index):
        """删除提示词"""
        if 0 <= index < len(self.prompts_data):
            del self.prompts_data[index]
            if self.current_selection_index >= len(self.prompts_data):
                self.current_selection_index = len(self.prompts_data) - 1
            return True
        return False

    def update_prompt(self, index, prompt_data):
        """更新提示词数据"""
        if 0 <= index < len(self.prompts_data):
            self.prompts_data[index].update(prompt_data)
            return True
        return False

    def set_current_selection(self, index):
        """设置当前选中的提示词索引"""
        if 0 <= index < len(self.prompts_data):
            self.current_selection_index = index
            return True
        return False

    def get_all_prompts(self):
        """获取所有提示词数据"""
        return self.prompts_data

    def clear_prompts(self):
        """清空所有提示词数据"""
        self.prompts_data = []
        self.current_selection_index = -1

    def populate_from_json(self, json_data):
        """从JSON数据导入提示词"""
        # 获取 character_id = 100001 的顺序信息
        prompt_orders = json_data.get("prompt_order", [])
        order_100001 = next(
            (
                order
                for order in prompt_orders
                if order.get("character_id", 0) == 100001
            ),
            None,
        )

        # 如果没有找到 character_id = 100001 的顺序信息，则创建一个默认的
        if order_100001 is None:
            order_100001 = {"character_id": 100001, "order": []}

        order_list = order_100001.get("order", [])

        # 创建order列表的identifier集合，用于快速查找
        order_identifiers = set(item["identifier"] for item in order_list)

        # 创建一个映射，用于快速查找提示词的启用状态
        prompt_enabled_map = {
            item["identifier"]: item["enabled"] for item in order_list
        }

        # 填充提示词列表
        self.prompts_data = []
        prompts = json_data.get("prompts", [])
        prompts_dict = {prompt.get("identifier"): prompt for prompt in prompts}

        # 先按顺序排列已知的提示词
        ordered_prompts = [
            prompts_dict[item["identifier"]]
            for item in order_list
            if item["identifier"] in prompts_dict
        ]

        # 添加未在顺序列表中的提示词
        ordered_prompt_identifiers = set(
            prompt.get("identifier") for prompt in ordered_prompts
        )
        ordered_prompts.extend(
            prompt
            for prompt in prompts
            if prompt.get("identifier") not in ordered_prompt_identifiers
        )

        # 构建数据结构
        for prompt in ordered_prompts:
            identifier = prompt.get("identifier", "")
            enabled = prompt_enabled_map.get(identifier, True)  # 默认启用

            prompt_data = prompt.copy()
            prompt_data["enabled"] = enabled
            self.prompts_data.append(prompt_data)

        # 清空当前选择
        self.current_selection_index = -1

        return order_list

    def update_json_data(self, json_data):
        """更新JSON数据中的提示词信息"""
        # 更新提示词列表和顺序信息
        prompts = []
        prompt_order = []

        # 遍历提示词数据，更新提示词数据和顺序信息
        for prompt in self.prompts_data:
            # 更新提示词列表
            prompt_copy = {
                k: v for k, v in prompt.items() if k != "enabled"
            }  # 从提示词列表中移除enabled字段
            prompts.append(prompt_copy)

            # 更新顺序信息
            prompt_order.append(
                {
                    "identifier": prompt.get("identifier", ""),
                    "enabled": prompt.get("enabled", True),
                }
            )

        json_data["prompts"] = prompts

        # 更新提示词顺序信息（使用 character_id = 100001）
        prompt_orders = json_data.get("prompt_order", [])
        order_100001 = next(
            (
                order
                for order in prompt_orders
                if order.get("character_id", 0) == 100001
            ),
            None,
        )

        if order_100001 is None:
            prompt_orders.append({"character_id": 100001, "order": prompt_order})
        else:
            order_100001["order"] = prompt_order

        json_data["prompt_order"] = prompt_orders

    def reorder_prompts(self, new_order_identifiers):
        """根据新的标识符顺序重新排列提示词"""
        # 创建一个标识符到提示词的映射
        prompt_dict = {prompt.get("identifier"): prompt for prompt in self.prompts_data}

        # 根据新顺序重新排列提示词数据
        ordered_prompts = [
            prompt_dict[identifier]
            for identifier in new_order_identifiers
            if identifier in prompt_dict
        ]

        # 添加剩余的提示词（不在order表中的）
        ordered_prompt_identifiers = set(
            prompt.get("identifier") for prompt in ordered_prompts
        )
        ordered_prompts.extend(
            prompt
            for prompt in self.prompts_data
            if prompt.get("identifier") not in ordered_prompt_identifiers
        )

        # 更新数据
        self.prompts_data = ordered_prompts

    def extract_variables(self):
        """提取所有变量信息"""
        variables = []
        setvar_names = set()  # 用于跟踪已找到的setvar变量名

        for prompt in self.prompts_data:
            content = prompt.get("content", "")
            identifier = prompt.get("identifier", "")
            name = prompt.get("name", "")

            # 查找 setvar 变量
            setvar_matches = re.findall(r"\{\{setvar::(.*?)::(.*?)\}\}", content)
            for var_name, var_value in setvar_matches:
                variables.append(("setvar", var_name, var_value, identifier, name))
                setvar_names.add(var_name)

            # 查找 getvar 变量
            getvar_matches = re.findall(r"\{\{getvar::(.*?)\}\}", content)
            for var_name in getvar_matches:
                variables.append(("getvar", var_name, "", identifier, name))
                setvar_names.add(var_name)  # 防止重复添加

        return variables


class PromptUIManager:
    """专门负责UI管理"""

    def __init__(self, main_window, data_manager):
        self.main_window = main_window
        self.data_manager = data_manager

    def get_display_text(self, name, enabled, in_order):
        """获取提示词列表项的显示文本"""
        visible_text = "看得见" if in_order else "看不见"
        enabled_text = "启用" if enabled else "禁用"
        return f"[{visible_text}][{enabled_text}] {name}"

    def refresh_all_ui(self):
        """刷新整个UI界面，必须同时刷新，不能单独刷新"""
        # 先确定order table
        self.refresh_order_table()
        # 再确定其他的
        self.refresh_prompts_list()
        self.refresh_variables_table()
        self.refresh_prompt_editor()

    def filter_variables(self, filter_text):
        """根据变量名筛选变量信息表格"""
        self.refresh_variables_table(filter_text)

    def refresh_prompts_list(self):
        """刷新提示词列表"""
        self.main_window.prompts_list.clear()

        # 获取order列表中的标识符
        order_identifiers = set()
        for i in range(self.main_window.order_table.rowCount()):
            item = self.main_window.order_table.item(i, 0)
            if item is not None:
                data = item.data(Qt.UserRole)
                if data is not None:
                    identifier, _ = data
                    order_identifiers.add(identifier)

        # 如果order表格有行数但没有获取到标识符，尝试重新获取
        if not order_identifiers and self.main_window.order_table.rowCount() > 0:
            for i in range(self.main_window.order_table.rowCount()):
                item = self.main_window.order_table.item(i, 0)
                if item is not None:
                    data = item.data(Qt.UserRole)
                    if data is not None:
                        identifier, _ = data
                        order_identifiers.add(identifier)

        for prompt in self.data_manager.get_all_prompts():
            identifier = prompt.get("identifier", "")
            enabled = prompt.get("enabled", True)
            name = prompt.get("name", "")
            # 检查提示词是否在order列表中
            in_order = identifier in order_identifiers
            display_text = self.get_display_text(name, enabled, in_order)

            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, prompt)
            self.main_window.prompts_list.addItem(item)

        # 确保order表格也被正确刷新
        self.main_window.order_table.viewport().update()

    def refresh_variables_table(self, filter_text=""):
        """刷新变量信息表格"""
        # 提取变量信息
        variables = self.data_manager.extract_variables()

        # 如果有筛选文本，则筛选变量
        if filter_text:
            # 找到所有匹配的变量名
            matching_var_names = set()
            for (
                var_type,
                var_name,
                var_value,
                prompt_identifier,
                prompt_name,
            ) in variables:
                if filter_text.lower() in var_name.lower():
                    matching_var_names.add(var_name)

            # 筛选出所有变量名在匹配集合中的变量
            filtered_variables = [
                (var_type, var_name, var_value, prompt_identifier, prompt_name)
                for var_type, var_name, var_value, prompt_identifier, prompt_name in variables
                if var_name in matching_var_names
            ]
            variables = filtered_variables

        # 更新表格
        table = self.main_window.variables_table
        table.setRowCount(len(variables))
        for i, (
            var_type,
            var_name,
            var_value,
            prompt_identifier,
            prompt_name,
        ) in enumerate(variables):
            prompt_item = QTableWidgetItem(prompt_name)
            name_item = QTableWidgetItem(var_name)
            type_item = QTableWidgetItem(var_type)
            value_item = QTableWidgetItem(var_value)

            data = (prompt_identifier, prompt_name)
            prompt_item.setData(Qt.UserRole, data)
            name_item.setData(Qt.UserRole, data)
            type_item.setData(Qt.UserRole, data)
            value_item.setData(Qt.UserRole, data)

            table.setItem(i, 0, prompt_item)
            table.setItem(i, 1, name_item)
            table.setItem(i, 2, type_item)
            table.setItem(i, 3, value_item)

    def refresh_order_table(self):
        """刷新排序表格"""
        # 获取当前order表中的信息
        current_order_info = {}
        for i in range(self.main_window.order_table.rowCount()):
            item = self.main_window.order_table.item(i, 0)
            if item is not None:
                data = item.data(Qt.UserRole)
                if data is not None:
                    identifier, name = data
                    # 获取启用状态
                    enabled_item = self.main_window.order_table.item(i, 1)
                    enabled_text = enabled_item.text() if enabled_item else "启用"
                    enabled = enabled_text == "启用"
                    current_order_info[identifier] = {
                        "name": name,
                        "enabled": enabled,
                        "row": i + 1,
                    }

        # 只为在order表中的提示词创建行
        table = self.main_window.order_table
        table.setRowCount(len(current_order_info))

        # 按照原始顺序填充order表格
        row_index = 0
        for identifier, info in current_order_info.items():
            name_item = QTableWidgetItem(info["name"])
            enabled_item = QTableWidgetItem("启用" if info["enabled"] else "禁用")
            order_item = QTableWidgetItem(str(row_index + 1))

            name_item.setData(Qt.UserRole, (identifier, info["name"]))
            enabled_item.setData(Qt.UserRole, (identifier, info["name"]))
            order_item.setData(Qt.UserRole, (identifier, info["name"]))

            table.setItem(row_index, 0, name_item)
            table.setItem(row_index, 1, enabled_item)
            table.setItem(row_index, 2, order_item)
            row_index += 1

    def refresh_prompt_editor(self):
        """刷新提示词编辑器"""
        prompt = self.data_manager.get_current_prompt()

        if prompt:
            # 定义role到索引的映射
            role_to_index = {"system": 0, "assistant": 1, "user": 2}

            self.main_window.prompt_name_edit.setText(prompt.get("name", ""))
            self.main_window.prompt_system_prompt_check.setChecked(
                prompt.get("system_prompt", False)
            )

            # 设置role下拉选项
            role = prompt.get("role", "user")
            index = role_to_index.get(role, 2)  # 默认为"user"
            self.main_window.prompt_role_combo.setCurrentIndex(index)

            self.main_window.prompt_identifier_edit.setText(
                prompt.get("identifier", "")
            )
            self.main_window.prompt_content_edit.setPlainText(prompt.get("content", ""))
            self.main_window.prompt_marker_check.setChecked(prompt.get("marker", False))
            self.main_window.prompt_enabled_check.setChecked(
                prompt.get("enabled", True)
            )

            # 设置新添加的字段
            injection_position = prompt.get("injection_position", 0)
            position_index = (
                0 if injection_position == 0 else 1 if injection_position == 1 else 0
            )
            self.main_window.prompt_injection_position.setCurrentIndex(position_index)

            self.main_window.prompt_injection_depth.setValue(
                prompt.get("injection_depth", 4)
            )
            self.main_window.prompt_injection_order.setValue(
                prompt.get("injection_order", 100)
            )
            self.main_window.prompt_forbid_overrides_check.setChecked(
                prompt.get("forbid_overrides", False)
            )

            # 检查这个提示词是否在order列表中
            identifier = prompt.get("identifier", "")
            in_order = False
            for i in range(self.main_window.order_table.rowCount()):
                item = self.main_window.order_table.item(i, 0)
                if item is not None:
                    data = item.data(Qt.UserRole)
                    if data is not None:
                        order_identifier, _ = data
                        if order_identifier == identifier:
                            in_order = True
                            break

            # 只有当提示词在order列表中时才勾选复选框
            self.main_window.prompt_add_to_order_check.setChecked(in_order)
        else:
            # 清空编辑器
            self.main_window.prompt_name_edit.clear()
            self.main_window.prompt_system_prompt_check.setChecked(False)
            self.main_window.prompt_role_combo.setCurrentIndex(2)
            self.main_window.prompt_identifier_edit.clear()
            self.main_window.prompt_content_edit.clear()
            self.main_window.prompt_marker_check.setChecked(False)
            self.main_window.prompt_enabled_check.setChecked(False)
            self.main_window.prompt_injection_position.setCurrentIndex(0)
            self.main_window.prompt_injection_depth.setValue(4)
            self.main_window.prompt_injection_order.setValue(100)
            self.main_window.prompt_forbid_overrides_check.setChecked(False)
            self.main_window.prompt_add_to_order_check.setChecked(False)

    def add_prompt_to_order_table(self, prompt_index):
        """将提示词添加到order表格中"""
        if 0 <= prompt_index < len(self.data_manager.get_all_prompts()):
            prompt = self.data_manager.get_all_prompts()[prompt_index]
            identifier = prompt.get("identifier", "")
            name = prompt.get("name", "")
            enabled = prompt.get("enabled", True)

            # 添加到order表
            table = self.main_window.order_table
            row_count = table.rowCount()
            table.setRowCount(row_count + 1)

            name_item = QTableWidgetItem(name)
            enabled_item = QTableWidgetItem("启用" if enabled else "禁用")
            order_item = QTableWidgetItem(str(row_count + 1))

            name_item.setData(Qt.UserRole, (identifier, name))
            enabled_item.setData(Qt.UserRole, (identifier, name))
            order_item.setData(Qt.UserRole, (identifier, name))

            table.setItem(row_count, 0, name_item)
            table.setItem(row_count, 1, enabled_item)
            table.setItem(row_count, 2, order_item)

            # 勾选"是否在列表里"复选框
            self.main_window.prompt_add_to_order_check.setChecked(True)

    def initialize_order_table(self, order_list):
        """初始化order表格"""
        table = self.main_window.order_table
        table.setRowCount(len(order_list))

        # 创建一个标识符到提示词名称的映射
        prompt_names = {
            prompt.get("identifier"): prompt.get("name", "")
            for prompt in self.data_manager.get_all_prompts()
        }

        # 按照顺序列表填充order表格
        for i, item in enumerate(order_list):
            identifier = item["identifier"]
            enabled = item["enabled"]
            prompt_name = prompt_names.get(identifier, "")

            name_item = QTableWidgetItem(prompt_name)
            enabled_item = QTableWidgetItem("启用" if enabled else "禁用")
            order_item = QTableWidgetItem(str(i + 1))  # 设置顺序数字

            name_item.setData(Qt.UserRole, (identifier, prompt_name))
            enabled_item.setData(Qt.UserRole, (identifier, prompt_name))
            order_item.setData(Qt.UserRole, (identifier, prompt_name))

            table.setItem(i, 0, name_item)
            table.setItem(i, 1, enabled_item)
            table.setItem(i, 2, order_item)

        # 刷新整个UI，确保所有组件状态正确
        self.refresh_all_ui()

    def handle_order_table_row_moved(self):
        """处理排序表格行移动"""
        # 获取order表中的新顺序
        new_order = []
        for row in range(self.main_window.order_table.rowCount()):
            # 获取提示词标识符
            item = self.main_window.order_table.item(row, 0)
            if item is not None:
                # 从单元格数据中获取提示词标识符和名称
                data = item.data(Qt.UserRole)
                if data is not None:
                    prompt_identifier, prompt_name = data
                    new_order.append(prompt_identifier)

        # 重新排列提示词数据
        self.data_manager.reorder_prompts(new_order)

        # 刷新UI
        self.refresh_all_ui()


class PromptsTabEditor:
    """主要负责协调数据管理和UI管理"""

    def __init__(self, main_window):
        self.main_window = main_window
        # 初始化数据管理器和UI管理器
        self.data_manager = PromptDataManager()
        self.ui_manager = PromptUIManager(main_window, self.data_manager)

    def on_prompt_selected(self, index):
        """处理提示词选择事件"""
        self.data_manager.set_current_selection(index)
        self.ui_manager.refresh_prompt_editor()

    def add_prompt(self):
        """添加新提示词"""
        self.data_manager.add_prompt()
        self.ui_manager.refresh_all_ui()

    def delete_prompt(self):
        """删除提示词"""
        current_index = self.data_manager.current_selection_index
        if 0 <= current_index < len(self.data_manager.get_all_prompts()):
            reply = QMessageBox.question(
                self.main_window,
                "确认",
                "确定要删除这个提示词吗？",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.data_manager.delete_prompt(current_index)
                self.ui_manager.refresh_all_ui()

    def save_prompt(self):
        """针对行内的某个内容进行修改，修改后保存"""
        current_index = self.data_manager.current_selection_index
        if 0 <= current_index < len(self.data_manager.get_all_prompts()):
            # 定义索引到role的映射
            index_to_role = {0: "system", 1: "assistant", 2: "user"}

            # 获取UI中的数据
            prompt_data = {
                "name": self.main_window.prompt_name_edit.text(),
                "system_prompt": self.main_window.prompt_system_prompt_check.isChecked(),
                "role": index_to_role.get(
                    self.main_window.prompt_role_combo.currentIndex(), "user"
                ),
                "identifier": self.main_window.prompt_identifier_edit.text(),
                "content": self.main_window.prompt_content_edit.toPlainText(),
                "marker": self.main_window.prompt_marker_check.isChecked(),
                "enabled": self.main_window.prompt_enabled_check.isChecked(),
                "injection_position": 0
                if self.main_window.prompt_injection_position.currentIndex() == 0
                else 1,
                "injection_depth": self.main_window.prompt_injection_depth.value(),
                "injection_order": self.main_window.prompt_injection_order.value(),
                "forbid_overrides": self.main_window.prompt_forbid_overrides_check.isChecked(),
            }

            # 更新数据
            self.data_manager.update_prompt(current_index, prompt_data)

            # 处理"是否在列表里"复选框的状态变化
            add_to_order = self.main_window.prompt_add_to_order_check.isChecked()
            identifier = prompt_data.get("identifier", "")

            # 查找在order表中是否已存在该提示词
            found_in_order = False
            row_to_update = -1
            for i in range(self.main_window.order_table.rowCount()):
                item = self.main_window.order_table.item(i, 0)
                if item is not None:
                    data = item.data(Qt.UserRole)
                    if data is not None:
                        order_identifier, _ = data
                        if order_identifier == identifier:
                            found_in_order = True
                            row_to_update = i
                            break

            # 如果用户勾选了"是否在列表里"但提示词不在order表中，则添加
            if add_to_order and not found_in_order and identifier:
                self.ui_manager.add_prompt_to_order_table(current_index)
            # 如果用户取消勾选了"是否在列表里"且提示词在order表中，则移除
            elif not add_to_order and found_in_order and identifier:
                # 从order表中移除
                table = self.main_window.order_table
                table.removeRow(row_to_update)

                # 重新编号
                for i in range(table.rowCount()):
                    order_item = table.item(i, 2)
                    if order_item:
                        order_item.setText(str(i + 1))

            # 刷新UI
            self.ui_manager.refresh_all_ui()

    def populate_prompts_fields(self, json_data):
        """导入整体预设"""
        order_list = self.data_manager.populate_from_json(json_data)
        self.ui_manager.initialize_order_table(order_list)

    def update_prompts_data(self, json_data):
        """更新提示词数据"""
        self.data_manager.update_json_data(json_data)

    def apply_order_sorting(self):
        """给在order列表的内容排序"""
        self.ui_manager.handle_order_table_row_moved()

    def on_order_table_row_moved(self):
        """处理排序表格行移动"""
        self.ui_manager.handle_order_table_row_moved()

    def update_order_table(self):
        """更新排序表格"""
        self.ui_manager.refresh_all_ui()

    def filter_variables(self, filter_text):
        """根据变量名筛选变量信息表格"""
        """调用UI管理器的筛选方法"""
        self.ui_manager.filter_variables(filter_text)
