# Gmail API 设置 - 详细步骤（中文）

## 当前状态
❌ 错误：`Credentials file not found: credentials.json`

## 需要做什么
下载 OAuth 2.0 凭据文件并保存为 `credentials.json`

---

## 详细步骤

### 第 1 步：访问 Google Cloud Console

1. 打开浏览器，访问：https://console.cloud.google.com
2. 登录您的 Google 账户
3. 确认您在正确的项目中（页面顶部会显示项目名称）

### 第 2 步：进入凭据页面

1. 点击左侧菜单栏的 **"API 和服务"**
2. 点击 **"凭据"** (Credentials)
3. 或者直接访问：https://console.cloud.google.com/apis/credentials

### 第 3 步：找到您的 OAuth 客户端

在 "OAuth 2.0 客户端 ID" 部分，您应该会看到：

```
名称                      类型          创建日期
XTrack Email Client    桌面应用       2024-12-28
```

### 第 4 步：配置 Redirect URI（如果还没做）

1. 点击 OAuth 客户端名称（如 "XTrack Email Client"）
2. 在 **"已获授权的重定向 URI"** 部分：
   - 点击 **"+ 添加 URI"**
   - 输入：`http://localhost`
   - 再次点击 **"+ 添加 URI"**
   - 输入：`http://localhost:8080/`
3. **"已获授权的 JavaScript 来源"** 留空
4. 点击页面底部的 **"保存"** 按钮

### 第 5 步：下载凭据文件

1. 返回凭据列表页面
2. 在 "OAuth 2.0 客户端 ID" 部分
3. 找到您的客户端行
4. 点击右侧的 **下载图标** ⬇️ （看起来像一个向下的箭头）

   ```
   名称                      类型          [编辑图标] [下载图标] [删除图标]
   XTrack Email Client    桌面应用       ✏️         ⬇️         🗑️
                                                    ↑ 点这里
   ```

5. 文件会下载到您的 Downloads 文件夹
6. 文件名类似：`client_secret_123456789-abc.apps.googleusercontent.com.json`

### 第 6 步：移动和重命名文件

**方法 1：使用终端（推荐）**

打开终端，执行以下命令：

```bash
# 进入 Downloads 目录
cd ~/Downloads

# 查看下载的文件
ls -la client_secret*.json

# 复制并重命名到项目目录
cp client_secret_*.json /Users/wenkai/ai-project/xtrack/backend/credentials.json

# 验证文件已复制
ls -la /Users/wenkai/ai-project/xtrack/backend/credentials.json
```

**方法 2：使用 Finder（图形界面）**

1. 打开 Finder
2. 点击左侧的 "下载" (Downloads)
3. 找到 `client_secret_xxx.json` 文件
4. 复制该文件（Cmd + C）
5. 在 Finder 中按 Cmd + Shift + G，输入：
   ```
   /Users/wenkai/ai-project/xtrack/backend
   ```
6. 粘贴文件（Cmd + V）
7. 右键点击文件，选择 "重命名"
8. 将文件名改为：`credentials.json`

### 第 7 步：验证文件

在终端执行：

```bash
cat /Users/wenkai/ai-project/xtrack/backend/credentials.json
```

您应该看到类似这样的内容：

```json
{
  "installed": {
    "client_id": "123456789-abc...apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    ...
  }
}
```

如果看到这样的内容，说明文件正确！

### 第 8 步：重新测试

1. 确保后端服务器正在运行：
   ```bash
   cd /Users/wenkai/ai-project/xtrack/backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. 在前端点击 "Run Test" 并输入邮箱

3. **第一次会打开浏览器**：
   - 自动打开浏览器窗口
   - 要求您登录 Google 账户
   - 显示授权页面
   - 点击 **"允许"**
   - 浏览器显示 "认证流程已完成"
   - 系统会自动创建 `token.pickle` 文件

4. 以后就不需要再授权了！

---

## 如果没有看到下载按钮？

### 可能原因 1：OAuth 客户端还没创建

如果您还没有创建 OAuth 客户端，请按以下步骤创建：

1. 在凭据页面，点击 **"创建凭据"**
2. 选择 **"OAuth 客户端 ID"**
3. 如果提示配置同意屏幕，先完成同意屏幕配置（见 GMAIL_SETUP_CN.md）
4. 应用类型选择：**"桌面应用"**
5. 名称：输入 "XTrack Email Client"
6. 点击 **"创建"**
7. 在弹出的对话框中，点击 **"下载 JSON"**
8. 保存文件

### 可能原因 2：权限问题

确保您有项目的 Owner 或 Editor 权限。

---

## 常见问题

### Q: 我找不到下载按钮
**A:** 确保您在 "凭据" 页面，而不是 "OAuth 同意屏幕" 页面。下载按钮在 OAuth 客户端列表的每一行右侧。

### Q: 下载的文件名很长
**A:** 这是正常的！OAuth 凭据文件的默认名称包含客户端 ID。您需要将它重命名为 `credentials.json`。

### Q: 我下载了多个文件，应该用哪个？
**A:** 使用最新的那个。如果不确定，删除所有旧的，重新下载一次。

### Q: 文件内容看起来不对
**A:** 确保下载的是 **OAuth 客户端 ID** 的凭据，不是 API Key 或服务账户密钥。正确的文件应该包含 `"installed"` 或 `"web"` 字段。

---

## 下一步

文件放置好后：

1. ✅ `credentials.json` 在 `backend/` 目录
2. ✅ 重启后端服务器
3. ✅ 测试发送邮件
4. ✅ 第一次会打开浏览器授权
5. ✅ `token.pickle` 自动创建
6. ✅ 以后就可以直接发送邮件了！

---

## 需要帮助？

如果按照以上步骤仍然有问题：

1. 检查文件路径是否正确
2. 检查文件权限：`ls -la backend/credentials.json`
3. 查看后端日志中的详细错误信息
4. 确认 Google Cloud Console 中 Gmail API 已启用

---

## 文件位置应该是

```
backend/
├── credentials.json        ← 您下载并重命名的文件
├── token.pickle            ← 第一次授权后自动生成
├── .env                    ← 您的配置文件
├── app/
│   └── ...
└── ...
```

⚠️ **重要**：这两个文件都已在 `.gitignore` 中，不会被提交到 Git。

