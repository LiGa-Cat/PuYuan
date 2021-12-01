from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, response
from django.contrib import auth
from .models import *
from .models import Blood_sugar
from friend.models import *
from datetime import date, datetime, time
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from user.models import *

# Create your views here.


@csrf_exempt
def blood_pressure(request):  # 上傳血壓測量結果!
    if request.method == 'POST':
        # data = json.loads(bytes.decode(request.body,'Utf-8')) #request.body datatype is byte ，json轉換python
        systolic = request.POST["systolic"]
        diastolic = request.POST["diastolic"]
        pulse = request.POST["pulse"]
        Time = datetime.now().strftime("%Y-%m-%d %T")  # "%Y-%m-%d,%H:%M:%S"%Y-%m-%d,%T
        try:
            pre = Blood_pressure.objects.create(
                uid=request.user.id, systolic=systolic, diastolic=diastolic, recorded_at=Time, pulse=pulse)
            output = {"status": "0",
                      "id": pre.id,
                      "user_id": pre.uid,
                      "systolic": pre.systolic,
                      "diastolic": pre.diastolic,
                      "pulse": pre.pulse,
                      "recorded_at": str(pre.recorded_at)
                      }
            print("新增血壓成功")
        except Exception as e:
            print("00")
            print(e)
            output = {"status": "1"}
    return JsonResponse(output)


@csrf_exempt
def body_weight(request):  # 上傳體重測量結果!
    if request.method == 'POST':
        # data = json.loads(bytes.decode(request.body,'Utf-8')) #request.body datatype is byte ，json轉換python
        # "%Y-%m-%d,%H:%M:%S"%y-%m-%d,%T
        Time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        weight = request.POST['weight']
        body_fat = request.POST['body_fat']
        bmi = request.POST['bmi']
        # recorded_at = data['recorded_at']
        # recorded_at = recorded_at.replace("%20", " ")
        # recorded_at = recorded_at.replace("%3A", ":")
        try:
            Weight.objects.create(
                uid=request.user.id, weight=weight, recorded_at=Time, body_fat=body_fat, bmi=bmi)
            output = {"status": "0"}
            print("新增體重成功")
        except Exception as e:
            print(e)
            output = {"status": "1"}
    return JsonResponse(output)


@csrf_exempt
def blood_sugar(request):  # 上傳血糖測量結果!(1120_1435)
    if request.method == 'POST':
        data = request.POST
        print("bloodsuger", data)
        timeperiod = int(request.POST['timeperiod'])
        # print("timeperiod",timeperiod)
        # print(type(timeperiod))
        timeperiod_list = ['晨起', '早餐前', '早餐後',
                           '午餐前', '午餐後', '晚餐前', '晚餐後', '睡前']
        timeperiod_list = timeperiod_list[(timeperiod-1) % 8]
        sugar = request.POST['sugar']
        Time = datetime.now().strftime("%Y-%m-%d %T")
        try:
            Blood_sugar.objects.create(
                uid=request.user.id, sugar=sugar, timeperiod=timeperiod, recorded_at=Time)
            output = {"status": "0"}
            print("新增血糖成功")
        except Exception as e:
            print(e)
            output = {"status": "1"}
    return JsonResponse(output)


@csrf_exempt
def last_upload(request):  # 最後上傳時間!
    uid = request.user.id
    print(uid)
    upload = []
    if request.method == 'GET':
        if Blood_pressure.objects.filter(uid=uid):
            pre = Blood_pressure.objects.filter(uid=uid).latest('recorded_at')
            pre = str(pre.recorded_at)
            upload.append({"blood_pressure": pre})
        if Weight.objects.filter(uid=uid):
            wei = Weight.objects.filter(uid=uid).latest('recorded_at')
            wei = str(wei.recorded_at)
            upload.append({"weight": wei})
        if Blood_sugar.objects.filter(uid=uid):
            sug = Blood_sugar.objects.filter(uid=uid).latest('recorded_at')
            sug = str(sug.recorded_at)
            upload.append({"blood_sugar": sug})
        if Diary_diet.objects.filter(uid=uid):
            die = Diary_diet.objects.filter(uid=uid).latest('recorded_at')
            die = str(die.recorded_at)
            upload.append({"diet": die})
        output = {
            "status": "0",
            "last_upload": upload
        }
    else:
        output = {"status": "1"}
    return JsonResponse(output)


