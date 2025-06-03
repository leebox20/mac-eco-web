import pandas as pd

# 读取CSV文件
df = pd.read_csv('update/月度数据完整合并结果.csv', encoding='utf-8')
df['date'] = pd.to_datetime(df['date'])

print(f"CSV文件形状: {df.shape}")
print(f"时间范围: {df['date'].min()} 到 {df['date'].max()}")

# 检查上证综合指数
column = '上证综合指数'
if column in df.columns:
    print(f"\n检查指标: {column}")
    
    # 找到第一个非空值
    first_valid_idx = df[column].first_valid_index()
    print(f"第一个非空值的索引: {first_valid_idx}")
    if first_valid_idx is not None:
        print(f"第一个非空值的日期: {df.loc[first_valid_idx, 'date']}")
        print(f"第一个非空值: {df.loc[first_valid_idx, column]}")
    
    # 统计非空值数量
    non_null_count = df[column].notna().sum()
    print(f"非空值数量: {non_null_count}")
    
    # 显示前几个非空值
    non_null_data = df[df[column].notna()][['date', column]].head(10)
    print(f"\n前10个非空值:")
    for _, row in non_null_data.iterrows():
        is_pred = row['date'] >= pd.Timestamp('2025-06-01')
        print(f"  {row['date'].strftime('%Y-%m-%d')}: {row[column]} (预测: {is_pred})")
    
    # 从第一个非空值开始的数据
    if first_valid_idx is not None:
        subset = df.loc[first_valid_idx:].copy()
        print(f"\n从第一个非空值开始的数据量: {len(subset)}")
        print(f"时间范围: {subset['date'].min()} 到 {subset['date'].max()}")
        
        # 统计预测vs历史数据
        subset['is_predicted'] = subset['date'] >= pd.Timestamp('2025-06-01')
        historical_count = (~subset['is_predicted']).sum()
        predicted_count = subset['is_predicted'].sum()
        print(f"历史数据点: {historical_count}")
        print(f"预测数据点: {predicted_count}")
else:
    print(f"未找到列: {column}")
    print("可用的列:")
    for i, col in enumerate(df.columns[:10]):
        print(f"  {i}: {col}")
