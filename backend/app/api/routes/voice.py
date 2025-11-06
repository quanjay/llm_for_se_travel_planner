from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional
import logging
from app.services.voice_recognition_service import voice_recognition_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/recognize")
async def recognize_voice(
    audio: UploadFile = File(..., description="音频文件（支持 WAV, PCM 格式）"),
    language: Optional[str] = "zh_cn"
):
    """
    语音识别接口
    
    接收音频文件，返回识别的文本和解析的旅行意图
    """
    try:
        # 验证文件类型
        if not audio.content_type or not audio.content_type.startswith('audio'):
            # 允许 application/octet-stream（原始音频数据）
            if audio.content_type != 'application/octet-stream':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不支持的文件类型，请上传音频文件"
                )
        
        # 读取音频数据
        audio_data = await audio.read()
        
        if len(audio_data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="音频文件为空"
            )
        
        logger.info(f"接收到音频文件: {audio.filename}, 大小: {len(audio_data)} bytes")
        
        # 调用语音识别服务
        recognition_result = await voice_recognition_service.recognize_audio(
            audio_data=audio_data,
            language=language
        )
        
        if not recognition_result["success"]:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "code": 503,
                    "message": f"语音识别失败: {recognition_result.get('error', '未知错误')}",
                    "data": None
                }
            )
        
        recognized_text = recognition_result["text"]
        
        if not recognized_text:
            return {
                "code": 200,
                "message": "未识别到有效内容",
                "data": {
                    "text": "",
                    "intent": None
                }
            }
        
        # 解析旅行意图
        travel_intent = voice_recognition_service.parse_travel_intent(recognized_text)
        
        return {
            "code": 200,
            "message": "识别成功",
            "data": {
                "text": recognized_text,
                "intent": travel_intent
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"语音识别处理失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语音识别处理失败: {str(e)}"
        )


@router.post("/parse-intent")
async def parse_travel_intent(text: str):
    """
    解析旅行意图接口
    
    从文本中提取旅行相关信息
    """
    try:
        intent = voice_recognition_service.parse_travel_intent(text)
        
        return {
            "code": 200,
            "message": "解析成功",
            "data": intent
        }
        
    except Exception as e:
        logger.error(f"意图解析失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"意图解析失败: {str(e)}"
        )


@router.post("/parse-expense")
async def parse_expense_intent(text: str):
    """
    解析费用记录意图接口
    
    从文本中提取费用相关信息
    """
    try:
        intent = voice_recognition_service.parse_expense_intent(text)
        
        return {
            "code": 200,
            "message": "解析成功",
            "data": intent
        }
        
    except Exception as e:
        logger.error(f"费用意图解析失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"费用意图解析失败: {str(e)}"
        )


@router.post("/recognize-expense")
async def recognize_expense_voice(
    audio: UploadFile = File(..., description="音频文件（支持 WAV, PCM 格式）"),
    language: Optional[str] = "zh_cn"
):
    """
    费用记录语音识别接口
    
    接收音频文件，返回识别的文本和解析的费用信息
    """
    try:
        # 验证文件类型
        if not audio.content_type or not audio.content_type.startswith('audio'):
            if audio.content_type != 'application/octet-stream':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不支持的文件类型，请上传音频文件"
                )
        
        # 读取音频数据
        audio_data = await audio.read()
        
        if len(audio_data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="音频文件为空"
            )
        
        logger.info(f"接收到费用记录音频: {audio.filename}, 大小: {len(audio_data)} bytes")
        
        # 调用语音识别服务
        recognition_result = await voice_recognition_service.recognize_audio(
            audio_data=audio_data,
            language=language
        )
        
        if not recognition_result["success"]:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "code": 503,
                    "message": f"语音识别失败: {recognition_result.get('error', '未知错误')}",
                    "data": None
                }
            )
        
        recognized_text = recognition_result["text"]
        
        if not recognized_text:
            return {
                "code": 200,
                "message": "未识别到有效内容",
                "data": {
                    "text": "",
                    "expense": None
                }
            }
        
        # 解析费用意图
        expense_intent = voice_recognition_service.parse_expense_intent(recognized_text)
        
        return {
            "code": 200,
            "message": "识别成功",
            "data": {
                "text": recognized_text,
                "expense": expense_intent
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"费用语音识别处理失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"费用语音识别处理失败: {str(e)}"
        )


@router.get("/status")
async def check_voice_service_status():
    """检查语音识别服务状态"""
    is_configured = all([
        voice_recognition_service.app_id,
        voice_recognition_service.api_key,
        voice_recognition_service.api_secret
    ])
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "available": is_configured,
            "provider": "科大讯飞",
            "message": "语音识别服务已配置" if is_configured else "语音识别服务未配置"
        }
    }
