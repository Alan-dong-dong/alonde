import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio
from app.core.config import settings
from app.core.exceptions import WeatherAPIException
from app.models.schemas import WeatherModel, LocationModel, WeatherCondition
import logging

logger = logging.getLogger(__name__)


class WeatherService:
    """和风天气API服务类"""
    
    def __init__(self):
        self.api_key = settings.HEFENG_API_KEY
        self.base_url = settings.HEFENG_BASE_URL
        self.timeout = settings.REQUEST_TIMEOUT
        
        if not self.api_key:
            logger.warning("和风天气API密钥未配置")
    
    async def get_current_weather(self, location: LocationModel) -> WeatherModel:
        """获取当前天气信息"""
        try:
            # 构建请求URL
            url = f"{self.base_url}/v7/weather/now"
            params = {
                "location": f"{location.longitude},{location.latitude}",
                "key": self.api_key
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("code") != "200":
                    raise WeatherAPIException(f"天气API返回错误: {data.get('code')}")
                
                weather_data = data.get("now", {})
                
                return self._parse_weather_data(weather_data, location)
                
        except httpx.TimeoutException:
            logger.error("天气API请求超时")
            raise WeatherAPIException("天气服务请求超时")
        except httpx.HTTPError as e:
            logger.error(f"天气API请求失败: {e}")
            raise WeatherAPIException("天气服务暂时不可用")
        except Exception as e:
            logger.error(f"获取天气信息时发生未知错误: {e}")
            raise WeatherAPIException("获取天气信息失败")
    
    async def get_weather_forecast(self, location: LocationModel, days: int = 3) -> List[WeatherModel]:
        """获取天气预报"""
        try:
            url = f"{self.base_url}/v7/weather/{days}d"
            params = {
                "location": f"{location.longitude},{location.latitude}",
                "key": self.api_key
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("code") != "200":
                    raise WeatherAPIException(f"天气预报API返回错误: {data.get('code')}")
                
                daily_data = data.get("daily", [])
                forecasts = []
                
                for day_data in daily_data:
                    # 将预报数据转换为当前天气格式
                    weather_data = {
                        "temp": day_data.get("tempMax", "0"),
                        "feelsLike": day_data.get("tempMax", "0"),
                        "humidity": day_data.get("humidity", "0"),
                        "windSpeed": day_data.get("windSpeed", "0"),
                        "windDir": day_data.get("windDir", "无风向"),
                        "text": day_data.get("textDay", "未知"),
                        "vis": day_data.get("vis", "10"),
                        "pressure": day_data.get("pressure", "1013"),
                        "obsTime": day_data.get("fxDate", datetime.now().isoformat())
                    }
                    
                    forecasts.append(self._parse_weather_data(weather_data, location))
                
                return forecasts
                
        except Exception as e:
            logger.error(f"获取天气预报时发生错误: {e}")
            raise WeatherAPIException("获取天气预报失败")
    
    def _parse_weather_data(self, data: Dict[str, Any], location: LocationModel) -> WeatherModel:
        """解析天气数据"""
        try:
            # 映射天气状况
            condition_map = {
                "晴": WeatherCondition.SUNNY,
                "多云": WeatherCondition.CLOUDY,
                "阴": WeatherCondition.OVERCAST,
                "小雨": WeatherCondition.RAINY,
                "中雨": WeatherCondition.RAINY,
                "大雨": WeatherCondition.RAINY,
                "暴雨": WeatherCondition.STORMY,
                "雪": WeatherCondition.SNOWY,
                "雾": WeatherCondition.FOGGY,
            }
            
            weather_text = data.get("text", "未知")
            condition = WeatherCondition.SUNNY  # 默认值
            
            for key, value in condition_map.items():
                if key in weather_text:
                    condition = value
                    break
            
            return WeatherModel(
                location=location,
                temperature=float(data.get("temp", 0)),
                feels_like=float(data.get("feelsLike", data.get("temp", 0))),
                humidity=int(data.get("humidity", 0)),
                wind_speed=float(data.get("windSpeed", 0)),
                wind_direction=data.get("windDir", "无风向"),
                condition=condition,
                description=weather_text,
                visibility=float(data.get("vis", 10)),
                pressure=float(data.get("pressure", 1013)),
                update_time=datetime.fromisoformat(data.get("obsTime", datetime.now().isoformat()).replace("Z", "+00:00"))
            )
            
        except Exception as e:
            logger.error(f"解析天气数据时发生错误: {e}")
            raise WeatherAPIException("天气数据解析失败")
    
    async def get_weather_by_city(self, city_name: str) -> WeatherModel:
        """根据城市名称获取天气"""
        try:
            # 使用高德地图API获取城市坐标
            from app.services.map_service import MapService
            map_service = MapService()
            location = await map_service.geocode_address(city_name)
            return await self.get_current_weather(location)
        except Exception as e:
            logger.error(f"根据城市获取天气失败: {e}")
            raise WeatherAPIException(f"无法获取{city_name}的天气信息")
    
    async def get_weather_by_mcp(self, longitude: float, latitude: float, days: str = "now") -> Dict[str, Any]:
        """使用MCP服务获取和风天气数据"""
        try:
            # 这里可以集成MCP服务调用
            # 目前返回模拟数据，实际使用时需要调用MCP服务
            location_str = f"{longitude},{latitude}"
            
            # 模拟和风天气API响应格式
            if days == "now":
                return {
                    "code": "200",
                    "now": {
                        "temp": "22",
                        "feelsLike": "24",
                        "humidity": "65",
                        "windSpeed": "12",
                        "windDir": "东南风",
                        "text": "多云",
                        "vis": "10",
                        "pressure": "1013",
                        "obsTime": datetime.now().isoformat()
                    }
                }
            else:
                # 返回预报数据格式
                return {
                    "code": "200",
                    "daily": [
                        {
                            "tempMax": "25",
                            "tempMin": "18",
                            "humidity": "70",
                            "windSpeed": "15",
                            "windDir": "东南风",
                            "textDay": "多云",
                            "vis": "10",
                            "pressure": "1013",
                            "fxDate": datetime.now().strftime("%Y-%m-%d")
                        }
                    ]
                }
        except Exception as e:
            logger.error(f"MCP服务调用失败: {e}")
            raise WeatherAPIException("天气服务暂时不可用")


# 创建全局天气服务实例
weather_service = WeatherService()