import pandas as pd
import os

# 读取历史数据文件
hist_file = r"C:\Users\leebox\Desktop\mac-eco-web\社科数值混频模型数据20250527\DATACY-250527.csv"

print("=== 调试历史数据文件格式 ===")

# 尝试不同编码读取
for encoding in ['gbk', 'utf-8', 'gb2312']:
    try:
        df = pd.read_csv(hist_file, encoding=encoding)
        print(f"使用 {encoding} 编码读取成功")
        print(f"数据形状: {df.shape}")
        print(f"前5列: {list(df.columns[:5])}")
        print(f"第一行数据:")
        print(df.iloc[0, :5])
        print(f"第二行数据:")
        print(df.iloc[1, :5])
        
        # 检查是否包含"上证综合指数"
        if '上证综合指数' in df.columns:
            print(f"\n找到'上证综合指数'列!")
            shanghai_data = df['上证综合指数']
            non_null_count = shanghai_data.notna().sum()
            print(f"非空值数量: {non_null_count}")
            if non_null_count > 0:
                print("前几个非空值:")
                non_null_data = df[df['上证综合指数'].notna()][['指标名称', '上证综合指数']].head()
                print(non_null_data)
        else:
            print("未找到'上证综合指数'列")
            print("可用列名:")
            for i, col in enumerate(df.columns):
                if '上证' in col or '综合' in col:
                    print(f"  {i}: {col}")
        
        break
    except UnicodeDecodeError:
        print(f"{encoding} 编码失败")
        continue
    except Exception as e:
        print(f"{encoding} 编码出错: {e}")
        continue

print("\n=== 检查合并后的数据文件 ===")
merged_file = r"C:\Users\leebox\Desktop\mac-eco-web\update\月度数据完整合并结果.csv"
merged_df = pd.read_csv(merged_file, encoding='utf-8')
print(f"合并文件形状: {merged_df.shape}")
print(f"时间范围: {merged_df['date'].min()} 到 {merged_df['date'].max()}")

if '上证综合指数' in merged_df.columns:
    print(f"\n合并文件中找到'上证综合指数'!")
    shanghai_data = merged_df['上证综合指数']
    non_null_count = shanghai_data.notna().sum()
    print(f"非空值数量: {non_null_count}")
    if non_null_count > 0:
        print("前几个非空值:")
        non_null_data = merged_df[merged_df['上证综合指数'].notna()][['date', '上证综合指数']].head()
        print(non_null_data)
else:
    print("合并文件中未找到'上证综合指数'")
    print("可用列名:")
    for col in merged_df.columns:
        if '上证' in col or '综合' in col:
            print(f"  {col}")
