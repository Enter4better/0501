import os
import time
import threading
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from queue import Queue, Empty
import json
import sys
from pathlib import Path

# 添加backend目录到路�?
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config import WATCHDOG_CONFIG

# 尝试导入watchdog�?
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = object
    logging.warning("watchdog库未安装，日志监控功能将被禁�?)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogEventHandler(FileSystemEventHandler):
    """日志文件事件处理�?""
    
    def __init__(self, callback: Callable):
        self.callback = callback
        self.file_positions: Dict[str, int] = {}
    
    def on_modified(self, event):
        """文件修改事件"""
        if not event.is_directory:
            file_path = event.src_path
            if file_path.endswith(('.log', '.txt')):
                self._process_log_file(file_path)
    
    def _process_log_file(self, file_path: str):
        """处理日志文件"""
        try:
            # 获取文件当前位置
            current_position = self.file_positions.get(file_path, 0)
            
            # 读取新增内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(current_position)
                new_content = f.read()
                current_position = f.tell()
            
            # 更新文件位置
            self.file_positions[file_path] = current_position
            
            # 如果有新增内容，处理日志
            if new_content.strip():
                self.callback(file_path, new_content)
                
        except Exception as e:
            logger.error(f"处理日志文件失败: {file_path} - {e}")


class WatchdogService:
    """日志监控服务"""
    
    def __init__(self):
        self.observer = Observer() if WATCHDOG_AVAILABLE else None
        self.event_handler = None
        self.running = False
        self.log_queue = Queue()
        self.processed_files: Dict[str, int] = {}
        self.callbacks: List[Callable] = []
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'total_logs': 0,
            'errors': 0
        }
    
    def start(self):
        """启动监控服务"""
        if self.running:
            return
        
        if not WATCHDOG_AVAILABLE:
            logger.warning("watchdog库未安装，日志监控功能被禁用")
            self.running = True
            return
        
        self.running = True
        
        # 创建事件处理�?
        self.event_handler = LogEventHandler(self._on_log_event)
        
        # 添加监控路径
        for watch_path in WATCHDOG_CONFIG['watch_paths']:
            if os.path.exists(watch_path):
                self.observer.schedule(
                    self.event_handler,
                    watch_path,
                    recursive=WATCHDOG_CONFIG['recursive']
                )
                logger.info(f"添加监控路径: {watch_path}")
            else:
                logger.warning(f"监控路径不存�? {watch_path}")
        
        # 启动观察�?
        self.observer.start()
        logger.info("日志监控服务已启�?)
        
        # 启动日志处理线程
        self._start_log_processor()
    
    def stop(self):
        """停止监控服务"""
        if not self.running:
            return
        
        self.running = False
        
        # 停止观察�?
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
        
        logger.info("日志监控服务已停�?)
    
    def add_callback(self, callback: Callable):
        """添加回调函数"""
        self.callbacks.append(callback)
    
    def _on_log_event(self, file_path: str, content: str):
        """处理日志事件"""
        try:
            # 将日志放入队�?
            log_entry = {
                'file_path': file_path,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'file_size': os.path.getsize(file_path)
            }
            
            self.log_queue.put(log_entry)
            self.stats['total_logs'] += 1
            
        except Exception as e:
            logger.error(f"处理日志事件失败: {e}")
            self.stats['errors'] += 1
    
    def _start_log_processor(self):
        """启动日志处理线程"""
        def process_logs():
            while self.running:
                try:
                    # 从队列获取日�?
                    log_entry = self.log_queue.get(timeout=1)
                    
                    # 处理日志内容
                    self._process_log_content(log_entry)
                    
                    # 标记任务完成
                    self.log_queue.task_done()
                    
                except Empty:
                    continue
                except Exception as e:
                    logger.error(f"处理日志失败: {e}")
                    self.stats['errors'] += 1
        
        # 启动处理线程
        processor_thread = threading.Thread(target=process_logs, daemon=True)
        processor_thread.start()
    
    def _process_log_content(self, log_entry: Dict[str, Any]):
        """处理日志内容"""
        try:
            file_path = log_entry['file_path']
            content = log_entry['content']
            timestamp = log_entry['timestamp']
            
            # 解析日志内容
            log_lines = content.strip().split('\n')
            
            for line in log_lines:
                if line.strip():
                    # 根据文件路径判断日志类型
                    log_type = self._detect_log_type(file_path)
                    level = self._detect_log_level(line)
                    source = self._detect_log_source(file_path)
                    
                    # 调用回调函数
                    for callback in self.callbacks:
                        try:
                            callback({
                                'file_path': file_path,
                                'content': line.strip(),
                                'level': level,
                                'source': source,
                                'timestamp': timestamp
                            })
                        except Exception as e:
                            logger.error(f"回调函数执行失败: {e}")
            
            # 更新统计信息
            if file_path not in self.processed_files:
                self.processed_files[file_path] = 0
                self.stats['total_files'] += 1
            
            self.processed_files[file_path] += 1
            self.stats['processed_files'] = len(self.processed_files)
            
        except Exception as e:
            logger.error(f"处理日志内容失败: {e}")
            self.stats['errors'] += 1
    
    def _detect_log_type(self, file_path: str) -> str:
        """检测日志类�?""
        if 'docker' in file_path.lower():
            return 'docker'
        elif 'attack' in file_path.lower():
            return 'attack'
        elif 'defense' in file_path.lower():
            return 'defense'
        elif 'system' in file_path.lower():
            return 'system'
        else:
            return 'unknown'
    
    def _detect_log_level(self, line: str) -> str:
        """检测日志级�?""
        line_lower = line.lower()
        
        if any(keyword in line_lower for keyword in ['error', 'err', 'failed', 'fail']):
            return 'danger'
        elif any(keyword in line_lower for keyword in ['warning', 'warn']):
            return 'warning'
        elif any(keyword in line_lower for keyword in ['success', 'ok', 'complete']):
            return 'success'
        else:
            return 'info'
    
    def _detect_log_source(self, file_path: str) -> str:
        """检测日志来�?""
        if 'docker' in file_path.lower():
            return 'docker'
        elif 'attack' in file_path.lower():
            return 'attack'
        elif 'defense' in file_path.lower():
            return 'defense'
        elif 'system' in file_path.lower():
            return 'system'
        else:
            return 'unknown'
    
    def _get_target_id_from_path(self, file_path: str) -> Optional[int]:
        """从文件路径获取靶场ID"""
        try:
            # 从文件路径中提取靶场名称
            filename = os.path.basename(file_path)
            if '_' in filename:
                target_name = filename.split('_')[0]
                # 这里可以根据靶场名称查询靶场ID
                # 简化处理，返回None
                return None
        except Exception:
            pass
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """获取监控统计"""
        return {
            'running': self.running,
            'watched_paths': WATCHDOG_CONFIG['watch_paths'],
            'stats': self.stats.copy(),
            'processed_files': len(self.processed_files),
            'queue_size': self.log_queue.qsize()
        }
    
    def get_processed_files(self) -> List[str]:
        """获取已处理的文件列表"""
        return list(self.processed_files.keys())
    
    def clear_stats(self):
        """清空统计信息"""
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'total_logs': 0,
            'errors': 0
        }
        self.processed_files.clear()
        logger.info("监控统计信息已清�?)
    
    def add_watch_path(self, path: str):
        """添加监控路径"""
        if os.path.exists(path) and path not in WATCHDOG_CONFIG['watch_paths']:
            WATCHDOG_CONFIG['watch_paths'].append(path)
            
            if self.running:
                self.observer.schedule(
                    self.event_handler,
                    path,
                    recursive=WATCHDOG_CONFIG['recursive']
                )
            
            logger.info(f"添加监控路径: {path}")
    
    def remove_watch_path(self, path: str):
        """移除监控路径"""
        if path in WATCHDOG_CONFIG['watch_paths']:
            WATCHDOG_CONFIG['watch_paths'].remove(path)
            logger.info(f"移除监控路径: {path}")


# 全局监控服务实例
watchdog_service = WatchdogService()
