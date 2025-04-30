#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UI组件模块 (PyQt5版本)
包含应用程序的图形用户界面组件
"""

import sys
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QComboBox, QPushButton, QTextEdit, QLineEdit,
                            QFrame, QSplitter, QDialog, QFormLayout, QMessageBox,
                            QMenu, QAction, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QTextCursor, QIcon

from model_handlers import create_model_handler
from config_manager import ConfigManager
from markdown_utils import md_to_html, get_markdown_css

class LLMChatApp(QMainWindow):
    """LLM聊天应用程序 (PyQt5版本)"""

    # 定义信号
    response_received = pyqtSignal(str, str)  # 模型名称, 回复内容
    ui_reset_signal = pyqtSignal()
    error_signal = pyqtSignal(str)  # 错误消息

    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.setWindowTitle("LLM聊天程序")
        self.resize(1000, 700)

        # 初始化配置管理器
        self.config_manager = ConfigManager()

        # 加载配置
        self.config = self.config_manager.load_config()
        self.prompts = self.config_manager.load_prompts()

        # 侧边栏可见状态
        self.sidebar_visible = True

        # 连接信号和槽
        self.response_received.connect(self.update_chat_with_response)
        self.ui_reset_signal.connect(self.reset_ui_after_send)
        self.error_signal.connect(self.show_error)

        # 创建界面
        self.create_ui()

        # 设置Markdown样式
        self.setup_markdown_style()

    def create_ui(self):
        """创建用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QHBoxLayout(central_widget)

        # 创建左侧面板（模型选择和参数设置）
        self.left_panel = QWidget()
        self.left_panel.setMinimumWidth(300)
        self.left_panel.setMaximumWidth(300)
        left_layout = QVBoxLayout(self.left_panel)

        # 模型设置组
        model_group = QGroupBox("模型设置")
        model_layout = QVBoxLayout(model_group)

        # 模型选择
        model_select_layout = QHBoxLayout()
        model_select_layout.addWidget(QLabel("选择模型:"))
        self.model_combo = QComboBox()
        self.model_combo.currentIndexChanged.connect(self.on_model_selected)
        model_select_layout.addWidget(self.model_combo)
        model_layout.addLayout(model_select_layout)

        # 模型操作按钮
        button_layout = QGridLayout()
        add_model_btn = QPushButton("添加模型")
        add_model_btn.clicked.connect(self.add_model)
        button_layout.addWidget(add_model_btn, 0, 0)

        edit_model_btn = QPushButton("编辑模型")
        edit_model_btn.clicked.connect(self.edit_model)
        button_layout.addWidget(edit_model_btn, 0, 1)

        delete_model_btn = QPushButton("删除模型")
        delete_model_btn.clicked.connect(self.delete_model)
        button_layout.addWidget(delete_model_btn, 1, 0)

        save_config_btn = QPushButton("保存配置")
        save_config_btn.clicked.connect(self.save_config)
        button_layout.addWidget(save_config_btn, 1, 1)

        model_layout.addLayout(button_layout)
        left_layout.addWidget(model_group)

        # 提示词管理组
        prompt_group = QGroupBox("提示词管理")
        prompt_layout = QVBoxLayout(prompt_group)

        # 提示词选择
        prompt_select_layout = QHBoxLayout()
        prompt_select_layout.addWidget(QLabel("选择提示词:"))
        self.prompt_combo = QComboBox()
        self.prompt_combo.currentIndexChanged.connect(self.on_prompt_selected)
        prompt_select_layout.addWidget(self.prompt_combo)
        prompt_layout.addLayout(prompt_select_layout)

        # 提示词操作按钮
        prompt_button_layout = QHBoxLayout()
        add_prompt_btn = QPushButton("添加提示词")
        add_prompt_btn.clicked.connect(self.add_prompt)
        prompt_button_layout.addWidget(add_prompt_btn)

        edit_prompt_btn = QPushButton("编辑提示词")
        edit_prompt_btn.clicked.connect(self.edit_prompt)
        prompt_button_layout.addWidget(edit_prompt_btn)

        delete_prompt_btn = QPushButton("删除提示词")
        delete_prompt_btn.clicked.connect(self.delete_prompt)
        prompt_button_layout.addWidget(delete_prompt_btn)

        prompt_layout.addLayout(prompt_button_layout)

        # 当前提示词内容显示
        prompt_layout.addWidget(QLabel("当前提示词内容:"))
        self.prompt_content_text = QTextEdit()
        self.prompt_content_text.setReadOnly(True)
        prompt_layout.addWidget(self.prompt_content_text)

        left_layout.addWidget(prompt_group)

        # 创建切换按钮
        self.toggle_btn = QPushButton("◀")
        self.toggle_btn.setFixedWidth(20)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)

        # 创建右侧面板（聊天界面）
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # 聊天记录和操作按钮
        chat_top_layout = QHBoxLayout()
        chat_top_layout.addStretch()

        copy_chat_btn = QPushButton("复制聊天")
        copy_chat_btn.clicked.connect(self.copy_all_text)
        chat_top_layout.addWidget(copy_chat_btn)

        clear_chat_btn = QPushButton("清空聊天")
        clear_chat_btn.clicked.connect(self.clear_chat)
        chat_top_layout.addWidget(clear_chat_btn)

        right_layout.addLayout(chat_top_layout)

        # 聊天记录
        self.chat_text = QTextEdit()
        self.chat_text.setReadOnly(True)
        self.chat_text.setContextMenuPolicy(Qt.CustomContextMenu)
        self.chat_text.customContextMenuRequested.connect(self.show_context_menu)
        # 启用HTML支持
        self.chat_text.setAcceptRichText(True)
        right_layout.addWidget(self.chat_text)

        # 输入框和发送按钮
        input_layout = QHBoxLayout()
        self.input_text = QTextEdit()
        self.input_text.setFixedHeight(100)
        input_layout.addWidget(self.input_text)

        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        right_layout.addLayout(input_layout)

        # 添加到主布局
        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(self.toggle_btn)
        main_layout.addWidget(right_panel)

        # 创建右键菜单
        self.context_menu = QMenu(self)
        copy_action = QAction("复制", self)
        copy_action.triggered.connect(self.copy_selected_text)
        self.context_menu.addAction(copy_action)

        copy_all_action = QAction("复制全部", self)
        copy_all_action.triggered.connect(self.copy_all_text)
        self.context_menu.addAction(copy_all_action)

        # 更新模型和提示词下拉框
        self.update_model_combo()
        self.update_prompt_combo()

    def update_model_combo(self):
        """更新模型下拉框"""
        self.model_combo.clear()
        model_names = [model["name"] for model in self.config["models"]]
        self.model_combo.addItems(model_names)
        if model_names:
            self.model_combo.setCurrentIndex(0)
            self.on_model_selected(0)

    def update_prompt_combo(self):
        """更新提示词下拉框"""
        self.prompt_combo.clear()
        prompt_names = [prompt["name"] for prompt in self.prompts["prompts"]]
        self.prompt_combo.addItems(prompt_names)
        if prompt_names:
            self.prompt_combo.setCurrentIndex(0)
            self.on_prompt_selected(0)  # 更新提示词内容显示区域

    def on_model_selected(self, _):
        """模型选择事件处理"""
        # 由于我们不再在主界面显示模型参数，此方法现在只是一个占位符
        # 如果将来需要在选择模型时执行某些操作，可以在这里添加代码
        pass

    def on_prompt_selected(self, index):
        """提示词选择事件处理"""
        if index < 0 or self.prompt_combo.count() == 0:
            return

        # 获取选中的提示词
        prompt_name = self.prompt_combo.currentText()
        selected_prompt = self.config_manager.get_prompt_by_name(prompt_name)

        if selected_prompt:
            # 更新提示词内容显示区域
            self.prompt_content_text.clear()
            self.prompt_content_text.setText(selected_prompt["content"])

    def add_model_dialog(self, edit_mode=False, model_data=None):
        """添加或编辑模型对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("添加模型" if not edit_mode else "编辑模型")
        dialog.resize(400, 300)

        layout = QVBoxLayout(dialog)

        # 创建表单
        form_layout = QFormLayout()

        # 模型名称
        name_edit = QLineEdit()
        form_layout.addRow("模型名称:", name_edit)

        # API密钥
        api_key_edit = QLineEdit()
        form_layout.addRow("API密钥:", api_key_edit)

        # API URL
        api_url_edit = QLineEdit()
        form_layout.addRow("API URL:", api_url_edit)

        # 模型标识
        model_name_edit = QLineEdit()
        form_layout.addRow("模型标识:", model_name_edit)

        layout.addLayout(form_layout)

        # 如果是编辑模式，填充现有数据
        original_name = ""
        if edit_mode and model_data:
            name_edit.setText(model_data["name"])
            api_key_edit.setText(model_data["api_key"])
            api_url_edit.setText(model_data["api_url"])
            model_name_edit.setText(model_data["model_name"])
            original_name = model_data["name"]

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        # 确定按钮
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

        # 显示对话框
        if dialog.exec_() == QDialog.Accepted:
            # 获取输入的参数
            name = name_edit.text().strip()
            api_key = api_key_edit.text().strip()
            api_url = api_url_edit.text().strip()
            model_name = model_name_edit.text().strip()

            # 验证输入
            if not name or not api_key or not api_url or not model_name:
                QMessageBox.critical(self, "错误", "所有字段都必须填写")
                return

            # 检查是否已存在同名模型（编辑模式下，如果名称未更改则跳过此检查）
            if not (edit_mode and name == original_name):
                for model in self.config["models"]:
                    if model["name"] == name:
                        QMessageBox.critical(self, "错误", f"已存在名为 '{name}' 的模型")
                        return

            # 创建模型数据
            model_data = {
                "name": name,
                "api_key": api_key,
                "api_url": api_url,
                "model_name": model_name
            }

            # 根据模式执行不同操作
            if edit_mode:
                # 更新现有模型
                self.config_manager.update_model(original_name, model_data)
                QMessageBox.information(self, "成功", f"已更新模型 '{name}'")
            else:
                # 添加新模型
                self.config_manager.add_model(model_data)
                QMessageBox.information(self, "成功", f"已添加模型 '{name}'")

            # 更新下拉框
            current_index = self.model_combo.currentIndex()
            self.update_model_combo()

            # 如果是编辑模式，尝试保持选择相同的项
            if edit_mode and current_index >= 0:
                if current_index < len(self.config["models"]):
                    self.model_combo.setCurrentIndex(current_index)
                else:
                    self.model_combo.setCurrentIndex(len(self.config["models"]) - 1)

    def add_model(self):
        """添加新模型"""
        self.add_model_dialog(edit_mode=False)

    def edit_model(self):
        """编辑模型"""
        if self.model_combo.count() == 0:
            QMessageBox.warning(self, "错误", "请先选择一个模型")
            return

        # 获取选中的模型
        model_name = self.model_combo.currentText()
        selected_model = self.config_manager.get_model_by_name(model_name)

        if not selected_model:
            QMessageBox.warning(self, "错误", "未找到选中的模型")
            return

        # 打开编辑对话框
        self.add_model_dialog(edit_mode=True, model_data=selected_model)

    def delete_model(self):
        """删除模型"""
        if self.model_combo.count() == 0:
            QMessageBox.warning(self, "错误", "请先选择一个模型")
            return

        model_name = self.model_combo.currentText()

        # 确认删除
        reply = QMessageBox.question(self, "确认", f"确定要删除模型 '{model_name}' 吗？",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        # 获取当前选中的索引
        current_index = self.model_combo.currentIndex()

        # 删除模型
        if self.config_manager.delete_model(model_name):
            # 更新下拉框
            self.update_model_combo()

            # 选择下一个可用的模型
            if self.model_combo.count() > 0:
                # 如果删除的是最后一个模型，选择新的最后一个
                if current_index >= self.model_combo.count():
                    self.model_combo.setCurrentIndex(self.model_combo.count() - 1)
                # 否则保持相同的索引
                else:
                    self.model_combo.setCurrentIndex(current_index)

            QMessageBox.information(self, "成功", f"已删除模型 '{model_name}'")

    def save_config(self):
        """保存配置"""
        if self.config_manager.save_config():
            QMessageBox.information(self, "成功", "配置已保存")

    def add_prompt(self):
        """添加新提示词"""
        dialog = QDialog(self)
        dialog.setWindowTitle("添加提示词")
        dialog.resize(400, 300)

        layout = QVBoxLayout(dialog)

        # 提示词名称
        name_label = QLabel("提示词名称:")
        layout.addWidget(name_label)

        name_edit = QLineEdit()
        layout.addWidget(name_edit)

        # 提示词内容
        content_label = QLabel("提示词内容:")
        layout.addWidget(content_label)

        content_text = QTextEdit()
        layout.addWidget(content_text)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        # 确定按钮
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

        # 显示对话框
        if dialog.exec_() == QDialog.Accepted:
            name = name_edit.text().strip()
            content = content_text.toPlainText().strip()

            if not name or not content:
                QMessageBox.critical(self, "错误", "名称和内容不能为空")
                return

            # 检查是否已存在同名提示词
            for prompt in self.prompts["prompts"]:
                if prompt["name"] == name:
                    QMessageBox.critical(self, "错误", f"已存在名为 '{name}' 的提示词")
                    return

            # 添加新提示词
            self.config_manager.add_prompt({
                "name": name,
                "content": content
            })

            # 保存提示词
            self.config_manager.save_prompts()

            # 更新下拉框
            self.update_prompt_combo()

    def edit_prompt(self):
        """编辑提示词"""
        if self.prompt_combo.count() == 0:
            QMessageBox.warning(self, "错误", "请先选择一个提示词")
            return

        prompt_name = self.prompt_combo.currentText()

        # 获取选中的提示词
        selected_prompt = None
        selected_index = -1
        for i, prompt in enumerate(self.prompts["prompts"]):
            if prompt["name"] == prompt_name:
                selected_prompt = prompt
                selected_index = i
                break

        if not selected_prompt:
            QMessageBox.warning(self, "错误", "未找到选中的提示词")
            return

        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("编辑提示词")
        dialog.resize(400, 300)

        layout = QVBoxLayout(dialog)

        # 提示词名称
        name_label = QLabel("提示词名称:")
        layout.addWidget(name_label)

        name_edit = QLineEdit()
        name_edit.setText(selected_prompt["name"])
        layout.addWidget(name_edit)

        # 提示词内容
        content_label = QLabel("提示词内容:")
        layout.addWidget(content_label)

        content_text = QTextEdit()
        content_text.setText(selected_prompt["content"])
        layout.addWidget(content_text)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        # 确定按钮
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

        # 显示对话框
        if dialog.exec_() == QDialog.Accepted:
            name = name_edit.text().strip()
            content = content_text.toPlainText().strip()

            if not name or not content:
                QMessageBox.critical(self, "错误", "名称和内容不能为空")
                return

            # 如果名称已更改，检查是否与其他提示词冲突
            if name != selected_prompt["name"]:
                for prompt in self.prompts["prompts"]:
                    if prompt["name"] == name:
                        QMessageBox.critical(self, "错误", f"已存在名为 '{name}' 的提示词")
                        return

            # 更新提示词
            self.config_manager.update_prompt(selected_index, {
                "name": name,
                "content": content
            })

            # 保存提示词
            self.config_manager.save_prompts()

            # 更新下拉框
            current_index = self.prompt_combo.currentIndex()
            self.update_prompt_combo()
            if current_index >= 0 and current_index < len(self.prompts["prompts"]):
                self.prompt_combo.setCurrentIndex(current_index)
                self.on_prompt_selected(current_index)

    def delete_prompt(self):
        """删除提示词"""
        if self.prompt_combo.count() == 0:
            QMessageBox.warning(self, "错误", "请先选择一个提示词")
            return

        prompt_name = self.prompt_combo.currentText()

        # 确认删除
        reply = QMessageBox.question(self, "确认", f"确定要删除提示词 '{prompt_name}' 吗？",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        # 获取当前选中的索引
        current_index = self.prompt_combo.currentIndex()

        # 删除提示词
        if self.config_manager.delete_prompt(prompt_name):
            # 保存提示词
            self.config_manager.save_prompts()

            # 更新下拉框
            self.update_prompt_combo()

            # 选择下一个可用的提示词
            if self.prompt_combo.count() > 0:
                # 如果删除的是最后一个提示词，选择新的最后一个
                if current_index >= self.prompt_combo.count():
                    self.prompt_combo.setCurrentIndex(self.prompt_combo.count() - 1)
                # 否则保持相同的索引
                else:
                    self.prompt_combo.setCurrentIndex(current_index)
                # 更新提示词内容显示区域
                self.on_prompt_selected(self.prompt_combo.currentIndex())
            else:
                # 如果没有提示词了，清空提示词内容显示区域
                self.prompt_content_text.clear()

            QMessageBox.information(self, "成功", f"已删除提示词 '{prompt_name}'")

    def send_message(self):
        """发送消息"""
        if self.model_combo.count() == 0:
            QMessageBox.warning(self, "错误", "请先选择一个模型")
            return

        user_message = self.input_text.toPlainText().strip()
        if not user_message:
            QMessageBox.warning(self, "错误", "请输入消息")
            return

        # 获取选中的模型
        model_name = self.model_combo.currentText()
        selected_model = self.config_manager.get_model_by_name(model_name)

        if not selected_model:
            QMessageBox.warning(self, "错误", "未找到选中的模型")
            return

        # 检查是否选择了提示词，如果选择了，将提示词内容加在用户输入内容前面
        message = user_message
        if self.prompt_combo.count() > 0:
            prompt_name = self.prompt_combo.currentText()
            selected_prompt = self.config_manager.get_prompt_by_name(prompt_name)

            if selected_prompt:
                # 将提示词内容加在用户输入内容前面
                message = selected_prompt["content"] + "\n\n" + user_message

        # 在聊天记录中显示用户消息（只显示用户输入的部分，不显示提示词）
        # 添加分隔线
        if not self.chat_text.toPlainText().strip() == "":
            self.chat_text.append("-" * 50)

        # 添加用户消息头部
        self.chat_text.append("<strong>你 (用户):</strong>")

        # 将用户消息转换为HTML并添加
        user_message_html = md_to_html(user_message)
        self.chat_text.append(user_message_html)
        self.chat_text.append("")  # 空行

        # 滚动到底部
        self.chat_text.moveCursor(QTextCursor.End)

        # 清空输入框
        self.input_text.clear()

        # 创建模型处理器
        try:
            handler = create_model_handler(selected_model)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建模型处理器时出错: {str(e)}")
            return

        # 添加状态指示（使用HTML格式使其更加明显）
        self.chat_text.append(f'<span style="color: #0066cc; font-weight: bold;">{handler.name}: 正在思考中...</span>')

        # 禁用发送按钮，防止重复发送
        self.send_button.setEnabled(False)

        # 在后台线程中发送消息
        def send_in_background():
            try:
                response = handler.send_message(message)
                # 使用信号槽机制在主线程中更新UI
                self.response_received.emit(handler.name, response)
            except Exception as e:
                error_msg = str(e)
                # 使用信号发送错误消息到主线程
                self.error_signal.emit(f"发送消息时出错: {error_msg}")
            finally:
                # 恢复UI状态
                self.ui_reset_signal.emit()

        # 启动后台线程
        threading.Thread(target=send_in_background, daemon=True).start()

    def update_chat_with_response(self, model_name, response):
        """更新聊天记录，显示模型回复"""
        # 获取当前文本的HTML
        current_html = self.chat_text.toHtml()

        # 查找并删除"正在思考中..."的HTML标记
        thinking_text = f'<span style="color: #0066cc; font-weight: bold;">{model_name}: 正在思考中...</span>'
        if thinking_text in current_html:
            # 找到最后一个段落的开始位置
            last_para_start = current_html.rfind("<p", 0, current_html.rfind(thinking_text))
            if last_para_start != -1:
                # 找到段落的结束位置
                last_para_end = current_html.find("</p>", last_para_start) + 4

                # 删除包含"正在思考中..."的段落
                current_html = current_html[:last_para_start] + current_html[last_para_end:]
                self.chat_text.setHtml(current_html)

        # 添加模型回复头部
        self.chat_text.append(f"<strong>{model_name} (AI):</strong>")

        # 将模型回复转换为HTML并添加
        response_html = md_to_html(response)
        self.chat_text.append(response_html)
        self.chat_text.append("")  # 空行

        # 滚动到底部
        self.chat_text.verticalScrollBar().setValue(self.chat_text.verticalScrollBar().maximum())

    def reset_ui_after_send(self):
        """重置UI状态"""
        self.send_button.setEnabled(True)

    def show_error(self, error_message):
        """显示错误消息"""
        QMessageBox.critical(self, "错误", error_message)

    def clear_chat(self):
        """清空聊天记录"""
        reply = QMessageBox.question(self, "确认", "确定要清空所有聊天记录吗？",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.chat_text.clear()

    def show_context_menu(self, position):
        """显示右键菜单"""
        self.context_menu.exec_(self.chat_text.mapToGlobal(position))

    def copy_selected_text(self):
        """复制选中的文本"""
        self.chat_text.copy()

    def copy_all_text(self):
        """复制所有文本"""
        cursor = self.chat_text.textCursor()
        cursor.select(QTextCursor.Document)
        self.chat_text.setTextCursor(cursor)
        self.chat_text.copy()
        QMessageBox.information(self, "复制成功", "已复制全部聊天内容到剪贴板")

        # 取消选择
        cursor.clearSelection()
        self.chat_text.setTextCursor(cursor)

    def setup_markdown_style(self):
        """设置Markdown样式"""
        # 获取Markdown CSS样式
        css = get_markdown_css()

        # 创建样式表
        style_sheet = f"""
        QTextEdit {{
            background-color: white;
            color: black;
            selection-background-color: #b5d5ff;
        }}
        {css}
        """

        # 应用样式表到聊天文本框
        self.chat_text.document().setDefaultStyleSheet(style_sheet)

        # 启用富文本
        self.chat_text.setAcceptRichText(True)

    def toggle_sidebar(self):
        """切换左侧面板的显示/隐藏状态"""
        if self.sidebar_visible:
            # 隐藏左侧面板
            self.left_panel.hide()
            # 更新切换按钮文本
            self.toggle_btn.setText("▶")
            # 更新状态
            self.sidebar_visible = False
        else:
            # 显示左侧面板
            self.left_panel.show()
            # 更新切换按钮文本
            self.toggle_btn.setText("◀")
            # 更新状态
            self.sidebar_visible = True
