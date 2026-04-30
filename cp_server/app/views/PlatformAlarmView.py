import os
import time
import base64
import random
from app.views.ViewsBase import *
from app.models import *
from app.utils.TarUtils import TarUtils
from app.utils.AlarmUtils import AlarmUtils
from app.utils.Utils import gen_random_code_s
from django.shortcuts import render, redirect
from app.utils.Utils import buildPageLabels
from app.utils.OSSystem import OSSystem


def f_getAlarmInfoByCode(alarm_code):
    alarm = PlatformAlarmModel.objects.filter(code=alarm_code).first()
    if alarm:
        video_count = alarm.video_count
        video_is_wav = 0
        if video_count > 0:
            videoUrl = g_config.storageDir_www + alarm.video_path
            if alarm.node_code:
                videoUrl += "&node_code=" + alarm.node_code
            if alarm.video_path.endswith("wav"):
                video_is_wav = 1
        else:
            videoUrl = ""

        image_count = alarm.image_count
        other_image_count = alarm.other_image_count

        if image_count > 0:
            imageUrl = g_config.storageDir_www + alarm.image_path
            if alarm.node_code:
                imageUrl += "&node_code=" + alarm.node_code
        else:
            imageUrl = "/static/images/720p.jpg"

        imageUrlArray = []
        if image_count > 0:
            imageUrlArray.append(imageUrl)
            image_path = alarm.image_path

            if other_image_count > 0:
                dot_pos = image_path.rfind(".")
                if dot_pos > 0:
                    image_path_l = image_path[:dot_pos]
                    image_path_r = image_path[dot_pos + 1:]
                    for i in range(other_image_count):
                        __imageUrl = g_config.storageDir_www + "%s_%d.%s" % (image_path_l, (i + 1), image_path_r)
                        if alarm.node_code:
                            __imageUrl += "&node_code=" + alarm.node_code
                        imageUrlArray.append(__imageUrl)

        alarm_info = {
            "id": alarm.id,
            "code": alarm.code,
            "stream_code": alarm.stream_code,
            "control_code": alarm.control_code,
            "flow_code": alarm.flow_code,
            "flow_name": alarm.flow_name,
            "flag": alarm.flag,
            "draw_type": alarm.draw_type,
            "video_count": video_count,
            "video_is_wav": video_is_wav,
            "videoUrl": videoUrl,
            "image_count": image_count,
            "imageUrl": imageUrl,
            "imageUrlArray": imageUrlArray,
            "desc": alarm.desc,
            "create_time": alarm.create_time,
            "state": alarm.state,
            "review_remark": alarm.review_remark
        }
        return alarm_info

    return None


def index(request):
    context = {
        "settings": g_settings.data
    }

    stream_data = g_database.select("select stream_code as code,stream_nickname as nickname from cp_platform_stream where state=0 ")
    flow_data = g_database.select("select flow_code as code,flow_name as name from cp_platform_algorithm_flow where state=0 ")

    context["streams"] = stream_data
    context["flows"] = flow_data

    now_date = datetime.now()
    context["startDate"] = (now_date - timedelta(days=6)).strftime("%Y-%m-%d")
    context["endDate"] = now_date.strftime("%Y-%m-%d")

    return render(request, 'app/platform/alarm/index.html', context)


