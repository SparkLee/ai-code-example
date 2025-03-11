"""
洛克菲勒家族关系研究项目 - 主程序
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_requirements():
    """检查并安装所需依赖"""
    print("正在检查并安装依赖...")
    try:
        # 使用uv安装依赖
        subprocess.run(["uv", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ 依赖安装完成")
    except FileNotFoundError:
        # 如果uv不可用，则使用pip
        print("⚠️ uv未安装，使用pip安装依赖")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ 依赖安装完成")
    except Exception as e:
        print(f"❌ 安装依赖时出错: {e}")
        sys.exit(1)

def collect_data():
    """收集洛克菲勒家族数据"""
    print("\n📊 正在收集洛克菲勒家族数据...")
    try:
        from 数据收集 import rockefeller_members
        print(f"✅ 数据收集完成，共收集 {len(rockefeller_members)} 位家族成员信息")
    except Exception as e:
        print(f"❌ 数据收集失败: {e}")
        sys.exit(1)

def analyze_data():
    """分析家族关系数据"""
    print("\n🔍 正在分析洛克菲勒家族关系...")
    try:
        import 数据分析
        print("✅ 数据分析完成")
    except Exception as e:
        print(f"❌ 数据分析失败: {e}")
        sys.exit(1)

def start_web_report():
    """启动Web报告服务器"""
    print("\n🌐 正在启动Web报告服务器...")
    try:
        # 使用subprocess启动Web服务器
        web_process = subprocess.Popen([sys.executable, "web_report.py"], 
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             text=True)
        
        # 等待服务器启动
        time.sleep(2)
        
        if web_process.poll() is None:
            print("✅ Web报告服务器已启动")
            print("📱 请在浏览器中访问: http://127.0.0.1:8050")
        else:
            stdout, stderr = web_process.communicate()
            print(f"❌ Web报告服务器启动失败")
            print(f"错误信息: {stderr}")
            sys.exit(1)
        
        return web_process
    except Exception as e:
        print(f"❌ 启动Web服务器失败: {e}")
        sys.exit(1)

def update_todo():
    """更新待办事项"""
    todo_path = Path('../todo.md')
    if todo_path.exists():
        with open(todo_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新待办事项
        content = content.replace("- [ ] 收集洛克菲勒家族基础信息", "- [x] 收集洛克菲勒家族基础信息")
        content = content.replace("- [ ] 收集家族重要成员信息", "- [x] 收集家族重要成员信息")
        content = content.replace("- [ ] 分析家族关系网络", "- [x] 分析家族关系网络")
        content = content.replace("- [ ] 创建数据可视化", "- [x] 创建数据可视化")
        content = content.replace("- [ ] 构建交互式Web报告", "- [x] 构建交互式Web报告")
        
        # 更新进行中和已完成的任务
        content = content.replace("## 进行中\n- 创建项目结构", "## 进行中\n- 完成项目总结")
        content = content.replace("## 已完成", "## 已完成\n- 创建项目结构\n- 收集洛克菲勒家族基础信息\n- 收集家族重要成员信息\n- 分析家族关系网络\n- 创建数据可视化\n- 构建交互式Web报告")
        
        with open(todo_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 待办事项已更新")

if __name__ == "__main__":
    print("="*50)
    print("🚀 洛克菲勒家族关系研究项目 🚀")
    print("="*50)
    
    # 检查requirements.txt是否存在，如果不存在则创建
    if not os.path.exists('requirements.txt'):
        with open('requirements.txt', 'w', encoding='utf-8') as f:
            f.write("dash==2.14.0\nplotly==5.18.0\nnetworkx==3.2.1\npandas==2.1.2\nnumpy==1.26.1")
    
    # 检查并安装依赖
    check_requirements()
    
    # 检查数据目录
    os.makedirs('数据', exist_ok=True)
    os.makedirs('结果', exist_ok=True)
    
    # 收集数据
    collect_data()
    
    # 分析数据
    analyze_data()
    
    # 更新待办事项
    update_todo()
    
    # 启动Web报告
    web_process = start_web_report()
    
    # 等待用户退出
    print("\n🔍 研究项目已完成并启动Web报告服务")
    print("按 Ctrl+C 退出程序")
    
    try:
        # 等待Web服务器进程结束
        web_process.wait()
    except KeyboardInterrupt:
        print("\n正在关闭服务器...")
        web_process.terminate()
        print("程序已退出")
