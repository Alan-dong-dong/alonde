"""穿搭推荐API端点"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from ....models.schemas import (
    OutfitRecommendationRequest, OutfitRecommendationResponse,
    ClothingItem, APIResponse
)
from ....services.outfit_service import OutfitService
from ....core.exceptions import APIException, DataValidationException

logger = logging.getLogger(__name__)

router = APIRouter()
outfit_service = OutfitService()

@router.post("/recommend", response_model=OutfitRecommendationResponse)
async def get_outfit_recommendation(request: OutfitRecommendationRequest):
    """
    根据天气信息获取穿搭推荐
    
    Args:
        request: 穿搭推荐请求，包含天气信息和用户偏好
    
    Returns:
        OutfitRecommendationResponse: 穿搭推荐响应
    
    Raises:
        HTTPException: 当推荐生成失败时
    """
    try:
        logger.info(f"收到穿搭推荐请求: 温度{request.weather_info.temperature}°C, 天气{request.weather_info.weather_text}")
        
        # 调用穿搭推荐服务
        response = await outfit_service.get_outfit_recommendation(request)
        
        logger.info(f"穿搭推荐生成成功，返回{len(response.data['recommendations'])}个推荐")
        return response
        
    except DataValidationException as e:
        logger.error(f"穿搭推荐数据验证失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except APIException as e:
        logger.error(f"穿搭推荐API异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"穿搭推荐未知异常: {str(e)}")
        raise HTTPException(status_code=500, detail="穿搭推荐服务暂时不可用")

@router.get("/categories", response_model=APIResponse)
async def get_clothing_categories():
    """
    获取服装分类列表
    
    Returns:
        APIResponse: 包含服装分类列表的响应
    """
    try:
        categories = outfit_service.get_clothing_categories()
        
        return APIResponse(
            success=True,
            message="获取服装分类成功",
            data={"categories": categories}
        )
        
    except Exception as e:
        logger.error(f"获取服装分类失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取服装分类失败")

@router.get("/categories/{category}/items", response_model=APIResponse)
async def get_clothes_by_category(category: str):
    """
    根据分类获取服装列表
    
    Args:
        category: 服装分类名称
    
    Returns:
        APIResponse: 包含该分类下所有服装的响应
    """
    try:
        clothes = outfit_service.get_clothes_by_category(category)
        
        if not clothes:
            raise HTTPException(status_code=404, detail=f"分类'{category}'不存在或没有服装")
        
        return APIResponse(
            success=True,
            message=f"获取{category}分类服装成功",
            data={
                "category": category,
                "items": [item.dict() for item in clothes]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取分类服装失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取分类服装失败")

@router.post("/recommend/simple", response_model=OutfitRecommendationResponse)
async def get_simple_outfit_recommendation(
    temperature: float,
    weather_text: str,
    humidity: int = 50,
    wind_speed: float = 10.0
):
    """
    简化的穿搭推荐接口
    
    Args:
        temperature: 温度（摄氏度）
        weather_text: 天气描述
        humidity: 湿度百分比，默认50
        wind_speed: 风速（km/h），默认10.0
    
    Returns:
        OutfitRecommendationResponse: 穿搭推荐响应
    """
    try:
        # 构造天气信息
        from ....models.schemas import WeatherInfo
        
        weather_info = WeatherInfo(
            temperature=temperature,
            weather_text=weather_text,
            humidity=humidity,
            wind_speed=wind_speed,
            pressure=1013.25,  # 标准大气压
            visibility=10.0,   # 默认能见度
            uv_index=5         # 默认紫外线指数
        )
        
        request = OutfitRecommendationRequest(
            weather_info=weather_info,
            user_preferences={}
        )
        
        logger.info(f"收到简化穿搭推荐请求: 温度{temperature}°C, 天气{weather_text}")
        
        # 调用穿搭推荐服务
        response = await outfit_service.get_outfit_recommendation(request)
        
        logger.info(f"简化穿搭推荐生成成功")
        return response
        
    except Exception as e:
        logger.error(f"简化穿搭推荐失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"穿搭推荐失败: {str(e)}")