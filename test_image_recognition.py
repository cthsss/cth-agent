#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片识别功能测试脚本
"""

import os
from tools.image_recognition import AliyunImageRecognition

def test_image_recognition():
    """测试图片识别功能"""
    print("🔍 图片识别功能测试")
    print("=" * 40)
    
    # 初始化识别器
    recognizer = AliyunImageRecognition()
    
    # 检查配置
    print("🔧 配置检查:")
    print(f"   API Key: {'✓' if recognizer.access_key else '✗'}")
    print(f"   Secret: {'✓' if recognizer.access_secret else '✗'}")
    print(f"   App Code: {'✓' if recognizer.app_code else '✗'}")
    
    if not all([recognizer.access_key, recognizer.access_secret, recognizer.app_code]):
        print("❌ 配置不完整，请检查.env文件")
        return
    
    # 测试图片路径（这里可以替换为实际的测试图片路径）
    test_images = [
        "test_image.jpg",  # 你可以准备一些测试图片
        "sample_product.jpg"
    ]
    
    print("\n📝 测试说明:")
    print("请准备测试图片文件，然后在终端中使用以下格式:")
    print("image:图片路径")
    print("\n例如:")
    print("image:test_image.jpg")
    print("image:C:\\Users\\YourName\\Pictures\\product.jpg")

if __name__ == "__main__":
    test_image_recognition()