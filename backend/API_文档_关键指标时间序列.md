# 关键指标时间序列数据API文档

## API概述

**端点名称：** 获取关键经济指标完整时间序列数据  
**请求地址：** `GET /api/key-indicators-series`  
**功能描述：** 获取所有关键经济指标的完整时间序列数据，包含历史数据和预测数据，以及置信区间信息

## 请求参数

**请求方法：** GET  
**请求参数：** 无需参数  
**Content-Type：** application/json

## 响应数据结构

### 成功响应 (200 OK)

```json
{
  "indicators": [
    {
      "name": "社会消费品零售总额",
      "column": "中国:社会消费品零售总额:当月同比",
      "unit": "%",
      "total_points": 300,
      "data": [
        {
          "date": "2001-01",
          "value": 12.5,
          "is_predicted": false,
          "confidence_interval": null
        },
        {
          "date": "2001-02",
          "value": 8.6,
          "is_predicted": false,
          "confidence_interval": null
        },
        "...(省略中间数据)...",
        {
          "date": "2025-06",
          "value": 5.298763,
          "is_predicted": true,
          "confidence_interval": [5.02275562, 5.57476938]
        },
        {
          "date": "2025-12",
          "value": 4.898776,
          "is_predicted": true,
          "confidence_interval": [4.84765247, 4.94989953]
        }
      ]
    },
    {
      "name": "CPI",
      "column": "中国:CPI:当月同比",
      "unit": "%",
      "total_points": 300,
      "data": [
        {
          "date": "2001-01",
          "value": 1.2,
          "is_predicted": false,
          "confidence_interval": null
        },
        "...(省略中间数据)...",
        {
          "date": "2025-12",
          "value": -0.06633282,
          "is_predicted": true,
          "confidence_interval": [-0.081488836, -0.051176804]
        }
      ]
    }
  ],
  "total_indicators": 12,
  "data_source": "月度关键数据预测结果含区间.csv",
  "update_time": "2025-06-23 09:34:00"
}
```

### 字段说明

#### 根级字段
- `indicators` (Array): 指标数据数组
- `total_indicators` (Number): 总指标数量
- `data_source` (String): 数据来源文件名
- `update_time` (String): 数据更新时间

#### indicators数组中每个对象的字段
- `name` (String): 指标中文名称
- `column` (String): 数据库中的列名（技术字段）
- `unit` (String): 数据单位（%或亿元）
- `total_points` (Number): 该指标的数据点总数
- `data` (Array): 时间序列数据数组

#### data数组中每个数据点的字段
- `date` (String): 日期，格式为 "YYYY-MM"
- `value` (Number): 指标数值
- `is_predicted` (Boolean): 是否为预测数据（2025年6月及以后为true，之前为false）
- `confidence_interval` (Array|null): 置信区间，包含[下限, 上限]。历史数据为null，预测数据包含置信区间

### 包含的指标列表

1. **社会消费品零售总额** - 单位：%
2. **CPI** - 单位：%
3. **PPI** - 单位：%
4. **工业增加值** - 单位：%
5. **固定资产投资** - 单位：%
6. **出口金额** - 单位：%
7. **进口金额** - 单位：%
8. **房地产投资** - 单位：%
9. **制造业投资** - 单位：%
10. **基础设施投资** - 单位：%
11. **M2货币供应量** - 单位：%
12. **社会融资规模** - 单位：亿元

## 错误响应

### 404 Not Found
```json
{
  "detail": "未找到关键指标数据文件"
}
```

### 500 Internal Server Error
```json
{
  "detail": "获取关键指标时间序列数据失败: [具体错误信息]"
}
```

## 前端使用示例

