from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.schemas import (
    RouteInfo,
    LocationModel,
    RouteRequest,
    TransportMode,
    ResponseModel
)
from app.services.map_service import map_service
from app.core.exceptions import MapAPIException
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/plan", response_model=ResponseModel, summary="路线规划")
async def plan_route(request: RouteRequest):
    """
    智能路线规划
    
    - **origin**: 起点位置信息
    - **destination**: 终点位置信息
    - **transport_mode**: 交通方式（driving/walking/cycling/transit）
    - **avoid_weather**: 是否考虑天气因素
    """
    try:
        route_info = None
        
        if request.transport_mode == TransportMode.DRIVING:
            route_info = await map_service.plan_driving_route(request.origin, request.destination)
        elif request.transport_mode == TransportMode.WALKING:
            route_info = await map_service.plan_walking_route(request.origin, request.destination)
        elif request.transport_mode == TransportMode.CYCLING:
            route_info = await map_service.plan_cycling_route(request.origin, request.destination)
        elif request.transport_mode == TransportMode.TRANSIT:
            # 公交路线需要城市信息
            origin_city = request.origin.city or "北京"
            dest_city = request.destination.city or origin_city
            route_info = await map_service.plan_transit_route(
                request.origin, request.destination, origin_city, dest_city
            )
        
        if not route_info:
            raise MapAPIException("路线规划失败")
        
        # 如果需要考虑天气因素，可以在这里添加天气影响分析
        if request.avoid_weather:
            route_info = await _add_weather_impact(route_info)
        
        return ResponseModel(
            success=True,
            message="路线规划成功",
            data=route_info
        )
        
    except MapAPIException as e:
        logger.error(f"路线规划失败: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"路线规划时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/plan/driving", response_model=ResponseModel, summary="驾车路线规划")
async def plan_driving_route(
    origin_lng: float = Query(..., description="起点经度", ge=-180, le=180),
    origin_lat: float = Query(..., description="起点纬度", ge=-90, le=90),
    dest_lng: float = Query(..., description="终点经度", ge=-180, le=180),
    dest_lat: float = Query(..., description="终点纬度", ge=-90, le=90),
    origin_address: Optional[str] = Query(None, description="起点地址"),
    dest_address: Optional[str] = Query(None, description="终点地址")
):
    """
    驾车路线规划
    
    - **origin_lng**: 起点经度
    - **origin_lat**: 起点纬度
    - **dest_lng**: 终点经度
    - **dest_lat**: 终点纬度
    - **origin_address**: 起点地址（可选）
    - **dest_address**: 终点地址（可选）
    """
    try:
        origin = LocationModel(
            longitude=origin_lng,
            latitude=origin_lat,
            address=origin_address
        )
        destination = LocationModel(
            longitude=dest_lng,
            latitude=dest_lat,
            address=dest_address
        )
        
        route_info = await map_service.plan_driving_route(origin, destination)
        
        return ResponseModel(
            success=True,
            message="驾车路线规划成功",
            data=route_info
        )
        
    except MapAPIException as e:
        logger.error(f"驾车路线规划失败: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"驾车路线规划时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/plan/walking", response_model=ResponseModel, summary="步行路线规划")
async def plan_walking_route(
    origin_lng: float = Query(..., description="起点经度", ge=-180, le=180),
    origin_lat: float = Query(..., description="起点纬度", ge=-90, le=90),
    dest_lng: float = Query(..., description="终点经度", ge=-180, le=180),
    dest_lat: float = Query(..., description="终点纬度", ge=-90, le=90),
    origin_address: Optional[str] = Query(None, description="起点地址"),
    dest_address: Optional[str] = Query(None, description="终点地址")
):
    """
    步行路线规划
    
    - **origin_lng**: 起点经度
    - **origin_lat**: 起点纬度
    - **dest_lng**: 终点经度
    - **dest_lat**: 终点纬度
    - **origin_address**: 起点地址（可选）
    - **dest_address**: 终点地址（可选）
    """
    try:
        origin = LocationModel(
            longitude=origin_lng,
            latitude=origin_lat,
            address=origin_address
        )
        destination = LocationModel(
            longitude=dest_lng,
            latitude=dest_lat,
            address=dest_address
        )
        
        route_info = await map_service.plan_walking_route(origin, destination)
        
        return ResponseModel(
            success=True,
            message="步行路线规划成功",
            data=route_info
        )
        
    except MapAPIException as e:
        logger.error(f"步行路线规划失败: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"步行路线规划时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/plan/cycling", response_model=ResponseModel, summary="骑行路线规划")
async def plan_cycling_route(
    origin_lng: float = Query(..., description="起点经度", ge=-180, le=180),
    origin_lat: float = Query(..., description="起点纬度", ge=-90, le=90),
    dest_lng: float = Query(..., description="终点经度", ge=-180, le=180),
    dest_lat: float = Query(..., description="终点纬度", ge=-90, le=90),
    origin_address: Optional[str] = Query(None, description="起点地址"),
    dest_address: Optional[str] = Query(None, description="终点地址")
):
    """
    骑行路线规划
    
    - **origin_lng**: 起点经度
    - **origin_lat**: 起点纬度
    - **dest_lng**: 终点经度
    - **dest_lat**: 终点纬度
    - **origin_address**: 起点地址（可选）
    - **dest_address**: 终点地址（可选）
    """
    try:
        origin = LocationModel(
            longitude=origin_lng,
            latitude=origin_lat,
            address=origin_address
        )
        destination = LocationModel(
            longitude=dest_lng,
            latitude=dest_lat,
            address=dest_address
        )
        
        route_info = await map_service.plan_cycling_route(origin, destination)
        
        return ResponseModel(
            success=True,
            message="骑行路线规划成功",
            data=route_info
        )
        
    except MapAPIException as e:
        logger.error(f"骑行路线规划失败: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"骑行路线规划时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/geocode", response_model=ResponseModel, summary="地址转坐标")
async def geocode_address(
    address: str = Query(..., description="地址", min_length=1),
    city: Optional[str] = Query(None, description="城市")
):
    """
    地址转坐标（地理编码）
    
    - **address**: 地址描述
    - **city**: 城市（可选）
    """
    try:
        location = await map_service.geocode_address(address, city)
        
        return ResponseModel(
            success=True,
            message="地理编码成功",
            data=location
        )
        
    except MapAPIException as e:
        logger.error(f"地理编码失败: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"地理编码时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/reverse-geocode", response_model=ResponseModel, summary="坐标转地址")
async def reverse_geocode(
    longitude: float = Query(..., description="经度", ge=-180, le=180),
    latitude: float = Query(..., description="纬度", ge=-90, le=90)
):
    """
    坐标转地址（逆地理编码）
    
    - **longitude**: 经度
    - **latitude**: 纬度
    """
    try:
        location = LocationModel(longitude=longitude, latitude=latitude)
        result = await map_service.reverse_geocode(location)
        
        return ResponseModel(
            success=True,
            message="逆地理编码成功",
            data=result
        )
        
    except MapAPIException as e:
        logger.error(f"逆地理编码失败: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"逆地理编码时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


async def _add_weather_impact(route_info: RouteInfo) -> RouteInfo:
    """添加天气影响分析"""
    try:
        # 这里可以根据路线和当前天气情况添加影响提示
        from app.services.weather_service import weather_service
        
        # 获取起点天气
        weather = await weather_service.get_current_weather(route_info.origin)
        
        weather_tips = []
        
        # 根据天气条件给出建议
        if weather.condition.value == "rainy":
            if route_info.transport_mode == TransportMode.WALKING:
                weather_tips.append("当前有雨，建议携带雨具或选择其他交通方式")
            elif route_info.transport_mode == TransportMode.CYCLING:
                weather_tips.append("雨天骑行请注意安全，路面湿滑")
            elif route_info.transport_mode == TransportMode.DRIVING:
                weather_tips.append("雨天驾驶请减速慢行，注意行车安全")
        
        if weather.temperature < 0:
            if route_info.transport_mode in [TransportMode.WALKING, TransportMode.CYCLING]:
                weather_tips.append("气温较低，请注意保暖")
        
        if weather.wind_speed > 20:
            if route_info.transport_mode == TransportMode.CYCLING:
                weather_tips.append("风力较大，骑行请注意安全")
        
        if weather_tips:
            route_info.weather_impact = "; ".join(weather_tips)
        
        return route_info
        
    except Exception as e:
        logger.warning(f"添加天气影响分析时发生错误: {e}")
        return route_info


@router.get("/search-places", response_model=ResponseModel, summary="搜索地点")
async def search_places(
    keywords: str = Query(..., description="搜索关键词", min_length=1),
    city: Optional[str] = Query(None, description="城市")
):
    """
    搜索地点（POI搜索）
    
    - **keywords**: 搜索关键词
    - **city**: 城市（可选）
    """
    try:
        locations = await map_service.search_places(keywords, city)
        
        return ResponseModel(
            success=True,
            message="地点搜索成功",
            data=locations
        )
        
    except MapAPIException as e:
        logger.error(f"地点搜索失败: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"地点搜索时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")