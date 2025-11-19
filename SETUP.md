# 项目设置指南

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/ykykj/7103C-DataMining-Project.git
cd 7103C-DataMining-Project
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 并重命名为 `.env`：

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

然后编辑 `.env` 文件，填入你的 API Keys：

```env
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
GOOGLE_CLOUD_AUTH_EMAIL=your-email@gmail.com
```

#### 📝 如何获取 DeepSeek API Key：
1. 访问 https://platform.deepseek.com/api_keys
2. 注册/登录账户
3. 点击 "Create API Key"
4. 复制生成的 API Key

💰 **费用说明**：DeepSeek 价格极低，充值 ¥10-20 可以使用很长时间。

### 5. 配置 Google OAuth 凭证

#### a) 获取凭证文件：
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目并启用以下 API：
   - Gmail API
   - Google Calendar API
   - Google Drive API
   - Google Docs API
3. 创建 OAuth 2.0 客户端 ID（类型：桌面应用）
4. 下载 `credentials.json` 文件

#### b) 放置文件：
```bash
mkdir creds
# 将下载的 credentials.json 放到 creds 目录
```

最终路径应该是：`creds/credentials.json`

### 6. 运行项目

#### Windows：
```bash
# 双击运行
run.bat

# 或命令行
python src\Main.py
```

#### macOS/Linux：
```bash
python src/Main.py
```

### 7. 首次授权

首次运行时：
1. 程序会自动打开浏览器
2. 使用你的 Google 账户登录
3. 授权应用访问 Gmail、Calendar、Drive
4. 授权成功后会生成 `token.pickle` 文件
5. 之后运行无需重复授权

---

## 📂 项目结构

```
Personal-Assistant-Agent/
├── .env                    # 环境变量（需要创建，不在 Git 中）
├── .env.example            # 环境变量模板
├── .gitignore
├── requirements.txt        # Python 依赖
├── README.md              # 项目介绍
├── SETUP.md               # 本文件
├── run.bat                # Windows 快速启动
├── run.ps1                # PowerShell 启动
├── creds/
│   └── credentials.json   # Google OAuth（需要自己下载）
└── src/
    ├── Main.py            # 程序入口
    ├── agent/
    │   └── PersonalAssistantAgent.py
    ├── service/
    │   └── GoogleService.py
    └── tools/
        └── AgentTools.py
```

---

## 🔧 常见问题

### Q1: ModuleNotFoundError
**解决**：确保虚拟环境已激活，并重新安装依赖
```bash
pip install -r requirements.txt
```

### Q2: DeepSeek API 错误
**解决**：
1. 检查 `.env` 文件中的 `DEEPSEEK_API_KEY` 是否正确
2. 确认账户有余额：https://platform.deepseek.com/usage

### Q3: Google 授权失败
**解决**：
1. 确认 `creds/credentials.json` 文件存在
2. 删除 `token.pickle` 重新授权
3. 检查 Google Cloud Console 中 API 是否已启用

### Q4: 权限错误（PowerShell）
**解决**：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 💡 使用示例

启动后，尝试这些命令：

```
You: what can you do?
You: 发送邮件给 john@example.com，主题是项目更新
You: 搜索来自张三的邮件
You: 创建明天下午3点的会议
You: 帮我制定一个 Python 学习计划
You: exit
```

---

## 📞 技术支持

如果遇到问题，请：
1. 检查本文档的常见问题部分
2. 查看 GitHub Issues
3. 联系项目维护者

---

## 🔐 安全提醒

⚠️ **重要**：
- **不要**将 `.env` 文件提交到 Git
- **不要**分享你的 API Keys
- **不要**上传 `credentials.json` 和 `token.pickle`
- 团队成员需要使用各自的 API Keys 和 Google 凭证

