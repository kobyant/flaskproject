#coding:utf8
import json

from flask import current_app, jsonify
from flask import g
from flask import request

from ihome import constants
from ihome import redis_store, db
from ihome.api_1_0 import api
from ihome.lib.upload_image import upload_image
from ihome.models import Area, House, Facility, HouseImage, User
from ihome.utils.commons import required_login
from ihome.utils.response_code import RET

#功能描述: 获取城区信息
#请求路径: /api/v1_0/areas
#请求方式: GET
#请求参数: 无
@api.route('/areas')
def get_area():
    #0.先到redis中,获取城区信息
    try:
        area_json = redis_store.get("areas_info")
    except Exception as e:
        current_app.logger.error(e)
        area_json = None

    if area_json is None:
        #1.获取城区数据(列表)
        try:
            areas_list = Area.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DATAERR,errmsg="城区查询失败")

        #2.将城区的对象信息转成字典信息
        areas = []
        for area in areas_list:
            areas.append(area.to_dict())

        #2.1保存到redis中
        area_json = json.dumps(areas)
        try:
            redis_store.setex("areas_info",3600,area_json)
        except Exception as e:
            current_app.logger.error(e)

    #将json字符串转成字典
    areas_dict = json.loads(area_json)

    #3.返回
    return jsonify(errno=RET.OK,errmsg="获取成功",data={"areas":areas_dict})


#功能描述: 保存房屋的基本信息,设施信息
#请求路径:/api/v1_0/houses/info
#请求方式:POST
#请求参数:基本信息,设施信息
@api.route('/houses/info',methods=["POST"])
@required_login
def save_house_info():
    #1.获取参数
    req_data = request.data
    req_dict = json.loads(req_data)

    title = req_dict.get("title")
    price = req_dict.get("price")
    area_id = req_dict.get("area_id")
    address = req_dict.get("address")
    room_count = req_dict.get("room_count")
    acreage = req_dict.get("acreage")
    unit = req_dict.get("unit")
    capacity = req_dict.get("capacity")
    beds = req_dict.get("beds")
    deposit = req_dict.get("deposit")
    min_days = req_dict.get("min_days")
    max_days = req_dict.get("max_days")

    #2.校验参数
    if not all([title,price,area_id,address,room_count,acreage,unit,capacity,beds,deposit,min_days,max_days]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")

    #校验单价和押金
    try:
        price = float(price)
        deposit = float(deposit)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="参数填写有误")

    #3.根据参数创建房屋对象
    house =  House(
        user_id = g.user_id,
        title=title,
        price = price,
        area_id = area_id,
        address = address,
        room_count = room_count,
        acreage = acreage,
        unit = unit,
        capacity = capacity,
        beds = beds,
        deposit = deposit,
        min_days = min_days,
        max_days = max_days
    )

    #设置房屋的设施信息
    facility_id_list = req_dict.get("facility")
    if facility_id_list is not None:
        try:
           facilisty_list = Facility.query.filter(Facility.id.in_(facility_id_list)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="数据库查询异常")

    if facilisty_list is not None:
        house.facilities = facilisty_list

    #4.将房屋对象保存到数据库中
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.SESSIONERR,errmsg="保存失败")

    #5.返回
    return jsonify(errno=RET.OK,errmsg="保存成功",data={"house_id":house.id})


#功能描述: 上传图片
#请求路径: /api/v1_0/houses/image
#请求方式: POST
#请求参数: 房屋的id, 图片
@api.route('/houses/image',methods=["POST"])
@required_login
def save_house_image():
    #1.获取参数(房屋的id,图片)
    house_id = request.form.get("house_id")
    house_image = request.files.get("house_image")

    #2.校验是否为空
    if not all([house_id,house_image]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数有误")


    #3.根据房屋id,查出对应的房屋对象
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="没有该房子")


    #4.上传图片到七牛云空间,获取到图片名字
    try:
        image_name = upload_image(house_image.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg="上传图片错误")


    #5.创建图片对象
    image = HouseImage(
        house_id = house.id,
        url = image_name
    )

    #6.给房屋设置默认图片
    if not house.index_image_url:
        house.index_image_url = image_name

    #7.将房屋图片对象保存到数据库中
    try:
        db.session.add(image)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="保存图片失败")


    #8.返回,带上图片的完整路径
    image_url = constants.QI_NIU_DOMAIN + image_name
    return jsonify(errno=RET.OK,errmsg="上传图片成功",data={"image_url":image_url})


