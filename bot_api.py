"""
企微机器人模块 - 后端API
处理webhook配置、消息发送、历史记录等
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json
import requests
import hashlib
import base64
from datetime import datetime

router = APIRouter()
DB_PATH = 'data/crm.db'

# ========== 数据模型 ==========

class WebhookCreate(BaseModel):
    """创建Webhook配置"""
    group_name: str
    group_type: str  # 'supplier' 或 'agent'
    webhook_url: str
    purpose: Optional[str] = None
    remark: Optional[str] = None

class NotificationCreate(BaseModel):
    """创建通知消息"""
    group_type: str  # 'supplier' 或 'agent'
    title: Optional[str] = None
    content: str
    msg_type: str  # text, markdown, image, news, file, template_card
    target_webhooks: List[int]  # webhook ID列表
    mentioned_list: Optional[List[str]] = None  # @成员列表
    send_mode: str = 'manual'  # manual 或 auto
    send_time: Optional[str] = None  # 定时发送时间
    need_approval: int = 0  # 是否需要审核

# ========== Webhook管理 ==========

@router.get("/webhooks")
def get_webhooks(group_type: Optional[str] = None, api_token: str = None):
    """获取webhook列表"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if group_type:
            cursor.execute("""
                SELECT id, group_name, group_type, webhook_url, purpose, remark, status, 
                       created_at, updated_at
                FROM bot_webhooks 
                WHERE group_type = ?
                ORDER BY created_at DESC
            """, (group_type,))
        else:
            cursor.execute("""
                SELECT id, group_name, group_type, webhook_url, purpose, remark, status,
                       created_at, updated_at
                FROM bot_webhooks 
                ORDER BY created_at DESC
            """)
        
        rows = cursor.fetchall()
        webhooks = []
        for row in rows:
            webhooks.append({
                'id': row[0],
                'group_name': row[1],
                'group_type': row[2],
                'webhook_url': row[3],
                'purpose': row[4],
                'remark': row[5],
                'status': row[6],
                'created_at': row[7],
                'updated_at': row[8]
            })
        
        conn.close()
        return webhooks
        
    except Exception as e:
        return {'success': False, 'message': str(e)}

@router.post("/webhooks")
def create_webhook(webhook: WebhookCreate, api_token: str = None):
    """创建webhook配置"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查webhook_url是否已存在
        cursor.execute("SELECT id FROM bot_webhooks WHERE webhook_url = ?", (webhook.webhook_url,))
        if cursor.fetchone():
            conn.close()
            return {'success': False, 'message': 'Webhook地址已存在'}
        
        # 插入数据
        now = int(datetime.now().timestamp() * 1000)  # 毫秒时间戳
        cursor.execute("""
            INSERT INTO bot_webhooks (group_name, group_type, webhook_url, purpose, remark, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (webhook.group_name, webhook.group_type, webhook.webhook_url, webhook.purpose, webhook.remark, now, now))
        
        webhook_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': '添加成功', 'id': webhook_id}
        
    except Exception as e:
        return {'success': False, 'message': str(e)}

