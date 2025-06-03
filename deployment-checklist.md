# 部署检查清单

## ✅ 前端配置已完成

### 已更新的配置文件：
1. **src/config.js** - 主API配置
   - ✅ 已切换到生产环境: `http://120.48.150.254:8888`

2. **src/config/axios.js** - Axios默认配置
   - ✅ 已切换到生产环境: `http://120.48.150.254:8888`

3. **vite.config.js** - 开发服务器代理配置
   - ✅ 已切换到生产环境: `http://120.48.150.254:8888`

4. **src/views/Database.vue** - 数据库页面API配置
   - ✅ 已切换到生产环境: `http://120.48.150.254:8888`

### 使用全局配置的文件（自动更新）：
- ✅ **src/views/AIAssistant.vue** - 使用 `import { API_BASE_URL } from '../config'`
- ✅ **src/views/Home.vue** - 使用全局axios配置

## 🚀 部署步骤

### 1. 构建前端
```bash
npm run build
```

### 2. 使用Docker部署（推荐）
```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3. 手动部署
```bash
# 前端部署
npm run build
# 将 dist/ 目录部署到 Nginx 或其他 Web 服务器

# 后端部署
cd backend
# 确保后端服务在 8888 端口运行
```

## 🔧 环境切换

### 切换到生产环境
```bash
python switch-env.py production
```

### 切换回本地环境
```bash
python switch-env.py local
```

## 📋 部署后验证

### 1. 检查前端访问
- [ ] 前端页面能正常加载
- [ ] 首页数据能正常显示
- [ ] 图表能正常渲染

### 2. 检查API连接
- [ ] 首页API调用正常
- [ ] 数据库页面API调用正常
- [ ] AI助手功能正常
- [ ] 预测功能正常

### 3. 检查后端服务
- [ ] 后端服务在 8888 端口正常运行
- [ ] API端点响应正常
- [ ] 数据库连接正常

## 🌐 访问地址

- **前端**: http://120.48.150.254:3001 (如果使用Docker)
- **后端API**: http://120.48.150.254:8888
- **API文档**: http://120.48.150.254:8888/docs

## 🔍 故障排除

### 常见问题：
1. **CORS错误**: 检查后端CORS配置
2. **API连接失败**: 确认后端服务运行状态
3. **静态资源404**: 检查前端构建和部署路径
4. **数据不显示**: 检查API响应和数据格式

### 日志查看：
```bash
# Docker日志
docker-compose logs frontend
docker-compose logs backend

# 浏览器控制台
# 检查网络请求和JavaScript错误
```
