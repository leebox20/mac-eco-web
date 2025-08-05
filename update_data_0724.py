#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据更新脚本 - 20250724数据更新
将新的预测数据更新到对应的CSV文件中
"""

import pandas as pd
import os
import shutil
from datetime import datetime
import chardet

def detect_encoding(file_path):
    """检测文件编码"""
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        return result['encoding']

def backup_file(file_path):
    """备份原文件"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_path)
        print(f"已备份原文件: {backup_path}")
        return backup_path
    return None

def update_monthly_key_indicators():
    """更新月度关键数据预测结果含区间.csv"""
    print("=" * 60)
    print("更新月度关键数据预测结果含区间.csv")
    print("=" * 60)
    
    # 文件路径
    new_data_file = "20250724数据更新/月度关键数据预测结果0724.csv"
    target_file = "update/月度关键数据预测结果含区间.csv"
    
    # 检查新数据文件是否存在
    if not os.path.exists(new_data_file):
        print(f"错误: 新数据文件不存在 {new_data_file}")
        return False
    
    try:
        # 备份原文件
        backup_file(target_file)
        
        # 读取新数据
        print(f"读取新数据文件: {new_data_file}")
        df_new = pd.read_csv(new_data_file, encoding='utf-8')
        print(f"新数据形状: {df_new.shape}")
        print(f"新数据时间范围: {df_new['timestamp'].min()} 到 {df_new['timestamp'].max()}")
        
        # 读取现有数据
        if os.path.exists(target_file):
            print(f"读取现有数据文件: {target_file}")
            df_existing = pd.read_csv(target_file, encoding='utf-8')
            print(f"现有数据形状: {df_existing.shape}")
            print(f"现有数据时间范围: {df_existing['timestamp'].min()} 到 {df_existing['timestamp'].max()}")
            
            # 转换时间格式以便比较
            df_new['timestamp_date'] = pd.to_datetime(df_new['timestamp'])
            df_existing['timestamp_date'] = pd.to_datetime(df_existing['timestamp'])
            
            # 找出需要更新的数据（新数据中的时间点）
            new_dates = set(df_new['timestamp_date'])
            existing_dates = set(df_existing['timestamp_date'])
            
            # 删除现有数据中与新数据重叠的时间点
            df_existing_filtered = df_existing[~df_existing['timestamp_date'].isin(new_dates)]
            
            # 合并数据
            df_combined = pd.concat([df_existing_filtered.drop('timestamp_date', axis=1), 
                                   df_new.drop('timestamp_date', axis=1)], 
                                  ignore_index=True)
            
            # 按时间排序
            df_combined['timestamp_date'] = pd.to_datetime(df_combined['timestamp'])
            df_combined = df_combined.sort_values('timestamp_date').drop('timestamp_date', axis=1)
            
        else:
            print("目标文件不存在，直接使用新数据")
            df_combined = df_new
        
        # 保存更新后的数据
        df_combined.to_csv(target_file, index=False, encoding='utf-8')
        print(f"已更新文件: {target_file}")
        print(f"更新后数据形状: {df_combined.shape}")
        print(f"更新后时间范围: {df_combined['timestamp'].min()} 到 {df_combined['timestamp'].max()}")
        
        return True
        
    except Exception as e:
        print(f"更新月度关键数据时出错: {str(e)}")
        return False

