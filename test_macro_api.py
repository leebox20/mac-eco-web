import requests
import json
from datetime import datetime

# 测试宏观分析API
def test_macro_analysis_api():
    """测试宏观经济整体分析API"""
    url = "http://120.48.150.254:8888/api/macro-analysis"
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始测试宏观分析API...")
    print(f"请求URL: {url}")
    print("-" * 50)
    
    try:
        # 发送POST请求
        response = requests.post(url, timeout=120)  # 设置较长的超时时间，因为AI分析需要时间
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("[SUCCESS] API调用成功！")
            print("\n响应数据结构:")
            print(f"- status: {result.get('status')}")
            print(f"- data keys: {list(result.get('data', {}).keys())}")
            
            if result.get('data'):
                data = result['data']
                print(f"\n数据详情:")
                print(f"- 指标数量: {data.get('indicators_count')}")
                print(f"- 更新时间: {data.get('update_time')}")
                print(f"- 数据来源: {data.get('data_source')}")
                
                # 显示分析内容的前500个字符
                analysis = data.get('analysis', '')
                print(f"\n分析内容预览 (前500字):")
                print("-" * 50)
                print(analysis[:500] + "..." if len(analysis) > 500 else analysis)
                print("-" * 50)
                
                # 保存完整响应到文件
                with open('macro_analysis_response.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print("\n完整响应已保存到: macro_analysis_response.json")
                
        else:
            print(f"[ERROR] API调用失败！")
            print(f"错误内容: {response.text}")
            
    except requests.exceptions.Timeout:
        print("[ERROR] 请求超时！API响应时间过长。")
    except requests.exceptions.ConnectionError:
        print("[ERROR] 连接错误！请确保后端服务器正在运行。")
    except Exception as e:
        print(f"[ERROR] 发生错误: {type(e).__name__}: {e}")
    
    print("\n测试完成！")

if __name__ == "__main__":
    test_macro_analysis_api()