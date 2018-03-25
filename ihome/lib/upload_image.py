#coding:utf8

from qiniu import Auth, put_file, etag, urlsafe_base64_encode,put_data
import qiniu.config

#需要填写你的 Access Key 和 Secret Key
access_key = 'v3n5FPnRvLujRroKe3X9FxjMSgtWCmMWBeharusu'
secret_key = 'd3uJUlaQ9iKh0b5XkhU-Tlx5hjrDiWDDeHA4xotw'

def upload_image(data):
    #构建鉴权对象
    q = Auth(access_key, secret_key)

    #要上传的空间
    bucket_name = 'ihome4'

    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    # ret, info = put_file(token, None, localfile)
    ret, info = put_data(token, None, data)

    #判断
    if info.status_code == 200:
        #上传成功,返回图片名字
        return ret.get("key")
    else:
        raise Exception("上传失败")

# if __name__ == '__main__':
#     try:
#         #读取图片的二进制数据
#         file = open("./33.jpg","rb")
#         data = file.read()
#         upload_image(data)
#     except Exception as e:
#         print "上传图片异常"