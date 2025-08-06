class MergedSettingsEditor:
    def __init__(self, main_window):
        self.main_window = main_window

    def populate_settings_fields(self, json_data):
        """填充设置字段"""
        # 填充基本参数
        self.main_window.temperature_spin.setValue(json_data.get("temperature", 1.0))
        self.main_window.frequency_penalty_spin.setValue(
            json_data.get("frequency_penalty", 0.0)
        )
        self.main_window.presence_penalty_spin.setValue(
            json_data.get("presence_penalty", 0.0)
        )
        self.main_window.top_p_spin.setValue(json_data.get("top_p", 1.0))
        self.main_window.top_k_spin.setValue(json_data.get("top_k", 0))
        self.main_window.top_a_spin.setValue(json_data.get("top_a", 0.0))
        self.main_window.min_p_spin.setValue(json_data.get("min_p", 0.0))
        self.main_window.repetition_penalty_spin.setValue(
            json_data.get("repetition_penalty", 1.0)
        )
        self.main_window.openai_max_context_spin.setValue(
            json_data.get("openai_max_context", 250000)
        )
        self.main_window.openai_max_tokens_spin.setValue(
            json_data.get("openai_max_tokens", 65536)
        )
        self.main_window.seed_spin.setValue(json_data.get("seed", -1))

        # 填充布尔值参数
        self.main_window.wrap_in_quotes_check.setChecked(
            json_data.get("wrap_in_quotes", False)
        )
        self.main_window.max_context_unlocked_check.setChecked(
            json_data.get("max_context_unlocked", True)
        )
        self.main_window.stream_openai_check.setChecked(
            json_data.get("stream_openai", False)
        )
        self.main_window.show_external_models_check.setChecked(
            json_data.get("show_external_models", False)
        )
        self.main_window.claude_use_sysprompt_check.setChecked(
            json_data.get("claude_use_sysprompt", False)
        )
        self.main_window.squash_system_messages_check.setChecked(
            json_data.get("squash_system_messages", False)
        )
        self.main_window.image_inlining_check.setChecked(
            json_data.get("image_inlining", False)
        )
        self.main_window.bypass_status_check_check.setChecked(
            json_data.get("bypass_status_check", False)
        )
        self.main_window.continue_prefill_check.setChecked(
            json_data.get("continue_prefill", False)
        )

        # 填充文本参数
        self.main_window.send_if_empty_edit.setText(json_data.get("send_if_empty", ""))
        self.main_window.assistant_prefill_edit.setText(
            json_data.get("assistant_prefill", "")
        )
        self.main_window.assistant_impersonation_edit.setText(
            json_data.get("assistant_impersonation", "")
        )
        self.main_window.continue_postfix_edit.setText(
            json_data.get("continue_postfix", "")
        )

        self.main_window.impersonation_prompt_edit.setPlainText(
            json_data.get(
                "impersonation_prompt",
                "[Write your next reply from the point of view of {{user}}, using the chat history so far as a guideline for the writing style of {{user}}. Write 1 reply only in internet RP style. Don't write as {{char}} or system. Don't describe actions of {{char}}.]",
            )
        )
        self.main_window.new_chat_prompt_edit.setPlainText(
            json_data.get("new_chat_prompt", "")
        )
        self.main_window.new_group_chat_prompt_edit.setPlainText(
            json_data.get(
                "new_group_chat_prompt",
                "[Start a new group chat. Group members: {{group}}]",
            )
        )
        self.main_window.new_example_chat_prompt_edit.setPlainText(
            json_data.get("new_example_chat_prompt", "[Example Chat]")
        )
        self.main_window.continue_nudge_prompt_edit.setPlainText(
            json_data.get(
                "continue_nudge_prompt",
                "[Continue the following message. Do not include ANY parts of the original message. Use capitalization and punctuation as if your reply is a part of the original message: {{lastChatMessage}}]",
            )
        )
        self.main_window.group_nudge_prompt_edit.setPlainText(
            json_data.get(
                "group_nudge_prompt", "[Write the next reply only as {{char}}.]"
            )
        )

        # 填充其他参数
        bias_preset = json_data.get("bias_preset_selected", "Default (none)")
        index = self.main_window.bias_preset_combo.findText(bias_preset)
        if index >= 0:
            self.main_window.bias_preset_combo.setCurrentIndex(index)

        self.main_window.names_behavior_spin.setValue(
            json_data.get("names_behavior", 0)
        )
        self.main_window.n_spin.setValue(json_data.get("n", 1))

    def update_settings_data(self, json_data):
        """更新设置数据"""
        # 更新基本参数
        json_data["temperature"] = self.main_window.temperature_spin.value()
        json_data["frequency_penalty"] = self.main_window.frequency_penalty_spin.value()
        json_data["presence_penalty"] = self.main_window.presence_penalty_spin.value()
        json_data["top_p"] = self.main_window.top_p_spin.value()
        json_data["top_k"] = self.main_window.top_k_spin.value()
        json_data["top_a"] = self.main_window.top_a_spin.value()
        json_data["min_p"] = self.main_window.min_p_spin.value()
        json_data["repetition_penalty"] = (
            self.main_window.repetition_penalty_spin.value()
        )
        json_data["openai_max_context"] = (
            self.main_window.openai_max_context_spin.value()
        )
        json_data["openai_max_tokens"] = self.main_window.openai_max_tokens_spin.value()
        json_data["seed"] = self.main_window.seed_spin.value()

        # 更新布尔值参数
        json_data["wrap_in_quotes"] = self.main_window.wrap_in_quotes_check.isChecked()
        json_data["max_context_unlocked"] = (
            self.main_window.max_context_unlocked_check.isChecked()
        )
        json_data["stream_openai"] = self.main_window.stream_openai_check.isChecked()
        json_data["show_external_models"] = (
            self.main_window.show_external_models_check.isChecked()
        )
        json_data["claude_use_sysprompt"] = (
            self.main_window.claude_use_sysprompt_check.isChecked()
        )
        json_data["squash_system_messages"] = (
            self.main_window.squash_system_messages_check.isChecked()
        )
        json_data["image_inlining"] = self.main_window.image_inlining_check.isChecked()
        json_data["bypass_status_check"] = (
            self.main_window.bypass_status_check_check.isChecked()
        )
        json_data["continue_prefill"] = (
            self.main_window.continue_prefill_check.isChecked()
        )

        # 更新文本参数
        json_data["send_if_empty"] = self.main_window.send_if_empty_edit.text()
        json_data["assistant_prefill"] = self.main_window.assistant_prefill_edit.text()
        json_data["assistant_impersonation"] = (
            self.main_window.assistant_impersonation_edit.text()
        )
        json_data["continue_postfix"] = self.main_window.continue_postfix_edit.text()

        json_data["impersonation_prompt"] = (
            self.main_window.impersonation_prompt_edit.toPlainText()
        )
        json_data["new_chat_prompt"] = (
            self.main_window.new_chat_prompt_edit.toPlainText()
        )
        json_data["new_group_chat_prompt"] = (
            self.main_window.new_group_chat_prompt_edit.toPlainText()
        )
        json_data["new_example_chat_prompt"] = (
            self.main_window.new_example_chat_prompt_edit.toPlainText()
        )
        json_data["continue_nudge_prompt"] = (
            self.main_window.continue_nudge_prompt_edit.toPlainText()
        )
        json_data["group_nudge_prompt"] = (
            self.main_window.group_nudge_prompt_edit.toPlainText()
        )

        # 更新其他参数
        json_data["bias_preset_selected"] = (
            self.main_window.bias_preset_combo.currentText()
        )
        json_data["names_behavior"] = self.main_window.names_behavior_spin.value()
        json_data["n"] = self.main_window.n_spin.value()
