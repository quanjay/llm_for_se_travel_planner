"""
Supabase 数据库服务
完全替代 SQLAlchemy，提供所有数据库操作
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase库未安装，请运行: pip install supabase")


class SupabaseService:
    """Supabase 数据库服务 - 完整的数据库访问层"""
    
    def __init__(self):
        """初始化 Supabase 客户端"""
        self.enabled = False
        self.client: Optional[Any] = None
        self.error_message = ""
        
        # 检查配置
        enable_cloud_sync = settings.__dict__.get('ENABLE_CLOUD_SYNC', False)
        if isinstance(enable_cloud_sync, str):
            enable_cloud_sync = enable_cloud_sync.lower() == 'true'
        
        supabase_url = settings.__dict__.get('SUPABASE_URL', '')
        supabase_key = settings.__dict__.get('SUPABASE_KEY', '')
        
        if not enable_cloud_sync or not supabase_url or not supabase_key:
            self.error_message = "Supabase未启用或配置不完整"
            logger.warning(self.error_message)
            return
        
        if not SUPABASE_AVAILABLE:
            self.error_message = "Supabase库未安装"
            logger.error(self.error_message)
            return
        
        try:
            self.client = create_client(supabase_url, supabase_key)
            self.enabled = True
            logger.info("✅ Supabase 数据库连接成功")
        except Exception as e:
            self.error_message = f"Supabase 初始化失败: {str(e)}"
            logger.error(self.error_message)
    
    def is_enabled(self) -> bool:
        """检查服务是否可用"""
        return self.enabled and self.client is not None
    
    # ========================================
    # 用户相关操作 (Users)
    # ========================================
    
    async def create_user(self, email: str, username: str, hashed_password: str, 
                         phone: Optional[str] = None) -> Dict[str, Any]:
        """创建新用户"""
        if not self.is_enabled():
            raise Exception("数据库服务未启用")
        
        try:
            response = self.client.table("users").insert({
                "email": email,
                "username": username,
                "hashed_password": hashed_password,
                "phone": phone
            }).execute()
            
            if response.data:
                logger.info(f"创建用户成功: {email}")
                return response.data[0]
            else:
                raise Exception("创建用户失败：无返回数据")
                
        except Exception as e:
            logger.error(f"创建用户失败: {str(e)}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱获取用户"""
        if not self.is_enabled():
            raise Exception("数据库服务未启用")
        
        try:
            response = self.client.table("users").select("*").eq("email", email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"查询用户失败: {str(e)}")
            raise
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户"""
        if not self.is_enabled():
            raise Exception("数据库服务未启用")
        
        try:
            response = self.client.table("users").select("*").eq("username", username).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"查询用户失败: {str(e)}")
            raise
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户"""
        if not self.is_enabled():
            raise Exception("数据库服务未启用")
        
        try:
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"查询用户失败: {str(e)}")
            raise
    
    async def update_user(self, user_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新用户信息"""
        if not self.is_enabled():
            raise Exception("数据库服务未启用")
        
        try:
            response = self.client.table("users").update(update_data).eq("id", user_id).execute()
            
            if response.data:
                logger.info(f"更新用户成功: {user_id}")
                return response.data[0]
            else:
                raise Exception("更新用户失败")
                
        except Exception as e:
            logger.error(f"更新用户失败: {str(e)}")
            raise
    
    # ========================================
    # 旅行计划相关操作 (Travel Plans)
    # ========================================
    
    async def create_travel_plan(self, user_id: int, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建旅行计划"""
        if not self.is_enabled():
            raise Exception("数据库服务未启用")
        
        try:
            # 准备数据
            insert_data = {
                "user_id": user_id,
                "title": plan_data.get("title"),
                "destination": plan_data.get("destination"),
                "start_date": plan_data.get("start_date"),
                "end_date": plan_data.get("end_date"),
                "budget": plan_data.get("budget"),
                "people_count": plan_data.get("people_count", 1),
                "preferences": plan_data.get("preferences"),
                "itinerary": plan_data.get("itinerary"),
                "status": plan_data.get("status", "draft"),
                "total_cost": plan_data.get("total_cost", 0)
            }
            
            # 移除 None 值
            insert_data = {k: v for k, v in insert_data.items() if v is not None}
            
            response = self.client.table("travel_plans").insert(insert_data).execute()
            
            if response.data:
                logger.info(f"创建行程成功: {response.data[0]['id']}")
                return response.data[0]
            else:
                raise Exception("创建行程失败")
                
        except Exception as e:
            logger.error(f"创建行程失败: {str(e)}")
            raise
    
    async def get_travel_plan_by_id(self, plan_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """获取单个旅行计划"""
        if not self.is_enabled():
            raise Exception("数据库服务未启用")
        
        try:
            response = self.client.table("travel_plans").select("*").eq(
                "id", plan_id
            ).eq("user_id", user_id).execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"查询行程失败: {str(e)}")
            raise
    
    async def get_user_travel_plans(self, user_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取用户的所有旅行计划"""
        if not self.is_enabled():
            raise Exception("数据库服务未启用")
        
        try:
            query = self.client.table("travel_plans").select("*").eq("user_id", user_id)
            
            if status:
                query = query.eq("status", status)
            
            response = query.execute()
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"查询行程列表失败: {str(e)}")
            raise
    
    async def update_travel_plan(self, plan_id: int, user_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新旅行计划"""
        if not self.is_enabled():
            raise Exception("数据库服务未启用")
        
        try:
            # 移除 None 值
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            response = self.client.table("travel_plans").update(update_data).eq(
                "id", plan_id
            ).eq("user_id", user_id).execute()
            
            if response.data:
                logger.info(f"更新行程成功: {plan_id}")
                return response.data[0]
            else:
                raise Exception("更新行程失败或无权限")
                
        except Exception as e:
            logger.error(f"更新行程失败: {str(e)}")
            raise
    
    async def delete_travel_plan(self, plan_id: int, user_id: int) -> bool:
        """删除旅行计划"""
        if not self.is_enabled():
            raise Exception("数据库服务未启用")
        
        try:
            response = self.client.table("travel_plans").delete().eq(
                "id", plan_id
            ).eq("user_id", user_id).execute()
            
            logger.info(f"删除行程成功: {plan_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除行程失败: {str(e)}")
            raise
    
    # ========================================
    # 费用记录相关操作 (Expenses)
    # ========================================
    
    async def create_expense(self, user_id: int, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建费用记录"""
        if not self.is_enabled():
            raise Exception("数据库服务未启用")
        
        try:
            insert_data = {
                "user_id": user_id,
                "travel_plan_id": expense_data.get("travel_plan_id"),
                "category": expense_data.get("category"),
                "amount": expense_data.get("amount"),
                "description": expense_data.get("description"),
                "expense_date": expense_data.get("expense_date") or expense_data.get("date")
            }
            
            # 移除 None 值
            insert_data = {k: v for k, v in insert_data.items() if v is not None}
            
            response = self.client.table("expenses").insert(insert_data).execute()
            
            if response.data:
                logger.info(f"创建费用成功: {response.data[0]['id']}")
                return response.data[0]
            else:
                raise Exception("创建费用失败")
                
        except Exception as e:
            logger.error(f"创建费用失败: {str(e)}")
            raise
    
    async def get_expense_by_id(self, expense_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """获取单个费用记录"""
        if not self.is_enabled():
            raise Exception("数据库服务未启用")
        
        try:
            response = self.client.table("expenses").select("*").eq(
                "id", expense_id
            ).eq("user_id", user_id).execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"查询费用失败: {str(e)}")
            raise
    
    async def get_user_expenses(self, user_id: int, travel_plan_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取用户的费用记录"""
        if not self.is_enabled():
            raise Exception("数据库服务未启用")
        
        try:
            query = self.client.table("expenses").select("*").eq("user_id", user_id)
            
            if travel_plan_id:
                query = query.eq("travel_plan_id", travel_plan_id)
            
            response = query.execute()
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"查询费用列表失败: {str(e)}")
            raise
    
    async def get_plan_expenses(self, plan_id: int, user_id: int) -> List[Dict[str, Any]]:
        """获取指定行程的所有费用"""
        if not self.is_enabled():
            raise Exception("数据库服务未启用")
        
        try:
            response = self.client.table("expenses").select("*").eq(
                "travel_plan_id", plan_id
            ).eq("user_id", user_id).execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"查询行程费用失败: {str(e)}")
            raise
    
    async def update_expense(self, expense_id: int, user_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新费用记录"""
        if not self.is_enabled():
            raise Exception("数据库服务未启用")
        
        try:
            # 移除 None 值
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            response = self.client.table("expenses").update(update_data).eq(
                "id", expense_id
            ).eq("user_id", user_id).execute()
            
            if response.data:
                logger.info(f"更新费用成功: {expense_id}")
                return response.data[0]
            else:
                raise Exception("更新费用失败或无权限")
                
        except Exception as e:
            logger.error(f"更新费用失败: {str(e)}")
            raise
    
    async def delete_expense(self, expense_id: int, user_id: int) -> bool:
        """删除费用记录"""
        if not self.is_enabled():
            raise Exception("数据库服务未启用")
        
        try:
            response = self.client.table("expenses").delete().eq(
                "id", expense_id
            ).eq("user_id", user_id).execute()
            
            logger.info(f"删除费用成功: {expense_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除费用失败: {str(e)}")
            raise
    
    # ========================================
    # 统计和分析功能
    # ========================================
    
    async def get_expense_statistics(self, user_id: int, travel_plan_id: Optional[int] = None) -> Dict[str, Any]:
        """获取费用统计"""
        if not self.is_enabled():
            raise Exception("数据库服务未启用")
        
        try:
            # 获取所有费用
            expenses = await self.get_user_expenses(user_id, travel_plan_id)
            
            if not expenses:
                return {
                    "total": 0,
                    "count": 0,
                    "by_category": {},
                    "average": 0
                }
            
            # 计算总额
            total = sum(float(exp.get("amount", 0)) for exp in expenses)
            count = len(expenses)
            
            # 按类别统计
            by_category = {}
            for exp in expenses:
                category = exp.get("category", "other")
                if category not in by_category:
                    by_category[category] = {"count": 0, "total": 0}
                by_category[category]["count"] += 1
                by_category[category]["total"] += float(exp.get("amount", 0))
            
            return {
                "total": total,
                "count": count,
                "by_category": by_category,
                "average": total / count if count > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"统计费用失败: {str(e)}")
            raise
    
    async def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """获取用户统计信息"""
        if not self.is_enabled():
            raise Exception("数据库服务未启用")
        
        try:
            # 获取行程数量
            plans = await self.get_user_travel_plans(user_id)
            plans_count = len(plans)
            
            # 按状态统计
            status_counts = {}
            for plan in plans:
                status = plan.get("status", "draft")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # 获取费用统计
            expense_stats = await self.get_expense_statistics(user_id)
            
            return {
                "plans_count": plans_count,
                "plans_by_status": status_counts,
                "total_expenses": expense_stats["total"],
                "expenses_count": expense_stats["count"]
            }
            
        except Exception as e:
            logger.error(f"获取用户统计失败: {str(e)}")
            raise


# 创建全局服务实例
db = SupabaseService()