@csrf_exempt
def records(request):  # 上一筆紀錄資訊!+刪除日記記錄!
    id = request.user.id
    # data = json.loads(bytes.decode(request.body,"utf-8"))
    output = {"status": "1"}
    data = request.GET
    if request.method == 'POST':
        if Blood_pressure.objects.filter(uid=id):
            pre = Blood_pressure.objects.filter(uid=id).latest('recorded_at')
            output["Blood_pressure"] = {
                "id": pre.id,
                "user_id": pre.id,
                "systolic": pre.systolic,
                "diastolic": pre.diastolic,
                "pulse": pre.pulse,
                "recorded_at": str(pre.recorded_at)
            }
        if Weight.objects.filter(uid=id):
            wei = Weight.objects.filter(uid=id).latest('recorded_at')
            output["weights"] = {
                "id": wei.id,
                "user_id": wei.uid,
                "weight": wei.weight,
                "body_fat": wei.body_fat,
                "bmi": wei.bmi,
                "recorded_at": str(wei.recorded_at)
            }
        if Blood_sugar.objects.filter(uid=id):
            sug = Blood_sugar.objects.filter(uid=id).latest('recorded_at')
            output["blood_sugars"] = {
                "id": sug.id,
                "user_id": sug.id,
                "sugar": int(sug.sugar),
                "timeperiod": int(sug.timeperiod),
                "recorded_at": str(sug.recorded_at)
            }
        timeperiod_list = ['晨起', '早餐前', '早餐後',
                           '午餐前', '午餐後', '晚餐前', '晚餐後', '睡前']
        diets = request.POST['diets']
        diets = timeperiod_list[(int(diets)-1) % 8]
        output = {"status": "0"}
    if request.method == 'DELETE':  # 刪除日記記錄!
        print("111111111", request.GET)
        print("222222222", request.POST)
        print("333333333", request.body)
        # user_id=request.user.id
        # print(user_id)
        if request.GET.get("blood_pressures[]"):
            print("555555")
            # data_list = request.GET.getlist("blood_pressures[]")  #get 輸入 url 參數 blood_pressures = id
            # print("data_list",data_list)
            # for data in data_list:
            blood_blood_pressures_id = request.GET.get("blood_pressures[]")
            print(blood_blood_pressures_id)
            Blood_pressure.objects.filter(id=blood_blood_pressures_id).delete()
            print("血壓紀錄刪除成功")
            output = {"status": "0"}
        if request.GET.getlist("weights[]"):
            # data_list = request.GET.getlist("weights[]")
            # for data in data_list:
            weights_id = request.GET.get("weights[]")
            print(weights_id)
            Weight.objects.filter(id=weights_id).delete()
            output = {"status": "0"}
        if request.GET.getlist("blood_sugars[]"):
            # data_list = request.GET.getlist("blood_sugars[]")
            # for data in data_list:
            blood_sugars_id = request.GET.get("blood_sugars[]")
            print(blood_sugars_id)
            data = Blood_sugar.objects.filter(id=blood_sugars_id).delete()
            print(data)
            print("血糖紀錄刪除成功")
            output = {"status": "0"}
        if request.GET.getlist("diets[]"):
            # data_list = request.GET.getlist("diets")
            # for data in data_list:
            diets_id = request.GET.get("diets[]")
            Diary_diet.objects.filter(id=diets_id).delete()
            output = {"status": "0"}
    return JsonResponse(output)