def api_openIndex(request):
    ret = False
    msg = "未知错误"

    top_msg = ""
    data = []
    pageData = {}
    __check_ret, __check_msg = f_checkRequestSafe(request)
    if __check_ret:
        params = f_parseGetParams(request)
        page = params.get('p', 1)
        page_size = params.get('ps', 10)
        drawType = str(params.get('drawType', "-1"))
        controlCode = str(params.get('controlCode', "-1"))
        streamCode = str(params.get('streamCode', "-1"))
        flowCode = str(params.get('flowCode', "-1"))

        dateRange = str(params.get('dateRange'))

        startTimestamp = 0
        endTimestamp = 0
        try:
            dateRangeV = dateRange.split("to")
            if len(dateRangeV) == 2:
                startDate = dateRangeV[0].strip()
                endDate = dateRangeV[1].strip()
                startTimestamp = int(datetime.strptime(startDate, "%Y-%m-%d").timestamp())
                endTimestamp = int(datetime.strptime(endDate, "%Y-%m-%d").timestamp())
        except:
            pass

        try:
            page = int(page)
        except:
            page = 1

        try:
            page_size = int(page_size)
            if page_size < 1:
                page_size = 1
        except:
            page_size = 10

        search_fields = []
        if drawType != "-1":
            search_fields.append(" cp_platform_alarm.draw_type = {field} ".format(field=int(drawType)))
        if controlCode != "-1":
            search_fields.append(" cp_platform_alarm.control_code = '{field}' ".format(field=controlCode))
        if streamCode != "-1":
            search_fields.append(" cp_platform_alarm.stream_code = '{field}' ".format(field=streamCode))
        if flowCode != "-1":
            search_fields.append(" cp_platform_alarm.flow_code = '{field}' ".format(field=flowCode))

        if startTimestamp > 0 and endTimestamp > 0:
            search_fields.append(
                " cp_platform_alarm.create_timestamp>={startTimestamp} and cp_platform_alarm.create_timestamp<={endTimestamp} ".format(
                    startTimestamp=startTimestamp, endTimestamp=endTimestamp))

        where_count = "where cp_platform_alarm.state!=5 "
        if len(search_fields) > 0:
            where_count += " and " + "and".join(search_fields)

        where_unread_count = "where cp_platform_alarm.state=0 "
        if len(search_fields) > 0:
            where_unread_count += " and " + "and".join(search_fields)

        count = g_database.select("select count(id) as count from cp_platform_alarm %s" % where_count)
        count = int(count[0]["count"])

        unread_count = 0
        if count > 0:
            skip = (page - 1) * page_size
            __data = g_database.select("select cp_platform_alarm.* from cp_platform_alarm %s order by cp_platform_alarm.id desc limit %d,%d " % (
                where_count, skip, page_size))

            for d in __data:
                video_count = d["video_count"]
                if video_count > 0:
                    videoUrl = g_config.storageDir_www + d["video_path"]
                    if d.get("node_code"):
                        videoUrl += "&node_code=" + d["node_code"]
                else:
                    videoUrl = ""

                image_count = d["image_count"]
                if image_count > 0:
                    imageUrl = g_config.storageDir_www + d["image_path"]
                    if d.get("node_code"):
                        imageUrl += "&node_code=" + d["node_code"]
                else:
                    imageUrl = "/static/images/720p.jpg"

                data.append({
                    "id": d["id"],
                    "code": d["code"],
                    "video_count": video_count,
                    "videoUrl": videoUrl,
                    "image_count": image_count,
                    "imageUrl": imageUrl,
                    "desc": d["desc"],
                    "create_time": d["create_time"],
                    "create_time_str": d["create_time"].strftime("%Y-%m-%d %H:%M:%S"),
                    "state": d["state"],
                    "flow_code": d["flow_code"],
                    "flow_name": d["flow_name"],
                })

            unread_count = g_database.select("select count(id) as count from cp_platform_alarm %s" % where_unread_count)
            if len(unread_count) > 0:
                unread_count = int(unread_count[0]["count"])
            else:
                unread_count = 0

        page_num = int(count / page_size)
        if count % page_size > 0:
            page_num += 1
        pageLabels = buildPageLabels(page=page, page_num=page_num)
        pageData = {
            "page": page,
            "page_size": page_size,
            "page_num": page_num,
            "count": count,
            "pageLabels": pageLabels
        }
        if count > 0:
            top_msg = "总计%d条，未处理%d条" % (count, unread_count)
        else:
            top_msg = "暂无数据"

        ret = True
        msg = "success"
    else:
        msg = __check_msg

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data,
        "pageData": pageData,
        "top_msg": top_msg
    }
    return f_responseJson(res)


def edit(request):
    ret = False
    msg = "未知错误"

    params = f_parsePostParams(request)
    g_logger.info("PlatformAlarmView.edit() params:%s" % str(params))

    code = params.get("code")
    state = params.get("state", 1)
    review_remark = params.get("review_remark", "")

    alarm = PlatformAlarmModel.objects.filter(code=code)
    if len(alarm) > 0:
        alarm = alarm[0]
        alarm.state = state
        alarm.review_remark = review_remark
        alarm.save()
        ret = True
        msg = "success"
    else:
        msg = "the data does not exist"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("PlatformAlarmView.edit() res:%s" % str(res))
    return f_responseJson(res)


