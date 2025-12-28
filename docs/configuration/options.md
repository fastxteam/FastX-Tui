# 配置项说明

## 概述

本文档详细介绍了 FastX-Tui 的配置项，包括外观设置、行为设置、插件设置和高级设置。

## 配置文件格式

FastX-Tui 使用 YAML 格式的配置文件，配置项采用分层结构。

## 配置项列表

### 1. 外观设置 (appearance)

| 配置项 | 类型 | 默认值 | 描述 |
|-------|------|--------|------|
| `theme` | `str` | `"default"` | 应用主题，支持 `default`、`dark`、`light` |
| `color_scheme` | `str` | `"default"` | 颜色方案，支持 `default`、`cyberpunk`、`retro` |
| `font_size` | `int` | `12` | 字体大小，范围 8-24 |
| `animation_enabled` | `bool` | `true` | 是否启用动画效果 |
| `compact_mode` | `bool` | `false` | 是否启用紧凑布局 |
| `show_icons` | `bool` | `true` | 是否显示图标 |
| `icon_style` | `str` | `"emoji"` | 图标样式，支持 `emoji`、`ascii` |

### 2. 行为设置 (behavior)

| 配置项 | 类型 | 默认值 | 描述 |
|-------|------|--------|------|
| `startup_view` | `str` | `"main_menu"` | 默认启动视图 |
| `auto_save_config` | `bool` | `true` | 是否自动保存配置 |
| `confirm_dangerous_actions` | `bool` | `true` | 是否显示危险操作确认提示 |
| `default_log_level` | `str` | `"INFO"` | 默认日志级别 |
| `auto_clear_logs` | `bool` | `false` | 是否自动清除旧日志 |
| `log_retention_days` | `int` | `7` | 日志保留天数 |
| `show_splash_screen` | `bool` | `true` | 是否显示启动画面 |
| `splash_screen_duration` | `int` | `2000` | 启动画面显示时间（毫秒） |

### 3. 插件设置 (plugins)

| 配置项 | 类型 | 默认值 | 描述 |
|-------|------|--------|------|
| `plugin_dir` | `str` | 系统默认位置 | 插件存放目录 |
| `auto_update_plugins` | `bool` | `false` | 是否自动更新插件 |
| `plugin_sources` | `list[str]` | `["https://github.com/FastXTeam/FastX-Tui-Plugins"]` | 插件源列表 |
| `enabled_plugins` | `list[str]` | `[]` | 启用的插件列表 |
| `disabled_plugins` | `list[str]` | `[]` | 禁用的插件列表 |
| `sandbox_mode` | `bool` | `false` | 是否启用插件沙箱模式 |

### 4. 高级设置 (advanced)

| 配置项 | 类型 | 默认值 | 描述 |
|-------|------|--------|------|
| `debug_mode` | `bool` | `false` | 是否启用调试模式 |
| `use_async_tasks` | `bool` | `true` | 是否使用异步任务执行 |
| `task_queue_size` | `int` | `100` | 任务队列大小 |
| `worker_threads` | `int` | 系统CPU核心数 | 工作线程数量 |
| `performance_monitoring` | `bool` | `false` | 是否启用性能监控 |
| `max_concurrent_downloads` | `int` | `3` | 最大并发下载数 |
| `network_timeout` | `int` | `30` | 网络超时时间（秒） |
| `cache_dir` | `str` | 系统默认位置 | 缓存目录 |
| `max_cache_size` | `int` | `100` | 最大缓存大小（MB） |

### 5. 键盘设置 (keyboard)

| 配置项 | 类型 | 默认值 | 描述 |
|-------|------|--------|------|
| `key_bindings` | `dict` | 系统默认键位 | 自定义键位映射 |
| `enable_key_repeat` | `bool` | `true` | 是否启用按键重复 |
| `key_repeat_delay` | `int` | `500` | 按键重复延迟（毫秒） |
| `key_repeat_rate` | `int` | `30` | 按键重复速率（毫秒/次） |

### 6. 语言设置 (language)

| 配置项 | 类型 | 默认值 | 描述 |
|-------|------|--------|------|
| `language` | `str` | `"zh_CN"` | 应用语言，支持 `zh_CN`、`en_US`、`ja_JP`、`ko_KR` |
| `auto_detect_language` | `bool` | `true` | 是否自动检测系统语言 |

## 配置文件示例

```yaml
# 外观设置
appearance:
  theme: "default"
  color_scheme: "default"
  font_size: 12
  animation_enabled: true
  compact_mode: false
  show_icons: true
  icon_style: "emoji"

# 行为设置
behavior:
  startup_view: "main_menu"
  auto_save_config: true
  confirm_dangerous_actions: true
  default_log_level: "INFO"
  auto_clear_logs: false
  log_retention_days: 7
  show_splash_screen: true
  splash_screen_duration: 2000

# 插件设置
plugins:
  plugin_dir: "plugins"
  auto_update_plugins: false
  plugin_sources: ["https://github.com/FastXTeam/FastX-Tui-Plugins"]
  enabled_plugins: []
  disabled_plugins: []
  sandbox_mode: false

# 高级设置
advanced:
  debug_mode: false
  use_async_tasks: true
  task_queue_size: 100
  worker_threads: 4
  performance_monitoring: false
  max_concurrent_downloads: 3
  network_timeout: 30
  cache_dir: ".cache"
  max_cache_size: 100

# 键盘设置
keyboard:
  key_bindings: {}
  enable_key_repeat: true
  key_repeat_delay: 500
  key_repeat_rate: 30

# 语言设置
language:
  language: "zh_CN"
  auto_detect_language: true
```

## 环境变量覆盖

您可以使用环境变量覆盖配置项，环境变量的命名规则是：

1. 将配置项路径转换为大写
2. 使用下划线替代点
3. 前缀为 `FASTX_TUI_`

例如，要覆盖 `appearance.theme` 配置项，可以设置：

```bash
FASTX_TUI_APPEARANCE_THEME=dark fastx-tui
```

## 命令行参数

您可以使用命令行参数临时覆盖配置项：

```bash
fastx-tui --config appearance.theme=dark --config behavior.debug_mode=true
```

## 配置验证

FastX-Tui 会自动验证配置的有效性：

- 检查配置项类型是否正确
- 检查配置项值是否在允许范围内
- 检查配置项依赖关系
- 检查配置项兼容性

如果配置无效，FastX-Tui 会显示错误信息，并使用默认值代替无效配置。

## 下一步

- 了解 [高级配置](advanced.md)
- 学习 [开发指南](../development/environment.md)
