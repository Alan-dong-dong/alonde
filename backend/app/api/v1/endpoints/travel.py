"""智能出行规划API端点"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging

from ....models.schemas import (
    SmartTravelPlanRequest, SmartTravelPlanResponse, APIResponse
)
from ....services.travel_service import TravelService
from ....core.exceptions import APIException, DataValidationException

logger = logging.getLogger(__name__)

router = APIRouter()
travel_service = TravelService()

@router.post("/plan", response_model=SmartTravelPlanResponse)
async def create_smart_travel_plan(request: SmartTravelPlanRequest):
    """
    创建智能出行计划
    
    Args:
        request: 智能出行计划请求
    
    Returns:
        SmartTravelPlanResponse: 智能出行计划响应
    
    Raises:
        HTTPException: 当计划创建失败时
    """
    try:
        logger.info(f"收到智能出行计划请求: {request.origin} -> {request.destination}")
        
        # 调用智能出行规划服务
        response = await travel_service.create_smart_travel_plan(request)
        
        logger.info(f"智能出行计划创建成功: {response.data['travel_plan'].plan_id}")
        return response
        
    except DataValidationException as e:
        logger.error(f"智能出行计划数据验证失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except APIException as e:
        logger.error(f"智能出行计划API异常: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"智能出行计划未知异常: {str(e)}")
        raise HTTPException(status_code=500, detail="智能出行规划服务暂时不可用")

@router.get("/plan/simple", response_model=SmartTravelPlanResponse)
async def create_simple_travel_plan(
    origin: str = Query(..., description="出发地（地址或经纬度）"),
    destination: str = Query(..., description="目的地（地址或经纬度）"),
    transport_mode: Optional[str] = Query("driving", description="交通方式：driving, walking, bicycling, transit"),
    preferred_arrival_time: Optional[str] = Query(None, description="期望到达时间（HH:MM格式）")
):
    """
    简化的智能出行计划接口
    
    Args:
        origin: 出发地
        destination: 目的地
        transport_mode: 交通方式
        preferred_arrival_time: 期望到达时间
    
    Returns:
        SmartTravelPlanResponse: 智能出行计划响应
    """
    try:
        # 构造请求对象
        request = SmartTravelPlanRequest(
            origin=origin,
            destination=destination,
            transport_mode=transport_mode,
            preferred_arrival_time=preferred_arrival_time,
            user_preferences={}
        )
        
        logger.info(f"收到简化智能出行计划请求: {origin} -> {destination}")
        
        # 调用智能出行规划服务
        response = await travel_service.create_smart_travel_plan(request)
        
        logger.info(f"简化智能出行计划创建成功")
        return response
        
    except Exception as e:
        logger.error(f"简化智能出行计划失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"智能出行规划失败: {str(e)}")

@router.get("/weather-forecast", response_model=APIResponse)
async def get_route_weather_forecast(
    origin: str = Query(..., description="出发地（地址或经纬度）"),
    destination: str = Query(..., description="目的地（地址或经纬度）"),
    days: int = Query(3, ge=1, le=7, description="预报天数（1-7天）")
):
    """
    获取路线沿途天气预报
    
    Args:
        origin: 出发地
        destination: 目的地
        days: 预报天数
    
    Returns:
        APIResponse: 包含天气预报的响应
    """
    try:
        logger.info(f"获取路线天气预报: {origin} -> {destination}, {days}天")
        
        # 调用天气预报服务
        forecast_data = await travel_service.get_weather_forecast_for_route(origin, destination, days)
        
        if forecast_data["success"]:
            return APIResponse(
                success=True,
                message=forecast_data["message"],
                data=forecast_data["forecasts"]
            )
        else:
            raise HTTPException(status_code=500, detail=forecast_data["message"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取路线天气预报失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取天气预报失败")

@router.post("/plan/batch", response_model=APIResponse)
async def create_batch_travel_plans(requests: List[SmartTravelPlanRequest]):
    """
    批量创建智能出行计划
    
    Args:
        requests: 智能出行计划请求列表
    
    Returns:
        APIResponse: 包含所有计划的响应
    """
    try:
        if len(requests) > 10:
            raise HTTPException(status_code=400, detail="批量请求数量不能超过10个")
        
        logger.info(f"收到批量智能出行计划请求，共{len(requests)}个")
        
        plans = []
        errors = []
        
        for i, request in enumerate(requests):
            try:
                response = await travel_service.create_smart_travel_plan(request)
                if response.success:
                    plans.append({
                        "index": i,
                        "plan": response.data["travel_plan"],
                        "success": True
                    })
                else:
                    errors.append({
                        "index": i,
                        "error": response.message,
                        "success": False
                    })
            except Exception as e:
                errors.append({
                    "index": i,
                    "error": str(e),
                    "success": False
                })
        
        return APIResponse(
            success=True,
            message=f"批量处理完成，成功{len(plans)}个，失败{len(errors)}个",
            data={
                "successful_plans": plans,
                "failed_plans": errors,
                "total_requests": len(requests),
                "success_count": len(plans),
                "error_count": len(errors)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量创建智能出行计划失败: {str(e)}")
        raise HTTPException(status_code=500, detail="批量处理失败")