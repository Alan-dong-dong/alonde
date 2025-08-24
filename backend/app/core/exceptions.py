from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Union


logger = logging.getLogger(__name__)


class APIException(Exception):
    """自定义API异常基类"""
    
    def __init__(self, message: str, status_code: int = 500, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or f"ERROR_{status_code}"
        super().__init__(self.message)


class WeatherAPIException(APIException):
    """天气API异常"""
    
    def __init__(self, message: str = "天气服务暂时不可用"):
        super().__init__(message, 503, "WEATHER_API_ERROR")


class MapAPIException(APIException):
    """地图API异常"""
    
    def __init__(self, message: str = "地图服务暂时不可用"):
        super().__init__(message, 503, "MAP_API_ERROR")


class ValidationException(APIException):
    """数据验证异常"""
    
    def __init__(self, message: str = "数据验证失败"):
        super().__init__(message, 422, "VALIDATION_ERROR")


class DataValidationException(APIException):
    """数据验证异常"""
    
    def __init__(self, message: str = "数据验证失败"):
        super().__init__(message, 422, "DATA_VALIDATION_ERROR")


class NotFoundError(APIException):
    """资源未找到异常"""
    
    def __init__(self, message: str = "请求的资源未找到"):
        super().__init__(message, 404, "NOT_FOUND")


def setup_exception_handlers(app: FastAPI):
    """设置全局异常处理器"""
    
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        """处理自定义API异常"""
        logger.error(f"API异常: {exc.message} - 路径: {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": exc.error_code,
                "message": exc.message,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """处理HTTP异常"""
        logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail} - 路径: {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """处理请求验证异常"""
        logger.warning(f"请求验证失败: {exc.errors()} - 路径: {request.url.path}")
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": "请求参数验证失败",
                "details": exc.errors(),
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """处理未捕获的异常"""
        logger.error(f"未处理异常: {str(exc)} - 路径: {request.url.path}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "服务器内部错误",
                "path": str(request.url.path)
            }
        )