#coding:utf8
import json

from flask import current_app
from flask import g, jsonify
from flask import request
from flask import session

from ihome import constants, db
from ihome.api_1_0 import api
from ihome.lib.upload_image import upload_image
from ihome.models import User
from ihome.utils.commons import required_login
from ihome.utils.response_code import RET

#请求路径: /api/v1_0/users/avatar
#请求方式: post
#参数: 头像(avatar)
@api.route("/users/avatar",methods=["POST"])
@required_login
def set_user_avatar():
    #1. 获取参数(用户id, 图像对象)
    user_id = g.user_id
    file_image = request.files.get("avatar")

    #2.校验参数
    if not all([user_id,file_image]):
        return jsonify(errno=RET.DATAERR,errmsg="参数不正确")

    #3.读取图像中的内容(二进制数据)
    file_data = file_image.read()

    #4.上传头像到七牛云
    try:
        file_name =  upload_image(file_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="图像上传到七牛云错误")

    #5.将头像数据更新到数据库
    try:
        User.query.filter_by(id=user_id).update({"avatar_url":file_name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="图像数据库保存错误")

    #6.返回响应信息
    file_url = constants.QI_NIU_DOMAIN + file_name
    return jsonify(errno=RET.OK,errmsg="图像保存成功",data={"avatar_url":file_url})

#功能描述: 修改用户名
#请求路径:/api/v1_0/user/name
#请求方式:PUT
#请求参数:新的用户名
@api.route('/user/name',methods=["PUT"])
def change_user_name():
    #1.获取参数(用户名,id)
    user_id = session.get("user_id")
    user_name = json.loads(request.data).get("name")

    #2.校验参数
    if not all([user_id,user_name]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")

    #3.根据id修改对应的数据库中的用户名
    try:
        User.query.filter_by(id=user_id).update({"name":user_name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    #4.更新session中的信息
    session["user_name"]= user_name

    #5.返回
    return jsonify(errno=RET.OK,errmsg="修改成功")


#功能描述: 展示用户信息
#请求路径: /api/v1_0/user
#请求方式: GET
#请求参数: 无
@api.route('/user')
@required_login
def show_user_info():
    #1. 获取参数(用户的id)
    user_id = session.get("user_id")

    #2.查询用户的信息根据id
    try:
        user = User.query.filter_by(id=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取失败")

    #3.将用户对象中的内容,拼接成一个字典
    # user_dict = {
    #     "id":user.id,
    #     "name":user.name,
    #     "mobile":user.mobile,
    #     "real_name":user.real_name,
    #     "avatar":constants.QI_NIU_DOMAIN + user.avatar_url if user.avatar_url else ""
    # }

    #3.返回
    return jsonify(errno=RET.OK,errmsg="获取成功",data=user.user_dict())


#功能描述: 获取实名认证界面信息
#请求路径: /api/v1_0/user/auth
#请求方式: GET
#请求参数: 无
@api.route('/user/auth')
@required_login
def check_auth():
    #1. 获取参数(用户id)
    user_id = session.get("user_id")

    #2.根据用户id到数据库查询对应的用户
    try:
        user = User.query.filter_by(id=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取认证信息失败")

    #3.判断查询到的用户对象是否为空
    if user is None:
        return jsonify(errno=RET.DATAERR,errmsg="没有该用户")

    #3.将对象中的数据拼接成字典返回
    return jsonify(errno=RET.OK,errmsg="获取认证信息成功",data=user.user_dict())


#功能描述: 设置用户的实名认证信息
#请求路径: /api/v1_0/user/auth
#请求方式: POST
#请求参数: 身份证号, 真实姓名
@api.route('/user/auth',methods=["POST"])
@required_login
def set_user_auth():
    #1. 获取用户提交的参数(id,id_card,real_name)
    user_id = session.get("user_id")
    req_data = request.data
    req_dict = json.loads(req_data)

    id_card = req_dict.get("id_card")
    real_name = req_dict.get("real_name")

    #2. 校验参数
    if not all([id_card,real_name]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")

    #3.根据用户的id设置数据库中的用户对象
    try:
        User.query.filter_by(id=user_id).update({"real_name":real_name,"id_card":id_card})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return  jsonify(errno=RET.DBERR,errmsg="设置信息异常")


    #4.返回状态
    return jsonify(errno=RET.OK,errmsg="设置成功")
