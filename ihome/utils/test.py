#coding:utf8
import json
from functools import wraps

"""
在使用装饰器的时候,不应该改变原有视图的结构,所以可以使用
@wraps在内层函数中进行修饰
"""

def require_login(view_func):
    @wraps(view_func)
    def wrapper(*args,**kwargs):
        """内层函数装饰器"""
        pass

    return wrapper


@require_login
def set_avatar():
    """设置头像"""
    pass


print set_avatar.__name__
print set_avatar.__doc__


#三目运算符
print 100 if False else 200


dict1 = {"name":"张三"}
dict2 = {"age":13}

array = [dict1,dict2]

arraystring = json.dumps(array)
print arraystring
print type(arraystring)


array_dict = json.loads(arraystring)
print array_dict
print type(array_dict)