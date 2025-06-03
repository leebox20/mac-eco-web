#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
月度数据整合脚本
整合月度历史数据和预测数据，生成完整的月度数据文件
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def read_csv_with_encoding(file_path):
    """尝试不同编码读取CSV文件"""
    encodings = ['gbk', 'gb2312', 'utf-8', 'utf-8-sig']
    
    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            print(f"成功使用 {encoding} 编码读取文件: {file_path}")
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"使用 {encoding} 编码读取文件失败: {e}")
            continue
    
    raise Exception(f"无法读取文件 {file_path}，尝试了所有编码方式")

def convert_date_format(date_str):
    """转换日期格式"""
    if pd.isna(date_str):
        return None

    date_str = str(date_str).strip()

    # 处理不同的日期格式
    try:
        # 格式: 2025/6/30, 2025/7/31 等
        if '/' in date_str and len(date_str.split('/')) == 3:
            parts = date_str.split('/')
            year, month, day = parts
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        # 格式: 2001M1, 2001-01, 2001/01
        elif 'M' in date_str and len(date_str.split('M')) == 2:
            year, month = date_str.split('M')
            if year.isdigit() and month.isdigit():
                return f"{year}-{month.zfill(2)}-01"
        elif '-' in date_str and len(date_str.split('-')) == 2:
            year, month = date_str.split('-')
            if year.isdigit() and month.isdigit():
                return f"{year}-{month.zfill(2)}-01"
        elif '/' in date_str and len(date_str.split('/')) == 2:
            year, month = date_str.split('/')
            if year.isdigit() and month.isdigit():
                return f"{year}-{month.zfill(2)}-01"
        # 已经是标准格式
        elif len(date_str) == 10 and date_str.count('-') == 2:
            return date_str
        else:
            return None
    except Exception as e:
        return None

def process_monthly_historical_data():
    """处理月度历史数据"""
    print("正在读取月度历史数据...")

    # 读取月度金融数据
    monthly_financial = read_csv_with_encoding('社科数值混频模型数据20250527/DATALF-250527-monthly.csv')

    # 读取月度宏观数据
    monthly_macro = read_csv_with_encoding('社科数值混频模型数据20250527/DATADM-250527.csv')

    print(f"月度金融数据形状: {monthly_financial.shape}")
    print(f"月度宏观数据形状: {monthly_macro.shape}")

    # 显示前几行来调试
    print("月度金融数据前几行:")
    print(monthly_financial.head())
    print("\n月度宏观数据前几行:")
    print(monthly_macro.head())

    # 处理金融数据：第一列是日期，其他列是指标
    # 数据结构：行是时间，列是指标，第一列是日期
    monthly_financial_t = monthly_financial.copy()
    monthly_financial_t.rename(columns={'指标名称': 'timestamp'}, inplace=True)

    # 处理宏观数据：第一列是日期，其他列是指标
    monthly_macro_t = monthly_macro.copy()
    monthly_macro_t.rename(columns={'指标名称': 'timestamp'}, inplace=True)

    print(f"转置后金融数据形状: {monthly_financial_t.shape}")
    print(f"转置后宏观数据形状: {monthly_macro_t.shape}")

    print("转置后金融数据前几行:")
    print(monthly_financial_t.head())

    # 转换日期格式
    monthly_financial_t['timestamp'] = monthly_financial_t['timestamp'].apply(convert_date_format)
    monthly_macro_t['timestamp'] = monthly_macro_t['timestamp'].apply(convert_date_format)

    # 删除无效日期的行
    monthly_financial_t = monthly_financial_t.dropna(subset=['timestamp'])
    monthly_macro_t = monthly_macro_t.dropna(subset=['timestamp'])

    print(f"过滤后金融数据形状: {monthly_financial_t.shape}")
    print(f"过滤后宏观数据形状: {monthly_macro_t.shape}")

    # 合并两个数据集
    print("正在合并历史数据...")
    historical_data = pd.merge(monthly_financial_t, monthly_macro_t, on='timestamp', how='outer', suffixes=('', '_macro'))

    # 删除重复列
    duplicate_cols = [col for col in historical_data.columns if col.endswith('_macro')]
    for col in duplicate_cols:
        original_col = col.replace('_macro', '')
        if original_col in historical_data.columns:
            # 如果原列有空值，用macro列填充
            historical_data[original_col] = historical_data[original_col].fillna(historical_data[col])
            historical_data.drop(columns=[col], inplace=True)

    print(f"合并后历史数据形状: {historical_data.shape}")
    return historical_data

def process_prediction_data():
    """处理预测数据"""
    print("正在读取预测数据...")

    prediction_data = read_csv_with_encoding('update/月度数据预测结果.csv')
    print(f"预测数据形状: {prediction_data.shape}")

    # 预测数据已经是正确格式（时间戳作为行，指标作为列），无需转置
    # 转换日期格式
    prediction_data['timestamp'] = prediction_data['timestamp'].apply(convert_date_format)
    prediction_data = prediction_data.dropna(subset=['timestamp'])

    print(f"处理后预测数据形状: {prediction_data.shape}")
    return prediction_data

def merge_data(historical_data, prediction_data):
    """合并历史数据和预测数据"""
    print("正在合并历史数据和预测数据...")
    
    # 获取共同的列
    common_columns = set(historical_data.columns) & set(prediction_data.columns)
    print(f"共同列数: {len(common_columns)}")
    
    # 只保留共同的列
    historical_subset = historical_data[list(common_columns)]
    prediction_subset = prediction_data[list(common_columns)]
    
    # 合并数据
    merged_data = pd.concat([historical_subset, prediction_subset], ignore_index=True)

    # 按时间戳排序
    merged_data['timestamp'] = pd.to_datetime(merged_data['timestamp'])
    merged_data = merged_data.sort_values('timestamp')

    # 去重，保留最新的数据
    merged_data = merged_data.drop_duplicates(subset=['timestamp'], keep='last')

    # 重置索引
    merged_data.reset_index(drop=True, inplace=True)

    # 将timestamp列移到第一列
    cols = merged_data.columns.tolist()
    cols.remove('timestamp')
    merged_data = merged_data[['timestamp'] + cols]

    print(f"最终合并数据形状: {merged_data.shape}")
    return merged_data

def main():
    """主函数"""
    try:
        print("开始整合月度数据...")
        
        # 处理历史数据
        historical_data = process_monthly_historical_data()
        
        # 处理预测数据
        prediction_data = process_prediction_data()
        
        # 合并数据
        final_data = merge_data(historical_data, prediction_data)
        
        # 保存结果
        output_file = 'update/月度数据完整合并结果.csv'
        final_data.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"数据整合完成！")
        print(f"输出文件: {output_file}")
        print(f"最终数据形状: {final_data.shape}")
        print(f"时间范围: {final_data['timestamp'].min()} 到 {final_data['timestamp'].max()}")
        print(f"总列数: {len(final_data.columns)}")
        
        # 显示前几行数据
        print("\n前5行数据预览:")
        print(final_data.head())
        
        # 显示列名
        print(f"\n列名 (共{len(final_data.columns)}列):")
        for i, col in enumerate(final_data.columns):
            print(f"{i+1:3d}. {col}")
            
    except Exception as e:
        print(f"数据整合过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
