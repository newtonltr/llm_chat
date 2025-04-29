#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM聊天程序入口 (PyQt5版本)
启动应用程序的PyQt5版本
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui_components_qt import LLMChatApp

def main():
    """程序入口函数"""
    app = QApplication(sys.argv)
    window = LLMChatApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
