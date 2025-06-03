import pandas as pd
import chardet

# 检测文件编码
file_path = r"C:\Users\leebox\Desktop\mac-eco-web\update\月度数据预测结果.csv"

print("=== 检测文件编码 ===")
with open(file_path, 'rb') as f:
    raw_data = f.read()
    result = chardet.detect(raw_data)
    print(f"检测到的编码: {result}")

print("\n=== 尝试不同编码读取 ===")
encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5']

for encoding in encodings:
    try:
        df = pd.read_csv(file_path, encoding=encoding)
        print(f"\n{encoding} 编码读取成功:")
        print(f"数据形状: {df.shape}")
        print(f"前5列名: {list(df.columns[:5])}")
        
        # 检查是否有中文列名
        chinese_cols = [col for col in df.columns if any('\u4e00' <= char <= '\u9fff' for char in col)]
        print(f"中文列名数量: {len(chinese_cols)}")
        if chinese_cols:
            print(f"前3个中文列名: {chinese_cols[:3]}")
        
        # 如果找到了正确的编码，保存修复后的文件
        if len(chinese_cols) > 0:
            print(f"\n找到正确编码: {encoding}")
            output_file = r"C:\Users\leebox\Desktop\mac-eco-web\update\月度数据预测结果_修复编码.csv"
            df.to_csv(output_file, encoding='utf-8', index=False)
            print(f"修复后的文件已保存到: {output_file}")
            break
            
    except Exception as e:
        print(f"{encoding} 编码失败: {e}")

print("\n=== 检查合并文件的编码 ===")
merged_file = r"C:\Users\leebox\Desktop\mac-eco-web\update\月度数据完整合并结果.csv"
try:
    merged_df = pd.read_csv(merged_file, encoding='utf-8')
    print(f"合并文件形状: {merged_df.shape}")
    print(f"前5列名: {list(merged_df.columns[:5])}")
    
    # 检查是否有中文列名
    chinese_cols = [col for col in merged_df.columns if any('\u4e00' <= char <= '\u9fff' for char in col)]
    print(f"中文列名数量: {len(chinese_cols)}")
    if chinese_cols:
        print(f"前3个中文列名: {chinese_cols[:3]}")
except Exception as e:
    print(f"读取合并文件失败: {e}")
