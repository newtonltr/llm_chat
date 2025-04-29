#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM聊天程序入口
允许用户通过GUI选择使用PyQt5或Tkinter框架
"""

import os
import sys
import importlib.util
import tkinter as tk
from tkinter import messagebox, ttk

def check_module_available(module_name):
    """检查模块是否可用"""
    return importlib.util.find_spec(module_name) is not None

def launch_pyqt_version():
    """启动PyQt5版本"""
    if not check_module_available('PyQt5'):
        messagebox.showerror("错误", "PyQt5未安装。请运行 'pip install PyQt5' 安装它，或选择Tkinter框架。")
        return False

    print("启动PyQt5版本...")
    import main_qt
    main_qt.main()
    return True

def launch_tk_version():
    """启动Tkinter版本"""
    if not check_module_available('tkinter'):
        messagebox.showerror("错误", "Tkinter未安装。这通常是Python标准库的一部分，请检查您的Python安装。")
        return False

    print("启动Tkinter版本...")
    import main_tk
    main_tk.main()
    return True

def show_framework_selector():
    """显示框架选择器对话框"""
    # 创建选择器窗口
    root = tk.Tk()
    root.title("选择GUI框架")
    root.geometry("400x200")
    root.resizable(False, False)

    # 设置窗口居中
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    # 创建标题标签
    title_label = tk.Label(root, text="请选择GUI框架", font=("Arial", 16))
    title_label.pack(pady=20)

    # 创建按钮框架
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)

    # PyQt5按钮
    def on_pyqt_click():
        root.destroy()  # 关闭选择器窗口
        launch_pyqt_version()

    pyqt_btn = ttk.Button(
        button_frame,
        text="PyQt5 (更现代的界面)",
        width=25,
        command=on_pyqt_click
    )
    pyqt_btn.pack(pady=5)

    # Tkinter按钮
    def on_tk_click():
        root.destroy()  # 关闭选择器窗口
        launch_tk_version()

    tk_btn = ttk.Button(
        button_frame,
        text="Tkinter (更轻量级)",
        width=25,
        command=on_tk_click
    )
    tk_btn.pack(pady=5)

    # 运行主循环
    root.mainloop()

def main():
    """程序入口函数"""
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] in ['-qt', '-tk']:
        framework = sys.argv[1][1:]  # 去掉前面的'-'

        if framework == 'qt':
            launch_pyqt_version()
        else:  # framework == 'tk'
            launch_tk_version()
    else:
        # 如果没有指定，则显示选择器对话框
        show_framework_selector()

if __name__ == "__main__":
    main()
