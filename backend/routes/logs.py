from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import sys
from pathlib import Path

# 添加backend目录到路�?
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from models.log import Log
from services.database import db_service
from services.watchdog import watchdog_service

logs_bp = Blueprint('logs', __name__, url_prefix='/api/logs')

@logs_bp.route('/list', methods=['GET'])
@jwt_required()
def list_logs():
    """获取日志列表"""
    try:
        user_id = get_jwt_identity()
        
        # 获取查询参数
        level = request.args.get('level')
        source = request.args.get('source')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        # 获取日志列表
        logs = Log.list_all(limit=limit, offset=offset, level=level, source=source, user_id=user_id)
        
        return jsonify({
            'status': 'success',
            'logs': logs,
            'total': len(logs)
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取日志列表失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取日志列表失败'}), 500

@logs_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_log_stats():
    """获取日志统计信息"""
    try:
        user_id = get_jwt_identity()
        
        # 获取全局统计
        stats = Log.get_stats()
        
        # 获取用户统计
        user_logs = Log.list_all(limit=1000, user_id=user_id)
        user_stats = {
            'total': len(user_logs),
            'today': len([l for l in user_logs if datetime.fromisoformat(l['created_at']).date() == datetime.now().date()]),
            'level_counts': {},
            'source_counts': {}
        }
        
        # 统计用户日志的级别和来源
        for log in user_logs:
            level = log.get('level', 'info')
            source = log.get('source', 'unknown')
            
            user_stats['level_counts'][level] = user_stats['level_counts'].get(level, 0) + 1
            user_stats['source_counts'][source] = user_stats['source_counts'].get(source, 0) + 1
        
        return jsonify({
            'status': 'success',
            'stats': stats,
            'user_stats': user_stats
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取日志统计失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取日志统计失败'}), 500

@logs_bp.route('/attack', methods=['GET'])
@jwt_required()
def get_attack_logs():
    """获取攻击日志"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 50))
        
        logs = Log.get_attack_logs(limit)
        
        return jsonify({
            'status': 'success',
            'logs': logs,
            'total': len(logs)
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取攻击日志失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取攻击日志失败'}), 500

@logs_bp.route('/defense', methods=['GET'])
@jwt_required()
def get_defense_logs():
    """获取防御日志"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 50))
        
        logs = Log.get_defense_logs(limit)
        
        return jsonify({
            'status': 'success',
            'logs': logs,
            'total': len(logs)
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取防御日志失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取防御日志失败'}), 500

@logs_bp.route('/system', methods=['GET'])
@jwt_required()
def get_system_logs():
    """获取系统日志"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 50))
        
        logs = Log.get_system_logs(limit)
        
        return jsonify({
            'status': 'success',
            'logs': logs,
            'total': len(logs)
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取系统日志失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取系统日志失败'}), 500

@logs_bp.route('/docker', methods=['GET'])
@jwt_required()
def get_docker_logs():
    """获取Docker日志"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 50))
        
        logs = Log.get_docker_logs(limit)
        
        return jsonify({
            'status': 'success',
            'logs': logs,
            'total': len(logs)
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取Docker日志失败: {e}")
        return jsonify({'status': 'error', 'msg': '获取Docker日志失败'}), 500

@logs_bp.route('/search', methods=['GET'])
@jwt_required()
def search_logs():
    """搜索日志"""
    try:
        user_id = get_jwt_identity()
        
        # 获取查询参数
        keyword = request.args.get('keyword', '')
        level = request.args.get('level')
        source = request.args.get('source')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 100))
        
        # 构建查询条件
        conditions = []
        params = []
        
        if keyword:
            conditions.append("message LIKE %s")
            params.append(f"%{keyword}%")
        
        if level:
            conditions.append("level = %s")
            params.append(level)
        
        if source:
            conditions.append("source = %s")
            params.append(source)
        
        if start_date:
            conditions.append("created_at >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("created_at <= %s")
            params.append(end_date)
        
        # 构建SQL查询
        sql = "SELECT * FROM logs WHERE 1=1"
        if conditions:
            sql += " AND " + " AND ".join(conditions)
        sql += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        # 执行查询
        connection = db_service.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            columns = [desc[0] for desc in cursor.description]
            logs = [dict(zip(columns, row)) for row in results]
        
        return jsonify({
            'status': 'success',
            'logs': logs,
            'total': len(logs),
            'keyword': keyword
        }), 200
    except Exception as e:
        current_app.logger.error(f"搜索日志失败: {e}")
        return jsonify({'status': 'error', 'msg': '搜索日志失败'}), 500

@logs_bp.route('/export', methods=['GET'])
@jwt_required()
def export_logs():
    """导出日志"""
    try:
        user_id = get_jwt_identity()
        
        # 获取查询参数
        format_type = request.args.get('format', 'json')
        level = request.args.get('level')
        source = request.args.get('source')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询条件
        conditions = []
        params = []
        
        if level:
            conditions.append("level = %s")
            params.append(level)
        
        if source:
            conditions.append("source = %s")
            params.append(source)
        
        if start_date:
            conditions.append("created_at >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("created_at <= %s")
            params.append(end_date)
        
        # 构建SQL查询
        sql = "SELECT * FROM logs WHERE 1=1"
        if conditions:
            sql += " AND " + " AND ".join(conditions)
        sql += " ORDER BY created_at DESC"
        
        # 执行查询
        connection = db_service.get_connection()
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            columns = [desc[0] for desc in cursor.description]
            logs = [dict(zip(columns, row)) for row in results]
        
        # 根据格式导出
        if format_type == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=columns)
            writer.writeheader()
            writer.writerows(logs)
            
            return output.getvalue(), 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': 'attachment; filename=logs_export.csv'
            }
        else:
            return jsonify({
                'status': 'success',
                'logs': logs,
                'total': len(logs)
            }), 200
    except Exception as e:
        current_app.logger.error(f"导出日志失败: {e}")
        return jsonify({'status': 'error', 'msg': '导出日志失败'}), 500

@logs_bp.route('/clear', methods=['POST'])
@jwt_required()
def clear_logs():
    """清理日志"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # 获取清理条件
        older_than_days = data.get('older_than_days')
        
        # 执行清理
        count = Log.clear_logs(older_than_days)
        
        # 记录日志
        if older_than_days:
            message = f'清理�?{count} �?{older_than_days} 天前的日�?
        else:
            message = f'清理了所有日志，�?{count} �?
        
        current_app.logger.info(message)
        
        return jsonify({
            'status': 'success',
            'message': message,
            'cleared_count': count
        }), 200
    except Exception as e:
        current_app.logger.error(f"清理日志失败: {e}")
        return jsonify({'status': 'error', 'msg': '清理日志失败'}), 500

@logs_bp.route('/watchdog/status', methods=['GET'])
@jwt_required()
def get_watchdog_status():
    """获取监控服务状�?""
    try:
        status = watchdog_service.get_stats()
        return jsonify({
            'status': 'success',
            'watchdog': status
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取监控服务状态失�? {e}")
        return jsonify({'status': 'error', 'msg': '获取监控服务状态失�?}), 500

@logs_bp.route('/watchdog/start', methods=['POST'])
@jwt_required()
def start_watchdog():
    """启动监控服务"""
    try:
        watchdog_service.start()
        return jsonify({
            'status': 'success',
            'message': '监控服务已启�?
        }), 200
    except Exception as e:
        current_app.logger.error(f"启动监控服务失败: {e}")
        return jsonify({'status': 'error', 'msg': '启动监控服务失败'}), 500

@logs_bp.route('/watchdog/stop', methods=['POST'])
@jwt_required()
def stop_watchdog():
    """停止监控服务"""
    try:
        watchdog_service.stop()
        return jsonify({
            'status': 'success',
            'message': '监控服务已停�?
        }), 200
    except Exception as e:
        current_app.logger.error(f"停止监控服务失败: {e}")
        return jsonify({'status': 'error', 'msg': '停止监控服务失败'}), 500

@logs_bp.route('/watchdog/clear', methods=['POST'])
@jwt_required()
def clear_watchdog_stats():
    """清空监控统计"""
    try:
        watchdog_service.clear_stats()
        return jsonify({
            'status': 'success',
            'message': '监控统计已清�?
        }), 200
    except Exception as e:
        current_app.logger.error(f"清空监控统计失败: {e}")
        return jsonify({'status': 'error', 'msg': '清空监控统计失败'}), 500
