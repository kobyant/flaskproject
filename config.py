#coding:utf8
import redis

class Config(object):
    """配置信息"""
    # SECRET_KEY = "kdhfkjfeflk898u83984934"
    SECRET_KEY = "xhosido*F(DHSDF*D(SDdslfhdos"
    # 配置数据库
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/ihome3"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 配置redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # flask_session配置信息
    SESSION_TYPE = "redis" # 保存的类型是redis
    SESSION_USE_SIGNER = True # 保存的时候以加密的方式
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 传递redis实例对象
    PERMANENT_SESSION_LIFETIME = 86400  # 默认session在redis中的有效时间


#在实际的开中会涉及到开发环境和测试环境,用到的参数可能不一样
#测试环境
class Development(Config):
    DEBUG = True

#正式环境
class Prodution(Config):
    pass

#通过配置字典获取对应的开发环境
config_dict = {
    "develop": Development,
    "product":Prodution
}