def update_gdp_data():
    """更新GDP季度数据"""
    print("=" * 60)
    print("更新GDP季度数据")
    print("=" * 60)
    
    # 文件路径
    new_data_file = "20250724数据更新/季度数据预测结果0724.csv"
    target_file = "backend/data/gdp_complete_data.csv"
    
    # 检查新数据文件是否存在
    if not os.path.exists(new_data_file):
        print(f"错误: 新数据文件不存在 {new_data_file}")
        return False
    
    try:
        # 备份原文件
        backup_file(target_file)
        
        # 读取新数据（使用GB2312编码）
        print(f"读取新数据文件: {new_data_file}")
        df_new = pd.read_csv(new_data_file, encoding='gb2312')
        print(f"新数据形状: {df_new.shape}")
        print("新数据列名:", df_new.columns.tolist())
        print("新数据内容:")
        print(df_new)
        
        # 处理新数据格式
        # 重命名列名
        df_new.columns = ['quarter', 'gdp_value', 'gdp_value_variation']
        
        # 转换季度格式为日期
        def quarter_to_date(quarter_str):
            year, q = quarter_str.split('Q')
            if q == '1':
                return f"{year}-03-31"
            elif q == '2':
                return f"{year}-06-30"
            elif q == '3':
                return f"{year}-09-30"
            elif q == '4':
                return f"{year}-12-31"
        
        df_new['date'] = df_new['quarter'].apply(quarter_to_date)
        df_new['is_predicted'] = True
        
        # 计算置信区间
        df_new['confidence_interval'] = df_new.apply(
            lambda row: f"[{row['gdp_value'] - row['gdp_value_variation']}, {row['gdp_value'] + row['gdp_value_variation']}]",
            axis=1
        )
        
        # 选择需要的列
        df_new_formatted = df_new[['date', 'quarter', 'gdp_value', 'is_predicted', 'confidence_interval']]
        
        print("处理后的新数据:")
        print(df_new_formatted)
        
        # 读取现有数据
        if os.path.exists(target_file):
            print(f"读取现有数据文件: {target_file}")
            df_existing = pd.read_csv(target_file, encoding='utf-8')
            print(f"现有数据形状: {df_existing.shape}")
            
            # 找出需要更新的季度
            new_quarters = set(df_new_formatted['quarter'])
            
            # 删除现有数据中与新数据重叠的季度
            df_existing_filtered = df_existing[~df_existing['quarter'].isin(new_quarters)]
            
            # 合并数据
            df_combined = pd.concat([df_existing_filtered, df_new_formatted], ignore_index=True)
            
            # 按日期排序
            df_combined['date'] = pd.to_datetime(df_combined['date'])
            df_combined = df_combined.sort_values('date')
            df_combined['date'] = df_combined['date'].dt.strftime('%Y-%m-%d')
            
        else:
            print("目标文件不存在，直接使用新数据")
            df_combined = df_new_formatted
        
        # 保存更新后的数据
        df_combined.to_csv(target_file, index=False, encoding='utf-8')
        print(f"已更新文件: {target_file}")
        print(f"更新后数据形状: {df_combined.shape}")
        print(f"更新后季度范围: {df_combined['quarter'].min()} 到 {df_combined['quarter'].max()}")
        
        return True
        
    except Exception as e:
        print(f"更新GDP数据时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def update_monthly_prediction_data():
    """更新月度数据预测结果"""
    print("=" * 60)
    print("更新月度数据预测结果")
    print("=" * 60)
    
    # 文件路径
    new_data_file = "20250724数据更新/月度数据预测结果0724.csv"
    target_file = "update/月度数据预测结果.csv"
    
    # 检查新数据文件是否存在
    if not os.path.exists(new_data_file):
        print(f"警告: 新数据文件不存在 {new_data_file}，跳过此更新")
        return True
    
    try:
        # 备份原文件
        backup_file(target_file)
        
        # 读取新数据
        print(f"读取新数据文件: {new_data_file}")
        df_new = pd.read_csv(new_data_file, encoding='utf-8')
        print(f"新数据形状: {df_new.shape}")
        print(f"新数据列数: {len(df_new.columns)}")
        
        # 直接替换目标文件（因为这是完整的月度数据预测结果）
        df_new.to_csv(target_file, index=False, encoding='utf-8')
        print(f"已更新文件: {target_file}")
        
        return True
        
    except Exception as e:
        print(f"更新月度数据预测结果时出错: {str(e)}")
        return False

def main():
    """主函数"""
    print("开始数据更新 - 20250724")
    print("当前时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    success_count = 0
    total_count = 3
    
    # 1. 更新月度关键数据预测结果含区间
    if update_monthly_key_indicators():
        success_count += 1
    
    print()
    
    # 2. 更新GDP季度数据
    if update_gdp_data():
        success_count += 1
    
    print()
    
    # 3. 更新月度数据预测结果
    if update_monthly_prediction_data():
        success_count += 1
    
    print()
    print("=" * 60)
    print(f"数据更新完成: {success_count}/{total_count} 个文件更新成功")
    print("=" * 60)
    
    if success_count == total_count:
        print("✅ 所有数据更新成功！")
    else:
        print("⚠️  部分数据更新失败，请检查错误信息")

if __name__ == "__main__":
    main()
