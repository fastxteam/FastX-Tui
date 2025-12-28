#!/usr/bin/env python3
"""
任务管理器模块 - 管理异步任务队列
"""
import asyncio
import uuid
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"  # 等待执行
    RUNNING = "running"  # 正在执行
    COMPLETED = "completed"  # 执行完成
    FAILED = "failed"  # 执行失败
    CANCELLED = "cancelled"  # 已取消


@dataclass
class Task:
    """任务数据类"""
    id: str
    name: str
    description: str
    command_type: str
    command: Optional[str] = None
    python_func: Optional[Callable] = None
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    execution_time: Optional[float] = None
    is_viewed: bool = False  # 是否已查看结果


class TaskManager:
    """任务管理器 - 管理异步任务队列"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}  # 任务字典，key为任务ID
        self.task_queue: asyncio.Queue = asyncio.Queue()  # 任务队列
        self.is_running = False  # 任务管理器是否正在运行
        self.worker_task: Optional[asyncio.Task] = None  # 工作线程任务
    
    def start(self):
        """启动任务管理器 - 标记为运行状态，但不立即创建工作线程"""
        if not self.is_running:
            self.is_running = True
            # 工作线程将在第一个任务添加时创建
    
    async def ensure_worker_running(self):
        """确保工作线程正在运行"""
        if self.is_running and not self.worker_task:
            self.worker_task = asyncio.create_task(self._worker())
    
    async def stop(self):
        """停止任务管理器"""
        if self.is_running:
            self.is_running = False
            # 向队列中添加一个None值，用于终止工作线程
            await self.task_queue.put(None)
            if self.worker_task:
                await self.worker_task
                self.worker_task = None
    
    async def _worker(self):
        """工作线程 - 处理任务队列"""
        while self.is_running:
            try:
                task_id = await self.task_queue.get()
                if task_id is None:  # 终止信号
                    break
                
                task = self.tasks.get(task_id)
                if task:
                    await self._execute_task(task)
            except Exception as e:
                print(f"任务工作线程错误: {str(e)}")
    
    async def _execute_task(self, task: Task):
        """执行单个任务"""
        task.status = TaskStatus.RUNNING
        task.start_time = time.time()
        
        try:
            if task.python_func:
                # 执行Python函数
                result = task.python_func(*task.args, **task.kwargs)
                # 检查是否是协程对象，如果是则等待执行
                if hasattr(result, '__await__'):
                    result = await result
                task.result = str(result)
            elif task.command:
                # 执行Shell命令
                import subprocess
                import sys
                
                # 异步执行shell命令
                process = await asyncio.create_subprocess_shell(
                    task.command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding='gbk' if sys.platform == 'win32' else 'utf-8'
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    task.result = stdout
                else:
                    task.error = f"命令执行失败 (返回码: {process.returncode}): {stderr}"
                    task.status = TaskStatus.FAILED
                    return
            
            task.status = TaskStatus.COMPLETED
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
        finally:
            task.end_time = time.time()
            if task.start_time:
                task.execution_time = task.end_time - task.start_time
    
    def add_task(
        self,
        name: str,
        description: str,
        command_type: str,
        command: Optional[str] = None,
        python_func: Optional[Callable] = None,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None
    ) -> str:
        """添加任务到队列
        
        Args:
            name: 任务名称
            description: 任务描述
            command_type: 命令类型 (python 或 shell)
            command: Shell命令字符串（如果是shell类型）
            python_func: Python函数（如果是python类型）
            args: 函数参数列表
            kwargs: 函数关键字参数
            
        Returns:
            任务ID
        """
        task_id = str(uuid.uuid4())
        
        task = Task(
            id=task_id,
            name=name,
            description=description,
            command_type=command_type,
            command=command,
            python_func=python_func,
            args=args or [],
            kwargs=kwargs or {}
        )
        
        self.tasks[task_id] = task
        
        # 确保工作线程正在运行
        asyncio.create_task(self._ensure_worker_and_put(task_id))
        
        return task_id
    
    async def _ensure_worker_and_put(self, task_id):
        """确保工作线程运行并将任务放入队列"""
        # 确保工作线程正在运行
        await self.ensure_worker_running()
        # 将任务ID放入队列
        await self.task_queue.put(task_id)
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """根据ID获取任务"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """获取所有任务，按创建时间排序"""
        # 转换为列表并返回
        return list(self.tasks.values())
    
    def get_pending_tasks(self) -> List[Task]:
        """获取等待执行的任务"""
        return [task for task in self.tasks.values() if task.status == TaskStatus.PENDING]
    
    def get_running_tasks(self) -> List[Task]:
        """获取正在执行的任务"""
        return [task for task in self.tasks.values() if task.status == TaskStatus.RUNNING]
    
    def get_completed_tasks(self) -> List[Task]:
        """获取已完成的任务"""
        return [task for task in self.tasks.values() if task.status == TaskStatus.COMPLETED]
    
    def get_failed_tasks(self) -> List[Task]:
        """获取执行失败的任务"""
        return [task for task in self.tasks.values() if task.status == TaskStatus.FAILED]
    
    def mark_task_as_viewed(self, task_id: str):
        """标记任务结果为已查看"""
        if task_id in self.tasks:
            self.tasks[task_id].is_viewed = True
    
    def clear_completed_tasks(self):
        """清理已完成的任务"""
        self.tasks = {k: v for k, v in self.tasks.items() 
                     if v.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]}
    
    def get_task_count(self) -> Dict[str, int]:
        """获取各状态任务数量"""
        return {
            "total": len(self.tasks),
            "pending": len(self.get_pending_tasks()),
            "running": len(self.get_running_tasks()),
            "completed": len(self.get_completed_tasks()),
            "failed": len(self.get_failed_tasks())
        }
