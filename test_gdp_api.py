#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试GDP API
"""

import requests
import json

def test_gdp_api():
    """测试GDP API"""
    print("🔍 测试GDP API...")
    
    base_url = "http://localhost:8000"
    
    try:
        # 测试GDP数据API
        response = requests.get(f"{base_url}/api/gdp-data")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API响应成功，状态码: {response.status_code}")
            print(f"📊 数据记录数: {data.get('total_records', 0)}")
            print(f"📈 历史数据: {data.get('historical_count', 0)} 条")
            print(f"🔮 预测数据: {data.get('predicted_count', 0)} 条")
            print(f"📅 最新季度: {data.get('latest_quarter', 'N/A')}")
            print(f"📊 最新数值: {data.get('latest_value', 'N/A')}%")
            
            # 检查最近的季度数据
            quarters = data.get('quarters', [])
            values = data.get('values', [])
            is_predicted = data.get('is_predicted', [])
            confidence_intervals = data.get('confidence_intervals', [])
            
            print("\n最近10个季度的数据:")
            recent_count = min(10, len(quarters))
            start_index = len(quarters) - recent_count
            
            for i in range(start_index, len(quarters)):
                quarter = quarters[i]
                value = values[i]
                is_pred = is_predicted[i]
                interval = confidence_intervals[i]
                
                status = "预测" if is_pred else "历史"
                interval_text = ""
                if interval:
                    if isinstance(interval, list) and len(interval) == 2:
                        interval_text = f", 区间: [{interval[0]:.3f}, {interval[1]:.3f}]"
                    else:
                        interval_text = f", 区间: ±{interval}"
                
                print(f"  {quarter}: {value}% ({status}{interval_text})")
            
            # 检查是否有重复的季度
            quarter_counts = {}
            for quarter in quarters:
                quarter_counts[quarter] = quarter_counts.get(quarter, 0) + 1
            
            duplicates = {q: count for q, count in quarter_counts.items() if count > 1}
            if duplicates:
                print(f"\n⚠️  发现重复的季度: {duplicates}")
            else:
                print(f"\n✅ 没有重复的季度数据")
            
            # 特别检查关键季度
            print(f"\n🔍 检查关键季度:")
            key_quarters = ['2024Q4', '2025Q1', '2025Q2']
            for quarter in key_quarters:
                if quarter in quarters:
                    index = quarters.index(quarter)
                    value = values[index]
                    is_pred = is_predicted[index]
                    status = "预测" if is_pred else "历史"
                    print(f"  {quarter}: {value}% ({status})")
                else:
                    print(f"  {quarter}: 数据缺失")
                
        else:
            print(f"❌ API响应失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端服务正在运行")
        print("启动命令: cd backend && python app.py")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == "__main__":
    test_gdp_api()
