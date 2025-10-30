# API Playground 使用说明

## 概述

我们为 Surf API 文档添加了一个强大的交互式测试工具，让开发者可以直接在浏览器中测试 API，无需安装任何命令行工具。

## 新增功能

### 1. 在线 API 测试工具 (api-tester.html)

一个完整的 HTML 页面，提供以下功能：

- ✅ **输入框**：支持输入完整的 curl 命令
- ✅ **一键执行**：点击按钮即可执行 API 请求
- ✅ **实时响应**：显示 API 返回的完整 JSON 响应
- ✅ **状态显示**：显示 HTTP 状态码和响应时间
- ✅ **快速示例**：内置多个常用 API 的示例命令
- ✅ **键盘快捷键**：支持 Ctrl+Enter / Cmd+Enter 快速执行

### 2. API Playground 文档页面 (api-playground.mdx)

专门的文档页面，包含：
- 工具使用说明
- 嵌入的测试工具界面
- 快速开始示例
- 使用提示和注意事项

### 3. 各 API 页面增强

每个 API 页面顶部都添加了：
- 醒目的提示框，指向在线测试工具
- 更详细的 curl 使用示例
- 多场景的命令示例

## 文件结构

```
muninn/
├── api-reference/
│   ├── api-playground.mdx          # API Playground 页面
│   ├── events/
│   │   └── get-event.mdx           # ✨ 已更新
│   ├── projects/
│   │   ├── get-project.mdx         # ✨ 已更新
│   │   └── get-cyber-mind-share.mdx # ✨ 已更新
│   ├── search/
│   │   └── search.mdx              # ✨ 已更新
│   └── trendings/
│       ├── get-dex.mdx             # ✨ 已更新
│       ├── get-mind-shares.mdx     # ✨ 已更新
│       ├── get-smart-followings.mdx # ✨ 已更新
│       └── get-generals.mdx        # ✨ 已更新
├── api-tester.html                 # 🆕 在线测试工具
├── mint.json                       # ✨ 已更新导航
└── api-reference.mdx               # ✨ 已添加工具链接
```

## 如何使用

### 方法 1：通过导航栏访问

1. 打开文档首页
2. 在左侧导航栏的 "Getting Started" 部分
3. 点击 "API Playground"

### 方法 2：通过 API 页面快速访问

1. 打开任意 API 文档页面
2. 页面顶部有蓝色提示框
3. 点击"在线 API 测试工具"链接

### 方法 3：直接访问 HTML 页面

直接在浏览器中打开：`/api-tester.html`

## 功能演示

### 执行 curl 命令

1. 在输入框中输入或粘贴 curl 命令：
   ```bash
   curl -X GET "https://api.asksurf.ai/huginn/v1/search?query=bitcoin&limit=5"
   ```

2. 点击"执行请求"按钮

3. 查看响应结果，包括：
   - HTTP 状态码
   - 响应时间
   - 完整的 JSON 数据

### 使用快速示例

页面底部提供了 5 个常用 API 的示例：
- 搜索 API
- 趋势 DEX 代币
- 趋势 Mind Shares
- 趋势 Smart Followings
- 综合趋势

点击任意示例，命令会自动填充到输入框中。

## 技术特性

### API 测试工具特性

- **智能解析**：自动解析 curl 命令中的 URL、HTTP 方法和请求头
- **跨域支持**：使用浏览器 Fetch API，支持 CORS
- **响应格式化**：JSON 响应自动格式化，易于阅读
- **错误处理**：清晰显示错误信息
- **响应式设计**：适配各种屏幕尺寸

### 安全性

- ✅ 所有请求都是从浏览器直接发送到 API 服务器
- ✅ 不存储任何敏感信息
- ✅ 纯前端实现，无后端服务器
- ✅ 支持 Surf API 的公开接口（无需认证）

## 浏览器支持

- ✅ Chrome / Edge (推荐)
- ✅ Firefox
- ✅ Safari
- ✅ 所有支持 ES6+ 和 Fetch API 的现代浏览器

## 开发建议

### 建议 1：添加认证支持（如果需要）

如果未来 API 需要认证，可以在 HTML 中添加：

```javascript
headers['Authorization'] = 'Bearer YOUR_TOKEN';
```

### 建议 2：添加更多示例

在 `api-tester.html` 的 `.examples` 部分添加更多常用场景。

### 建议 3：集成到 CI/CD

可以将这些 curl 命令用于自动化测试：

```bash
# 在 CI 中执行
curl -X GET "https://api.asksurf.ai/huginn/v1/search?query=test" | jq
```

## 常见问题

### Q: 为什么有些请求失败？

A: 可能的原因：
1. URL 格式错误
2. 网络连接问题
3. API 服务器暂时不可用
4. CORS 限制（如果调用非公开 API）

### Q: 可以测试 POST 请求吗？

A: 可以！工具支持所有 HTTP 方法，只需在 curl 命令中指定：
```bash
curl -X POST "https://api.example.com/endpoint" -d '{"key":"value"}'
```

### Q: 响应结果太长怎么办？

A: 响应区域支持滚动，最大高度为 400px。可以复制结果到文本编辑器中查看。

## 更新日志

### 2025-10-30
- ✅ 创建 `api-tester.html` 交互式测试工具
- ✅ 创建 `api-playground.mdx` 文档页面
- ✅ 更新所有 API 页面，添加工具链接
- ✅ 优化 curl 命令示例，使其更易执行
- ✅ 更新导航配置

## 反馈

如果您有任何建议或发现问题，欢迎联系开发团队：
- Email: backend@cybertinolab.com
- 在 GitHub 上提交 Issue

---

**享受便捷的 API 测试体验！** 🚀

