#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM聊天程序入口 (Tkinter版本)
启动应用程序的Tkinter版本
"""

import tkinter as tk
from ui_components import LLMChatApp

def main():
    """程序入口函数"""
    root = tk.Tk()
    app = LLMChatApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
