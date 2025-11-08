"""
Supabase 云端存储服务
提供云端数据同步、备份和恢复功能
"""

import logging
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase库未安装，请运行: pip install supabase")


class SupabaseService:
    """Supabase 云端存储服务"""
    
    def __init__(self):
        """初始化 Supabase 客户端"""
        self.enabled = False
        self.client: Optional[Any] = None
        self.error_message = ""
        
        # 检查是否启用云端同步
        enable_cloud_sync = settings.__dict__.get('ENABLE_CLOUD_SYNC', False)
        if isinstance(enable_cloud_sync, str):
            enable_cloud_sync = enable_cloud_sync.lower() == 'true'
        
        supabase_url = settings.__dict__.get('SUPABASE_URL', '')
        supabase_key = settings.__dict__.get('SUPABASE_KEY', '')
        
        if not enable_cloud_sync or not supabase_url or not supabase_key:
            self.error_message = "云端同步未启用或配置不完整"
            logger.info(self.error_message)
            return
        
        if not SUPABASE_AVAILABLE:
            self.error_message = "Supabase库未安装"
            logger.warning(self.error_message)
            return
        
        try:
            # 初始化 Supabase 客户端
            self.client = create_client(supabase_url, supabase_key)
            self.enabled = True
            logger.info("✅ Supabase 客户端初始化成功")
        except Exception as e:
            self.error_message = f"Supabase 初始化失败: {str(e)}"
            logger.error(self.error_message)
    
    def is_enabled(self) -> bool:
        """检查是否启用云端同步"""
        return self.enabled and self.client is not None
    
    async def sync_travel_plan(self, user_id: int, travel_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        同步行程计划到云端
        
        Args:
            user_id: 用户ID
            travel_plan: 行程计划数据
            
        Returns:
            同步结果
        """
        if not self.is_enabled():
            return {
                "success": False,
                "message": "云端同步未启用",
                "synced": False
            }
        
        try:
            # 准备数据 - 根据实际表结构
            sync_data = {
                "user_id": user_id,
                "plan_id": travel_plan.get("id"),  # 本地行程 ID
                "title": travel_plan.get("title") or travel_plan.get("name", ""),
                "destination": travel_plan.get("destination"),
                "start_date": travel_plan.get("start_date"),
                "end_date": travel_plan.get("end_date"),
                "budget": float(travel_plan.get("budget", 0)) if travel_plan.get("budget") else None,
                "preferences": travel_plan.get("preferences"),
                "itinerary": travel_plan.get("itinerary"),
                "status": travel_plan.get("status", "draft"),
                "updated_at": datetime.utcnow().isoformat(),
                "created_at": travel_plan.get("created_at") or datetime.utcnow().isoformat()
            }
            
            # 移除 None 值
            sync_data = {k: v for k, v in sync_data.items() if v is not None}
            
            # 上传到 Supabase
            response = self.client.table("travel_plans").upsert(
                sync_data,
                returning="minimal"
            ).execute()
            
            logger.info(f"行程 {travel_plan.get('id')} 同步到云端成功")
            
            return {
                "success": True,
                "message": "行程同步成功",
                "synced": True,
                "plan_id": travel_plan.get("id")
            }
            
        except Exception as e:
            logger.error(f"行程同步失败: {str(e)}")
            return {
                "success": False,
                "message": f"行程同步失败: {str(e)}",
                "synced": False
            }
    
    async def sync_expense(self, user_id: int, expense: Dict[str, Any]) -> Dict[str, Any]:
        """
        同步费用记录到云端
        
        Args:
            user_id: 用户ID
            expense: 费用记录数据
            
        Returns:
            同步结果
        """
        if not self.is_enabled():
            return {
                "success": False,
                "message": "云端同步未启用",
                "synced": False
            }
        
        try:
            # 准备数据 - 根据实际表结构
            sync_data = {
                "user_id": user_id,
                "expense_id": expense.get("id"),  # 本地费用 ID
                "travel_plan_id": expense.get("travel_plan_id"),
                "category": expense.get("category"),
                "amount": float(expense.get("amount", 0)) if expense.get("amount") else None,
                "description": expense.get("description"),
                "expense_date": expense.get("expense_date") or expense.get("date"),
                "updated_at": datetime.utcnow().isoformat(),
                "created_at": expense.get("created_at") or datetime.utcnow().isoformat()
            }
            
            # 移除 None 值
            sync_data = {k: v for k, v in sync_data.items() if v is not None}
            
            # 上传到 Supabase
            response = self.client.table("expenses").upsert(
                sync_data,
                returning="minimal"
            ).execute()
            
            logger.info(f"费用 {expense.get('id')} 同步到云端成功")
            
            return {
                "success": True,
                "message": "费用同步成功",
                "synced": True,
                "expense_id": expense.get("id")
            }
            
        except Exception as e:
            logger.error(f"费用同步失败: {str(e)}")
            return {
                "success": False,
                "message": f"费用同步失败: {str(e)}",
                "synced": False
            }
    
    async def sync_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        同步用户信息到云端（不包含密码）
        
        Args:
            user: 用户数据
            
        Returns:
            同步结果
        """
        if not self.is_enabled():
            return {
                "success": False,
                "message": "云端同步未启用",
                "synced": False
            }
        
        try:
            # 准备数据 - 不包含敏感信息如密码
            sync_data = {
                "user_id": user.get("id"),  # 本地用户 ID
                "email": user.get("email"),
                "username": user.get("username"),
                "phone": user.get("phone"),
                "avatar": user.get("avatar"),
                "updated_at": datetime.utcnow().isoformat(),
                "created_at": user.get("created_at") or datetime.utcnow().isoformat()
            }
            
            # 移除 None 值
            sync_data = {k: v for k, v in sync_data.items() if v is not None}
            
            # 上传到 Supabase
            response = self.client.table("users").upsert(
                sync_data,
                returning="minimal"
            ).execute()
            
            logger.info(f"用户 {user.get('id')} 同步到云端成功")
            
            return {
                "success": True,
                "message": "用户信息同步成功",
                "synced": True,
                "user_id": user.get("id")
            }
            
        except Exception as e:
            logger.error(f"用户同步失败: {str(e)}")
            return {
                "success": False,
                "message": f"用户同步失败: {str(e)}",
                "synced": False
            }
    
    async def get_user_travel_plans(self, user_id: int) -> Dict[str, Any]:
        """
        从云端获取用户的所有行程
        
        Args:
            user_id: 用户ID
            
        Returns:
            行程列表
        """
        if not self.is_enabled():
            return {
                "success": False,
                "message": "云端同步未启用",
                "data": []
            }
        
        try:
            response = self.client.table("travel_plans").select("*").eq(
                "user_id", user_id
            ).execute()
            
            logger.info(f"从云端获取用户 {user_id} 的行程成功")
            
            return {
                "success": True,
                "message": "获取行程成功",
                "data": response.data
            }
            
        except Exception as e:
            logger.error(f"获取云端行程失败: {str(e)}")
            return {
                "success": False,
                "message": f"获取行程失败: {str(e)}",
                "data": []
            }
    
    async def get_user_expenses(self, user_id: int) -> Dict[str, Any]:
        """
        从云端获取用户的所有费用
        
        Args:
            user_id: 用户ID
            
        Returns:
            费用列表
        """
        if not self.is_enabled():
            return {
                "success": False,
                "message": "云端同步未启用",
                "data": []
            }
        
        try:
            response = self.client.table("expenses").select("*").eq(
                "user_id", user_id
            ).execute()
            
            logger.info(f"从云端获取用户 {user_id} 的费用成功")
            
            return {
                "success": True,
                "message": "获取费用成功",
                "data": response.data
            }
            
        except Exception as e:
            logger.error(f"获取云端费用失败: {str(e)}")
            return {
                "success": False,
                "message": f"获取费用失败: {str(e)}",
                "data": []
            }
    
    async def get_user_info(self, user_id: int) -> Dict[str, Any]:
        """
        从云端获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户信息
        """
        if not self.is_enabled():
            return {
                "success": False,
                "message": "云端同步未启用",
                "data": None
            }
        
        try:
            response = self.client.table("users").select("*").eq(
                "user_id", user_id
            ).execute()
            
            logger.info(f"从云端获取用户 {user_id} 的信息成功")
            
            return {
                "success": True,
                "message": "获取用户信息成功",
                "data": response.data[0] if response.data else None
            }
            
        except Exception as e:
            logger.error(f"获取云端用户信息失败: {str(e)}")
            return {
                "success": False,
                "message": f"获取用户信息失败: {str(e)}",
                "data": None
            }
    
    async def sync_all_data(self, user_id: int, travel_plans: List[Dict], expenses: List[Dict]) -> Dict[str, Any]:
        """
        批量同步所有数据到云端
        
        Args:
            user_id: 用户ID
            travel_plans: 行程列表
            expenses: 费用列表
            
        Returns:
            同步结果
        """
        if not self.is_enabled():
            return {
                "success": False,
                "message": "云端同步未启用",
                "plans_synced": 0,
                "expenses_synced": 0
            }
        
        try:
            plans_synced = 0
            expenses_synced = 0
            
            # 同步行程
            for plan in travel_plans:
                result = await self.sync_travel_plan(user_id, plan)
                if result["synced"]:
                    plans_synced += 1
            
            # 同步费用
            for expense in expenses:
                result = await self.sync_expense(user_id, expense)
                if result["synced"]:
                    expenses_synced += 1
            
            logger.info(f"批量同步完成: {plans_synced} 个行程，{expenses_synced} 个费用")
            
            return {
                "success": True,
                "message": "批量同步成功",
                "plans_synced": plans_synced,
                "expenses_synced": expenses_synced,
                "total_synced": plans_synced + expenses_synced
            }
            
        except Exception as e:
            logger.error(f"批量同步失败: {str(e)}")
            return {
                "success": False,
                "message": f"批量同步失败: {str(e)}",
                "plans_synced": 0,
                "expenses_synced": 0,
                "total_synced": 0
            }
    
    async def delete_travel_plan_sync(self, user_id: int, plan_id: int) -> Dict[str, Any]:
        """
        从云端删除行程
        
        Args:
            user_id: 用户ID
            plan_id: 行程ID
            
        Returns:
            删除结果
        """
        if not self.is_enabled():
            return {
                "success": False,
                "message": "云端同步未启用"
            }
        
        try:
            response = self.client.table("travel_plans").delete().eq(
                "user_id", user_id
            ).eq("plan_id", plan_id).execute()
            
            logger.info(f"从云端删除行程 {plan_id} 成功")
            
            return {
                "success": True,
                "message": "删除成功"
            }
            
        except Exception as e:
            logger.error(f"从云端删除行程失败: {str(e)}")
            return {
                "success": False,
                "message": f"删除失败: {str(e)}"
            }
    
    async def delete_expense_sync(self, user_id: int, expense_id: int) -> Dict[str, Any]:
        """
        从云端删除费用
        
        Args:
            user_id: 用户ID
            expense_id: 费用ID
            
        Returns:
            删除结果
        """
        if not self.is_enabled():
            return {
                "success": False,
                "message": "云端同步未启用"
            }
        
        try:
            response = self.client.table("expenses").delete().eq(
                "user_id", user_id
            ).eq("expense_id", expense_id).execute()
            
            logger.info(f"从云端删除费用 {expense_id} 成功")
            
            return {
                "success": True,
                "message": "删除成功"
            }
            
        except Exception as e:
            logger.error(f"从云端删除费用失败: {str(e)}")
            return {
                "success": False,
                "message": f"删除失败: {str(e)}"
            }
    
    async def delete_user_sync(self, user_id: int) -> Dict[str, Any]:
        """
        从云端删除用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            删除结果
        """
        if not self.is_enabled():
            return {
                "success": False,
                "message": "云端同步未启用"
            }
        
        try:
            response = self.client.table("users").delete().eq(
                "user_id", user_id
            ).execute()
            
            logger.info(f"从云端删除用户 {user_id} 成功")
            
            return {
                "success": True,
                "message": "删除成功"
            }
            
        except Exception as e:
            logger.error(f"从云端删除用户失败: {str(e)}")
            return {
                "success": False,
                "message": f"删除失败: {str(e)}"
            }
    
    async def get_sync_status(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户的同步状态
        
        Args:
            user_id: 用户ID
            
        Returns:
            同步状态统计
        """
        if not self.is_enabled():
            return {
                "success": False,
                "enabled": False,
                "message": "云端同步未启用"
            }
        
        try:
            # 获取所有行程（不使用聚合函数）
            plans_response = self.client.table("travel_plans").select(
                "*"
            ).eq("user_id", user_id).execute()
            plans_count = len(plans_response.data) if plans_response.data else 0
            
            # 获取所有费用（不使用聚合函数）
            expenses_response = self.client.table("expenses").select(
                "*"
            ).eq("user_id", user_id).execute()
            expenses_count = len(expenses_response.data) if expenses_response.data else 0
            
            # 检查用户信息是否已同步
            user_response = self.client.table("users").select(
                "*"
            ).eq("user_id", user_id).execute()
            user_synced = len(user_response.data) > 0 if user_response.data else False
            
            return {
                "success": True,
                "enabled": True,
                "user_synced": user_synced,
                "plans_count": plans_count,
                "expenses_count": expenses_count,
                "total_items": plans_count + expenses_count,
                "message": f"同步状态: 用户{'已' if user_synced else '未'}同步, {plans_count} 个行程，{expenses_count} 个费用"
            }
            
        except Exception as e:
            logger.error(f"获取同步状态失败: {str(e)}")
            return {
                "success": False,
                "enabled": self.is_enabled(),
                "message": f"获取同步状态失败: {str(e)}"
            }


# 创建全局服务实例
supabase_service = SupabaseService()
