#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UI组件模块
包含应用程序的图形用户界面组件
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

from model_handlers import create_model_handler
from config_manager import ConfigManager

class LLMChatApp:
    """LLM聊天应用程序"""

    def __init__(self, root):
        self.root = root
        self.root.title("LLM聊天程序")
        self.root.geometry("1000x700")

        # 初始化配置管理器
        self.config_manager = ConfigManager()

        # 加载配置
        self.config = self.config_manager.load_config()
        self.prompts = self.config_manager.load_prompts()

        # 英文提问按钮状态
        self.english_translation_enabled = False

        # 对话历史记录
        self.chat_history = []

        # 上下文对话保留长度，默认为10
        self.context_length = 10

        # 创建界面
        self.create_ui()

    def create_ui(self):
        """创建用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 添加状态变量，跟踪左侧面板的当前状态
        self.sidebar_visible = True

        # 创建左侧面板（模型选择和参数设置）
        self.left_frame = ttk.LabelFrame(main_frame, text="模型设置", padding=10)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)

        # 设置默认宽度，实际宽度会在窗口显示后自动调整
        self.sidebar_width = 300  # 默认宽度

        # 模型选择
        model_select_frame = ttk.Frame(self.left_frame)
        model_select_frame.pack(fill=tk.X, pady=5)

        ttk.Label(model_select_frame, text="选择模型:").pack(side=tk.LEFT, padx=5)
        self.model_combo = ttk.Combobox(model_select_frame, width=30, state="readonly")
        self.model_combo.pack(side=tk.LEFT, padx=5)
        self.model_combo.bind("<<ComboboxSelected>>", self.on_model_selected)

        # 模型操作按钮 - 使用网格布局
        button_frame = ttk.Frame(self.left_frame)
        button_frame.pack(fill=tk.X, pady=10)

        # 第一行按钮
        ttk.Button(button_frame, text="添加模型", command=self.add_model).grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Button(button_frame, text="编辑模型", command=self.edit_model).grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)

        # 第二行按钮
        ttk.Button(button_frame, text="删除模型", command=self.delete_model).grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Button(button_frame, text="保存配置", command=self.save_config).grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)

        # 配置列的权重，使按钮均匀分布
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        # 添加提示词管理区域到左侧面板
        prompt_frame = ttk.LabelFrame(self.left_frame, text="提示词管理", padding=10)
        prompt_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 提示词选择
        prompt_select_frame = ttk.Frame(prompt_frame)
        prompt_select_frame.pack(fill=tk.X, pady=5)

        ttk.Label(prompt_select_frame, text="选择提示词:").pack(side=tk.LEFT, padx=5)
        self.prompt_combo = ttk.Combobox(prompt_select_frame, width=30, state="readonly")
        self.prompt_combo.pack(side=tk.LEFT, padx=5)
        self.prompt_combo.bind("<<ComboboxSelected>>", self.on_prompt_selected)

        # 提示词操作按钮
        prompt_button_frame = ttk.Frame(prompt_frame)
        prompt_button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(prompt_button_frame, text="添加提示词", command=self.add_prompt).pack(side=tk.LEFT, padx=5)
        ttk.Button(prompt_button_frame, text="编辑提示词", command=self.edit_prompt).pack(side=tk.LEFT, padx=5)
        ttk.Button(prompt_button_frame, text="删除提示词", command=self.delete_prompt).pack(side=tk.LEFT, padx=5)

        # 当前提示词内容显示
        ttk.Label(prompt_frame, text="当前提示词内容:").pack(anchor=tk.W, pady=5)
        self.prompt_content_text = scrolledtext.ScrolledText(prompt_frame, wrap=tk.WORD, width=30, height=10)
        self.prompt_content_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.prompt_content_text.config(state=tk.DISABLED)

        # 上下文设置框架
        context_frame = ttk.LabelFrame(self.left_frame, text="上下文设置")
        context_frame.pack(fill=tk.X, padx=5, pady=5)

        # 上下文长度滑动条
        context_label = ttk.Label(context_frame, text="设置对话上下文保留长度:")
        context_label.pack(fill=tk.X, pady=(5, 0))

        # 滑动条和值显示的框架
        slider_frame = ttk.Frame(context_frame)
        slider_frame.pack(fill=tk.X, pady=5)

        # 创建滑动条
        self.context_slider = ttk.Scale(
            slider_frame,
            from_=0,
            to=20,
            orient=tk.HORIZONTAL,
            value=self.context_length,
            command=self.on_context_length_changed
        )
        self.context_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # 创建值显示标签
        self.context_value_label = ttk.Label(slider_frame, text=str(self.context_length))
        self.context_value_label.pack(side=tk.RIGHT)

        # 添加说明文本
        context_info = ttk.Label(context_frame, text="0表示不保留历史对话，20表示保留最多20轮对话")
        context_info.pack(fill=tk.X, pady=(0, 5))

        # 创建切换按钮框架
        self.toggle_frame = ttk.Frame(main_frame, width=20)
        self.toggle_frame.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=5)

        # 创建切换按钮
        self.toggle_button = ttk.Button(self.toggle_frame, text="◀", width=2, command=self.toggle_sidebar)
        self.toggle_button.pack(side=tk.TOP, pady=10)

        # 创建右侧面板（聊天界面）
        self.right_frame = ttk.LabelFrame(main_frame, text="聊天", padding=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 聊天记录和操作按钮
        chat_top_frame = ttk.Frame(self.right_frame)
        chat_top_frame.pack(fill=tk.X, pady=5)

        # 聊天操作按钮
        self.copy_chat_button = ttk.Button(chat_top_frame, text="复制聊天", command=self.copy_all_text)
        self.copy_chat_button.pack(side=tk.RIGHT, padx=5)

        self.clear_chat_button = ttk.Button(chat_top_frame, text="清空聊天", command=self.clear_chat)
        self.clear_chat_button.pack(side=tk.RIGHT, padx=5)

        # 聊天记录
        self.chat_text = scrolledtext.ScrolledText(self.right_frame, wrap=tk.WORD, width=60, height=20)
        self.chat_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # 创建右键菜单
        self.context_menu = tk.Menu(self.chat_text, tearoff=0)
        self.context_menu.add_command(label="复制", command=self.copy_selected_text)
        self.context_menu.add_command(label="复制全部", command=self.copy_all_text)

        # 绑定右键点击事件
        self.chat_text.bind("<Button-3>", self.show_context_menu)

        # 绑定标准复制快捷键
        self.chat_text.bind("<Control-c>", lambda _: self.copy_selected_text())

        # 配置标签样式 - 使用更轻量级的样式，确保文本可选择
        self.chat_text.tag_configure("user_header", foreground="white", background="#007bff",
                                     font=("Arial", 10, "bold"),
                                     spacing1=5, spacing3=5)
        self.chat_text.tag_configure("user_content", foreground="black", background="#e6f2ff",
                                     spacing1=3, spacing3=5)
        self.chat_text.tag_configure("model_header", foreground="white", background="#28a745",
                                     font=("Arial", 10, "bold"),
                                     spacing1=5, spacing3=5)
        self.chat_text.tag_configure("model_content", foreground="black", background="#e6ffe6",
                                     spacing1=3, spacing3=5)
        self.chat_text.tag_configure("separator", foreground="gray", justify="center",
                                     spacing1=10, spacing3=10)

        self.chat_text.config(state=tk.DISABLED)

        # 输入框
        input_frame = ttk.Frame(self.right_frame)
        input_frame.pack(fill=tk.X, pady=5)

        self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, width=60, height=5)
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.send_button = ttk.Button(input_frame, text="发送", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=5)

        # 添加英文提问按钮
        button_frame = ttk.Frame(self.right_frame)
        button_frame.pack(fill=tk.X, pady=5)

        # 创建一个变量来跟踪按钮状态
        self.english_var = tk.BooleanVar(value=False)

        # 创建英文提问按钮
        self.english_button = ttk.Checkbutton(
            button_frame,
            text="英文提问",
            variable=self.english_var,
            command=self.toggle_english_translation
        )
        self.english_button.pack(side=tk.RIGHT, padx=5)

        # 更新模型和提示词下拉框
        self.update_model_combo()
        self.update_prompt_combo()

    def update_model_combo(self):
        """更新模型下拉框"""
        model_names = [model["name"] for model in self.config["models"]]
        self.model_combo["values"] = model_names
        if model_names:
            self.model_combo.current(0)
            self.on_model_selected(None)

    def update_prompt_combo(self):
        """更新提示词下拉框"""
        prompt_names = [prompt["name"] for prompt in self.prompts["prompts"]]
        self.prompt_combo["values"] = prompt_names
        if prompt_names:
            self.prompt_combo.current(0)
            self.on_prompt_selected(None)  # 更新提示词内容显示区域

    def on_model_selected(self, _):
        """模型选择事件处理"""
        # 由于我们不再在主界面显示模型参数，此方法现在只是一个占位符
        # 如果将来需要在选择模型时执行某些操作，可以在这里添加代码
        pass

    def on_prompt_selected(self, _):
        """提示词选择事件处理"""
        if not self.prompt_combo.get():
            return

        # 获取选中的提示词
        selected_prompt = self.config_manager.get_prompt_by_name(self.prompt_combo.get())

        if selected_prompt:
            # 只更新提示词内容显示区域，不再更新输入框
            self.prompt_content_text.config(state=tk.NORMAL)
            self.prompt_content_text.delete(1.0, tk.END)
            self.prompt_content_text.insert(tk.END, selected_prompt["content"])
            self.prompt_content_text.config(state=tk.DISABLED)

    def add_model_dialog(self, edit_mode=False, model_data=None):
        """添加或编辑模型对话框"""
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("添加模型" if not edit_mode else "编辑模型")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # 创建表单
        form_frame = ttk.Frame(dialog, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # 模型名称
        ttk.Label(form_frame, text="模型名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(form_frame, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)

        # API密钥
        ttk.Label(form_frame, text="API密钥:").grid(row=1, column=0, sticky=tk.W, pady=5)
        api_key_entry = ttk.Entry(form_frame, width=30)
        api_key_entry.grid(row=1, column=1, sticky=tk.W, pady=5)

        # API URL
        ttk.Label(form_frame, text="API URL:").grid(row=2, column=0, sticky=tk.W, pady=5)
        api_url_entry = ttk.Entry(form_frame, width=30)
        api_url_entry.grid(row=2, column=1, sticky=tk.W, pady=5)

        # 模型标识
        ttk.Label(form_frame, text="模型标识:").grid(row=3, column=0, sticky=tk.W, pady=5)
        model_name_entry = ttk.Entry(form_frame, width=30)
        model_name_entry.grid(row=3, column=1, sticky=tk.W, pady=5)

        # 如果是编辑模式，填充现有数据
        original_name = ""
        if edit_mode and model_data:
            name_entry.insert(0, model_data["name"])
            api_key_entry.insert(0, model_data["api_key"])
            api_url_entry.insert(0, model_data["api_url"])
            model_name_entry.insert(0, model_data["model_name"])
            original_name = model_data["name"]

        # 按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=10)

        # 确定按钮回调
        def on_confirm():
            # 获取输入的参数
            name = name_entry.get().strip()
            api_key = api_key_entry.get().strip()
            api_url = api_url_entry.get().strip()
            model_name = model_name_entry.get().strip()

            # 验证输入
            if not name or not api_key or not api_url or not model_name:
                messagebox.showerror("错误", "所有字段都必须填写", parent=dialog)
                return

            # 检查是否已存在同名模型（编辑模式下，如果名称未更改则跳过此检查）
            if not (edit_mode and name == original_name):
                for model in self.config["models"]:
                    if model["name"] == name:
                        messagebox.showerror("错误", f"已存在名为 '{name}' 的模型", parent=dialog)
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
                messagebox.showinfo("成功", f"已更新模型 '{name}'")
            else:
                # 添加新模型
                self.config_manager.add_model(model_data)
                messagebox.showinfo("成功", f"已添加模型 '{name}'")

            # 更新下拉框
            current_selection = self.model_combo.current()
            self.update_model_combo()

            # 如果是编辑模式，尝试保持选择相同的项
            if edit_mode and current_selection >= 0:
                if current_selection < len(self.config["models"]):
                    self.model_combo.current(current_selection)
                else:
                    self.model_combo.current(len(self.config["models"]) - 1)

            # 关闭对话框
            dialog.destroy()

        # 取消按钮回调
        def on_cancel():
            dialog.destroy()

        # 添加按钮
        ttk.Button(button_frame, text="确定", command=on_confirm).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=on_cancel).pack(side=tk.RIGHT, padx=5)

        # 设置焦点
        name_entry.focus_set()

        # 等待对话框关闭
        dialog.wait_window()

    def add_model(self):
        """添加新模型"""
        self.add_model_dialog(edit_mode=False)

    def edit_model(self):
        """编辑模型"""
        if not self.model_combo.get():
            messagebox.showerror("错误", "请先选择一个模型")
            return

        # 获取选中的模型
        selected_model = self.config_manager.get_model_by_name(self.model_combo.get())

        if not selected_model:
            messagebox.showerror("错误", "未找到选中的模型")
            return

        # 打开编辑对话框
        self.add_model_dialog(edit_mode=True, model_data=selected_model)

    def delete_model(self):
        """删除模型"""
        if not self.model_combo.get():
            messagebox.showerror("错误", "请先选择一个模型")
            return

        # 确认删除
        if not messagebox.askyesno("确认", f"确定要删除模型 '{self.model_combo.get()}' 吗？"):
            return

        # 获取当前选中的索引
        current_index = self.model_combo.current()
        model_name = self.model_combo.get()

        # 删除模型
        if self.config_manager.delete_model(model_name):
            # 更新下拉框
            self.update_model_combo()

            # 选择下一个可用的模型
            if self.config["models"]:
                # 如果删除的是最后一个模型，选择新的最后一个
                if current_index >= len(self.config["models"]):
                    self.model_combo.current(len(self.config["models"]) - 1)
                # 否则保持相同的索引
                else:
                    self.model_combo.current(current_index)

            messagebox.showinfo("成功", f"已删除模型 '{model_name}'")

    def save_config(self):
        """保存配置"""
        self.config_manager.save_config()

    def add_prompt(self):
        """添加新提示词"""
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("添加提示词")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # 提示词名称
        ttk.Label(dialog, text="提示词名称:").pack(anchor=tk.W, padx=10, pady=5)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(fill=tk.X, padx=10, pady=5)

        # 提示词内容
        ttk.Label(dialog, text="提示词内容:").pack(anchor=tk.W, padx=10, pady=5)
        content_text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, width=40, height=10)
        content_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 确定按钮
        def on_confirm():
            name = name_entry.get().strip()
            content = content_text.get(1.0, tk.END).strip()

            if not name or not content:
                messagebox.showerror("错误", "名称和内容不能为空", parent=dialog)
                return

            # 检查是否已存在同名提示词
            for prompt in self.prompts["prompts"]:
                if prompt["name"] == name:
                    messagebox.showerror("错误", f"已存在名为 '{name}' 的提示词", parent=dialog)
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

            dialog.destroy()

        ttk.Button(dialog, text="确定", command=on_confirm).pack(pady=10)

    def edit_prompt(self):
        """编辑提示词"""
        if not self.prompt_combo.get():
            messagebox.showerror("错误", "请先选择一个提示词")
            return

        # 获取选中的提示词
        selected_prompt = None
        selected_index = -1
        for i, prompt in enumerate(self.prompts["prompts"]):
            if prompt["name"] == self.prompt_combo.get():
                selected_prompt = prompt
                selected_index = i
                break

        if not selected_prompt:
            messagebox.showerror("错误", "未找到选中的提示词")
            return

        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑提示词")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # 提示词名称
        ttk.Label(dialog, text="提示词名称:").pack(anchor=tk.W, padx=10, pady=5)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(fill=tk.X, padx=10, pady=5)
        name_entry.insert(0, selected_prompt["name"])

        # 提示词内容
        ttk.Label(dialog, text="提示词内容:").pack(anchor=tk.W, padx=10, pady=5)
        content_text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, width=40, height=10)
        content_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        content_text.insert(tk.END, selected_prompt["content"])

        # 确定按钮
        def on_confirm():
            name = name_entry.get().strip()
            content = content_text.get(1.0, tk.END).strip()

            if not name or not content:
                messagebox.showerror("错误", "名称和内容不能为空", parent=dialog)
                return

            # 如果名称已更改，检查是否与其他提示词冲突
            if name != selected_prompt["name"]:
                for prompt in self.prompts["prompts"]:
                    if prompt["name"] == name:
                        messagebox.showerror("错误", f"已存在名为 '{name}' 的提示词", parent=dialog)
                        return

            # 更新提示词
            self.config_manager.update_prompt(selected_index, {
                "name": name,
                "content": content
            })

            # 保存提示词
            self.config_manager.save_prompts()

            # 更新下拉框
            current_selection = self.prompt_combo.current()
            self.update_prompt_combo()
            if current_selection >= 0 and current_selection < len(self.prompts["prompts"]):
                self.prompt_combo.current(current_selection)
                self.on_prompt_selected(None)

            dialog.destroy()

        ttk.Button(dialog, text="确定", command=on_confirm).pack(pady=10)

    def delete_prompt(self):
        """删除提示词"""
        if not self.prompt_combo.get():
            messagebox.showerror("错误", "请先选择一个提示词")
            return

        # 确认删除
        if not messagebox.askyesno("确认", f"确定要删除提示词 '{self.prompt_combo.get()}' 吗？"):
            return

        # 获取当前选中的索引
        current_index = self.prompt_combo.current()
        prompt_name = self.prompt_combo.get()

        # 删除提示词
        if self.config_manager.delete_prompt(prompt_name):
            # 保存提示词
            self.config_manager.save_prompts()

            # 更新下拉框
            self.update_prompt_combo()

            # 选择下一个可用的提示词
            if self.prompts["prompts"]:
                # 如果删除的是最后一个提示词，选择新的最后一个
                if current_index >= len(self.prompts["prompts"]):
                    self.prompt_combo.current(len(self.prompts["prompts"]) - 1)
                # 否则保持相同的索引
                else:
                    self.prompt_combo.current(current_index)
                # 更新提示词内容显示区域
                self.on_prompt_selected(None)
            else:
                # 如果没有提示词了，清空提示词内容显示区域
                self.prompt_content_text.config(state=tk.NORMAL)
                self.prompt_content_text.delete(1.0, tk.END)
                self.prompt_content_text.config(state=tk.DISABLED)

            messagebox.showinfo("成功", f"已删除提示词 '{prompt_name}'")

    def send_message(self):
        """发送消息"""
        if not self.model_combo.get():
            messagebox.showerror("错误", "请先选择一个模型")
            return

        user_message = self.input_text.get(1.0, tk.END).strip()
        if not user_message:
            messagebox.showerror("错误", "请输入消息")
            return

        # 获取选中的模型
        selected_model = self.config_manager.get_model_by_name(self.model_combo.get())

        if not selected_model:
            messagebox.showerror("错误", "未找到选中的模型")
            return

        # 在聊天记录中显示用户消息（只显示用户输入的部分，不显示提示词）
        self.chat_text.config(state=tk.NORMAL)

        # 添加分隔线
        if self.chat_text.get(1.0, tk.END).strip():  # 如果聊天框不为空，添加分隔线
            self.chat_text.insert(tk.END, "\n" + "-" * 50 + "\n", "separator")

        # 添加用户消息头部
        self.chat_text.insert(tk.END, "你 (用户):\n", "user_header")

        # 添加用户消息内容
        self.chat_text.insert(tk.END, f"{user_message}\n", "user_content")

        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)

        # 清空输入框
        self.input_text.delete(1.0, tk.END)

        # 创建模型处理器
        try:
            handler = create_model_handler(selected_model)
        except Exception as e:
            messagebox.showerror("错误", f"创建模型处理器时出错: {str(e)}")
            return

        # 添加状态指示
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"{handler.name}: 正在思考中...\n")
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)

        # 禁用发送按钮，防止重复发送
        self.send_button.config(state=tk.DISABLED)

        # 设置等待光标
        self.root.config(cursor="wait")

        # 将用户消息添加到对话历史记录
        self.chat_history.append({"role": "user", "content": user_message})

        # 在后台线程中发送消息
        def send_in_background():
            try:
                # 检查是否启用了英文提问
                if self.english_translation_enabled:
                    # 获取英文翻译提示词
                    en_tran_prompt = self.config_manager.get_prompt_by_name("en_tran")

                    if not en_tran_prompt:
                        self.root.after(0, self.show_error, "未找到英文翻译提示词'en_tran'，请确保已添加该提示词")
                        return

                    # 构建翻译请求
                    translation_message = en_tran_prompt["content"] + "\n\n" + user_message

                    # 发送翻译请求
                    translated_message = handler.send_message(translation_message)

                    # 使用翻译后的消息构建最终请求
                    final_message = self.build_final_message(translated_message)

                    # 获取历史对话记录（根据滑动条设置的长度）
                    history = self.get_chat_history_for_context()

                    # 发送最终请求（包含历史记录）
                    response = handler.send_message(final_message, history)
                else:
                    # 直接使用原始消息构建最终请求
                    final_message = self.build_final_message(user_message)

                    # 获取历史对话记录（根据滑动条设置的长度）
                    history = self.get_chat_history_for_context()

                    # 发送最终请求（包含历史记录）
                    response = handler.send_message(final_message, history)

                # 使用after方法在主线程中更新UI
                self.root.after(0, self.update_chat_with_response, handler.name, response)
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, self.show_error, f"发送消息时出错: {error_msg}")
            finally:
                # 恢复UI状态
                self.root.after(0, self.reset_ui_after_send)

        # 启动后台线程
        threading.Thread(target=send_in_background, daemon=True).start()

    def build_final_message(self, user_message):
        """构建最终发送给模型的消息，包含提示词"""
        # 检查是否选择了提示词
        if self.prompt_combo.get():
            prompt_name = self.prompt_combo.get()
            selected_prompt = self.config_manager.get_prompt_by_name(prompt_name)

            if selected_prompt and prompt_name != "en_tran":  # 确保不是使用翻译提示词
                # 将提示词内容加在用户输入内容前面
                return selected_prompt["content"] + "\n\n" + user_message

        # 如果没有选择提示词或选择的是翻译提示词，直接返回用户消息
        return user_message

    def update_chat_with_response(self, model_name, response):
        """更新聊天记录，显示模型回复"""
        self.chat_text.config(state=tk.NORMAL)
        # 删除"正在思考中..."的提示
        self.chat_text.delete("end-2l", "end-1c")

        # 添加模型回复头部
        self.chat_text.insert(tk.END, f"{model_name} (AI):\n", "model_header")

        # 添加模型回复内容
        self.chat_text.insert(tk.END, f"{response}\n", "model_content")

        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)

        # 将模型回复添加到对话历史记录
        self.chat_history.append({"role": "assistant", "content": response})

    def show_error(self, error_message):
        """显示错误消息"""
        messagebox.showerror("错误", error_message)

    def reset_ui_after_send(self):
        """重置UI状态"""
        self.send_button.config(state=tk.NORMAL)
        self.root.config(cursor="")

    def clear_chat(self):
        """清空聊天记录"""
        if messagebox.askyesno("确认", "确定要清空所有聊天记录吗？"):
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.delete(1.0, tk.END)
            self.chat_text.config(state=tk.DISABLED)

            # 同时清除对话历史记录
            self.chat_history = []

    def show_context_menu(self, event):
        """显示右键菜单"""
        # 确保文本框处于可选择状态
        current_state = self.chat_text.cget("state")
        if current_state == tk.DISABLED:
            self.chat_text.config(state=tk.NORMAL)
            self.context_menu.post(event.x_root, event.y_root)
            self.chat_text.config(state=current_state)
        else:
            self.context_menu.post(event.x_root, event.y_root)

    def copy_selected_text(self):
        """复制选中的文本"""
        # 确保文本框处于可选择状态
        current_state = self.chat_text.cget("state")
        if current_state == tk.DISABLED:
            self.chat_text.config(state=tk.NORMAL)

        try:
            selected_text = self.chat_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except tk.TclError:
            # 如果没有选中文本，不做任何操作
            pass
        finally:
            # 恢复原始状态
            if current_state == tk.DISABLED:
                self.chat_text.config(state=current_state)

    def copy_all_text(self):
        """复制所有文本"""
        # 确保文本框处于可选择状态
        current_state = self.chat_text.cget("state")
        if current_state == tk.DISABLED:
            self.chat_text.config(state=tk.NORMAL)

        try:
            all_text = self.chat_text.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(all_text)
            messagebox.showinfo("复制成功", "已复制全部聊天内容到剪贴板")
        finally:
            # 恢复原始状态
            if current_state == tk.DISABLED:
                self.chat_text.config(state=current_state)

    def toggle_sidebar(self):
        """切换左侧面板的显示/隐藏状态"""
        if self.sidebar_visible:
            # 隐藏左侧面板
            self.left_frame.pack_forget()
            # 更新切换按钮文本
            self.toggle_button.config(text="▶")
            # 更新状态
            self.sidebar_visible = False
        else:
            # 显示左侧面板
            self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
            # 确保切换按钮在左侧面板右侧
            self.toggle_frame.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=5)
            # 确保右侧面板在最右侧
            self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            # 更新切换按钮文本
            self.toggle_button.config(text="◀")
            # 更新状态
            self.sidebar_visible = True

    def toggle_english_translation(self):
        """切换英文提问按钮状态"""
        self.english_translation_enabled = self.english_var.get()

        # 根据状态更改按钮样式
        style = ttk.Style()
        if self.english_translation_enabled:
            style.configure("TCheckbutton", background="#007bff", foreground="white")
            self.english_button.configure(style="TCheckbutton")
        else:
            style.configure("TCheckbutton", background="", foreground="")
            self.english_button.configure(style="TCheckbutton")

    def on_context_length_changed(self, value):
        """处理上下文长度滑动条值变化"""
        # 将字符串值转换为整数
        self.context_length = int(float(value))
        self.context_value_label.config(text=str(self.context_length))

    def get_chat_history_for_context(self):
        """根据设置的上下文长度，获取要包含在请求中的对话历史记录"""
        # 如果上下文长度为0，不包含历史记录
        if self.context_length == 0 or len(self.chat_history) == 0:
            return []

        # 计算要包含的对话轮数（每轮包含用户和助手的消息）
        # 由于我们是按消息存储的，所以需要乘以2
        context_pairs = self.context_length

        # 确保不超过历史记录的长度
        if context_pairs * 2 > len(self.chat_history):
            # 返回所有历史记录，但不包括最后一条（最后一条是当前用户消息，会在send_message中单独处理）
            return self.chat_history[:-1]
        else:
            # 返回指定长度的历史记录，但不包括最后一条
            start_index = len(self.chat_history) - 1 - (context_pairs * 2)
            if start_index < 0:
                start_index = 0
            return self.chat_history[start_index:-1]
