#coding:utf8

#创建celery对象
from celery import Celery

from ihome.lib.ytx.SendTemplateSMS import CCP

app = Celery("ihome",broker="redis://127.0.0.1:6379")


@app.task
def send_template_sms(to, datas, tempId):
    ccp = CCP()
    ccp.sendTemplateSMS(to,datas,tempId)