@csrf_exempt
def diary_list(request):  # 日記列表資料!
    print("data11", request.GET)
    uid = request.user.id
    date = request.GET.get("date")
    if request.method == "GET":
        if date:
            if Blood_pressure.objects.filter(uid=uid, date=date):
                blood_pressures = Blood_pressure.objects.filter(
                    uid=uid, date=date)
                # print("blood_pressures_list", blood_pressures)
                if blood_pressures != None:
                    for blood_pressure in blood_pressures:
                        r = {
                            "id": blood_pressure.id,
                            "user_id": blood_pressure.uid,
                            "systolic": blood_pressure.systolic,
                            "diastolic": blood_pressure.diastolic,
                            "pulse": blood_pressure.pulse,
                            "recorded_at": str(blood_pressure.recorded_at),
                            "type": "blood_pressure"
                        }
                        output = {"status": "0", "diary": r}
                    # diary.append(r)
            if Weight.objects.filter(uid=uid, date=date):
                weights = Weight.objects.filter(uid=uid, date=date)
                if weights != None:
                    for weight in weights:
                        r = {
                            "id": weight.id,
                            "user_id": weight.uid,
                            "weight": weight.weight,
                            "body_fat": weight.body_fat,
                            "bmi": weight.bmi,
                            "recorded_at": str(weight.recorded_at),
                            "type": "weight"
                        }
                        output = {"status": "0", "diary": r}
                        # diary.append(r)
            if Blood_sugar.objects.filter(uid=uid, date=date):
                blood_sugars = Blood_sugar.objects.filter(uid=uid, date=date)
                # print("12121121212", blood_sugars)
                if blood_sugars != None:
                    for blood_sugar in blood_sugars:
                        r = {
                            "id": blood_sugar.id,
                            "user_id": blood_sugar.uid,
                            "sugar": int(blood_sugar.sugar),
                            "timeperiod": int(blood_sugar.timeperiod),
                            "recorded_at": str(blood_sugar.recorded_at),
                            "type": "blood_sugar"
                        }
                        output = {"status": "0", "diary": r}
                        # diary.append(r)
            if Diary_diet.objects.filter(uid=uid, date=date):
                diary_diets = Diary_diet.objects.filter(uid=uid, date=date)
                if diary_diets != None:
                    for diary_diet in diary_diets:
                        if UserCare.objects.filter(uid=uid, date=date):
                            reply = UserCare.objects.filter(
                                member_id=0, date=date).latest('updated_at')
                            r = {
                                "id": diary_diet.id,
                                "user_id": diary_diet.uid,
                                "description": diary_diet.description,
                                "meal": int(diary_diet.meal),
                                "tag": diary_diet.tag,
                                "image": diary_diet.image_count,
                                "type": "diet",
                                "location":
                                        {
                                            "lat": diary_diet.lat,
                                            "lng": diary_diet.lng
                                },
                                "recorded_at": str(diary_diet.recorded_at),
                                "reply": reply.message
                            }
                        # else:
                        #     r = {
                        #         "id": diary_diet.id,
                        #         "user_id": diary_diet.uid,
                        #         "description": diary_diet.description,
                        #         "meal": int(diary_diet.meal),
                        #         "tag": diary_diet.tag,
                        #         "image": diary_diet.image_count,
                        #         "type": "diet",
                        #         "location":
                        #                 {
                        #                     "lat": diary_diet.lat,
                        #                     "lng": diary_diet.lng
                        #         },
                        #         "recorded_at": str(diary_diet.recorded_at),
                        #     }
                            output = {"status": "0", "diary": r}
                        # diary.append(r)
            if (len(Blood_pressure.objects.filter(uid=uid, date=date)) != 0) or (len(Diary_diet.objects.filter(uid=uid, date=date)) != 0) or (len(Blood_sugar.objects.filter(uid=uid, date=date)) != 0) or (len(Weight.objects.filter(uid=uid, date=date)) != 0):
                print("1212121121")
                output = {"status": "0", "diary": r}
            else:
                output = {"status": "1"}
        else:
            output = {"status": "1"}
    return JsonResponse(output)


