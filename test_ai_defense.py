#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试网络安全靶场系统功能
"""
import requests
import json
import time


def test_basic_functionality():
    """测试基本功能"""
    print("=" * 60)
    print("测试网络安全靶场系统")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    try:
        # 测试健康检查
        print("\n1. 测试系统健康检查:")
        health_response = requests.get(f"{base_url}/api/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   系统状态: {health_data.get('status', 'unknown')}")
            print(f"   数据库状态: {health_data.get('database', 'unknown')}")
        else:
            print(f"   健康检查失败: {health_response.status_code}")
        
        # 测试登录
        print("\n2. 测试用户登录:")
        login_response = requests.post(f"{base_url}/api/login", 
                                     json={"username": "admin", "password": "admin123"})
        if login_response.status_code == 200:
            token = login_response.json().get('token')
            headers = {"Authorization": f"Bearer {token}"}
            print(f"   登录成功，获取令牌: {token[:20]}...")
        else:
            print(f"   登录失败: {login_response.status_code}")
            return
        
        # 测试获取目标
        print("\n3. 测试获取目标:")
        targets_response = requests.get(f"{base_url}/api/targets", headers=headers)
        print(f"   获取目标状态: {targets_response.status_code}")
        if targets_response.status_code == 200:
            targets = targets_response.json().get('targets', [])
            print(f"   目标数量: {len(targets)}")
        
        # 测试获取攻击类型
        print("\n4. 测试获取攻击类型:")
        attacks_response = requests.get(f"{base_url}/api/attack/types", headers=headers)
        print(f"   获取攻击类型状态: {attacks_response.status_code}")
        if attacks_response.status_code == 200:
            attack_types = attacks_response.json().get('types', [])
            print(f"   攻击类型数量: {len(attack_types)}")
        
        # 测试获取防御机制
        print("\n5. 测试获取防御机制:")
        defenses_response = requests.get(f"{base_url}/api/defense/list", headers=headers)
        print(f"   获取防御机制状态: {defenses_response.status_code}")
        if defenses_response.status_code == 200:
            defenses = defenses_response.json().get('defenses', [])
            print(f"   防御机制数量: {len(defenses)}")
        
        # 测试获取统计数据
        print("\n6. 测试获取统计数据:")
        stats_response = requests.get(f"{base_url}/api/stats/attacks", headers=headers)
        print(f"   获取统计数据状态: {stats_response.status_code}")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"   攻击统计: {stats}")
        
        # 测试获取日志
        print("\n7. 测试获取日志:")
        logs_response = requests.get(f"{base_url}/api/logs/activity", headers=headers)
        print(f"   获取日志状态: {logs_response.status_code}")
        if logs_response.status_code == 200:
            logs = logs_response.json().get('logs', [])
            print(f"   日志数量: {len(logs)}")
        
        # 测试网络拓扑
        print("\n8. 测试获取网络拓扑:")
        topology_response = requests.get(f"{base_url}/api/topology/current", headers=headers)
        print(f"   获取拓扑状态: {topology_response.status_code}")
        if topology_response.status_code == 200:
            topology = topology_response.json()
            print(f"   拓扑节点数: {len(topology.get('topology', {}).get('nodes', []))}")
    
    except requests.exceptions.ConnectionError:
        print("   无法连接到API服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"   API测试出错: {e}")


def test_api_endpoints():
    """测试API端点"""
    print("\n" + "=" * 60)
    print("测试API端点")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    try:
        # 测试登录
        print("\n1. 测试用户登录:")
        login_response = requests.post(f"{base_url}/api/auth/login", 
                                     json={"username": "admin", "password": "admin123"})
        if login_response.status_code == 200:
            token = login_response.json().get('token')
            headers = {"Authorization": f"Bearer {token}"}
            print(f"   登录成功，获取令牌: {token[:20]}...")
        else:
            print(f"   登录失败: {login_response.status_code}")
            return
        
        # 测试获取目标
        print("\n2. 测试获取目标:")
        targets_response = requests.get(f"{base_url}/api/targets", headers=headers)
        print(f"   获取目标状态: {targets_response.status_code}")
        if targets_response.status_code == 200:
            targets = targets_response.json().get('targets', [])
            print(f"   目标数量: {len(targets)}")
        
        # 测试获取攻击类型
        print("\n3. 测试获取攻击类型:")
        attacks_response = requests.get(f"{base_url}/api/attacks/types", headers=headers)
        print(f"   获取攻击类型状态: {attacks_response.status_code}")
        if attacks_response.status_code == 200:
            attack_types = attacks_response.json().get('attack_types', [])
            print(f"   攻击类型数量: {len(attack_types)}")
        
        # 测试获取统计数据
        print("\n4. 测试获取统计数据:")
        stats_response = requests.get(f"{base_url}/api/stats/overview", headers=headers)
        print(f"   获取统计数据状态: {stats_response.status_code}")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"   统计数据: {stats}")
        
        # 测试获取日志
        print("\n5. 测试获取日志:")
        logs_response = requests.get(f"{base_url}/api/logs", headers=headers)
        print(f"   获取日志状态: {logs_response.status_code}")
        if logs_response.status_code == 200:
            logs = logs_response.json().get('logs', [])
            print(f"   日志数量: {len(logs)}")
        
    except requests.exceptions.ConnectionError:
        print("   无法连接到API服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"   API测试出错: {e}")


if __name__ == "__main__":
    print("开始测试网络安全靶场系统...")
    
    # 测试基本功能
    test_basic_functionality()
    
    # 等待一段时间让服务器完全就绪
    time.sleep(2)
    
    # 测试API端点
    test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("系统特性总结:")
    print("- 标准化的安全攻击/防御类型")
    print("- 真实数据驱动的系统")
    print("- 完整的攻击/防御模拟流程")
    print("- 详细的日志记录与分析")
    print("- 可视化的网络拓扑展示")
    print("- 实时统计数据监控")
    print("=" * 60)
