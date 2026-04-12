# Git 分支策略 - Appt 项目

## 🌳 分支结构

```
main              # 生产环境 (受保护)
├── develop       # 开发主分支
│   ├── feature/* # 功能分支 (如：feature/booking-system)
│   ├── bugfix/*  # Bug 修复分支
│   └── hotfix/*  # 紧急热修复
└── release/*     # 预发布分支
```

## 📝 工作流程

### 1. 创建功能分支
```bash
git checkout develop
git pull origin develop
git checkout -b feature/booking-api
```

### 2. 开发并提交
```bash
# Commit 消息规范：type(scope): description
git add .
git commit -m "feat(bookings): implement conflict detection logic"
```

**Commit Type:**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整 (不影响功能)
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

### 3. 推送与 Pull Request
```bash
git push origin feature/booking-api
```

在 GitHub 上创建 PR，合并到 `develop` 分支。

### 4. 发布流程
```bash
# 从 develop 创建 release 分支
git checkout -b release/v1.0.0 develop

# 测试完成后合并到 main 并打标签
git checkout main
git merge --no-ff release/v1.0.0
git tag -a v1.0.0 -m "Release 1.0.0"
```

## 🔒 分支保护规则

**main 分支:**
- ✅ 仅允许通过 Pull Request 合并
- ✅ 需要至少 1 个代码审查者批准
- ✅ CI/CD 流水线必须通过

**develop 分支:**
- ✅ 仅允许通过 Pull Request 合并

## 🤝 Git Hooks (可选)

建议在 `.githooks/` 目录配置:
- `pre-commit`: ESLint + Prettier 检查
- `commit-msg`: Commit 消息格式验证

---

*最后更新：2026-04-11 | 作者：罗杰斯*
