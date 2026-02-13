#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云图片识别工具模块
"""

import base64
import requests
import json
import os
from typing import Dict, Any, Optional

class AliyunImageRecognition:
    """阿里云图片识别工具类"""
    
    def __init__(self):
        self.access_key = os.getenv('ALIYUN_IMAGE_API_KEY')
        self.access_secret = os.getenv('ALIYUN_IMAGE_API_SECRET')
        self.app_code = os.getenv('ALIYUN_IMAGE_APP_CODE')
        self.endpoint = "https://imagerecog.cn-shanghai.aliyuncs.com"  # 根据实际API调整
        
    def recognize_product(self, image_path: str) -> Dict[str, Any]:
        """
        识别商品图片
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            识别结果字典
        """
        try:
            # 读取并编码图片
            with open(image_path, 'rb') as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 构建请求
            payload = {
                "Action": "RecognizeProduct",
                "Image": encoded_image,
                "RegionId": "cn-shanghai"
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"APPCODE {self.app_code}"
            }
            
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_product_result(result)
            else:
                return {"error": f"API调用失败: {response.status_code}, {response.text}"}
                
        except FileNotFoundError:
            return {"error": "图片文件不存在"}
        except Exception as e:
            return {"error": f"识别出错: {str(e)}"}
    
    def _parse_product_result(self, api_response: Dict) -> Dict[str, Any]:
        """解析商品识别结果"""
        try:
            products = api_response.get("Products", [])
            if not products:
                return {"message": "未识别到商品信息"}
            
            # 提取主要商品信息
            main_product = products[0]
            return {
                "product_name": main_product.get("Name", "未知商品"),
                "category": main_product.get("Category", "未知分类"),
                "confidence": main_product.get("Confidence", 0),
                "price_range": main_product.get("PriceRange", "价格待确认"),
                "similar_products": len(products) - 1
            }
        except Exception as e:
            return {"error": f"结果解析失败: {str(e)}"}

# 使用示例
if __name__ == "__main__":
    recognizer = AliyunImageRecognition()
    
    # 测试图片识别
    test_image = "path/to/your/test/image.jpg"
    result = recognizer.recognize_product(test_image)
    print("识别结果:", json.dumps(result, ensure_ascii=False, indent=2))