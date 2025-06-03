#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复GDP数据重复问题
"""

import pandas as pd
import json
import os
from datetime import datetime

def fix_gdp_data():
    """修复GDP数据重复问题"""
    print("🔧 开始修复GDP数据重复问题...")
    
    # 1. 读取CSV文件并检查重复
    csv_file = 'backend/data/gdp_complete_data.csv'
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file, encoding='utf-8')
        print(f"CSV文件原始记录数: {len(df)}")
        
        # 检查重复的季度
        duplicates = df[df.duplicated(subset=['quarter'], keep=False)]
        if not duplicates.empty:
            print("发现重复的季度数据:")
            print(duplicates[['quarter', 'gdp_value', 'is_predicted']])
            
            # 去重，保留最新的数据
            df_clean = df.drop_duplicates(subset=['quarter'], keep='last')
            df_clean = df_clean.sort_values('date').reset_index(drop=True)
            
            # 保存清理后的数据
            df_clean.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"CSV文件去重后记录数: {len(df_clean)}")
        else:
            print("CSV文件中没有重复数据")
            df_clean = df
    else:
        print("❌ CSV文件不存在")
        return
    
    # 2. 重新生成JSON文件
    print("\n📄 重新生成JSON文件...")
    
    # 准备JSON数据
    json_data = {
        'dates': df_clean['date'].tolist(),
        'quarters': df_clean['quarter'].tolist(),
        'values': df_clean['gdp_value'].tolist(),
        'is_predicted': df_clean['is_predicted'].tolist(),
        'confidence_intervals': df_clean['confidence_interval'].fillna('NaN').tolist(),
        'total_records': len(df_clean),
        'latest_value': float(df_clean['gdp_value'].iloc[-1]),
        'latest_quarter': df_clean['quarter'].iloc[-1],
        'historical_count': len(df_clean[~df_clean['is_predicted']]),
        'predicted_count': len(df_clean[df_clean['is_predicted']])
    }
    
    # 保存JSON文件
    json_file = 'backend/data/gdp_api_data.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"JSON文件已更新，记录数: {len(df_clean)}")
    
    # 3. 验证数据
    print("\n✅ 验证修复后的数据:")
    print(f"总记录数: {len(df_clean)}")
    print(f"历史数据: {json_data['historical_count']} 条")
    print(f"预测数据: {json_data['predicted_count']} 条")
    print(f"最新季度: {json_data['latest_quarter']}")
    print(f"最新数值: {json_data['latest_value']}%")
    
    # 显示最近的数据
    print("\n最近10个季度的数据:")
    recent_data = df_clean.tail(10)
    for _, row in recent_data.iterrows():
        status = "预测" if row['is_predicted'] else "历史"
        interval_info = f", 区间: ±{row['confidence_interval']}" if pd.notna(row['confidence_interval']) else ""
        print(f"  {row['quarter']}: {row['gdp_value']}% ({status}{interval_info})")
    
    # 4. 检查特定的季度
    print("\n🔍 检查关键季度:")
    key_quarters = ['2024Q4', '2025Q1', '2025Q2']
    for quarter in key_quarters:
        quarter_data = df_clean[df_clean['quarter'] == quarter]
        if not quarter_data.empty:
            row = quarter_data.iloc[0]
            status = "预测" if row['is_predicted'] else "历史"
            interval_info = f", 区间: ±{row['confidence_interval']}" if pd.notna(row['confidence_interval']) else ""
            print(f"  {quarter}: {row['gdp_value']}% ({status}{interval_info})")
        else:
            print(f"  {quarter}: 数据缺失")
    
    print("\n✅ GDP数据修复完成!")

if __name__ == "__main__":
    fix_gdp_data()
