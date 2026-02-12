#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目配置文件 - 精简版
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """精简配置类"""
    
    # API配置
    DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # 内存配置
    MEMORY_MAX_HISTORY = 8
    MEMORY_SUMMARY_THRESHOLD = 4

# 导出配置实例
config = Config()