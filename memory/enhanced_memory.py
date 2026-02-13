#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版内存管理模块
支持智能上下文理解、重要信息提取和对话摘要
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class MessageType(Enum):
    """消息类型枚举"""
    USER_QUERY = "user_query"
    PRODUCT_INQUIRY = "product_inquiry"
    ORDER_QUESTION = "order_question"
    AFTER_SALES = "after_sales"
    GENERAL_CHAT = "general_chat"

@dataclass
class DialogTurn:
    """对话轮次数据类"""
    user_input: str
    ai_response: str
    timestamp: str
    message_type: MessageType
    key_entities: List[str]  # 关键实体（商品名、订单号等）
    intent: str  # 用户意图

class EnhancedMemory:
    """增强版内存管理器"""
    
    def __init__(self, max_history: int = 10, summary_threshold: int = 6):
        """
        初始化增强内存管理器
        
        Args:
            max_history: 最大历史记录数
            summary_threshold: 触发摘要的对话轮次数
        """
        self.max_history = max_history
        self.summary_threshold = summary_threshold
        self.dialog_history: List[DialogTurn] = []
        self.conversation_summary: str = ""
        self.current_context: Dict[str, Any] = {}
        
        # 电商领域关键词库
        self.ecommerce_keywords = {
            "product_related": ["商品", "产品", "衣服", "鞋子", "电子产品", "价格", "规格", "尺码"],
            "order_related": ["订单", "购买", "下单", "付款", "支付", "账单"],
            "logistics_related": ["发货", "快递", "物流", "配送", "运输", "到货"],
            "after_sales": ["退货", "换货", "退款", "售后", "保修", "质量问题"]
        }
    
    def add_dialog_turn(self, user_input: str, ai_response: str, 
                       message_type: MessageType = MessageType.GENERAL_CHAT,
                       key_entities: List[str] = None):
        """
        添加对话轮次
        
        Args:
            user_input: 用户输入
            ai_response: AI回复
            message_type: 消息类型
            key_entities: 关键实体列表
        """
        turn = DialogTurn(
            user_input=user_input,
            ai_response=ai_response,
            timestamp=datetime.now().isoformat(),
            message_type=message_type,
            key_entities=key_entities or [],
            intent=self._analyze_intent(user_input)
        )
        
        self.dialog_history.append(turn)
        
        # 更新当前上下文
        self._update_context(turn)
        
        # 控制历史长度
        if len(self.dialog_history) > self.max_history:
            self.dialog_history.pop(0)
        
        # 检查是否需要生成摘要
        if len(self.dialog_history) >= self.summary_threshold:
            self._generate_summary()
    
    def _analyze_intent(self, user_input: str) -> str:
        """分析用户意图"""
        user_input_lower = user_input.lower()
        
        # 检查各类关键词
        if any(keyword in user_input_lower for keyword in self.ecommerce_keywords["product_related"]):
            return "product_inquiry"
        elif any(keyword in user_input_lower for keyword in self.ecommerce_keywords["order_related"]):
            return "order_question"
        elif any(keyword in user_input_lower for keyword in self.ecommerce_keywords["logistics_related"]):
            return "logistics_query"
        elif any(keyword in user_input_lower for keyword in self.ecommerce_keywords["after_sales"]):
            return "after_sales"
        else:
            return "general_inquiry"
    
    def _update_context(self, turn: DialogTurn):
        """更新对话上下文"""
        # 提取和更新关键信息
        if turn.message_type == MessageType.PRODUCT_INQUIRY:
            # 提取商品相关信息
            product_info = self._extract_product_info(turn.user_input)
            if product_info:
                self.current_context["current_product"] = product_info
                
        elif turn.message_type == MessageType.ORDER_QUESTION:
            # 提取订单相关信息
            order_info = self._extract_order_info(turn.user_input)
            if order_info:
                self.current_context["current_order"] = order_info
    
    def _extract_product_info(self, text: str) -> Optional[Dict[str, str]]:
        """提取商品信息"""
        # 简单的关键词匹配，实际应用中可以用NER模型
        product_keywords = ["衣服", "鞋子", "手机", "电脑", "化妆品"]
        for keyword in product_keywords:
            if keyword in text:
                return {"product_type": keyword, "query": text}
        return None
    
    def _extract_order_info(self, text: str) -> Optional[Dict[str, str]]:
        """提取订单信息"""
        # 简单的订单号匹配
        import re
        order_pattern = r'[A-Z0-9]{10,}'  # 订单号通常包含字母数字组合
        match = re.search(order_pattern, text)
        if match:
            return {"order_id": match.group(), "query": text}
        return None
    
    def _generate_summary(self):
        """生成对话摘要"""
        if len(self.dialog_history) < 2:
            return
        
        # 简单的摘要策略：保留最近几轮和关键信息
        recent_turns = self.dialog_history[-3:]  # 最近3轮
        key_topics = self._extract_key_topics()
        
        summary_parts = []
        summary_parts.append("对话摘要：")
        
        # 添加关键主题
        if key_topics:
            summary_parts.append(f"主要话题：{', '.join(key_topics)}")
        
        # 添加最近对话要点
        summary_parts.append("近期讨论：")
        for i, turn in enumerate(recent_turns, 1):
            summary_parts.append(f"{i}. 用户询问{turn.intent}相关问题")
        
        self.conversation_summary = "\n".join(summary_parts)
    
    def _extract_key_topics(self) -> List[str]:
        """提取关键话题"""
        topics = set()
        for turn in self.dialog_history:
            if turn.message_type != MessageType.GENERAL_CHAT:
                topics.add(turn.message_type.value.replace("_", " "))
        return list(topics)
    
    def get_context_for_prompt(self) -> str:
        """获取用于Prompt的上下文信息"""
        context_parts = []
        
        # 添加对话摘要
        if self.conversation_summary:
            context_parts.append(self.conversation_summary)
        
        # 添加当前上下文
        if self.current_context:
            context_parts.append("当前上下文信息：")
            for key, value in self.current_context.items():
                context_parts.append(f"- {key}: {value}")
        
        # 添加最近几轮对话（如果摘要不存在）
        if not self.conversation_summary and self.dialog_history:
            recent_history = self.dialog_history[-2:]  # 最近2轮
            context_parts.append("最近对话：")
            for turn in recent_history:
                context_parts.append(f"用户: {turn.user_input}")
                context_parts.append(f"客服: {turn.ai_response}")
        
        return "\n".join(context_parts) if context_parts else "无历史对话记录"
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取内存统计信息"""
        return {
            "total_turns": len(self.dialog_history),
            "current_summary": self.conversation_summary[:100] + "..." if self.conversation_summary else "无",
            "context_keys": list(self.current_context.keys()),
            "message_types": [turn.message_type.value for turn in self.dialog_history[-5:]]
        }
    
    def clear_memory(self):
        """清空所有内存"""
        self.dialog_history.clear()
        self.conversation_summary = ""
        self.current_context.clear()
    
    def export_memory(self) -> str:
        """导出内存状态为JSON字符串"""
        memory_data = {
            "dialog_history": [
                {
                    "user_input": turn.user_input,
                    "ai_response": turn.ai_response,
                    "timestamp": turn.timestamp,
                    "message_type": turn.message_type.value,
                    "key_entities": turn.key_entities,
                    "intent": turn.intent
                }
                for turn in self.dialog_history
            ],
            "conversation_summary": self.conversation_summary,
            "current_context": self.current_context
        }
        return json.dumps(memory_data, ensure_ascii=False, indent=2)
    
    def auto_save_to_file(self, filepath: str = None) -> bool:
        """
        自动保存记忆到JSON文件
        
        Args:
            filepath: 保存路径，如果为None则使用默认路径
            
        Returns:
            bool: 保存是否成功
        """
        try:
            if filepath is None:
                # 默认保存到项目根目录的backup文件夹
                import os
                backup_dir = os.path.join(os.getcwd(), 'backup')
                os.makedirs(backup_dir, exist_ok=True)
                filepath = os.path.join(backup_dir, 'memory_backup.json')
            
            # 导出并保存
            json_data = self.export_memory()
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_data)
            
            print(f"✅ 记忆已保存到: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ 保存记忆失败: {e}")
            return False
