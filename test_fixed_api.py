import requests
import json

# 测试修复后的API - 查找有历史数据的指标
url = "http://120.48.150.254:8888/api/monthly-prediction-data?page=1&page_size=20"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("API响应成功!")
    print(f"总指标数: {data.get('total', 0)}")
    
    # 查找有历史数据的指标
    historical_indicators = []
    prediction_only_indicators = []
    
    for indicator in data.get('data', []):
        has_historical = any(not pred for pred in indicator['is_predicted'])
        if has_historical:
            historical_count = sum(1 for pred in indicator['is_predicted'] if not pred)
            predicted_count = sum(1 for pred in indicator['is_predicted'] if pred)
            historical_indicators.append({
                'title': indicator['title'],
                'total_points': len(indicator['times']),
                'historical_points': historical_count,
                'predicted_points': predicted_count,
                'time_range': f"{indicator['times'][0]} 到 {indicator['times'][-1]}"
            })
        else:
            prediction_only_indicators.append({
                'title': indicator['title'],
                'total_points': len(indicator['times']),
                'time_range': f"{indicator['times'][0]} 到 {indicator['times'][-1]}"
            })
    
    print(f"\n=== 包含历史数据的指标 ({len(historical_indicators)}个) ===")
    for i, indicator in enumerate(historical_indicators, 1):
        print(f"{i}. {indicator['title']}")
        print(f"   总数据点: {indicator['total_points']}")
        print(f"   历史数据: {indicator['historical_points']} 个")
        print(f"   预测数据: {indicator['predicted_points']} 个")
        print(f"   时间范围: {indicator['time_range']}")
        print()
    
    print(f"\n=== 仅有预测数据的指标 ({len(prediction_only_indicators)}个) ===")
    for i, indicator in enumerate(prediction_only_indicators[:5], 1):  # 只显示前5个
        print(f"{i}. {indicator['title']}")
        print(f"   总数据点: {indicator['total_points']}")
        print(f"   时间范围: {indicator['time_range']}")
    
    if len(prediction_only_indicators) > 5:
        print(f"   ... 还有 {len(prediction_only_indicators) - 5} 个仅有预测数据的指标")
    
    # 如果找到了有历史数据的指标，显示详细信息
    if historical_indicators:
        print(f"\n=== 第一个有历史数据的指标详细信息 ===")
        # 重新获取第一个有历史数据的指标
        for indicator in data.get('data', []):
            has_historical = any(not pred for pred in indicator['is_predicted'])
            if has_historical:
                print(f"指标名称: {indicator['title']}")
                print(f"前10个数据点:")
                for i in range(min(10, len(indicator['times']))):
                    pred_text = "预测" if indicator['is_predicted'][i] else "历史"
                    print(f"  {indicator['times'][i]}: {indicator['values'][i]} ({pred_text})")
                break
else:
    print(f"API请求失败: {response.status_code}")
    print(response.text)
