#!/usr/bin/env python3
"""
FastX-Tui 构建命令工具
"""
import os
import sys
import subprocess
from rich.console import Console

console = Console()

def build_exe():
    """
    使用 PyInstaller 打包 FastX-Tui 为可执行文件
    """
    console.print("[bold green]🚀 开始构建 FastX-Tui 可执行文件...[/bold green]")
    
    # 检查 PyInstaller 是否安装
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        console.print("[bold red]❌ PyInstaller 未安装，请先安装: pip install pyinstaller[/bold red]")
        sys.exit(1)
    
    # 构建命令
    build_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # 生成单个可执行文件
        "--name", "fastx-tui",  # 可执行文件名称
        # "--windowed",  # 无控制台窗口（仅GUI应用），CLI应用需要控制台
        "--icon", "NONE",  # 无图标（可根据需要添加图标路径）
        "--add-data", "locales;locales",  # 添加语言文件
        "--add-data", "plugins;plugins",  # 添加插件目录
        "--hidden-import", "core",  # 隐藏导入
        "--hidden-import", "config",  # 隐藏导入
        "--hidden-import", "features",  # 隐藏导入
        "--hidden-import", "models",  # 隐藏导入
        "--hidden-import", "tools",  # 隐藏导入
        "main.py"  # 主入口文件
    ]
    
    console.print(f"[bold blue]📋 构建命令:[/bold blue] {' '.join(build_cmd)}")
    console.print("[bold yellow]⏳ 正在构建...[/bold yellow]")
    
    try:
        # 执行构建命令
        # 使用check=False，因为PyInstaller可能会返回非零退出码，但实际上构建成功
        result = subprocess.run(build_cmd, check=False, text=True)
        
        # 检查是否生成了可执行文件
        exe_path = os.path.join(os.getcwd(), 'dist', 'fastx-tui.exe') if sys.platform == 'win32' else os.path.join(os.getcwd(), 'dist', 'fastx-tui')
        if os.path.exists(exe_path):
            console.print("[bold green]✅ 构建成功！[/bold green]")
            console.print(f"[bold blue]📦 输出目录:[/bold blue] {os.path.join(os.getcwd(), 'dist')}")
            console.print(f"[bold blue]📄 可执行文件:[/bold blue] {exe_path}")
            return True
        else:
            console.print("[bold red]❌ 构建失败，未生成可执行文件[/bold red]")
            return False
    except Exception as e:
        console.print(f"[bold red]❌ 构建过程中发生错误:[/bold red] {str(e)}")
        return False

# 直接运行该脚本时执行构建
if __name__ == "__main__":
    build_exe()
