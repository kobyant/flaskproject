#coding=utf-8
from flask import current_app

from CCPRestSDK import REST
import ConfigParser

#主帐号
accountSid= '8a216da861f5a257016204a0d5ac06f0';

#主帐号Token
accountToken= '07885bc11c584f1ba6342a3cc8d7d2a4';

#应用Id
appId='8a216da861f5a257016204a0d60406f6';

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com';

#请求端口 
serverPort='8883';

#REST版本号
softVersion='2013-12-26';

#将REST初始化的方式,变成单例模式,只需要被初始化一次即可正常发送短信(需求)
# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：['12','34']，如不需替换请填 ''
# @param $tempId 模板Id
class CCP(object):
    #1.编写__new__方法
    #2.判断CCP中是否有instance实例
    #3.如果没有创建CCP的对象赋值给instance
    def __new__(cls):
        if not hasattr(cls,"instance"):
            obj = super(CCP,cls).__new__(cls)

            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)

            cls.instance = obj
        return cls.instance

    #发送短信的实例方法
    def sendTemplateSMS(self,to, datas, tempId):

        try:
            result = self.rest.sendTemplateSMS(to, datas, tempId)
        except Exception as e:
            current_app.logger.error(e)

        if result.get("statusCode") == "000000":
            #0表示发送成功
            return 0
        else:
            #-1表示发送失败
            return -1


#封装到CCP中之后发送短信的方式
# ccp = CCP()
# ccp.sendTemplateSMS(...)

#sendTemplateSMS(手机号码,内容数据,模板Id)
if __name__ == '__main__':
    ccp = CCP()
    ccp.sendTemplateSMS("18210094341",["123456",5],1)