#功能描述: 　获取我的房源
#请求路径:　/api/v1_0/user_houses
#请求方式： GET
#请求参数： 无
@api.route('/user/houses')
@required_login
def get_house_info():
    #1.获取参数（获取用户ｉｄ）
    user_id = g.user_id

    #2.获取和用户相关的所有房屋
    try:
        user = User.query.get(user_id)
        houses = user.houses
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR,errmsg="获取失败")

    #3.将房屋的对象信息，拼接成字典内容
    house_list = []
    if houses:
        for house in houses:
            house_list.append(house.get_house_basicInfo())

    #4.返回
    return jsonify(errno=RET.OK,errmsg="获取成功",data={"houses":house_list})



#功能描述: 获取房屋首页信息
#请求路径: /api/v1_0/houses/index
#请求方式: GET
#请求参数: 无
@api.route('/houses/index')
def get_house_index():
    #1.从redis中获取房屋展示的图片信息
    try:
        house_index_imageData = redis_store.get("house_index_image")
    except Exception as e:
        current_app.logger.error(e)


    #2.判断是否存在
    if house_index_imageData:
        house_index_dict = json.loads(house_index_imageData)
        return jsonify(errno=RET.OK,errmsg="获取成功",data=house_index_dict)


    #3.从数据库中获取房屋的信息(前五个)
    try:
       houses = House.query.order_by(House.order_count.desc()).limit(constants.HOUSE_INDEX_IMAGE)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取失败")

    if not houses:
        return jsonify(errno=RET.DATAERR,errmsg="获取房屋信息失败")

    #4.将房屋的信息拼接成字典
    house_dict = []
    for house in houses:
        house_dict.append(house.get_house_basicInfo())

    #5.存储到redis中
    try:
        redis_store.setex("house_index_image",constants.HOUSE_INDEX_IMAGE_EXPIRES,json.dumps(house_dict))
    except Exception as e:
        current_app.logger.error(e)

    #6.返回
    return jsonify(errno=RET.OK,errmsg="获取成功",data=house_dict)













#请求功能:获取方法全部信息
#请求路径:/api/v1_0/houses/index
#请求方式:
#请求参数:
@api.route('/houses/<int:house_id>')
@required_login
def get_house_detail(house_id):
    #1.获取到用户的id
    user_id = g.user_id

    #2.获取redis中的房屋详情
    try:
        house_detail = redis_store.get("house_detail_%s"%house_id)
    except Exception as e:
        current_app.logger.error(e)

    #3.判断redis中是否有house_detail详情
    if house_detail:
        house_dict = json.loads(house_detail)
        return jsonify(errno=RET.OK,errmsg="获取成功",data=house_dict)

    #4.根据house_id查询房屋对象
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询失败")

    #5.判断房子是否存在
    if not house:
        return jsonify(errno=RET.DATAERR,errmsg="该房子不存在")

    #使用房子对象拼接成字典



    #6.存储房子详情信息数据到redis中
    try:
        redis_store.setex("house_detail_%s"%house_id,constants.HOUSE_DETAIL_EXPIRES,json.dumps(house.house_all_dict()))
    except Exception as e:
        current_app.logger.error(e)


    #7.返回信息给前段
    return jsonify(errno=RET.OK,errmsg="查询成功",data=json.loads(house.house_all_dict()))


