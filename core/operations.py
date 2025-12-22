#!/usr/bin/env python3
"""
操作类模块
"""
import platform
import os
import sys
import time
import psutil
import socket
import pkg_resources # pip install setuptools
from typing import List, Dict
from datetime import datetime

class SystemOperations:
    """系统操作类"""
    
    @staticmethod
    def get_system_info() -> str:
        """获取系统信息"""
        info = []
        info.append("=" * 70)
        info.append("📊 系统信息".center(70))
        info.append("=" * 70)
        
        # 基础信息
        info.append(f"\n🏷️  操作系统: {platform.system()} {platform.version()}")
        info.append(f"🖥️  计算机名: {platform.node()}")
        info.append(f"⚙️  处理器: {platform.processor()}")
        info.append(f"🧮 CPU核心数: {psutil.cpu_count(logical=True)}")
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=0.5)
        info.append(f"📈 CPU使用率: {cpu_percent}%")
        
        # CPU频率
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                info.append(f"📊 CPU频率: {cpu_freq.current:.0f} MHz")
        except:
            pass
        
        # 内存信息
        mem = psutil.virtual_memory()
        info.append(f"\n💾 内存信息:")
        info.append(f"  总量: {mem.total / (1024**3):.2f} GB")
        info.append(f"  已用: {mem.used / (1024**3):.2f} GB ({mem.percent}%)")
        info.append(f"  可用: {mem.available / (1024**3):.2f} GB")
        
        # 交换内存
        swap = psutil.swap_memory()
        info.append(f"\n💽 交换内存:")
        info.append(f"  总量: {swap.total / (1024**3):.2f} GB")
        info.append(f"  已用: {swap.used / (1024**3):.2f} GB ({swap.percent}%)")
        
        # 获取磁盘信息
        info.append(f"\n💿 磁盘信息:")
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                info.append(f"\n  {partition.device}:")
                info.append(f"    挂载点: {partition.mountpoint}")
                info.append(f"    文件系统: {partition.fstype}")
                info.append(f"    总容量: {usage.total / (1024**3):.2f} GB")
                info.append(f"    已使用: {usage.used / (1024**3):.2f} GB ({usage.percent}%)")
                info.append(f"    可用空间: {usage.free / (1024**3):.2f} GB")
                
                # 进度条
                bar_length = 30
                filled_length = int(bar_length * usage.percent / 100)
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                info.append(f"    使用率: [{bar}]")
                
            except Exception as e:
                info.append(f"\n  {partition.device}: 无法访问 ({str(e)})")
        
        info.append(f"\n🐍 Python版本: {platform.python_version()}")
        info.append(f"🕐 系统运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(info)
    
    @staticmethod
    def create_plugin(plugin_name: str, plugin_display_name: str = "") -> str:
        """创建FastX-Tui插件脚手架
        
        Args:
            plugin_name: 插件名称（英文，用于目录和类名）
            plugin_display_name: 插件显示名称（中文，用于界面显示）
            
        Returns:
            创建结果信息
        """
        import shutil
        import subprocess
        from pathlib import Path
        
        # 设置插件目录
        plugins_dir = "plugins"
        plugin_dir_name = f"FastX-Tui-Plugin-{plugin_name}"
        plugin_path = Path(plugins_dir) / plugin_dir_name
        
        # 如果显示名称未提供，使用插件名称
        if not plugin_display_name:
            plugin_display_name = plugin_name
        
        try:
            # 检查cookiecutter是否安装
            try:
                subprocess.run([sys.executable, "-m", "cookiecutter", "--version"], 
                              capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError:
                # 安装cookiecutter
                subprocess.run([sys.executable, "-m", "pip", "install", "cookiecutter"], 
                              capture_output=True, text=True, check=True)
            
            # 创建插件目录
            plugin_path.mkdir(parents=True, exist_ok=True)
            
            # 构建cookiecutter命令
            cookiecutter_dir = Path("cookiecutter-fastx-tui-plugin-templates")
            
            # 如果本地有cookiecutter模板，使用本地模板
            if cookiecutter_dir.exists():
                cmd = [
                    sys.executable, "-m", "cookiecutter", 
                    str(cookiecutter_dir),
                    "--output-dir", plugins_dir,
                    "--no-input",
                    f"plugin_name={plugin_name}",
                    f"plugin_display_name={plugin_display_name}",
                    f"plugin_description=FastX-Tui插件示例",
                    f"plugin_author=Your Name",
                    f"plugin_version=1.0.0",
                    f"plugin_category=工具",
                    f"plugin_tags=['示例', '工具']",
                    f"plugin_repository=",
                    f"license=MIT",
                    f"year={datetime.now().year}"
                ]
            else:
                # 使用GitHub上的模板
                cmd = [
                    sys.executable, "-m", "cookiecutter", 
                    "https://github.com/fastxteam/cookiecutter-fastx-tui-plugin-templates.git",
                    "--output-dir", plugins_dir,
                    "--no-input",
                    f"plugin_name={plugin_name}",
                    f"plugin_display_name={plugin_display_name}",
                    f"plugin_description=FastX-Tui插件示例",
                    f"plugin_author=Your Name",
                    f"plugin_version=1.0.0",
                    f"plugin_category=工具",
                    f"plugin_tags=['示例', '工具']",
                    f"plugin_repository=",
                    f"license=MIT",
                    f"year={datetime.now().year}"
                ]
            
            # 执行cookiecutter命令
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return f"✅ 插件 '{plugin_display_name}' 创建成功！\n" \
                       f"📁 插件目录: {plugin_path}\n" \
                       f"🚀 插件已准备就绪，可以开始开发。"
            else:
                return f"❌ 插件创建失败: {result.stderr}"
                
        except Exception as e:
            return f"❌ 插件创建过程中出错: {str(e)}"
    
    @staticmethod
    def get_network_info() -> str:
        """获取网络信息"""
        info = []
        info.append("=" * 70)
        info.append("🌐 网络信息".center(70))
        info.append("=" * 70)
        
        # 获取主机信息
        hostname = socket.gethostname()
        info.append(f"\n🏷️  主机名: {hostname}")
        
        try:
            local_ip = socket.gethostbyname(hostname)
            info.append(f"📡 本地IP: {local_ip}")
        except:
            info.append("📡 本地IP: 无法获取")
        
        # 获取网络接口信息
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        info.append(f"\n🔌 网络接口:")
        for interface, addr_list in addrs.items():
            info.append(f"\n  {interface}:")
            if interface in stats:
                stat = stats[interface]
                status_icon = "🟢" if stat.isup else "🔴"
                info.append(f"    状态: {status_icon} {'已连接' if stat.isup else '未连接'}")
                if stat.speed > 0:
                    info.append(f"    速度: {stat.speed} Mbps")
                info.append(f"    MTU: {stat.mtu}")
            
            for addr in addr_list:
                if addr.family == 2:  # AF_INET
                    info.append(f"    IPv4地址: {addr.address}")
                    if addr.netmask:
                        info.append(f"    子网掩码: {addr.netmask}")
                    if addr.broadcast:
                        info.append(f"    广播地址: {addr.broadcast}")
                elif addr.family == 23:  # AF_INET6:
                    info.append(f"    IPv6地址: {addr.address}")
        
        # 网络连接统计
        net_io = psutil.net_io_counters()
        info.append(f"\n📊 网络统计:")
        info.append(f"  发送字节: {net_io.bytes_sent / (1024**2):.2f} MB")
        info.append(f"  接收字节: {net_io.bytes_recv / (1024**2):.2f} MB")
        info.append(f"  发送包数: {net_io.packets_sent}")
        info.append(f"  接收包数: {net_io.packets_recv}")
        
        return "\n".join(info)
    
    @staticmethod
    def list_processes() -> str:
        """列出进程"""
        info = []
        info.append("=" * 70)
        info.append("📋 进程列表".center(70))
        info.append("=" * 70)
        
        info.append(f"\n{'PID':<8} {'进程名':<25} {'状态':<10} {'CPU%':<8} {'内存%':<8} {'用户':<15}")
        info.append("-" * 70)
        
        count = 0
        try:
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'username']):
                try:
                    proc_info = proc.info
                    info.append(f"{proc_info['pid']:<8} "
                              f"{proc_info['name'][:24]:<25} "
                              f"{proc_info['status']:<10} "
                              f"{proc_info['cpu_percent']:<8.1f} "
                              f"{proc_info['memory_percent']:<8.1f} "
                              f"{proc_info['username'] or 'N/A':<15}")
                    count += 1
                    if count >= 30:
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            info.append(f"\n获取进程信息时出错: {str(e)}")
        
        total_procs = len(list(psutil.process_iter()))
        info.append(f"\n📈 显示进程数: {count} (总共: {total_procs})")
        
        return "\n".join(info)
    
    @staticmethod
    def get_disk_space() -> str:
        """获取磁盘空间信息"""
        info = []
        info.append("=" * 70)
        info.append("💾 磁盘空间".center(70))
        info.append("=" * 70)
        
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                info.append(f"\n📂 {partition.device}")
                info.append(f"  挂载点: {partition.mountpoint}")
                info.append(f"  文件系统: {partition.fstype}")
                info.append(f"  总容量: {usage.total / (1024**3):.2f} GB")
                info.append(f"  已使用: {usage.used / (1024**3):.2f} GB")
                info.append(f"  可用空间: {usage.free / (1024**3):.2f} GB")
                
                # 进度条
                percent = usage.percent
                bar_length = 30
                filled_length = int(bar_length * percent / 100)
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                
                # 根据使用率显示不同颜色
                if percent > 90:
                    color = "red"
                elif percent > 70:
                    color = "yellow"
                else:
                    color = "green"
                
                info.append(f"  使用率: [{bar}] {percent:.1f}%")
                
            except Exception as e:
                info.append(f"\n❌ {partition.device}: 无法访问 ({str(e)})")
        
        return "\n".join(info)
    
    @staticmethod
    def get_system_uptime() -> str:
        """获取系统运行时间"""
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        
        days = int(uptime_seconds // (24 * 3600))
        hours = int((uptime_seconds % (24 * 3600)) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        
        info = []
        info.append("=" * 70)
        info.append("⏰ 系统运行时间".center(70))
        info.append("=" * 70)
        
        info.append(f"\n系统启动时间: {datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S')}")
        info.append(f"已运行时间: {days}天 {hours}小时 {minutes}分钟 {seconds}秒")
        
        return "\n".join(info)

class FileOperations:
    """文件操作类"""
    
    @staticmethod
    def list_directory(path: str = ".") -> str:
        """列出目录"""
        info = []
        info.append("=" * 70)
        info.append(f"📁 目录列表: {os.path.abspath(path)}".center(70))
        info.append("=" * 70)
        
        try:
            items = os.listdir(path)
            items.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
            
            info.append(f"\n{'类型':<6} {'权限':<10} {'大小':<12} {'修改时间':<20} {'名称':<30}")
            info.append("-" * 70)
            
            total_size = 0
            dir_count = 0
            file_count = 0
            
            for item in items:
                full_path = os.path.join(path, item)
                try:
                    stat = os.stat(full_path)
                    
                    if os.path.isdir(full_path):
                        item_type = "[目录]"
                        size = ""
                        dir_count += 1
                    else:
                        item_type = "[文件]"
                        size = FileOperations._format_size(stat.st_size)
                        total_size += stat.st_size
                        file_count += 1
                    
                    # 获取权限
                    mode = stat.st_mode
                    permissions = FileOperations._get_permissions(mode)
                    
                    # 获取修改时间
                    mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    
                    info.append(f"{item_type:<6} {permissions:<10} {size:<12} {mtime:<20} {item:<30}")
                    
                except Exception as e:
                    info.append(f"[错误] {'':<10} {'':<12} {'':<20} {item} ({str(e)})")
            
            info.append(f"\n📊 统计:")
            info.append(f"  目录数: {dir_count}")
            info.append(f"  文件数: {file_count}")
            info.append(f"  总大小: {FileOperations._format_size(total_size)}")
            
        except Exception as e:
            info.append(f"\n❌ 错误: {str(e)}")
        
        return "\n".join(info)
    
    @staticmethod
    def _format_size(size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    @staticmethod
    def _get_permissions(mode):
        """获取权限字符串"""
        perm = []
        # Owner
        perm.append('r' if mode & 0o400 else '-')
        perm.append('w' if mode & 0o200 else '-')
        perm.append('x' if mode & 0o100 else '-')
        # Group
        perm.append('r' if mode & 0o040 else '-')
        perm.append('w' if mode & 0o020 else '-')
        perm.append('x' if mode & 0o010 else '-')
        # Others
        perm.append('r' if mode & 0o004 else '-')
        perm.append('w' if mode & 0o002 else '-')
        perm.append('x' if mode & 0o001 else '-')
        return ''.join(perm)
    
    @staticmethod
    def show_file_tree(path: str = ".", max_depth: int = 3) -> str:
        """显示文件树"""
        def build_tree(startpath, prefix="", depth=0):
            if depth >= max_depth:
                return []
            
            try:
                items = os.listdir(startpath)
            except:
                return [f"{prefix}❌ 无法访问"]
            
            items.sort(key=lambda x: (not os.path.isdir(os.path.join(startpath, x)), x.lower()))
            
            lines = []
            for i, item in enumerate(items):
                if item.startswith('.'):
                    continue
                    
                full_path = os.path.join(startpath, item)
                is_last = i == len(items) - 1
                
                if os.path.isdir(full_path):
                    lines.append(f"{prefix}{'└── ' if is_last else '├── '}📁 {item}/")
                    extension = "    " if is_last else "│   "
                    lines.extend(build_tree(full_path, prefix + extension, depth + 1))
                else:
                    try:
                        size = os.path.getsize(full_path)
                        size_str = FileOperations._format_size(size)
                        lines.append(f"{prefix}{'└── ' if is_last else '├── '}📄 {item} ({size_str})")
                    except:
                        lines.append(f"{prefix}{'└── ' if is_last else '├── '}📄 {item}")
            
            return lines
        
        info = [f"🌳 目录树: {os.path.abspath(path)} (深度: {max_depth})\n"]
        info.extend(build_tree(path))
        return "\n".join(info)
    
    @staticmethod
    def search_files(pattern: str = "*", path: str = ".", max_results: int = 50) -> str:
        """搜索文件"""
        import fnmatch
        
        info = []
        info.append("=" * 70)
        info.append(f"🔍 文件搜索: '{pattern}' 在 '{path}'".center(70))
        info.append("=" * 70)
        
        matches = []
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if fnmatch.fnmatch(file, pattern):
                        full_path = os.path.join(root, file)
                        try:
                            size = os.path.getsize(full_path)
                            size_str = FileOperations._format_size(size)
                            mtime = os.path.getmtime(full_path)
                            mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                            matches.append((full_path, size_str, mtime_str))
                        except:
                            matches.append((full_path, "未知", "未知"))
                
                if len(matches) >= max_results:
                    break
        
        except Exception as e:
            info.append(f"\n❌ 搜索错误: {str(e)}")
            return "\n".join(info)
        
        if matches:
            info.append(f"\n✅ 找到 {len(matches)} 个文件:\n")
            info.append(f"{'路径':<50} {'大小':<12} {'修改时间':<20}")
            info.append("-" * 70)
            
            for match in matches[:max_results]:
                info.append(f"{match[0]:<50} {match[1]:<12} {match[2]:<20}")
            
            if len(matches) > max_results:
                info.append(f"\n... 还有 {len(matches) - max_results} 个文件未显示")
        else:
            info.append(f"\n📭 没有找到匹配 '{pattern}' 的文件")
        
        return "\n".join(info)

class PythonOperations:
    """Python操作类"""
    
    @staticmethod
    def get_python_info() -> str:
        """获取Python信息"""
        info = []
        info.append("=" * 70)
        info.append("🐍 Python环境信息".center(70))
        info.append("=" * 70)
        
        info.append(f"\n📌 Python版本: {platform.python_version()}")
        info.append(f"🏷️  实现: {platform.python_implementation()}")
        info.append(f"🔧 编译器: {platform.python_compiler()}")
        info.append(f"📂 执行路径: {sys.executable}")
        
        # 检查虚拟环境
        in_venv = (hasattr(sys, 'real_prefix') or 
                  (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
        info.append(f"🌐 虚拟环境: {'✅ 是' if in_venv else '❌ 否'}")
        
        if in_venv:
            info.append(f"  虚拟环境路径: {sys.prefix}")
            info.append(f"  基础Python路径: {sys.base_prefix}")
        
        # 检查环境变量
        venv_path = os.environ.get('VIRTUAL_ENV')
        if venv_path:
            info.append(f"  环境变量 VIRTUAL_ENV: {venv_path}")
        
        info.append(f"\n🗺️  Python路径 (前10个):")
        for i, path in enumerate(sys.path[:10], 1):
            info.append(f"  {i:2d}. {path}")
        
        if len(sys.path) > 10:
            info.append(f"  ... 还有 {len(sys.path)-10} 个路径")
        
        # Python编译选项
        if hasattr(sys, 'flags'):
            flags = []
            for flag in ['debug', 'inspect', 'interactive', 'optimize', 
                        'dont_write_bytecode', 'no_user_site', 'no_site',
                        'ignore_environment', 'verbose', 'bytes_warning',
                        'quiet', 'hash_randomization', 'isolated']:
                if getattr(sys.flags, flag, False):
                    flags.append(flag)
            if flags:
                info.append(f"\n⚙️  编译选项: {', '.join(flags)}")
        
        return "\n".join(info)
    
    @staticmethod
    def list_packages() -> str:
        """列出已安装包"""
        info = []
        info.append("=" * 70)
        info.append("📦 已安装Python包".center(70))
        info.append("=" * 70)
        
        packages = []
        try:
            for dist in pkg_resources.working_set:
                packages.append((dist.project_name, dist.version))
            
            # 按名称排序
            packages.sort(key=lambda x: x[0].lower())
            
            info.append(f"\n📊 总计: {len(packages)} 个包\n")
            
            # 分列显示
            col_width = 30
            cols = 3
            row_count = (len(packages) + cols - 1) // cols
            
            for i in range(row_count):
                row = []
                for col in range(cols):
                    idx = i + col * row_count
                    if idx < len(packages):
                        name, version = packages[idx]
                        # 截断过长的包名
                        if len(name) > col_width - 12:
                            name = name[:col_width - 15] + "..."
                        row.append(f"{name:<{col_width-10}} {version:<10}")
                if row:
                    info.append("  ".join(row))
            
            # 添加统计信息
            unique_versions = len(set(version for _, version in packages))
            info.append(f"\n📈 统计:")
            info.append(f"  唯一版本数: {unique_versions}")
            
            # 找出最大的包
            if packages:
                max_package = max(packages, key=lambda x: len(x[0]))
                info.append(f"  最长包名: {max_package[0]} ({max_package[1]})")
            
        except Exception as e:
            info.append(f"\n❌ 获取包信息时出错: {str(e)}")
        
        return "\n".join(info)
    
    @staticmethod
    def check_imports() -> str:
        """检查常用包的导入"""
        common_packages = [
            ("numpy", "数值计算"),
            ("pandas", "数据分析"),
            ("matplotlib", "数据可视化"),
            ("requests", "HTTP请求"),
            ("flask", "Web框架"),
            ("django", "Web框架"),
            ("sqlalchemy", "数据库ORM"),
            ("pytest", "测试框架"),
            ("rich", "终端美化"),
            ("psutil", "系统监控")
        ]
        
        info = []
        info.append("=" * 70)
        info.append("🔍 常用Python包检查".center(70))
        info.append("=" * 70)
        
        info.append(f"\n{'包名':<20} {'状态':<10} {'描述':<30}")
        info.append("-" * 70)
        
        available = 0
        for package, description in common_packages:
            try:
                __import__(package)
                status = "✅ 已安装"
                available += 1
            except ImportError:
                status = "❌ 未安装"
            except Exception as e:
                status = f"⚠️  错误: {str(e)[:20]}"
            
            info.append(f"{package:<20} {status:<10} {description:<30}")
        
        info.append(f"\n📊 统计: {available}/{len(common_packages)} 个常用包已安装")
        
        return "\n".join(info)