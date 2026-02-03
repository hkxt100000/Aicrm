"""
企业微信 API 客户端
"""
import time
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
from config import (
    CORP_ID, CONTACT_SECRET, CUSTOMER_SECRET, APP_SECRET, AGENT_ID,
    WECOM_API_BASE, CACHE_DIR,
    ACCESS_TOKEN_CACHE_KEY, ACCESS_TOKEN_EXPIRES
)

class WeComClient:
    """企业微信 API 客户端"""
    
    def __init__(self):
        self.corp_id = CORP_ID
        self.contact_secret = CONTACT_SECRET
        self.customer_secret = CUSTOMER_SECRET
        self.app_secret = APP_SECRET  # 自建应用 Secret
        self.agent_id = AGENT_ID  # 应用 AgentId
        self.api_base = WECOM_API_BASE
        
        # 禁用代理
        self.proxies = {
            'http': None,
            'https': None
        }
        
        # 创建缓存目录
        Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)
        self.cache_file = Path(CACHE_DIR) / "access_token.json"
    
    def update_config(self, corp_id=None, contact_secret=None, customer_secret=None, app_secret=None, agent_id=None):
        """动态更新配置"""
        if corp_id:
            self.corp_id = corp_id
        if contact_secret:
            self.contact_secret = contact_secret
        if customer_secret:
            self.customer_secret = customer_secret
        if app_secret:
            self.app_secret = app_secret
        if agent_id:
            self.agent_id = agent_id
        print(f"[配置] 已更新配置: corpid={self.corp_id}, has_app_secret={bool(self.app_secret)}")
    
    def _get_cache(self, key: str) -> Optional[Dict]:
        """读取缓存"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    if key in cache:
                        data = cache[key]
                        # 检查是否过期
                        if time.time() < data.get('expires_at', 0):
                            return data
        except Exception as e:
            print(f"[缓存] 读取失败: {e}")
        return None
    
    def _set_cache(self, key: str, value: str, expires_in: int):
        """写入缓存"""
        try:
            cache = {}
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            
            cache[key] = {
                'value': value,
                'expires_at': time.time() + expires_in
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[缓存] 写入失败: {e}")
    
    def get_access_token(self, secret_type: str = "app") -> str:
        """
        获取 access_token
        :param secret_type: "contact" 通讯录 / "customer" 客户联系 / "app" 自建应用（推荐）
        """
        cache_key = f"{ACCESS_TOKEN_CACHE_KEY}_{secret_type}"
        
        # 先从缓存读取
        cached = self._get_cache(cache_key)
        if cached:
            print(f"[Token] 使用缓存的 {secret_type} access_token")
            return cached['value']
        
        # 缓存失效，重新获取
        # 优先使用应用 Secret，其次客户联系 Secret，最后通讯录 Secret
        if secret_type == "app" and self.app_secret:
            secret = self.app_secret
            print(f"[Token] 使用自建应用 Secret")
        elif secret_type == "customer":
            secret = self.customer_secret
        else:
            secret = self.contact_secret
        
        url = f"{self.api_base}/gettoken"
        params = {
            'corpid': self.corp_id,
            'corpsecret': secret
        }
        
        # 详细调试信息
        print(f"[Token] 请求URL: {url}")
        print(f"[Token] Corp ID 长度: {len(self.corp_id)}")
        print(f"[Token] Corp ID 字节: {self.corp_id.encode('utf-8')}")
        print(f"[Token] Secret 长度: {len(secret)}")
        
        try:
            response = requests.get(url, params=params, timeout=10, proxies=self.proxies)
            result = response.json()
            
            print(f"[Token] HTTP 状态码: {response.status_code}")
            print(f"[Token] API 响应: errcode={result.get('errcode')}, errmsg={result.get('errmsg')}")
            
            if result.get('errcode') == 0:
                access_token = result['access_token']
                expires_in = result.get('expires_in', 7200)
                
                # 写入缓存
                self._set_cache(cache_key, access_token, expires_in - 200)
                
                print(f"[Token] 获取新的 {secret_type} access_token 成功")
                print(f"[Token] Token 前10位: {access_token[:10]}...")
                return access_token
            else:
                error_msg = result.get('errmsg', 'Unknown error')
                print(f"[Token] 获取失败: errcode={result.get('errcode')}, errmsg={error_msg}")
                return ""
        except Exception as e:
            print(f"[Token] 请求异常: {e}")
            return ""
    
    def _get_wedoc_access_token(self) -> str:
        """
        获取微文档 API 的 access_token
        优先级：客户联系 > 自建应用 > 通讯录
        """
        # 优先使用客户联系 Secret（通常有微文档权限）
        if self.customer_secret:
            token = self.get_access_token('customer')
            if token:
                print("[微文档] 使用客户联系 Secret")
                return token
        
        # 其次尝试自建应用 Secret
        if self.app_secret:
            token = self.get_access_token('app')
            if token:
                print("[微文档] 使用自建应用 Secret")
                return token
        
        # 最后尝试通讯录 Secret
        if self.contact_secret:
            token = self.get_access_token('contact')
            if token:
                print("[微文档] 使用通讯录 Secret")
                return token
        
        print("[微文档] 错误：未配置任何 Secret")
        return ""
    
    def get_department_list(self) -> List[Dict]:
        """获取部门列表"""
        access_token = self.get_access_token("contact")
        if not access_token:
            return []
        
        url = f"{self.api_base}/department/list"
        params = {'access_token': access_token}
        
        try:
            response = requests.get(url, params=params, timeout=10, proxies=self.proxies)
            result = response.json()
            
            if result.get('errcode') == 0:
                return result.get('department', [])
            else:
                print(f"[部门] 获取失败: {result.get('errmsg')}")
                return []
        except Exception as e:
            print(f"[部门] 请求异常: {e}")
            return []
    
    def get_user_list(self, department_id: int = 1, fetch_child: int = 1) -> List[Dict]:
        """
        获取成员列表
        :param department_id: 部门 ID
        :param fetch_child: 是否递归获取子部门成员
        
        注意：获取手机号和邮箱需要使用通讯录管理密钥（contact_secret）
        """
        # 必须使用通讯录 Token 才能获取手机号和邮箱
        access_token = self.get_access_token("contact")
        if not access_token:
            print("[成员] ⚠️ 未配置通讯录密钥，无法获取手机号和邮箱")
            return []
        
        url = f"{self.api_base}/user/list"
        params = {
            'access_token': access_token,
            'department_id': department_id,
            'fetch_child': fetch_child
        }
        
        try:
            response = requests.get(url, params=params, timeout=10, proxies=self.proxies)
            result = response.json()
            
            print(f"[成员] API 响应: errcode={result.get('errcode')}, errmsg={result.get('errmsg')}")
            
            if result.get('errcode') == 0:
                userlist = result.get('userlist', [])
                print(f"[成员] 成功获取 {len(userlist)} 个成员")
                
                # 检查第一个成员的字段
                if userlist and len(userlist) > 0:
                    first_user = userlist[0]
                    print(f"[成员] 字段检查（第一个成员）:")
                    print(f"  - name: {first_user.get('name', '无')}")
                    print(f"  - mobile: {'有' if first_user.get('mobile') else '❌ 无'}")
                    print(f"  - email: {'有' if first_user.get('email') else '❌ 无'}")
                    print(f"  - biz_mail: {'有' if first_user.get('biz_mail') else '❌ 无'}")
                    
                    # 如果没有 mobile 和 email，提示权限问题
                    if not first_user.get('mobile') and not first_user.get('email'):
                        print(f"[成员] ⚠️ 警告：未获取到手机号和邮箱！")
                        print(f"[成员] 请检查：")
                        print(f"  1. 应用是否有「通讯录-成员信息-手机号」权限")
                        print(f"  2. 应用是否有「通讯录-成员信息-邮箱」权限")
                        print(f"  3. 成员是否在应用的可见范围内")
                
                return userlist
            else:
                print(f"[成员] 获取失败: {result.get('errmsg')}")
                return []
        except Exception as e:
            print(f"[成员] 请求异常: {e}")
            return []
    
    def get_external_contact_list(self, userid: str) -> List[str]:
        """
        获取客户列表（仅返回 external_userid）
        :param userid: 成员 userid
        """
        # 优先使用应用 Token，其次客户联系 Token
        access_token = self.get_access_token("app") or self.get_access_token("customer")
        if not access_token:
            print(f"[客户列表] 无法获取 access_token")
            return []
        
        url = f"{self.api_base}/externalcontact/list"
        params = {'access_token': access_token, 'userid': userid}
        
        try:
            response = requests.get(url, params=params, timeout=10, proxies=self.proxies)
            result = response.json()
            
            print(f"[客户列表] API 响应: errcode={result.get('errcode')}, errmsg={result.get('errmsg')}")
            
            if result.get('errcode') == 0:
                external_userids = result.get('external_userid', [])
                print(f"[客户列表] 成功获取 {len(external_userids)} 个客户 ID")
                return external_userids
            else:
                print(f"[客户列表] 获取失败: errcode={result.get('errcode')}, errmsg={result.get('errmsg')}")
                return []
        except Exception as e:
            print(f"[客户列表] 请求异常: {e}")
            return []
    
    def get_external_contact_detail(self, external_userid: str) -> Optional[Dict]:
        """
        获取客户详情
        :param external_userid: 客户 external_userid
        """
        # 优先使用应用 Token，其次客户联系 Token
        access_token = self.get_access_token("app") or self.get_access_token("customer")
        if not access_token:
            return None
        
        url = f"{self.api_base}/externalcontact/get"
        params = {'access_token': access_token, 'external_userid': external_userid}
        
        try:
            response = requests.get(url, params=params, timeout=10, proxies=self.proxies)
            result = response.json()
            
            if result.get('errcode') == 0:
                return result
            else:
                print(f"[客户详情] 获取失败: {result.get('errmsg')}")
                return None
        except Exception as e:
            print(f"[客户详情] 请求异常: {e}")
            return None
    
    def get_corp_tag_list(self, tag_id: List[str] = None) -> List[Dict]:
        """
        获取企业标签库
        :param tag_id: 标签 ID 列表（可选）
        """
        # 优先使用应用 Token，其次客户联系 Token
        access_token = self.get_access_token("app") or self.get_access_token("customer")
        if not access_token:
            return []
        
        url = f"{self.api_base}/externalcontact/get_corp_tag_list"
        params = {'access_token': access_token}
        data = {}
        if tag_id:
            data['tag_id'] = tag_id
        
        try:
            response = requests.post(url, params=params, json=data, timeout=10, proxies=self.proxies)
            result = response.json()
            
            if result.get('errcode') == 0:
                return result.get('tag_group', [])
            else:
                print(f"[标签] 获取失败: {result.get('errmsg')}")
                return []
        except Exception as e:
            print(f"[标签] 请求异常: {e}")
            return []
    
    def get_group_chat_tag_list(self, tag_ids: List[str] = None, group_ids: List[str] = None) -> List[Dict]:
        """
        获取客户群标签列表
        
        注意：企业微信的客户群标签 API 可能需要特定权限或版本
        如果 404，则回退使用企业客户标签 API
        
        :param tag_ids: 标签ID列表（可选）
        :param group_ids: 标签组ID列表（可选）
        :return: 标签组列表
        """
        # 使用客户联系或应用 Token
        access_token = self.get_access_token("customer") or self.get_access_token("app")
        if not access_token:
            print("[客户群标签] 获取access_token失败")
            return []
        
        # 先尝试客户群标签专用 API
        url = f"{self.api_base}/externalcontact/groupchat/get_tag_list"
        params = {'access_token': access_token}
        data = {}
        
        if tag_ids:
            data['tag_id'] = tag_ids
        if group_ids:
            data['group_id'] = group_ids
        
        try:
            print(f"[客户群标签] 尝试专用API: {url}")
            response = requests.post(url, params=params, json=data, timeout=10, proxies=self.proxies)
            
            print(f"[客户群标签] 响应状态码: {response.status_code}")
            
            # 如果是 404，说明这个 API 不存在，回退到企业标签
            if response.status_code == 404:
                print("[客户群标签] 专用API不存在(404)，回退使用企业客户标签API")
                return self._get_corp_tags_as_fallback(access_token, tag_ids, group_ids)
            
            print(f"[客户群标签] 响应内容前500字符: {response.text[:500]}")
            
            result = response.json()
            
            if result.get('errcode') == 0:
                tag_groups = result.get('tag_group', [])
                print(f"[客户群标签] 获取成功，共 {len(tag_groups)} 个标签组")
                return tag_groups
            elif result.get('errcode') == 40066:  # invalid url
                print("[客户群标签] API路径无效，回退使用企业客户标签API")
                return self._get_corp_tags_as_fallback(access_token, tag_ids, group_ids)
            else:
                print(f"[客户群标签] API返回错误: errcode={result.get('errcode')}, errmsg={result.get('errmsg')}")
                return []
        except Exception as e:
            print(f"[客户群标签] 请求异常: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _get_corp_tags_as_fallback(self, access_token: str, tag_ids: List[str] = None, group_ids: List[str] = None) -> List[Dict]:
        """
        使用企业客户标签作为备选方案
        """
        url = f"{self.api_base}/externalcontact/get_corp_tag_list"
        params = {'access_token': access_token}
        data = {}
        
        if tag_ids:
            data['tag_id'] = tag_ids
        if group_ids:
            data['group_id'] = group_ids
        
        try:
            print(f"[客户群标签-备选] 使用企业标签API: {url}")
            response = requests.post(url, params=params, json=data, timeout=10, proxies=self.proxies)
            result = response.json()
            
            if result.get('errcode') == 0:
                tag_groups = result.get('tag_group', [])
                print(f"[客户群标签-备选] 获取成功，共 {len(tag_groups)} 个标签组")
                return tag_groups
            else:
                print(f"[客户群标签-备选] 获取失败: errcode={result.get('errcode')}, errmsg={result.get('errmsg')}")
                return []
        except Exception as e:
            print(f"[客户群标签-备选] 请求异常: {e}")
            return []
    
    def get_group_chat_list(self, status_filter: int = 0, limit: int = 1000) -> List[Dict]:
        """
        获取客户群列表（支持自动分页获取所有群）
        :param status_filter: 客户群状态过滤。0 - 所有列表；1 - 离职待继承；2 - 离职继承中；3 - 离职继承完成
        :param limit: 每页数量（最大1000）
        :return: 所有客户群ID列表
        """
        # 使用客户联系或应用 Token
        access_token = self.get_access_token("customer") or self.get_access_token("app")
        if not access_token:
            print("[客户群列表] 获取access_token失败")
            return []
        
        url = f"{self.api_base}/externalcontact/groupchat/list"
        all_chat_ids = []
        offset = 0
        
        while True:
            params = {'access_token': access_token}
            data = {
                'status_filter': status_filter,
                'offset': offset,
                'limit': limit
            }
            
            try:
                response = requests.post(url, params=params, json=data, timeout=10, proxies=self.proxies)
                result = response.json()
                
                if result.get('errcode') == 0:
                    group_chat_list = result.get('group_chat_list', [])
                    chat_ids = [g.get('chat_id') for g in group_chat_list if g.get('chat_id')]
                    all_chat_ids.extend(chat_ids)
                    
                    print(f"[客户群列表] 第 {offset//limit + 1} 页，获取 {len(chat_ids)} 个群，累计 {len(all_chat_ids)} 个")
                    
                    # 如果返回数量小于limit，说明已经是最后一页
                    if len(group_chat_list) < limit:
                        break
                    
                    offset += limit
                else:
                    print(f"[客户群列表] 获取失败: {result.get('errmsg')}")
                    break
            except Exception as e:
                print(f"[客户群列表] 请求异常: {e}")
                break
        
        print(f"[客户群列表] 共获取 {len(all_chat_ids)} 个客户群ID")
        return all_chat_ids
    
    def get_group_chat_detail(self, chat_id: str, need_name: bool = False, retry_count: int = 3) -> Optional[Dict]:
        """
        获取客户群详情
        :param chat_id: 客户群ID
        :param need_name: 是否需要获取成员名称（默认False，避免超时）
        :param retry_count: 重试次数
        :return: 客户群详情
        """
        # 关键修复：优先使用 app token，customer token 可能有权限问题
        access_token = self.get_access_token("app") or self.get_access_token("customer")
        if not access_token:
            print(f"[客户群详情] 无法获取 access_token")
            return None
        
        url = f"{self.api_base}/externalcontact/groupchat/get"
        params = {'access_token': access_token}
        # 关键修复：need_name 默认为 0，减少API负担
        data = {
            'chat_id': chat_id,
            'need_name': 1 if need_name else 0
        }
        
        print(f"[客户群详情] 开始获取: {chat_id}, need_name={data['need_name']}")
        
        # 重试逻辑
        for attempt in range(retry_count):
            try:
                # 关键修复：降低超时时间到15秒，快速失败
                response = requests.post(url, params=params, json=data, timeout=15, proxies=self.proxies)
                result = response.json()
                
                print(f"[客户群详情] API响应: errcode={result.get('errcode')}, errmsg={result.get('errmsg')}")
                
                if result.get('errcode') == 0:
                    group_chat = result.get('group_chat', {})
                    member_list = group_chat.get('member_list', [])
                    
                    # 统计成员类型
                    external_count = sum(1 for m in member_list if m.get('type') == 2)
                    internal_count = sum(1 for m in member_list if m.get('type') == 1)
                    
                    # 从成员列表中获取群主姓名（避免额外API调用）
                    owner_userid = group_chat.get('owner', '')
                    owner_name = ''
                    if owner_userid and member_list:
                        # 在成员列表中查找群主
                        for member in member_list:
                            if member.get('userid') == owner_userid:
                                owner_name = member.get('name', '')
                                break
                    
                    print(f"[客户群详情] 获取成功: {group_chat.get('name', '未命名')}, 群主={owner_name or owner_userid}, 成员数={len(member_list)}, 外部={external_count}, 内部={internal_count}")
                    
                    return {
                        'chat_id': group_chat.get('chat_id'),
                        'name': group_chat.get('name', ''),
                        'owner': owner_userid,
                        'owner_name': owner_name,  # 从成员列表获取群主姓名
                        'create_time': group_chat.get('create_time', 0),
                        'notice': group_chat.get('notice', ''),
                        'member_count': len(member_list),
                        'external_member_count': external_count,
                        'internal_member_count': internal_count,
                        'admin_list': group_chat.get('admin_list', []),
                        'group_type': 'external' if external_count > 0 else 'internal',
                        'status': 0,  # 默认正常状态
                        'version': group_chat.get('version', 0)
                    }
                elif result.get('errcode') == 84061:  # 限流
                    wait_time = (attempt + 1) * 2  # 逐步增加等待时间
                    if attempt < retry_count - 1:
                        import time
                        print(f"[限流] 遇到限流，等待 {wait_time} 秒后重试 (第{attempt + 1}次)...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"[客户群详情] 获取失败 ({chat_id}): 达到限流重试上限")
                        return None
                elif result.get('errcode') == 40014:  # 无效的access_token
                    print(f"[客户群详情] access_token 无效，尝试重新获取")
                    # 清除token缓存
                    self.token_cache = {}
                    if attempt < retry_count - 1:
                        continue
                    return None
                else:
                    print(f"[客户群详情] 获取失败: chat_id={chat_id}, errcode={result.get('errcode')}, errmsg={result.get('errmsg')}")
                    # 非致命错误，返回None但不重试
                    return None
            except requests.exceptions.Timeout:
                if attempt < retry_count - 1:
                    print(f"[超时] chat_id={chat_id}, 第{attempt + 1}次超时，立即重试...")
                    continue
                else:
                    print(f"[客户群详情] 请求超时 (已重试{retry_count}次): {chat_id}")
                    return None
            except requests.exceptions.ConnectionError as e:
                print(f"[网络错误] chat_id={chat_id}, 连接失败: {e}")
                if attempt < retry_count - 1:
                    import time
                    time.sleep(1)  # 网络错误等待1秒
                    continue
                return None
            except Exception as e:
                print(f"[异常] chat_id={chat_id}, 第{attempt + 1}次异常: {e}")
                import traceback
                traceback.print_exc()
                if attempt < retry_count - 1:
                    continue
                else:
                    return None
        
        return None
    
    def _get_user_name(self, userid: str) -> str:
        """获取用户名称（辅助方法）"""
        if not userid:
            return ''
        
        try:
            access_token = self.get_access_token("contact") or self.get_access_token("app")
            if not access_token:
                return userid
            
            url = f"{self.api_base}/user/get"
            params = {'access_token': access_token, 'userid': userid}
            
            response = requests.get(url, params=params, timeout=5, proxies=self.proxies)
            result = response.json()
            
            if result.get('errcode') == 0:
                return result.get('name', userid)
            else:
                return userid
        except:
            return userid
    
    def update_customer_remark(self, external_userid: str, userid: str, remark: str) -> bool:
        """
        更新客户备注
        :param external_userid: 客户external_userid
        :param userid: 企业员工userid
        :param remark: 备注内容
        :return: 是否成功
        """
        access_token = self.get_access_token("customer") or self.get_access_token("app")
        if not access_token:
            print("[更新备注] 获取access_token失败")
            return False
        
        url = f"{self.api_base}/externalcontact/remark"
        params = {'access_token': access_token}
        data = {
            'userid': userid,
            'external_userid': external_userid,
            'remark': remark
        }
        
        try:
            response = requests.post(url, params=params, json=data, timeout=10, proxies=self.proxies)
            result = response.json()
            
            print(f"[更新备注] API响应: {result}")
            
            if result.get('errcode') == 0:
                print(f"[更新备注] 成功: {external_userid} -> {remark}")
                return True
            else:
                print(f"[更新备注] 失败: {result.get('errmsg')}")
                return False
        except Exception as e:
            print(f"[更新备注] 请求异常: {e}")
            return False
    
    def update_customer_tags(self, external_userid: str, userid: str, add_tag: List[str] = None, remove_tag: List[str] = None) -> bool:
        """
        编辑客户企业标签
        :param external_userid: 客户external_userid
        :param userid: 企业员工userid
        :param add_tag: 要添加的标签ID列表
        :param remove_tag: 要移除的标签ID列表
        :return: 是否成功
        """
        access_token = self.get_access_token("customer") or self.get_access_token("app")
        if not access_token:
            print("[更新标签] 获取access_token失败")
            return False
        
        url = f"{self.api_base}/externalcontact/mark_tag"
        params = {'access_token': access_token}
        data = {
            'userid': userid,
            'external_userid': external_userid
        }
        
        if add_tag:
            data['add_tag'] = add_tag
        if remove_tag:
            data['remove_tag'] = remove_tag
        
        try:
            response = requests.post(url, params=params, json=data, timeout=10, proxies=self.proxies)
            result = response.json()
            
            print(f"[更新标签] API响应: {result}")
            
            if result.get('errcode') == 0:
                print(f"[更新标签] 成功: {external_userid}")
                return True
            else:
                print(f"[更新标签] 失败: {result.get('errmsg')}")
                return False
        except Exception as e:
            print(f"[更新标签] 请求异常: {e}")
            return False
    
    def sync_all_customers(self) -> List[Dict]:
        """
        同步所有客户数据
        """
        print("[同步] 开始同步客户数据...")
        
        # 1. 获取所有成员
        users = self.get_user_list()
        print(f"[同步] 获取到 {len(users)} 个成员")
        
        all_customers = []
        
        # 2. 遍历每个成员，获取其客户列表
        for user in users:
            userid = user['userid']
            username = user['name']
            
            print(f"[同步] 正在获取 {username}({userid}) 的客户...")
            
            # 获取客户 ID 列表
            external_userids = self.get_external_contact_list(userid)
            print(f"[同步] {username} 有 {len(external_userids)} 个客户")
            
            # 获取每个客户的详情
            for external_userid in external_userids:
                detail = self.get_external_contact_detail(external_userid)
                if detail:
                    # 添加所属员工信息
                    customer_data = detail.get('external_contact', {})
                    follow_user = detail.get('follow_user', [])
                    
                    # 找到当前员工的跟进信息
                    current_follow = next((f for f in follow_user if f['userid'] == userid), None)
                    
                    if current_follow:
                        customer_data['owner_userid'] = userid
                        customer_data['owner_name'] = username
                        customer_data['add_time'] = current_follow.get('createtime', 0)
                        customer_data['remark'] = current_follow.get('remark', '')
                        customer_data['description'] = current_follow.get('description', '')
                        customer_data['add_way'] = current_follow.get('add_way', 0)
                        customer_data['state'] = current_follow.get('state', '')
                        customer_data['remark_mobiles'] = current_follow.get('remark_mobiles', [])
                        customer_data['remark_corp_name'] = current_follow.get('remark_corp_name', '')
                        customer_data['im_status'] = current_follow.get('im_status', 0)
                        customer_data['tags'] = current_follow.get('tags', [])
                        
                        all_customers.append(customer_data)
        
        print(f"[同步] 同步完成，共 {len(all_customers)} 个客户")
        return all_customers
    
    # ==================== 企业微信文档管理 API ====================
    
    def get_space_list(self) -> Dict:
        """
        获取企业微信空间列表
        
        Returns:
            {
                "errcode": 0,
                "errmsg": "ok",
                "space_list": [
                    {
                        "spaceid": "space_xxxxxxxxxxxx",
                        "space_name": "空间名称"
                    }
                ]
            }
        """
        # 获取 access_token
        if self.app_secret:
            access_token = self.get_access_token('app')
        elif self.customer_secret:
            access_token = self.get_access_token('customer')
        elif self.contact_secret:
            access_token = self.get_access_token('contact')
        else:
            return {"errcode": -1, "errmsg": "未配置 Secret"}
        
        if not access_token:
            return {"errcode": -1, "errmsg": "无法获取 access_token"}
        
        url = f"{self.api_base}/wedoc/get_space_list"
        
        try:
            response = requests.post(
                url,
                params={'access_token': access_token},
                json={},
                timeout=10,
                proxies=self.proxies
            )
            result = response.json()
            print(f"[空间] 获取空间列表响应: {result}")
            return result
        except Exception as e:
            print(f"[空间] 获取空间列表失败: {e}")
            return {"errcode": -1, "errmsg": str(e)}
    
    def create_spreadsheet(self, doc_name: str, admin_users: List[str] = None, spaceid: str = None) -> Dict:
        """
        创建企业微信智能表格
        
        Args:
            doc_name: 文档名称
            admin_users: 管理员列表（userid）
            spaceid: 空间ID（可选）
        
        Returns:
            {
                "errcode": 0,
                "errmsg": "ok",
                "docid": "doc_xxxxxxxxxxxx",
                "url": "https://doc.weixin.qq.com/sheet/xxxxx"
            }
        """
        # 微文档 API 通常需要客户联系或通讯录权限
        # 优先使用客户联系 Secret
        if self.customer_secret:
            access_token = self.get_access_token('customer')
            print("[表格] 使用客户联系 Secret 创建表格")
        elif self.app_secret:
            access_token = self.get_access_token('app')
            print("[表格] 使用自建应用 Secret 创建表格")
        elif self.contact_secret:
            access_token = self.get_access_token('contact')
            print("[表格] 使用通讯录 Secret 创建表格")
        else:
            print("[表格] 错误：未配置任何 Secret")
            return {"errcode": -1, "errmsg": "未配置 Secret，请在配置页面填写客户联系 Secret 或其他 Secret"}
        
        if not access_token:
            print("[表格] 错误：无法获取 access_token")
            return {"errcode": -1, "errmsg": "无法获取 access_token，请检查企业 ID 和 Secret 是否正确"}
        
        url = f"{self.api_base}/wedoc/create_doc"
        
        # 明确构建请求数据，确保只包含企业微信 API 需要的字段
        data = {
            "doc_type": 10,  # 10=智能表格（支持 API 操作）
            "doc_name": doc_name
        }
        
        # admin_users 参数：只有当提供了非空列表时才添加
        # 传递空数组会导致 invalid Request Parameter 错误
        if admin_users and len(admin_users) > 0:
            data["admin_users"] = admin_users
            print(f"[表格] 指定管理员: {admin_users}")
        else:
            print(f"[表格] 不指定管理员，使用默认（access_token 对应的用户）")
        
        # 可选参数
        if spaceid:
            data["spaceid"] = spaceid
        
        print(f"[表格] 创建表格: {doc_name}")
        print(f"[表格] 请求 URL: {url}")
        print(f"[表格] access_token 前10位: {access_token[:10] if access_token else 'None'}...")
        print(f"[表格] 请求参数: {json.dumps(data, ensure_ascii=False)}")
        
        try:
            response = requests.post(
                url, 
                params={'access_token': access_token},
                json=data,
                timeout=10,
                proxies=self.proxies
            )
            result = response.json()
            
            print(f"[表格] API 响应: errcode={result.get('errcode')}, errmsg={result.get('errmsg')}")
            
            if result.get('errcode') == 0:
                print(f"[表格] 创建成功，docid={result.get('docid')}")
                print(f"[表格] 访问链接: {result.get('url')}")
                return result
            else:
                print(f"[表格] 创建失败: {result.get('errmsg')}")
                return result
        except Exception as e:
            print(f"[表格] 创建表格失败: {e}")
            return {"errcode": -1, "errmsg": str(e)}
    
    def delete_spreadsheet(self, docid: str) -> Dict:
        """
        删除智能表格文档
        
        Args:
            docid: 文档ID
        
        Returns:
            {
                "errcode": 0,
                "errmsg": "ok"
            }
        """
        access_token = self.get_access_token('app')
        url = f"{self.api_base}/wedoc/del_doc"
        
        data = {
            "docid": docid
        }
        
        print(f"[表格] 删除文档: {docid}")
        
        try:
            response = requests.post(
                url,
                params={'access_token': access_token},
                json=data,
                timeout=10,
                proxies=self.proxies
            )
            result = response.json()
            
            print(f"[表格] 删除响应: errcode={result.get('errcode')}, errmsg={result.get('errmsg')}")
            
            return result
        except Exception as e:
            print(f"[表格] 删除文档失败: {e}")
            return {"errcode": -1, "errmsg": str(e)}
    
    def write_spreadsheet_data(self, docid: str, values: List[List], range_str: str = None) -> Dict:
        """
        写入表格数据
        
        Args:
            docid: 文档ID
            values: 数据（二维数组）
                例如：[
                    ["客户姓名", "公司", "电话"],
                    ["张三", "阿里巴巴", "13800138000"]
                ]
            range_str: 写入范围，默认自动计算
                例如：Sheet1!A1:C100
        
        Returns:
            {
                "errcode": 0,
                "errmsg": "ok"
            }
        """
        access_token = self.get_access_token('app')
        
        # 使用正确的 API 路径：smartsheet（一个词，不是 smart_sheet）
        get_sheet_url = f"{self.api_base}/wedoc/smartsheet/get_sheet"
        
        print(f"[表格] Step 1: 获取子表列表")
        print(f"[表格] API 路径: {get_sheet_url}")
        
        try:
            sheet_response = requests.post(
                get_sheet_url,
                params={'access_token': access_token},
                json={"docid": docid},
                timeout=10,
                proxies=self.proxies
            )
            
            print(f"[表格] HTTP 状态码: {sheet_response.status_code}")
            print(f"[表格] 响应 Content-Type: {sheet_response.headers.get('Content-Type')}")
            print(f"[表格] 响应内容前500字符: {sheet_response.text[:500]}")
            
            sheet_result = sheet_response.json()
            
            print(f"[表格] 子表列表响应: {sheet_result}")
            
            if sheet_result.get('errcode') != 0:
                print(f"[表格] 获取子表列表失败: {sheet_result.get('errmsg')}")
                return sheet_result
            
            # 获取第一个子表的 sheet_id
            sheet_list = sheet_result.get('sheet_list', [])
            if not sheet_list:
                print(f"[表格] 错误：表格中没有子表")
                return {"errcode": -1, "errmsg": "表格中没有子表"}
            
            sheet_id = sheet_list[0].get('sheet_id')
            print(f"[表格] 使用子表: {sheet_id}")
            
        except Exception as e:
            print(f"[表格] 获取子表列表失败: {e}")
            print(f"[表格] 将尝试不使用 sheet_id，直接添加记录")
            sheet_id = None  # 尝试不使用 sheet_id
        
        # 智能表格需要将数据转换为记录格式
        # values 的第一行是表头，后续行是数据
        if not values or len(values) < 2:
            print("[表格] 错误：数据为空或只有表头")
            return {"errcode": -1, "errmsg": "数据为空"}
        
        headers = values[0]  # 第一行是表头
        data_rows = values[1:]  # 后续行是数据
        
        print(f"[表格] 数据分析...")
        print(f"[表格] 字段数: {len(headers)}")
        print(f"[表格] 数据行数: {len(data_rows)}")
        print(f"[表格] 前5个字段: {headers[:5]}")
        print(f"[表格] 第一行数据前5个值: {data_rows[0][:5] if data_rows else []}")
        
        # 验证数据对齐
        print(f"[表格] 验证字段-数据对应:")
        for i in range(min(3, len(headers))):
            field_name = headers[i]
            field_value = data_rows[0][i] if data_rows and i < len(data_rows[0]) else "N/A"
            print(f"  列{i}: {field_name} = {field_value}")
        
        # Step 2: 智能字段管理（删除默认字段 + 添加我们的字段）
        field_title_to_id = {}  # 字段名 -> 字段ID 的映射
        
        if sheet_id:
            print(f"[表格] Step 2: 智能字段管理")
            
            # Step 2.1: 查询现有字段
            get_fields_url = f"{self.api_base}/wedoc/smartsheet/get_fields"
            try:
                get_fields_response = requests.post(
                    get_fields_url,
                    params={'access_token': access_token},
                    json={"docid": docid, "sheet_id": sheet_id},
                    timeout=10,
                    proxies=self.proxies
                )
                get_fields_result = get_fields_response.json()
                
                if get_fields_result.get('errcode') == 0:
                    existing_fields = get_fields_result.get('fields', [])
                    print(f"[表格] 现有字段数: {len(existing_fields)}")
                    
                    # ⭐ Step 2.2: 删除所有默认字段，然后添加我们的字段
                    # 这样可以保证字段顺序正确
                    
                    all_field_ids = [f.get('field_id') for f in existing_fields]
                    
                    if all_field_ids:
                        print(f"[表格] 尝试删除所有 {len(all_field_ids)} 个默认字段...")
                        delete_fields_url = f"{self.api_base}/wedoc/smartsheet/delete_fields"
                        
                        try:
                            delete_response = requests.post(
                                delete_fields_url,
                                params={'access_token': access_token},
                                json={
                                    "docid": docid,
                                    "sheet_id": sheet_id,
                                    "field_ids": all_field_ids
                                },
                                timeout=30,
                                proxies=self.proxies
                            )
                            delete_result = delete_response.json()
                            
                            if delete_result.get('errcode') == 0:
                                print(f"[表格] ✅ 成功删除所有默认字段")
                            else:
                                print(f"[表格] ⚠️ 删除默认字段失败: {delete_result.get('errmsg')}")
                                print(f"[表格] 将继续添加字段（可能导致顺序不对）")
                        except Exception as delete_error:
                            print(f"[表格] ⚠️ 删除字段异常: {delete_error}")
                    
                    # Step 2.3: 添加所有字段（全部为文本类型）
                    # ⭐⭐⭐ 倒序添加字段，尝试让企业微信显示为正序
                    print(f"[表格] 添加 {len(headers)} 个自定义字段（全部为文本类型）...")
                    print(f"[表格] ⚠️ 使用倒序添加策略...")
                    add_fields_url = f"{self.api_base}/wedoc/smartsheet/add_fields"
                    fields = []
                    # 倒序遍历 headers
                    for header in reversed(headers):
                        fields.append({
                            "field_title": header,
                            "field_type": "FIELD_TYPE_TEXT"
                        })
                    
                    print(f"[表格] 📋 添加顺序（倒序，前10个）:")
                    for idx, field in enumerate(fields[:10]):
                        print(f"[表格]   添加序号{idx+1}: {field['field_title']}")
                    
                    fields_data = {
                        "docid": docid,
                        "sheet_id": sheet_id,
                        "fields": fields
                    }
                    
                    try:
                        fields_response = requests.post(
                            add_fields_url,
                            params={'access_token': access_token},
                            json=fields_data,
                            timeout=30,
                            proxies=self.proxies
                        )
                        
                        fields_result = fields_response.json()
                        print(f"[表格] 添加字段响应: errcode={fields_result.get('errcode')}, errmsg={fields_result.get('errmsg')}")
                        
                        # ⭐ 验证字段添加顺序
                        if fields_result.get('errcode') == 0:
                            print(f"[表格] ✅ 成功添加 {len(headers)} 个字段")
                            print(f"[表格] 📋 预期字段顺序（前10个）:")
                            for idx, header in enumerate(headers[:10]):
                                print(f"[表格]   位置{idx+1}: {header}")
                            
                            # 重新查询字段列表，验证实际顺序
                            print(f"[表格] 🔍 查询实际字段顺序...")
                            verify_response = requests.post(
                                get_fields_url,
                                params={'access_token': access_token},
                                json={"docid": docid, "sheet_id": sheet_id},
                                timeout=10,
                                proxies=self.proxies
                            )
                            verify_result = verify_response.json()
                            
                            if verify_result.get('errcode') == 0:
                                actual_fields = verify_result.get('fields', [])
                                print(f"[表格] 📊 实际字段顺序（前10个）:")
                                for idx, field in enumerate(actual_fields[:10]):
                                    field_title = field.get('field_title', 'Unknown')
                                    field_type = field.get('field_type', 'Unknown')
                                    field_id = field.get('field_id', 'Unknown')
                                    print(f"[表格]   位置{idx+1}: {field_title} ({field_type}) [ID: {field_id}]")
                                
                                # 建立字段名到 field_id 的映射
                                for field in actual_fields:
                                    field_title_to_id[field.get('field_title')] = field.get('field_id')
                        else:
                            print(f"[表格] 警告：添加字段失败 - {fields_result.get('errmsg')}")
                    except Exception as add_error:
                        print(f"[表格] 添加字段失败: {add_error}")
                else:
                    print(f"[表格] 查询字段失败，将尝试添加所有字段")
                        
            except Exception as query_error:
                print(f"[表格] 查询字段失败: {query_error}")
                print(f"[表格] 将继续尝试添加记录")
        
        # Step 3: 使用正确的 API 路径添加记录
        # smartsheet 是一个词，不是 smart_sheet
        url = f"{self.api_base}/wedoc/smartsheet/add_records"
        
        print(f"[表格] Step 3: 添加记录到智能表格")
        print(f"[表格] API 路径: {url}")
        
        # 转换为智能表格记录格式
        # ⭐⭐⭐ 关键：使用字段标题（field_title），不使用字段ID
        # 根据官方文档和实际测试，API 默认使用 FIELD_TITLE 模式
        records = []
        for row_idx, row in enumerate(data_rows):
            record_values = {}
            
            # 遍历所有字段
            for col_idx, header in enumerate(headers):
                cell_value = row[col_idx] if col_idx < len(row) else ""
                
                # 调试：显示第一行的字段映射
                if row_idx == 0 and col_idx < 10:
                    print(f"[表格] 列{col_idx}: 字段='{header}', 值='{cell_value}'")
                
                # 过滤空值和 "--" 
                if cell_value and str(cell_value).strip() not in ["", "--", "None", "null"]:
                    # ⭐ 直接使用 header（字段标题），不使用 field_id
                    # 正确的数据格式：三层嵌套
                    record_values[header] = [
                        {
                            "type": "text",
                            "text": str(cell_value)
                        }
                    ]
            
            # 只添加非空记录
            if record_values:
                records.append({"values": record_values})
            
            # 调试：显示第一条记录
            if row_idx == 0:
                print(f"[表格] 第一条记录示例（使用字段标题）:")
                for k, v in list(record_values.items())[:3]:
                    print(f"  {k}: {v[0]['text']}")
        
        # 智能表格的参数格式
        data = {
            "docid": docid,
            "records": records
        }
        
        # 如果有 sheet_id，添加到参数中
        if sheet_id:
            data["sheet_id"] = sheet_id
        
        # ⭐ 不指定 key_type，使用默认值 FIELD_TITLE
        print(f"[表格] 写入数据到 {docid}, sheet_id: {sheet_id}, 记录数: {len(records)}")
        
        print(f"[表格] 数据格式: 智能表格记录格式（使用字段标题）")
        print(f"[表格] 字段列表: {headers[:10]}...")  # 只显示前10个
        
        # ⭐ 验证数据写入的字段顺序
        print(f"[表格] 🔍 数据写入验证（前10个字段）:")
        for idx, header in enumerate(headers[:10]):
            sample_value = data_rows[0][idx] if data_rows and idx < len(data_rows[0]) else "N/A"
            print(f"[表格]   {idx+1}. {header} = {sample_value}")
        
        if records:
            # 显示第一条记录的前3个字段
            first_record_values = records[0]['values']
            preview_items = list(first_record_values.items())[:3]
            preview_dict = {k: v[0]['text'] for k, v in preview_items}
            print(f"[表格] 示例记录（前3个字段）: {preview_dict}")
        
        try:
            response = requests.post(
                url,
                params={'access_token': access_token},
                json=data,
                timeout=30,
                proxies=self.proxies
            )
            
            print(f"[表格] HTTP 状态码: {response.status_code}")
            print(f"[表格] 响应头 Content-Type: {response.headers.get('Content-Type')}")
            print(f"[表格] 响应内容前500字符: {response.text[:500]}")
            
            # 尝试解析 JSON
            try:
                result = response.json()
            except Exception as json_error:
                print(f"[表格] JSON 解析失败: {json_error}")
                print(f"[表格] 完整响应内容: {response.text}")
                
                # 如果是 404，说明接口不存在，返回特殊错误码
                if response.status_code == 404:
                    return {
                        "errcode": -404, 
                        "errmsg": "智能表格暂不支持 API 写入数据，请手动导入"
                    }
                
                return {"errcode": -1, "errmsg": f"响应不是 JSON 格式: {response.text[:200]}"}
            
            print(f"[表格] API 响应: errcode={result.get('errcode')}, errmsg={result.get('errmsg')}")
            
            if result.get('errcode') == 0:
                print(f"[表格] 写入成功")
                
                # ⭐ 检测空白列（默认字段）
                print(f"[表格] Step 4: 检测空白列...")
                empty_columns = []
                if sheet_id:
                    try:
                        get_fields_url = f"{self.api_base}/wedoc/smartsheet/get_fields"
                        get_fields_response = requests.post(
                            get_fields_url,
                            params={'access_token': access_token},
                            json={"docid": docid, "sheet_id": sheet_id},
                            timeout=10,
                            proxies=self.proxies
                        )
                        get_fields_result = get_fields_response.json()
                        
                        if get_fields_result.get('errcode') == 0:
                            fields = get_fields_result.get('fields', [])
                            
                            # 检测默认字段（这些字段名不在我们的 headers 中）
                            default_field_names = ['文本', '数字', '日期', '货选', '人员', '串联']
                            for idx, field in enumerate(fields):
                                field_title = field.get('field_title', '')
                                if field_title in default_field_names:
                                    empty_columns.append({
                                        'index': idx + 1,
                                        'field_title': field_title,
                                        'field_type': field.get('field_type', '')
                                    })
                                    print(f"[表格]   发现空白列: 第{idx+1}列 - {field_title} ({field.get('field_type')})")
                            
                            print(f"[表格] 空白列检测完成: 发现 {len(empty_columns)} 个空白列")
                    except Exception as detect_error:
                        print(f"[表格] 空白列检测失败: {detect_error}")
                
                # 返回详细结果
                return {
                    'errcode': 0,
                    'errmsg': 'ok',
                    'field_count': len(headers),
                    'record_count': len(records),
                    'empty_columns': empty_columns,
                    'optimization_tip': len(empty_columns) > 0
                }
            else:
                print(f"[表格] 写入失败: {result.get('errmsg')}")
            
            return result
        except Exception as e:
            print(f"[表格] 写入数据失败: {e}")
            return {"errcode": -1, "errmsg": str(e)}
    
    def set_spreadsheet_permission(self, docid: str, member_list: List[Dict], auth_type: int = 1) -> Dict:
        """
        设置表格权限
        
        Args:
            docid: 文档ID
            member_list: 成员列表
                例如：[
                    {"type": 1, "userid": "zhangsan"},  # 1=成员
                    {"type": 2, "departmentid": 1}      # 2=部门
                ]
            auth_type: 权限类型
                1=可查看，2=可编辑
        
        Returns:
            {
                "errcode": 0,
                "errmsg": "ok"
            }
        """
        access_token = self.get_access_token('app')
        url = f"{self.api_base}/wedoc/mod_doc_member"
        
        data = {
            "docid": docid,
            "auth_type": auth_type,
            "member_list": member_list
        }
        
        print(f"[表格] 设置权限，docid={docid}, auth_type={auth_type}")
        
        try:
            response = requests.post(
                url,
                params={'access_token': access_token},
                json=data,
                timeout=10,
                proxies=self.proxies
            )
            result = response.json()
            
            print(f"[表格] API 响应: errcode={result.get('errcode')}, errmsg={result.get('errmsg')}")
            
            return result
        except Exception as e:
            print(f"[表格] 设置权限失败: {e}")
            return {"errcode": -1, "errmsg": str(e)}
    
    def read_spreadsheet_data(self, docid: str, range_str: str = None) -> Dict:
        """
        读取表格数据
        
        Args:
            docid: 文档ID
            range_str: 读取范围，例如：Sheet1!A1:Z100
                      如果不指定，默认读取整个表格
        
        Returns:
            {
                "errcode": 0,
                "errmsg": "ok",
                "values": [
                    ["姓名", "公司", "电话"],
                    ["张三", "阿里巴巴", "138xxx"]
                ]
            }
        """
        access_token = self.get_access_token('app')
        url = f"{self.api_base}/wedoc/spreadsheet/get"
        
        data = {
            "docid": docid
        }
        
        if range_str:
            data["range"] = range_str
        
        print(f"[表格] 读取数据，docid={docid}, 范围={range_str or '全部'}")
        
        try:
            response = requests.post(
                url,
                params={'access_token': access_token},
                json=data,
                timeout=30,
                proxies=self.proxies
            )
            result = response.json()
            
            print(f"[表格] API 响应: errcode={result.get('errcode')}, errmsg={result.get('errmsg')}")
            
            if result.get('errcode') == 0:
                values = result.get('values', [])
                print(f"[表格] 读取成功，共 {len(values)} 行")
                return result
            else:
                print(f"[表格] 读取失败: {result.get('errmsg')}")
                return result
        except Exception as e:
            print(f"[表格] 读取数据失败: {e}")
            return {"errcode": -1, "errmsg": str(e)}
    
    def get_spreadsheet_sheets(self, docid: str) -> Dict:
        """
        获取智能表格的子表列表
        
        Args:
            docid: 文档ID
        
        Returns:
            {
                "errcode": 0,
                "errmsg": "ok",
                "sheet_list": [
                    {
                        "sheet_id": "SHEET123",
                        "title": "工作表1",
                        "index": 0
                    }
                ]
            }
        """
        access_token = self.get_access_token('app')
        # 使用正确的 API：get_sheet（单数），不是 get_sheets
        url = f"{self.api_base}/wedoc/smartsheet/get_sheet"
        
        data = {"docid": docid}
        
        print(f"[表格] 获取子表信息，docid={docid}")
        print(f"[表格] API 路径: {url}")
        
        try:
            response = requests.post(
                url,
                params={'access_token': access_token},
                json=data,
                timeout=10,
                proxies=self.proxies
            )
            
            print(f"[表格] HTTP 状态码: {response.status_code}")
            print(f"[表格] 响应内容: {response.text[:300]}")
            
            result = response.json()
            
            if result.get('errcode') == 0:
                sheets = result.get('sheet_list', [])
                print(f"[表格] 获取到 {len(sheets)} 个子表")
                return result
            else:
                print(f"[表格] 获取子表失败: {result.get('errmsg')}")
                return result
        except Exception as e:
            print(f"[表格] 获取子表失败: {e}")
            return {"errcode": -1, "errmsg": str(e)}
    
    def add_spreadsheet_fields(self, docid: str, sheet_id: Optional[str], headers: List[str]) -> Dict:
        """
        添加智能表格字段（倒序添加，解决顺序问题）
        
        Args:
            docid: 文档ID
            sheet_id: 子表ID（可选）
            headers: 字段名称列表
        
        Returns:
            {
                "errcode": 0,
                "errmsg": "ok",
                "field_count": 10
            }
        """
        access_token = self.get_access_token('app')
        
        print(f"[表格] 添加字段: {len(headers)} 个")
        print(f"[表格] ⚠️  企业微信会自动创建5个默认字段，请在表格中手动隐藏")
        
        # 必须有 sheet_id
        if not sheet_id:
            print(f"[表格] ❌ 错误：缺少 sheet_id，无法添加字段")
            return {"errcode": -1, "errmsg": "缺少 sheet_id"}
        
        try:
            url = f"{self.api_base}/wedoc/smartsheet/add_fields"
            
            # 构建字段列表（倒序）
            fields = []
            for header in reversed(headers):
                fields.append({
                    "field_title": header,
                    "field_type": "FIELD_TYPE_TEXT"
                })
            
            data = {
                "docid": docid,
                "sheet_id": sheet_id,
                "fields": fields
            }
            
            print(f"[表格] 添加字段请求:")
            print(f"  - docid: {docid}")
            print(f"  - sheet_id: {sheet_id}")
            print(f"  - fields 数量: {len(fields)}")
            print(f"  - 添加顺序（倒序，前10个）: {[f['field_title'] for f in fields[:10]]}")
            
            response = requests.post(
                url,
                params={'access_token': access_token},
                json=data,
                timeout=30,
                proxies=self.proxies
            )
            
            print(f"[表格] HTTP 状态码: {response.status_code}")
            
            result = response.json()
            print(f"[表格] API 响应: errcode={result.get('errcode')}, errmsg={result.get('errmsg')}")
            
            if result.get('errcode') == 0:
                print(f"[表格] ✅ 添加成功: {len(headers)} 个字段")
                
                return {
                    "errcode": 0,
                    "errmsg": "ok",
                    "field_count": len(headers)
                }
            else:
                print(f"[表格] ❌ 添加字段失败: {result.get('errmsg')}")
                return result
                
        except Exception as e:
            print(f"[表格] 添加字段异常: {e}")
            import traceback
            traceback.print_exc()
            return {"errcode": -1, "errmsg": str(e)}
    
    def _delete_default_fields(self, docid: str, sheet_id: Optional[str]) -> Dict:
        """删除默认字段"""
        access_token = self.get_access_token('app')
        
        try:
            # 获取字段列表
            get_fields_url = f"{self.api_base}/wedoc/smartsheet/get_fields"
            get_fields_data = {"docid": docid}
            if sheet_id:
                get_fields_data["sheet_id"] = sheet_id
            
            response = requests.post(
                get_fields_url,
                params={'access_token': access_token},
                json=get_fields_data,
                timeout=10,
                proxies=self.proxies
            )
            fields_result = response.json()
            
            if fields_result.get('errcode') != 0:
                return fields_result
            
            existing_fields = fields_result.get('fields', [])
            
            # 默认字段名称
            default_field_names = ['文本', '数字', '日期', '货选', '人员', '串联']
            
            # 找出默认字段的 field_id
            field_ids_to_delete = []
            for field in existing_fields:
                field_title = field.get('field_title', '')
                if field_title in default_field_names:
                    field_ids_to_delete.append(field.get('field_id'))
            
            if not field_ids_to_delete:
                print(f"[表格] 没有找到默认字段")
                return {"errcode": 0, "errmsg": "ok"}
            
            # 删除默认字段
            delete_url = f"{self.api_base}/wedoc/smartsheet/delete_fields"
            delete_data = {
                "docid": docid,
                "field_ids": field_ids_to_delete
            }
            if sheet_id:
                delete_data["sheet_id"] = sheet_id
            
            response = requests.post(
                delete_url,
                params={'access_token': access_token},
                json=delete_data,
                timeout=10,
                proxies=self.proxies
            )
            result = response.json()
            
            if result.get('errcode') == 0:
                print(f"[表格] ✅ 已删除 {len(field_ids_to_delete)} 个默认字段")
            else:
                print(f"[表格] ⚠️  删除默认字段失败: {result.get('errmsg')}")
            
            return result
            
        except Exception as e:
            print(f"[表格] 删除默认字段异常: {e}")
            return {"errcode": -1, "errmsg": str(e)}
    
    def _verify_field_order(self, docid: str, sheet_id: Optional[str], expected_headers: List[str]):
        """验证字段顺序"""
        access_token = self.get_access_token('app')
        
        try:
            get_fields_url = f"{self.api_base}/wedoc/smartsheet/get_fields"
            get_fields_data = {"docid": docid}
            if sheet_id:
                get_fields_data["sheet_id"] = sheet_id
            
            response = requests.post(
                get_fields_url,
                params={'access_token': access_token},
                json=get_fields_data,
                timeout=10,
                proxies=self.proxies
            )
            result = response.json()
            
            if result.get('errcode') == 0:
                fields = result.get('fields', [])
                actual_titles = [f.get('field_title') for f in fields[:10]]
                print(f"[表格] 实际字段顺序（前10个）: {actual_titles}")
            
        except Exception as e:
            print(f"[表格] 验证字段顺序失败: {e}")
            return {"errcode": -1, "errmsg": str(e)}
            return {"errcode": -1, "errmsg": str(e)}
    
    def export_customers_to_spreadsheet(self, customers: List[Dict], doc_name: str, admin_users: List[str] = None) -> Dict:
        """
        导出客户列表到企业微信表格（一站式方法）
        
        Args:
            customers: 客户列表
            doc_name: 表格名称
            admin_users: 管理员列表
        
        Returns:
            {
                "success": True,
                "docid": "doc_xxxxxxxxxxxx",
                "url": "https://doc.weixin.qq.com/sheet/xxxxx",
                "count": 100
            }
        """
        print(f"[导出] 开始导出 {len(customers)} 个客户到企业微信表格")
        
        # 1. 创建表格
        create_result = self.create_spreadsheet(doc_name, admin_users)
        
        if create_result.get('errcode') != 0:
            return {
                "success": False,
                "message": f"创建表格失败: {create_result.get('errmsg')}"
            }
        
        docid = create_result.get('docid')
        url = create_result.get('url')
        
        # 2. 准备数据
        # 表头
        headers = ["客户姓名", "公司名称", "职位", "性别", "手机号", "邮箱", "所属员工", "客户标签", "添加时间", "备注"]
        
        # 数据行
        rows = [headers]
        for customer in customers:
            # 性别转换
            gender_map = {1: "男", 2: "女", 0: "未知"}
            gender = gender_map.get(customer.get('gender', 0), "未知")
            
            # 标签转换
            tags = customer.get('tags', [])
            if isinstance(tags, str):
                tags_text = tags
            elif isinstance(tags, list):
                tags_text = ", ".join([tag.get('tag_name', '') for tag in tags if isinstance(tag, dict)])
            else:
                tags_text = ""
            
            # 添加时间转换
            add_time = customer.get('add_time', 0)
            if add_time and add_time > 0:
                from datetime import datetime
                add_time_str = datetime.fromtimestamp(add_time).strftime('%Y-%m-%d %H:%M:%S')
            else:
                add_time_str = ""
            
            row = [
                customer.get('name', ''),
                customer.get('corp_name', ''),
                customer.get('position', ''),
                gender,
                customer.get('phone', ''),
                customer.get('email', ''),
                customer.get('owner_name', ''),
                tags_text,
                add_time_str,
                customer.get('remark', '')
            ]
            rows.append(row)
        
        # 3. 写入数据
        write_result = self.write_spreadsheet_data(docid, rows)
        
        if write_result.get('errcode') != 0:
            return {
                "success": False,
                "message": f"写入数据失败: {write_result.get('errmsg')}"
            }
        
        print(f"[导出] 导出成功，共 {len(customers)} 个客户")
        
        return {
            "success": True,
            "docid": docid,
            "url": url,
            "count": len(customers),
            "message": f"成功导出 {len(customers)} 个客户到企业微信表格"
        }

# 创建全局实例
wecom_client = WeComClient()
