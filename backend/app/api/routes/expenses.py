from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_expenses():
    """获取费用列表 - 开发中"""
    return {"message": "费用管理功能开发中"}

@router.post("/")
async def create_expense():
    """添加费用记录 - 开发中"""
    return {"message": "添加费用功能开发中"}