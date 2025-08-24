"""API路由主文件"""

from fastapi import APIRouter

from .endpoints import weather, routes, outfit, travel

api_router = APIRouter()

# 注册各个功能模块的路由
api_router.include_router(weather.router, prefix="/weather", tags=["天气服务"])
api_router.include_router(routes.router, prefix="/routes", tags=["路线规划"])
api_router.include_router(outfit.router, prefix="/outfit", tags=["穿搭推荐"])
api_router.include_router(travel.router, prefix="/travel", tags=["智能出行规划"])