from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.models.schemas import (
    WeatherModel, 
    LocationModel, 
    WeatherRequest, 
    ResponseModel
)
from app.services.weather_service import weather_service
from app.services.hefeng_weather_service import hefeng_weather_service
from app.core.exceptions import WeatherAPIException
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/current", response_model=ResponseModel, summary="获取当前天气")
async def get_current_weather(request: WeatherRequest):
    """
    获取指定位置的当前天气信息
    
    - **location**: 位置信息（经纬度）
    """
    try:
        weather_data = await weather_service.get_current_weather(request.location)
        return ResponseModel(
            success=True,
            message="获取天气信息成功",
            data=weather_data
        )
    except WeatherAPIException as e:
        logger.error(f"获取天气信息失败: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"获取天气信息时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/current/by-coordinates", response_model=ResponseModel, summary="根据坐标获取天气")
async def get_weather_by_coordinates(
    longitude: float = Query(..., description="经度", ge=-180, le=180),
    latitude: float = Query(..., description="纬度", ge=-90, le=90),
    address: Optional[str] = Query(None, description="地址描述")
):
    """
    根据经纬度坐标获取当前天气信息
    
    - **longitude**: 经度
    - **latitude**: 纬度
    - **address**: 地址描述（可选）
    """
    try:
        location = LocationModel(
            longitude=longitude,
            latitude=latitude,
            address=address
        )
        weather_data = await weather_service.get_current_weather(location)
        return ResponseModel(
            success=True,
            message="获取天气信息成功",
            data=weather_data
        )
    except WeatherAPIException as e:
        logger.error(f"获取天气信息失败: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"获取天气信息时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/current/by-city", response_model=ResponseModel, summary="根据城市获取天气")
async def get_weather_by_city(
    city: str = Query(..., description="城市名称", min_length=1)
):
    """
    根据城市名称获取当前天气信息
    
    - **city**: 城市名称
    """
    try:
        weather_data = await weather_service.get_weather_by_city(city)
        return ResponseModel(
            success=True,
            message=f"获取{city}天气信息成功",
            data=weather_data
        )
    except WeatherAPIException as e:
        logger.error(f"获取{city}天气信息失败: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"获取{city}天气信息时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/forecast", response_model=ResponseModel, summary="获取天气预报")
async def get_weather_forecast(
    request: WeatherRequest,
    days: int = Query(3, description="预报天数", ge=1, le=7)
):
    """
    获取指定位置的天气预报
    
    - **location**: 位置信息（经纬度）
    - **days**: 预报天数（1-7天）
    """
    try:
        forecast_data = await weather_service.get_weather_forecast(request.location, days)
        return ResponseModel(
            success=True,
            message=f"获取{days}天天气预报成功",
            data=forecast_data
        )
    except WeatherAPIException as e:
        logger.error(f"获取天气预报失败: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"获取天气预报时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/hefeng", response_model=ResponseModel, summary="使用和风天气API获取天气")
async def get_hefeng_weather(
    longitude: float = Query(..., description="经度", ge=-180, le=180),
    latitude: float = Query(..., description="纬度", ge=-90, le=90),
    days: str = Query("now", description="预报类型：now(实时), 3d(3天预报), 7d(7天预报)")
):
    """
    直接使用和风天气API获取天气信息
    
    - **longitude**: 经度
    - **latitude**: 纬度  
    - **days**: 预报类型
    """
    try:
        # 使用和风天气MCP服务获取数据
        weather_data = await hefeng_weather_service.get_weather_data(longitude, latitude, days)
        
        if weather_data.get("success"):
            return ResponseModel(
                success=True,
                message="获取和风天气数据成功",
                data=weather_data.get("data")
            )
        else:
            raise WeatherAPIException(weather_data.get("error", "获取天气数据失败"))
            
    except WeatherAPIException as e:
        logger.error(f"获取和风天气数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"获取和风天气数据时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/hefeng/structured", response_model=ResponseModel, summary="使用和风天气API获取结构化天气数据")
async def get_hefeng_structured_weather(
    longitude: float = Query(..., description="经度", ge=-180, le=180),
    latitude: float = Query(..., description="纬度", ge=-90, le=90),
    address: Optional[str] = Query(None, description="地址描述")
):
    """
    使用和风天气API获取结构化的天气数据
    
    - **longitude**: 经度
    - **latitude**: 纬度
    - **address**: 地址描述（可选）
    """
    try:
        location = LocationModel(
            longitude=longitude,
            latitude=latitude,
            address=address or f"位置({longitude}, {latitude})"
        )
        
        # 使用和风天气服务获取结构化数据
        weather_model = await hefeng_weather_service.get_current_weather(location)
        
        return ResponseModel(
            success=True,
            message="获取和风天气结构化数据成功",
            data=weather_model
        )
        
    except WeatherAPIException as e:
        logger.error(f"获取和风天气结构化数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"获取和风天气结构化数据时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")
 
 
@router.get("/forecast/by-coordinates", response_model=ResponseModel, summary="根据坐标获取天气预报")
async def get_forecast_by_coordinates(
    longitude: float = Query(..., description="经度", ge=-180, le=180),
    latitude: float = Query(..., description="纬度", ge=-90, le=90),
    days: int = Query(3, description="预报天数", ge=1, le=7),
    address: Optional[str] = Query(None, description="地址描述")
):
    """
    根据经纬度坐标获取天气预报
    
    - **longitude**: 经度
    - **latitude**: 纬度
    - **days**: 预报天数（1-7天）
    - **address**: 地址描述（可选）
    """
    try:
        location = LocationModel(
            longitude=longitude,
            latitude=latitude,
            address=address
        )
        forecast_data = await weather_service.get_weather_forecast(location, days)
        return ResponseModel(
            success=True,
            message=f"获取{days}天天气预报成功",
            data=forecast_data
        )
    except WeatherAPIException as e:
        logger.error(f"获取天气预报失败: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"获取天气预报时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")