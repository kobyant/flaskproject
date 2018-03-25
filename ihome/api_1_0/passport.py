#coding:utf8
import json
import re
from flask import current_app
from flask import g
from flask import request, jsonify
from flask import session

from ihome import constants
from ihome import redis_store, db
from ihome.api_1_0 import api

#注册功能
#请求路径: /api/v1_0/users
#请求方式: POST,  修改,更新服务器的数据
#参数: 手机号, 短信验证码,密码
from ihome.models import User, Area
from ihome.utils.commons import required_login
from ihome.utils.response_code import RET

@api.route('/users',methods=["POST"])
def register():
    #1.获取请求参数
    req_json =  request.data
    req_dict = json.loads(req_json)
    mobile = req_dict["mobile"]
    sms_code = req_dict["sms_code"]
    password = req_dict["password"]

    #2.校验参数
    if not all([mobile,sms_code,password]):
        return jsonify(errno=RET.PARAMERR,errmsg = "参数填写不完整")

    #验证手机号是否正确
    if not re.match(r"1[356789]\d{9}",mobile):
        return jsonify(errno=RET.DATAERR,errmsg="手机号填写错误")

    #3.业务逻辑处理
    #3.1取出redis中的短信验证码
    try:
        real_sms_code = "1"#redis_store.get("sms_code_%s"%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码异常")

    #3.2判断是否过期
    if real_sms_code is None:
        return jsonify(errno=RET.DATAERR,errmsg="短信验证码过期")

    #3.3删除redis中的短信
    try:
        redis_store.delete("sms_code_%s"%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="短信验证码异常")

    #3.4判断短信验证码是否正确
    if sms_code != real_sms_code:
        return jsonify(errno=RET.DATAERR,errmsg="短信验证码出错")

    #3.5判断用户输入的手机号是否已经注册了
    user =  User.query.filter_by(mobile=mobile).first()
    if user is not None:
        return jsonify(errno=RET.DATAERR,errmsg="该手机号已经注册了")

    #3.6根据传入的参数创建对象,存储到数据库中
    try:
        """
        密码不能以明文的形式存储在数据库中,有安全隐患
        常见的加密方式: MD5(不可逆),SHA1,SHA256,AES,DES,DES,RSA..
        """
        user = User(name=mobile,mobile=mobile)
        user.password = password

        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="注册失败")

    #3.7记录用户的状态
    session["user_id"] = user.id
    session["name"] = mobile
    session["mobile"] = mobile

    #3.7返回注册信息
    return jsonify(errno=RET.OK,errmsg="注册成功")


#请求路径:/api/v1_0/sessions
#请求方式:POST
#参数:手机号,密码
@api.route('/sessions',methods=["POST"])
def login():
    #1.获取参数(手机号,密码)
    req_json = request.data
    req_dict = json.loads(req_json)
    mobile = req_dict.get("mobile")
    password = req_dict.get("password")

    #2.校验参数
    if not all([mobile,password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数有误")

    #验证手机号的格式
    if not re.match(r"1[356789]\d{9}",mobile):
        return jsonify(errno=RET.PARAMERR,errmsg="手机号格式有误")


    #记录用户的登录次数
    try:
        ip = request.remote_addr #获取用户的ip
        account = redis_store.get("access_%s"%ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if account is not None and int(account) >= constants.LOGIN_ERROR_COUNT:
            return jsonify(errno=RET.DBERR,errmsg="登录次数用完,请十分钟再试")

    #3.根据手机号取出用户对象
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询异常")

    #4.判断用户名,密码
    if user is None or not user.check_password(password):
        try:
            redis_store.incr("access_%s"%ip)
            redis_store.expire("access_%s"%ip,constants.LOGIN_ERROR_TIME)
        except Exception as e:
            current_app.logger.error(e)

        return jsonify(errno=RET.DATAERR,errmsg="用户名或者密码错误")

    #登录成功,清除redis中的登录错误次数
    try:
        redis_store.delete("access_%s"%ip)
    except Exception as e:
        current_app.logger.error(e)

    #5.记录用户的登录状态
    session["user_id"] = user.id
    session["user_name"] = user.name
    session["mobile"] = user.mobile

    #6.响应
    return jsonify(errno=RET.OK,errmsg="登录成功")


#请求路径: /api/v1_0/session
#请求方式: GET
#请求参数: 无
@api.route('/session')
def check_login ():

    #1.获取session中的用户名
    name = session.get("user_name")

    #2.判断用户的登录状态
    if name is not None:
        return jsonify(errno=RET.OK,errmsg="登录成功",data={"name":name})
    else:
        return jsonify(errno=RET.SESSIONERR,errmsg="未登录")

#请求路径: /api/v1_0/session
#请求方式: DELETE
#请求参数: 无
@api.route('/session',methods=["DELETE"])
def logout():
    #清除session中的内容
    session.clear()
    return jsonify(errno=RET.OK,errmsg="退出成功")

