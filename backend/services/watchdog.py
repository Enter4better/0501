# -*- coding: utf-8 -*-
"""
监控服务 - 系统监控和告警
"""
import threading
import time
from datetime import datetime
from typing import Optional, List, Dict, Any, Callable
import logging
import sys
from pathlib import Path

# 添加backend目录到路径
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config import DB_CONFIG

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WatchdogService:
    """监控服务"""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.running = False
        self.thread = None
        self.monitors = {}
        self.alerts = []
        self.max_alerts = 100
    
    def start(self):
        """启动监控服务"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info("监控服务启动")
    
    def stop(self):
        """停止监控服务"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("监控服务停止")
    
    def register_monitor(self, name: str, check_func: Callable, interval: int = None,
                         alert_threshold: float = None, alert_message: str = None):
        """注册监控器"""
        self.monitors[name] = {
            'name': name,
            'check_func': check_func,
            'interval': interval or self.check_interval,
            'alert_threshold': alert_threshold,
            'alert_message': alert_message,
            'last_check': None,
            'last_value': None,
            'status': 'unknown'
        }
        logger.info(f"监控器注册成功: {name}")
    
    def unregister_monitor(self, name: str):
        """注销监控器"""
        if name in self.monitors:
            del self.monitors[name]
            logger.info(f"监控器注销成功: {name}")
    
    def get_monitor_status(self, name: str) -> Optional[Dict[str, Any]]:
        """获取监控器状态"""
        if name in self.monitors:
            monitor = self.monitors[name]
            return {
                'name': monitor['name'],
                'status': monitor['status'],
                'last_check': monitor['last_check'].isoformat() if monitor['last_check'] else None,
                'last_value': monitor['last_value'],
                'alert_threshold': monitor['alert_threshold']
            }
        return None
    
    def get_all_monitors(self) -> List[Dict[str, Any]]:
        """获取所有监控器状态"""
        return [self.get_monitor_status(name) for name in self.monitors]
    
    def get_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取告警列表"""
        return self.alerts[-limit:]
    
    def clear_alerts(self):
        """清理告警"""
        self.alerts.clear()
        logger.info("告警已清理")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            for name, monitor in self.monitors.items():
                try:
                    # 执行检查
                    value = monitor['check_func']()
                    monitor['last_value'] = value
                    monitor['last_check'] = datetime.now()
                    
                    # 检查阈值
                    if monitor['alert_threshold'] is not None:
                        if value > monitor['alert_threshold']:
                            monitor['status'] = 'warning'
                            self._add_alert(name, value, monitor['alert_message'])
                        else:
                            monitor['status'] = 'normal'
                    else:
                        monitor['status'] = 'normal'
                        
                except Exception as e:
                    monitor['status'] = 'error'
                    logger.error(f"监控器检查失败: {name} - {e}")
            
            # 休眠
            time.sleep(self.check_interval)
    
    def _add_alert(self, monitor_name: str, value: float, message: str = None):
        """添加告警"""
        alert = {
            'monitor_name': monitor_name,
            'value': value,
            'message': message or f"{monitor_name} 告警: {value}",
            'timestamp': datetime.now().isoformat()
        }
        self.alerts.append(alert)
        
        # 限制告警数量
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]
        
        logger.warning(f"告警: {alert['message']}")


class SystemMonitor:
    """系统监控"""
    
    @staticmethod
    def check_cpu_usage() -> float:
        """检查CPU使用率"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except ImportError:
            # 如果没有psutil，返回模拟值
            return 25.0
    
    @staticmethod
    def check_memory_usage() -> float:
        """检查内存使用率"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except ImportError:
            return 50.0
    
    @staticmethod
    def check_disk_usage() -> float:
        """检查磁盘使用率"""
        try:
            import psutil
            return psutil.disk_usage('/').percent
        except ImportError:
            return 40.0
    
    @staticmethod
    def check_network_connections() -> int:
        """检查网络连接数"""
        try:
            import psutil
            return len(psutil.net_connections())
        except ImportError:
            return 10
    
    @staticmethod
    def check_docker_containers() -> int:
        """检查Docker容器数"""
        try:
            import docker
            client = docker.from_env()
            return len(client.containers.list())
        except Exception:
            return 0


# 全局监控服务实例
watchdog_service = WatchdogService()


def init_watchdog():
    """初始化监控服务"""
    # 注册系统监控器
    watchdog_service.register_monitor(
        name='cpu_usage',
        check_func=SystemMonitor.check_cpu_usage,
        interval=30,
        alert_threshold=80.0,
        alert_message='CPU使用率过高'
    )
    
    watchdog_service.register_monitor(
        name='memory_usage',
        check_func=SystemMonitor.check_memory_usage,
        interval=30,
        alert_threshold=85.0,
        alert_message='内存使用率过高'
    )
    
    watchdog_service.register_monitor(
        name='disk_usage',
        check_func=SystemMonitor.check_disk_usage,
        interval=60,
        alert_threshold=90.0,
        alert_message='磁盘使用率过高'
    )
    
    watchdog_service.register_monitor(
        name='docker_containers',
        check_func=SystemMonitor.check_docker_containers,
        interval=30,
        alert_threshold=None
    )
    
    # 启动监控服务
    watchdog_service.start()
    logger.info("系统监控初始化完成")