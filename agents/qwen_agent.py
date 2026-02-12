#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通义千问电商客服Agent（集成增强内存管理）
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from memory.enhanced_memory import EnhancedMemory, MessageType

# 加载环境变量
load_dotenv()

class QwenEcommerceAgent:
    """通义千问电商客服Agent（增强版）"""
    
    def __init__(self, agent_name: str = "电商智能客服"):
        self.agent_name = agent_name
        self.memory = EnhancedMemory(max_history=8, summary_threshold=4)  # 增强内存配置
        
        # 初始化通义千问
        try:
            import dashscope
            self.dashscope = dashscope
            self.api_key = os.getenv('DASHSCOPE_API_KEY')
            
            if not self.api_key:
                # 如果没有专门的千问key，使用OpenAI key作为备选
                self.api_key = os.getenv('OPENAI_API_KEY')
                if not self.api_key:
                    raise ValueError("请设置DASHSCOPE_API_KEY或OPENAI_API_KEY环境变量")
            
            self.dashscope.api_key = self.api_key
            print(f"✅ {self.agent_name} 通义千问初始化完成")
            
        except ImportError:
            raise ImportError("请安装dashscope: pip install dashscope")
        
        # 电商专业知识库
        self.knowledge_base = {
            "主营品类": [
                "时尚服装（男装、女装、童装）",
                "数码电子（手机、电脑、配件）", 
                "家居生活（家具、装饰、日用）",
                "美妆个护（护肤品、彩妆、个人护理）",
                "食品饮料（零食、饮品、保健品）"
            ],
            "售后服务": [
                "7天无理由退换货服务",
                "质量问题30天包退换",
                "破损补寄服务",
                "客服24小时在线支持",
                "售后无忧保障计划"
            ],
            "物流配送": [
                "全国快递配送服务",
                "江浙沪地区包邮",
                "偏远地区需补运费15-30元",
                "默认使用圆通/中通快递",
                "支持指定快递公司（需额外付费）",
                "发货时间：下单后1-2个工作日内发货"
            ],
            "支付方式": [
                "微信支付",
                "支付宝支付", 
                "银行卡支付",
                "花呗分期付款",
                "信用卡支付"
            ]
        }
    
    def _classify_message_type(self, user_input: str) -> MessageType:
        """分类用户消息类型"""
        text_lower = user_input.lower()
        
        # 商品咨询相关
        product_keywords = ["商品", "产品", "衣服", "鞋子", "价格", "多少钱", "规格", "型号"]
        if any(keyword in text_lower for keyword in product_keywords):
            return MessageType.PRODUCT_INQUIRY
        
        # 订单相关
        order_keywords = ["订单", "下单", "购买", "付款", "支付", "账单"]
        if any(keyword in text_lower for keyword in order_keywords):
            return MessageType.ORDER_QUESTION
        
        # 售后相关
        after_sales_keywords = ["退货", "换货", "退款", "售后", "保修", "质量问题"]
        if any(keyword in text_lower for keyword in after_sales_keywords):
            return MessageType.AFTER_SALES
        
        # 物流相关
        logistics_keywords = ["发货", "快递", "物流", "配送", "运输", "到货", "什么时候到"]
        if any(keyword in text_lower for keyword in logistics_keywords):
            return MessageType.LOGISTICS_QUERY
        
        return MessageType.GENERAL_CHAT
    
    def _extract_key_entities(self, user_input: str) -> List[str]:
        """提取关键实体"""
        entities = []
        
        # 简单的实体提取（实际应用中可用NER模型）
        import re
        
        # 提取可能的订单号
        order_pattern = r'[A-Z0-9]{8,}'
        order_matches = re.findall(order_pattern, user_input)
        entities.extend([f"订单号:{match}" for match in order_matches])
        
        # 提取商品关键词
        product_keywords = ["T恤", "裤子", "鞋子", "手机", "电脑", "化妆品"]
        for keyword in product_keywords:
            if keyword in user_input:
                entities.append(f"商品:{keyword}")
        
        # 提取颜色、尺码等属性
        size_patterns = [r"[XSMLXL\d]+码", r"(\d+)寸", r"(红色|蓝色|黑色|白色)"]
        for pattern in size_patterns:
            matches = re.findall(pattern, user_input)
            entities.extend(matches)
        
        return entities
    
    def _build_qwen_prompt(self, user_input: str) -> str:
        """构建增强版千问提示词"""
        
        # 获取上下文信息
        context_info = self.memory.get_context_for_prompt()
        
        # 系统角色设定
        system_role = f"""你是一个专业的电商客服专家，名叫{self.agent_name}。
你的职责是为顾客提供专业、友好、及时的购物咨询服务。

## 你的专业知识包括：
【商品品类】
{chr(10).join([f'- {item}' for item in self.knowledge_base['主营品类']])}

【售后服务】
{chr(10).join([f'- {item}' for item in self.knowledge_base['售后服务']])}

【物流配送】
{chr(10).join([f'- {item}' for item in self.knowledge_base['物流配送']])}

【支付方式】
{chr(10).join([f'- {item}' for item in self.knowledge_base['支付方式']])}

## 回复原则：
1. 语气亲切专业，使用礼貌用语
2. 回答要具体准确，避免模糊表述
3. 主动询问用户需求，提供个性化建议
4. 遇到复杂问题时，引导用户联系人工客服
5. 适当使用表情符号增加亲和力😊

## 对话上下文：
{context_info}

## 用户最新问题：
{user_input}

请根据以上信息，给出专业且友好的回复："""
        
        return system_role
    
    def process_message(self, user_input: str) -> str:
        """
        处理用户消息（增强版）
        
        Args:
            user_input: 用户输入
            
        Returns:
            AI客服回复
        """
        try:
            # 分析消息类型和提取实体
            message_type = self._classify_message_type(user_input)
            key_entities = self._extract_key_entities(user_input)
            
            # 构建提示词
            prompt = self._build_qwen_prompt(user_input)
            
            # 调用通义千问API
            response = self.dashscope.Generation.call(
                model='qwen-plus',
                prompt=prompt,
                max_tokens=800,
                temperature=0.7,
                top_p=0.8
            )
            
            # 提取回复内容
            if response.status_code == 200:
                ai_reply = response.output.text.strip()
            else:
                ai_reply = f"抱歉，系统暂时无法响应您的问题。错误代码：{response.status_code}"
            
            # 保存对话记录到增强内存
            self.memory.add_dialog_turn(
                user_input=user_input,
                ai_response=ai_reply,
                message_type=message_type,
                key_entities=key_entities
            )
            
            # 日志输出
            print(f"📥 用户: {user_input}")
            print(f"📤 {self.agent_name}: {ai_reply}")
            print(f"🏷️  消息类型: {message_type.value}")
            if key_entities:
                print(f"🔑 关键实体: {', '.join(key_entities)}")
            print("-" * 50)
            
            return ai_reply
            
        except Exception as e:
            error_msg = f"处理消息时发生错误: {str(e)}"
            print(f"❌ 错误: {error_msg}")
            return "非常抱歉，我现在遇到了一些技术问题，请您稍后再试，或者联系人工客服为您服务。😊"
    
    def get_agent_status(self) -> Dict[str, Any]:
        """获取Agent详细状态"""
        memory_stats = self.memory.get_memory_stats()
        return {
            "agent_name": self.agent_name,
            "model": "qwen-plus",
            "memory_stats": memory_stats,
            "knowledge_areas": list(self.knowledge_base.keys())
        }
    
    def clear_session(self):
        """清空当前会话"""
        self.memory.clear_memory()
        print(f"🗑️ {self.agent_name} 会话已清空")

