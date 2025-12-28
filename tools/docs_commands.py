#!/usr/bin/env python3
"""
FastX-Tui 文档命令工具

使用 Typer 构建的文档相关命令行工具，提供生成、预览和部署文档的功能
"""
import os
import subprocess
from typing import Optional
import typer

app = typer.Typer(name="fastx-tui-docs", help="FastX-Tui 文档命令工具")

def run_command(cmd: str, cwd: Optional[str] = None) -> int:
    """运行系统命令
    
    Args:
        cmd: 要运行的命令
        cwd: 工作目录
        
    Returns:
        命令返回码
    """
    print(f"运行命令: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print(f"错误: {result.stderr}")
    return result.returncode


@app.command()
def build(
    output_dir: Optional[str] = typer.Option(
        "build/site",
        "--output-dir",
        "-o",
        help="文档构建输出目录"
    ),
    theme: Optional[str] = typer.Option(
        "material",
        "--theme",
        "-t",
        help="文档主题"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="显示详细信息"
    )
):
    """构建文档
    
    使用 MkDocs 构建 FastX-Tui 文档
    """
    print("📚 构建 FastX-Tui 文档...")
    
    cmd = f"mkdocs build --site-dir {output_dir}"
    if verbose:
        cmd += " --verbose"
    
    returncode = run_command(cmd)
    
    if returncode == 0:
        print(f"✅ 文档构建成功！输出目录: {output_dir}")
    else:
        print("❌ 文档构建失败！")
    
    return returncode


@app.command()
def serve(
    port: Optional[int] = typer.Option(
        8000,
        "--port",
        "-p",
        help="本地服务器端口"
    ),
    livereload: bool = typer.Option(
        True,
        "--livereload/--no-livereload",
        help="是否启用实时重载"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="显示详细信息"
    )
):
    """启动本地文档服务器
    
    在本地启动 MkDocs 开发服务器，用于预览文档
    """
    print(f"🚀 启动本地文档服务器...")
    
    cmd = f"mkdocs serve --port {port}"
    if not livereload:
        cmd += " --no-livereload"
    if verbose:
        cmd += " --verbose"
    
    print(f"\n📖 文档服务器正在运行...")
    print(f"🌐 访问地址: http://localhost:{port}")
    print(f"💡 按 Ctrl+C 停止服务器\n")
    
    returncode = run_command(cmd)
    
    if returncode == 0:
        print("✅ 文档服务器正常关闭")
    else:
        print("❌ 文档服务器异常关闭")
    
    return returncode


@app.command()
def init(
    project_name: str = typer.Option(
        "FastX-Tui",
        "--project-name",
        "-n",
        help="项目名称"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="强制覆盖现有配置"
    )
):
    """初始化文档配置
    
    初始化 MkDocs 文档配置文件
    """
    print("🔧 初始化文档配置...")
    
    # 检查 mkdocs.yml 是否已存在
    if os.path.exists("mkdocs.yml") and not force:
        print("⚠️  mkdocs.yml 已存在，使用 --force 强制覆盖")
        return 1
    
    # 运行 mkdocs new 命令
    cmd = f"mkdocs new . --site-dir site --theme material --quiet"
    returncode = run_command(cmd)
    
    if returncode == 0:
        print("✅ 文档配置初始化成功！")
        print("📄 配置文件: mkdocs.yml")
        print("💡 使用 'fastx-tui-docs serve' 预览文档")
    else:
        print("❌ 文档配置初始化失败！")
    
    return returncode


@app.command()
def deploy(
    repo: Optional[str] = typer.Option(
        None,
        "--repo",
        "-r",
        help="部署目标仓库"
    ),
    branch: Optional[str] = typer.Option(
        "gh-pages",
        "--branch",
        "-b",
        help="部署目标分支"
    )
):
    """部署文档
    
    将文档部署到 GitHub Pages 或其他 git 仓库
    """
    print("🚀 部署文档...")
    
    if repo:
        cmd = f"mkdocs gh-deploy --force --remote-name {repo} --remote-branch {branch}"
    else:
        cmd = f"mkdocs gh-deploy --force --remote-branch {branch}"
    
    returncode = run_command(cmd)
    
    if returncode == 0:
        print(f"✅ 文档部署成功！")
        print(f"🌐 部署分支: {branch}")
    else:
        print("❌ 文档部署失败！")
    
    return returncode


@app.command()
def check():
    """检查文档配置
    
    检查 MkDocs 配置文件和文档结构是否正确
    """
    print("🔍 检查文档配置...")
    
    cmd = "mkdocs build --dry-run"
    returncode = run_command(cmd)
    
    if returncode == 0:
        print("✅ 文档配置检查通过！")
    else:
        print("❌ 文档配置检查失败！")
    
    return returncode


@app.command()
def help(
    command: Optional[str] = typer.Argument(None, help="要查看帮助的命令")
):
    """显示帮助信息
    
    显示指定命令的帮助信息
    """
    if command:
        print(f"显示命令 '{command}' 的帮助信息:")
        cmd = f"fastx-tui-docs {command} --help"
    else:
        print("FastX-Tui 文档命令工具帮助:")
        cmd = "fastx-tui-docs --help"
    
    return run_command(cmd)


if __name__ == "__main__":
    app()
