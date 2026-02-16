#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
物流通知API客户端 - 基于文档实例
"""

import os
import urllib.parse
import ssl
import urllib3
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class LogisticsNotifyClient:
    def __init__(self):
        # 从环境变量读取配置
        self.app_code = os.getenv('LOGISTICS_APP_CODE')  # 对应文档中的appcode
        
        # 直接使用文档中的配置
        self.host = 'https://kdzsdy.market.alicloudapi.com'
        self.path = '/notify/url/save'
        self.url = self.host + self.path
    
    def _build_headers(self):
        """构建请求头 - 完全按照文档实例"""
        return {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Authorization': 'APPCODE ' + self.app_code
        }
    
    def _build_body(self, notify_url):
        """构建请求体 - 按照文档格式"""
        bodys = {
            'notifyUrl': notify_url
        }
        return urllib.parse.urlencode(bodys).encode('utf-8')
    
    def save_notify_url(self, notify_url):
        """保存通知URL - 完整复现文档实例"""
        try:
            # 创建HTTP客户端
            http = urllib3.PoolManager()
            
            # 构建请求
            headers = self._build_headers()
            body_data = self._build_body(notify_url)
            
            # 发送请求
            response = http.request('POST', self.url, body=body_data, headers=headers)
            
            # 返回结果
            content = response.data.decode('utf-8')
            return content
            
        except Exception as e:
            return f"调用失败: {str(e)}"