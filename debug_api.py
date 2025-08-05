#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试API数据处理问题
"""

import pandas as pd
import os

def debug_monthly_prediction_data():
    """调试月度预测数据API"""
    print("=" * 60)
    print("调试月度预测数据API")
    print("=" * 60)
    
    # 文件路径
    merged_file = "update/月度数据完整合并结果.csv"
    
    if not os.path.exists(merged_file):
        print(f"错误: 文件不存在 {merged_file}")
        return
    
    try:
        # 读取数据
        df = pd.read_csv(merged_file, encoding='utf-8')
        print(f"数据形状: {df.shape}")
        
        time_column = 'timestamp'
        df[time_column] = pd.to_datetime(df[time_column])
        
        # 检查第一个数据列
        first_data_col = df.columns[1]
        print(f"第一个数据列: {first_data_col}")
        
        # 找到该列第一个非空值的位置
        first_valid_idx = df[first_data_col].first_valid_index()
        print(f"第一个非空值索引: {first_valid_idx}")
        
        # 从第一个非空值开始处理数据
        column_data = df.loc[first_valid_idx:].copy()
        print(f"从第一个非空值开始的数据形状: {column_data.shape}")
        
        # 模拟API处理逻辑
        times = []
        values = []
        is_predicted = []
        
        print("\n处理数据...")
        processed_count = 0
        skipped_count = 0
        
        for idx, row in column_data.iterrows():
            # 只处理非空值
            if pd.notna(row[first_data_col]):
                date_str = row[time_column].strftime('%Y-%m-%d')
                
                # 处理数值格式
                value_str = str(row[first_data_col]).strip()
                is_pred = False
                
                if not value_str or value_str.lower() == 'nan':
                    skipped_count += 1
                    continue
                
                # 检查预测标记
                if '(预测)' in value_str:
                    is_pred = True
                    value_str = value_str.replace('(预测)', '').strip()
                
                # 移除逗号并转换为浮点数
                try:
                    clean_value = value_str.replace(',', '')
                    if not clean_value:
                        skipped_count += 1
                        continue
                    
                    float_value = float(clean_value)
                    times.append(date_str)
                    values.append(float_value)
                    is_predicted.append(is_pred)
                    processed_count += 1
                    
                    # 打印最后几个数据点
                    if processed_count > len(column_data) - 10:
                        print(f"  {date_str}: {float_value} (预测: {is_pred})")
                    
                except (ValueError, TypeError) as e:
                    print(f"  转换失败 {date_str}: {value_str} - {e}")
                    skipped_count += 1
                    continue
        
        print(f"\n处理结果:")
        print(f"  成功处理: {processed_count} 个数据点")
        print(f"  跳过: {skipped_count} 个数据点")
        print(f"  时间范围: {times[0] if times else 'N/A'} 到 {times[-1] if times else 'N/A'}")
        
        # 检查2026年1月的数据
        jan_2026_times = [t for t in times if t.startswith('2026-01')]
        print(f"  2026年1月数据点: {len(jan_2026_times)}")
        if jan_2026_times:
            print(f"  2026年1月时间点: {jan_2026_times}")
        
        # 检查最后10个时间点
        print(f"  最后10个时间点: {times[-10:] if len(times) >= 10 else times}")
        
        return {
            'times': times,
            'values': values,
            'is_predicted': is_predicted,
            'total_processed': processed_count,
            'total_skipped': skipped_count
        }
        
    except Exception as e:
        print(f"调试时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def check_data_consistency():
    """检查数据一致性"""
    print("\n" + "=" * 60)
    print("检查数据一致性")
    print("=" * 60)
    
    merged_file = "update/月度数据完整合并结果.csv"
    df = pd.read_csv(merged_file, encoding='utf-8')
    
    # 检查时间列
    print(f"时间列名: {df.columns[0]}")
    print(f"数据行数: {len(df)}")
    
    # 转换时间
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 检查时间范围
    print(f"时间范围: {df['timestamp'].min()} 到 {df['timestamp'].max()}")
    
    # 检查2025-2026年的数据
    recent_data = df[df['timestamp'] >= '2025-01-01']
    print(f"2025年以后数据行数: {len(recent_data)}")
    
    print("2025年以后的时间点:")
    for ts in recent_data['timestamp']:
        print(f"  {ts.strftime('%Y-%m-%d')}")
    
    # 检查第一个数据列的非空值
    first_data_col = df.columns[1]
    print(f"\n第一个数据列: {first_data_col}")
    
    recent_non_null = recent_data[recent_data[first_data_col].notna()]
    print(f"2025年以后非空数据行数: {len(recent_non_null)}")
    
    print("2025年以后非空数据:")
    for _, row in recent_non_null.iterrows():
        ts = row['timestamp'].strftime('%Y-%m-%d')
        val = row[first_data_col]
        print(f"  {ts}: {val}")

def main():
    """主函数"""
    print("开始调试API数据处理问题")
    print("当前时间:", pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    # 检查数据一致性
    check_data_consistency()
    
    # 调试API处理逻辑
    result = debug_monthly_prediction_data()
    
    if result:
        print("\n" + "=" * 60)
        print("调试完成")
        print("=" * 60)
        
        if '2026-01-31' in result['times']:
            print("✅ 2026年1月数据存在于处理结果中")
        else:
            print("❌ 2026年1月数据不在处理结果中")
            print("可能的原因:")
            print("1. 数据文件中没有2026年1月的数据")
            print("2. 数据值为空或无效")
            print("3. 数据处理逻辑有问题")
    else:
        print("调试失败")

if __name__ == "__main__":
    main()
