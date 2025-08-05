#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试API是否返回2026年数据
"""

import requests
import json

def quick_test():
    try:
        print("测试API...")
        response = requests.get("http://120.48.150.254:8888/api/monthly-prediction-data?page=1&page_size=1", timeout=10)
        
        if response.status_code != 200:
            print(f"API错误: {response.status_code}")
            return
        
        data = response.json()
        first_indicator = data['data'][0]
        
        has_2026 = any('2026' in t for t in first_indicator['times'])
        print(f"包含2026年数据: {has_2026}")
        
        if has_2026:
            print("✅ 成功！找到2026年数据")
            for i, time in enumerate(first_indicator['times']):
                if '2026' in time:
                    print(f"  {time}: {first_indicator['values'][i]}")
        else:
            print("❌ 仍然没有2026年数据")
            print(f"最后时间点: {first_indicator['times'][-1]}")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    quick_test()
