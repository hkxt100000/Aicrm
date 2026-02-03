"""
企业微信同步服务 - 支持并发、增量同步、后台队列
"""
import time
import json
import sqlite3
import threading
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from dataclasses import dataclass
from datetime import datetime

# 尝试导入 schedule，如果没有则禁用定时任务
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    print("⚠️ schedule 库未安装，定时同步功能已禁用。安装方法: pip install schedule")

from config import DB_PATH
from wecom_client import WeComClient


@dataclass
class SyncTask:
    """同步任务"""
    task_id: str
    task_type: str  # 'full' 或 'incremental'
    status: str  # 'pending', 'running', 'completed', 'failed'
    progress: int  # 0-100
    total_count: int
    processed_count: int
    added_count: int
    updated_count: int
    failed_count: int
    start_time: float
    end_time: Optional[float]
    error_message: Optional[str]


class SyncService:
    """同步服务"""
    
    def __init__(self, wecom_client: WeComClient, max_workers: int = 10):
        self.wecom_client = wecom_client
        self.max_workers = max_workers
        self.task_queue = Queue()
        self.active_tasks: Dict[str, SyncTask] = {}
        self.lock = threading.Lock()
        self.stop_flags: Dict[str, bool] = {}  # 停止标志
        
        # 启动后台工作线程
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        
        # 启动定时任务线程（仅当 schedule 可用时）
        if SCHEDULE_AVAILABLE:
            self.scheduler_thread = threading.Thread(target=self._scheduler, daemon=True)
            self.scheduler_thread.start()
            print(f"✅ 同步服务已启动 (最大并发: {max_workers} 线程)")
            print(f"⏰ 定时任务已启动 (每小时自动增量同步)")
        else:
            print(f"✅ 同步服务已启动 (最大并发: {max_workers} 线程)")
            print(f"⚠️ 定时任务未启动（需要安装 schedule 库）")
    
    def _worker(self):
        """后台工作线程"""
        while True:
            try:
                task = self.task_queue.get()
                if task is None:
                    break
                
                task_id = task['task_id']
                task_type = task['task_type']
                config = task.get('config')
                
                # 更新配置
                if config:
                    self.wecom_client.update_config(
                        corp_id=config.get('corpid'),
                        contact_secret=config.get('contact_secret'),
                        customer_secret=config.get('customer_secret'),
                        app_secret=config.get('app_secret'),
                        agent_id=config.get('agentid')
                    )
                
                # 执行同步
                if task_type == 'full':
                    self._sync_all_customers(task_id)
                elif task_type == 'incremental':
                    self._sync_incremental_customers(task_id)
                
                self.task_queue.task_done()
            except Exception as e:
                print(f"❌ 后台任务执行失败: {e}")
    
    def _scheduler(self):
        """定时任务调度器"""
        if not SCHEDULE_AVAILABLE:
            return
        
        # 每小时执行一次增量同步
        schedule.every().hour.at(":00").do(self._auto_sync)
        
        print("⏰ 定时同步已配置: 每小时执行一次增量同步")
        
        while True:
            schedule.run_pending()
            time.sleep(30)  # 每30秒检查一次
    
    def _auto_sync(self):
        """自动增量同步"""
        try:
            current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n{'='*80}")
            print(f"⏰ 定时任务触发: {current_time_str}")
            print(f"🔄 开始自动增量同步...")
            print(f"{'='*80}\n")
            
            # 启动增量同步任务
            task_id = self.start_sync_task(task_type='incremental')
            print(f"✅ 自动同步任务已启动: {task_id}")
        except Exception as e:
            print(f"❌ 自动同步失败: {e}")
    
    def start_sync_task(self, task_type: str = 'incremental', config: Optional[Dict] = None) -> str:
        """
        启动同步任务
        :param task_type: 'full' 或 'incremental'
        :param config: 企业微信配置
        :return: task_id
        """
        task_id = f"sync_{int(time.time() * 1000)}"
        
        # 创建任务记录
        task = SyncTask(
            task_id=task_id,
            task_type=task_type,
            status='pending',
            progress=0,
            total_count=0,
            processed_count=0,
            added_count=0,
            updated_count=0,
            failed_count=0,
            start_time=time.time(),
            end_time=None,
            error_message=None
        )
        
        with self.lock:
            self.active_tasks[task_id] = task
        
        # 添加到队列
        self.task_queue.put({
            'task_id': task_id,
            'task_type': task_type,
            'config': config
        })
        
        print(f"📋 同步任务已创建: {task_id} (类型: {task_type})")
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        with self.lock:
            task = self.active_tasks.get(task_id)
            if not task:
                return None
            
            return {
                'task_id': task.task_id,
                'task_type': task.task_type,
                'status': task.status,
                'progress': task.progress,
                'total_count': task.total_count,
                'processed_count': task.processed_count,
                'added_count': task.added_count,
                'updated_count': task.updated_count,
                'failed_count': task.failed_count,
                'start_time': task.start_time,
                'end_time': task.end_time,
                'error_message': task.error_message,
                'duration': (task.end_time or time.time()) - task.start_time
            }
    
    def _update_task(self, task_id: str, **kwargs):
        """更新任务状态"""
        with self.lock:
            task = self.active_tasks.get(task_id)
            if task:
                for key, value in kwargs.items():
                    setattr(task, key, value)
                
                # 计算进度
                if task.total_count > 0:
                    task.progress = int((task.processed_count / task.total_count) * 100)
    
    def stop_task(self, task_id: str) -> bool:
        """停止同步任务"""
        with self.lock:
            task = self.active_tasks.get(task_id)
            if not task:
                print(f"❌ 任务不存在: {task_id}")
                return False
            
            if task.status in ['completed', 'failed']:
                print(f"⚠️ 任务已结束: {task_id} (状态: {task.status})")
                return False
            
            # 设置停止标志
            self.stop_flags[task_id] = True
            print(f"🛑 停止任务请求已发出: {task_id}")
            return True
    
    def _should_stop(self, task_id: str) -> bool:
        """检查是否应该停止"""
        return self.stop_flags.get(task_id, False)
    
    def _sync_all_customers(self, task_id: str):
        """全量同步所有客户"""
        try:
            self._update_task(task_id, status='running')
            print(f"🔄 开始全量同步任务: {task_id}")
            
            # 获取所有成员
            users = self.wecom_client.get_user_list()
            if not users:
                self._update_task(
                    task_id,
                    status='failed',
                    error_message='未获取到成员列表',
                    end_time=time.time()
                )
                return
            
            print(f"👥 获取到 {len(users)} 个成员")
            
            # 检查是否被停止
            if self._should_stop(task_id):
                print(f"🛑 收到停止信号，正在终止同步任务: {task_id}")
                self._update_task(
                    task_id,
                    status='failed',
                    error_message='用户手动停止',
                    end_time=time.time()
                )
                return
            
            # 收集所有客户ID
            all_customer_ids = []
            for user in users:
                userid = user.get('userid')
                external_userids = self.wecom_client.get_external_contact_list(userid)
                all_customer_ids.extend([(eid, userid, user.get('name', '')) for eid in external_userids])
            
            self._update_task(task_id, total_count=len(all_customer_ids))
            print(f"📊 共 {len(all_customer_ids)} 个客户待同步")
            
            # 检查是否被停止
            if self._should_stop(task_id):
                print(f"🛑 收到停止信号，正在终止同步任务: {task_id}")
                self._update_task(
                    task_id,
                    status='failed',
                    error_message='用户手动停止',
                    end_time=time.time()
                )
                return
            
            # 并发获取客户详情
            self._sync_customers_concurrent(task_id, all_customer_ids)
            
        except Exception as e:
            print(f"❌ 全量同步失败: {e}")
            self._update_task(
                task_id,
                status='failed',
                error_message=str(e),
                end_time=time.time()
            )
    
    def _sync_incremental_customers(self, task_id: str):
        """增量同步 - 仅同步最近变化的客户"""
        try:
            self._update_task(task_id, status='running')
            print(f"🔄 开始增量同步任务: {task_id}")
            
            # 从 config 表获取上次同步时间
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM config WHERE key = ?", ('last_customer_sync_time',))
            result = cursor.fetchone()
            last_sync_time = int(result[0]) if result else 0
            print(f"📅 上次同步时间: {last_sync_time} ({time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_sync_time)) if last_sync_time > 0 else '从未同步'})")
            
            # 增量同步策略：
            # 1. 只同步数据库中不存在的客户（新客户）
            # 2. 只同步最近6小时有更新的客户（updated_at < 当前时间-6小时）
            # 注意：企业微信API不支持按时间筛选，所以需要先获取客户ID列表，然后对比数据库
            
            current_time = int(time.time())
            sync_threshold = current_time - (6 * 3600)  # 6小时阈值
            
            print(f"⏰ 同步阈值时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(sync_threshold))}")
            
            # 获取所有员工（这步无法避免，因为需要知道有哪些员工）
            users = self.wecom_client.get_user_list()
            if not users:
                self._update_task(
                    task_id,
                    status='failed',
                    error_message='未获取到成员列表',
                    end_time=time.time()
                )
                conn.close()
                return
            
            print(f"👥 获取到 {len(users)} 个成员")
            
            # 快速筛选策略：先查询数据库中需要更新的客户ID
            cursor.execute("""
                SELECT id, updated_at 
                FROM customers 
                WHERE updated_at IS NULL OR updated_at < ?
            """, (sync_threshold,))
            
            db_customers_to_update = {row[0]: row[1] for row in cursor.fetchall()}
            print(f"📊 数据库中有 {len(db_customers_to_update)} 个客户需要更新（6小时内未同步）")
            
            # 收集需要同步的客户
            customers_to_sync = []
            all_external_count = 0
            
            for user in users:
                userid = user.get('userid')
                username = user.get('name', '')
                
                # 获取该员工的客户列表
                external_userids = self.wecom_client.get_external_contact_list(userid)
                all_external_count += len(external_userids)
                
                for eid in external_userids:
                    # 检查是否需要同步
                    if eid not in db_customers_to_update:
                        # 检查是否是新客户
                        cursor.execute("SELECT id FROM customers WHERE id = ?", (eid,))
                        if not cursor.fetchone():
                            # 新客户，需要同步
                            customers_to_sync.append((eid, userid, username))
                            print(f"  ➕ 新客户: {eid} (跟进人: {username})")
                    else:
                        # 旧客户但需要更新
                        customers_to_sync.append((eid, userid, username))
                        last_update = db_customers_to_update[eid]
                        if last_update:
                            print(f"  🔄 更新客户: {eid} (上次更新: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_update))})")
                        else:
                            print(f"  🔄 更新客户: {eid} (从未同步)")
            
            conn.close()
            
            # 检查是否被停止
            if self._should_stop(task_id):
                print(f"🛑 收到停止信号，正在终止同步任务: {task_id}")
                self._update_task(
                    task_id,
                    status='failed',
                    error_message='用户手动停止',
                    end_time=time.time()
                )
                return
            
            self._update_task(task_id, total_count=len(customers_to_sync))
            print(f"\n📊 同步统计:")
            print(f"   - 企业微信总客户数: {all_external_count}")
            print(f"   - 需要同步的客户: {len(customers_to_sync)}")
            print(f"   - 跳过的客户: {all_external_count - len(customers_to_sync)}")
            
            if len(customers_to_sync) == 0:
                self._update_task(
                    task_id,
                    status='completed',
                    end_time=time.time()
                )
                print("\n✅ 无需同步，所有客户数据已是最新（6小时内已同步）")
                return
            
            # 并发获取客户详情
            print(f"\n🚀 开始同步 {len(customers_to_sync)} 个客户...")
            self._sync_customers_concurrent(task_id, customers_to_sync)
            
            # 记录本次同步时间到 config 表
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO config (key, value, updated_at) VALUES (?, ?, ?)",
                ('last_customer_sync_time', str(current_time), current_time)
            )
            conn.commit()
            conn.close()
            print(f"✅ 已更新同步时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}")
            
        except Exception as e:
            print(f"❌ 增量同步失败: {e}")
            self._update_task(
                task_id,
                status='failed',
                error_message=str(e),
                end_time=time.time()
            )
    
    def _sync_customers_concurrent(self, task_id: str, customer_list: List[tuple]):
        """
        并发同步客户列表
        :param task_id: 任务ID
        :param customer_list: [(external_userid, owner_userid, owner_name), ...]
        """
        added_count = 0
        updated_count = 0
        failed_count = 0
        processed_count = 0
        
        print(f"\n{'='*80}")
        print(f"🚀 开始10线程并发同步")
        print(f"📊 总客户数: {len(customer_list)}")
        print(f"🔧 线程池大小: {self.max_workers} 线程")
        print(f"{'='*80}\n")
        
        def fetch_and_save_customer(item):
            """获取并保存单个客户"""
            external_userid, owner_userid, owner_name = item
            try:
                # 获取客户详情
                detail = self.wecom_client.get_external_contact_detail(external_userid)
                if not detail:
                    return 'failed', None
                
                customer_data = detail.get('external_contact', {})
                follow_users = detail.get('follow_user', [])
                
                # 找到当前跟进人的记录
                current_follow = None
                for follow in follow_users:
                    if follow.get('userid') == owner_userid:
                        current_follow = follow
                        break
                
                # 合并跟进人信息
                if current_follow:
                    customer_data['owner_userid'] = owner_userid
                    customer_data['owner_name'] = owner_name
                    customer_data['add_time'] = current_follow.get('createtime', 0)
                    customer_data['remark'] = current_follow.get('remark', '')
                    customer_data['description'] = current_follow.get('description', '')
                    customer_data['add_way'] = current_follow.get('add_way', 0)
                    customer_data['state'] = current_follow.get('state', '')
                    customer_data['remark_mobiles'] = current_follow.get('remark_mobiles', [])
                    customer_data['remark_corp_name'] = current_follow.get('remark_corp_name', '')
                    customer_data['im_status'] = current_follow.get('oper_userid', '')
                    customer_data['tags'] = current_follow.get('tags', [])
                
                # 保存到数据库
                return self._save_customer(customer_data)
                
            except Exception as e:
                print(f"❌ 处理客户 {external_userid} 失败: {e}")
                return 'failed', None
        
        # 使用线程池并发处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(fetch_and_save_customer, item): item for item in customer_list}
            
            for future in as_completed(futures):
                # 检查是否需要停止
                if self._should_stop(task_id):
                    print(f"🛑 收到停止信号，正在终止同步任务: {task_id}")
                    executor.shutdown(wait=False, cancel_futures=True)
                    self._update_task(
                        task_id,
                        status='failed',
                        error_message='用户手动停止',
                        end_time=time.time()
                    )
                    print(f"⛔ 同步任务已停止: {task_id} (已处理: {processed_count}/{len(customer_list)})")
                    return
                
                try:
                    result_type, customer_id = future.result()
                    
                    if result_type == 'added':
                        added_count += 1
                    elif result_type == 'updated':
                        updated_count += 1
                    elif result_type == 'failed':
                        failed_count += 1
                    
                    # 更新任务进度
                    processed_count = added_count + updated_count + failed_count
                    self._update_task(
                        task_id,
                        processed_count=processed_count,
                        added_count=added_count,
                        updated_count=updated_count,
                        failed_count=failed_count
                    )
                    
                    # 每处理5个客户打印一次进度（更频繁的日志）
                    if processed_count % 5 == 0 or processed_count == 1:
                        task_status = self.get_task_status(task_id)
                        # 计算当前速度（每秒处理的客户数）
                        elapsed_time = time.time() - task_status['start_time']
                        speed = processed_count / elapsed_time if elapsed_time > 0 else 0
                        print(f"⚡ [{processed_count:>5}/{len(customer_list)}] {task_status['progress']:>3.0f}% | "
                              f"新增:{added_count:>3} 更新:{updated_count:>3} 失败:{failed_count:>3} | "
                              f"速度: {speed:.1f}个/秒 | 10线程并发")
                    
                except Exception as e:
                    print(f"❌ 处理结果异常: {e}")
                    failed_count += 1
        
        # 任务完成
        end_time = time.time()
        elapsed_time = end_time - self.get_task_status(task_id)['start_time']
        
        self._update_task(
            task_id,
            status='completed',
            end_time=end_time
        )
        
        print(f"\n{'='*80}")
        print(f"✅ 同步任务完成: {task_id}")
        print(f"📊 统计信息:")
        print(f"   - 总客户数: {len(customer_list)}")
        print(f"   - 新增: {added_count}")
        print(f"   - 更新: {updated_count}")
        print(f"   - 失败: {failed_count}")
        print(f"   - 耗时: {elapsed_time:.1f} 秒")
        print(f"   - 平均速度: {len(customer_list)/elapsed_time:.1f} 个/秒")
        print(f"   - 并发线程: {self.max_workers}")
        print(f"{'='*80}\n")
    
    def _save_customer(self, customer: Dict) -> tuple:
        """
        保存客户到数据库
        :return: ('added'/'updated'/'failed', customer_id)
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            external_userid = customer.get('external_userid')
            if not external_userid:
                conn.close()
                return 'failed', None
            
            # 检查是否已存在
            cursor.execute("SELECT id FROM customers WHERE id = ?", (external_userid,))
            exists = cursor.fetchone()
            
            # 准备数据
            tags_json = json.dumps([tag.get('tag_name', '') for tag in customer.get('tags', [])], ensure_ascii=False)
            
            # 标签分类
            enterprise_tags = []
            personal_tags = []
            rule_tags = []
            
            for tag in customer.get('tags', []):
                tag_type = tag.get('type', 1)
                tag_data = {
                    'tag_id': tag.get('tag_id', ''),
                    'tag_name': tag.get('tag_name', ''),
                    'group_name': tag.get('group_name', '')
                }
                if tag_type == 1:
                    enterprise_tags.append(tag_data)
                elif tag_type == 2:
                    personal_tags.append(tag_data)
                elif tag_type == 3:
                    rule_tags.append(tag_data)
            
            enterprise_tags_json = json.dumps(enterprise_tags, ensure_ascii=False)
            personal_tags_json = json.dumps(personal_tags, ensure_ascii=False)
            rule_tags_json = json.dumps(rule_tags, ensure_ascii=False)
            
            current_time = int(time.time())
            
            if exists:
                # 更新
                cursor.execute("""
                    UPDATE customers SET
                        name = ?, avatar = ?, gender = ?, type = ?,
                        corp_name = ?, position = ?,
                        owner_userid = ?, owner_name = ?,
                        add_time = ?, tags = ?, remark = ?,
                        description = ?, add_way = ?, im_status = ?, state = ?,
                        remark_mobiles = ?, remark_corp_name = ?,
                        enterprise_tags = ?, personal_tags = ?, rule_tags = ?,
                        unionid = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (
                    customer.get('name', ''),
                    customer.get('avatar', ''),
                    customer.get('gender', 0),
                    customer.get('type', 1),
                    customer.get('corp_name', ''),
                    customer.get('position', ''),
                    customer.get('owner_userid', ''),
                    customer.get('owner_name', ''),
                    customer.get('add_time', 0),
                    tags_json,
                    customer.get('remark', ''),
                    customer.get('description', ''),
                    customer.get('add_way', 0),
                    customer.get('im_status', ''),
                    customer.get('state', ''),
                    json.dumps(customer.get('remark_mobiles', []), ensure_ascii=False),
                    customer.get('remark_corp_name', ''),
                    enterprise_tags_json,
                    personal_tags_json,
                    rule_tags_json,
                    customer.get('unionid', ''),
                    current_time,
                    external_userid  # WHERE id = ?
                ))
                conn.commit()
                conn.close()
                return 'updated', external_userid
            else:
                # 新增
                cursor.execute("""
                    INSERT INTO customers (
                        id, name, avatar, gender, type, unionid,
                        position, corp_name, owner_userid, owner_name,
                        add_time, tags, remark, description, add_way,
                        im_status, state, remark_mobiles, remark_corp_name,
                        enterprise_tags, personal_tags, rule_tags,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    external_userid,
                    customer.get('name', ''),
                    customer.get('avatar', ''),
                    customer.get('gender', 0),
                    customer.get('type', 1),
                    customer.get('unionid', ''),
                    customer.get('position', ''),
                    customer.get('corp_name', ''),
                    customer.get('owner_userid', ''),
                    customer.get('owner_name', ''),
                    customer.get('add_time', 0),
                    tags_json,
                    customer.get('remark', ''),
                    customer.get('description', ''),
                    customer.get('add_way', 0),
                    customer.get('im_status', ''),
                    customer.get('state', ''),
                    json.dumps(customer.get('remark_mobiles', []), ensure_ascii=False),
                    customer.get('remark_corp_name', ''),
                    enterprise_tags_json,
                    personal_tags_json,
                    rule_tags_json,
                    current_time,
                    current_time
                ))
                conn.commit()
                conn.close()
                return 'added', external_userid
                
        except Exception as e:
            print(f"❌ 保存客户失败: {e}")
            try:
                conn.close()
            except:
                pass
            return 'failed', None

    # ==================== 客户群同步方法 ====================
    
    def sync_customer_groups_async(self) -> str:
        """异步同步客户群"""
        task_id = f"sync_groups_{int(time.time() * 1000)}"
        
        # 创建任务记录
        task = SyncTask(
            task_id=task_id,
            task_type='customer_groups',
            status='pending',
            progress=0,
            total_count=0,
            processed_count=0,
            added_count=0,
            updated_count=0,
            failed_count=0,
            start_time=time.time(),
            end_time=None,
            error_message=None
        )
        
        with self.lock:
            self.active_tasks[task_id] = task
            self.stop_flags[task_id] = False
        
        # 启动同步线程
        thread = threading.Thread(target=self._sync_customer_groups, args=(task_id,), daemon=True)
        thread.start()
        
        print(f"📋 客户群同步任务已创建: {task_id}")
        return task_id
    
    def _sync_customer_groups(self, task_id: str):
        """同步客户群（内部方法）"""
        try:
            self._update_task(task_id, status='running', progress=5)
            
            print(f"[步骤1] 获取客户群ID列表...")
            # 获取所有客户群ID
            chat_ids = self.wecom_client.get_group_chat_list()
            
            if not chat_ids:
                self._update_task(
                    task_id,
                    status='completed',
                    progress=100,
                    total_count=0,
                    end_time=time.time(),
                    error_message='未获取到客户群数据'
                )
                return
            
            total = len(chat_ids)
            self._update_task(task_id, total_count=total, progress=10)
            print(f"[步骤2] 共获取到 {total} 个客户群，开始并发获取详情...")
            
            processed_count = 0
            added_count = 0
            updated_count = 0
            failed_count = 0
            
            def fetch_and_save_group(chat_id):
                """获取并保存单个客户群"""
                nonlocal processed_count, added_count, updated_count, failed_count
                
                try:
                    # 获取群详情
                    group = self.wecom_client.get_group_chat_detail(chat_id, need_name=False)
                    if not group:
                        with self.lock:
                            processed_count += 1
                            failed_count += 1
                        return 'failed', None
                    
                    # 保存到数据库
                    status, _ = self._save_customer_group(group)
                    
                    # 更新计数器（在锁内）
                    with self.lock:
                        processed_count += 1
                        if status == 'added':
                            added_count += 1
                        elif status == 'updated':
                            updated_count += 1
                        elif status == 'failed':
                            failed_count += 1
                    
                    # 更新任务进度（在锁外！避免死锁）
                    progress = int(10 + (processed_count / total) * 85)
                    self._update_task(
                        task_id,
                        processed_count=processed_count,
                        added_count=added_count,
                        updated_count=updated_count,
                        failed_count=failed_count,
                        progress=progress
                    )
                    
                    # 每 10 个打印一次进度
                    if processed_count % 10 == 0:
                        print(f"[进度] {processed_count}/{total} ({progress}%) - 新增:{added_count}, 更新:{updated_count}, 失败:{failed_count}")
                    
                    return status, chat_id
                    
                except Exception as e:
                    print(f"❌ 处理客户群异常: {e}")
                    import traceback
                    traceback.print_exc()
                    with self.lock:
                        processed_count += 1
                        failed_count += 1
                    return 'failed', None
            
            # 使用线程池并发处理（10个并发）
            print(f"[同步策略] 使用10个线程并发处理")
            
            from concurrent.futures import ThreadPoolExecutor, as_completed
            import time
            
            # 使用线程池，10个并发
            with ThreadPoolExecutor(max_workers=10) as executor:
                # 提交所有任务
                future_to_chat = {executor.submit(fetch_and_save_group, chat_id): chat_id for chat_id in chat_ids}
                
                # 处理完成的任务
                for future in as_completed(future_to_chat):
                    chat_id = future_to_chat[future]
                    
                    # 检查是否需要停止
                    if self._should_stop(task_id):
                        print(f"🛑 收到停止信号，正在终止同步任务: {task_id}")
                        # 取消所有未完成的任务
                        executor.shutdown(wait=False, cancel_futures=True)
                        self._update_task(
                            task_id,
                            status='cancelled',
                            error_message='用户手动停止',
                            end_time=time.time()
                        )
                        print(f"⛔ 同步任务已停止: {task_id} (已处理: {processed_count}/{total})")
                        return
                    
                    try:
                        result = future.result(timeout=30)
                    except Exception as e:
                        print(f"❌ 处理群 {chat_id} 异常: {e}")
                        with self.lock:
                            processed_count += 1
                            failed_count += 1
                
                print(f"[线程池] 所有任务已提交完成")
            
            # 完成
            self._update_task(
                task_id,
                status='completed',
                progress=100,
                end_time=time.time()
            )
            
            print(f"✅ 客户群同步完成: 共{total}个, 新增{added_count}, 更新{updated_count}, 失败{failed_count}")
            
        except Exception as e:
            print(f"❌ 客户群同步失败: {e}")
            import traceback
            traceback.print_exc()
            self._update_task(
                task_id,
                status='failed',
                error_message=str(e),
                end_time=time.time()
            )
    
    def _save_customer_group(self, group: Dict) -> tuple:
        """
        保存客户群到数据库
        :return: ('added'/'updated'/'failed', chat_id)
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            chat_id = group.get('chat_id')
            if not chat_id:
                conn.close()
                return 'failed', None
            
            # 检查是否已存在
            cursor.execute("SELECT chat_id FROM customer_groups WHERE chat_id = ?", (chat_id,))
            exists = cursor.fetchone()
            
            current_time = int(time.time())
            
            # 处理admin_list - 可能是字符串列表或字典列表
            admin_list = group.get('admin_list', [])
            if admin_list:
                if isinstance(admin_list[0], dict):
                    # 如果是字典列表，提取userid
                    admin_list_str = ','.join([str(admin.get('userid', '')) for admin in admin_list if admin.get('userid')])
                else:
                    # 如果是字符串列表
                    admin_list_str = ','.join([str(admin) for admin in admin_list])
            else:
                admin_list_str = ''
            
            if exists:
                # 更新
                cursor.execute("""
                    UPDATE customer_groups SET
                        name = ?, owner_userid = ?, owner_name = ?, notice = ?,
                        member_count = ?, external_member_count = ?, internal_member_count = ?,
                        admin_list = ?, group_type = ?, status = ?, version = ?,
                        last_sync_time = ?, updated_at = ?
                    WHERE chat_id = ?
                """, (
                    group.get('name', ''),
                    group.get('owner', ''),
                    group.get('owner_name', ''),
                    group.get('notice', ''),
                    group.get('member_count', 0),
                    group.get('external_member_count', 0),
                    group.get('internal_member_count', 0),
                    admin_list_str,
                    group.get('group_type', 'external'),
                    group.get('status', 0),
                    group.get('version', 0),
                    current_time,
                    current_time,
                    chat_id
                ))
                conn.commit()
                conn.close()
                return 'updated', chat_id
            else:
                # 新增
                cursor.execute("""
                    INSERT INTO customer_groups 
                    (chat_id, name, owner_userid, owner_name, notice, member_count,
                     external_member_count, internal_member_count, admin_list, group_type,
                     status, version, create_time, last_sync_time, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chat_id,
                    group.get('name', ''),
                    group.get('owner', ''),
                    group.get('owner_name', ''),
                    group.get('notice', ''),
                    group.get('member_count', 0),
                    group.get('external_member_count', 0),
                    group.get('internal_member_count', 0),
                    admin_list_str,
                    group.get('group_type', 'external'),
                    group.get('status', 0),
                    group.get('version', 0),
                    group.get('create_time', current_time),
                    current_time,
                    current_time,
                    current_time
                ))
                conn.commit()
                conn.close()
                return 'added', chat_id
                
        except Exception as e:
            print(f"❌ 保存客户群失败: {e}")
            try:
                conn.close()
            except:
                pass
            return 'failed', None
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        with self.lock:
            if task_id in self.stop_flags:
                self.stop_flags[task_id] = True
                print(f"🛑 任务取消请求已发送: {task_id}")
                return True
            return False

