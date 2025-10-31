from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_travel_plans():
    """获取行程列表 - 开发中"""
    return {"message": "行程规划功能开发中"}

@router.post("/")
async def create_travel_plan():
    """创建新行程 - 开发中"""
    return {"message": "创建行程功能开发中"}