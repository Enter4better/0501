from .auth import auth_bp
from .targets import targets_bp
from .attacks import attacks_bp
from .defenses import defenses_bp
from .logs import logs_bp
from .stats import stats_bp
from .ai import ai_bp
from .topology import topology_bp
from .agents import agents_bp

# 注册所有路�?
all_blueprints = [
    auth_bp,
    targets_bp,
    attacks_bp,
    defenses_bp,
    logs_bp,
    stats_bp,
    ai_bp,
    topology_bp,
    agents_bp  # AI Agent路由
]

__all__ = ['all_blueprints']
