import httpx
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.core.exceptions import MapAPIException
from app.models.schemas import (
    LocationModel, 
    RouteInfo, 
    RouteStep, 
    TransportMode
)
import logging
import json

logger = logging.getLogger(__name__)


class MapService:
    """高德地图API服务类"""
    
    def __init__(self):
        self.api_key = settings.AMAP_API_KEY
        self.security_key = settings.AMAP_SECURITY_KEY
        self.base_url = settings.AMAP_BASE_URL
        self.timeout = settings.REQUEST_TIMEOUT
        
        if not self.api_key:
            logger.warning("高德地图API密钥未配置")
        if not self.security_key:
            logger.warning("高德地图安全密钥未配置")
    
    async def geocode_address(self, address: str, city: Optional[str] = None) -> LocationModel:
        """地址转坐标（地理编码）"""
        # 检查API密钥配置
        if not self.api_key:
            raise MapAPIException("高德地图API密钥未配置，请在.env文件中设置AMAP_API_KEY")
        
        try:
            url = f"{self.base_url}/v3/geocode/geo"
            params = {
                "address": address,
                "key": self.api_key
            }
            
            if self.security_key:
                params["jscode"] = self.security_key
            
            if city:
                params["city"] = city
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("status") != "1":
                    raise MapAPIException(f"地理编码失败: {data.get('info')}")
                
                geocodes = data.get("geocodes", [])
                if not geocodes:
                    raise MapAPIException(f"未找到地址: {address}")
                
                geocode = geocodes[0]
                location_str = geocode.get("location", "")
                
                if not location_str:
                    raise MapAPIException("无效的坐标信息")
                
                longitude, latitude = map(float, location_str.split(","))
                
                return LocationModel(
                    longitude=longitude,
                    latitude=latitude,
                    address=geocode.get("formatted_address", address),
                    city=geocode.get("city", city)
                )
                
        except httpx.TimeoutException:
            logger.error("地理编码请求超时")
            raise MapAPIException("地图服务请求超时")
        except httpx.HTTPError as e:
            logger.error(f"地理编码请求失败: {e}")
            raise MapAPIException("地图服务暂时不可用")
        except Exception as e:
            logger.error(f"地理编码时发生未知错误: {e}")
            raise MapAPIException("地理编码失败")
    
    async def reverse_geocode(self, location: LocationModel) -> LocationModel:
        """坐标转地址（逆地理编码）"""
        # 检查API密钥配置
        if not self.api_key:
            raise MapAPIException("高德地图API密钥未配置，请在.env文件中设置AMAP_API_KEY")
        
        try:
            url = f"{self.base_url}/v3/geocode/regeo"
            params = {
                "location": f"{location.longitude},{location.latitude}",
                "key": self.api_key,
                "radius": 1000,
                "extensions": "base"
            }
            
            if self.security_key:
                params["jscode"] = self.security_key
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("status") != "1":
                    raise MapAPIException(f"逆地理编码失败: {data.get('info')}")
                
                regeocode = data.get("regeocode", {})
                address_component = regeocode.get("addressComponent", {})
                
                return LocationModel(
                    longitude=location.longitude,
                    latitude=location.latitude,
                    address=regeocode.get("formatted_address", ""),
                    city=address_component.get("city", "")
                )
                
        except Exception as e:
            logger.error(f"逆地理编码时发生错误: {e}")
            raise MapAPIException("逆地理编码失败")
    
    async def search_places(self, keywords: str, city: Optional[str] = None) -> List[LocationModel]:
        """搜索地点（POI搜索）"""
        # 检查API密钥配置
        if not self.api_key:
            raise MapAPIException("高德地图API密钥未配置，请在.env文件中设置AMAP_API_KEY")
        
        try:
            url = f"{self.base_url}/v3/place/text"
            params = {
                "keywords": keywords,
                "key": self.api_key,
                "extensions": "base"
            }
            
            if self.security_key:
                params["jscode"] = self.security_key
            
            if city:
                params["city"] = city
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("status") != "1":
                    raise MapAPIException(f"地点搜索失败: {data.get('info')}")
                
                pois = data.get("pois", [])
                locations = []
                
                for poi in pois:
                    location_str = poi.get("location", "")
                    if location_str:
                        longitude, latitude = map(float, location_str.split(","))
                        location = LocationModel(
                            longitude=longitude,
                            latitude=latitude,
                            address=poi.get("name", "") + " " + poi.get("address", ""),
                            city=poi.get("cityname", city)
                        )
                        locations.append(location)
                
                return locations
                
        except httpx.TimeoutException:
            logger.error("地点搜索请求超时")
            raise MapAPIException("地图服务请求超时")
        except httpx.HTTPError as e:
            logger.error(f"地点搜索请求失败: {e}")
            raise MapAPIException("地图服务暂时不可用")
        except Exception as e:
            logger.error(f"地点搜索时发生未知错误: {e}")
            raise MapAPIException("地点搜索失败")
    
    async def plan_driving_route(self, origin: LocationModel, destination: LocationModel) -> RouteInfo:
        """驾车路径规划"""
        try:
            url = f"{self.base_url}/v3/direction/driving"
            params = {
                "origin": f"{origin.longitude},{origin.latitude}",
                "destination": f"{destination.longitude},{destination.latitude}",
                "key": self.api_key,
                "extensions": "all"
            }
            
            if self.security_key:
                params["jscode"] = self.security_key
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("status") != "1":
                    raise MapAPIException(f"路径规划失败: {data.get('info')}")
                
                route = data.get("route", {})
                paths = route.get("paths", [])
                
                if not paths:
                    raise MapAPIException("未找到可用路径")
                
                path = paths[0]  # 取第一条路径
                
                return self._parse_driving_route(path, origin, destination)
                
        except Exception as e:
            logger.error(f"驾车路径规划时发生错误: {e}")
            raise MapAPIException("驾车路径规划失败")
    
    async def plan_walking_route(self, origin: LocationModel, destination: LocationModel) -> RouteInfo:
        """步行路径规划"""
        try:
            url = f"{self.base_url}/v3/direction/walking"
            params = {
                "origin": f"{origin.longitude},{origin.latitude}",
                "destination": f"{destination.longitude},{destination.latitude}",
                "key": self.api_key
            }
            
            if self.security_key:
                params["jscode"] = self.security_key
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("status") != "1":
                    raise MapAPIException(f"步行路径规划失败: {data.get('info')}")
                
                route = data.get("route", {})
                paths = route.get("paths", [])
                
                if not paths:
                    raise MapAPIException("未找到可用步行路径")
                
                path = paths[0]
                
                return self._parse_walking_route(path, origin, destination)
                
        except Exception as e:
            logger.error(f"步行路径规划时发生错误: {e}")
            raise MapAPIException("步行路径规划失败")
    
    async def plan_cycling_route(self, origin: LocationModel, destination: LocationModel) -> RouteInfo:
        """骑行路径规划"""
        try:
            url = f"{self.base_url}/v4/direction/bicycling"
            params = {
                "origin": f"{origin.longitude},{origin.latitude}",
                "destination": f"{destination.longitude},{destination.latitude}",
                "key": self.api_key
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("status") != "1":
                    raise MapAPIException(f"骑行路径规划失败: {data.get('info')}")
                
                route = data.get("route", {})
                paths = route.get("paths", [])
                
                if not paths:
                    raise MapAPIException("未找到可用骑行路径")
                
                path = paths[0]
                
                return self._parse_cycling_route(path, origin, destination)
                
        except Exception as e:
            logger.error(f"骑行路径规划时发生错误: {e}")
            raise MapAPIException("骑行路径规划失败")
    
    async def plan_transit_route(self, origin: LocationModel, destination: LocationModel, 
                               origin_city: str, dest_city: str) -> RouteInfo:
        """公交路径规划"""
        try:
            url = f"{self.base_url}/v3/direction/transit/integrated"
            params = {
                "origin": f"{origin.longitude},{origin.latitude}",
                "destination": f"{destination.longitude},{destination.latitude}",
                "city": origin_city,
                "cityd": dest_city,
                "key": self.api_key,
                "extensions": "all"
            }
            
            if self.security_key:
                params["jscode"] = self.security_key
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("status") != "1":
                    raise MapAPIException(f"公交路径规划失败: {data.get('info')}")
                
                route = data.get("route", {})
                transits = route.get("transits", [])
                
                if not transits:
                    raise MapAPIException("未找到可用公交路径")
                
                transit = transits[0]
                
                return self._parse_transit_route(transit, origin, destination)
                
        except Exception as e:
            logger.error(f"公交路径规划时发生错误: {e}")
            raise MapAPIException("公交路径规划失败")
    
    def _parse_driving_route(self, path: Dict[str, Any], origin: LocationModel, destination: LocationModel) -> RouteInfo:
        """解析驾车路径数据"""
        steps = []
        for step_data in path.get("steps", []):
            step = RouteStep(
                instruction=step_data.get("instruction", ""),
                distance=float(step_data.get("distance", 0)),
                duration=int(step_data.get("duration", 0)),
                polyline=step_data.get("polyline", "")
            )
            steps.append(step)
        
        return RouteInfo(
            origin=origin,
            destination=destination,
            transport_mode=TransportMode.DRIVING,
            total_distance=float(path.get("distance", 0)),
            total_duration=int(path.get("duration", 0)),
            steps=steps,
            polyline=path.get("polyline", "")
        )
    
    def _parse_walking_route(self, path: Dict[str, Any], origin: LocationModel, destination: LocationModel) -> RouteInfo:
        """解析步行路径数据"""
        steps = []
        for step_data in path.get("steps", []):
            step = RouteStep(
                instruction=step_data.get("instruction", ""),
                distance=float(step_data.get("distance", 0)),
                duration=int(step_data.get("duration", 0)),
                polyline=step_data.get("polyline", "")
            )
            steps.append(step)
        
        return RouteInfo(
            origin=origin,
            destination=destination,
            transport_mode=TransportMode.WALKING,
            total_distance=float(path.get("distance", 0)),
            total_duration=int(path.get("duration", 0)),
            steps=steps,
            polyline=path.get("polyline", "")
        )
    
    def _parse_cycling_route(self, path: Dict[str, Any], origin: LocationModel, destination: LocationModel) -> RouteInfo:
        """解析骑行路径数据"""
        steps = []
        for step_data in path.get("steps", []):
            step = RouteStep(
                instruction=step_data.get("instruction", ""),
                distance=float(step_data.get("distance", 0)),
                duration=int(step_data.get("duration", 0)),
                polyline=step_data.get("polyline", "")
            )
            steps.append(step)
        
        return RouteInfo(
            origin=origin,
            destination=destination,
            transport_mode=TransportMode.CYCLING,
            total_distance=float(path.get("distance", 0)),
            total_duration=int(path.get("duration", 0)),
            steps=steps,
            polyline=path.get("polyline", "")
        )
    
    def _parse_transit_route(self, transit: Dict[str, Any], origin: LocationModel, destination: LocationModel) -> RouteInfo:
        """解析公交路径数据"""
        steps = []
        segments = transit.get("segments", [])
        
        for segment in segments:
            if segment.get("walking"):
                # 步行段
                walking = segment["walking"]
                step = RouteStep(
                    instruction=f"步行 {walking.get('distance', 0)}米",
                    distance=float(walking.get("distance", 0)),
                    duration=int(walking.get("duration", 0)),
                    polyline=walking.get("polyline", "")
                )
                steps.append(step)
            
            if segment.get("bus"):
                # 公交段
                bus = segment["bus"]
                buslines = bus.get("buslines", [])
                if buslines:
                    busline = buslines[0]
                    step = RouteStep(
                        instruction=f"乘坐{busline.get('name', '公交')} {bus.get('distance', 0)}米",
                        distance=float(bus.get("distance", 0)),
                        duration=int(bus.get("duration", 0)),
                        polyline=bus.get("polyline", "")
                    )
                    steps.append(step)
        
        return RouteInfo(
            origin=origin,
            destination=destination,
            transport_mode=TransportMode.TRANSIT,
            total_distance=float(transit.get("distance", 0)),
            total_duration=int(transit.get("duration", 0)),
            steps=steps
        )


# 创建全局地图服务实例
map_service = MapService()