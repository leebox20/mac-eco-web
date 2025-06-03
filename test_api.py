import requests
import json

# 测试API
url = "http://localhost:8889/api/monthly-prediction-data?page=1&page_size=1"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("API响应成功!")
    print(f"总指标数: {data.get('total', 0)}")
    
    if data.get('data'):
        first_indicator = data['data'][0]
        print(f"\n第一个指标: {first_indicator['title']}")
        print(f"数据点数量: {len(first_indicator['times'])}")
        print(f"时间范围: {first_indicator['times'][0]} 到 {first_indicator['times'][-1]}")
        print(f"预测标记: {first_indicator['is_predicted']}")
        
        # 检查是否有历史数据
        has_historical = any(not pred for pred in first_indicator['is_predicted'])
        print(f"包含历史数据: {has_historical}")
        
        if has_historical:
            historical_count = sum(1 for pred in first_indicator['is_predicted'] if not pred)
            predicted_count = sum(1 for pred in first_indicator['is_predicted'] if pred)
            print(f"历史数据点: {historical_count}")
            print(f"预测数据点: {predicted_count}")
        
        print(f"\n前5个时间点:")
        for i in range(min(5, len(first_indicator['times']))):
            print(f"  {first_indicator['times'][i]}: {first_indicator['values'][i]} (预测: {first_indicator['is_predicted'][i]})")
else:
    print(f"API请求失败: {response.status_code}")
    print(response.text)
