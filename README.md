# LLM聊天程序 (LLM Chat Application)

一个基于Python和PyQt5的大语言模型聊天应用程序，支持多种LLM API接口，提供友好的图形用户界面，方便用户与各种大语言模型进行交互。

## 功能特点

- **多模型支持**：内置支持OpenRouter、Google Gemini和DeepSeek等多种API接口
- **模型管理**：可视化界面添加、编辑和删除模型配置
- **提示词管理**：创建、编辑和使用预设提示词，提高交互效率

## 支持的API

- [OpenRouter](https://openrouter.ai/) - 支持多种开源和商业模型
- [Google Gemini](https://ai.google.dev/) - Google的Gemini系列模型
- [DeepSeek](https://www.deepseek.com/) - DeepSeek的AI模型

## 安装说明

### 前提条件

- Python 3.6+
- pip (Python包管理器)

### 安装步骤

1. 克隆仓库到本地：

```bash
git clone https://github.com/newtonltr/llm_chat.git
cd llm-chat-app
```

1. 安装依赖：

```bash
pip install -r requirements.txt
```

1. 运行应用程序：

```bash
python main.py  # 会弹出GUI选择框，让您选择使用PyQt5或Tkinter框架
# 或者直接指定框架
python main.py -qt  # 使用PyQt5框架
python main.py -tk  # 使用Tkinter框架
```

您也可以直接运行特定版本：

```bash
python main_qt.py  # 直接运行PyQt5版本
python main_tk.py  # 直接运行Tkinter版本
```

## 配置说明

### 模型配置

应用程序使用`llm_config.json`文件存储模型配置。每个模型配置包含以下字段：

- `name`: 模型显示名称
- `api_key`: API密钥
- `api_url`: API端点URL
- `model_name`: 模型标识符

示例配置：

```json
{
    "models": [
        {
            "name": "Gemini Pro",
            "api_key": "YOUR_API_KEY",
            "api_url": "https://generativelanguage.googleapis.com/v1beta/models",
            "model_name": "gemini-pro"
        }
    ]
}
```

### 提示词配置

应用程序使用`prompts.json`文件存储提示词配置。每个提示词包含以下字段：

- `name`: 提示词名称
- `content`: 提示词内容

示例配置：

```json
{
    "prompts": [
        {
            "name": "简单问候",
            "content": "你好，请简单介绍一下你自己。"
        }
    ]
}
```

## 使用指南

### 添加新模型

1. 点击"添加模型"按钮
2. 填写模型名称、API密钥、API URL和模型标识符
3. 点击"确定"保存

### 使用提示词

1. 从提示词下拉菜单中选择一个提示词
2. 在输入框中输入您的问题
3. 点击"发送"按钮，提示词内容将与您的问题一起发送给模型

### 管理聊天记录

- 使用右上角的"复制聊天"按钮复制所有聊天内容
- 使用右上角的"清空聊天"按钮清除聊天历史
- 右键点击聊天区域可以复制选中的文本

## 开发说明

### 项目结构

- `main.py`: 程序入口文件（框架选择器）
- `main_qt.py`: PyQt5版本入口文件
- `main_tk.py`: Tkinter版本入口文件
- `model_handlers.py`: 模型处理器类
- `config_manager.py`: 配置管理类
- `ui_components_qt.py`: PyQt5用户界面组件
- `ui_components.py`: Tkinter用户界面组件
- `llm_config.json`: 模型配置文件
- `prompts.json`: 提示词配置文件
- `requirements.txt`: 依赖列表

### 技术实现细节

#### 多线程处理

为了保持UI的响应性，程序在后台线程中处理API请求：

- **PyQt5版本**：使用信号槽机制（Signals/Slots）在线程间安全通信
  - `response_received`信号：从工作线程发送模型回复到主线程
  - `error_signal`信号：从工作线程发送错误消息到主线程
  - `ui_reset_signal`信号：重置UI状态

- **Tkinter版本**：使用`after`方法在主线程中安全更新UI

### 添加新的API支持

要添加对新API的支持，需要：

1. 在`model_handlers.py`中创建一个新的处理器类，继承自`ModelHandler`
2. 实现`send_message`方法
3. 在`create_model_handler`函数中添加对新API的识别逻辑

示例：

```python
class NewAPIHandler(ModelHandler):
    """新API处理器"""

    def send_message(self, message):
        # 实现与新API的通信逻辑
        pass

# 在create_model_handler函数中添加
if "newapi.com" in api_url:
    return NewAPIHandler(model_config)
```

## 贡献指南

欢迎贡献代码、报告问题或提出改进建议！请遵循以下步骤：

1. Fork本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建一个Pull Request

## 许可证

本项目采用MIT许可证 - 详情请参见[LICENSE](LICENSE)文件

## 致谢

- 感谢所有为本项目做出贡献的开发者
- 感谢OpenRouter、Google和DeepSeek提供的API服务
