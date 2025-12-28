# 自动文档生成

## 概述

FastX-Tui 使用 `mkdocstrings` 插件从 Python 代码生成文档。该插件可以自动提取代码中的文档字符串，并生成结构化的文档页面。

## 配置

`mkdocstrings` 插件已经在 `mkdocs.yml` 中配置好了：

```yaml
plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            show_root_heading: true
            show_source: true
            show_inheritance: true
            show_signature_annotations: true
            signature_crossrefs: true
            separate_signature: true
```

## 使用方法

### 1. 在 Markdown 中引用代码

您可以使用以下语法在 Markdown 文档中引用 Python 代码：

```markdown
::: core.task_manager.TaskManager
```

这将自动生成 `TaskManager` 类的文档，包括：
- 类的文档字符串
- 所有方法和属性
- 继承关系
- 源代码链接

### 2. 自定义文档生成

您可以使用选项自定义文档生成：

```markdown
::: core.task_manager.TaskManager
    options:
        show_root_heading: true
        show_source: false
        show_inheritance: true
        members:
            - create_task
            - get_task_status
            - get_task_result
        exclude_members:
            - _ensure_worker_and_put
            - _worker
```

### 3. 引用特定方法

您可以引用特定的方法：

```markdown
::: core.task_manager.TaskManager.create_task
    options:
        show_source: true
        show_signature_annotations: true
```

## 代码示例

### 引用 TaskManager 类

::: core.task_manager.TaskManager

### 引用 TaskStatus 枚举

::: core.task_manager.TaskStatus

## 文档字符串格式

`mkdocstrings` 支持多种文档字符串格式，FastX-Tui 推荐使用 Google 风格的文档字符串：

```python
def example_function(param1: str, param2: int) -> bool:
    """示例函数
    
    Args:
        param1: 参数1的描述
        param2: 参数2的描述
    
    Returns:
        返回值的描述
    
    Raises:
        ValueError: 当参数无效时引发
    """
    pass
```

## 最佳实践

1. **为所有公共类和方法编写文档字符串**
2. **使用类型提示**
3. **保持文档字符串简洁明了**
4. **使用 Google 风格的文档字符串**
5. **在文档中引用相关代码**
6. **定期更新文档**

## 生成的文档示例

### TaskManager 类

::: core.task_manager.TaskManager
    options:
        show_root_heading: true
        show_source: true
        show_inheritance: true
        members:
            - __init__
            - create_task
            - get_task_status
            - get_task_result
            - cancel_task
            - get_all_tasks
            - delete_task
            - clear_tasks
        show_signature_annotations: true
        signature_crossrefs: true
        separate_signature: true

### Task 数据类

::: core.task_manager.Task
    options:
        show_root_heading: true
        show_source: true
        show_inheritance: true
        show_signature_annotations: true

### ViewManager 类

::: core.view_manager.ViewManager
    options:
        show_root_heading: true
        show_source: true
        show_inheritance: true
        members:
            - __init__
            - register_route
            - register_view
            - navigate
            - back
            - go_home
            - clear_screen
            - render_menu
        show_signature_annotations: true
        signature_crossrefs: true
        separate_signature: true

### View 抽象基类

::: core.view_manager.View
    options:
        show_root_heading: true
        show_source: true
        show_inheritance: true
        show_signature_annotations: true

### ViewRoute 数据类

::: core.view_manager.ViewRoute
    options:
        show_root_heading: true
        show_source: true
        show_signature_annotations: true

## core.plugin_manager 模块文档

### PluginInfo 数据类

::: core.plugin_manager.PluginInfo
    options:
        show_root_heading: true
        show_source: true
        show_signature_annotations: true

### Plugin 抽象基类

::: core.plugin_manager.Plugin
    options:
        show_root_heading: true
        show_source: true
        show_inheritance: true
        members:
            - __init__
            - get_info
            - register
            - initialize
            - cleanup
            - get_binary_path
            - get_resource_path
            - get_manual
            - get_config_schema
            - get_config
            - set_config
            - log_debug
            - log_info
            - log_warning
            - log_error
            - log_critical
        show_signature_annotations: true
        signature_crossrefs: true
        separate_signature: true

### PluginManager 类

::: core.plugin_manager.PluginManager
    options:
        show_root_heading: true
        show_source: true
        show_inheritance: true
        members:
            - __init__
            - discover_plugins
            - load_plugin
            - load_all_plugins
            - register_all_plugins
            - get_plugin
            - list_plugins
            - uninstall_plugin
            - enable_plugin
            - disable_plugin
            - cleanup_all
            - install_plugin_from_github
            - reload_plugin
            - reload_all_plugins
        show_signature_annotations: true
        signature_crossrefs: true
        separate_signature: true

### PluginRepository 类

::: core.plugin_manager.PluginRepository
    options:
        show_root_heading: true
        show_source: true
        show_inheritance: true
        members:
            - __init__
            - get_plugins
            - get_plugin_info_from_github
            - get_plugin_details
            - install_plugin
            - search_plugins
            - get_categories
            - update_plugin
        show_signature_annotations: true
        signature_crossrefs: true
        separate_signature: true
