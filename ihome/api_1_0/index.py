#coding:utf8
from flask import current_app
from ihome import models
from  . import api

@api.route('/')
def index():
    # current_app.logger.debug("调试")
    # current_app.logger.info("配置信息")
    # current_app.logger.warn("警告")
    # current_app.logger.error("错误信息")
    return  "this is index"