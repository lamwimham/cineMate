# Issue & PR 标题格式规范指南

> **适用项目**: CineMate
> **版本**: v1.0
> **更新日期**: 2026-04-24

---

## 🎯 核心原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **清晰明确** | 标题要具体，避免模糊 | ❌ 修复bug → ✅ 修复用户登录验证码失效问题 |
| **简洁精炼** | 控制长度，避免冗长 | ❌ 修复了在用户尝试登录时... → ✅ 修复登录验证码提前过期问题 |
| **可搜索** | 使用关键词便于检索 | ❌ 那个问题 → ✅ 支付页面金额显示异常 |

---

## 📋 Issue 标题格式

### 标准格式

```
[类型] 简短描述
[类型][优先级] 简短描述
[类型][模块] 简短描述
[类型][优先级][模块] 简短描述
```

### 类型标签（Type Tags）

| 标签 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `[feat] 添加用户头像上传功能` |
| `fix` | Bug修复 | `[fix] 修复购物车数量计算错误` |
| `docs` | 文档更新 | `[docs] 更新API使用文档` |
| `refactor` | 代码重构 | `[refactor] 重构用户认证模块` |
| `perf` | 性能优化 | `[perf] 优化首页加载速度` |
| `test` | 测试相关 | `[test] 添加单元测试覆盖率` |
| `chore` | 构建/工具 | `[chore] 升级依赖包版本` |
| `style` | 代码格式 | `[style] 统一代码缩进风格` |
| `ci` | CI/CD配置 | `[ci] 添加自动化部署脚本` |

### 优先级标签（可选）

| 标签 | 说明 | 示例 |
|------|------|------|
| `P0` | 🔴 Critical - 阻塞进度 | `[fix][P0] 修复pytest环境问题` |
| `P1` | 🟡 Important - 应完成 | `[test][P1] 生成测试覆盖率报告` |
| `P2` | 🟢 Optional - 可选 | `[docs][P2] 补充使用说明文档` |

### 模块标签（可选）

| 标签 | 说明 | 示例 |
|------|------|------|
| `infra` | 基础设施模块 | `[fix][infra] 修复JobQueue集成问题` |
| `adapter` | 适配器模块 | `[feat][adapter] 实现Kling Provider` |
| `engine` | 引擎模块 | `[refactor][engine] 重构DAG执行逻辑` |
| `agent` | Agent模块 | `[feat][agent] 实现Director Agent` |
| `config` | 配置模块 | `[feat][config] 添加环境变量覆盖` |

---

## 🔧 PR (Pull Request) 标题格式

### Conventional Commits 格式

```
<type>(<scope>): <subject>
```

### Type 类型详解

| Type | 说明 | 版本号变更 |
|------|------|-----------|
| `feat` | 新功能 | ✅ MINOR (v1.2.0 → v1.3.0) |
| `fix` | Bug修复 | ✅ PATCH (v1.2.0 → v1.2.1) |
| `docs` | 文档变更 | ❌ 无 |
| `style` | 代码格式 | ❌ 无 |
| `refactor` | 重构 | ❌ 无 |
| `perf` | 性能优化 | ❌ 无 |
| `test` | 测试相关 | ❌ 无 |
| `chore` | 构建/工具 | ❌ 无 |
| `revert` | 回滚提交 | ✅ PATCH |

### Scope 范围（可选）

指定影响的模块或组件：

```bash
feat(user): add profile editing
feat(payment): implement WeChat Pay
fix(cart): resolve quantity bug
refactor(api): migrate to GraphQL
```

### Subject 规范

| 规则 | 说明 |
|------|------|
| 使用祈使句 | `add` not `added` |
| 首字母小写 | `add` not `Add` |
| 不加句号结尾 | `add feature` not `add feature.` |
| 保持在50字符以内 | 简洁精炼 |

### PR 标题示例

```bash
# ✅ 正确
feat(auth): add password strength validator
fix(cart): resolve duplicate item bug
docs(api): add usage examples

# ❌ 错误
feat(auth): Added password strength validator  # 过去式
feat(auth): Add password strength validator.   # 首字母大写+句号
feat(auth): This PR adds a password strength validator that checks...  # 过长
```

---

## 📊 CineMate 项目实例

### Sprint 2 Day 4 Issues（已更新）

