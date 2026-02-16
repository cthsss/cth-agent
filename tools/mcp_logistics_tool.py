#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
物流查询MCP工具
基于示例数据的物流查询实现
"""

import time
from typing import Dict, Any
from tools.mcp_base import MCPTool

class LogisticsMCPTool(MCPTool):
    """物流查询MCP工具"""
    
    def __init__(self):
        super().__init__(
            name="logistics_tracker",
            description="物流信息查询工具"
        )
        self.required_env_vars = ["LOGISTICS_APP_CODE"]
        self.sample_data = {
            "SF123456789CN": {
                "status": "运输中",
                "location": "上海市转运中心",
                "time": "2024-01-15 14:30:00",
                "progress": "已到达上海转运中心，准备发往下一站"
            },
            "YT987654321CN": {
                "status": "已签收",
                "location": "北京市朝阳区",
                "time": "2024-01-14 16:45:00",
                "progress": "快件已被本人签收"
            }
        }
    
    def initialize(self) -> bool:
        """初始化物流工具"""
        print("ℹ️  物流查询工具初始化")
        # 检查环境变量
        if not self.check_permissions():
            print("⚠️  缺少物流API配置，将使用示例数据模式")
        
        print("✅ 物流工具初始化完成")
        return True
    
    def execute(self, tracking_number: str) -> Dict[str, Any]:
        """执行物流查询"""
        # 模拟API调用延迟
        time.sleep(1)
        
        # 检查是否为示例单号
        if tracking_number in self.sample_data:
            return {
                "success": True,
                "tracking_number": tracking_number,
                "status": self.sample_data[tracking_number]["status"],
                "current_location": self.sample_data[tracking_number]["location"],
                "update_time": self.sample_data[tracking_number]["time"],
                "latest_progress": self.sample_data[tracking_number]["progress"],
                "is_sample_data": True
            }
        else:
            # 模拟真实API响应
            return {
                "success": True,
                "tracking_number": tracking_number,
                "status": "查询中",
                "current_location": "数据处理中",
                "update_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "latest_progress": "正在查询物流信息...",
                "is_sample_data": True,
                "note": "此为示例数据，实际使用需要配置真实物流API"
            }

# 注册工具
from tools.mcp_base import mcp_manager
logistics_tool = LogisticsMCPTool()
mcp_manager.register_tool(logistics_tool)