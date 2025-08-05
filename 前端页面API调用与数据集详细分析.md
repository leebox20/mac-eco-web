# 前端页面API调用与数据集详细分析

## 概述

本文档详细分析中国宏观经济大数据AI预测系统中每个前端页面调用的API接口以及对应的数据集来源，帮助理解整个系统的数据流向。

## 1. 前端页面与API调用关系

### 1.1 Home.vue (首页经济指标展示)

**调用的API:**
```javascript
// 1. 获取关键经济指标数据（用于顶部卡片显示）
const keyIndicatorsResponse = await axios.get(`${API_BASE_URL}/api/key-indicators`)

// 2. 获取GDP季度数据
const gdpResponse = await axios.get(`${API_BASE_URL}/api/gdp-data`)

// 3. 获取关键指标时间序列数据（用于图表显示）
const seriesResponse = await axios.get(`${API_BASE_URL}/api/key-indicators-series`)
```

**功能说明:**
- 显示最新的经济指标卡片（GDP、CPI、PPI等）
- 渲染ECharts时间序列图表
- 区分历史数据和预测数据

### 1.2 Database.vue (数据库查询界面)

**调用的API:**
```javascript
// 1. 获取月度预测数据（主要数据源）
const response = await axios.get(`${API_BASE_URL}/api/monthly-prediction-data`, {
    params: {
        page: currentPage.value,
        page_size: pageSize.value,
        search: searchQuery.value
    }
})

// 2. 获取图表数据（备用数据源，清空搜索时使用）
const response = await axios.get(`${API_BASE_URL}/api/chart-data`, {
    params: {
        page: 1,
        page_size: pageSize.value
    }
})
```

**功能说明:**
- 分页展示经济指标数据
- 支持搜索过滤功能
- 数据对比和图表展示

### 1.3 AIAssistant.vue (AI助手聊天)

**调用的API:**
```javascript
// 1. 创建新对话
const response = await fetch(`${API_BASE_URL}/conversation`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
})

// 2. 发送流式聊天请求
const response = await fetch(`${API_BASE_URL}/stream`, {
    method: 'POST',
    body: JSON.stringify({
        conversation_id: currentConversationId.value,
        query: userMessage
    })
})
```

**功能说明:**
- 创建和管理对话会话
- 实时流式AI对话
- 本地存储对话历史

### 1.4 Prediction.vue (预测分析页面)

**调用的API:**
```javascript
// 与Home.vue相同的三个API
const keyIndicatorsResponse = await axios.get(`${API_BASE_URL}/api/key-indicators`)
const gdpResponse = await axios.get(`${API_BASE_URL}/api/gdp-data`)
const seriesResponse = await axios.get(`${API_BASE_URL}/api/key-indicators-series`)

// 额外的分析API（未实现）
const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    body: JSON.stringify({ indicatorId })
})
```

**功能说明:**
- 复用首页的数据展示逻辑
- 提供预测分析功能

### 1.5 AnalysisPredictResult.vue (分析预测结果)

**调用的API:**
```javascript
// 1. 宏观经济分析
const response = await fetch(`${API_BASE_URL}/api/macro-analysis`, {
    method: 'POST'
})

// 2. 获取关键指标时间序列数据
const seriesResponse = await fetch(`${API_BASE_URL}/api/key-indicators-series`)

// 3. 获取GDP数据
const gdpResponse = await fetch(`${API_BASE_URL}/api/gdp-data`)

// 4. 获取关键指标数据
const keyIndicatorsResponse = await fetch(`${API_BASE_URL}/api/key-indicators`)
```

**功能说明:**
- 综合宏观经济分析
- 多指标数据展示
- AI分析结果展示

## 2. API接口与数据集映射关系

### 2.1 GET /api/key-indicators (首页关键指标)

**数据来源优先级:**
1. `update/月度关键数据预测结果含区间.csv` (最优先)
2. `update/月度关键数据预测结果.csv` (备用)
3. `data/DATAMERGED-20241203-完整数据集-修复版.csv` (最后备用)
4. `data/gdp_complete_data.csv` (GDP数据)

