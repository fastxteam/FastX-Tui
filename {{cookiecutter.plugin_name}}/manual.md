# {{ cookiecutter.plugin_display_name }}

## 概述

{{ cookiecutter.plugin_description }}

## 功能特点

- 示例功能 1
- 示例功能 2
- 示例功能 3

## 安装

```bash
pip install -e .
```

## 使用方法

### 命令说明

1. **示例命令**
   - 描述：执行示例命令
   - 用法：在菜单中选择 `{{ cookiecutter.plugin_display_name }}` → `示例命令`
   - 功能：演示插件的基本功能

## 配置

### 配置项说明

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| example_config | string | default_value | 示例配置项 |

### 配置方法

1. 在 FastX-Tui 主菜单中选择 `配置`
2. 选择 `插件配置`
3. 选择 `{{ cookiecutter.plugin_display_name }}`
4. 修改配置项并保存

## 开发

### 项目结构

```
{{ cookiecutter.plugin_name }}/
├── {{ cookiecutter.plugin_name }}_business.py  # 业务逻辑
├── fastx_tui_plugin.py                          # 插件接口
├── manual.md                                    # 插件手册
├── config_schema.json                           # 配置 schema
├── pyproject.toml                               # 项目配置
└── README.md                                    # 项目说明
```

### 扩展开发

1. 在 `{{ cookiecutter.plugin_name }}_business.py` 中添加新的业务逻辑
2. 在 `fastx_tui_plugin.py` 中注册新的命令
3. 更新 `manual.md` 文档
4. 更新 `config_schema.json` 配置 schema

## 许可证

{{ cookiecutter.license }}
