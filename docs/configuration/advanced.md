# 高级配置

## 概述

本文档介绍了 FastX-Tui 的高级配置选项，适合高级用户和开发者使用。这些配置选项可以调整 FastX-Tui 的底层行为和性能。

## 异步任务配置

### 1. 启用/禁用异步任务

```yaml
advanced:
  use_async_tasks: true
```

- `true`：启用异步任务执行，命令将在后台执行，不会阻塞界面
- `false`：禁用异步任务执行，命令将在主线程执行，可能会阻塞界面

### 2. 调整任务队列大小

```yaml
advanced:
  task_queue_size: 100
```

任务队列大小决定了可以同时排队的任务数量。如果队列已满，新的任务将被拒绝。

### 3. 调整工作线程数量

```yaml
advanced:
  worker_threads: 4
```

工作线程数量决定了可以同时执行的任务数量。默认值为系统 CPU 核心数。

## 调试模式

### 1. 启用调试模式

```yaml
advanced:
  debug_mode: true
```

启用调试模式后，FastX-Tui 将：
- 输出更详细的日志
- 显示调试信息
- 启用性能分析
- 显示额外的错误信息

### 2. 使用环境变量启用调试模式

```bash
FASTX_TUI_ADVANCED_DEBUG_MODE=true fastx-tui
```

### 3. 使用命令行参数启用调试模式

```bash
fastx-tui --debug
```

## 性能监控

### 1. 启用性能监控

```yaml
advanced:
  performance_monitoring: true
```

启用性能监控后，FastX-Tui 将：
- 记录各个组件的执行时间
- 显示性能统计信息
- 生成性能报告

### 2. 查看性能报告

1. 按 `S` 键打开设置界面
2. 选择「高级设置」
3. 选择「性能监控」
4. 查看性能报告

## 网络配置

### 1. 调整网络超时时间

```yaml
advanced:
  network_timeout: 30
```

网络超时时间决定了网络请求的最大等待时间（秒）。

### 2. 调整最大并发下载数

```yaml
advanced:
  max_concurrent_downloads: 3
```

最大并发下载数决定了可以同时进行的下载操作数量。

## 缓存配置

### 1. 调整缓存目录

```yaml
advanced:
  cache_dir: "/path/to/cache"
```

### 2. 调整最大缓存大小

```yaml
advanced:
  max_cache_size: 100
```

最大缓存大小决定了缓存目录的最大容量（MB）。当缓存超过此大小，旧的缓存文件将被自动清理。

## 插件沙箱模式

### 1. 启用插件沙箱模式

```yaml
plugins:
  sandbox_mode: true
```

启用沙箱模式后，插件将在受限环境中运行，限制对系统资源的访问。

### 2. 沙箱模式限制

沙箱模式下，插件将受到以下限制：
- 无法访问系统文件系统
- 无法执行系统命令
- 无法访问网络
- 无法修改系统配置

## 自定义键位映射

### 1. 配置自定义键位

```yaml
keyboard:
  key_bindings:
    "main_menu":
      "q": "quit"
      "h": "help"
    "task_list":
      "d": "delete_task"
      "c": "clear_tasks"
```

### 2. 键位映射格式

键位映射使用以下格式：

```yaml
keyboard:
  key_bindings:
    "view_id":
      "key": "action"
```

- `view_id`：视图 ID
- `key`：按键
- `action`：执行的操作

## 高级日志配置

### 1. 配置日志格式

```yaml
logging:
  format: "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"
```

### 2. 配置日志旋转

```yaml
logging:
  rotation: "1 day"
  retention: "7 days"
  compression: "zip"
```

- `rotation`：日志文件旋转策略，支持 "1 day"、"10 MB" 等
- `retention`：日志文件保留时间
- `compression`：日志压缩格式，支持 "zip"、"gz" 等

## 开发模式

### 1. 启用开发模式

```bash
FASTX_TUI_ADVANCED_DEBUG_MODE=true FASTX_TUI_ADVANCED_PERFORMANCE_MONITORING=true fastx-tui
```

开发模式启用了调试模式和性能监控，适合开发者使用。

### 2. 热重载

开发模式支持热重载，当代码文件发生变化时，FastX-Tui 将自动重新加载。

## 高级插件配置

### 1. 配置插件依赖解析

```yaml
plugins:
  resolve_dependencies: true
```

启用依赖解析后，插件管理器将自动解析和安装插件依赖。

### 2. 配置插件加载顺序

```yaml
plugins:
  load_order: ["CorePlugin", "ExamplePlugin"]
```

插件加载顺序决定了插件的初始化顺序。

## 性能优化建议

1. **对于低配置系统**：
   - 禁用动画效果
   - 减少工作线程数量
   - 启用紧凑模式
   - 减少日志级别

2. **对于高配置系统**：
   - 增加工作线程数量
   - 增加任务队列大小
   - 启用性能监控

3. **对于网络环境较差的系统**：
   - 增加网络超时时间
   - 减少最大并发下载数
   - 禁用自动更新插件

## 故障排除

### 1. 配置文件损坏

如果配置文件损坏，可以删除配置文件，FastX-Tui 会自动重新创建默认配置文件。

### 2. 配置项无效

如果某个配置项无效，FastX-Tui 会显示错误信息，并使用默认值代替。

### 3. 性能问题

如果遇到性能问题，可以：
- 启用性能监控
- 查看性能报告
- 调整工作线程数量
- 调整任务队列大小
- 禁用不必要的功能

## 下一步

- 学习 [开发指南](../development/environment.md)
- 了解 [插件开发](../plugin_development/guide.md)
