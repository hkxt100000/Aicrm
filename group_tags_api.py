#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户群标签 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import time
import json
import uuid
import threading

from config import DB_PATH, API_TOKEN

# 创建路由器
router = APIRouter()

# 任务状态存储
sync_tasks = {}
sync_tasks_lock = threading.Lock()

# Token 验证
def check_token(api_token: str):
    if api_token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API token")
    return api_token

# ========== 数据模型 ==========

class TagModel(BaseModel):
    """标签模型"""
    id: Optional[str] = None
    name: str
    order: int = 0

class GroupTagModel(BaseModel):
    """标签组模型"""
    group_id: Optional[str] = None
    group_name: str
    order: int = 0
    tag: List[TagModel] = []

# ========== 数据库操作 ==========

def get_all_group_tags():
    """获取所有标签组及其标签"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 获取所有标签组
    cursor.execute('''
        SELECT * FROM group_chat_tag_groups 
        ORDER BY order_index ASC, created_at DESC
    ''')
    groups = [dict(row) for row in cursor.fetchall()]
    
    # 为每个标签组获取标签
    for group in groups:
        cursor.execute('''
            SELECT * FROM group_chat_tags 
            WHERE group_id = ?
            ORDER BY order_index ASC, created_at DESC
        ''', (group['group_id'],))
        
        tags = []
        for tag_row in cursor.fetchall():
            tag_dict = dict(tag_row)
            tag_id = tag_dict['id']
            
            # 统计使用该标签的群数量
            cursor.execute('''
                SELECT COUNT(*) as group_count
                FROM group_chat_tag_relations
                WHERE tag_id = ?
            ''', (tag_id,))
            count_result = cursor.fetchone()
            group_count = count_result[0] if count_result else 0
            
            tags.append({
                'id': tag_id,
                'name': tag_dict['name'],
                'create_time': tag_dict['create_time'],
                'order': tag_dict['order_index'],
                'group_count': group_count  # 添加群数量
            })
        
        group['tag'] = tags
        group['order'] = group['order_index']
    
    conn.close()
    return groups

def create_group_tag(group_data: GroupTagModel):
    """创建标签组"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 生成 group_id
    group_id = f"GROUP_{int(time.time() * 1000)}"
    now = int(time.time())
    
    try:
        # 插入标签组
        cursor.execute('''
            INSERT INTO group_chat_tag_groups 
            (group_id, group_name, create_time, order_index, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (group_id, group_data.group_name, now, group_data.order, now, now))
        
        # 插入标签
        for idx, tag in enumerate(group_data.tag):
            tag_id = f"TAG_{int(time.time() * 1000)}_{idx}"
            cursor.execute('''
                INSERT INTO group_chat_tags 
                (id, group_id, name, create_time, order_index, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (tag_id, group_id, tag.name, now, tag.order, now, now))
        
        conn.commit()
        return {"success": True, "group_id": group_id}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

def update_group_tag(group_id: str, group_data: GroupTagModel):
    """更新标签组"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = int(time.time())
    
    try:
        # 更新标签组信息
        cursor.execute('''
            UPDATE group_chat_tag_groups 
            SET group_name = ?, order_index = ?, updated_at = ?
            WHERE group_id = ?
        ''', (group_data.group_name, group_data.order, now, group_id))
        
        # 获取现有标签
        cursor.execute('SELECT id FROM group_chat_tags WHERE group_id = ?', (group_id,))
        existing_tag_ids = {row[0] for row in cursor.fetchall()}
        
        # 处理标签
        new_tag_ids = set()
        for idx, tag in enumerate(group_data.tag):
            if tag.id and tag.id in existing_tag_ids:
                # 更新现有标签
                cursor.execute('''
                    UPDATE group_chat_tags 
                    SET name = ?, order_index = ?, updated_at = ?
                    WHERE id = ?
                ''', (tag.name, tag.order, now, tag.id))
                new_tag_ids.add(tag.id)
            else:
                # 新增标签
                tag_id = tag.id or f"TAG_{int(time.time() * 1000)}_{idx}"
                cursor.execute('''
                    INSERT INTO group_chat_tags 
                    (id, group_id, name, create_time, order_index, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (tag_id, group_id, tag.name, now, tag.order, now, now))
                new_tag_ids.add(tag_id)
        
        # 删除不再存在的标签
        tags_to_delete = existing_tag_ids - new_tag_ids
        if tags_to_delete:
            placeholders = ','.join('?' * len(tags_to_delete))
            cursor.execute(f'DELETE FROM group_chat_tags WHERE id IN ({placeholders})', tuple(tags_to_delete))
        
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

def delete_group_tag(group_id: str):
    """删除标签组"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 删除标签
        cursor.execute('DELETE FROM group_chat_tags WHERE group_id = ?', (group_id,))
        # 删除标签组
        cursor.execute('DELETE FROM group_chat_tag_groups WHERE group_id = ?', (group_id,))
        
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

def update_single_tag(group_id: str, tag_id: str, name: str, order: int):
    """更新单个标签"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = int(time.time())
    
    try:
        cursor.execute('''
            UPDATE group_chat_tags 
            SET name = ?, order_index = ?, updated_at = ?
            WHERE id = ? AND group_id = ?
        ''', (name, order, now, tag_id, group_id))
        
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

def delete_single_tag(group_id: str, tag_id: str):
    """删除单个标签"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM group_chat_tags WHERE id = ? AND group_id = ?', (tag_id, group_id))
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

# ========== API 路由 ==========

@router.get("/api/group-tags")
async def get_group_tags(token: str = Depends(check_token)):
    """获取客户群标签列表"""
    try:
        tags = get_all_group_tags()
        return {"success": True, "data": tags}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.post("/api/group-tags")
async def create_group_tag_api(group_data: GroupTagModel, token: str = Depends(check_token)):
    """创建标签组"""
    return create_group_tag(group_data)

@router.put("/api/group-tags/{group_id}")
async def update_group_tag_api(group_id: str, group_data: GroupTagModel, token: str = Depends(check_token)):
    """更新标签组"""
    return update_group_tag(group_id, group_data)

@router.delete("/api/group-tags/{group_id}")
async def delete_group_tag_api(group_id: str, token: str = Depends(check_token)):
    """删除标签组"""
    return delete_group_tag(group_id)

@router.put("/api/group-tags/{group_id}/tags/{tag_id}")
async def update_tag_api(
    group_id: str, 
    tag_id: str,
    data: dict,
    token: str = Depends(check_token)
):
    """更新单个标签"""
    name = data.get('name', '')
    order = data.get('order', 0)
    return update_single_tag(group_id, tag_id, name, order)

@router.delete("/api/group-tags/{group_id}/tags/{tag_id}")
async def delete_tag_api(group_id: str, tag_id: str, token: str = Depends(check_token)):
    """删除单个标签"""
    return delete_single_tag(group_id, tag_id)

# ========== 同步功能 ==========

def sync_group_tags_task(task_id: str):
    """
    自建标签系统 - 不从企业微信同步标签
    这个任务主要用于演示，实际标签完全由用户手动创建管理
    """
    try:
        with sync_tasks_lock:
            sync_tasks[task_id] = {
                "status": "running",
                "progress": 0,
                "message": "自建标签系统不需要从企业微信同步",
                "total": 0,
                "added": 0,
                "updated": 0,
                "failed": 0,
                "start_time": time.time()
            }
        
        print(f"[客户群标签] 任务 {task_id} 开始")
        print(f"[客户群标签] 提示：本系统使用自建标签，标签由用户手动创建管理")
        
        # 检查数据库中是否有标签
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        with sync_tasks_lock:
            sync_tasks[task_id]["message"] = "检查现有标签数据..."
            sync_tasks[task_id]["progress"] = 30
        
        cursor.execute('SELECT COUNT(*) FROM group_chat_tag_groups')
        groups_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM group_chat_tags')
        tags_count = cursor.fetchone()[0]
        
        conn.close()
        
        with sync_tasks_lock:
            sync_tasks[task_id]["status"] = "completed"
            sync_tasks[task_id]["progress"] = 100
            sync_tasks[task_id]["total"] = groups_count
            sync_tasks[task_id]["message"] = f"系统当前有 {groups_count} 个标签组，{tags_count} 个标签。请使用「新建标签组」按钮手动创建标签。"
            sync_tasks[task_id]["end_time"] = time.time()
        
        print(f"[客户群标签] 任务 {task_id} 完成")
        print(f"[客户群标签] 当前标签组数量: {groups_count}, 标签数量: {tags_count}")
        
    except Exception as e:
        print(f"[客户群标签] 任务 {task_id} 失败: {e}")
        with sync_tasks_lock:
            sync_tasks[task_id]["status"] = "failed"
            sync_tasks[task_id]["message"] = f"检查失败: {str(e)}"
            sync_tasks[task_id]["progress"] = 0

@router.post("/api/sync/group-tags")
async def sync_group_tags_api(background_tasks: BackgroundTasks, token: str = Depends(check_token)):
    """从企业微信同步客户群标签"""
    # 生成任务 ID
    task_id = f"sync_group_tags_{int(time.time() * 1000)}"
    
    # 启动后台任务
    background_tasks.add_task(sync_group_tags_task, task_id)
    
    print(f"[客户群标签同步] 创建任务: {task_id}")
    
    return {
        "success": True,
        "task_id": task_id,
        "message": "同步任务已启动"
    }

@router.get("/api/sync/group-tags/status/{task_id}")
async def get_sync_status(task_id: str, token: str = Depends(check_token)):
    """获取同步任务状态"""
    with sync_tasks_lock:
        if task_id not in sync_tasks:
            raise HTTPException(status_code=404, detail="任务不存在")
        return {
            "success": True,
            "data": sync_tasks[task_id]
        }

@router.post("/api/sync/group-tags/stop/{task_id}")
async def stop_sync_task(task_id: str, token: str = Depends(check_token)):
    """停止同步任务"""
    with sync_tasks_lock:
        if task_id not in sync_tasks:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        sync_tasks[task_id]["status"] = "stopped"
        sync_tasks[task_id]["message"] = "用户手动停止"
        
        return {
            "success": True,
            "message": "任务已停止"
        }

# ========== 客户群标签关联管理 ==========

@router.post("/api/group-chats/{chat_id}/tags")
async def add_tags_to_group(chat_id: str, tag_ids: List[str], token: str = Depends(check_token)):
    """给客户群添加标签"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        added = 0
        for tag_id in tag_ids:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO group_chat_tag_relations (chat_id, tag_id, created_at)
                    VALUES (?, ?, ?)
                ''', (chat_id, tag_id, int(time.time() * 1000)))
                if cursor.rowcount > 0:
                    added += 1
            except Exception as e:
                print(f"[群标签] 添加标签失败: {e}")
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"成功添加 {added} 个标签"
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.delete("/api/group-chats/{chat_id}/tags/{tag_id}")
async def remove_tag_from_group(chat_id: str, tag_id: str, token: str = Depends(check_token)):
    """从客户群移除标签"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM group_chat_tag_relations
            WHERE chat_id = ? AND tag_id = ?
        ''', (chat_id, tag_id))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "标签已移除"
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.get("/api/group-chats/{chat_id}/tags")
async def get_group_tags(chat_id: str, token: str = Depends(check_token)):
    """获取客户群的标签"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.*, r.created_at as relation_created_at
            FROM group_chat_tags t
            JOIN group_chat_tag_relations r ON t.id = r.tag_id
            WHERE r.chat_id = ?
            ORDER BY t.order_index
        ''', (chat_id,))
        
        tags = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "success": True,
            "data": tags
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.post("/api/group-chats/batch-tags")
async def batch_add_tags(data: dict, token: str = Depends(check_token)):
    """批量给客户群添加标签"""
    try:
        chat_ids = data.get('chat_ids', [])
        tag_ids = data.get('tag_ids', [])
        
        if not chat_ids or not tag_ids:
            return {"success": False, "message": "参数不完整"}
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        added = 0
        for chat_id in chat_ids:
            for tag_id in tag_ids:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO group_chat_tag_relations (chat_id, tag_id, created_at)
                        VALUES (?, ?, ?)
                    ''', (chat_id, tag_id, int(time.time() * 1000)))
                    if cursor.rowcount > 0:
                        added += 1
                except Exception as e:
                    print(f"[群标签] 批量添加失败: {e}")
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"成功为 {len(chat_ids)} 个群添加了 {added} 个标签关联"
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

# ========== 新增：单个和批量打标签 API ==========

class AssignTagRequest(BaseModel):
    """单个群打标签请求"""
    chat_id: str
    tags: List[dict]  # [{"tag_id": "xxx", "tag_name": "xxx"}]

class BatchAssignTagRequest(BaseModel):
    """批量打标签请求"""
    chat_ids: List[str]
    tags: List[dict]  # [{"tag_id": "xxx", "tag_name": "xxx"}]

@router.post("/api/group-tags/assign")
async def assign_tags_to_group(request: AssignTagRequest, api_token: str = Depends(check_token)):
    """给单个客户群打标签"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 先删除该群的所有标签
        cursor.execute('DELETE FROM group_chat_tag_relations WHERE chat_id = ?', (request.chat_id,))
        
        # 添加新标签
        added = 0
        for tag in request.tags:
            try:
                cursor.execute('''
                    INSERT INTO group_chat_tag_relations (chat_id, tag_id, tag_name, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (request.chat_id, tag['tag_id'], tag['tag_name'], int(time.time() * 1000)))
                added += 1
            except Exception as e:
                print(f"[群标签] 添加标签失败: {e}")
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"成功添加 {added} 个标签"
        }
    except Exception as e:
        print(f"[群标签] 打标签失败: {e}")
        return {"success": False, "message": str(e)}

@router.post("/api/group-tags/batch-assign")
async def batch_assign_tags_to_groups(request: BatchAssignTagRequest, api_token: str = Depends(check_token)):
    """批量给客户群打标签"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 先删除这些群的所有标签
        placeholders = ','.join(['?' for _ in request.chat_ids])
        cursor.execute(f'DELETE FROM group_chat_tag_relations WHERE chat_id IN ({placeholders})', request.chat_ids)
        
        # 批量添加新标签
        added = 0
        for chat_id in request.chat_ids:
            for tag in request.tags:
                try:
                    cursor.execute('''
                        INSERT INTO group_chat_tag_relations (chat_id, tag_id, tag_name, created_at)
                        VALUES (?, ?, ?, ?)
                    ''', (chat_id, tag['tag_id'], tag['tag_name'], int(time.time() * 1000)))
                    added += 1
                except Exception as e:
                    print(f"[群标签] 批量添加失败: {e}")
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"成功为 {len(request.chat_ids)} 个群添加了标签"
        }
    except Exception as e:
        print(f"[群标签] 批量打标签失败: {e}")
        return {"success": False, "message": str(e)}

print("[客户群标签API] 路由已加载")