@router.delete("/webhooks/{webhook_id}")
def delete_webhook(webhook_id: int, api_token: str = None):
    """删除webhook配置"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM bot_webhooks WHERE id = ?", (webhook_id,))
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': '删除成功'}
        
    except Exception as e:
        return {'success': False, 'message': str(e)}

@router.post("/webhooks/{webhook_id}/test")
def test_webhook(webhook_id: int, api_token: str = None):
    """测试webhook"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取webhook信息
        cursor.execute("""
            SELECT group_name, webhook_url, status 
            FROM bot_webhooks 
            WHERE id = ?
        """, (webhook_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {'success': False, 'message': 'Webhook不存在'}
        
        group_name = row[0]
        webhook_url = row[1]
        status = row[2]
        
        if status != 'active':
            conn.close()
            return {'success': False, 'message': 'Webhook已停用'}
        
        # 发送测试消息
        test_message = {
            'msgtype': 'text',
            'text': {
                'content': f'🤖 这是来自【{group_name}】的测试消息\n\n发送时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n如果您看到这条消息，说明机器人配置正常！'
            }
        }
        
        response = requests.post(webhook_url, json=test_message, timeout=10)
        response_data = response.json()
        
        conn.close()
        
        if response_data.get('errcode') == 0:
            return {
                'success': True,
                'message': '测试成功！请检查群聊是否收到消息',
                'response': response_data
            }
        else:
            return {
                'success': False,
                'message': f'测试失败：{response_data.get("errmsg", "未知错误")}',
                'response': response_data
            }
        
    except Exception as e:
        return {'success': False, 'message': f'测试失败：{str(e)}'}

@router.put("/webhooks/{webhook_id}")
def update_webhook(webhook_id: int, webhook: WebhookCreate, api_token: str = None):
    """更新webhook配置"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查webhook是否存在
        cursor.execute("SELECT id FROM bot_webhooks WHERE id = ?", (webhook_id,))
        if not cursor.fetchone():
            conn.close()
            return {'success': False, 'message': 'Webhook不存在'}
        
        # 检查新的webhook_url是否与其他记录重复
        cursor.execute("""
            SELECT id FROM bot_webhooks 
            WHERE webhook_url = ? AND id != ?
        """, (webhook.webhook_url, webhook_id))
        if cursor.fetchone():
            conn.close()
            return {'success': False, 'message': 'Webhook地址已被其他配置使用'}
        
        # 更新数据
        now = int(datetime.now().timestamp() * 1000)
        cursor.execute("""
            UPDATE bot_webhooks 
            SET group_name = ?, group_type = ?, webhook_url = ?, purpose = ?, remark = ?, updated_at = ?
            WHERE id = ?
        """, (webhook.group_name, webhook.group_type, webhook.webhook_url, webhook.purpose, webhook.remark, now, webhook_id))
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': '更新成功'}
        
    except Exception as e:
        return {'success': False, 'message': str(e)}

@router.patch("/webhooks/{webhook_id}/status")
def toggle_webhook_status(webhook_id: int, api_token: str = None):
    """切换webhook状态（启用/停用）"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取当前状态
        cursor.execute("SELECT status FROM bot_webhooks WHERE id = ?", (webhook_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {'success': False, 'message': 'Webhook不存在'}
        
        current_status = row[0]
        new_status = 'inactive' if current_status == 'active' else 'active'
        
        # 更新状态
        now = int(datetime.now().timestamp() * 1000)
        cursor.execute("""
            UPDATE bot_webhooks 
            SET status = ?, updated_at = ?
            WHERE id = ?
        """, (new_status, now, webhook_id))
        
        conn.commit()
        conn.close()
        
        status_text = '启用' if new_status == 'active' else '停用'
        return {'success': True, 'message': f'已{status_text}', 'status': new_status}
        
    except Exception as e:
        return {'success': False, 'message': str(e)}

# ========== 通知消息管理 ==========

@router.get("/notifications")
def get_notifications(group_type: Optional[str] = None, status: Optional[str] = None, api_token: str = None):
    """获取通知列表"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        sql = """
            SELECT id, group_type, title, content, msg_type, target_webhooks, mentioned_list,
                   send_mode, send_time, status, need_approval, approval_status,
                   created_by, created_at, updated_at
            FROM bot_notifications 
            WHERE 1=1
        """
        params = []
        
        if group_type:
            sql += " AND group_type = ?"
            params.append(group_type)
        
        if status:
            sql += " AND status = ?"
            params.append(status)
        
        sql += " ORDER BY created_at DESC LIMIT 100"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        notifications = []
        for row in rows:
            notifications.append({
                'id': row[0],
                'group_type': row[1],
                'title': row[2],
                'content': row[3],
                'msg_type': row[4],
                'target_webhooks': json.loads(row[5]) if row[5] else [],
                'mentioned_list': json.loads(row[6]) if row[6] else [],
                'send_mode': row[7],
                'send_time': row[8],
                'status': row[9],
                'need_approval': row[10],
                'approval_status': row[11],
                'created_by': row[12],
                'created_at': row[13],
                'updated_at': row[14]
            })
        
        conn.close()
        return notifications
        
    except Exception as e:
        return {'success': False, 'message': str(e)}

@router.post("/notifications")
def create_notification(notification: NotificationCreate, api_token: str = None):
    """创建通知消息并发送"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 插入通知记录
        now = int(datetime.now().timestamp() * 1000)  # 毫秒时间戳
        cursor.execute("""
            INSERT INTO bot_notifications 
            (group_type, title, content, msg_type, target_webhooks, mentioned_list, 
             send_mode, send_time, status, need_approval, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            notification.group_type,
            notification.title,
            notification.content,
            notification.msg_type,
            json.dumps(notification.target_webhooks),
            json.dumps(notification.mentioned_list) if notification.mentioned_list else None,
            notification.send_mode,
            notification.send_time,
            'pending',  # 初始状态为待发送
            notification.need_approval,
            now,
            now
        ))
        
        notification_id = cursor.lastrowid
        conn.commit()
        
        # 如果是手动模式且没有定时，立即发送
        if notification.send_mode == 'manual' and not notification.send_time:
            # 获取webhook详情和发送
            target_webhooks = notification.target_webhooks
            webhook_ids_str = ','.join('?' * len(target_webhooks))
            cursor.execute(f"""
                SELECT id, group_name, webhook_url 
                FROM bot_webhooks 
                WHERE id IN ({webhook_ids_str}) AND status = 'active'
            """, target_webhooks)
            
            webhooks = cursor.fetchall()
            
            # 解析消息内容
            content_obj = json.loads(notification.content)
            
            # 发送到每个webhook
            success_count = 0
            failed_count = 0
            
            for webhook in webhooks:
                webhook_id = webhook[0]
                webhook_name = webhook[1]
                webhook_url = webhook[2]
                
                try:
                    # 发送请求
                    response = requests.post(webhook_url, json=content_obj, timeout=10)
                    response_data = response.json()
                    
                    send_timestamp = int(datetime.now().timestamp() * 1000)
                    
                    if response_data.get('errcode') == 0:
                        status = 'success'
                        error_msg = None
                        success_count += 1
                    else:
                        status = 'failed'
                        error_msg = response_data.get('errmsg', '未知错误')
                        failed_count += 1
                    
                    # 记录发送日志
                    cursor.execute("""
                        INSERT INTO bot_send_logs 
                        (notification_id, webhook_id, webhook_name, send_time, status, error_msg, response, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (notification_id, webhook_id, webhook_name, send_timestamp, status, error_msg, json.dumps(response_data), send_timestamp))
                    
                except Exception as e:
                    failed_count += 1
                    send_timestamp = int(datetime.now().timestamp() * 1000)
                    cursor.execute("""
                        INSERT INTO bot_send_logs 
                        (notification_id, webhook_id, webhook_name, send_time, status, error_msg, created_at)
                        VALUES (?, ?, ?, ?, 'failed', ?, ?)
                    """, (notification_id, webhook_id, webhook_name, send_timestamp, str(e), send_timestamp))
            
            # 更新通知状态
            final_status = 'sent' if failed_count == 0 else 'failed'
            now = int(datetime.now().timestamp() * 1000)
            cursor.execute("""
                UPDATE bot_notifications 
                SET status = ?, updated_at = ?
                WHERE id = ?
            """, (final_status, now, notification_id))
            
            conn.commit()
            
            return {
                'success': True,
                'message': f'发送完成：成功 {success_count} 个，失败 {failed_count} 个',
                'id': notification_id,
                'success_count': success_count,
                'failed_count': failed_count
            }
        
        conn.close()
        
        return {'success': True, 'message': '创建成功', 'id': notification_id}
        
    except Exception as e:
        return {'success': False, 'message': str(e)}

@router.post("/notifications/{notification_id}/send")
def send_notification(notification_id: int, api_token: str = None):
    """发送通知消息"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取通知详情
        cursor.execute("""
            SELECT group_type, content, msg_type, target_webhooks, mentioned_list
            FROM bot_notifications 
            WHERE id = ?
        """, (notification_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {'success': False, 'message': '通知不存在'}
        
        content = row[1]
        msg_type = row[2]
        target_webhooks = json.loads(row[3])
        mentioned_list = json.loads(row[4]) if row[4] else []
        
        # 更新状态为发送中
        now = int(datetime.now().timestamp() * 1000)
        cursor.execute("""
            UPDATE bot_notifications 
            SET status = 'sending', updated_at = ?
            WHERE id = ?
        """, (now, notification_id))
        conn.commit()
        
        # 获取webhook详情
        webhook_ids_str = ','.join('?' * len(target_webhooks))
        cursor.execute(f"""
            SELECT id, name, webhook_url 
            FROM bot_webhooks 
            WHERE id IN ({webhook_ids_str}) AND is_active = 1
        """, target_webhooks)
        
        webhooks = cursor.fetchall()
        
        # 发送到每个webhook
        success_count = 0
        failed_count = 0
        
        for webhook in webhooks:
            webhook_id = webhook[0]
            webhook_name = webhook[1]
            webhook_url = webhook[2]
            
            try:
                # 构建消息体
                if msg_type == 'text':
                    data = {
                        'msgtype': 'text',
                        'text': {
                            'content': content
                        }
                    }
                    if mentioned_list:
                        data['text']['mentioned_list'] = mentioned_list
                
                elif msg_type == 'markdown':
                    data = {
                        'msgtype': 'markdown',
                        'markdown': {
                            'content': content
                        }
                    }
                
                else:
                    # 其他类型暂时不支持
                    data = {
                        'msgtype': 'text',
                        'text': {
                            'content': content
                        }
                    }
                
                # 发送请求
                response = requests.post(webhook_url, json=data, timeout=10)
                response_data = response.json()
                
                if response_data.get('errcode') == 0:
                    # 发送成功
                    status = 'success'
                    error_msg = None
                    success_count += 1
                else:
                    # 发送失败
                    status = 'failed'
                    error_msg = response_data.get('errmsg', '未知错误')
                    failed_count += 1
                
                # 记录发送日志
                send_timestamp = int(datetime.now().timestamp() * 1000)
                cursor.execute("""
                    INSERT INTO bot_send_logs 
                    (notification_id, webhook_id, webhook_name, send_time, status, error_msg, response, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (notification_id, webhook_id, webhook_name, send_timestamp, status, error_msg, json.dumps(response_data), send_timestamp))
                
            except Exception as e:
                # 发送异常
                failed_count += 1
                send_timestamp = int(datetime.now().timestamp() * 1000)
                cursor.execute("""
                    INSERT INTO bot_send_logs 
                    (notification_id, webhook_id, webhook_name, send_time, status, error_msg, created_at)
                    VALUES (?, ?, ?, ?, 'failed', ?, ?)
                """, (notification_id, webhook_id, webhook_name, send_timestamp, str(e), send_timestamp))
        
        # 更新通知状态
        final_status = 'sent' if failed_count == 0 else 'failed'
        now = int(datetime.now().timestamp() * 1000)
        cursor.execute("""
            UPDATE bot_notifications 
            SET status = ?, updated_at = ?
            WHERE id = ?
        """, (final_status, now, notification_id))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'message': f'发送完成：成功 {success_count} 个，失败 {failed_count} 个',
            'success_count': success_count,
            'failed_count': failed_count
        }
        
    except Exception as e:
        return {'success': False, 'message': str(e)}

@router.get("/notifications/{notification_id}")
def get_notification_detail(notification_id: int, api_token: str = None):
    """获取通知详情"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取通知基本信息
        cursor.execute("""
            SELECT id, group_type, title, content, msg_type, target_webhooks, mentioned_list,
                   send_mode, send_time, status, need_approval, approval_status,
                   created_by, created_at, updated_at
            FROM bot_notifications 
            WHERE id = ?
        """, (notification_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {'success': False, 'message': '通知不存在'}
        
        notification = {
            'id': row[0],
            'group_type': row[1],
            'title': row[2],
            'content': row[3],
            'msg_type': row[4],
            'target_webhooks': json.loads(row[5]) if row[5] else [],
            'mentioned_list': json.loads(row[6]) if row[6] else [],
            'send_mode': row[7],
            'send_time': row[8],
            'status': row[9],
            'need_approval': row[10],
            'approval_status': row[11],
            'created_by': row[12],
            'created_at': row[13],
            'updated_at': row[14]
        }
        
        # 获取目标群信息
        target_webhook_ids = notification['target_webhooks']
        if target_webhook_ids:
            webhook_ids_str = ','.join('?' * len(target_webhook_ids))
            cursor.execute(f"""
                SELECT id, group_name, webhook_url, status
                FROM bot_webhooks 
                WHERE id IN ({webhook_ids_str})
            """, target_webhook_ids)
            
            webhooks = []
            for wrow in cursor.fetchall():
                webhooks.append({
                    'id': wrow[0],
                    'group_name': wrow[1],
                    'webhook_url': wrow[2],
                    'status': wrow[3]
                })
            notification['webhooks'] = webhooks
        else:
            notification['webhooks'] = []
        
        # 获取发送记录
        cursor.execute("""
            SELECT id, webhook_id, webhook_name, send_time, status, error_msg, response
            FROM bot_send_logs
            WHERE notification_id = ?
            ORDER BY send_time DESC
        """, (notification_id,))
        
        send_logs = []
        for lrow in cursor.fetchall():
            send_logs.append({
                'id': lrow[0],
                'webhook_id': lrow[1],
                'webhook_name': lrow[2],
                'send_time': lrow[3],
                'status': lrow[4],
                'error_msg': lrow[5],
                'response': json.loads(lrow[6]) if lrow[6] else None
            })
        notification['send_logs'] = send_logs
        
        conn.close()
        return notification
        
    except Exception as e:
        return {'success': False, 'message': str(e)}

@router.get("/send-logs/{notification_id}")
def get_send_logs(notification_id: int, api_token: str = None):
    """获取发送记录"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, webhook_name, send_time, status, error_msg, response
            FROM bot_send_logs
            WHERE notification_id = ?
            ORDER BY send_time DESC
        """, (notification_id,))
        
        rows = cursor.fetchall()
        logs = []
        for row in rows:
            logs.append({
                'id': row[0],
                'webhook_name': row[1],
                'send_time': row[2],
                'status': row[3],
                'error_msg': row[4],
                'response': json.loads(row[5]) if row[5] else None
            })
        
        conn.close()
        return logs
        
    except Exception as e:
        return {'success': False, 'message': str(e)}
