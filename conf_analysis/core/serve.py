#!/usr/bin/env python3
"""
简单的本地HTTP服务器
用于在本地运行前端页面，避免CORS问题
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def start_server():
    """启动本地服务器"""
    # 切换到项目根目录
    os.chdir(Path(__file__).parent)
    
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    
    print(f"🚀 启动本地服务器...")
    print(f"📂 服务目录: {os.getcwd()}")
    print(f"🌐 访问地址: http://localhost:{PORT}")
    print(f"📊 分析报告: http://localhost:{PORT}/frontend/index.html")
    print("按 Ctrl+C 停止服务器")
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"✅ 服务器已启动在端口 {PORT}")
            
            # 自动打开浏览器
            webbrowser.open(f'http://localhost:{PORT}/frontend/index.html')
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ 端口 {PORT} 已被占用，请尝试关闭其他服务或使用不同端口")
        else:
            print(f"❌ 启动服务器失败: {e}")

if __name__ == "__main__":
    start_server()