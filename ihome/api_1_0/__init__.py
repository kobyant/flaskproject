#coding:utf8
"""
蓝图使用流程:
1. 创建蓝图对象
2. 注册蓝图(将视图函数中的路径包装到蓝图中)
3. 注册蓝图对象(关联app对象和蓝图对象)

"""""
from flask import Blueprint

api = Blueprint("api_1_0",__name__)

from . import index,verify_code,passport,profile,houses