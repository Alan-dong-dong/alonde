# 智能出行助手 🚗

基于天气数据的智能出行规划和穿搭推荐系统，为用户提供个性化的出行建议和穿搭推荐。

## ✨ 功能特性

### 🌤️ 天气服务
- **实时天气查询**：支持城市名称、坐标定位获取当前天气
- **天气预报**：提供未来7天详细天气预报
- **生活指数**：包含穿衣、运动、洗车等生活建议
- **天气图表**：温度、湿度趋势可视化展示

### 🗺️ 路线规划
- **多种交通方式**：支持驾车、步行、骑行、公交路线规划
- **智能推荐**：结合天气因素的路线优化建议
- **地理编码**：地址与坐标相互转换
- **路线收藏**：保存常用路线，快速访问

### 👔 穿搭推荐
- **智能推荐**：基于天气、温度、湿度的穿搭建议
- **服装分类**：按类别浏览不同服装选择
- **个性化设置**：根据用户偏好调整推荐
- **季节适配**：自动适应不同季节的穿搭需求

### 🎨 用户体验
- **响应式设计**：完美适配桌面端和移动端
- **深色主题**：支持明暗主题切换
- **离线提醒**：网络状态监控和提醒
- **错误处理**：友好的错误提示和恢复机制
- **加载优化**：优雅的加载动画和状态提示

## 🛠️ 技术栈

### 后端技术
- **FastAPI** - 现代化的Python Web框架
- **Python 3.8+** - 编程语言
- **Uvicorn** - ASGI服务器
- **Pydantic** - 数据验证和序列化
- **和风天气API** - 天气数据服务
- **高德地图API** - 地图和路线服务

### 前端技术
- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全的JavaScript
- **Element Plus** - Vue 3 UI组件库
- **Vite** - 现代化构建工具
- **Pinia** - Vue 状态管理
- **Vue Router** - 路由管理

## 🚀 快速开始

### 环境要求
- **Python**: 3.8 或更高版本
- **Node.js**: 16 或更高版本
- **包管理器**: npm 或 yarn

### 1. 克隆项目
```bash
git clone <repository-url>
cd 智能出行
```

### 2. 后端设置

#### 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 配置环境变量
复制 `.env.example` 到 `.env` 并填入API密钥：
```bash
cp .env.example .env
```

编辑 `.env` 文件：
```env
# 和风天气API密钥
HEFENG_API_KEY=your_hefeng_api_key_here

# 高德地图API密钥
AMAP_API_KEY=your_amap_api_key_here

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

#### 启动后端服务
```bash
python main.py
```

后端服务将在 `http://localhost:8000` 启动

### 3. 前端设置

#### 安装依赖
```bash
cd frontend
npm install
```

#### 配置环境变量
编辑 `.env` 文件：
```env
# API基础URL
VITE_API_BASE_URL=http://localhost:8000/api/v1

# 应用配置
VITE_APP_TITLE=智能出行助手
VITE_APP_VERSION=1.0.0
```

#### 启动前端服务
```bash
npm run dev
```

前端应用将在 `http://localhost:3000` 启动

## 📚 API文档

启动后端服务后，可以通过以下方式查看API文档：

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### 主要API端点

#### 天气服务
- `POST /api/v1/weather/current` - 获取当前天气
- `GET /api/v1/weather/current/by-coordinates` - 通过坐标获取天气
- `GET /api/v1/weather/current/by-city` - 通过城市获取天气
- `GET /api/v1/weather/forecast/by-coordinates` - 获取天气预报

#### 路线规划
- `POST /api/v1/routes/plan` - 智能路线规划
- `GET /api/v1/routes/plan/driving` - 驾车路线规划
- `GET /api/v1/routes/plan/walking` - 步行路线规划
- `GET /api/v1/routes/geocode` - 地理编码
- `GET /api/v1/routes/reverse-geocode` - 逆地理编码

#### 穿搭推荐
- `POST /api/v1/outfit/recommend` - 获取穿搭推荐
- `POST /api/v1/outfit/recommend/simple` - 简化穿搭推荐
- `GET /api/v1/outfit/categories` - 获取服装分类

## 🏗️ 项目结构

```
智能出行/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   └── services/       # 业务服务
│   ├── main.py            # 应用入口
│   └── requirements.txt   # Python依赖
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/           # API调用
│   │   ├── components/    # Vue组件
│   │   ├── stores/        # 状态管理
│   │   ├── views/         # 页面视图
│   │   └── utils/         # 工具函数
│   ├── package.json       # 前端依赖
│   └── vite.config.ts     # Vite配置
└── README.md              # 项目文档
```

## 🔧 开发指南

### 代码规范
- 后端遵循 PEP 8 Python代码规范
- 前端使用 ESLint + Prettier 进行代码格式化
- 提交信息遵循 Conventional Commits 规范

### 测试
```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm run test
```

### 构建部署
```bash
# 前端构建
cd frontend
npm run build

# 后端部署
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 问题反馈

如果您发现了bug或有功能建议，请通过 [Issues](../../issues) 告诉我们。

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [和风天气](https://www.qweather.com/) - 提供天气数据服务
- [高德地图](https://lbs.amap.com/) - 提供地图和路线服务
- [Vue.js](https://vuejs.org/) - 前端框架
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [Element Plus](https://element-plus.org/) - UI组件库

---

**智能出行助手** - 让每一次出行都更加智能和舒适 🌟