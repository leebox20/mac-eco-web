#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新月度数据完整合并结果.csv文件
将新的预测数据（2025年8月-2026年1月）合并到现有文件中
"""

import pandas as pd
import os
import shutil
from datetime import datetime

def backup_file(file_path):
    """备份原文件"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_path)
        print(f"已备份原文件: {backup_path}")
        return backup_path
    return None

def update_merged_data():
    """更新月度数据完整合并结果.csv"""
    print("=" * 60)
    print("更新月度数据完整合并结果.csv")
    print("=" * 60)
    
    # 文件路径
    new_data_file = "update/月度数据预测结果.csv"
    target_file = "update/月度数据完整合并结果.csv"
    
    # 检查文件是否存在
    if not os.path.exists(new_data_file):
        print(f"错误: 新数据文件不存在 {new_data_file}")
        return False
    
    if not os.path.exists(target_file):
        print(f"错误: 目标文件不存在 {target_file}")
        return False
    
    try:
        # 备份原文件
        backup_file(target_file)
        
        # 读取新数据（2025年8月-2026年1月）
        print(f"读取新数据文件: {new_data_file}")
        df_new = pd.read_csv(new_data_file, encoding='utf-8')
        print(f"新数据形状: {df_new.shape}")
        print(f"新数据时间范围: {df_new['timestamp'].min()} 到 {df_new['timestamp'].max()}")
        
        # 读取现有合并数据
        print(f"读取现有合并数据: {target_file}")
        df_existing = pd.read_csv(target_file, encoding='utf-8')
        print(f"现有数据形状: {df_existing.shape}")
        print(f"现有数据时间范围: {df_existing['timestamp'].min()} 到 {df_existing['timestamp'].max()}")
        
        # 转换时间格式以便比较
        df_new['timestamp_date'] = pd.to_datetime(df_new['timestamp'])
        df_existing['timestamp_date'] = pd.to_datetime(df_existing['timestamp'])
        
        # 找出新数据的时间范围
        new_start_date = df_new['timestamp_date'].min()
        new_end_date = df_new['timestamp_date'].max()
        print(f"新数据时间范围: {new_start_date} 到 {new_end_date}")
        
        # 删除现有数据中与新数据重叠的时间点
        df_existing_filtered = df_existing[
            (df_existing['timestamp_date'] < new_start_date) | 
            (df_existing['timestamp_date'] > new_end_date)
        ]
        print(f"过滤后现有数据形状: {df_existing_filtered.shape}")
        
        # 检查列名是否匹配
        existing_cols = set(df_existing.columns) - {'timestamp_date'}
        new_cols = set(df_new.columns)
        
        print(f"现有数据列数: {len(existing_cols)}")
        print(f"新数据列数: {len(new_cols)}")
        
        # 找出共同的列
        common_cols = existing_cols.intersection(new_cols)
        print(f"共同列数: {len(common_cols)}")
        
        # 如果列不完全匹配，需要处理
        if len(common_cols) < len(new_cols):
            print("警告: 新数据包含现有数据中没有的列")
            missing_in_existing = new_cols - existing_cols
            print(f"现有数据中缺少的列: {list(missing_in_existing)[:10]}...")  # 只显示前10个
            
            # 为现有数据添加缺少的列（填充NaN）
            for col in missing_in_existing:
                if col != 'timestamp_date':
                    df_existing_filtered[col] = float('nan')
        
        if len(common_cols) < len(existing_cols):
            print("警告: 现有数据包含新数据中没有的列")
            missing_in_new = existing_cols - new_cols
            print(f"新数据中缺少的列: {list(missing_in_new)[:10]}...")  # 只显示前10个
            
            # 为新数据添加缺少的列（填充NaN）
            for col in missing_in_new:
                if col != 'timestamp_date':
                    df_new[col] = float('nan')
        
        # 确保列顺序一致
        all_cols = ['timestamp'] + sorted([col for col in df_existing.columns if col not in ['timestamp', 'timestamp_date']])
        
        # 重新排列列顺序
        df_existing_filtered = df_existing_filtered[all_cols + ['timestamp_date']]
        df_new = df_new.reindex(columns=all_cols + ['timestamp_date'])
        
        # 合并数据
        df_combined = pd.concat([
            df_existing_filtered, 
            df_new
        ], ignore_index=True)
        
        # 按时间排序
        df_combined = df_combined.sort_values('timestamp_date')
        
        # 删除辅助列
        df_combined = df_combined.drop('timestamp_date', axis=1)
        
        print(f"合并后数据形状: {df_combined.shape}")
        print(f"合并后时间范围: {df_combined['timestamp'].min()} 到 {df_combined['timestamp'].max()}")
        
        # 检查2026年1月的数据
        df_combined['temp_date'] = pd.to_datetime(df_combined['timestamp'])
        jan_2026_data = df_combined[
            (df_combined['temp_date'].dt.year == 2026) & 
            (df_combined['temp_date'].dt.month == 1)
        ]
        print(f"2026年1月数据条数: {len(jan_2026_data)}")
        if len(jan_2026_data) > 0:
            print(f"2026年1月数据时间点: {jan_2026_data['timestamp'].tolist()}")
        
        df_combined = df_combined.drop('temp_date', axis=1)
        
        # 保存更新后的数据
        df_combined.to_csv(target_file, index=False, encoding='utf-8')
        print(f"已更新文件: {target_file}")
        
        return True
        
    except Exception as e:
        print(f"更新合并数据时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始更新月度数据完整合并结果文件")
    print("当前时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    if update_merged_data():
        print()
        print("=" * 60)
        print("✅ 月度数据完整合并结果文件更新成功！")
        print("现在数据库组件应该能显示2026年1月的数据了。")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("❌ 月度数据完整合并结果文件更新失败！")
        print("=" * 60)

if __name__ == "__main__":
    main()
