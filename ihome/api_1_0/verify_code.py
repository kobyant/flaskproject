#coding:utf8
import random
from flask import current_app, jsonify
from flask import make_response
from flask import request
from ihome import constants
from ihome import redis_store
from ihome.lib.ytx.SendTemplateSMS import CCP
from ihome.tasks import task_sms
from ihome.tasks.task_sms import send_template_sms
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome.utils.response_code import RET

@api.route('/get_image_code/<image_code>')
def get_image_code(image_code):

    #1.生成验证码(名字,验证码,图片二进制数据)
    name,text,imageData =  captcha.generate_captcha()

    #2.保存验证码到redis中
    try:
        # redis_store.set("image_id_%s"%image_code,text)
        # redis_store.expires("image_id_%s"%image_code,constants.IMAGE_CODE_EXPIRES)
        redis_store.setex("image_code_%s"%image_code,constants.IMAGE_CODE_EXPIRES,text)
    except Exception as e:
        current_app.logger.error(e)
        resp = {
            "errno":RET.DBERR,
            "errmsg":"验证码保存失败"
        }
        return jsonify(resp)

    #3.返回验证码的图片
    resp = make_response(imageData)
    resp.headers["Content-Type"]  = "image/jpg"
    return resp

"""
#发送短信
#请求的路经: /api/v1_0/sms_codes/mobile?image_code_id=xxx&image_code=xxx
#请求参数: 手机号,图片验证码,编号
#请求方式: GET
@api.route('/sms_codes/<re(r"1[356789]\d{9}"):mobile>')
def get_sms_code(mobile):

    #1.获取get请求参数
    image_code_id =  request.args.get("image_code_id")
    image_code = request.args.get("image_code")

    #2.校验参数
    if not all([image_code_id,image_code]):
        resp = {
            "errno":RET.PARAMERR,
            "errmsg":"参数不完整"
        }
        return jsonify(resp)
        # return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")

    #3.业务逻辑处理
    #获取到redis中的图片验证码
    try:
        real_image_code = redis_store.get("image_code_%s"%image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="验证码异常")

    #判断redis中的验证码是否过期
    if real_image_code == None:
        return jsonify(errno=RET.DATAERR, errmsg = "图片验证码过期")

    #删除redis中的图片验证码
    try:
        redis_store.delete("image_code_%s"%image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="验证码异常")

    #判断图片验证码是否正确
    if image_code.lower() != real_image_code.lower():
        return jsonify(errno=RET.DATAERR,errmsg="验证码错误")

    #生成短信验证码
    sms_code = "%06d"%random.randint(0,999999)

    # 将短信验证码存储到redis中
    try:
        redis_store.setex("sms_code_%s" % mobile, constants.SMS_CODE_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="短信验证码异常")

    #发送短信验证码
    try:
        ccp = CCP()
        result = ccp.sendTemplateSMS(mobile,[sms_code,5],1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg="短信发送异常")

    #判断短信验证码是否发送成功
    if result == 0:
        return jsonify(errno=RET.OK,errmsg="短信发送成功")
    else:
        return jsonify(errno=RET.DATAERR,errmsg="短信发送失败")
"""

#发送短信
#请求的路经: /api/v1_0/sms_codes/mobile?image_code_id=xxx&image_code=xxx
#请求参数: 手机号,图片验证码,编号
#请求方式: GET
@api.route('/sms_codes/<re(r"1[356789]\d{9}"):mobile>')
def get_sms_code(mobile):

    #1.获取get请求参数
    image_code_id =  request.args.get("image_code_id")
    image_code = request.args.get("image_code")

    #2.校验参数
    if not all([image_code_id,image_code]):
        resp = {
            "errno":RET.PARAMERR,
            "errmsg":"参数不完整"
        }
        return jsonify(resp)
        # return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")

    #3.业务逻辑处理
    #获取到redis中的图片验证码
    try:
        real_image_code = redis_store.get("image_code_%s"%image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="验证码异常")

    #判断redis中的验证码是否过期
    if real_image_code == None:
        return jsonify(errno=RET.DATAERR, errmsg = "图片验证码过期")

    #删除redis中的图片验证码
    try:
        redis_store.delete("image_code_%s"%image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="验证码异常")

    #判断图片验证码是否正确
    if image_code.lower() != real_image_code.lower():
        return jsonify(errno=RET.DATAERR,errmsg="验证码错误")

    #生成短信验证码
    sms_code = "%06d"%random.randint(0,999999)

    # 将短信验证码存储到redis中
    try:
        redis_store.setex("sms_code_%s" % mobile, constants.SMS_CODE_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="短信验证码异常")

    #发送短信验证码
    """
    try:
        ccp = CCP()
        result = ccp.sendTemplateSMS(mobile,[sms_code,5],1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg="短信发送异常")
    """

    task_sms.send_template_sms(mobile,["444",5],1)

    # #判断短信验证码是否发送成功
    # if result == 0:
    return jsonify(errno=RET.OK,errmsg="短信发送成功")
    # else:
    #     return jsonify(errno=RET.DATAERR,errmsg="短信发送失败")
