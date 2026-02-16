#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云OCR MCP工具实现
基于现有的阿里云OCR API配置
"""

import os
import json
import base64
import urllib.request
import ssl
from typing import Dict, Any
from tools.mcp_base import MCPTool

class AliyunOCRMCPTool(MCPTool):
    """阿里云OCR MCP工具"""
    
    def __init__(self):
        super().__init__(
            name="aliyun_ocr",
            description="阿里云高级OCR文字识别服务"
        )
        self.required_env_vars = [
            "ALIYUN_IMAGE_APP_CODE"
        ]
        self.api_url = "https://gjbsb.market.alicloudapi.com/ocrservice/advanced"
    
    def initialize(self) -> bool:
        """初始化OCR工具"""
        if not self.check_permissions():
            return False
        
        # 测试API连接
        try:
            app_code = os.getenv("ALIYUN_IMAGE_APP_CODE")
            context = ssl._create_unverified_context()
            request = urllib.request.Request(self.api_url)
            request.add_header("Authorization", f"APPCODE {app_code}")
            request.add_header("Content-Type", "application/json; charset=UTF-8")
            
            try:
                response = urllib.request.urlopen(request, context=context, timeout=5)
                print("✅ 阿里云OCR API连接测试成功")
                return True
            except urllib.error.HTTPError as e:
                if e.code == 400:
                    print("✅ 阿里云OCR API连接测试成功（参数验证）")
                    return True
                else:
                    print(f"❌ 阿里云OCR API连接失败: HTTP {e.code}")
                    return False
            except Exception as e:
                print(f"❌ 阿里云OCR API连接测试失败: {e}")
                return False
                
        except Exception as e:
            print(f"❌ OCR工具初始化失败: {e}")
            return False
    
    def execute(self, image_path: str) -> Dict[str, Any]:
        """执行OCR识别"""
        if not os.path.exists(image_path):
            return {"error": f"图片文件不存在: {image_path}", "success": False}
        
        try:
            # 使用现有的image_recognition模块
            from tools.image_recognition import AliyunImageRecognition
            recognizer = AliyunImageRecognition()
            
            result = recognizer.recognize_product(image_path)
            
            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"]
                }
            elif "raw_response" in result:
                try:
                    response_data = json.loads(result["raw_response"])
                    if response_data.get("success"):
                        ocr_text = self._extract_text_from_response(response_data)
                        return {
                            "success": True,
                            "recognized_text": ocr_text,
                            "raw_response": response_data
                        }
                    else:
                        return {
                            "success": False,
                            "error": response_data.get("message", "OCR识别失败"),
                            "raw_response": response_data
                        }
                except json.JSONDecodeError:
                    return {
                        "success": True,
                        "recognized_text": str(result["raw_response"]),
                        "raw_response": result["raw_response"]
                    }
            else:
                return {
                    "success": False,
                    "error": "未知的响应格式"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"OCR识别过程中出错: {str(e)}"
            }
    
    def _extract_text_from_response(self, response_data: dict) -> str:
        """从OCR响应中提取文本内容"""
        ocr_text = ""
        try:
            if 'data' in response_data and 'blocks' in response_data['data']:
                for block in response_data['data']['blocks']:
                    if 'lines' in block:
                        for line in block['lines']:
                            if 'words' in line:
                                for word in line['words']:
                                    ocr_text += word.get('word', '') + ' '
        except Exception:
            pass
        
        return ocr_text.strip() if ocr_text else "未识别到文本内容"

# 注册工具
from tools.mcp_base import mcp_manager
ocr_tool = AliyunOCRMCPTool()
mcp_manager.register_tool(ocr_tool)