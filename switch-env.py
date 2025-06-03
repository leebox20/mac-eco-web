#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境切换脚本：在本地测试环境和生产环境之间快速切换API配置
"""

import os
import re
import sys

def switch_to_local():
    """切换到本地测试环境"""
    print("🔄 切换到本地测试环境...")
    
    files_to_update = [
        {
            'file': 'src/config.js',
            'local': "export const API_BASE_URL = 'http://localhost:8888'",
            'prod': "// export const API_BASE_URL = 'http://120.48.150.254:8888'"
        },
        {
            'file': 'src/config/axios.js', 
            'local': "axios.defaults.baseURL = 'http://localhost:8888'",
            'prod': "// axios.defaults.baseURL = 'http://120.48.150.254:8888'"
        },
        {
            'file': 'vite.config.js',
            'local': "        target: 'http://localhost:8888',",
            'prod': "        // target: 'http://120.48.150.254:8888',"
        },
        {
            'file': 'src/views/Database.vue',
            'local': "const API_BASE_URL = 'http://localhost:8888'",
            'prod': "// const API_BASE_URL = 'http://120.48.150.254:8888'"
        }
    ]
    
    for file_info in files_to_update:
        update_file_for_local(file_info)
    
    print("✅ 已切换到本地测试环境")
    print("📝 本地配置:")
    print("   - 前端开发服务器: http://localhost:5173")
    print("   - 后端API服务器: http://localhost:8888")

def switch_to_production():
    """切换到生产环境"""
    print("🔄 切换到生产环境...")
    
    files_to_update = [
        {
            'file': 'src/config.js',
            'local': "// export const API_BASE_URL = 'http://localhost:8888'",
            'prod': "export const API_BASE_URL = 'http://120.48.150.254:8888'"
        },
        {
            'file': 'src/config/axios.js',
            'local': "// axios.defaults.baseURL = 'http://localhost:8888'", 
            'prod': "axios.defaults.baseURL = 'http://120.48.150.254:8888'"
        },
        {
            'file': 'vite.config.js',
            'local': "        // target: 'http://localhost:8888',",
            'prod': "        target: 'http://120.48.150.254:8888',"
        },
        {
            'file': 'src/views/Database.vue',
            'local': "// const API_BASE_URL = 'http://localhost:8888'",
            'prod': "const API_BASE_URL = 'http://120.48.150.254:8888'"
        }
    ]
    
    for file_info in files_to_update:
        update_file_for_production(file_info)
    
    print("✅ 已切换到生产环境")
    print("📝 生产配置:")
    print("   - API服务器: http://120.48.150.254:8888")

def update_file_for_local(file_info):
    """更新文件为本地配置"""
    file_path = file_info['file']
    if not os.path.exists(file_path):
        print(f"⚠️ 文件不存在: {file_path}")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换生产配置为注释
        content = content.replace(
            file_info['prod'].replace('//', '').strip(),
            file_info['prod']
        )
        
        # 启用本地配置
        content = content.replace(
            file_info['local'].replace('//', '').strip(),
            file_info['local']
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 已更新: {file_path}")
        
    except Exception as e:
        print(f"❌ 更新文件失败 {file_path}: {e}")

def update_file_for_production(file_info):
    """更新文件为生产配置"""
    file_path = file_info['file']
    if not os.path.exists(file_path):
        print(f"⚠️ 文件不存在: {file_path}")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 注释本地配置
        content = content.replace(
            file_info['local'].replace('//', '').strip(),
            file_info['local']
        )
        
        # 启用生产配置
        content = content.replace(
            file_info['prod'].replace('//', '').strip(),
            file_info['prod']
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 已更新: {file_path}")
        
    except Exception as e:
        print(f"❌ 更新文件失败 {file_path}: {e}")

def show_current_config():
    """显示当前配置"""
    print("📋 当前配置状态:")
    
    config_file = 'src/config.js'
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'localhost:8888' in content and not content.count('// export const API_BASE_URL') > content.count('export const API_BASE_URL'):
            print("🟢 当前环境: 本地测试环境")
            print("   - API地址: http://localhost:8888")
        else:
            print("🔵 当前环境: 生产环境")
            print("   - API地址: http://120.48.150.254:8888")
    else:
        print("❌ 配置文件不存在")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("🔧 环境切换脚本")
        print("用法:")
        print("  python switch-env.py local      # 切换到本地测试环境")
        print("  python switch-env.py prod       # 切换到生产环境")
        print("  python switch-env.py status     # 查看当前环境状态")
        print()
        show_current_config()
        return
    
    command = sys.argv[1].lower()
    
    if command in ['local', 'localhost', 'dev']:
        switch_to_local()
    elif command in ['prod', 'production', 'deploy']:
        switch_to_production()
    elif command in ['status', 'show', 'current']:
        show_current_config()
    else:
        print(f"❌ 未知命令: {command}")
        print("支持的命令: local, prod, status")

if __name__ == "__main__":
    main()
