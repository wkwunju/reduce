# OAuth 客户端 - 授权 URI 配置

## 重要提示

如果您在 Google Cloud Console 中创建的是 **"桌面应用"** 类型的 OAuth 客户端（推荐），那么：

### ✅ 桌面应用（推荐）

**Authorized redirect URIs（必须添加）:**
```
http://localhost
```

或者添加多个端口以确保兼容性：
```
http://localhost:8080/
http://localhost:8081/
http://localhost:8090/
http://localhost:9000/
```

**Authorized JavaScript origins:**
- ❌ **留空** - 桌面应用不需要

---

## 如果您创建的是 "Web 应用"（不推荐用于此项目）

如果您误选了 "Web 应用" 类型，请删除并重新创建为 "桌面应用"。

但如果必须使用 Web 应用类型，则需要：

**Authorized JavaScript origins:**
```
http://localhost
http://localhost:8000
```

**Authorized redirect URIs:**
```
http://localhost:8000/oauth2callback
http://localhost/oauth2callback
```

---

## 操作步骤（截图中的界面）

### 1. Authorized JavaScript origins
- 如果是桌面应用：**跳过此部分**（留空）
- 如果必须填写：点击 "+ Add URI"，输入 `http://localhost`

### 2. Authorized redirect URIs（重要！）
1. 点击 **"+ Add URI"** 按钮
2. 输入：`http://localhost`
3. （可选）再次点击 "+ Add URI"，添加：
   - `http://localhost:8080/`
   - `http://localhost:8081/`
   - `http://localhost:8090/`
4. 点击页面底部的 **"Save"** 或 **"保存"** 按钮

---

## 验证配置

配置完成后：

1. 下载更新后的凭据（如果提示）
2. 确保 `credentials.json` 在 `backend/` 目录
3. 启动服务器：
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```
4. OAuth 流程会自动打开浏览器，使用您刚才配置的 redirect URI

---

## 常见问题

### "redirect_uri_mismatch" 错误

如果看到此错误，说明：
- OAuth 流程使用的 URI 与您在 Google Cloud Console 中配置的不匹配
- 解决方法：查看错误消息中显示的实际 URI，然后在 Google Cloud Console 中添加该 URI

### 应该选择什么应用类型？

- ✅ **推荐：桌面应用** - 适用于服务器端运行的应用
- ❌ **不推荐：Web 应用** - 除非您的应用完全在浏览器中运行

如果您当前的客户端是 "Web 应用" 类型：
1. 在 Google Cloud Console 中删除它
2. 重新创建，选择 **"桌面应用"** 类型
3. 下载新的 credentials.json

---

## 截图配置示例

根据您的截图，应该这样填写：

### Authorized JavaScript origins
```
（留空 - 桌面应用不需要）
```

### Authorized redirect URIs
```
http://localhost
http://localhost:8080/
http://localhost:8090/
```

填写完成后，点击 **"保存"** 按钮。

