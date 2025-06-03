#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试更新后的GDP数据
"""

import pandas as pd
import json
import os
from datetime import datetime

def test_gdp_data():
    """测试GDP数据的完整性和正确性"""
    print("🔍 开始测试GDP数据...")
    
    # 1. 测试CSV文件
    print("\n📊 测试CSV文件...")
    csv_file = 'backend/data/gdp_complete_data.csv'
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file, encoding='utf-8')
        print(f"CSV文件记录数: {len(df)}")
        print(f"日期范围: {df['date'].min()} 到 {df['date'].max()}")
        
        # 检查最近的数据
        recent_data = df.tail(10)
        print("\n最近10条记录:")
        for _, row in recent_data.iterrows():
            status = "预测" if row['is_predicted'] else "历史"
            interval_info = f", 区间: ±{row['confidence_interval']}" if pd.notna(row['confidence_interval']) else ""
            print(f"  {row['quarter']}: {row['gdp_value']}% ({status}{interval_info})")
        
        # 检查数据分布
        historical_count = len(df[~df['is_predicted']])
        predicted_count = len(df[df['is_predicted']])
        print(f"\n数据分布: 历史数据 {historical_count} 条, 预测数据 {predicted_count} 条")
        
        # 检查置信区间
        with_interval = len(df[pd.notna(df['confidence_interval'])])
        print(f"含置信区间的数据: {with_interval} 条")
        
    else:
        print("❌ CSV文件不存在")
    
    # 2. 测试JSON文件
    print("\n📄 测试JSON文件...")
    json_file = 'backend/data/gdp_api_data.json'
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"JSON数据记录数: {len(data['quarters'])}")
        print(f"季度范围: {data['quarters'][0]} 到 {data['quarters'][-1]}")
        
        # 检查最近的数据
        print("\n最近5个季度:")
        for i in range(-5, 0):
            quarter = data['quarters'][i]
            value = data['values'][i]
            is_pred = data['is_predicted'][i]
            interval = data['confidence_intervals'][i]
            
            status = "预测" if is_pred else "历史"
            interval_info = f", 区间: ±{interval}" if interval != "NaN" and interval is not None else ""
            print(f"  {quarter}: {value}% ({status}{interval_info})")
        
        # 检查数据一致性
        predicted_count = sum(data['is_predicted'])
        historical_count = len(data['is_predicted']) - predicted_count
        print(f"\n数据分布: 历史数据 {historical_count} 条, 预测数据 {predicted_count} 条")
        
    else:
        print("❌ JSON文件不存在")
    
    # 3. 测试季度区间文件
    print("\n📈 测试季度区间文件...")
    interval_file = 'update/季度关键数据预测结果含区间.csv'
    if os.path.exists(interval_file):
        try:
            df_interval = pd.read_csv(interval_file, encoding='utf-8')
            print(f"区间文件记录数: {len(df_interval)}")
            print("\n区间数据:")
            for _, row in df_interval.iterrows():
                if pd.notna(row.iloc[0]):
                    timestamp = row.iloc[0]
                    gdp_value = row.iloc[1] if len(row) > 1 else "N/A"
                    variation = row.iloc[2] if len(row) > 2 else "N/A"
                    print(f"  {timestamp}: {gdp_value}% ±{variation}")
        except Exception as e:
            print(f"❌ 读取区间文件失败: {e}")
    else:
        print("❌ 季度区间文件不存在")
    
    # 4. 验证时间逻辑
    print("\n⏰ 验证时间逻辑...")
    current_date = datetime(2025, 6, 3)
    print(f"当前时间: {current_date.strftime('%Y年%m月%d日')}")
    
    # 根据当前时间，2024Q4和2025Q1应该是历史数据，2025Q2及以后是预测数据
    expected_historical = ['2024Q4', '2025Q1']
    expected_predicted = ['2025Q2', '2025Q3', '2025Q4']
    
    print(f"预期历史数据季度: {expected_historical}")
    print(f"预期预测数据季度: {expected_predicted}")
    
    print("\n✅ GDP数据测试完成!")

if __name__ == "__main__":
    test_gdp_data()
