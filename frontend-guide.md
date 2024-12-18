# GDP预测分析接口调用指南

## 接口说明

GDP预测分析现在分为4个独立的流式接口，每个接口负责不同方面的分析。

### 基本信息

提供四个独立的流式接口：

- **历史分析**: `/api/gdp-analysis/historical`
- **宏观分析**: `/api/gdp-analysis/macro`
- **市场分析**: `/api/gdp-analysis/market`
- **预期分析**: `/api/gdp-analysis/expectation`

所有接口都采用：
- **请求方法**: POST
- **数据格式**: JSON
- **响应类型**: Server-Sent Events (SSE)

### 请求参数

```json
{
    5.0  // GDP预测值，浮点数类型
}
```

### 响应格式

每个接口都会以流式方式返回数据，响应格式如下：

```json
{
    "name": "GDP数据分析流X",  // 分析模块名称
    "result": {
        // 具体的分析结果 下面是historical模块的示例
        ”First_Paragraph“ : ”“,
        ”Historical_Economic_Cycle_Analysis_Module”: ”“,
        ”Long_term_trend_analysis_modul“e : ”“,

    }
}
```

### 分析模块说明

| 接口路径 | 模块名称 | 分析内容 |
|---------|---------|---------|
| `/historical` | GDP数据分析流1 | 历史数据和经济趋势分析 |
| `/macro` | GDP数据分析流2 | 当前宏观经济环境分析 |
| `/market` | GDP数据分析���3 | 市场活动和商业信心分析 |
| `/expectation` | GDP数据分析流4 | 市场预期与投资者行为分析 |



## 各个APi返回的具体字段

historical: 

First_Paragraph, 
Historical_Economic_Cycle_Analysis_Module, Long_term_trend_analysis_module

macro: 

Policy_Background, 
International_economic_environment, 
Second_Paragraph


market: 
Consumption_and_investment_trends, 
Corporate_and_Industry_News, 
Third_Paragraph


expectation: 

Market_expectations, 
labour_market, 
Forth_Paragraph


## 注意事项

1. 每个接口都是独立的流式响应
2. 可以并行请求多个分析结果
3. 每个模块的处理时间约为30-40秒
4. 建议为每个模块单独显示加载状态
5. 可以根据需要选择性请求特定分析

## 错误处理

每个接口可能返回的错误：

- 400: 请求参数错误
- 500: 服务器内部错误
- 504: 请求超时

建议为每个接口单独实现错误处理和重试机制。

## 性能优化建议

1. 实现每个分析模块的结果缓存
2. 添加独立的加载状态指示器
3. 支持取消单个分析请求
4. 实现各个模块的断线重连机制
5. 可以根据需要选择性加载特定分析模块