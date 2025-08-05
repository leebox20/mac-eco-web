import requests
import json

# 测试API - 获取更多指标
url = "http://120.48.150.254:8888/api/monthly-prediction-data?page=1&page_size=10"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("API响应成功!")
    print(f"总指标数: {data.get('total', 0)}")
    
    # 查找有历史数据的指标
    for i, indicator in enumerate(data.get('data', [])):
        has_historical = any(not pred for pred in indicator['is_predicted'])
        if has_historical:
            print(f"\n找到有历史数据的指标: {indicator['title']}")
            print(f"数据点数量: {len(indicator['times'])}")
            print(f"时间范围: {indicator['times'][0]} 到 {indicator['times'][-1]}")
            
            historical_count = sum(1 for pred in indicator['is_predicted'] if not pred)
            predicted_count = sum(1 for pred in indicator['is_predicted'] if pred)
            print(f"历史数据点: {historical_count}")
            print(f"预测数据点: {predicted_count}")
            
            print(f"\n前5个时间点:")
            for j in range(min(5, len(indicator['times']))):
                print(f"  {indicator['times'][j]}: {indicator['values'][j]} (预测: {indicator['is_predicted'][j]})")
            break
    else:
        print("\n前10个指标都没有历史数据，只有预测数据")
        for i, indicator in enumerate(data.get('data', [])):
            print(f"{i+1}. {indicator['title']}: {len(indicator['times'])} 个数据点")
else:
    print(f"API请求失败: {response.status_code}")
    print(response.text)
