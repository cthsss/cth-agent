#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电商客服智能Agent - 使用独立向量数据库模块
支持通义千问和OpenAI双模型
"""

import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 导入独立的向量数据库模块
from vector_db import vector_db

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

def main():
    """主函数"""
    print("🚀 电商智能客服启动中...")
    
    # 检查API配置
    provider, api_key = check_api_configuration()
    
    if not provider:
        print("❌ 请先配置API Key")
        print("💡 请在 .env 文件中设置 DASHSCOPE_API_KEY 或 OPENAI_API_KEY")
        return
    
    print(f"✅ 使用 {provider.upper()} API 服务")
    
    try:
        # 初始化向量数据库
        print("📦 正在加载向量数据库...")
        if not vector_db.initialize():
            print("❌ 向量数据库初始化失败")
            return
        
        # 显示数据库状态
        stats = vector_db.get_stats()
        print(f"📊 向量数据库状态: {stats}")
        
        # 创建问答链
        qa_chain = create_qa_chain(provider)
        
        print("\n✅ 客服系统启动成功！")
        print("💬 开始对话（输入 'quit' 退出）:")
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
                
                # 使用RAG系统获取回答
                print("🔄 正在检索相关信息...")
                response = qa_chain.invoke(user_input)
                print(f"🤖 客服: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 程序已退出")
                break
            except Exception as e:
                print(f"❌ 处理消息时出错: {e}")
                continue
                
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("💡 请确保已安装所需依赖: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")

if __name__ == "__main__":
    main()