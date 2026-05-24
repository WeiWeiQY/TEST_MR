# Python 漏洞靶场 - 安装和使用指南

## 📦 安装步骤

### 方法1：使用虚拟环境（推荐）

```bash
cd /Users/wuxin/Desktop/python_vuln_range

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py
```

### 方法2：使用 --user 标志

```bash
cd /Users/wuxin/Desktop/python_vuln_range

# 使用 --user 标志安装
pip install --user -r requirements.txt

# 运行应用
python app.py
```

### 方法3：使用 --break-system-packages（不推荐，仅在测试环境使用）

```bash
cd /Users/wuxin/Desktop/python_vuln_range

# 禁用系统包检查（仅用于测试）
pip install --break-system-packages -r requirements.txt

# 运行应用
python app.py
```

## 🚀 启动应用

安装完依赖后，运行：

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动。

## 📋 项目文件结构

```
python_vuln_range/
├── app.py                      # 主应用程序（包含所有漏洞逻辑）
├── requirements.txt            # Python依赖包
├── README.md                   # 项目文档
├── INSTALL.md                  # 本安装指南
├── templates/                  # HTML模板文件夹
│   ├── base.html             # 基础模板
│   ├── index.html            # 主页（漏洞列表）
│   ├── vuln_detail.html      # 漏洞详情页面
│   ├── sqli_demo.html        # SQL注入演示
│   ├── xss_demo.html         # XSS演示
│   ├── file_upload_demo.html # 文件上传演示
│   ├── command_injection_demo.html # 命令注入演示
│   ├── csrf.html             # CSRF演示
│   ├── csrf_login.html       # CSRF登录页面
│   ├── ssrf_demo.html        # SSRF演示
│   ├── xxe_demo.html         # XXE演示
│   ├── deserialization_demo.html # 反序列化演示
│   ├── path_traversal_demo.html # 路径遍历演示
│   ├── demo_base.html        # 演示基础模板
│   └── simple_demo.html      # 简单演示模板
├── uploads/                   # 上传文件目录（自动创建）
└── data/                     # 数据文件目录（自动创建）
    └── files/                # 文件包含演示文件
```

## 🎯 功能特性

✅ **10种常见漏洞演示**
- SQL注入、XSS、文件上传、文件包含、命令执行
- CSRF、SSRF、XXE、反序列化、路径遍历

✅ **每个漏洞包含**
- 详细的漏洞说明
- POC（概念验证）示例
- 易受攻击的代码示例
- 修复代码示例
- 交互式演示环境

✅ **友好的Web界面**
- 响应式设计
- 代码高亮显示
- 分标签查看（说明、POC、代码、修复）
- 安全警告提示

## 🌐 使用说明

1. **启动应用**
   ```bash
   python app.py
   ```

2. **访问主页**
   - 打开浏览器访问 `http://localhost:5000`

3. **学习流程**
   - 在主页选择要学习的漏洞
   - 点击"查看详情"了解漏洞原理和修复方案
   - 点击"演示"进入交互式测试环境
   - 对照易受攻击代码和修复代码学习

## ⚠️ 重要注意事项

- 此靶场仅供学习和研究使用
- 请勿在任何生产环境或未经授权的系统中使用
- 所有演示都是在受控环境中进行
- 使用这些知识进行非法活动将承担法律责任

## 🛠️ 依赖包说明

- Flask 3.0.0 - Web框架
- Flask-SQLAlchemy 3.1.1 - ORM（演示时非必需）
- Werkzeug 3.0.1 - WSGI工具库
- requests 2.31.0 - HTTP库（SSRF演示使用）
- lxml 4.9.3 - XML解析（XXE演示使用）
- python-dotenv 1.0.0 - 环境变量管理

## 🔧 故障排除

### 问题1: ModuleNotFoundError

**解决方案：**
```bash
# 创建虚拟环境并安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 问题2: 权限错误

**解决方案：**
```bash
# 使用 --user 标志安装
pip install --user -r requirements.txt
```

### 问题3: 端口被占用

**解决方案：**
修改 `app.py` 最后一行：
```python
# 修改端口号为其他可用端口
app.run(host='0.0.0.0', port=8000, debug=True)
```

## 📚 学习路径建议

### 初学者
1. SQL注入
2. XSS
3. 文件上传

### 进阶
4. 命令注入
5. CSRF
6. 文件包含

### 高级
7. SSRF
8. XXE
9. 反序列化
10. 路径遍历

## 🎓 扩展学习

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [Hack The Box](https://www.hackthebox.com/)

## 📞 支持

如有问题，请参考项目README.md或提交Issue。

---

**开始你的安全学习之旅吧！🚀**
