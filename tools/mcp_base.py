#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP工具基类 - Model Context Protocol 工具管理
提供统一的工具接口和权限管理
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class MCPTool(ABC):
    """MCP工具抽象基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.is_enabled = False
        self.required_env_vars: List[str] = []
        
    @abstractmethod
    def initialize(self) -> bool:
        """初始化工具 - 检查依赖和配置"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行工具功能"""
        pass
    
    def check_permissions(self) -> bool:
        """检查必要的环境变量和权限"""
        missing_vars = []
        for var in self.required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️  工具 {self.name} 缺少必要的环境变量: {', '.join(missing_vars)}")
            return False
        return True
    
    def enable(self):
        """启用工具"""
        if self.initialize():
            self.is_enabled = True
            print(f"✅ 工具 {self.name} 已启用")
            return True
        else:
            print(f"❌ 工具 {self.name} 启用失败")
            return False
    
    def disable(self):
        """禁用工具"""
        self.is_enabled = False
        print(f"🚫 工具 {self.name} 已禁用")

class MCPManager:
    """MCP工具管理器"""
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.enabled_tools: List[str] = []
    
    def register_tool(self, tool: MCPTool):
        """注册工具"""
        self.tools[tool.name] = tool
        print(f"📝 已注册工具: {tool.name} - {tool.description}")
    
    def enable_tool(self, tool_name: str) -> bool:
        """启用指定工具"""
        if tool_name in self.tools:
            if self.tools[tool_name].enable():
                self.enabled_tools.append(tool_name)
                return True
        return False
    
    def disable_tool(self, tool_name: str):
        """禁用指定工具"""
        if tool_name in self.tools:
            self.tools[tool_name].disable()
            if tool_name in self.enabled_tools:
                self.enabled_tools.remove(tool_name)
    
    def get_available_tools(self) -> List[str]:
        """获取所有可用工具列表"""
        return list(self.tools.keys())
    
    def get_enabled_tools(self) -> List[str]:
        """获取已启用工具列表"""
        return self.enabled_tools.copy()
    
    def execute_tool(self, tool_name: str, **kwargs) -> Optional[Dict[str, Any]]:
        """执行指定工具"""
        if tool_name not in self.tools:
            print(f"❌ 未找到工具: {tool_name}")
            return None
            
        tool = self.tools[tool_name]
        if not tool.is_enabled:
            print(f"❌ 工具 {tool_name} 未启用")
            return None
            
        try:
            return tool.execute(**kwargs)
        except Exception as e:
            print(f"❌ 执行工具 {tool_name} 时出错: {e}")
            return {"error": str(e)}

# 全局MCP管理器实例
mcp_manager = MCPManager()