| Issue | 标题 | 助手 | 优先级 |
|-------|------|------|--------|
| #18 | `[fix][P0] 修复Python环境问题 - pytest无法导入networkx` | Hermes + Copaw | 🔴 P0 |
| #19 | `[test][P1] 生成Sprint2测试覆盖率报告` | Claude | 🟡 P1 |
| #20 | `[docs][P1] Sprint2整体代码审查报告` | Copaw | 🟡 P1 |
| #21 | `[feat][P2] 创建Sprint2演示脚本` | Hermes | 🟢 P2 |
| #22 | `[docs][P2] 创建Sprint2演示流程文档` | Hermes | 🟢 P2 |

### PR 标题示例

```bash
# Issue #18 → PR
fix(env): configure project-level venv for pytest
Closes #18

# Issue #19 → PR
test(coverage): generate sprint2 coverage report
Closes #19

# Issue #20 → PR
docs(review): add sprint2 code review report
Closes #20

# Issue #21 → PR
feat(demo): create sprint2 demo script
Closes #21

# Issue #22 → PR
docs(demo): create sprint2 demo guide
Closes #22
```

---

## 🛠️ 自动化工具配置

### Commitlint 配置

```javascript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always', [
      'feat', 'fix', 'docs', 'style', 'refactor',
      'perf', 'test', 'chore', 'revert'
    ]],
    'subject-max-length': [2, 'always', 72]
  }
};
```

### Husky + Commitlint

```json
// package.json
{
  "husky": {
    "hooks": {
      "commit-msg": "commitlint -E HUSKY_GIT_PARAMS"
    }
  }
}
```

---

## 📝 Issue & PR 模板

### Issue 模板

```markdown
## 助手

**分配给**: Hermes / Copaw / Claude / Qwen

---

## [类型][优先级] 简短描述

### 问题描述

[具体描述问题内容]

### 影响范围

[描述影响的功能模块或用户]

### 验收标准

- [ ] 标准1
- [ ] 标准2
- [ ] 标准3

### 交付物

- 文件1
- 文件2

### 预估工时

X小时

### Sprint

Sprint X Day Y
```

### PR 模板

```markdown
## Type of change

- [ ] feat: 新功能
- [ ] fix: Bug修复
- [ ] docs: 文档更新
- [ ] refactor: 重构
- [ ] perf: 性能优化
- [ ] test: 测试
- [ ] chore: 构建/工具

## Description

<type>(<scope>): <subject>

[简要描述变更内容]

## Related Issue

Closes #xxx

## 助手

**开发者**: Hermes / Copaw / Claude

## Checklist

- [ ] 代码符合规范
- [ ] 添加/更新测试
- [ ] 更新文档
- [ ] 本地测试通过
```

---

## 🔄 Issue → PR → Merge 流程

### 流程图

```
┌──────────────┐
│ PM (Qwen)    │
│ 创建 Issue   │
│ 标题:        │
│ [type][P]    │
│ 简短描述     │
│ 分配助手     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 助手         │
│ 开发实现     │
│ 提交 Commit  │
│ 标题:        │
│ type(scope): │
│ subject      │
│ 提交 PR      │
│ 标题:        │
│ type(scope): │
│ subject      │
│ Closes #xxx  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ PM (Qwen)    │
│ Review PR    │
│ 合并 PR      │
│ Issue 自动   │
│ 关闭         │
└──────────────┘
```

---

## ⚠️ 常见错误对照

| ❌ 错误 | ✅ 正确 |
|---------|---------|
| `Added new feature` | `feat: add new feature` |
| `Fixed bug in login` | `fix(auth): resolve login bug` |
| `Update README.md` | `docs: update README` |
| `Some changes` | `refactor(api): improve error handling` |
| `P0: Fix bug` | `[fix][P0] 修复bug描述` |

---

## 💡 记忆口诀

```
Issue要清晰，PR要规范，
Commit要一致，自动化来帮忙！

Issue: [类型][优先级] 简短描述
PR:    type(scope): subject + Closes #xxx
```

---

## 📚 参考资源

- [Conventional Commits 规范](https://www.conventionalcommits.org/)
- [Angular Commit Guidelines](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit)
- [Commitlint](https://commitlint.js.org/)
- [Standard Version](https://github.com/conventional-changelog/standard-version)

---

**签名**: PM (Qwen)
**日期**: 2026-04-24