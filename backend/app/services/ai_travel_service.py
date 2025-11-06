from typing import Dict, List, Any
import json
import asyncio
import logging
from datetime import datetime, timedelta
from app.core.config import settings
from openai import OpenAI

# 设置日志
logger = logging.getLogger(__name__)

class AITravelPlannerService:
    """AI行程规划服务"""
    
    def __init__(self):
        self.api_key = settings.QIANWEN_API_KEY
        
        # 初始化 OpenAI 客户端（用于通义千问）
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            logger.info(f"通义千问 API 已配置，密钥前缀: {self.api_key[:10]}...")
        else:
            self.client = None
            logger.warning("通义千问 API KEY 未配置，将使用默认模板")
    
    async def generate_travel_plan(
        self,
        destination: str,
        start_date: datetime,
        end_date: datetime,
        budget: float,
        people_count: int,
        preferences: List[str],
        special_requirements: str = None
    ) -> Dict[str, Any]:
        """生成AI行程规划"""
        
        # 计算天数
        days = (end_date - start_date).days + 1
        logger.info(f"开始生成 {destination} {days}天行程，预算: {budget}元，人数: {people_count}人")
        
        # 构建提示词
        prompt = self._build_prompt(
            destination=destination,
            days=days,
            budget=budget,
            people_count=people_count,
            preferences=preferences,
            special_requirements=special_requirements,
            start_date=start_date
        )
        
        # 检查 API 客户端是否配置
        if not self.client:
            logger.warning("通义千问 API 客户端未配置，使用默认模板")
            return self._generate_fallback_plan(destination, start_date, days, budget, people_count)
        
        try:
            logger.info(f"正在调用通义千问 API 生成 {destination} 的行程...")
            
            # 调用通义千问API
            response = await self._call_qianwen_api(prompt)
            logger.info("通义千问 API 调用成功")
            
            # 解析响应并构建行程数据
            itinerary = self._parse_ai_response(response, start_date, days)
            
            return {
                "success": True,
                "itinerary": itinerary,
                "estimated_cost": self._calculate_total_cost(itinerary),
                "ai_generated": True
            }
        except Exception as e:
            logger.error(f"通义千问 API 调用失败: {str(e)}")
            logger.info("正在使用默认模板生成行程...")
            # 如果AI服务失败，返回默认模板
            fallback_result = self._generate_fallback_plan(destination, start_date, days, budget, people_count)
            fallback_result["ai_generated"] = False
            fallback_result["error"] = f"AI服务暂时不可用: {str(e)}"
            return fallback_result
    
    def _build_prompt(
        self,
        destination: str,
        days: int,
        budget: float,
        people_count: int,
        preferences: List[str],
        special_requirements: str,
        start_date: datetime
    ) -> str:
        """构建AI提示词"""
        
        preferences_str = "、".join(preferences) if preferences else "无特殊偏好"
        special_str = f"特殊需求：{special_requirements}" if special_requirements else ""
        
        prompt = f"""请为{destination}{days}天旅行制定行程计划：
- 人数：{people_count}人，预算：{budget}元
- 偏好：{preferences_str}
{f'- {special_str}' if special_str else ''}
- 开始：{start_date.strftime('%Y-%m-%d')}

返回JSON格式，每天3-4个活动：
{{
  "itinerary": [
    {{
      "day": 1,
      "date": "{start_date.strftime('%Y-%m-%d')}",
      "activities": [
        {{"type": "attraction", "name": "景点名", "description": "简介", "location": "地址", "start_time": "09:00", "end_time": "12:00", "cost": 100, "rating": 4.5}},
        {{"type": "restaurant", "name": "餐厅名", "description": "特色", "location": "地址", "start_time": "12:30", "end_time": "14:00", "cost": 80, "rating": 4.3}}
      ],
      "total_cost": 180
    }}
  ]
}}

要求：活动类型仅限于 attraction(景点)/restaurant(餐厅)/transport(交通)/shopping(购物)/entertainment(娱乐) 之一，费用合理，只返回JSON无其他文字。"""
        return prompt
    
    async def _call_qianwen_api(self, prompt: str) -> str:
        """调用通义千问API"""
        logger.info("调用通义千问 API")
        
        # 重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"第 {attempt + 1} 次尝试调用 API...")
                
                # 使用 OpenAI 客户端调用通义千问
                loop = asyncio.get_event_loop()
                completion = await loop.run_in_executor(
                    None,
                    lambda: self.client.chat.completions.create(
                        model="qwen-turbo",
                        messages=[
                            {"role": "system", "content": "你是一个专业的旅行规划助手。请严格按照要求返回JSON格式的行程计划。"},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=16000,
                        timeout=120
                    )
                )
                
                logger.info("API 调用成功，正在解析响应...")
                response_content = completion.choices[0].message.content
                
                if response_content:
                    return response_content
                else:
                    raise Exception("API 返回空响应")
                    
            except Exception as e:
                logger.error(f"API 调用出现错误 (第 {attempt + 1} 次): {str(e)}")
                
                # 检查是否是认证错误
                if "401" in str(e) or "unauthorized" in str(e).lower():
                    logger.error("API 密钥无效或已过期")
                    raise Exception("API 密钥无效，请检查 QIANWEN_API_KEY 配置")
                
                # 检查是否是频率限制
                if "429" in str(e) or "rate limit" in str(e).lower():
                    logger.warning("API 调用频率限制，等待重试...")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(5)
                        continue
                    else:
                        raise Exception("API 调用频率限制，请稍后再试")
                
                # 检查是否是超时错误
                if "timeout" in str(e).lower():
                    logger.warning(f"API 调用超时 (第 {attempt + 1} 次)")
                    if attempt < max_retries - 1:
                        logger.info("等待 3 秒后重试...")
                        await asyncio.sleep(3)
                        continue
                    else:
                        logger.error("API 调用多次超时，放弃重试")
                        raise Exception("API 调用超时，请检查网络连接或稍后再试")
                
                # 其他错误
                if attempt < max_retries - 1:
                    logger.info("等待 2 秒后重试...")
                    await asyncio.sleep(2)
                    continue
                else:
                    raise Exception(f"API 调用失败: {str(e)}")
    
    def _parse_ai_response(self, response: str, start_date: datetime, days: int) -> List[Dict[str, Any]]:
        """解析AI响应并构建标准格式的行程数据"""
        try:
            # 尝试解析JSON
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                raise ValueError("无法找到JSON数据")
            
            data = json.loads(json_str)
            
            if "itinerary" in data:
                return data["itinerary"]
            else:
                return data if isinstance(data, list) else []
                
        except (json.JSONDecodeError, ValueError):
            # 如果解析失败，返回默认计划
            return self._generate_default_itinerary(start_date, days)
    
    def _generate_default_itinerary(self, start_date: datetime, days: int) -> List[Dict[str, Any]]:
        """生成默认行程计划"""
        itinerary = []
        
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            day_plan = {
                "day": day + 1,
                "date": current_date.strftime("%Y-%m-%d"),
                "activities": [
                    {
                        "type": "attraction",
                        "name": "景点游览",
                        "description": "游览当地知名景点",
                        "location": "市中心",
                        "start_time": "09:00",
                        "end_time": "12:00",
                        "cost": 100,
                        "rating": 4.5
                    },
                    {
                        "type": "restaurant", 
                        "name": "当地美食",
                        "description": "品尝当地特色菜",
                        "location": "美食街",
                        "start_time": "12:30",
                        "end_time": "14:00",
                        "cost": 80,
                        "rating": 4.3
                    },
                    {
                        "type": "attraction",
                        "name": "文化体验",
                        "description": "了解当地文化",
                        "location": "文化区",
                        "start_time": "15:00",
                        "end_time": "18:00",
                        "cost": 60,
                        "rating": 4.2
                    }
                ],
                "total_cost": 240
            }
            itinerary.append(day_plan)
        
        return itinerary
    
    def _calculate_total_cost(self, itinerary: List[Dict[str, Any]]) -> float:
        """计算总费用"""
        total = 0
        for day in itinerary:
            total += day.get("total_cost", 0)
        return total
    
    def _generate_fallback_plan(
        self,
        destination: str,
        start_date: datetime,
        days: int,
        budget: float,
        people_count: int
    ) -> Dict[str, Any]:
        """生成备用计划（当AI服务不可用时）"""
        itinerary = self._generate_default_itinerary(start_date, days)
        
        return {
            "success": True,
            "itinerary": itinerary,
            "estimated_cost": self._calculate_total_cost(itinerary),
            "note": "使用默认模板生成，建议手动调整"
        }

# 创建服务实例
ai_travel_service = AITravelPlannerService()