### JavaScript/Fetch
```javascript
async function fetchKeyIndicatorsSeries() {
  try {
    const response = await fetch('/api/key-indicators-series');
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('获取到', data.total_indicators, '个指标数据');
    
    // 处理数据
    data.indicators.forEach(indicator => {
      console.log(`${indicator.name}: ${indicator.total_points}个数据点`);
      
      // 分离历史数据和预测数据
      const historicalData = indicator.data.filter(item => !item.is_predicted);
      const predictedData = indicator.data.filter(item => item.is_predicted);
      
      console.log(`历史数据: ${historicalData.length}点，预测数据: ${predictedData.length}点`);
    });
    
    return data;
  } catch (error) {
    console.error('获取关键指标数据失败:', error);
    throw error;
  }
}
```

### React Hook示例
```jsx
import { useState, useEffect } from 'react';

function useKeyIndicatorsSeries() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const response = await fetch('/api/key-indicators-series');
        
        if (!response.ok) {
          throw new Error(`获取数据失败: ${response.status}`);
        }
        
        const result = await response.json();
        setData(result);
        setError(null);
      } catch (err) {
        setError(err.message);
        setData(null);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  return { data, loading, error };
}

// 使用示例
function KeyIndicatorsChart() {
  const { data, loading, error } = useKeyIndicatorsSeries();

  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误: {error}</div>;
  if (!data) return <div>暂无数据</div>;

  return (
    <div>
      <h2>关键经济指标 ({data.total_indicators}个)</h2>
      <p>数据更新时间: {data.update_time}</p>
      
      {data.indicators.map((indicator, index) => (
        <div key={index}>
          <h3>{indicator.name} ({indicator.unit})</h3>
          <p>数据点: {indicator.total_points}个</p>
          {/* 这里可以集成图表组件 */}
        </div>
      ))}
    </div>
  );
}
```

## 图表集成建议

### 使用ECharts
```javascript
function createTimeSeriesChart(indicator) {
  const option = {
    title: {
      text: `${indicator.name} (${indicator.unit})`
    },
    xAxis: {
      type: 'category',
      data: indicator.data.map(item => item.date)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '数值',
        type: 'line',
        data: indicator.data.map(item => item.value),
        markPoint: {
          data: indicator.data
            .filter(item => item.is_predicted)
            .map(item => ({
              name: '预测',
              xAxis: item.date,
              yAxis: item.value
            }))
        }
      }
    ]
  };
  
  // 如果有置信区间，添加区域图
  if (indicator.data.some(item => item.confidence_interval)) {
    option.series.push({
      name: '置信区间',
      type: 'line',
      data: indicator.data.map(item => 
        item.confidence_interval ? item.confidence_interval : [null, null]
      ),
      areaStyle: {
        opacity: 0.3
      }
    });
  }
  
  return option;
}
```

## 数据说明

### 时间范围
- **历史数据**：2001年1月 - 2025年5月（共288个月）
- **预测数据**：2025年6月 - 2025年12月（共7个月）
- **总计**：300个数据点

### 数据特征
- **历史数据特征**：
  - `is_predicted`: false
  - `confidence_interval`: null
  - 数据来源：实际统计数据
  
- **预测数据特征**：
  - `is_predicted`: true
  - `confidence_interval`: [下限, 上限]
  - 数据来源：模型预测结果

## 注意事项

1. **数据规模**：每个指标包含300个数据点，覆盖24年的完整时间序列
2. **数据时效性**：数据每次请求时实时读取文件，确保最新
3. **置信区间**：只有预测数据（2025年6月-12月）才有置信区间，历史数据为null
4. **日期格式**：统一为"YYYY-MM"格式，便于前端处理
5. **数据筛选**：可通过`is_predicted`字段区分历史数据和预测数据
6. **单位处理**：注意社会融资规模单位为"亿元"，其他均为"%"
7. **数据连续性**：数据按月连续，无缺失月份

## 性能建议

- **数据量较大**：每个指标300个数据点，建议前端分页显示或按需加载
- **缓存策略**：建议在前端做适当缓存，避免频繁请求
- **图表优化**：对于长时间序列，建议提供时间范围筛选功能
- **数据压缩**：可考虑前端按年份或时间段分组显示
- **版本控制**：可考虑添加数据版本控制，只在数据更新时重新获取 