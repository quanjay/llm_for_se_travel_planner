from typing import Dict, Any, Optional
import json
import base64
import hmac
import hashlib
import time
from datetime import datetime
from urllib.parse import urlencode
import websocket
import asyncio
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class VoiceRecognitionService:
    """科大讯飞语音识别服务"""
    
    def __init__(self):
        self.app_id = settings.XFYUN_APP_ID
        self.api_key = settings.XFYUN_API_KEY
        self.api_secret = settings.XFYUN_API_SECRET
        self.base_url = "wss://iat-api.xfyun.cn/v2/iat"
        
        if not all([self.app_id, self.api_key, self.api_secret]):
            logger.warning("科大讯飞语音识别 API 未完全配置")
    
    def create_url(self) -> str:
        """生成鉴权URL"""
        # 生成RFC1123格式的时间戳
        now = datetime.utcnow()
        date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # 拼接字符串
        signature_origin = f"host: iat-api.xfyun.cn\n"
        signature_origin += f"date: {date}\n"
        signature_origin += f"GET /v2/iat HTTP/1.1"
        
        # 进行hmac-sha256加密
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode('utf-8')
        
        # 构建authorization
        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
        
        # 构建请求参数
        params = {
            "authorization": authorization,
            "date": date,
            "host": "iat-api.xfyun.cn"
        }
        
        return f"{self.base_url}?{urlencode(params)}"
    
    def extract_pcm_from_wav(self, wav_data: bytes) -> bytes:
        """从WAV文件中提取PCM数据"""
        try:
            # WAV文件头通常是44字节
            # 检查是否是有效的WAV文件
            if len(wav_data) < 44:
                logger.warning(f"音频数据太短，可能不是有效的WAV文件: {len(wav_data)} bytes")
                return wav_data
            
            # 检查RIFF标识
            if wav_data[:4] != b'RIFF':
                logger.warning("不是有效的WAV文件，没有RIFF标识")
                return wav_data
            
            # 检查WAVE标识
            if wav_data[8:12] != b'WAVE':
                logger.warning("不是有效的WAV文件，没有WAVE标识")
                return wav_data
            
            # 查找data块
            data_pos = wav_data.find(b'data')
            if data_pos == -1:
                logger.warning("WAV文件中未找到data块")
                return wav_data
            
            # data块后4字节是数据大小，之后是PCM数据
            pcm_data = wav_data[data_pos + 8:]
            logger.info(f"从WAV文件中提取PCM数据: 原始{len(wav_data)}字节 -> PCM {len(pcm_data)}字节")
            return pcm_data
            
        except Exception as e:
            logger.error(f"提取PCM数据失败: {str(e)}")
            return wav_data
    
    async def recognize_audio(
        self, 
        audio_data: bytes,
        audio_format: str = "audio/L16;rate=16000",
        language: str = "zh_cn"
    ) -> Dict[str, Any]:
        """
        识别音频文件
        
        Args:
            audio_data: 音频二进制数据
            audio_format: 音频格式，默认为 PCM 16k 16bit
            language: 语言，zh_cn(中文) 或 en_us(英文)
        
        Returns:
            识别结果字典
        """
        if not all([self.app_id, self.api_key, self.api_secret]):
            return {
                "success": False,
                "error": "科大讯飞语音识别 API 未配置",
                "text": ""
            }
        
        try:
            # 如果是WAV文件，提取PCM数据
            if audio_data[:4] == b'RIFF':
                logger.info("检测到WAV文件，提取PCM数据")
                audio_data = self.extract_pcm_from_wav(audio_data)
            
            logger.info(f"准备识别音频: {len(audio_data)} bytes")
            result_text = ""
            
            # 创建WebSocket连接
            ws_url = self.create_url()
            
            def on_message(ws, message):
                nonlocal result_text
                try:
                    data = json.loads(message)
                    code = data.get("code", -1)
                    
                    logger.info(f"收到消息: code={code}, data={data}")
                    
                    if code != 0:
                        logger.error(f"识别错误: code={code}, message={data.get('message', '未知错误')}")
                        logger.error(f"完整错误信息: {json.dumps(data, ensure_ascii=False)}")
                        ws.close()
                        return
                    
                    # 解析识别结果
                    data_content = data.get("data", {})
                    result = data_content.get("result", {})
                    ws_list = result.get("ws", [])
                    
                    logger.info(f"解析结果: ws_list长度={len(ws_list)}")
                    
                    for ws_item in ws_list:
                        for cw_item in ws_item.get("cw", []):
                            word = cw_item.get("w", "")
                            if word:
                                result_text += word
                                logger.info(f"识别到词语: {word}")
                    
                    # 判断是否结束
                    status = data_content.get("status")
                    logger.info(f"当前状态: status={status}, 已识别文本长度={len(result_text)}")
                    
                    if status == 2:
                        logger.info(f"识别完成: {result_text}")
                        ws.close()
                        
                except Exception as e:
                    logger.error(f"解析识别结果出错: {str(e)}")
                    logger.exception(e)
                    ws.close()
            
            def on_error(ws, error):
                logger.error(f"WebSocket错误: {error}")
            
            def on_close(ws, close_status_code, close_msg):
                logger.info("WebSocket连接关闭")
            
            def on_open(ws):
                def run():
                    try:
                        # 发送配置信息
                        common_args = {
                            "app_id": self.app_id
                        }
                        business_args = {
                            "domain": "iat",
                            "language": language,
                            "accent": "mandarin",  # 普通话
                            "vad_eos": 2000,  # 静音检测时长 2秒
                            "dwa": "wpgs"  # 动态修正
                        }
                        
                        # 注意：第一帧不发送音频数据，只发送配置
                        frame = {
                            "common": common_args,
                            "business": business_args,
                            "data": {
                                "status": 0,
                                "format": "audio/L16;rate=16000",
                                "encoding": "raw",
                                "audio": ""
                            }
                        }
                        logger.info(f"发送配置帧: {json.dumps(frame, ensure_ascii=False)}")
                        ws.send(json.dumps(frame))
                        time.sleep(0.04)
                        
                        # 分片发送音频数据
                        chunk_size = 1280  # 40ms 音频数据 (16000 * 2 * 0.04 = 1280)
                        total_chunks = (len(audio_data) + chunk_size - 1) // chunk_size
                        logger.info(f"音频数据总大小: {len(audio_data)} bytes, 将分{total_chunks}片发送")
                        
                        for i in range(0, len(audio_data), chunk_size):
                            chunk = audio_data[i:i + chunk_size]
                            audio_base64 = base64.b64encode(chunk).decode('utf-8')
                            
                            # 判断状态
                            if i + chunk_size >= len(audio_data):
                                status = 2  # 最后一帧
                            else:
                                status = 1  # 中间帧
                            
                            frame = {
                                "data": {
                                    "status": status,
                                    "format": "audio/L16;rate=16000",
                                    "encoding": "raw",
                                    "audio": audio_base64
                                }
                            }
                            ws.send(json.dumps(frame))
                            
                            if i % (chunk_size * 10) == 0:  # 每10片打印一次日志
                                logger.info(f"已发送 {i // chunk_size + 1}/{total_chunks} 片")
                            
                            time.sleep(0.04)  # 模拟音频采集间隔
                        
                    except Exception as e:
                        logger.error(f"发送音频数据出错: {str(e)}")
                        ws.close()
                
                # 在新线程中运行
                import threading
                threading.Thread(target=run).start()
            
            # 创建WebSocket连接
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.on_open = on_open
            
            # 运行WebSocket（会阻塞直到连接关闭）
            ws.run_forever()
            
            return {
                "success": True,
                "text": result_text.strip(),
                "error": None
            }
            
        except Exception as e:
            logger.error(f"语音识别失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    def parse_expense_intent(self, text: str) -> Dict[str, Any]:
        """
        解析费用记录语音意图
        
        Args:
            text: 识别出的文本
        
        Returns:
            解析出的费用信息
        """
        import re
        from datetime import datetime
        
        result = {
            "amount": None,
            "category": None,
            "description": None,
            "expense_date": datetime.now().isoformat(),
            "raw_text": text
        }
        
        # 提取金额（按优先级排序，避免误匹配）
        amount_patterns = [
            r"花了?(\d+\.?\d*)元",
            r"花了?(\d+\.?\d*)块",
            r"消费了?(\d+\.?\d*)元?",
            r"支付了?(\d+\.?\d*)元?",
            r"花费(\d+\.?\d*)元?",
            r"(\d+\.?\d*)块钱",
            r"(\d+\.?\d*)rmb",
            r"(\d+\.?\d*)元",  # 最后匹配纯数字+元，避免过早匹配
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result["amount"] = float(match.group(1))
                    break
                except (ValueError, IndexError):
                    continue
        
        # 识别费用类别和描述
        category_keywords = {
            'transport': {
                'keywords': ['打车', '出租车', '滴滴', '公交', '地铁', '火车', '高铁', '飞机', '机票', '车票', '交通', '油费', '停车'],
                'description_templates': ['交通费用', '打车', '公共交通']
            },
            'accommodation': {
                'keywords': ['酒店', '住宿', '旅馆', '民宿', '客栈', '宾馆', '房费'],
                'description_templates': ['住宿费用', '酒店', '民宿']
            },
            'food': {
                'keywords': ['吃饭', '餐厅', '饭店', '美食', '午餐', '晚餐', '早餐', '夜宵', '小吃', '餐费', '喝咖啡', '奶茶'],
                'description_templates': ['餐饮费用', '就餐', '用餐']
            },
            'attraction': {
                'keywords': ['门票', '景点', '游览', '参观', '博物馆', '公园', '游乐园', '动物园'],
                'description_templates': ['景点门票', '游览费用', '门票']
            },
            'shopping': {
                'keywords': ['购物', '买', '商场', '超市', '纪念品', '特产', '商店'],
                'description_templates': ['购物消费', '购买商品', '购物']
            },
            'other': {
                'keywords': ['其他', '杂费', '费用'],
                'description_templates': ['其他费用', '杂项支出']
            }
        }
        
        # 匹配类别
        matched_category = None
        matched_keywords = []
        
        for category, data in category_keywords.items():
            for keyword in data['keywords']:
                if keyword in text:
                    matched_category = category
                    matched_keywords.append(keyword)
                    break
            if matched_category:
                break
        
        if matched_category:
            result["category"] = matched_category
            # 生成描述
            if matched_keywords:
                result["description"] = f"{matched_keywords[0]}"
        else:
            # 默认为其他类别
            result["category"] = "other"
        
        # 尝试提取更详细的描述信息
        # 提取地点/商家名称
        location_patterns = [
            r"在(.{2,10}?)(?:吃饭|消费|购物|花了)",
            r"(.{2,10}?)(?:餐厅|饭店|商场|超市|店)",
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                location = match.group(1).strip()
                if location and len(location) <= 20:
                    if result["description"]:
                        result["description"] = f"{location} - {result['description']}"
                    else:
                        result["description"] = location
                break
        
        # 如果没有描述，使用原文的简化版本
        if not result["description"] and result["amount"]:
            # 去掉金额部分，保留描述性文字
            desc = re.sub(r'\d+\.?\d*[元块钱rmb]*', '', text).strip()
            desc = re.sub(r'[花了消费支付]', '', desc).strip()
            if desc and len(desc) <= 50:
                result["description"] = desc
            else:
                result["description"] = "消费"
        
        # 日期识别（如果提到了日期）
        date_patterns = [
            r"昨天",
            r"前天",
            r"今天",
            r"刚才",
            r"(\d{1,2})号",
            r"(\d{1,2})日"
        ]
        
        date_keywords = {
            "昨天": -1,
            "前天": -2,
            "今天": 0,
            "刚才": 0
        }
        
        for keyword, offset in date_keywords.items():
            if keyword in text:
                from datetime import timedelta
                target_date = datetime.now() + timedelta(days=offset)
                result["expense_date"] = target_date.isoformat()
                break
        
        return result
    
    def parse_travel_intent(self, text: str) -> Dict[str, Any]:
        """
        解析用户语音意图，提取旅行规划相关信息
        
        Args:
            text: 识别出的文本
        
        Returns:
            解析出的旅行信息
        """
        import re
        
        result = {
            "destination": None,
            "days": None,
            "budget": None,
            "people_count": 1,
            "preferences": [],
            "raw_text": text
        }
        
        # 提取目的地（简单规则，可以用NLP优化）
        destination_patterns = [
            r"去([\u4e00-\u9fa5]+)",
            r"到([\u4e00-\u9fa5]+)",
            r"想去([\u4e00-\u9fa5]+)",
            r"([\u4e00-\u9fa5]+)旅游",
            r"([\u4e00-\u9fa5]+)旅行"
        ]
        for pattern in destination_patterns:
            match = re.search(pattern, text)
            if match:
                result["destination"] = match.group(1)
                break
        
        # 提取天数
        days_patterns = [
            r"(\d+)天",
            r"(\d+)日",
            r"(\d+)个晚上"
        ]
        for pattern in days_patterns:
            match = re.search(pattern, text)
            if match:
                result["days"] = int(match.group(1))
                break
        
        # 提取预算
        budget_patterns = [
            r"预算(\d+)元",
            r"预算(\d+)块",
            r"(\d+)元预算",
            r"(\d+)块钱",
            r"预算.*?(\d+)",
            r"(\d+)万"
        ]
        for pattern in budget_patterns:
            match = re.search(pattern, text)
            if match:
                budget = int(match.group(1))
                if "万" in pattern:
                    budget *= 10000
                result["budget"] = budget
                break
        
        # 提取人数
        people_patterns = [
            r"(\d+)人",
            r"(\d+)个人"
        ]
        for pattern in people_patterns:
            match = re.search(pattern, text)
            if match:
                result["people_count"] = int(match.group(1))
                break
        
        # 识别偏好关键词
        preference_keywords = {
            "美食": ["美食", "吃", "小吃", "餐厅", "美味"],
            "购物": ["购物", "买东西", "商场", "逛街"],
            "文化": ["文化", "历史", "博物馆", "古迹", "遗产"],
            "自然风光": ["风景", "自然", "山水", "海边", "沙滩", "森林"],
            "亲子": ["亲子", "带孩子", "小孩", "儿童"],
            "休闲": ["休闲", "放松", "度假"],
            "冒险": ["冒险", "刺激", "极限"],
            "摄影": ["拍照", "摄影", "打卡"]
        }
        
        for preference, keywords in preference_keywords.items():
            if any(keyword in text for keyword in keywords):
                result["preferences"].append(preference)
        
        return result


# 创建服务实例
voice_recognition_service = VoiceRecognitionService()
