import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.config import settings
from app.core.exceptions import WeatherAPIException
from app.models.schemas import WeatherModel, LocationModel, WeatherCondition

logger = logging.getLogger(__name__)


class HefengWeatherService:
    """和风天气MCP服务集成类"""
    
    def __init__(self):
        self.service_name = "mcp.config.usrlocalmcp.hefeng-weather"
        self.tool_name = "get-weather"
    
    async def get_weather_data(self, longitude: float, latitude: float, days: str = "now") -> Dict[str, Any]:
        """通过MCP服务获取和风天气数据"""
        try:
            # 构建位置字符串
            location_str = f"{longitude},{latitude}"
            
            # 这里应该调用MCP服务，但由于当前环境限制，我们返回模拟数据
            # 实际部署时需要集成真实的MCP服务调用
            
            if days == "now":
                # 模拟实时天气数据
                return {
                    "success": True,
                    "data": {
                        "location": location_str,
                        "now": {
                            "obsTime": datetime.now().isoformat(),
                            "temp": "22",
                            "feelsLike": "24",
                            "icon": "101",
                            "text": "多云",
                            "wind360": "225",
                            "windDir": "西南风",
                            "windScale": "3",
                            "windSpeed": "12",
                            "humidity": "65",
                            "precip": "0.0",
                            "pressure": "1013",
                            "vis": "10",
                            "cloud": "40",
                            "dew": "15"
                        },
                        "refer": {
                            "sources": ["QWeather"],
                            "license": ["QWeather Developers License"]
                        }
                    }
                }
            elif days in ["3d", "7d", "10d", "15d"]:
                # 模拟预报数据
                forecast_days = int(days.replace('d', ''))
                daily_data = []
                
                for i in range(forecast_days):
                    date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    date = date.replace(day=date.day + i)
                    
                    daily_data.append({
                        "fxDate": date.strftime("%Y-%m-%d"),
                        "sunrise": "06:30",
                        "sunset": "18:45",
                        "moonrise": "20:15",
                        "moonset": "07:30",
                        "moonPhase": "上弦月",
                        "moonPhaseIcon": "803",
                        "tempMax": str(25 - i),
                        "tempMin": str(15 - i),
                        "iconDay": "101",
                        "textDay": "多云",
                        "iconNight": "150",
                        "textNight": "晴",
                        "wind360Day": "225",
                        "windDirDay": "西南风",
                        "windScaleDay": "3",
                        "windSpeedDay": "15",
                        "wind360Night": "225",
                        "windDirNight": "西南风",
                        "windScaleNight": "2",
                        "windSpeedNight": "8",
                        "humidity": str(70 - i * 5),
                        "precip": "0.0",
                        "pressure": "1013",
                        "vis": "10",
                        "cloud": "30",
                        "uvIndex": "5"
                    })
                
                return {
                    "success": True,
                    "data": {
                        "location": location_str,
                        "daily": daily_data,
                        "refer": {
                            "sources": ["QWeather"],
                            "license": ["QWeather Developers License"]
                        }
                    }
                }
            else:
                raise WeatherAPIException(f"不支持的预报类型: {days}")
                
        except Exception as e:
            logger.error(f"获取和风天气数据失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def parse_to_weather_model(self, data: Dict[str, Any], location: LocationModel) -> WeatherModel:
        """将和风天气数据转换为WeatherModel"""
        try:
            if not data.get("success") or "now" not in data.get("data", {}):
                raise WeatherAPIException("无效的天气数据")
            
            now_data = data["data"]["now"]
            
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
            
            weather_text = now_data.get("text", "未知")
            condition = WeatherCondition.SUNNY  # 默认值
            
            for key, value in condition_map.items():
                if key in weather_text:
                    condition = value
                    break
            
            return WeatherModel(
                location=location,
                temperature=float(now_data.get("temp", 0)),
                feels_like=float(now_data.get("feelsLike", now_data.get("temp", 0))),
                humidity=int(now_data.get("humidity", 0)),
                wind_speed=float(now_data.get("windSpeed", 0)),
                wind_direction=now_data.get("windDir", "无风向"),
                condition=condition,
                description=weather_text,
                visibility=float(now_data.get("vis", 10)),
                pressure=float(now_data.get("pressure", 1013)),
                update_time=datetime.fromisoformat(now_data.get("obsTime", datetime.now().isoformat()).replace("Z", "+00:00"))
            )
            
        except Exception as e:
            logger.error(f"解析和风天气数据失败: {e}")
            raise WeatherAPIException("天气数据解析失败")
    
    async def get_current_weather(self, location: LocationModel) -> WeatherModel:
        """获取当前天气"""
        try:
            weather_data = await self.get_weather_data(
                location.longitude, 
                location.latitude, 
                "now"
            )
            
            return await self.parse_to_weather_model(weather_data, location)
            
        except Exception as e:
            logger.error(f"获取当前天气失败: {e}")
            raise WeatherAPIException("获取天气信息失败")


# 创建全局和风天气服务实例
hefeng_weather_service = HefengWeatherService()