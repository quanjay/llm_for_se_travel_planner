from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.routes import auth, travel_plans, expenses, voice
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI旅行规划师后端API"
)

# 添加请求验证异常处理器
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误，返回详细的错误信息"""
    errors = exc.errors()
    logger.error(f"请求验证失败: {request.url}")
    logger.error(f"错误详情: {errors}")
    logger.error(f"请求体: {await request.body()}")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": 400,
            "message": "请求参数验证失败",
            "detail": errors
        }
    )

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(travel_plans.router, prefix="/api/travel-plans", tags=["行程规划"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["费用管理"])
app.include_router(voice.router, prefix="/api/voice", tags=["语音识别"])

@app.get("/")
async def root():
    return {"message": "AI旅行规划师API服务正在运行"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )