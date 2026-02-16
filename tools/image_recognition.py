#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云图片识别工具模块
最简化的外部API调用版本，确保能用
"""

import json
import base64
import os
import ssl
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from typing import Dict, Any

# 创建未验证的SSL上下文
context = ssl._create_unverified_context()

class AliyunImageRecognition:
    """阿里云图片识别工具类"""
    
    def __init__(self):
        # 直接使用您确认的APP_CODE
        self.app_code = "35754e14c9ff4395951840e9b92f41ea"
        self.request_url = "https://gjbsb.market.alicloudapi.com/ocrservice/advanced"
        
    def get_img(self, img_file):
        """将本地图片转成base64编码的字符串"""
        if img_file.startswith("http"):
            return img_file
        else:
            with open(os.path.expanduser(img_file), 'rb') as f:
                data = f.read()
        try:
            encodestr = str(base64.b64encode(data), 'utf-8')
        except TypeError:
            encodestr = base64.b64encode(data).decode('utf-8')
        return encodestr

    def posturl(self, headers, body):
        """发送请求，获取识别结果"""
        try:
            params = json.dumps(body).encode(encoding='UTF8')
            req = Request(self.request_url, params, headers)
            r = urlopen(req, context=context)
            html = r.read()
            return html.decode("utf8")
        except HTTPError as e:
            return f"HTTP Error {e.code}: {e.read().decode('utf8')}"

    def recognize_product(self, image_path: str) -> Dict[str, Any]:
        """
        识别商品图片 - 真正的外部API调用
        """
        try:
            # 请求参数（简化版）
            params = {
                "prob": False,
                "charInfo": False,
                "rotate": False,
                "table": False,
                "sortPage": False,
                "noStamp": False,
                "figure": False,
                "row": False,
                "paragraph": False,
                "oricoord": True
            }

            # 获取图片数据
            img = self.get_img(image_path)
            if img.startswith('http'):
                params.update({'url': img})
            else:
                params.update({'img': img})

            # 请求头
            headers = {
                'Authorization': 'APPCODE %s' % self.app_code,
                'Content-Type': 'application/json; charset=UTF-8'
            }

            # 发送请求
            response = self.posturl(headers, params)
            
            # 返回原始响应
            return {
                "raw_response": response,
                "status": "api_called",
                "file_path": image_path
            }
                
        except Exception as e:
            return {"error": f"识别出错: {str(e)}"}

# 测试函数
if __name__ == "__main__":
    recognizer = AliyunImageRecognition()
    result = recognizer.recognize_product(r"C:\Users\LEGION\Pictures\香蕉1.png")
    print("API调用结果:", result)