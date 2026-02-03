"""
企业微信用户信息验证工具
用于获取用户的完整 userid
"""

import requests
import json

def get_user_info(corp_id, secret, user_id):
    """获取用户详细信息"""
    
    # 1. 获取 access_token
    token_url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    token_params = {
        "corpid": corp_id,
        "corpsecret": secret
    }
    
    print("=" * 60)
    print("步骤 1: 获取 access_token")
    print("=" * 60)
    
    try:
        token_response = requests.get(token_url, params=token_params, timeout=10)
        token_data = token_response.json()
        
        print(f"响应: {json.dumps(token_data, ensure_ascii=False, indent=2)}")
        
        if token_data.get('errcode') != 0:
            print(f"\n❌ 获取 token 失败: {token_data}")
            return None
        
        access_token = token_data.get('access_token')
        print(f"\n✅ access_token 获取成功")
        
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return None
    
    # 2. 获取用户信息
    user_url = "https://qyapi.weixin.qq.com/cgi-bin/user/get"
    user_params = {
        "access_token": access_token,
        "userid": user_id
    }
    
    print("\n" + "=" * 60)
    print("步骤 2: 获取用户信息")
    print("=" * 60)
    print(f"请求 userid: {user_id}")
    
    try:
        user_response = requests.get(user_url, params=user_params, timeout=10)
        user_data = user_response.json()
        
        print(f"\n响应: {json.dumps(user_data, ensure_ascii=False, indent=2)}")
        
        if user_data.get('errcode') == 0:
            print("\n✅ 用户信息获取成功！")
            print("\n" + "=" * 60)
            print("用户详细信息")
            print("=" * 60)
            print(f"userid: {user_data.get('userid')}")
            print(f"姓名: {user_data.get('name')}")
            print(f"手机: {user_data.get('mobile')}")
            print(f"邮箱: {user_data.get('email')}")
            print(f"部门: {user_data.get('department')}")
            print(f"职位: {user_data.get('position')}")
            print(f"状态: {user_data.get('status')} (1=已激活, 2=已禁用, 4=未激活)")
            return user_data
        else:
            print(f"\n❌ 获取用户信息失败: {user_data}")
            return None
            
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return None


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("企业微信用户信息验证工具")
    print("=" * 60)
    
    # 使用您的企业信息
    corp_id = "wwae4f99f11753a5ea"
    secret = "OYemZuIEpaL3b5_qxnOVHqd29ZR5UEGWYsBxvFoZEnc"
    user_id = "msYang"
    
    print(f"\n企业ID: {corp_id}")
    print(f"Secret: {secret[:10]}...")
    print(f"用户ID: {user_id}")
    print("\n正在验证...")
    
    result = get_user_info(corp_id, secret, user_id)
    
    if result:
        print("\n" + "=" * 60)
        print("✅ 验证成功！可以使用以下 userid 创建表格：")
        print("=" * 60)
        print(f"\n>>> {result.get('userid')} <<<")
        print("\n" + "=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 验证失败！请检查：")
        print("=" * 60)
        print("1. 企业ID 是否正确")
        print("2. Secret 是否正确")
        print("3. userid 是否存在")
        print("4. 该用户是否已激活")
        print("=" * 60)
