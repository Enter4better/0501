# -*- coding: utf-8 -*-
"""
路由包 - 注册所有蓝图
"""
from .auth import auth_bp
from .targets import targets_bp
from .attacks import attacks_bp
from .defenses import defenses_bp, defenses_alt_bp
from .logs import logs_bp
from .stats import stats_bp
from .topology import topology_bp
from .compat import compat_bp

# 注册所有蓝图（兼容路由放在前面，优先匹配）
all_blueprints = [
    compat_bp,
    auth_bp,
    targets_bp,
    attacks_bp,
    defenses_bp,
    defenses_alt_bp,
    logs_bp,
    stats_bp,
    topology_bp
]

__all__ = ['all_blueprints']
