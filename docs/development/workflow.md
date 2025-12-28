# 开发流程

## 概述

本文档介绍了 FastX-Tui 的开发流程，包括分支管理、代码规范、提交规范和发布流程。

## 分支管理

FastX-Tui 使用 Git 进行版本控制，采用以下分支管理策略：

### 1. 主分支 (`main`)

- 包含稳定的、已发布的代码
- 只有经过充分测试的代码才能合并到主分支
- 每次合并到主分支都会触发版本号更新

### 2. 开发分支 (`develop`)

- 包含下一个版本的开发代码
- 所有功能开发和 bug 修复都从开发分支创建
- 定期合并到主分支发布新版本

### 3. 功能分支 (`feature/`)

- 用于开发新功能
- 从 `develop` 分支创建
- 命名格式：`feature/feature-name`
- 开发完成后合并回 `develop` 分支

### 4. Bug 修复分支 (`bugfix/`)

- 用于修复 bug
- 从 `develop` 分支创建（如果 bug 也存在于主分支，从 `main` 分支创建）
- 命名格式：`bugfix/bug-description`
- 修复完成后合并回 `develop` 分支（如果从 `main` 分支创建，还需合并回 `main` 分支）

### 5. 发布分支 (`release/`)

- 用于准备发布新版本
- 从 `develop` 分支创建
- 命名格式：`release/vx.y.z`
- 仅用于版本号更新和发布前的最终测试
- 发布完成后合并回 `main` 和 `develop` 分支

### 6. 热修复分支 (`hotfix/`)

- 用于紧急修复已发布版本的 bug
- 从 `main` 分支创建
- 命名格式：`hotfix/vx.y.z`
- 修复完成后合并回 `main` 和 `develop` 分支

## 代码规范

FastX-Tui 遵循以下代码规范：

### 1. Python 代码规范

- 遵循 PEP 8 规范
- 使用 Ruff 进行代码检查和格式化
- 使用类型提示
- 编写详细的文档字符串

### 2. 文档字符串规范

使用 Google 风格的文档字符串：

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

### 3. 命名规范

- 类名：使用驼峰命名法，首字母大写
- 函数名和变量名：使用蛇形命名法，全小写，单词之间用下划线分隔
- 常量：全大写，单词之间用下划线分隔
- 模块名：全小写，单词之间用下划线分隔

### 4. 注释规范

- 代码应该自解释，减少不必要的注释
- 使用中文注释
- 注释应该解释代码的意图，而不是代码本身
- 复杂的算法和逻辑需要详细的注释

## 提交规范

FastX-Tui 遵循 Conventional Commits 规范，提交信息格式如下：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### 1. Type 类型

- `feat`：新功能
- `fix`：bug 修复
- `docs`：文档更新
- `style`：代码格式调整
- `refactor`：代码重构
- `perf`：性能优化
- `test`：测试用例更新
- `build`：构建系统或依赖项更新
- `ci`：CI 配置更新
- `chore`：其他不影响代码功能的更新
- `revert`：回滚之前的提交

### 2. Scope（可选）

指定提交影响的范围，例如：

```
feat(menu): 添加新的菜单功能
fix(config): 修复配置文件解析错误
```

### 3. Description

简洁明了的描述提交内容，使用祈使句，首字母小写，不使用句号结尾。

### 4. Body（可选）

详细描述提交内容，包括为什么修改、修改了什么、如何修改等。

### 5. Footer（可选）

包含额外的信息，例如关闭的 Issue、Breaking Changes 等：

```
fix: 修复登录功能

closes #123

BREAKING CHANGE: 登录接口参数变更
```

## 开发工作流

### 1. 功能开发流程

