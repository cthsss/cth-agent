#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电商客服智能Agent - 使用独立向量数据库模块
支持通义千问和OpenAI双模型
纯命令行交互模式
集成MCP工具管理器
"""

import os
import re
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 导入独立的向量数据库模块
from vector_db import vector_db
# 导入MCP工具管理器和工具（所有API调用都通过MCP管理器）
from tools.mcp_base import mcp_manager
from tools.mcp_ocr_tool import AliyunOCRMCPTool
from tools.mcp_logistics_tool import LogisticsMCPTool

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

# 已移除handle_image_input函数，所有图片识别都通过MCP工具管理器处理

def handle_mcp_tool_command(command: str):
    """处理MCP工具命令"""
    # 解析命令格式: tool:工具名:参数
    parts = command.split(':', 2)
    if len(parts) < 2:
        print("❌ MCP工具命令格式错误")
        print("💡 正确格式: tool:工具名:参数")
        print("💡 可用工具: aliyun_ocr, logistics_tracker")
        return None
    
    tool_name = parts[1].strip()
    tool_params = parts[2].strip() if len(parts) > 2 else ""
    
    # 检查工具是否可用
    if tool_name not in mcp_manager.get_available_tools():
        print(f"❌ 未找到工具: {tool_name}")
        print(f"💡 可用工具: {', '.join(mcp_manager.get_available_tools())}")
        return None
    
    # 启用工具（如果还未启用）
    if tool_name not in mcp_manager.get_enabled_tools():
        if not mcp_manager.enable_tool(tool_name):
            print(f"❌ 工具 {tool_name} 启用失败")
            return None
    
    # 执行工具
    print(f"🔧 正在执行工具: {tool_name}")
    try:
        if tool_name == "aliyun_ocr":
            result = mcp_manager.execute_tool(tool_name, image_path=tool_params)
        elif tool_name == "logistics_tracker":
            result = mcp_manager.execute_tool(tool_name, tracking_number=tool_params)
        else:
            result = mcp_manager.execute_tool(tool_name, param=tool_params)
        
        if result and result.get("success"):
            print("✅ 工具执行成功:")
            for key, value in result.items():
                if key != "success":
                    print(f"   {key}: {value}")
            return result
        else:
            error_msg = result.get("error", "未知错误") if result else "工具返回空结果"
            print(f"❌ 工具执行失败: {error_msg}")
            return None
            
    except Exception as e:
        print(f"❌ 工具执行出错: {e}")
        return None

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
        
        # 初始化MCP工具管理器
        print("🔧 正在初始化MCP工具管理器...")
        
        # 注册所有工具
        ocr_tool = AliyunOCRMCPTool()
        logistics_tool = LogisticsMCPTool()
        
        mcp_manager.register_tool(ocr_tool)
        mcp_manager.register_tool(logistics_tool)
        
        # 尝试启用工具
        ocr_enabled = mcp_manager.enable_tool("aliyun_ocr")
        logistics_enabled = mcp_manager.enable_tool("logistics_tracker")
        
        if ocr_enabled:
            print("✅ MCP OCR工具已启用")
        else:
            print("⚠️  MCP OCR工具启用失败")
            
        if logistics_enabled:
            print("✅ MCP物流工具已启用")
        else:
            print("⚠️  MCP物流工具启用失败")
        
        # 创建问答链
        qa_chain = create_qa_chain(provider)
        
        print("\n✅ 客服系统启动成功！")
        print("💡 系统已完全基于MCP架构运行")
        print("💡 支持的MCP工具命令:")
        print("   - tool:aliyun_ocr:图片路径")
        print("   - tool:logistics_tracker:快递单号")
        return qa_chain, mcp_manager
        
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
    init_result = initialize_system()
    
    if not init_result or len(init_result) < 2:
        return
    
    qa_chain, mcp_manager_instance = init_result
    
    if not qa_chain:
        return
    
    print("\n💬 开始对话（输入 'quit' 退出）:")
    print("💡 所有功能均已通过MCP工具管理器提供")
    print("💡 图片识别: tool:aliyun_ocr:图片路径")
    print("💡 物流查询: tool:logistics_tracker:单号")
    print("💡 传统命令也支持: image:图片路径")
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
            
            # 统一通过MCP工具处理所有命令
            if user_input.startswith("tool:"):
                handle_mcp_tool_command(user_input)
                continue
            
            # 传统的图片识别命令也转为MCP调用
            image_pattern = r'^image:(.+)$'
            image_match = re.match(image_pattern, user_input.strip())
            
            if image_match:
                image_path = image_match.group(1).strip()
                print("🔄 正在通过MCP工具处理图片识别...")
                # 转换为MCP命令格式
                mcp_command = f"tool:aliyun_ocr:{image_path}"
                result = handle_mcp_tool_command(mcp_command)
                
                if result and result.get("success"):
                    # 将识别结果整合到对话中
                    recognized_text = result.get('recognized_text', '识别完成')
                    product_info = f"用户上传了一张商品图片，识别结果：{recognized_text}"
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