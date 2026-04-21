# 📝 Issue & PR 标题格式规范指南

> **版本**: 1.0  
> **日期**: 2026-04-24  
> **状态**: 团队采纳  
> **适用范围**: CineMate 项目全员 (hermes, copaw, claude)

---

## 🎯 核心原则

### 1. 清晰明确 (Clear & Specific)
- ❌ 模糊：修复 bug
- ✅ 明确：修复用户登录时验证码失效问题

### 2. 简洁精炼 (Concise)
- ❌ 冗长：修复了在用户尝试登录系统时出现的验证码在某些情况下会提前过期导致无法正常登录的 bug
- ✅ 精炼：修复登录验证码提前过期问题

### 3. 可搜索 (Searchable)
- ❌ 难搜索：那个问题
- ✅ 易搜索：支付页面金额显示异常

---

## 📋 Issue 标题格式

### 标准格式
```
[类型] 简短描述
```

### 类型标签（Type Tags）

| 标签 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `[feat] 添加用户头像上传功能` |
| `fix` | Bug 修复 | `[fix] 修复购物车数量计算错误` |
| `docs` | 文档更新 | `[docs] 更新 API 使用文档` |
| `refactor` | 代码重构 | `[refactor] 重构用户认证模块` |
| `perf` | 性能优化 | `[perf] 优化首页加载速度` |
| `test` | 测试相关 | `[test] 添加单元测试覆盖率` |
| `chore` | 构建/工具 | `[chore] 升级依赖包版本` |
| `style` | 代码格式 | `[style] 统一代码缩进风格` |
| `ci` | CI/CD 配置 | `[ci] 添加自动化部署脚本` |

### 优先级标签（可选）
```
[feat][P0] 实现用户注册功能
[fix][P1] 修复支付失败问题
[docs][P2] 补充使用说明文档
```

### 模块标签（可选）
```
[feat][用户模块] 添加第三方登录
[fix][支付模块] 修复退款流程异常
[perf][性能优化] 优化数据库查询
```

---

## 🔧 PR (Pull Request) 标题格式

### 推荐格式：Conventional Commits
```
<type>(<scope>): <subject>
```

### 完整示例

#### 基础格式
```
feat(auth): add OAuth2 login support
```

#### 带 BREAKING CHANGE
```
refactor(api): migrate to GraphQL

BREAKING CHANGE: REST API endpoints removed
```

#### 带 Issue 关联
```
fix(cart): resolve quantity calculation bug

Closes #123
```

### Type 类型详解

| Type | 说明 | 是否触发版本号变更 |
|------|------|-------------------|
| `feat` | 新功能 | ✅ MINOR (v1.2.0 → v1.3.0) |
| `fix` | Bug 修复 | ✅ PATCH (v1.2.0 → v1.2.1) |
| `docs` | 文档变更 | ❌ 无 |
| `style` | 代码格式 | ❌ 无 |
| `refactor` | 重构 | ❌ 无 |
| `perf` | 性能优化 | ❌ 无 |
| `test` | 测试相关 | ❌ 无 |
| `chore` | 构建/工具 | ❌ 无 |
| `revert` | 回滚提交 | ✅ PATCH |

### Scope 范围（可选）
指定影响的模块或组件：
```
feat(user): add profile editing
feat(payment): implement WeChat Pay
fix(cart): resolve quantity bug
refactor(api): migrate to GraphQL
```

### Subject 规范
- ✅ 使用祈使句（imperative mood）
- ✅ 首字母小写
- ✅ 不加句号结尾
- ✅ 保持在 50 字符以内

#### 示例对比

| ✅ 正确 | ❌ 错误 |
|--------|--------|
| `feat(auth): add password strength validator` | `feat(auth): Added password strength validator` (过去式) |
| `fix(cart): resolve duplicate item bug` | `feat(auth): Add password strength validator.` (首字母大写 + 句号) |
| | `feat(auth): This PR adds a password strength validator that checks...` (过长) |

---

## 📊 实际场景示例

### 场景 1：新功能开发
```
Issue 标题：[feat] 实现用户收藏功能
PR 标题：feat(favorites): implement user favorites system
Commit:   feat(favorites): add API endpoints for favorites
          feat(favorites): add UI components for favorites list
```

### 场景 2：Bug 修复
```
Issue 标题：[fix] 修复订单状态显示错误
PR 标题：fix(order): correct order status display logic
Commit:   fix(order): fix status mapping in order service
          test(order): add test case for status display
```