@csrf_exempt
def diary_diet(request):  # 飲食日記!
    uid = request.user.id
    print(request.POST)
    if request.method == 'POST':
        # data = json.loads(bytes.decode(request.body,"utf-8"))
        # data = request.POST
        # print("日記資料",data)
        # data1 = request.body
        # print("日記資料1",data1)
        # data2 = request.FILES
        # print("日記資料2",data2)
        # data3 = HttpRequest.body
        # print("日記資料3",data3)
        # tag = request.POST["tag[][]"]
        # print("tag",tag)
        description = request.POST["description"]
        lat = request.POST["lat"]
        lng = request.POST["lng"]
        image_count = request.POST["image"]
        meal = (int(request.POST["meal"])-1) % 3
        meal_list = ['早餐', '午餐', '晚餐']
        meal_list = meal_list[meal]
        # Time = datetime.now().strftime("%Y-%m-%d %T")
        recorded_at = request.POST['recorded_at']
        # print("日記時間",recorded_at)
        # recorded_at = recorded_at.replace("%20", " ")
        # recorded_at = recorded_at.replace("%3A", ":")
        try:
            if request.POST["tag[][]"]:
                tag = request.POST["tag[][]"]
                Diary_diet.objects.create(uid=uid, description=description, meal=meal, tag=tag,
                                          image_count=image_count, lat=lat, lng=lng, recorded_at=recorded_at)
                print("日記新增成功")
            else:
                Diary_diet.objects.create(uid=uid, description=description, meal=meal,
                                          image_count=image_count, lat=lat, lng=lng, recorded_at=recorded_at)
        except Exception as e:
            print(e)
            output = {"status": "1"}
        else:
            output = {
                "status": "0", "image_url": "http://211.23.17.100:3001/diet_1_2020-08-17_11:11:11_0"}
    return JsonResponse(output, safe=False)


@csrf_exempt
def care(request):  # 送出關懷諮詢!(uid送給別人)
    uid = request.user.id
    print(uid)
    print("POST", request.POST)
    recorded_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    output = {"status": "1"}
    if request.method == 'POST':
        # data = request.body
        # data = str(data, encoding="utf-8")
        # data = {
        #     i.split('=')[0]: i.split('=')[1]
        #     for i in data.replace("%40","@").split('&') if i.split('=')[1]
        # }
        # data = json.loads(bytes.decode(request.body,"utf-8"))
        message = request.POST['message']
        # recorded_at = request.POST['recorded_at']
        # recorded_at = recorded_at.replace("%20", " ") #特殊符號轉換
        # recorded_at = recorded_at.replace("%3A", ":")
        friend_list = Friend_data.objects.filter(uid=uid, status=1)
        print(friend_list)
        try:
            for friend_data in friend_list:
                UserCare.objects.create(uid=uid, member_id=friend_data.friend_type,
                                        reply_id=friend_data.relation_id, message=message, updated_at=recorded_at)
                UserCare.objects.create(uid=friend_data.relation_id, member_id=friend_data.friend_type, reply_id=uid, message=(
                    "from :", uid, message), updated_at=recorded_at)  # 新增
                output = {"status": "0"}
                print("送出關懷成功")
        except:
            output = {"status": "1"}
    if request.method == 'GET':  # 獲取關懷諮詢!(我關懷別人)
        usercares = UserCare.objects.filter(
            reply_id=uid)  # 利用我(uid)給別人的關懷資訊，取得被我送邀請人的資料
        cares = []
        for usercare in usercares:
            r = {
                "id": usercare.id,
                "user_id": usercare.uid,
                "member_id": usercare.member_id,
                "reply_id": usercare.reply_id,
                "message": usercare.message,
                "created_at": str(usercare.created_at),
                "updated_at": str(usercare.updated_at)
            }
            cares.append(r)
        output = {"status": "0", "cares": cares}
    return JsonResponse(output)


@csrf_exempt
def notification(request):  # 親友團通知!
    uid = request.user.id
    if request.method == 'POST':
        nowtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # data = request.body
        # data = str(data, encoding="utf-8")
        # data = {
        #     i.split('=')[0]: i.split('=')[1]
        #     for i in data.replace("%40","@").split('&') if i.split('=')[1]
        # }
        data = json.loads(bytes.decode(request.body, "utf-8"))
        message = data['message']
        try:
            friend_list = Friend_data.objects.filter(
                uid=uid, friend_type=1, status=1)
            for friend in friend_list:
                Notification.objects.create(
                    uid=uid, member_id=1, reply_id=friend.relation_id, message=message, updated_at=nowtime)
                output = {"status": "0"}
        except:
            output = {"status": "1"}
        return JsonResponse(output, safe=False)
