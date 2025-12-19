#!/usr/bin/env python3
"""
FastX TUI - 统一视图架构版本
"""
import os
import sys
from core.app_manager import AppManager

def main():
    """主函数"""
    # 创建应用管理器实例
    app_manager = AppManager()
    
    # 初始化应用
    if not app_manager.initialize():
        sys.exit(1)
    
    # 启动应用主循环
    try:
        app_manager.start_main_loop()
    except KeyboardInterrupt:
        # 优雅处理中断
        print("\n程序已中断")
    except Exception as e:
        print(f"\n程序发生错误: {str(e)}")
    finally:
        # 清理资源
        app_manager.cleanup()

if __name__ == "__main__":
    main()
