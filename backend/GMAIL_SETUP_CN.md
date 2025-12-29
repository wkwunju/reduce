# Gmail API 快速设置指南 (中文)

## 为什么使用 Gmail API 而不是 SMTP？

- ✅ **更安全**: 使用 OAuth 2.0 而不是密码
- ✅ **无需应用密码**: 不需要生成或管理应用密码
- ✅ **更好的控制**: 可以随时从 Google 账户设置中撤销访问权限
- ✅ **官方方法**: 使用 Google 官方 API

## 设置步骤

### 第 1 步：创建 Google Cloud 项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com)
2. 点击顶部的项目下拉菜单
3. 点击"新建项目"
4. 输入项目名称（例如 "XTrack"）
5. 点击"创建"

### 第 2 步：启用 Gmail API

1. 在 Google Cloud Console 中，转到 **"API 和服务"** > **"库"**
2. 搜索 **"Gmail API"**
3. 点击"Gmail API"
4. 点击 **"启用"**

### 第 3 步：配置 OAuth 同意屏幕

1. 转到 **"API 和服务"** > **"OAuth 同意屏幕"**
2. 选择 **"外部"** 用户类型
3. 点击 **"创建"**
4. 填写必填字段：
   - **应用名称**: XTrack（或您喜欢的名称）
   - **用户支持电子邮件**: 您的邮箱
   - **开发者联系信息**: 您的邮箱
5. 点击 **"保存并继续"**
6. 在"范围"页面，点击 **"添加或删除范围"**
7. 搜索并添加: `https://www.googleapis.com/auth/gmail.send`
8. 点击 **"更新"** 然后 **"保存并继续"**
9. 在"测试用户"页面，点击 **"添加用户"**
10. 添加您的 Gmail 地址（用于发送邮件的邮箱）
11. 点击 **"保存并继续"**

### 第 4 步：创建 OAuth 凭据

1. 转到 **"API 和服务"** > **"凭据"**
2. 点击 **"创建凭据"** > **"OAuth 客户端 ID"**
3. 选择 **"桌面应用"** 作为应用类型
4. 输入名称（例如 "XTrack Email Client"）
5. 点击 **"创建"**
6. 在成功对话框中点击 **"确定"**

### 第 5 步：下载凭据

1. 在"OAuth 2.0 客户端 ID"部分，找到您新创建的客户端
2. 点击右侧的 **下载图标** (⬇️)
3. 将文件保存为 **`credentials.json`**
4. 将其移动到您的 **`backend`** 目录：
   ```bash
   mv ~/Downloads/client_secret_*.json /path/to/xtrack/backend/credentials.json
   ```

### 第 6 步：配置环境变量

1. 打开 `backend/.env`（或从 `.env.example` 创建）
2. 添加或更新：
   ```env
   FROM_EMAIL=your_email@gmail.com
   GMAIL_CREDENTIALS_FILE=credentials.json
   GMAIL_TOKEN_FILE=token.pickle
   ```

### 第 7 步：首次运行 - OAuth 授权

1. 启动后端服务器：
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. 第一次尝试发送邮件时，系统会：
   - 自动打开浏览器窗口
   - 要求您登录 Google 账户
   - 显示 OAuth 同意屏幕
   - 要求您授予权限

3. **点击"允许"** 授予权限

4. 浏览器会显示"认证流程已完成"

5. 系统会在 `backend` 目录中自动创建 `token.pickle` 文件

6. **完成！** 令牌将被重复使用于后续请求

## 文件结构

设置完成后，您的 backend 目录应该包含：
```
backend/
├── credentials.json    # OAuth 客户端凭据（保密！）
├── token.pickle        # 访问令牌（自动生成，保密！）
├── .env               # 您的配置
├── app/
└── ...
```

⚠️ **安全提示**: 永远不要将 `credentials.json` 或 `token.pickle` 提交到 git！它们默认已在 `.gitignore` 中。

## 测试邮件

### 方法 1：使用前端测试功能

1. 访问 http://localhost:5173
2. 点击"快速测试"
3. 输入用户名和邮箱地址
4. 点击"运行测试"
5. 检查邮箱

### 方法 2：直接使用 API

```bash
curl -X POST "http://localhost:8000/api/monitoring/test" \
  -H "Content-Type: application/json" \
  -d '{
    "x_username": "elonmusk",
    "hours_back": 24,
    "topics": ["AI"],
    "email": "your_email@gmail.com"
  }'
```

## 常见问题

### "找不到 credentials.json"

- 确保您已从 Google Cloud Console 下载 OAuth 凭据
- 将文件放在 `backend` 目录中
- 将其重命名为 `credentials.json`（而不是 `client_secret_*.json`）

### "OAuth 流程失败"

- 确保您已在 Google Cloud Console 中启用 Gmail API
- 检查您的邮箱是否已在 OAuth 同意屏幕中添加为测试用户
- 尝试删除 `token.pickle` 并重新授权

### "权限不足"

- 确保您在 OAuth 同意屏幕中添加了 `gmail.send` 范围
- 删除 `token.pickle` 并重新授权以获取新权限

### OAuth 期间浏览器未打开

- 检查您的防火墙设置
- 应用尝试打开 `http://localhost:[random-port]`
- 您可以手动从终端复制 URL 并粘贴到浏览器中

### "访问被阻止：此应用的请求无效"

- 确保您的应用在 OAuth 同意屏幕中处于"测试"模式（而不是"已发布"）
- 将您的邮箱添加到测试用户列表
- 等待几分钟让 Google 传播更改

### 令牌过期

- 令牌会自动刷新
- 如果刷新失败，删除 `token.pickle` 并重新授权

## 撤销访问

要撤销 XTrack 对您 Gmail 的访问：

1. 访问 [Google 账户 - 有权访问您账户的应用](https://myaccount.google.com/permissions)
2. 找到"XTrack"（或您命名的任何名称）
3. 点击"删除访问权限"
4. 从 backend 目录删除 `token.pickle`

## 重新授权

如果您需要重新授权（例如，更改了 Gmail 账户）：

1. 删除 `token.pickle`：
   ```bash
   cd backend
   rm token.pickle
   ```
2. 重启服务器
3. OAuth 流程将自动重新开始

## 生产部署

对于生产环境：

1. **保护凭据安全**: 将 `credentials.json` 安全存储（例如 AWS Secrets Manager）
2. **使用环境变量**: 
   ```env
   GMAIL_CREDENTIALS_FILE=/secure/path/to/credentials.json
   GMAIL_TOKEN_FILE=/secure/path/to/token.pickle
   ```
3. **考虑服务账户**: 对于服务器到服务器的场景，使用服务账户
4. **迁移到"已发布"模式**: 如果您希望任何 Gmail 用户都能使用（需要验证）

## 与 SMTP 的区别

| 功能 | Gmail API (OAuth) | SMTP |
|------|------------------|------|
| 安全性 | OAuth 2.0 令牌 | 用户名 + 密码/应用密码 |
| 设置 | Google Cloud Console | 仅需凭据 |
| 访问控制 | 可从 Google 账户撤销 | 需要更改密码 |
| 速率限制 | 更高（最多 10 亿/天） | 较低 |
| 官方支持 | 是 | 是，但是旧方法 |
| 需要 2FA | 否 | 是（对于应用密码） |

## 额外资源

- [Gmail API 文档](https://developers.google.com/gmail/api)
- [桌面应用的 OAuth 2.0](https://developers.google.com/identity/protocols/oauth2/native-app)
- [Gmail API Python 快速入门](https://developers.google.com/gmail/api/quickstart/python)

