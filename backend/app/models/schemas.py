from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ResponseModel(BaseModel):
    """通用响应模型"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None


class LocationModel(BaseModel):
    """位置信息模型"""
    longitude: float = Field(..., description="经度", ge=-180, le=180)
    latitude: float = Field(..., description="纬度", ge=-90, le=90)
    address: Optional[str] = Field(None, description="地址描述")
    city: Optional[str] = Field(None, description="城市")


class WeatherCondition(str, Enum):
    """天气状况枚举"""
    SUNNY = "sunny"          # 晴天
    CLOUDY = "cloudy"        # 多云
    OVERCAST = "overcast"    # 阴天
    RAINY = "rainy"          # 雨天
    SNOWY = "snowy"          # 雪天
    FOGGY = "foggy"          # 雾天
    STORMY = "stormy"        # 暴风雨


class WeatherModel(BaseModel):
    """天气信息模型"""
    location: LocationModel
    temperature: float = Field(..., description="温度(摄氏度)")
    feels_like: float = Field(..., description="体感温度(摄氏度)")
    humidity: int = Field(..., description="湿度(%)", ge=0, le=100)
    wind_speed: float = Field(..., description="风速(km/h)", ge=0)
    wind_direction: str = Field(..., description="风向")
    condition: WeatherCondition = Field(..., description="天气状况")
    description: str = Field(..., description="天气描述")
    uv_index: Optional[int] = Field(None, description="紫外线指数", ge=0, le=11)
    visibility: Optional[float] = Field(None, description="能见度(km)")
    pressure: Optional[float] = Field(None, description="气压(hPa)")
    update_time: datetime = Field(..., description="更新时间")


class OutfitType(str, Enum):
    """服装类型枚举"""
    TOP = "top"              # 上衣
    BOTTOM = "bottom"        # 下装
    OUTERWEAR = "outerwear"  # 外套
    FOOTWEAR = "footwear"    # 鞋类
    ACCESSORY = "accessory"  # 配饰


class ClothingItem(BaseModel):
    """服装单品模型"""
    name: str = Field(..., description="服装名称")
    type: OutfitType = Field(..., description="服装类型")
    description: str = Field(..., description="服装描述")
    suitable_temp_min: Optional[float] = Field(None, description="适宜最低温度")
    suitable_temp_max: Optional[float] = Field(None, description="适宜最高温度")
    weather_conditions: List[WeatherCondition] = Field(default=[], description="适宜天气条件")


class OutfitRecommendation(BaseModel):
    """穿搭推荐模型"""
    weather: WeatherModel
    recommended_items: List[ClothingItem] = Field(..., description="推荐服装")
    style_tips: List[str] = Field(default=[], description="搭配建议")
    comfort_score: float = Field(..., description="舒适度评分", ge=0, le=10)
    reason: str = Field(..., description="推荐理由")


class TransportMode(str, Enum):
    """交通方式枚举"""
    WALKING = "walking"      # 步行
    CYCLING = "cycling"      # 骑行
    DRIVING = "driving"      # 驾车
    TRANSIT = "transit"      # 公共交通


class RouteStep(BaseModel):
    """路线步骤模型"""
    instruction: str = Field(..., description="导航指令")
    distance: float = Field(..., description="距离(米)")
    duration: int = Field(..., description="预计时间(秒)")
    polyline: Optional[str] = Field(None, description="路径坐标")


class RouteInfo(BaseModel):
    """路线信息模型"""
    origin: LocationModel = Field(..., description="起点")
    destination: LocationModel = Field(..., description="终点")
    transport_mode: TransportMode = Field(..., description="交通方式")
    total_distance: float = Field(..., description="总距离(米)")
    total_duration: int = Field(..., description="总时间(秒)")
    steps: List[RouteStep] = Field(default=[], description="路线步骤")
    polyline: Optional[str] = Field(None, description="完整路径坐标")
    weather_impact: Optional[str] = Field(None, description="天气影响提示")


class SmartTravelPlan(BaseModel):
    """智能出行计划模型"""
    weather: WeatherModel
    outfit_recommendation: OutfitRecommendation
    route_info: RouteInfo
    travel_tips: List[str] = Field(default=[], description="出行建议")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


# 请求模型
class WeatherRequest(BaseModel):
    """天气查询请求"""
    location: LocationModel


class OutfitRequest(BaseModel):
    """穿搭推荐请求"""
    weather: WeatherModel
    user_preferences: Optional[Dict[str, Any]] = Field(default={}, description="用户偏好")


class RouteRequest(BaseModel):
    """路线规划请求"""
    origin: LocationModel
    destination: LocationModel
    transport_mode: TransportMode = TransportMode.DRIVING
    avoid_weather: bool = Field(default=True, description="是否考虑天气因素")


class OutfitRecommendationRequest(BaseModel):
    """穿搭推荐请求"""
    location: LocationModel
    user_preferences: Optional[Dict[str, Any]] = Field(default={}, description="用户偏好")


class SmartTravelRequest(BaseModel):
    """智能出行规划请求"""
    origin: LocationModel
    destination: LocationModel
    transport_mode: TransportMode = TransportMode.DRIVING
    user_preferences: Optional[Dict[str, Any]] = Field(default={}, description="用户偏好")


class SmartTravelPlanRequest(BaseModel):
    """智能出行计划请求"""
    origin: str = Field(..., description="出发地")
    destination: str = Field(..., description="目的地")
    transport_mode: str = Field(default="driving", description="交通方式")
    preferred_arrival_time: Optional[str] = Field(None, description="期望到达时间")
    user_preferences: Optional[Dict[str, Any]] = Field(default={}, description="用户偏好")


# 响应模型
class APIResponse(BaseModel):
    """通用API响应"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None


class WeatherResponse(BaseModel):
    """天气查询响应"""
    success: bool = True
    message: str = "获取天气信息成功"
    data: Optional[WeatherModel] = None


class OutfitRecommendationResponse(BaseModel):
    """穿搭推荐响应"""
    success: bool = True
    message: str = "获取穿搭推荐成功"
    data: Optional[OutfitRecommendation] = None


class RouteResponse(BaseModel):
    """路线规划响应"""
    success: bool = True
    message: str = "路线规划成功"
    data: Optional[RouteInfo] = None


class SmartTravelPlanResponse(BaseModel):
    """智能出行计划响应"""
    success: bool = True
    message: str = "智能出行计划创建成功"
    data: Optional[Dict[str, Any]] = None