**数据处理逻辑:**
```python
# 1. 根据当前时间计算最新可用数据时间点
# 2. GDP数据：滞后1个季度发布
# 3. 月度数据：滞后1个月发布
# 4. 判断是否为预测数据（2025年6月后）
# 5. 处理置信区间数据
```

**返回的关键指标:**
- GDP不变价:当季同比
- 社会消费品零售总额
- CPI、PPI
- 工业增加值
- 固定资产投资
- 出口/进口金额
- 房地产投资
- M2货币供应量
- 社会融资规模

### 2.2 GET /api/gdp-data (GDP季度数据)

**数据来源:**
- 主要: `update/gdp_complete_data.csv`
- 备用: `data/gdp_complete_data.csv`

**数据结构:**
```csv
date,quarter,gdp_value,is_predicted,confidence_interval
2001-06-30,2001Q2,8.6,False,
2025-12-31,2025Q4,5.11,True,[4.8,5.4]
```

**特点:**
- 包含2001年至2025年的季度GDP数据
- 明确标识历史数据和预测数据
- 预测数据包含置信区间

### 2.3 GET /api/key-indicators-series (关键指标时间序列)

**数据来源:**
- `update/月度关键数据预测结果含区间.csv`

**数据特点:**
- 完整的时间序列数据
- 包含置信区间信息
- 支持历史和预测数据的连续展示

### 2.4 GET /api/chart-data (图表数据分页)

**数据来源:**
- `data/DATAMERGED-20241203-完整数据集-修复版.csv`

**处理机制:**
```python
# 使用LRU缓存机制
@lru_cache(maxsize=1000)
def get_cached_page_data(page, page_size, search):
    # 1. 从processed_data全局变量获取预处理数据
    # 2. 分页处理
    # 3. 搜索过滤
    # 4. 返回标准化格式
```

**数据范围:**
- 2001-2024年历史经济数据
- 包含所有主要经济指标
- 支持分页和搜索

### 2.5 GET /api/monthly-prediction-data (月度预测数据)

**数据来源:**
- `update/月度数据完整合并结果.csv`

**数据特点:**
- 历史数据 + 预测数据的完整合并
- 支持多种编码格式读取
- 自动识别预测数据标记

### 2.6 POST /conversation & POST /stream (AI对话)

**数据来源:**
- SQLite数据库 `test.db`
  - `conversations`表：对话记录
  - `messages`表：消息记录
- 百度千帆AI平台外部API

**数据流程:**
```
用户输入 → 本地数据库存储 → 百度千帆API → 流式响应 → 本地存储
```

### 2.7 POST /api/macro-analysis (宏观经济分析)

**数据来源:**
- 调用 `get_key_indicators()` 获取最新指标数据
- 通过百度千帆AI平台进行综合分析

## 3. 数据处理关键机制

### 3.1 数据时间判断逻辑

```python
# 预测数据判断
is_predicted = year > 2025 or (year == 2025 and month >= 6)

# 最新可用数据时间计算
if current_month <= 3:
    latest_quarter = f"{current_year-1}Q4"
elif current_month <= 6:
    latest_quarter = f"{current_year}Q1"
# ... 其他季度逻辑
```

### 3.2 置信区间处理

```python
# 置信区间格式化
if variation_column in df_monthly.columns:
    variation = row[variation_column]
    if pd.notna(variation):
        confidence_interval = [
            float(value) - float(variation), 
            float(value) + float(variation)
        ]
```

### 3.3 缓存机制

```python
# LRU缓存提升性能
@lru_cache(maxsize=1000)
def get_cached_page_data(page, page_size, search):
    # 分页数据缓存
    # 搜索结果缓存
    # 减少重复计算
```

## 4. 数据流向总结

1. **原始数据** → **CSV文件存储** → **后端预处理** → **API接口** → **前端展示**

2. **数据优先级**: 预测数据文件 > 历史数据文件 > 备用文件

3. **实时性**: 根据当前时间动态计算最新可用数据时间点

4. **完整性**: 历史数据与预测数据无缝衔接，明确标识区分

5. **性能**: 多级缓存机制，分页处理大数据量

这个系统通过精心设计的数据架构，实现了从原始经济数据到智能分析展示的完整数据流，为用户提供了专业、高效的宏观经济分析服务。
