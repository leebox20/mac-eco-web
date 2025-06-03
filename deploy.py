#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速部署脚本
自动化部署前端到生产环境
"""

import os
import sys
import subprocess
import time

def run_command(command, description=""):
    """执行命令并显示结果"""
    print(f"🔄 {description}")
    print(f"执行命令: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True, encoding='utf-8')
        print(f"✅ {description} 成功")
        if result.stdout:
            print(f"输出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败")
        print(f"错误: {e.stderr}")
        return False

def check_prerequisites():
    """检查部署前提条件"""
    print("🔍 检查部署前提条件...")
    
    # 检查Node.js
    if not run_command("node --version", "检查Node.js"):
        print("❌ 请先安装Node.js")
        return False
    
    # 检查npm
    if not run_command("npm --version", "检查npm"):
        print("❌ 请先安装npm")
        return False
    
    # 检查是否在项目根目录
    if not os.path.exists("package.json"):
        print("❌ 请在项目根目录运行此脚本")
        return False
    
    print("✅ 前提条件检查通过")
    return True

def switch_to_production():
    """切换到生产环境配置"""
    print("🔄 切换到生产环境配置...")
    return run_command("python switch-env.py production", "切换环境配置")

def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖...")
    return run_command("npm install", "安装npm依赖")

def build_frontend():
    """构建前端"""
    print("🏗️ 构建前端...")
    return run_command("npm run build", "构建前端项目")

def deploy_with_docker():
    """使用Docker部署"""
    print("🐳 使用Docker部署...")
    
    # 检查Docker
    if not run_command("docker --version", "检查Docker"):
        print("❌ 请先安装Docker")
        return False
    
    if not run_command("docker-compose --version", "检查Docker Compose"):
        print("❌ 请先安装Docker Compose")
        return False
    
    # 停止现有容器
    run_command("docker-compose down", "停止现有容器")
    
    # 构建并启动
    if run_command("docker-compose up -d --build", "构建并启动容器"):
        print("✅ Docker部署成功")
        print("🌐 前端访问地址: http://120.48.150.254:3001")
        print("🔗 后端API地址: http://120.48.150.254:8888")
        return True
    
    return False

def check_deployment():
    """检查部署状态"""
    print("🔍 检查部署状态...")
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(10)
    
    # 检查容器状态
    run_command("docker-compose ps", "检查容器状态")
    
    print("📋 部署完成！请手动验证以下项目：")
    print("1. 访问前端: http://120.48.150.254:3001")
    print("2. 检查API: http://120.48.150.254:8888/docs")
    print("3. 测试各页面功能是否正常")

def main():
    """主函数"""
    print("🚀 开始自动化部署...")
    print("=" * 50)
    
    # 检查前提条件
    if not check_prerequisites():
        sys.exit(1)
    
    # 切换到生产环境
    if not switch_to_production():
        print("❌ 环境切换失败")
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败")
        sys.exit(1)
    
    # 构建前端
    if not build_frontend():
        print("❌ 前端构建失败")
        sys.exit(1)
    
    # Docker部署
    if not deploy_with_docker():
        print("❌ Docker部署失败")
        sys.exit(1)
    
    # 检查部署
    check_deployment()
    
    print("=" * 50)
    print("🎉 部署完成！")

if __name__ == "__main__":
    main()
