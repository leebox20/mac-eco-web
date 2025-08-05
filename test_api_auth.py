import requests
import json

# 测试不同的认证方式
def test_auth_methods():
    """测试百度千帆API的不同认证方式"""
    
    # 当前的认证信息
    auth_string = "bce-v3/ALTAK-YLij17TdPMsg11izg9HAn/3168a0aea58dfbbe24023103d4dec3830d225aca"
    app_id = "31e13499-bc62-454e-9726-10318869d707"  # GDP数据分析流1
    
    # 创建对话的URL
    url = "https://qianfan.baidubce.com/v2/app/conversation"
    
    payload = {
        "app_id": app_id
    }
    
    print("测试不同的认证header...\n")
    
    # 测试1: 使用 Authorization header
    print("1. 测试 Authorization header:")
    headers1 = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_string}"
    }
    
    try:
        response1 = requests.post(url, json=payload, headers=headers1)
        print(f"   状态码: {response1.status_code}")
        print(f"   响应: {response1.text[:200]}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n" + "-"*50 + "\n")
    
    # 测试2: 使用 X-Appbuilder-Authorization header
    print("2. 测试 X-Appbuilder-Authorization header:")
    headers2 = {
        "Content-Type": "application/json",
        "X-Appbuilder-Authorization": f"Bearer {auth_string}"
    }
    
    try:
        response2 = requests.post(url, json=payload, headers=headers2)
        print(f"   状态码: {response2.status_code}")
        print(f"   响应: {response2.text[:200]}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n" + "-"*50 + "\n")
    
    # 测试3: 不使用 Bearer 前缀
    print("3. 测试不带Bearer前缀的 X-Appbuilder-Authorization:")
    headers3 = {
        "Content-Type": "application/json",
        "X-Appbuilder-Authorization": auth_string
    }
    
    try:
        response3 = requests.post(url, json=payload, headers=headers3)
        print(f"   状态码: {response3.status_code}")
        print(f"   响应: {response3.text[:200]}")
    except Exception as e:
        print(f"   错误: {e}")

if __name__ == "__main__":
    test_auth_methods()