#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建完整的GDP数据文件：合并历史数据和新预测数据
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def create_complete_gdp_data():
    """创建完整的GDP数据文件"""
    print("🔧 开始创建完整的GDP数据...")
    
    # 1. 读取历史GDP数据
    print("📖 读取历史GDP数据...")
    
    historical_gdp_file = 'data/seasonal_gdp.csv'
    if not os.path.exists(historical_gdp_file):
        print(f"❌ 历史GDP文件不存在: {historical_gdp_file}")
        return
    
    # 读取历史数据
    df_historical = pd.read_csv(historical_gdp_file, encoding='utf-8')
    print(f"历史数据形状: {df_historical.shape}")
    print(f"历史数据列名: {list(df_historical.columns)}")
    
    # 2. 处理历史数据
    print("🧹 处理历史数据...")
    
    # 重命名列
    df_historical.columns = ['quarter', 'gdp_value']
    
    # 清理数据
    df_historical['gdp_value'] = df_historical['gdp_value'].astype(str).str.strip()
    
    # 处理包含±的预测值
    processed_data = []
    for _, row in df_historical.iterrows():
        quarter = row['quarter']
        gdp_str = row['gdp_value']
        
        # 跳过空值
        if pd.isna(gdp_str) or gdp_str == '' or gdp_str == 'nan':
            continue
            
        # 处理预测区间
        if '±' in gdp_str:
            base_value, interval = gdp_str.split('±')
            gdp_value = float(base_value)
            confidence_interval = float(interval)
            is_predicted = True
        else:
            gdp_value = float(gdp_str)
            confidence_interval = None
            is_predicted = False
        
        # 转换季度格式：2024Q1 -> 2024-03-31
        try:
            year = int(quarter[:4])
            quarter_num = int(quarter[5:])
            
            # 季度末日期映射
            quarter_end_dates = {
                1: f"{year}-03-31",
                2: f"{year}-06-30", 
                3: f"{year}-09-30",
                4: f"{year}-12-31"
            }
            
            date = quarter_end_dates[quarter_num]
            
            processed_data.append({
                'date': date,
                'quarter': quarter,
                'gdp_value': gdp_value,
                'confidence_interval': confidence_interval,
                'is_predicted': is_predicted
            })
            
        except (ValueError, KeyError) as e:
            print(f"⚠️ 跳过无效季度: {quarter}, 错误: {e}")
            continue
    
    # 创建处理后的DataFrame
    df_processed = pd.DataFrame(processed_data)
    
    # 3. 添加新的预测数据
    print("📊 添加新的预测数据...")
    
    # 老师提供的新预测数据
    new_predictions = [
        {'date': '2025-06-30', 'quarter': '2025Q2', 'gdp_value': 4.857564, 'confidence_interval': None, 'is_predicted': True},
        {'date': '2025-09-30', 'quarter': '2025Q3', 'gdp_value': 5.492128, 'confidence_interval': None, 'is_predicted': True},
        {'date': '2025-12-31', 'quarter': '2025Q4', 'gdp_value': 5.112863, 'confidence_interval': None, 'is_predicted': True}
    ]
    
    # 添加新预测数据
    for pred in new_predictions:
        # 检查是否已存在该季度的数据
        existing = df_processed[df_processed['quarter'] == pred['quarter']]
        if existing.empty:
            df_processed = pd.concat([df_processed, pd.DataFrame([pred])], ignore_index=True)
        else:
            # 更新现有数据
            idx = existing.index[0]
            df_processed.loc[idx, 'gdp_value'] = pred['gdp_value']
            df_processed.loc[idx, 'is_predicted'] = True
            print(f"✅ 更新了 {pred['quarter']} 的预测值: {pred['gdp_value']}")
    
    # 4. 排序和最终处理
    print("📅 排序和最终处理...")
    
    # 转换日期并排序
    df_processed['date'] = pd.to_datetime(df_processed['date'])
    df_processed = df_processed.sort_values('date').reset_index(drop=True)
    
    # 5. 保存完整的GDP数据
    output_file = 'backend/data/gdp_complete_data.csv'
    print(f"💾 保存完整GDP数据到: {output_file}")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 保存为CSV
    df_output = df_processed.copy()
    df_output['date'] = df_output['date'].dt.strftime('%Y-%m-%d')
    df_output.to_csv(output_file, index=False, encoding='utf-8')
    
    # 6. 创建API格式的数据
    print("🔄 创建API格式数据...")
    
    # 准备API返回格式
    api_data = {
        'dates': df_output['date'].tolist(),
        'quarters': df_output['quarter'].tolist(),
        'values': df_output['gdp_value'].tolist(),
        'is_predicted': df_output['is_predicted'].tolist(),
        'confidence_intervals': df_output['confidence_interval'].tolist()
    }
    
    # 保存JSON格式（可选）
    import json
    json_file = 'backend/data/gdp_api_data.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(api_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ GDP数据创建完成!")
    print(f"📊 最终数据统计:")
    print(f"   - 总记录数: {len(df_output)}")
    print(f"   - 日期范围: {df_output['date'].min()} 到 {df_output['date'].max()}")
    print(f"   - 历史数据: {len(df_output[~df_output['is_predicted']])} 条")
    print(f"   - 预测数据: {len(df_output[df_output['is_predicted']])} 条")
    print(f"   - 最新GDP值: {df_output['gdp_value'].iloc[-1]}% ({df_output['quarter'].iloc[-1]})")
    
    # 显示最近几个季度的数据
    print(f"\n🎯 最近5个季度的GDP数据:")
    recent_data = df_output.tail(5)
    for _, row in recent_data.iterrows():
        status = "预测" if row['is_predicted'] else "历史"
        print(f"   {row['quarter']}: {row['gdp_value']}% ({status})")
    
    return df_output

if __name__ == "__main__":
    try:
        df = create_complete_gdp_data()
        
        if df is not None:
            print("\n🎉 GDP数据创建完成！")
            print("📝 下一步操作:")
            print("1. 创建GDP API端点")
            print("2. 修改首页调用逻辑")
            print("3. 测试新的GDP数据显示")
        
    except Exception as e:
        print(f"❌ 创建过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
