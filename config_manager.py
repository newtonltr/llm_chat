#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理模块
处理配置文件的加载和保存
"""

import json
import os
from tkinter import messagebox

class ConfigManager:
    """配置管理类"""
    
    def __init__(self):
        self.config = {"models": []}
        self.prompts = {"prompts": []}
        
    def load_config(self):
        """加载模型配置文件"""
        try:
            with open("llm_config.json", "r", encoding="utf-8") as f:
                self.config = json.load(f)
            return self.config
        except Exception as e:
            messagebox.showerror("错误", f"加载配置文件时出错: {str(e)}")
            self.config = {"models": []}
            return self.config
            
    def save_config(self):
        """保存模型配置文件"""
        try:
            with open("llm_config.json", "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("成功", "配置已保存")
            return True
        except Exception as e:
            messagebox.showerror("错误", f"保存配置文件时出错: {str(e)}")
            return False
            
    def load_prompts(self):
        """加载提示词文件"""
        try:
            with open("prompts.json", "r", encoding="utf-8") as f:
                self.prompts = json.load(f)
            return self.prompts
        except FileNotFoundError:
            # 如果文件不存在，创建默认提示词
            self.prompts = {
                "prompts": [
                    {
                        "name": "简单问候",
                        "content": "你好，请简单介绍一下你自己。"
                    }
                ]
            }
            self.save_prompts()
            return self.prompts
        except Exception as e:
            messagebox.showerror("错误", f"加载提示词文件时出错: {str(e)}")
            self.prompts = {"prompts": []}
            return self.prompts
            
    def save_prompts(self):
        """保存提示词文件"""
        try:
            with open("prompts.json", "w", encoding="utf-8") as f:
                json.dump(self.prompts, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("错误", f"保存提示词文件时出错: {str(e)}")
            return False
            
    def get_model_by_name(self, model_name):
        """根据名称获取模型配置"""
        for model in self.config["models"]:
            if model["name"] == model_name:
                return model
        return None
        
    def add_model(self, model_data):
        """添加新模型"""
        self.config["models"].append(model_data)
        
    def update_model(self, original_name, model_data):
        """更新现有模型"""
        for i, model in enumerate(self.config["models"]):
            if model["name"] == original_name:
                self.config["models"][i] = model_data
                return True
        return False
        
    def delete_model(self, model_name):
        """删除模型"""
        for i, model in enumerate(self.config["models"]):
            if model["name"] == model_name:
                del self.config["models"][i]
                return True
        return False
        
    def get_prompt_by_name(self, prompt_name):
        """根据名称获取提示词"""
        for prompt in self.prompts["prompts"]:
            if prompt["name"] == prompt_name:
                return prompt
        return None
        
    def add_prompt(self, prompt_data):
        """添加新提示词"""
        self.prompts["prompts"].append(prompt_data)
        
    def update_prompt(self, index, prompt_data):
        """更新提示词"""
        if 0 <= index < len(self.prompts["prompts"]):
            self.prompts["prompts"][index] = prompt_data
            return True
        return False
        
    def delete_prompt(self, prompt_name):
        """删除提示词"""
        for i, prompt in enumerate(self.prompts["prompts"]):
            if prompt["name"] == prompt_name:
                del self.prompts["prompts"][i]
                return True
        return False
