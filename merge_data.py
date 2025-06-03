#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据合并脚本：将历史数据和预测数据合并成一个完整的CSV文件
"""

import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def read_prediction_data(prediction_file):
    """读取预测数据文件"""
    logger.info(f"读取预测数据文件: {prediction_file}")
    
    # 尝试不同编码读取文件
    for encoding in ['gbk', 'utf-8', 'gb2312']:
        try:
            df = pd.read_csv(prediction_file, encoding=encoding)
            logger.info(f"预测数据使用 {encoding} 编码读取成功，形状: {df.shape}")
            
            # 处理时间列
            time_column = df.columns[0]
            df[time_column] = pd.to_datetime(df[time_column])
            df = df.rename(columns={time_column: 'date'})
            
            # 删除全为空的行
            df = df.dropna(how='all')
            
            logger.info(f"预测数据处理完成，包含 {len(df.columns)-1} 个指标，{len(df)} 个时间点")
            return df
            
        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.error(f"读取预测数据时出错 (编码: {encoding}): {str(e)}")
            continue
    
    raise Exception("无法读取预测数据文件，尝试了所有编码方式")

def read_historical_data(historical_dir):
    """读取历史数据目录中的所有CSV文件"""
    logger.info(f"读取历史数据目录: {historical_dir}")
    
    # 获取目录中的所有CSV文件
    csv_files = glob.glob(os.path.join(historical_dir, "*.csv"))
    logger.info(f"找到 {len(csv_files)} 个CSV文件")
    
    all_historical_data = {}
    
    for csv_file in csv_files:
        try:
            logger.info(f"处理文件: {os.path.basename(csv_file)}")
            
            # 尝试不同编码读取文件
            df = None
            for encoding in ['gbk', 'utf-8', 'gb2312']:
                try:
                    df = pd.read_csv(csv_file, encoding=encoding)
                    logger.info(f"文件 {os.path.basename(csv_file)} 使用 {encoding} 编码读取成功")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                logger.warning(f"无法读取文件: {csv_file}")
                continue
            
            # 处理数据格式
            if len(df.columns) > 0:
                # 第一列通常是时间或指标名称
                first_col = df.columns[0]
                
                # 检查第一列是否为时间格式
                try:
                    # 尝试将第一列转换为时间
                    df[first_col] = pd.to_datetime(df[first_col])
                    df = df.rename(columns={first_col: 'date'})
                    df = df.set_index('date')
                    
                    # 转置数据，使时间为行，指标为列
                    df = df.T
                    
                    logger.info(f"文件 {os.path.basename(csv_file)} 处理为时间序列格式，形状: {df.shape}")
                    
                except:
                    # 如果第一列不是时间，可能是指标名称在第一列
                    try:
                        df = df.set_index(first_col)
                        # 尝试将列名转换为时间
                        df.columns = pd.to_datetime(df.columns)
                        
                        logger.info(f"文件 {os.path.basename(csv_file)} 处理为指标格式，形状: {df.shape}")
                        
                    except:
                        logger.warning(f"无法确定文件 {os.path.basename(csv_file)} 的格式，跳过")
                        continue
                
                # 存储处理后的数据
                file_key = os.path.splitext(os.path.basename(csv_file))[0]
                all_historical_data[file_key] = df
                
        except Exception as e:
            logger.error(f"处理文件 {csv_file} 时出错: {str(e)}")
            continue
    
    logger.info(f"历史数据读取完成，共处理 {len(all_historical_data)} 个文件")
    return all_historical_data

def merge_data(prediction_df, historical_data_dict):
    """合并预测数据和历史数据"""
    logger.info("开始合并数据...")
    
    # 获取预测数据的指标列表
    prediction_columns = prediction_df.columns[1:]  # 排除date列
    logger.info(f"预测数据包含 {len(prediction_columns)} 个指标")
    
    # 创建合并后的数据框
    merged_data = []
    
    # 处理每个指标
    for column in prediction_columns:
        logger.info(f"处理指标: {column}")
        
        # 收集该指标的所有历史数据
        historical_values = []
        
        # 在所有历史数据文件中查找该指标
        for file_key, hist_df in historical_data_dict.items():
            if column in hist_df.index:
                # 找到了该指标的历史数据
                indicator_data = hist_df.loc[column]
                
                # 转换为时间序列格式
                for date, value in indicator_data.items():
                    if pd.notna(value) and pd.notna(date):
                        try:
                            # 确保日期格式正确
                            if isinstance(date, str):
                                date = pd.to_datetime(date)
                            
                            # 只保留2025年6月之前的历史数据
                            if date < pd.to_datetime('2025-06-01'):
                                historical_values.append({
                                    'date': date,
                                    'value': float(value),
                                    'is_predicted': False
                                })
                        except:
                            continue
        
        # 添加预测数据
        prediction_values = []
        for _, row in prediction_df.iterrows():
            if pd.notna(row[column]) and pd.notna(row['date']):
                prediction_values.append({
                    'date': row['date'],
                    'value': float(row[column]),
                    'is_predicted': True
                })
        
        # 合并历史数据和预测数据
        all_values = historical_values + prediction_values
        
        if all_values:
            # 按日期排序
            all_values.sort(key=lambda x: x['date'])
            
            # 创建该指标的完整时间序列
            for item in all_values:
                merged_data.append({
                    'date': item['date'],
                    'indicator': column,
                    'value': item['value'],
                    'is_predicted': item['is_predicted']
                })
            
            logger.info(f"指标 {column} 合并完成，共 {len(all_values)} 个数据点")
    
    # 转换为DataFrame
    merged_df = pd.DataFrame(merged_data)
    
    if not merged_df.empty:
        # 透视表格式，使指标成为列
        pivot_df = merged_df.pivot_table(
            index='date', 
            columns='indicator', 
            values='value', 
            aggfunc='first'
        )
        
        # 创建is_predicted标记
        is_predicted_df = merged_df.pivot_table(
            index='date', 
            columns='indicator', 
            values='is_predicted', 
            aggfunc='first'
        )
        
        # 重置索引
        pivot_df.reset_index(inplace=True)
        pivot_df.columns.name = None
        
        logger.info(f"数据合并完成，最终形状: {pivot_df.shape}")
        return pivot_df, is_predicted_df
    else:
        logger.warning("没有找到可合并的数据")
        return None, None

def save_merged_data(merged_df, output_file):
    """保存合并后的数据"""
    logger.info(f"保存合并数据到: {output_file}")

    try:
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 保存为CSV文件
        merged_df.to_csv(output_file, encoding='utf-8', index=False)
        logger.info(f"数据保存成功，文件大小: {os.path.getsize(output_file)} 字节")

        # 显示数据摘要
        logger.info(f"数据摘要:")
        logger.info(f"  - 时间范围: {merged_df['date'].min()} 到 {merged_df['date'].max()}")
        logger.info(f"  - 总行数: {len(merged_df)}")
        logger.info(f"  - 总列数: {len(merged_df.columns)}")
        logger.info(f"  - 指标数量: {len(merged_df.columns) - 1}")

    except Exception as e:
        logger.error(f"保存数据时出错: {str(e)}")
        raise

def main():
    """主函数"""
    logger.info("开始数据合并任务...")

    # 定义文件路径 - 使用修复编码后的文件
    prediction_file = r"C:\Users\leebox\Desktop\mac-eco-web\update\月度数据预测结果_修复编码.csv"
    historical_dir = r"C:\Users\leebox\Desktop\mac-eco-web\社科数值混频模型数据20250527"
    output_file = r"C:\Users\leebox\Desktop\mac-eco-web\update\月度数据完整合并结果.csv"

    try:
        # 检查文件是否存在
        if not os.path.exists(prediction_file):
            raise FileNotFoundError(f"预测数据文件不存在: {prediction_file}")

        if not os.path.exists(historical_dir):
            raise FileNotFoundError(f"历史数据目录不存在: {historical_dir}")

        # 1. 读取预测数据
        prediction_df = read_prediction_data(prediction_file)

        # 2. 读取历史数据
        historical_data_dict = read_historical_data(historical_dir)

        if not historical_data_dict:
            logger.warning("没有找到有效的历史数据文件")

        # 3. 合并数据
        merged_df, is_predicted_df = merge_data(prediction_df, historical_data_dict)

        if merged_df is not None:
            # 4. 保存合并后的数据
            save_merged_data(merged_df, output_file)

            # 5. 生成数据报告
            logger.info("\n=== 数据合并报告 ===")
            logger.info(f"预测数据文件: {prediction_file}")
            logger.info(f"历史数据目录: {historical_dir}")
            logger.info(f"输出文件: {output_file}")
            logger.info(f"处理的历史数据文件数量: {len(historical_data_dict)}")
            logger.info(f"最终数据形状: {merged_df.shape}")
            logger.info(f"时间范围: {merged_df['date'].min()} 到 {merged_df['date'].max()}")

            # 显示前几行数据作为示例
            logger.info("\n前5行数据示例:")
            print(merged_df.head())

            logger.info("\n数据合并任务完成！")

        else:
            logger.error("数据合并失败，没有生成有效的合并数据")

    except Exception as e:
        logger.error(f"数据合并任务失败: {str(e)}")
        raise

if __name__ == "__main__":
    main()
