#coding:utf8
"""
自定义转换器:
1. 自定义类,继承自BaseConverter
2. 编写__init__方法,接受三个参数,self,url_map,regex
3. 调用父类方法传递参数,自身类,self,url_map
4. 将规则赋值到当前对象,self.regex = regex

"""""
from functools import wraps

from flask import g
from flask import session, jsonify
from werkzeug.routing import BaseConverter

from ihome.utils.response_code import RET


class RegexConverter(BaseConverter):
    """自定义转换规则"""
    def __init__(self,url_map,regex):
        super(RegexConverter,self).__init__(url_map)
        self.regex = regex

"""
由于很多功能都依赖于用户是否登录
只有用户已经登录过得状态,才可以进行,修改,查询,订单..等等功能
所以可以使用装饰器来完成,一旦用户成功登录之后,可以记录用户的登录状态
"""
def required_login(view_func):
    """登录装饰器"""
    @wraps(view_func)
    def wrapper(*args,**kwargs):
        try:
            user_id =  session["user_id"]
        except Exception as e:
            user_id = None

        if user_id is not None:
            g.user_id = user_id
            return view_func(*args,**kwargs)
        else:
            return jsonify(errno=RET.SESSIONERR,errmsg="用户未登录")

    return  wrapper
