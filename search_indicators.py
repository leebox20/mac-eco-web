import pandas as pd
import os

# 读取历史数据文件
hist_file = r"C:\Users\leebox\Desktop\mac-eco-web\社科数值混频模型数据20250527\DATACY-250527.csv"

print("=== 搜索股票相关指标 ===")

df = pd.read_csv(hist_file, encoding='utf-8')
print(f"数据形状: {df.shape}")

# 搜索包含股票、指数、上证等关键词的列
keywords = ['股', '指数', '上证', '深证', '沪', '深', '证券', '股票']

print("\n包含股票相关关键词的列:")
stock_columns = []
for col in df.columns:
    for keyword in keywords:
        if keyword in col:
            stock_columns.append(col)
            print(f"  {col}")
            break

print(f"\n找到 {len(stock_columns)} 个股票相关列")

# 检查预测数据中的"上证综合指数"
print("\n=== 检查预测数据 ===")
pred_file = r"C:\Users\leebox\Desktop\mac-eco-web\update\月度数据预测结果.csv"

# 尝试不同编码读取预测数据
pred_df = None
for encoding in ['gbk', 'utf-8', 'gb2312']:
    try:
        pred_df = pd.read_csv(pred_file, encoding=encoding)
        print(f"预测数据使用 {encoding} 编码读取成功")
        break
    except UnicodeDecodeError:
        continue
if pred_df is not None:
    print(f"预测数据形状: {pred_df.shape}")
else:
    print("无法读取预测数据文件")
    exit()

if '上证综合指数' in pred_df.columns:
    print("预测数据中有'上证综合指数'")
    shanghai_data = pred_df['上证综合指数']
    non_null_count = shanghai_data.notna().sum()
    print(f"非空值数量: {non_null_count}")
else:
    print("预测数据中没有'上证综合指数'")

# 搜索预测数据中的股票相关指标
print("\n预测数据中包含股票相关关键词的列:")
pred_stock_columns = []
for col in pred_df.columns:
    for keyword in keywords:
        if keyword in col:
            pred_stock_columns.append(col)
            print(f"  {col}")
            break

print(f"\n预测数据中找到 {len(pred_stock_columns)} 个股票相关列")

# 比较两个数据源的指标名称
print("\n=== 指标名称匹配分析 ===")
hist_columns = set(df.columns[1:])  # 排除第一列"指标名称"
pred_columns = set(pred_df.columns[1:])  # 排除第一列"date"

common_columns = hist_columns.intersection(pred_columns)
print(f"共同指标数量: {len(common_columns)}")

hist_only = hist_columns - pred_columns
pred_only = pred_columns - hist_columns

print(f"仅在历史数据中的指标数量: {len(hist_only)}")
print(f"仅在预测数据中的指标数量: {len(pred_only)}")

print("\n仅在预测数据中的前10个指标:")
for i, col in enumerate(list(pred_only)[:10]):
    print(f"  {i+1}. {col}")

# 特别检查"上证综合指数"
if '上证综合指数' in pred_only:
    print(f"\n'上证综合指数' 确实只在预测数据中存在，历史数据中没有对应指标")
