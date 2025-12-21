#!/usr/bin/env python3
"""
网络工具插件
"""
import subprocess
import platform
import socket
import json
import time
import urllib.request
import urllib.error
from typing import Dict, List, Optional
from dataclasses import dataclass
from core.plugin_manager import Plugin, PluginInfo
from core.menu_system import MenuSystem, ActionItem, CommandType

@dataclass
class PingResult:
    """Ping测试结果"""
    target: str
    success: bool
    packets_sent: int
    packets_received: int
    packet_loss: float
    min_rtt: float
    avg_rtt: float
    max_rtt: float

class NetworkToolsPlugin(Plugin):
    """网络工具插件"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="网络工具",
            version="1.0.0",
            author="FastX Team",
            description="网络诊断和测试工具",
            enabled=True
        )
    
    def initialize(self):
        """初始化插件"""
        self.log_info("网络工具插件初始化完成")
    
    def cleanup(self):
        """清理插件资源"""
        self.log_info("网络工具插件清理完成")
    
    def register(self, menu_system: MenuSystem):
        """注册插件到菜单系统"""
        
        # 创建网络工具菜单
        from core.menu_system import MenuNode, MenuType
        network_menu = MenuNode(
            id="network_tools_menu",
            name="网络工具",
            description="网络诊断和测试工具",
            menu_type=MenuType.SUB,
            icon="🌐"
        )
        
        # 注册菜单
        menu_system.register_item(network_menu)
        
        # 添加Ping测试功能
        ping_action = ActionItem(
            id="ping_test",
            name="Ping测试",
            description="测试网络连接和延迟",
            icon="📶",
            command_type=CommandType.PYTHON,
            python_func=self.ping_test,
            args=["8.8.8.8"]  # 默认测试Google DNS
        )
        menu_system.register_item(ping_action)
        network_menu.add_item("ping_test")
        
        # 添加DNS查询功能
        dns_action = ActionItem(
            id="dns_lookup",
            name="DNS查询",
            description="查询域名的DNS记录",
            icon="🔍",
            command_type=CommandType.PYTHON,
            python_func=self.dns_lookup,
            args=["google.com"]  # 默认查询Google
        )
        menu_system.register_item(dns_action)
        network_menu.add_item("dns_lookup")
        
        # 添加端口扫描功能
        port_scan_action = ActionItem(
            id="port_scan",
            name="端口扫描",
            description="扫描指定主机的开放端口",
            icon="🔎",
            command_type=CommandType.PYTHON,
            python_func=self.port_scan,
            args=["localhost", "1-100"]  # 默认扫描本地主机的1-100端口
        )
        menu_system.register_item(port_scan_action)
        network_menu.add_item("port_scan")
        
        # 添加网络信息功能
        network_info_action = ActionItem(
            id="network_details",
            name="网络详情",
            description="显示详细网络信息",
            icon="📡",
            command_type=CommandType.PYTHON,
            python_func=self.get_network_details
        )
        menu_system.register_item(network_info_action)
        network_menu.add_item("network_details")
        
        # 将网络工具菜单添加到主菜单
        main_menu = menu_system.get_item_by_id("main_menu")
        if main_menu and isinstance(main_menu, MenuNode):
            main_menu.add_item("network_tools_menu")
    
    def ping_test(self, target: str = "8.8.8.8", count: int = 4) -> str:
        """执行Ping测试"""
        info = []
        info.append("=" * 70)
        info.append(f"📶 Ping测试: {target}".center(70))
        info.append("=" * 70)
        
        try:
            # 根据操作系统选择ping命令
            if platform.system() == "Windows":
                cmd = f"ping -n {count} {target}"
            else:
                cmd = f"ping -c {count} {target}"
            
            info.append(f"\n🔄 执行命令: {cmd}\n")
            
            # 执行ping命令
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # 解析ping结果（简化版）
                lines = output.split('\n')
                for line in lines:
                    if "Packets:" in line or " packets transmitted" in line:
                        info.append(f"📦 {line.strip()}")
                    elif "Minimum =" in line or "min/avg/max" in line:
                        info.append(f"⏱️  {line.strip()}")
                    elif "bytes from" in line or "Reply from" in line:
                        # 只显示第一个回复
                        if "第一个回复" not in locals():
                            info.append(f"✅ {line.strip()}")
                            locals()["第一个回复"] = True
                
                info.append(f"\n✅ Ping测试成功!")
                
            else:
                info.append(f"\n❌ Ping测试失败!")
                info.append(f"错误输出:\n{result.stderr}")
                
        except subprocess.TimeoutExpired:
            info.append(f"\n⏰ Ping测试超时!")
        except Exception as e:
            info.append(f"\n❌ Ping测试出错: {str(e)}")
        
        info.append(f"\n💡 提示: 可以使用 'ping_test google.com 8' 测试8次")
        
        return "\n".join(info)
    
    def dns_lookup(self, domain: str = "google.com") -> str:
        """执行DNS查询"""
        info = []
        info.append("=" * 70)
        info.append(f"🔍 DNS查询: {domain}".center(70))
        info.append("=" * 70)
        
        try:
            info.append(f"\n🔗 查询域名: {domain}")
            
            # 查询A记录
            try:
                ip_addresses = socket.gethostbyname_ex(domain)
                info.append(f"\n📡 A记录 (IPv4):")
                for ip in ip_addresses[2]:
                    info.append(f"  • {ip}")
            except socket.gaierror as e:
                info.append(f"\n❌ A记录查询失败: {str(e)}")
            
            # 尝试查询其他记录（需要安装dnspython）
            try:
                import dns.resolver
                
                # 查询MX记录
                try:
                    mx_records = dns.resolver.resolve(domain, 'MX')
                    info.append(f"\n📨 MX记录 (邮件服务器):")
                    for mx in mx_records:
                        info.append(f"  • {mx.preference} {mx.exchange}")
                except:
                    info.append(f"\n📭 没有MX记录")
                
                # 查询NS记录
                try:
                    ns_records = dns.resolver.resolve(domain, 'NS')
                    info.append(f"\n🏢 NS记录 (域名服务器):")
                    for ns in ns_records:
                        info.append(f"  • {ns}")
                except:
                    info.append(f"\n🏢 没有NS记录")
                
                # 查询TXT记录
                try:
                    txt_records = dns.resolver.resolve(domain, 'TXT')
                    info.append(f"\n📝 TXT记录:")
                    for txt in txt_records:
                        info.append(f"  • {txt}")
                except:
                    info.append(f"\n📝 没有TXT记录")
                    
            except ImportError:
                info.append(f"\n💡 提示: 安装 dnspython 包以获取更多DNS记录")
                info.append("      pip install dnspython")
            
        except Exception as e:
            info.append(f"\n❌ DNS查询出错: {str(e)}")
        
        return "\n".join(info)
    
    def port_scan(self, host: str = "localhost", port_range: str = "1-100") -> str:
        """扫描端口"""
        info = []
        info.append("=" * 70)
        info.append(f"🔎 端口扫描: {host}:{port_range}".center(70))
        info.append("=" * 70)
        
        try:
            # 解析端口范围
            if '-' in port_range:
                start_port, end_port = map(int, port_range.split('-'))
            else:
                start_port = end_port = int(port_range)
            
            if start_port < 1 or end_port > 65535 or start_port > end_port:
                info.append(f"\n❌ 无效的端口范围: {port_range}")
                info.append("💡 提示: 端口范围应为 1-65535，例如 1-100")
                return "\n".join(info)
            
            info.append(f"\n🎯 扫描目标: {host}")
            info.append(f"📊 端口范围: {start_port} - {end_port}")
            info.append(f"🔢 总端口数: {end_port - start_port + 1}")
            info.append("\n⏳ 开始扫描...")
            
            open_ports = []
            start_time = time.time()
            
            for port in range(start_port, end_port + 1):
                try:
                    # 创建socket连接
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)  # 设置超时
                    
                    result = sock.connect_ex((host, port))
                    if result == 0:
                        # 获取服务名称
                        try:
                            service = socket.getservbyport(port)
                        except:
                            service = "未知服务"
                        
                        open_ports.append((port, service))
                        info.append(f"  ✅ 端口 {port} 开放 ({service})")
                    
                    sock.close()
                    
                except Exception as e:
                    info.append(f"  ⚠️  扫描端口 {port} 时出错: {str(e)[:30]}")
            
            end_time = time.time()
            scan_time = end_time - start_time
            
            info.append(f"\n📊 扫描完成!")
            info.append(f"⏱️  扫描时间: {scan_time:.2f} 秒")
            info.append(f"🚪 开放端口数: {len(open_ports)}")
            
            if open_ports:
                info.append(f"\n📋 开放端口列表:")
                for port, service in open_ports:
                    info.append(f"  • 端口 {port}: {service}")
            else:
                info.append(f"\n📭 没有发现开放端口")
            
        except Exception as e:
            info.append(f"\n❌ 端口扫描出错: {str(e)}")
        
        info.append(f"\n⚠️  警告: 端口扫描可能违反安全策略，请谨慎使用!")
        
        return "\n".join(info)
    
    def get_network_details(self) -> str:
        """获取详细网络信息"""
        import psutil
        
        info = []
        info.append("=" * 70)
        info.append("📡 网络详细信息".center(70))
        info.append("=" * 70)
        
        try:
            # 获取网络接口
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            io_counters = psutil.net_io_counters(pernic=True)
            
            info.append(f"\n🔌 网络接口详情:")
            
            for interface, addr_list in addrs.items():
                info.append(f"\n📡 {interface}:")
                
                # 接口状态
                if interface in stats:
                    stat = stats[interface]
                    status_icon = "🟢" if stat.isup else "🔴"
                    info.append(f"  状态: {status_icon} {'已连接' if stat.isup else '未连接'}")
                    if stat.speed > 0:
                        info.append(f"  速度: {stat.speed} Mbps")
                    info.append(f"  MTU: {stat.mtu}")
                    info.append(f"  双工模式: {'全双工' if stat.duplex == 2 else '半双工'}")
                
                # IP地址
                for addr in addr_list:
                    if addr.family == 2:  # AF_INET
                        info.append(f"  IPv4地址: {addr.address}")
                        if addr.netmask:
                            info.append(f"    子网掩码: {addr.netmask}")
                        if addr.broadcast:
                            info.append(f"    广播地址: {addr.broadcast}")
                    elif addr.family == 23:  # AF_INET6:
                        info.append(f"  IPv6地址: {addr.address}")
                    elif addr.family == 17:  # AF_PACKET
                        info.append(f"  MAC地址: {addr.address}")
                
                # IO统计
                if interface in io_counters:
                    io = io_counters[interface]
                    info.append(f"  发送字节: {io.bytes_sent / (1024**2):.2f} MB")
                    info.append(f"  接收字节: {io.bytes_recv / (1024**2):.2f} MB")
                    info.append(f"  发送包数: {io.packets_sent}")
                    info.append(f"  接收包数: {io.packets_recv}")
            
            # 网络连接
            info.append(f"\n🔗 网络连接:")
            try:
                connections = psutil.net_connections(kind='inet')
                listening = [c for c in connections if c.status == 'LISTEN']
                established = [c for c in connections if c.status == 'ESTABLISHED']
                
                info.append(f"  监听连接: {len(listening)}")
                info.append(f"  已建立连接: {len(established)}")
                info.append(f"  总连接数: {len(connections)}")
                
                # 显示部分监听端口
                if listening:
                    info.append(f"\n  📍 监听端口 (前10个):")
                    for conn in listening[:10]:
                        if conn.laddr:
                            port = conn.laddr.port
                            try:
                                service = socket.getservbyport(port)
                            except:
                                service = "未知"
                            info.append(f"    • 端口 {port}: {service}")
                
            except (psutil.AccessDenied, AttributeError):
                info.append("  ⚠️  无法获取连接信息 (需要管理员权限)")
            
            # 路由表
            info.append(f"\n🗺️  路由信息:")
            try:
                import netifaces
                gateways = netifaces.gateways()
                if 'default' in gateways:
                    for family, (gateway, interface, _) in gateways['default'].items():
                        family_name = {netifaces.AF_INET: 'IPv4', 
                                     netifaces.AF_INET6: 'IPv6'}.get(family, family)
                        info.append(f"  默认网关 ({family_name}): {gateway} via {interface}")
            except ImportError:
                info.append("  💡 安装 netifaces 包以获取路由信息")
                info.append("      pip install netifaces")
            
        except Exception as e:
            info.append(f"\n❌ 获取网络信息出错: {str(e)}")
        
        return "\n".join(info)
    
    def check_github_version(self, current_version: str, repo: str = "fastxteam/FastX-Tui") -> Dict:
        """检查GitHub上的最新版本"""
        url = f"https://api.github.com/repos/{repo}/releases/latest"
        
        try:
            # 创建请求对象
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'FastX-Tui')
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=5) as response:
                # 读取并解析响应
                data = json.loads(response.read().decode())
                
                # 提取版本信息
                latest_version = data.get('tag_name', '').lstrip('v')
                release_url = data.get('html_url', '')
                release_notes = data.get('body', '')
                
                # 提取assets信息
                assets = data.get('assets', [])
                asset_list = []
                for asset in assets:
                    asset_list.append({
                        'name': asset.get('name', ''),
                        'browser_download_url': asset.get('browser_download_url', ''),
                        'size': asset.get('size', 0),
                        'content_type': asset.get('content_type', '')
                    })
                
                # 比较版本
                is_update_available = self._compare_versions(current_version, latest_version)
                
                return {
                    'success': True,
                    'current_version': current_version,
                    'latest_version': latest_version,
                    'update_available': is_update_available,
                    'release_url': release_url,
                    'release_notes': release_notes,
                    'assets': asset_list
                }
                
        except urllib.error.URLError as e:
            self.log_error(f"GitHub版本检查失败: 网络错误 - {str(e)}")
            return {
                'success': False,
                'error': f"网络错误: {str(e)}",
                'update_available': False
            }
        except json.JSONDecodeError as e:
            self.log_error(f"GitHub版本检查失败: JSON解析错误 - {str(e)}")
            return {
                'success': False,
                'error': f"JSON解析错误: {str(e)}",
                'update_available': False
            }
        except Exception as e:
            self.log_error(f"GitHub版本检查失败: 未知错误 - {str(e)}")
            return {
                'success': False,
                'error': f"未知错误: {str(e)}",
                'update_available': False
            }
    
    def _compare_versions(self, current: str, latest: str) -> bool:
        """比较版本号，返回是否需要更新"""
        if not current or not latest:
            return False
            
        # 移除前缀v
        current = current.lstrip('v')
        latest = latest.lstrip('v')
        
        # 分割版本号
        current_parts = list(map(int, current.split('.')))
        latest_parts = list(map(int, latest.split('.')))
        
        # 补全版本号长度
        max_len = max(len(current_parts), len(latest_parts))
        current_parts += [0] * (max_len - len(current_parts))
        latest_parts += [0] * (max_len - len(latest_parts))
        
        # 比较版本号
        for current_part, latest_part in zip(current_parts, latest_parts):
            if latest_part > current_part:
                return True
            elif latest_part < current_part:
                return False
        
        return False