#coding:utf8
"""
配置信息:
数据库
redis
session
csrf
模型
...
"""""
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from ihome import create_app, db

#1.获取app对象
app = create_app("develop")

#2.创建app管理对象,数据库迁移脚本
manager = Manager(app)
Migrate(app,db)
manager.add_command("db",MigrateCommand)

if __name__ == '__main__':
    manager.run()