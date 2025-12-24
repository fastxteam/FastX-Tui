#!/usr/bin/env python3
"""
Ruff 命令行工具，使用 Typer 构建
提供常用的 Ruff 代码检查和格式化命令
"""

import subprocess
import typer

app = typer.Typer(name="ruff-commands", help="Ruff 代码检查和格式化工具")

DEFAULT_PATHS = ["core", "config", "features", "locales", "plugins", "tests", "main.py"]

def run_command(cmd: list[str]) -> int:
    """运行命令并返回结果"""
    print(f"\n=== 运行命令: {' '.join(cmd)} ===")
    result = subprocess.run(cmd, shell=True)
    return result.returncode

@app.command(help="检查代码但不修复")
def lint(
    paths: list[str] = typer.Option(
        DEFAULT_PATHS,
        help="要检查的文件或目录，默认检查所有核心目录和文件"
    )
):
    """检查代码但不修复"""
    return run_command(["ruff", "check"] + paths)

@app.command(help="检查并修复代码")
def lint_fix(
    paths: list[str] = typer.Option(
        DEFAULT_PATHS,
        help="要检查并修复的文件或目录，默认检查所有核心目录和文件"
    )
):
    """检查并修复代码"""
    return run_command(["ruff", "check", "--fix"] + paths)

@app.command(help="格式化代码")
def format(
    paths: list[str] = typer.Option(
        DEFAULT_PATHS,
        help="要格式化的文件或目录，默认格式化所有核心目录和文件"
    )
):
    """格式化代码"""
    return run_command(["ruff", "format"] + paths)

@app.command(help="完整检查（lint + format）")
def check(
    paths: list[str] = typer.Option(
        DEFAULT_PATHS,
        help="要检查的文件或目录，默认检查所有核心目录和文件"
    )
):
    """完整检查（lint + format）"""
    exit_code = run_command(["ruff", "check"] + paths)
    if exit_code != 0:
        return exit_code
    return run_command(["ruff", "format"] + paths)

@app.command(help="运行所有检查并修复")
def all(
    paths: list[str] = typer.Option(
        DEFAULT_PATHS,
        help="要检查并修复的文件或目录，默认检查所有核心目录和文件"
    )
):
    """运行所有检查并修复"""
    exit_code = run_command(["ruff", "check", "--fix"] + paths)
    if exit_code != 0:
        return exit_code
    return run_command(["ruff", "format"] + paths)

if __name__ == "__main__":
    app()