1. **创建功能分支**：
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/feature-name
   ```

2. **开发功能**：
   - 编写代码
   - 添加测试用例
   - 运行代码检查
   - 运行测试

3. **提交代码**：
   ```bash
   git add .
   git commit -m "feat: 描述功能"
   ```

4. **推送分支**：
   ```bash
   git push -u origin feature/feature-name
   ```

5. **创建 Pull Request**：
   - 在 GitHub 上创建 Pull Request
   - 选择 `develop` 作为目标分支
   - 添加详细的描述
   - 等待代码审查

6. **代码审查**：
   - 修复审查中发现的问题
   - 重新提交代码

7. **合并代码**：
   - 代码审查通过后，合并到 `develop` 分支
   - 删除功能分支

### 2. Bug 修复流程

1. **创建 Bug 修复分支**：
   ```bash
   git checkout develop
   git pull
   git checkout -b bugfix/bug-description
   ```

2. **修复 Bug**：
   - 定位并修复 Bug
   - 添加测试用例验证修复
   - 运行代码检查
   - 运行测试

3. **提交代码**：
   ```bash
   git add .
   git commit -m "fix: 描述 Bug 修复"
   ```

4. **推送分支**：
   ```bash
   git push -u origin bugfix/bug-description
   ```

5. **创建 Pull Request**：
   - 在 GitHub 上创建 Pull Request
   - 选择 `develop` 作为目标分支
   - 添加详细的描述和相关 Issue
   - 等待代码审查

6. **代码审查**：
   - 修复审查中发现的问题
   - 重新提交代码

7. **合并代码**：
   - 代码审查通过后，合并到 `develop` 分支
   - 如果 Bug 也存在于主分支，从 `main` 分支创建新的 Bug 修复分支，重复修复过程，合并到 `main` 分支
   - 删除 Bug 修复分支

## 发布流程

1. **创建发布分支**：
   ```bash
   git checkout develop
   git pull
   git checkout -b release/vx.y.z
   ```

2. **更新版本号**：
   - 更新 `pyproject.toml` 中的版本号
   - 更新 `README.md` 中的版本信息
   - 更新 `core/version.py` 中的版本号
   - 提交版本号更新
   ```bash
   git add .
   git commit -m "chore: 更新版本号到 vx.y.z"
   ```

3. **运行最终测试**：
   ```bash
   # 运行代码检查
   uv run ruff check .
   
   # 运行测试
   uv run pytest
   
   # 构建包
   uv build
   ```

4. **合并到主分支**：
   ```bash
   git checkout main
   git pull
   git merge release/vx.y.z --no-ff
   git tag vx.y.z
   ```

5. **合并回开发分支**：
   ```bash
   git checkout develop
   git merge release/vx.y.z --no-ff
   ```

6. **推送代码和标签**：
   ```bash
   git push origin main develop
   git push origin --tags
   ```

7. **删除发布分支**：
   ```bash
   git branch -d release/vx.y.z
   git push origin --delete release/vx.y.z
   ```

8. **发布到 PyPI**：
   ```bash
   uv publish
   ```

## 代码审查流程

1. **创建 Pull Request**：
   - 添加详细的描述
   - 关联相关的 Issue
   - 选择合适的 reviewer

2. **Reviewer 审查**：
   - 检查代码是否符合规范
   - 检查代码质量和可读性
   - 检查是否有足够的测试用例
   - 检查是否有性能问题
   - 提供反馈和建议

3. **作者修改**：
   - 根据审查意见修改代码
   - 重新提交代码

4. **再次审查**：
   - Reviewer 再次审查修改后的代码
   - 如果通过，批准 Pull Request

5. **合并代码**：
   - 合并到目标分支
   - 删除功能分支

## 持续集成

FastX-Tui 使用 GitHub Actions 进行持续集成：

- **代码检查**：每次提交和 Pull Request 都运行 Ruff 检查
- **测试**：每次提交和 Pull Request 都运行 pytest
- **构建**：每次发布都构建包
- **发布**：发布到 PyPI

## 开发工具

- **代码编辑器**：VS Code 或 PyCharm
- **代码检查**：Ruff
- **测试框架**：pytest
- **包管理器**：uv
- **CI/CD**：GitHub Actions
- **文档生成**：MkDocs

## 下一步

- 学习 [贡献指南](contributing.md)
- 开始 [开发插件](../plugin_development/guide.md)