### 场景 3：性能优化
```
Issue 标题：[perf] 优化商品列表加载速度
PR 标题：perf(product): optimize product list query
Commit:   perf(product): add database index on category
          perf(product): implement pagination caching
```

### 场景 4：文档更新
```
Issue 标题：[docs] 补充 API 使用示例
PR 标题：docs(api): add usage examples for auth endpoints
Commit:   docs(api): add auth examples
          docs(api): update README with new examples
```

### 场景 5：Sprint 任务
```
Issue 标题：[feat][P0] 实现 Provider 适配器基础架构
PR 标题：feat(adapters): add BaseVideoProvider abstract class

Issue 标题：[test][P1] 添加 Provider 单元测试
PR 标题：test(adapters): add unit tests for KlingProvider
```

---

## 🛠️ 自动化检查

### Commit Message 检查清单

提交前自检：
- [ ] 使用 `<type>(<scope>): <subject>` 格式
- [ ] type 在允许列表中 (feat/fix/docs/style/refactor/perf/test/chore/revert)
- [ ] subject 使用祈使句、首字母小写、无句号
- [ ] subject 长度 ≤ 50 字符
- [ ] 如有 Issue 关联，添加 `Closes #xxx`

### PR 描述模板

```markdown
## Type of Change
- [ ] feat: 新功能
- [ ] fix: Bug 修复
- [ ] docs: 文档更新
- [ ] refactor: 重构
- [ ] perf: 性能优化
- [ ] test: 测试
- [ ] chore: 构建/工具

## Description
[简要描述变更内容]

## Related Issue
Closes #xxx

## Checklist
- [ ] 代码符合规范
- [ ] 添加/更新测试
- [ ] 更新文档
- [ ] 本地测试通过
```

---

## 📈 版本号自动生成

### 使用 standard-version

```bash
# 安装
npm install -g standard-version

# 自动生成 CHANGELOG 和版本号
standard-version
```

### 输出示例
```
v1.2.0
  feat(auth): add OAuth2 login
  fix(cart): resolve quantity bug
  docs(api): update examples
```

---

## ⚠️ 常见错误

| ❌ 错误 | ✅ 正确 |
|--------|--------|
| `Added new feature` | `feat: add new feature` |
| `Fixed bug in login` | `fix(auth): resolve login bug` |
| `Update README.md` | `docs: update README` |
| `Some changes` | `refactor(api): improve error handling` |
| `feat: 这是一个很长很长很长的描述，超过了 72 个字符限制` | `feat: improve error handling in API` |

---

## 🎨 CineMate 团队定制

### Git 提交规范

```
<type>(<module>): <subject>

Type: feat, fix, docs, style, refactor, perf, test, chore, revert
Module: adapters, agents, config, core, engine, infra, skills, tests, docs
```

### 示例
```
feat(adapters): add BaseVideoProvider abstract class
fix(infra): resolve Redis connection timeout issue
docs(adr): add ADR-003 provider adapter architecture
test(adapters): add unit tests for KlingProvider
chore(deps): upgrade pydantic to v2.0
```

### Git 配置（可选）

创建 `.gitmessage` 模板：
```
<type>(<scope>): <subject>

# Type: feat, fix, docs, style, refactor, perf, test, chore, revert
# Scope: adapters, agents, config, core, engine, infra, skills, tests, docs
# Subject: 祈使句，首字母小写，无句号，≤50 字符

# 示例:
# feat(adapters): add BaseVideoProvider abstract class
```

配置 Git 使用模板：
```bash
git config commit.template .gitmessage
```

---

## 💡 总结口诀

> **Issue 要清晰，PR 要规范，Commit 要一致，自动化来帮忙！**

### 推荐流程

1. **创建 Issue**: `[类型][模块] 简短描述`
2. **开发提交**: `<type>(<scope>): <subject>`
3. **提交 PR**: `<type>(<scope>): <subject>` + `Closes #xxx`
4. **自动化检查**: Commitlint + Husky
5. **版本发布**: Standard Version 自动生成

---

## 📚 参考资源

- [Conventional Commits 规范](https://www.conventionalcommits.org/)
- [Angular Commit Guidelines](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit)
- [Commitlint](https://commitlint.js.org/)
- [Standard Version](https://github.com/conventional-changelog/standard-version)

---

**采纳日期**: 2026-04-24  
**团队成员**: hermes, copaw, claude  
**下次回顾**: Sprint 3 开始前
