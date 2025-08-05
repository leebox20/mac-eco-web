#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试API是否返回2026年1月的数据
"""

import requests
import json

def test_api_2026_data():
    """测试API是否返回2026年1月的数据"""
    print("=" * 60)
    print("测试API是否返回2026年1月的数据")
    print("=" * 60)
    
    base_url = "http://120.48.150.254:8888"
    
    try:
        # 测试第一页数据
        print("测试第1页数据...")
        response = requests.get(f"{base_url}/api/monthly-prediction-data?page=1&page_size=5")
        
        if response.status_code != 200:
            print(f"API请求失败: {response.status_code}")
            return
        
        data = response.json()
        print(f"总指标数: {data['total']}")
        print(f"总页数: {data['total_pages']}")
        
        # 检查第一个指标
        if data['data']:
            first_indicator = data['data'][0]
            print(f"\n第一个指标: {first_indicator['title']}")
            print(f"数据点数量: {len(first_indicator['times'])}")
            print(f"时间范围: {first_indicator['times'][0]} 到 {first_indicator['times'][-1]}")
            
            # 检查是否包含2026年数据
            has_2026 = any('2026' in t for t in first_indicator['times'])
            print(f"包含2026年数据: {has_2026}")
            
            if has_2026:
                print("2026年数据点:")
                for i, time in enumerate(first_indicator['times']):
                    if '2026' in time:
                        value = first_indicator['values'][i]
                        is_pred = first_indicator['is_predicted'][i]
                        print(f"  {time}: {value} (预测: {is_pred})")
            else:
                print("最后10个数据点:")
                for i in range(max(0, len(first_indicator['times']) - 10), len(first_indicator['times'])):
                    time = first_indicator['times'][i]
                    value = first_indicator['values'][i]
                    is_pred = first_indicator['is_predicted'][i]
                    print(f"  {time}: {value} (预测: {is_pred})")
        
        # 测试搜索功能，看看能否找到包含2026年数据的指标
        print(f"\n测试搜索功能...")
        search_response = requests.get(f"{base_url}/api/monthly-prediction-data?page=1&page_size=10&search=利率")
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            print(f"搜索'利率'结果: {len(search_data['data'])} 个指标")
            
            for indicator in search_data['data']:
                has_2026 = any('2026' in t for t in indicator['times'])
                print(f"  {indicator['title']}: 包含2026年数据 = {has_2026}")
                if has_2026:
                    print(f"    时间范围: {indicator['times'][0]} 到 {indicator['times'][-1]}")
        
        # 测试最后几页，看看是否有指标包含2026年数据
        print(f"\n测试最后几页数据...")
        total_pages = data['total_pages']
        
        for page in range(max(1, total_pages - 2), total_pages + 1):
            print(f"检查第{page}页...")
            page_response = requests.get(f"{base_url}/api/monthly-prediction-data?page={page}&page_size=5")
            
            if page_response.status_code == 200:
                page_data = page_response.json()
                
                for indicator in page_data['data']:
                    has_2026 = any('2026' in t for t in indicator['times'])
                    if has_2026:
                        print(f"  找到包含2026年数据的指标: {indicator['title']}")
                        print(f"    时间范围: {indicator['times'][0]} 到 {indicator['times'][-1]}")
                        
                        # 显示2026年的数据点
                        for i, time in enumerate(indicator['times']):
                            if '2026' in time:
                                value = indicator['values'][i]
                                is_pred = indicator['is_predicted'][i]
                                print(f"    {time}: {value} (预测: {is_pred})")
                        return True
        
        print("未找到包含2026年数据的指标")
        return False
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("开始测试API 2026年数据")
    print("当前时间:", json.dumps({"timestamp": "2025-08-05 13:27:00"}))
    print()
    
    success = test_api_2026_data()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 找到了2026年数据！")
    else:
        print("❌ 没有找到2026年数据")
        print("\n可能的原因:")
        print("1. 后端服务没有重新加载更新后的数据文件")
        print("2. API处理逻辑有问题，过滤掉了2026年数据")
        print("3. 数据文件更新不完整")
        print("4. 缓存问题")
    print("=" * 60)

if __name__ == "__main__":
    main()
