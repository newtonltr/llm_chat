#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型处理器模块
包含与不同LLM API交互的处理器类
"""

import requests
from abc import ABC, abstractmethod

class ModelHandler(ABC):
    """模型处理器基类"""

    def __init__(self, model_config):
        self.name = model_config["name"]
        self.api_key = model_config["api_key"]
        self.api_url = model_config["api_url"]
        self.model_name = model_config["model_name"]

    @abstractmethod
    def send_message(self, message):
        """发送消息到模型并返回回复"""
        pass

class OpenRouterHandler(ModelHandler):
    """OpenRouter API处理器"""

    def send_message(self, message, history=None):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 如果提供了历史记录，使用历史记录构建消息列表
        if history and isinstance(history, list) and len(history) > 0:
            messages = history.copy()
            # 添加当前用户消息
            messages.append({"role": "user", "content": message})
        else:
            # 如果没有历史记录，只发送当前消息
            messages = [{"role": "user", "content": message}]

        data = {
            "model": self.model_name,
            "messages": messages
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"错误: {str(e)}"

class GeminiHandler(ModelHandler):
    """Google Gemini API处理器"""

    def send_message(self, message, history=None):
        # 构建正确的URL格式
        # 如果api_url中已经包含了模型名称和:generateContent，则直接使用
        # 否则，构建正确的URL
        if ":generateContent" in self.api_url:
            url = f"{self.api_url}?key={self.api_key}"
        else:
            # 标准URL格式：https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent
            base_url = "https://generativelanguage.googleapis.com/v1beta/models"
            url = f"{base_url}/{self.model_name}:generateContent?key={self.api_key}"

        # 如果提供了历史记录，构建多轮对话内容
        if history and isinstance(history, list) and len(history) > 0:
            contents = []

            # 将历史记录转换为Gemini格式
            for entry in history:
                role = entry.get("role", "")
                content = entry.get("content", "")

                # 在Gemini API中，用户是"user"，助手是"model"
                gemini_role = "user" if role == "user" else "model"

                contents.append({
                    "role": gemini_role,
                    "parts": [{"text": content}]
                })

            # 添加当前用户消息
            contents.append({
                "role": "user",
                "parts": [{"text": message}]
            })

            data = {
                "contents": contents
            }
        else:
            # 如果没有历史记录，只发送当前消息
            data = {
                "contents": [
                    {
                        "parts": [
                            {"text": message}
                        ]
                    }
                ]
            }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"错误: {str(e)}"

class DeepSeekHandler(ModelHandler):
    """DeepSeek API处理器"""

    def send_message(self, message, history=None):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 如果提供了历史记录，使用历史记录构建消息列表
        if history and isinstance(history, list) and len(history) > 0:
            messages = history.copy()
            # 添加当前用户消息
            messages.append({"role": "user", "content": message})
        else:
            # 如果没有历史记录，只发送当前消息
            messages = [{"role": "user", "content": message}]

        data = {
            "model": self.model_name,
            "messages": messages
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"错误: {str(e)}"

def create_model_handler(model_config):
    """创建适当的模型处理器"""
    api_url = model_config["api_url"].lower()

    if "openrouter.ai" in api_url:
        return OpenRouterHandler(model_config)
    elif "googleapis.com" in api_url:
        return GeminiHandler(model_config)
    elif "deepseek.com" in api_url:
        return DeepSeekHandler(model_config)
    else:
        raise ValueError(f"不支持的API URL: {api_url}")
