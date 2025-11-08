"""
用户认证相关 API 路由
使用 Supabase 作为数据存储，保留 JWT 认证
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import create_access_token, verify_password, get_password_hash, verify_token
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.database_service import db
from datetime import timedelta
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=dict)
async def register(user_data: UserCreate):
    """用户注册"""
    
    # 检查数据库服务
    if not db.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库服务不可用"
        )
    
    try:
        # 检查邮箱是否已存在
        existing_user = await db.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        
        # 检查用户名是否已存在
        existing_username = await db.get_user_by_username(user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被占用"
            )
        
        # 创建新用户
        hashed_password = get_password_hash(user_data.password)
        new_user = await db.create_user(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            phone=user_data.phone
        )
        
        logger.info(f"用户注册成功: {new_user['email']}")
        
        return {
            "code": 200,
            "message": "注册成功",
            "data": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"注册失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """用户登录"""
    
    # 检查数据库服务
    if not db.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库服务不可用"
        )
    
    try:
        # 查找用户
        user = await db.get_user_by_email(user_data.email)
        
        if not user or not verify_password(user_data.password, user['hashed_password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user['id'], expires_delta=access_token_expires
        )
        
        logger.info(f"用户登录成功: {user['email']}")
        
        return {
            "code": 200,
            "message": "登录成功",
            "data": {
                "token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user['id'],
                    "email": user['email'],
                    "username": user['username'],
                    "phone": user.get('phone'),
                    "avatar": user.get('avatar'),
                    "created_at": user['created_at'],
                    "updated_at": user['updated_at']
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """获取当前用户信息"""
    
    # 检查数据库服务
    if not db.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库服务不可用"
        )
    
    try:
        # 验证令牌
        token = credentials.credentials
        user_id = verify_token(token)
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的访问令牌"
            )
        
        # 获取用户信息
        user = await db.get_user_by_id(int(user_id))
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "id": user['id'],
                "email": user['email'],
                "username": user['username'],
                "phone": user.get('phone'),
                "avatar": user.get('avatar'),
                "created_at": user['created_at'],
                "updated_at": user['updated_at']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )


@router.put("/update", response_model=UserResponse)
async def update_user_info(
    update_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """更新用户信息"""
    
    # 检查数据库服务
    if not db.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库服务不可用"
        )
    
    try:
        # 验证令牌
        token = credentials.credentials
        user_id = verify_token(token)
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的访问令牌"
            )
        
        # 允许更新的字段
        allowed_fields = ['username', 'phone', 'avatar']
        filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
        
        if not filtered_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有可更新的字段"
            )
        
        # 如果要更新用户名，检查是否已存在
        if 'username' in filtered_data:
            existing_user = await db.get_user_by_username(filtered_data['username'])
            if existing_user and existing_user['id'] != int(user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户名已被占用"
                )
        
        # 更新用户信息
        updated_user = await db.update_user(int(user_id), filtered_data)
        
        logger.info(f"用户信息更新成功: {user_id}")
        
        return {
            "code": 200,
            "message": "更新成功",
            "data": {
                "id": updated_user['id'],
                "email": updated_user['email'],
                "username": updated_user['username'],
                "phone": updated_user.get('phone'),
                "avatar": updated_user.get('avatar'),
                "created_at": updated_user['created_at'],
                "updated_at": updated_user['updated_at']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新失败: {str(e)}"
        )


@router.put("/change-password")
async def change_password(
    password_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """修改密码"""
    
    # 检查数据库服务
    if not db.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库服务不可用"
        )
    
    try:
        # 验证令牌
        token = credentials.credentials
        user_id = verify_token(token)
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的访问令牌"
            )
        
        # 获取旧密码和新密码
        old_password = password_data.get('old_password')
        new_password = password_data.get('new_password')
        
        if not old_password or not new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码和新密码不能为空"
            )
        
        # 获取用户信息
        user = await db.get_user_by_id(int(user_id))
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 验证旧密码
        if not verify_password(old_password, user['hashed_password']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码错误"
            )
        
        # 更新密码
        new_hashed_password = get_password_hash(new_password)
        await db.update_user(int(user_id), {"hashed_password": new_hashed_password})
        
        logger.info(f"用户密码修改成功: {user_id}")
        
        return {
            "code": 200,
            "message": "密码修改成功",
            "data": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改密码失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"修改密码失败: {str(e)}"
        )