def api_openAdd(request):
    ret = False
    msg = "未知错误"

    if request.method == 'POST':
        params = f_parsePostParams(request)
        g_logger.info("PlatformAlarmView.openAdd() params:%s" % str(params))

        try:
            nodeCode = params.get("nodeCode", "node").strip()

            streamNickname = params.get("streamNickname", "").strip()
            streamDeviceId = params.get("streamDeviceId", "").strip()
            streamApp = params.get("streamApp", "").strip()
            streamName = params.get("streamName", "").strip()
            streamName = params.get("streamName", "").strip()
            streamCode = params.get("streamCode", "").strip()
            controlCode = params.get("controlCode", "").strip()
            flowCode = params.get("flowCode", "").strip()
            flowName = params.get("flowName", "").strip()
            flowMode = int(params.get("flowMode", 0))
            drawType = int(params.get("drawType", 0))
            flag = params.get("flag", "").strip()
            desc = params.get("desc", "").strip()
            videoCount = int(params.get("videoCount", 0))
            videoArray = params.get("videoArray")
            imageCount = int(params.get("imageCount", 0))
            imageArray = params.get("imageArray")
            imageDetects = params.get("imageDetects")
            extendParams = params.get("extendParams")
            createTime = params.get("createTime")

            if imageCount < 1:
                raise Exception("imageCount must be greater than 0")

            now_date = datetime.now()
            file_dir = "alarm/{nodeCode}/{controlCode}/{ymd}/{date}/{drawType}".format(
                nodeCode=nodeCode,
                controlCode=controlCode,
                ymd=now_date.strftime("%Y%m%d"),
                date=now_date.strftime("%Y%m%d%H%M%S") + str(random.randint(100, 999)),
                drawType=drawType
            )
            file_dir_abs = os.path.join(g_config.storageDir, file_dir)
            if not os.path.exists(file_dir_abs):
                os.makedirs(file_dir_abs)

            print("nodeCode",nodeCode)
            print("controlCode",controlCode)
            print("file_dir",file_dir)
            print("file_dir_abs",file_dir_abs)

            video_path = ""
            image_path = ""
            filename = now_date.strftime("%Y%m%d%H%M%S")
            if videoCount > 0:
                videoPath = videoArray[0]["videoPath"]
                if videoPath.endswith(".mp4"):
                    base64Str = videoArray[0]["base64Str"]
                    if base64Str and base64Str != "not enabled":
                        video_byte = base64.b64decode(base64Str)
                        print(videoCount, "视频序号:0")

                        video_path = "%s/%s" % (file_dir, "%s.mp4" % filename)
                        __video_path_abs = "%s/%s" % (file_dir_abs, "%s.mp4" % filename)
                        f = open(__video_path_abs, 'wb')
                        f.write(video_byte)
                        f.close()


            other_image_count = imageCount - 1 if imageCount > 0 else 0
            if imageCount > 0:

                for i in range(len(imageArray)):
                    base64Str = imageArray[i]["base64Str"]
                    # imagePath = imageArray[i]["imagePath"]
                    if base64Str and base64Str != "not enabled":
                        image_byte = base64.b64decode(base64Str)
                        print(imageCount, "图片序号:", i)
                        if i == 0:
                            image_path = "%s/%s" % (file_dir, "%s.jpg" % filename)
                            __image_path_abs = "%s/%s" % (file_dir_abs, "%s.jpg" % filename)
                            f = open(__image_path_abs, 'wb')
                            f.write(image_byte)
                            f.close()
                        else:
                            __other_image_path = "%s/%s" % (file_dir, "%s_%d.jpg" % (filename, i))
                            __other_image_path_abs = "%s/%s" % (file_dir_abs, "%s_%d.jpg" % (filename, i))
                            f = open(__other_image_path_abs, 'wb')
                            f.write(image_byte)
                            f.close()



            alarm = PlatformAlarmModel()
            alarm.sort = 0
            alarm.code = gen_random_code_s(prefix="alarm")
            alarm.draw_type = drawType
            alarm.flag = flag
            alarm.control_code = controlCode
            alarm.desc = desc
            alarm.video_path = video_path
            alarm.video_count = videoCount
            alarm.image_path = image_path
            alarm.image_count = imageCount
            alarm.other_image_count = other_image_count
            alarm.level = 0
            alarm.state = 0
            alarm.is_check = 0

            alarm.review_remark = ""
            alarm.stream_app = streamApp
            alarm.stream_name = streamName
            alarm.stream_code = streamCode
            alarm.flow_mode = flowMode
            alarm.flow_code = flowCode
            alarm.flow_name = flowName
            alarm.main_plate_color = 0
            alarm.main_plate_type = 0
            alarm.main_plate_no = ""
            alarm.main_track_max_code = ""
            alarm.main_track_max_custom_code = ""
            alarm.main_track_max_similary = 0
            alarm.expand1 = ""
            alarm.expand2 = ""

            alarm.create_time = now_date
            alarm.create_timestamp = int(time.time())
            alarm.last_update_time = now_date

            alarm.node_code = nodeCode
            alarm.save()

            msg = "success"
            ret = True

        except Exception as e:
            msg = "PlatformAlarmView.openAdd() error:%s" % str(e)
            g_logger.error(msg)

    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("PlatformAlarmView.openAdd() res:%s" % str(res))

    return f_responseJson(res)


def api_openInfo(request):
    ret = False
    msg = "未知错误"
    info = {}
    if request.method == 'GET':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parseGetParams(request)
            g_logger.info("PlatformAlarmView.openInfo() params:%s" % str(params))

            alarm_code = params.get("code", "")
            alarm_info = f_getAlarmInfoByCode(alarm_code=alarm_code)
            if alarm_info:
                info = alarm_info
                ret = True
                msg = "success"
            else:
                msg = "the data does not exist"
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    g_logger.info("PlatformAlarmView.openInfo() res:%s" % str(res))

    return f_responseJson(res)


