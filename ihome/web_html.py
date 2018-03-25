#coding:utf8
from flask import Blueprint
from flask import current_app
from flask import make_response
from flask_wtf.csrf import generate_csrf

"""
用户有可能:
127.0.0.1:5000/
127.0.0.1:5000/index.html
127.0.0.1:5000/register.html
.....
app(current_app)对象中的方法:send_static_file(页面)
可以获取到指定页面的内容
基本的网站都会使用favicon.ico作为网站的logo所以浏览器会自动的发送该资源的请求

"""
html = Blueprint("html",__name__)

@html.route('/<re(r".*"):file_name>')
def get_page(file_name):

    print file_name

    #1.判断首页
    if not file_name:
        # return current_app.send_static_file("html/index.html")
        file_name = "index.html"

    # 2.判断其他页面
    if file_name != "favicon.ico":
        # return current_app.send_static_file("html/%s"%file_name)
        file_name = "html/%s"%file_name


    #3.创建响应体, 给响应体中的csrf_token设置
    resp = make_response(current_app.send_static_file(file_name))
    resp.set_cookie("csrf_token", generate_csrf())# 保证请求的安全性

    return resp