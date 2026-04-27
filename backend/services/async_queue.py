import asyncio
import threading
import time
import logging
from typing import Any, Callable, Dict, List, Optional
from queue import Queue, Empty
from datetime import datetime
import json
import sys
from pathlib import Path

# 添加backend目录到路�?
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config import ASYNC_CONFIG

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AsyncTask:
    """异步任务�?""
    
    def __init__(self, task_id: str, task_type: str, func: Callable, args: tuple = (), 
                 kwargs: dict = None, priority: int = 0, timeout: int = None):
        self.task_id = task_id
        self.task_type = task_type
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.priority = priority
        self.timeout = timeout
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
        self.status = 'pending'  # pending, running, completed, failed
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字�?""
        return {
            'task_id': self.task_id,
            'task_type': self.task_type,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result': str(self.result) if self.result else None,
            'error': str(self.error) if self.error else None
        }


class AsyncQueue:
    """异步队列管理�?""
    
    def __init__(self, max_size: int = None, worker_count: int = None, timeout: int = None):
        self.max_size = max_size or ASYNC_CONFIG['max_queue_size']
        self.worker_count = worker_count or ASYNC_CONFIG['worker_count']
        self.timeout = timeout or ASYNC_CONFIG['timeout']
        
        # 任务队列
        self.task_queue = Queue(maxsize=self.max_size)
        
        # 结果存储
        self.results: Dict[str, Any] = {}
        self.errors: Dict[str, Exception] = {}
        
        # 工作线程
        self.workers: List[threading.Thread] = []
        self.running = False
        
        # 统计信息
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'pending_tasks': 0
        }
        
        # 任务历史
        self.task_history: List[Dict[str, Any]] = []
        
        # 回调函数
        self.task_callbacks: Dict[str, Callable] = {}
        self.type_callbacks: Dict[str, Callable] = {}
    
    def start(self):
        """启动异步队列"""
        if self.running:
            return
        
        self.running = True
        
        # 启动工作线程
        for i in range(self.worker_count):
            worker = threading.Thread(target=self._worker, name=f"AsyncWorker-{i}")
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"异步队列已启动，工作线程�? {self.worker_count}")
    
    def stop(self):
        """停止异步队列"""
        self.running = False
        
        # 等待所有工作线程结�?
        for worker in self.workers:
            worker.join(timeout=5)
        
        self.workers.clear()
        logger.info("异步队列已停�?)
    
    def add_task(self, task_id: str, task_type: str, func: Callable, args: tuple = (), 
                 kwargs: dict = None, priority: int = 0, timeout: int = None) -> bool:
        """添加任务到队�?""
        try:
            task = AsyncTask(
                task_id=task_id,
                task_type=task_type,
                func=func,
                args=args,
                kwargs=kwargs or {},
                priority=priority,
                timeout=timeout or self.timeout
            )
            
            # 根据优先级插入队�?
            if priority > 0 and self.task_queue.qsize() > 0:
                # 优先级队列，这里简化处理，实际应该使用优先级队�?
                pass
            
            self.task_queue.put(task)
            self.stats['total_tasks'] += 1
            self.stats['pending_tasks'] += 1
            
            # 记录任务历史
            self.task_history.append({
                'task_id': task_id,
                'task_type': task_type,
                'status': 'pending',
                'created_at': task.created_at.isoformat()
            })
            
            logger.info(f"任务已添加到队列: {task_id} ({task_type})")
            return True
            
        except Exception as e:
            logger.error(f"添加任务失败: {e}")
            return False
    
    def get_task_result(self, task_id: str, timeout: float = None) -> Any:
        """获取任务结果"""
        start_time = time.time()
        
        while True:
            if task_id in self.results:
                return self.results[task_id]
            
            if task_id in self.errors:
                raise self.errors[task_id]
            
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"任务 {task_id} 执行超时")
            
            time.sleep(0.1)
    
    def wait_for_completion(self, task_ids: List[str], timeout: float = None) -> Dict[str, Any]:
        """等待多个任务完成"""
        results = {}
        
        for task_id in task_ids:
            try:
                results[task_id] = self.get_task_result(task_id, timeout)
            except Exception as e:
                results[task_id] = e
        
        return results
    
    def _worker(self):
        """工作线程函数"""
        while self.running:
            try:
                # 从队列获取任�?
                task = self.task_queue.get(timeout=1)
                
                # 更新任务状�?
                task.status = 'running'
                task.started_at = datetime.now()
                self.stats['pending_tasks'] -= 1
                
                logger.info(f"开始执行任�? {task.task_id} ({task.task_type})")
                
                try:
                    # 执行任务
                    result = task.func(*task.args, **task.kwargs)
                    
                    # 保存结果
                    task.result = result
                    task.status = 'completed'
                    task.completed_at = datetime.now()
                    
                    self.results[task.task_id] = result
                    self.stats['completed_tasks'] += 1
                    
                    logger.info(f"任务执行成功: {task.task_id}")
                    
                    # 调用任务回调
                    if task.task_id in self.task_callbacks:
                        self.task_callbacks[task.task_id](result)
                    
                    # 调用类型回调
                    if task.task_type in self.type_callbacks:
                        self.type_callbacks[task.task_type](task.task_id, result)
                    
                except Exception as e:
                    # 处理错误
                    task.error = e
                    task.status = 'failed'
                    task.completed_at = datetime.now()
                    
                    self.errors[task.task_id] = e
                    self.stats['failed_tasks'] += 1
                    
                    logger.error(f"任务执行失败: {task.task_id} - {e}")
                    
                    # 调用错误回调
                    if task.task_id in self.task_callbacks:
                        self.task_callbacks[task.task_id](e)
                
                # 更新任务历史
                for history_item in self.task_history:
                    if history_item['task_id'] == task.task_id:
                        history_item.update({
                            'status': task.status,
                            'completed_at': task.completed_at.isoformat() if task.completed_at else None
                        })
                        break
                
                # 标记任务完成
                self.task_queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                logger.error(f"工作线程错误: {e}")
    
    def register_task_callback(self, task_id: str, callback: Callable):
        """注册任务回调"""
        self.task_callbacks[task_id] = callback
    
    def register_type_callback(self, task_type: str, callback: Callable):
        """注册类型回调"""
        self.type_callbacks[task_type] = callback
    
    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状�?""
        return {
            'running': self.running,
            'queue_size': self.task_queue.qsize(),
            'worker_count': len(self.workers),
            'stats': self.stats.copy(),
            'pending_tasks': self.stats['pending_tasks'],
            'completed_tasks': self.stats['completed_tasks'],
            'failed_tasks': self.stats['failed_tasks']
        }
    
    def get_task_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取任务历史"""
        return self.task_history[-limit:]
    
    def clear_history(self):
        """清空任务历史"""
        self.task_history.clear()
        logger.info("任务历史已清�?)
    
    def execute_task(self, task_id: str, task_type: str, func: Callable, 
                    args: tuple = (), kwargs: dict = None) -> asyncio.Future:
        """异步执行任务"""
        loop = asyncio.get_event_loop()
        
        def run_task():
            return self.add_task(task_id, task_type, func, args, kwargs)
        
        return loop.run_in_executor(None, run_task)


# 全局异步队列实例
async_queue = AsyncQueue()
