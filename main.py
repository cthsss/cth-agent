#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电商客服智能Agent - 使用独立向量数据库模块
支持通义千问和OpenAI双模型
纯命令行交互模式
"""

import os
import re
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 导入独立的向量数据库模块
from vector_db import vector_db
# 导入图片识别工具
from tools.image_recognition import AliyunImageRecognition

# 加载环境变量
load_dotenv()

def check_api_configuration():
    """检查API配置状态"""
    dashscope_key = os.getenv('DASHSCOPE_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if dashscope_key:
        return "qwen", dashscope_key
    elif openai_key:
        return "openai", openai_key
    else:
        return None, None

def get_chat_model(provider: str):
    """根据提供商获取聊天模型"""
    if provider == "qwen":
        try:
            from langchain_community.chat_models import ChatTongyi
            return ChatTongyi(
                dashscope_api_key=os.getenv('DASHSCOPE_API_KEY'),
                model="qwen-plus"
            )
        except ImportError:
            print("❌ 通义千问聊天模型不可用")
            return None
    else:  # openai
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
        except ImportError:
            print("❌ OpenAI聊天模型不可用")
            return None

def create_qa_chain(provider: str):
    """创建问答链"""
    print("🤖 正在构建问答系统...")
    
    # 获取聊天模型
    llm = get_chat_model(provider)
    if not llm:
        raise Exception("无法初始化聊天模型")
    
    # 获取向量数据库检索器
    retriever = vector_db.get_retriever()
    
    # 定义客服回复模板
    prompt = ChatPromptTemplate.from_template("""
你是一名专业的电商客服，需要根据以下参考信息回答用户的问题。

参考信息：
{context}

用户问题：
{question}

请根据参考信息，用专业、友好的语气回答用户问题。如果参考信息不足以完全回答问题，请诚实说明并建议联系人工客服。
""")
    
    # 创建问答链：检索 + 生成
    qa_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    print("✅ 问答系统构建完成！")
    return qa_chain

def handle_image_input(image_path: str, image_recognizer: AliyunImageRecognition):
    """处理图片输入"""
    print(f"📸 正在识别图片: {image_path}")
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"❌ 图片文件不存在: {image_path}")
        return None
    
    # 调用图片识别API
    result = image_recognizer.recognize_product(image_path)
    
    if "error" in result:
        print(f"❌ 图片识别失败: {result['error']}")
        return None
    
    # 显示识别结果
    print("✅ 图片识别完成！")
    print("🔍 识别结果:")
    for key, value in result.items():
        print(f"   {key}: {value}")
    
    return result

def initialize_system():
    """初始化系统"""
    print("🚀 电商智能客服启动中...")
    
    # 检查API配置
    provider, api_key = check_api_configuration()
    
    if not provider:
        print("❌ 请先配置API Key")
        print("💡 请在 .env 文件中设置 DASHSCOPE_API_KEY 或 OPENAI_API_KEY")
        return None, None
    
    print(f"✅ 使用 {provider.upper()} API 服务")
    
    try:
        # 初始化向量数据库
        print("📦 正在加载向量数据库...")
        if not vector_db.initialize():
            print("❌ 向量数据库初始化失败")
            return None, None
        
        # 显示数据库状态
        stats = vector_db.get_stats()
        print(f"📊 向量数据库状态: {stats}")
        
        # 初始化图片识别工具
        image_recognizer = AliyunImageRecognition()
        print("📸 图片识别工具已就绪")
        
        # 创建问答链
        qa_chain = create_qa_chain(provider)
        
        print("\n✅ 客服系统启动成功！")
        return qa_chain, image_recognizer
        
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("💡 请确保已安装所需依赖: pip install -r requirements.txt")
        return None, None
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")
        return None, None


def main():
    """主函数 - 纯命令行模式"""
    # 初始化系统
    qa_chain, image_recognizer = initialize_system()
    
    if not qa_chain or not image_recognizer:
        return
    
    print("\n💬 开始对话（输入 'quit' 退出）:")
    print("💡 支持文本对话和图片识别")
    print("💡 图片识别格式: image:图片路径")
    print("-" * 50)
    
    # 交互循环
    while True:
        try:
            user_input = input("\n👤 用户: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 感谢使用，再见！")
                break
            
            if not user_input:
                continue
            
            # 检查是否为图片识别请求
            image_pattern = r'^image:(.+)$'
            image_match = re.match(image_pattern, user_input.strip())
            
            if image_match:
                # 处理图片识别
                image_path = image_match.group(1).strip()
                recognition_result = handle_image_input(image_path, image_recognizer)
                
                if recognition_result:
                    # 将识别结果整合到对话中
                    product_info = f"用户上传了一张商品图片，识别结果：{recognition_result}"
                    print("🔄 正在基于图片信息为您提供相关服务...")
                    response = qa_chain.invoke(product_info)
                    print(f"🤖 客服: {response}")
            else:
                # 处理普通文本对话
                print("🔄 正在检索相关信息...")
                response = qa_chain.invoke(user_input)
                print(f"🤖 客服: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 程序已退出")
            break
        except Exception as e:
            print(f"❌ 处理消息时出错: {e}")
            continue

if __name__ == "__main__":
    main()