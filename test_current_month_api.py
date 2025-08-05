#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime

def test_key_indicators_api():
    """测试修改后的关键指标API"""
    print("🧪 测试关键指标API - 当前时间点数据")
    print("=" * 60)
    
    # API端点
    url = "http://120.48.150.254:8888/api/key-indicators"
    
    try:
        # 发送请求
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API响应成功，状态码: {response.status_code}")
            print(f"📊 总指标数: {data.get('total_indicators', 0)}")
            print(f"🕐 更新时间: {data.get('update_time', 'N/A')}")
            
            # 当前时间信息
            current_date = datetime.now()
            current_year = current_date.year
            current_month = current_date.month

            # 经济数据通常滞后发布，计算实际可获得的最新数据时间点
            # 确定可获得的最新季度数据（滞后1个季度）
            if current_month <= 3:
                # 1-3月，最新季度数据是去年Q4
                expected_quarter = f"{current_year-1}Q4"
            elif current_month <= 6:
                # 4-6月，最新季度数据是今年Q1
                expected_quarter = f"{current_year}Q1"
            elif current_month <= 9:
                # 7-9月，最新季度数据是今年Q2
                expected_quarter = f"{current_year}Q2"
            else:
                # 10-12月，最新季度数据是今年Q3
                expected_quarter = f"{current_year}Q3"

            # 确定可获得的最新月度数据（滞后1个月）
            if current_month == 1:
                # 1月，最新月度数据是去年12月
                expected_month_year = current_year - 1
                expected_month_num = 12
            else:
                # 其他月份，最新月度数据是上个月
                expected_month_year = current_year
                expected_month_num = current_month - 1

            expected_month_str = f"{expected_month_year}-{expected_month_num:02d}"
            
            print(f"\n📅 当前时间: {current_date.strftime('%Y-%m-%d')}")
            print(f"📅 期望季度: {expected_quarter} (滞后1个季度)")
            print(f"📅 期望月份: {expected_month_str} (滞后1个月)")
            
            # 检查GDP数据
            print(f"\n🏢 GDP数据:")
            gdp_data = data.get('gdp')
            if gdp_data:
                print(f"  名称: {gdp_data.get('name')}")
                print(f"  数值: {gdp_data.get('value')}%")
                print(f"  季度: {gdp_data.get('quarter')}")
                print(f"  预测数据: {gdp_data.get('is_predicted')}")
                
                # 检查是否返回了期望的季度
                if gdp_data.get('quarter') == expected_quarter:
                    print(f"  ✅ 正确返回期望季度 {expected_quarter} 的数据")
                else:
                    print(f"  ⚠️  返回的季度 {gdp_data.get('quarter')} 不是期望季度 {expected_quarter}")
            else:
                print("  ❌ 未找到GDP数据")
            
            # 检查月度指标数据
            print(f"\n📈 月度指标数据:")
            monthly_indicators = data.get('monthly_indicators', [])
            print(f"  月度指标数量: {len(monthly_indicators)}")
            
            for indicator in monthly_indicators:
                name = indicator.get('name')
                value = indicator.get('value')
                date = indicator.get('date')
                unit = indicator.get('unit')
                is_predicted = indicator.get('is_predicted')
                confidence_interval = indicator.get('confidence_interval')
                
                print(f"\n  📊 {name}:")
                print(f"    数值: {value}{unit}")
                print(f"    日期: {date}")
                print(f"    预测数据: {is_predicted}")
                if confidence_interval:
                    print(f"    置信区间: [{confidence_interval[0]:.2f}, {confidence_interval[1]:.2f}]")
                
                # 检查是否返回了期望的月份
                if date == expected_month_str:
                    print(f"    ✅ 正确返回期望月份 {expected_month_str} 的数据")
                else:
                    print(f"    ⚠️  返回的月份 {date} 不是期望月份 {expected_month_str}")
            
            # 数据验证总结
            print(f"\n📋 数据验证总结:")
            gdp_correct = gdp_data and gdp_data.get('quarter') == expected_quarter
            monthly_correct = all(indicator.get('date') == expected_month_str for indicator in monthly_indicators)

            print(f"  GDP季度数据正确: {'✅' if gdp_correct else '❌'}")
            print(f"  月度数据正确: {'✅' if monthly_correct else '❌'}")

            if gdp_correct and monthly_correct:
                print(f"\n🎉 所有数据都正确返回了期望时间点的数据（考虑数据发布滞后）！")
            else:
                print(f"\n⚠️  部分数据未返回期望时间点的数据，请检查数据文件")
                
        else:
            print(f"❌ API响应失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端服务正在运行")
        print("启动命令: cd backend && python app.py")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def test_data_files():
    """检查数据文件是否存在"""
    print("\n📁 检查数据文件:")
    print("=" * 60)
    
    import os
    
    files_to_check = [
        'backend/data/gdp_complete_data.csv',
        'update/月度关键数据预测结果含区间.csv',
        'update/月度关键数据预测结果.csv',
        'backend/data/DATAMERGED-20241203-完整数据集-修复版.csv'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  ✅ {file_path} (大小: {size:,} 字节)")
        else:
            print(f"  ❌ {file_path} (不存在)")

if __name__ == "__main__":
    test_data_files()
    test_key_indicators_api()