def api_openHandle(request):
    ret = False
    msg = "未知错误"

    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            params = f_parsePostParams(request)
            g_logger.info("PlatformAlarmView.openHandle() params:%s" % str(params))

            alarm_ids_str = params.get("alarm_ids_str", "")
            handle = params.get("handle", None)
            alarm_utils = AlarmUtils(g_logger, g_database, g_config.storageDir)
            
            if handle == "deleteAll":
                data = g_database.select("select id,video_path,image_path from cp_platform_alarm where state!=5")
                count = len(data)
                if count > 0:
                    success_count = 0
                    file_error_count = 0
                    db_error_count = 0
                    
                    for d in data:
                        try:
                            # 先删除文件
                            if d.get("video_path"):
                                try:
                                    alarm_utils.clearAlarmFiles(d["video_path"], 0)
                                except Exception as e:
                                    file_error_count += 1
                                    g_logger.error("delete video file error: %s" % str(e))
                            
                            if d.get("image_path"):
                                try:
                                    alarm_utils.clearAlarmFiles(d["image_path"], 0)
                                except Exception as e:
                                    file_error_count += 1
                                    g_logger.error("delete image file error: %s" % str(e))
                            
                            # 再删除数据库记录
                            alarm_id = d["id"]
                            PlatformAlarmModel.objects.filter(id=alarm_id).delete()
                            success_count += 1
                            
                        except Exception as e:
                            db_error_count += 1
                            g_logger.error("delete alarm record error: %s" % str(e))
                    
                    # 生成详细的返回消息
                    if file_error_count == 0 and db_error_count == 0:
                        msg = "成功删除%d条数据及对应文件" % count
                        ret = True
                    else:
                        msg = "删除完成：成功%d条，文件删除失败%d个，数据库删除失败%d个" % (
                            success_count, file_error_count, db_error_count)
                        ret = True if success_count > 0 else False
                else:
                    msg = "暂无待删除数据"
                    
            elif handle == "delete":
                alarm_ids = alarm_ids_str.split(",")
                if len(alarm_ids) > 0:
                    success_count = 0
                    file_error_count = 0
                    db_error_count = 0
                    not_found_count = 0
                    
                    for alarm_id in alarm_ids:
                        # 去除空格并跳过空字符串
                        alarm_id = alarm_id.strip()
                        if not alarm_id:
                            continue
                        
                        try:
                            alarm = PlatformAlarmModel.objects.filter(id=alarm_id).first()
                            if alarm:
                                # 先删除文件
                                if alarm.video_path:
                                    try:
                                        alarm_utils.clearAlarmFiles(alarm.video_path, 0)
                                    except Exception as e:
                                        file_error_count += 1
                                        g_logger.error("delete video file error: %s" % str(e))
                                
                                if alarm.image_path:
                                    try:
                                        alarm_utils.clearAlarmFiles(alarm.image_path, 0)
                                    except Exception as e:
                                        file_error_count += 1
                                        g_logger.error("delete image file error: %s" % str(e))
                                
                                # 再删除数据库记录
                                alarm.delete()
                                success_count += 1
                            else:
                                not_found_count += 1
                                g_logger.warning("alarm id=%s not found" % alarm_id)
                                
                        except Exception as e:
                            db_error_count += 1
                            g_logger.error("delete alarm record error: %s" % str(e))

                    # 生成详细的返回消息
                    total = len(alarm_ids)
                    if file_error_count == 0 and db_error_count == 0 and not_found_count == 0:
                        msg = "成功删除%d条数据及对应文件" % success_count
                        ret = True
                    else:
                        msg_parts = []
                        if success_count > 0:
                            msg_parts.append("成功%d条" % success_count)
                        if not_found_count > 0:
                            msg_parts.append("未找到%d条" % not_found_count)
                        if file_error_count > 0:
                            msg_parts.append("文件删除失败%d个" % file_error_count)
                        if db_error_count > 0:
                            msg_parts.append("数据库删除失败%d个" % db_error_count)
                        msg = "；".join(msg_parts)
                        ret = True if success_count > 0 else False
                else:
                    msg = "请至少选择一条数据"
            else:
                msg = "不支持的操作类型"
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"
    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    g_logger.info("PlatformAlarmView.openHandle() res:%s" % str(res))
    return f_responseJson(res)


def api_openExport(request):
    ret = False
    msg = "未知错误"
    info = {}

    if request.method == 'POST':
        __check_ret, __check_msg = f_checkRequestSafe(request)
        if __check_ret:
            pass
        else:
            msg = __check_msg
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    g_logger.info("PlatformAlarmView.openExport() res:%s" % str(res))
    return f_responseJson(res)
