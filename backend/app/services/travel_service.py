"""智能出行规划服务模块"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta

from ..models.schemas import (
    WeatherModel, RouteInfo, OutfitRecommendation,
    SmartTravelPlan, SmartTravelPlanRequest, SmartTravelPlanResponse,
    OutfitRecommendationRequest, RouteRequest
)
from ..core.exceptions import APIException, DataValidationException
from .weather_service import WeatherService
from .map_service import MapService
from .outfit_service import OutfitService

logger = logging.getLogger(__name__)

class TravelService:
    """智能出行规划服务类"""
    
    def __init__(self):
        """初始化智能出行规划服务"""
        self.weather_service = WeatherService()
        self.map_service = MapService()
        self.outfit_service = OutfitService()
    
    def _analyze_weather_impact_on_route(self, weather_info: WeatherModel, route_info: RouteInfo) -> Dict[str, Any]:
        """分析天气对路线的影响"""
        impact_analysis = {
            "overall_impact": "低",
            "recommendations": [],
            "warnings": [],
            "travel_time_adjustment": 1.0  # 时间调整系数
        }
        
        # 降雨影响
        if "雨" in weather_info.description:
            impact_analysis["overall_impact"] = "中"
            impact_analysis["recommendations"].append("雨天路滑，建议降低车速，增加跟车距离")
            impact_analysis["travel_time_adjustment"] = 1.2
            
            if route_info.transport_mode == "walking":
                impact_analysis["recommendations"].append("步行时请携带雨具，选择有遮挡的路线")
                impact_analysis["travel_time_adjustment"] = 1.3
            elif route_info.transport_mode == "bicycling":
                impact_analysis["warnings"].append("雨天骑行危险性较高，建议改用其他交通方式")
                impact_analysis["travel_time_adjustment"] = 1.5
        
        # 降雪影响
        if "雪" in weather_info.description:
            impact_analysis["overall_impact"] = "高"
            impact_analysis["warnings"].append("雪天路面湿滑，出行需格外小心")
            impact_analysis["recommendations"].append("建议使用防滑链，携带应急用品")
            impact_analysis["travel_time_adjustment"] = 1.5
            
            if route_info.transport_mode in ["walking", "bicycling"]:
                impact_analysis["warnings"].append("雪天步行/骑行极其危险，强烈建议改用公共交通")
                impact_analysis["travel_time_adjustment"] = 2.0
        
        # 大风影响
        if weather_info.wind_speed > 50:
            impact_analysis["overall_impact"] = "高" if impact_analysis["overall_impact"] != "高" else "高"
            impact_analysis["warnings"].append("大风天气，注意高空坠物")
            
            if route_info.transport_mode == "bicycling":
                impact_analysis["warnings"].append("大风天气骑行困难且危险")
                impact_analysis["travel_time_adjustment"] = max(impact_analysis["travel_time_adjustment"], 1.4)
        
        # 极端温度影响
        if weather_info.temperature > 35:
            impact_analysis["recommendations"].append("高温天气，避免长时间户外活动，及时补充水分")
            if route_info.transport_mode in ["walking", "bicycling"]:
                impact_analysis["recommendations"].append("建议选择阴凉路线，携带防晒用品")
        elif weather_info.temperature < -10:
            impact_analysis["recommendations"].append("严寒天气，注意保暖，避免长时间户外暴露")
            if route_info.transport_mode in ["walking", "bicycling"]:
                impact_analysis["warnings"].append("严寒天气户外活动风险较高")
        
        # 能见度影响
        if weather_info.visibility < 1.0:
            impact_analysis["overall_impact"] = "高"
            impact_analysis["warnings"].append("能见度极低，出行需格外谨慎")
            impact_analysis["travel_time_adjustment"] = max(impact_analysis["travel_time_adjustment"], 1.6)
        elif weather_info.visibility < 5.0:
            impact_analysis["overall_impact"] = "中" if impact_analysis["overall_impact"] == "低" else impact_analysis["overall_impact"]
            impact_analysis["recommendations"].append("能见度较低，注意开启车灯，保持安全距离")
            impact_analysis["travel_time_adjustment"] = max(impact_analysis["travel_time_adjustment"], 1.2)
        
        return impact_analysis
    
    def _calculate_optimal_departure_time(self, 
                                        route_info: RouteInfo, 
                                        weather_impact: Dict[str, Any],
                                        preferred_arrival_time: Optional[str] = None) -> Dict[str, Any]:
        """计算最佳出发时间"""
        base_duration = route_info.duration
        adjusted_duration = int(base_duration * weather_impact["travel_time_adjustment"])
        
        # 添加缓冲时间
        buffer_time = max(10, int(adjusted_duration * 0.1))  # 至少10分钟缓冲
        total_duration = adjusted_duration + buffer_time
        
        current_time = datetime.now()
        
        if preferred_arrival_time:
            try:
                # 解析期望到达时间
                arrival_time = datetime.strptime(preferred_arrival_time, "%H:%M")
                arrival_time = arrival_time.replace(
                    year=current_time.year,
                    month=current_time.month,
                    day=current_time.day
                )
                
                # 如果时间已过，设为明天
                if arrival_time < current_time:
                    arrival_time += timedelta(days=1)
                
                optimal_departure = arrival_time - timedelta(minutes=total_duration)
            except ValueError:
                # 如果时间格式错误，使用当前时间
                optimal_departure = current_time
        else:
            optimal_departure = current_time
        
        return {
            "optimal_departure_time": optimal_departure.strftime("%H:%M"),
            "estimated_arrival_time": (optimal_departure + timedelta(minutes=total_duration)).strftime("%H:%M"),
            "base_duration_minutes": base_duration,
            "adjusted_duration_minutes": adjusted_duration,
            "buffer_time_minutes": buffer_time,
            "total_duration_minutes": total_duration
        }
    
    def _generate_travel_tips(self, 
                            weather_info: WeatherModel, 
                            route_info: RouteInfo,
                            weather_impact: Dict[str, Any]) -> List[str]:
        """生成出行小贴士"""
        tips = []
        
        # 基础出行建议
        tips.append(f"预计行程时间{route_info.duration}分钟，建议提前{max(10, int(route_info.duration * 0.1))}分钟出发")
        
        # 天气相关建议
        if weather_info.temperature > 30:
            tips.append("高温天气，建议携带充足的水和防晒用品")
        elif weather_info.temperature < 0:
            tips.append("气温较低，注意保暖，路面可能结冰")
        
        if weather_info.humidity > 80:
            tips.append("湿度较高，容易感到闷热，选择透气衣物")
        
        if weather_info.wind_speed > 30:
            tips.append("风力较大，注意稳定行走，避免高空坠物")
        
        # 交通方式建议
        if route_info.transport_mode == "driving":
            tips.append("驾车出行，请遵守交通规则，注意行车安全")
            if "雨" in weather_info.description or "雪" in weather_info.description:
                tips.append("路面湿滑，请降低车速，增加跟车距离")
        elif route_info.transport_mode == "walking":
            tips.append("步行出行，请注意交通安全，选择人行道")
            if weather_info.temperature > 25:
                tips.append("天气较热，可选择阴凉路线，适当休息")
        elif route_info.transport_mode == "bicycling":
            tips.append("骑行出行，请佩戴安全头盔，注意交通安全")
            if weather_info.wind_speed > 40:
                tips.append("风力较大，骑行时请格外小心")
        elif route_info.transport_mode == "transit":
            tips.append("公共交通出行，请提前查看班次时间")
        
        # 添加天气影响的建议
        tips.extend(weather_impact["recommendations"])
        
        return tips
    
    async def create_smart_travel_plan(self, request: SmartTravelPlanRequest) -> SmartTravelPlanResponse:
        """创建智能出行计划"""
        try:
            logger.info(f"开始创建智能出行计划: {request.origin} -> {request.destination}")
            
            # 1. 获取路线信息
            route_request = RouteRequest(
                origin=request.origin,
                destination=request.destination,
                transport_mode=request.transport_mode or "driving"
            )
            
            route_response = await self.map_service.plan_route(route_request)
            if not route_response.success or not route_response.data:
                raise APIException("路线规划失败")
            
            route_info = RouteInfo(**route_response.data)
            
            # 2. 获取目的地天气信息
            try:
                # 尝试通过坐标获取天气
                dest_coords = request.destination.split(",")
                if len(dest_coords) == 2:
                    weather_response = await self.weather_service.get_current_weather_by_coords(
                        float(dest_coords[1]), float(dest_coords[0])  # 纬度，经度
                    )
                else:
                    # 如果不是坐标，尝试作为城市名获取天气
                    weather_response = await self.weather_service.get_current_weather_by_city(request.destination)
                
                if not weather_response.success:
                    raise APIException("天气信息获取失败")
                
                weather_info = WeatherInfo(**weather_response.data)
                
            except Exception as e:
                logger.warning(f"获取目的地天气失败，使用默认天气: {str(e)}")
                # 使用默认天气信息
                weather_info = WeatherInfo(
                    temperature=20.0,
                    weather_text="多云",
                    humidity=60,
                    wind_speed=15.0,
                    pressure=1013.25,
                    visibility=10.0,
                    uv_index=5
                )
            
            # 3. 获取穿搭推荐
            outfit_request = OutfitRecommendationRequest(
                weather_info=weather_info,
                user_preferences=request.user_preferences or {}
            )
            
            outfit_response = await self.outfit_service.get_outfit_recommendation(outfit_request)
            if not outfit_response.success:
                raise APIException("穿搭推荐生成失败")
            
            outfit_recommendations = outfit_response.data["recommendations"]
            
            # 4. 分析天气对路线的影响
            weather_impact = self._analyze_weather_impact_on_route(weather_info, route_info)
            
            # 5. 计算最佳出发时间
            timing_info = self._calculate_optimal_departure_time(
                route_info, weather_impact, request.preferred_arrival_time
            )
            
            # 6. 生成出行小贴士
            travel_tips = self._generate_travel_tips(weather_info, route_info, weather_impact)
            
            # 7. 创建智能出行计划
            travel_plan = SmartTravelPlan(
                plan_id=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                origin=request.origin,
                destination=request.destination,
                transport_mode=route_info.transport_mode,
                route_info=route_info,
                weather_info=weather_info,
                outfit_recommendations=outfit_recommendations,
                optimal_departure_time=timing_info["optimal_departure_time"],
                estimated_arrival_time=timing_info["estimated_arrival_time"],
                total_duration=timing_info["total_duration_minutes"],
                weather_impact_level=weather_impact["overall_impact"],
                travel_tips=travel_tips
            )
            
            logger.info(f"智能出行计划创建成功: {travel_plan.plan_id}")
            
            return SmartTravelPlanResponse(
                success=True,
                message="智能出行计划创建成功",
                data={
                    "travel_plan": travel_plan,
                    "weather_impact_analysis": weather_impact,
                    "timing_details": timing_info,
                    "outfit_advice": outfit_response.data.get("advice", "")
                }
            )
            
        except APIException:
            raise
        except Exception as e:
            logger.error(f"创建智能出行计划失败: {str(e)}")
            raise APIException(f"创建智能出行计划失败: {str(e)}")
    
    async def get_weather_forecast_for_route(self, origin: str, destination: str, days: int = 3) -> Dict[str, Any]:
        """获取路线沿途天气预报"""
        try:
            forecasts = {}
            
            # 获取起点天气预报
            try:
                origin_coords = origin.split(",")
                if len(origin_coords) == 2:
                    origin_forecast = await self.weather_service.get_weather_forecast_by_coords(
                        float(origin_coords[1]), float(origin_coords[0]), days
                    )
                else:
                    origin_forecast = await self.weather_service.get_weather_forecast_by_city(origin, days)
                
                if origin_forecast.success:
                    forecasts["origin"] = origin_forecast.data
            except Exception as e:
                logger.warning(f"获取起点天气预报失败: {str(e)}")
            
            # 获取终点天气预报
            try:
                dest_coords = destination.split(",")
                if len(dest_coords) == 2:
                    dest_forecast = await self.weather_service.get_weather_forecast_by_coords(
                        float(dest_coords[1]), float(dest_coords[0]), days
                    )
                else:
                    dest_forecast = await self.weather_service.get_weather_forecast_by_city(destination, days)
                
                if dest_forecast.success:
                    forecasts["destination"] = dest_forecast.data
            except Exception as e:
                logger.warning(f"获取终点天气预报失败: {str(e)}")
            
            return {
                "success": True,
                "forecasts": forecasts,
                "message": "天气预报获取成功"
            }
            
        except Exception as e:
            logger.error(f"获取路线天气预报失败: {str(e)}")
            return {
                "success": False,
                "message": f"获取天气预报失败: {str(e)}",
                "forecasts": {}
            }