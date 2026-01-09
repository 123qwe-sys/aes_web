# AES 文件加密工具

一个基于 FastAPI 和 Web 界面的 AES 文件加密解决方案。

## 项目概述

该项目提供了一个完整的文件加密系统，包括后端 API 和前端 Web 界面，支持多种 AES 加密模式。

## 功能特性

- 🔐 支持多种 AES 加密模式：EAX、CBC、CFB、OFB、CTR
- 📤 Web 界面文件上传和加密
- 💾 自动生成并下载加密文件
- ✅ 密钥长度验证（16/24/32 字节）
- 🎨 现代化、响应式用户界面

## 项目结构

```
aes_web/
├── main.py                          # FastAPI 后端应用
├── src/
│   ├── a.html                       # 示例网页
│   └── aes.html                     # AES 加密工具前端界面
├── file/                            # 加密文件存储目录
└── .gitignore
```

## 快速开始

### 安装依赖

```bash
pip install fastapi uvicorn pycryptodome
```

### 运行应用

```bash
uvicorn main:app --reload
```

应用将在 `http://localhost:8000` 启动。

## 使用说明

### 前端界面

访问 `http://localhost:8000/file_html/aes.html` 打开加密工具：

1. 选择要加密的文件
2. 输入 16、24 或 32 字节的加密密钥
3. 选择加密模式（默认为 EAX）
4. 点击"加密并下载"按钮
5. 加密文件将自动下载到本地

### API 端点

#### 获取加密文件
```http
GET /file/{file_name}
```
下载已加密的文件。

#### 加密文件
```http
POST /encrypt_file/
Content-Type: multipart/form-data

file: <binary file>
key: <encryption key>
mode: <EAX|CBC|CFB|OFB|CTR>
iv: <initialization vector> (仅 CBC、CFB、OFB 模式需要)
nonce: <nonce> (可选)
```

## 技术栈

- **后端框架**：[FastAPI](https://fastapi.tiangolo.com/)
- **加密库**：[PyCryptodome](https://www.dlitz.net/software/pycryptodome/)
- **前端**：HTML5、CSS3、JavaScript

## 加密模式说明

| 模式 | 说明 | 使用场景 |
|------|------|---------|
| **EAX** | 经过身份验证的加密 | 高安全性要求（推荐） |
| **CBC** | 密码块链接 | 需要提供 IV |
| **CFB** | 密文反馈 | 需要提供 IV |
| **OFB** | 输出反馈 | 需要提供 IV |
| **CTR** | 计数器模式 | 流式加密 |

## 文件说明

- main.py - 后端 FastAPI 应用，处理文件加密逻辑
- aes.html - 加密工具前端界面
- a.html - 示例网页模板

## 安全提示

⚠️ **生产环境注意事项**：

- 使用强密钥（16/24/32 字节的随机数据）
- 不要在代码中硬编码密钥
- HTTPS 传输敏感数据
- 定期更新依赖包
- 添加身份验证和授权机制

## 许可证

MIT
