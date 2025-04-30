#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Markdown工具模块
提供Markdown到HTML的转换功能
"""

import markdown
from markdown.extensions import Extension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension

def md_to_html(md_text):
    """
    将Markdown文本转换为HTML
    
    Args:
        md_text (str): Markdown格式的文本
        
    Returns:
        str: 转换后的HTML文本
    """
    # 定义扩展列表
    extensions = [
        'tables',                # 表格支持
        'fenced_code',           # 围栏式代码块
        CodeHiliteExtension(     # 代码高亮
            linenums=False,      # 不显示行号
            css_class='codehilite'
        ),
        'nl2br'                  # 将换行符转换为<br>标签
    ]
    
    # 转换Markdown为HTML
    html = markdown.markdown(md_text, extensions=extensions)
    
    # 添加基本样式
    styled_html = f"""
    <div class="markdown-body">
        {html}
    </div>
    """
    
    return styled_html

def get_markdown_css():
    """
    获取Markdown样式的CSS
    
    Returns:
        str: CSS样式文本
    """
    return """
    .markdown-body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        line-height: 1.6;
    }
    .markdown-body h1, .markdown-body h2, .markdown-body h3, 
    .markdown-body h4, .markdown-body h5, .markdown-body h6 {
        margin-top: 24px;
        margin-bottom: 16px;
        font-weight: 600;
        line-height: 1.25;
    }
    .markdown-body h1 { font-size: 2em; }
    .markdown-body h2 { font-size: 1.5em; }
    .markdown-body h3 { font-size: 1.25em; }
    .markdown-body p, .markdown-body blockquote, .markdown-body ul, 
    .markdown-body ol, .markdown-body dl, .markdown-body table {
        margin-top: 0;
        margin-bottom: 16px;
    }
    .markdown-body code {
        padding: 0.2em 0.4em;
        margin: 0;
        font-size: 85%;
        background-color: rgba(27,31,35,0.05);
        border-radius: 3px;
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
    }
    .markdown-body pre {
        padding: 16px;
        overflow: auto;
        font-size: 85%;
        line-height: 1.45;
        background-color: #f6f8fa;
        border-radius: 3px;
    }
    .markdown-body pre code {
        display: inline;
        max-width: auto;
        padding: 0;
        margin: 0;
        overflow: visible;
        line-height: inherit;
        word-wrap: normal;
        background-color: transparent;
        border: 0;
    }
    .markdown-body blockquote {
        padding: 0 1em;
        color: #6a737d;
        border-left: 0.25em solid #dfe2e5;
    }
    .markdown-body ul, .markdown-body ol {
        padding-left: 2em;
    }
    .markdown-body table {
        display: block;
        width: 100%;
        overflow: auto;
        border-spacing: 0;
        border-collapse: collapse;
    }
    .markdown-body table th {
        font-weight: 600;
    }
    .markdown-body table th, .markdown-body table td {
        padding: 6px 13px;
        border: 1px solid #dfe2e5;
    }
    .markdown-body table tr {
        background-color: #fff;
        border-top: 1px solid #c6cbd1;
    }
    .markdown-body table tr:nth-child(2n) {
        background-color: #f6f8fa;
    }
    .codehilite {
        background-color: #f8f8f8;
        border-radius: 3px;
        padding: 0.5em;
        margin-bottom: 16px;
    }
    .codehilite .hll { background-color: #ffffcc }
    .codehilite .c { color: #408080; font-style: italic } /* Comment */
    .codehilite .k { color: #008000; font-weight: bold } /* Keyword */
    .codehilite .o { color: #666666 } /* Operator */
    .codehilite .cm { color: #408080; font-style: italic } /* Comment.Multiline */
    .codehilite .cp { color: #BC7A00 } /* Comment.Preproc */
    .codehilite .c1 { color: #408080; font-style: italic } /* Comment.Single */
    .codehilite .cs { color: #408080; font-style: italic } /* Comment.Special */
    .codehilite .gd { color: #A00000 } /* Generic.Deleted */
    .codehilite .ge { font-style: italic } /* Generic.Emph */
    .codehilite .gr { color: #FF0000 } /* Generic.Error */
    .codehilite .gh { color: #000080; font-weight: bold } /* Generic.Heading */
    .codehilite .gi { color: #00A000 } /* Generic.Inserted */
    .codehilite .go { color: #888888 } /* Generic.Output */
    .codehilite .gp { color: #000080; font-weight: bold } /* Generic.Prompt */
    .codehilite .gs { font-weight: bold } /* Generic.Strong */
    .codehilite .gu { color: #800080; font-weight: bold } /* Generic.Subheading */
    .codehilite .gt { color: #0044DD } /* Generic.Traceback */
    .codehilite .kc { color: #008000; font-weight: bold } /* Keyword.Constant */
    .codehilite .kd { color: #008000; font-weight: bold } /* Keyword.Declaration */
    .codehilite .kn { color: #008000; font-weight: bold } /* Keyword.Namespace */
    .codehilite .kp { color: #008000 } /* Keyword.Pseudo */
    .codehilite .kr { color: #008000; font-weight: bold } /* Keyword.Reserved */
    .codehilite .kt { color: #B00040 } /* Keyword.Type */
    .codehilite .m { color: #666666 } /* Literal.Number */
    .codehilite .s { color: #BA2121 } /* Literal.String */
    """
