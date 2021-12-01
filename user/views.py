from json import decoder, loads
from django.db.models.query import RawQuerySet
from django.db.models.query_utils import PathInfo
from django.shortcuts import render
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from .models import *
from .models import UserSet
from django.core.mail import send_mail
import uuid
import base64
import json
import string
from random import *
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
import string
from datetime import datetime
from friend.models import *
from body.models import *
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from friend import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from PuYuan import settings
from .token import email_token
from .form import PersonalDefaultForm
import requests
import urllib.request
import re


# 註冊(1119 2215)
@csrf_exempt  # 避免csrfmiddleware驗證，未設置需生成csrf cookie
def register(request):
    if request.method == "POST":  # 判斷HTTP method
        try:
            account = request.POST["account"]  # 尋找key account的value
            password = request.POST["password"]  # 同上
            email = request.POST["email"]  # 同上
            random = Random()
            invite_code = "".join(random.sample('0123456789', 6))  # 生成邀請碼
            now = datetime.now()  # 生成時間
            Time = now.strftime("%Y-%m-%d,%H:%M:%S")  # 用字串轉日期格式顯示時間
            # 給account用uuid5生成uuid，
            uid = uuid.uuid3(uuid.NAMESPACE_DNS, account)
            same_name_user = UserProfile.objects.filter(
                username=account).first()
            if same_name_user is None:
                # 根據.model.userprofile create user資料表
                User = UserProfile.objects.create_user(
                    password=password, username=account, uid=uid, email=email, invite_code=invite_code)
                UserSet.objects.create(uid=uid, name=account, email=email,
                                       must_change_password=True, login_times=0, created_at=Time, updated_at=Time)
                id_number = User.id
                deflat.objects.create(
                    uid=uid, created_at=Time, updated_at=Time)
                Friend.objects.create(uid=id_number, invite_code=invite_code)
                medicalinformation.objects.create(uid=uid, created_at=Time)
                Notification.objects.create(uid=uid)
                # HbA1c.objects.create(uid=uid)
                message = {"status": "0"}
                print("註冊成功")
            else:
                message = {"status": "1"}
        except Exception as e:
            print("e", e)
            message = {"status": "1"}
        return JsonResponse(message)


@csrf_exempt
def login(request):  # 登入
    if request.method == "POST":
        # print("1212121")
        # data = request.body
        # data = bytes.decode(data,'UTF-8')    #使用UTF-8，將byte轉換成str ，也可使用str()
        # data = json.loads(data)    #json.load解析非str format json，loads 解析str
        try:
            # account = data['account']
            # password = data['password']
            account = request.POST["account"]
            password = request.POST["password"]
            # print("11111111111111111111")
            a = request.user.is_authenticated
            print("a", a)
            b = request.user.id
            print("b", b)
            # b=request.user.is_anonymous
            auth_obj = auth.authenticate(
                username=account, password=password)  # 驗證帳號對錯
            # print("登入狀態:", request.user.is_authenticated)
            # auth_obj = auth.authenticate(username=account, password=password)
            # print("登入資訊", auth_obj)
            # request.session.create()
            # auth.login(request, auth_obj)
            # message = {"status": "0",
            #            "token": request.session.session_key}  # 新增結束
            if auth_obj != None:  # 驗證是否有帳號已登入/新增開始
                auth_obj = auth.authenticate(
                    username=account, password=password)
                print(auth_obj)
                request.session.create()
                auth.login(request, auth_obj)
                message = {"status": "0",
                           "token": request.session.session_key}  # 新增結束
                print("成功登入")
                return JsonResponse(message)
            # if request.user.is_authenticated == True:
            #     message = {"帳號": "已登入"}
            #     print("帳號已登入")
            #     return JsonResponse(message)
            if auth_obj == None:
                message = {"帳號": "查無此帳號"}
                print("查無此帳號")
                return JsonResponse(message)
        except Exception as e:
            print("e", e)
            message = {"status": "1"}
        return JsonResponse(message)


@csrf_exempt
def logout(request):  # 登出
    try:
        auth.logout(request)
        message = {"status": "0"}
        print("成功登出")
        # return HttpResponseRedirect('auth')
    except:
        message = {"status": "1"}
    return JsonResponse(message)


@csrf_exempt
def send(request):  # 傳送驗證信(1119測試完成)
    if request.method == "POST":
        try:
            token = email_token()
            email = request.POST["email"]
            sender = settings.EMAIL_HOST_USER
            token_s = token.generate_validate_token(email)
            title = "普元血糖帳號驗證"
            meg = "\n".join(["{0}歡迎使用普元血糖app".format(email),
                            "請點選下列連結完成註冊:\n",
                             "".join((f"http://api/verification/send/{token_s}"))])
            send_mail(title, meg, sender, [email])
            message = {'status': '0', 'tokens': token_s}
        except Exception as e:
            print("e", e)
            message = {'status': '1'}
        return JsonResponse(message)


@csrf_exempt
def check(request, token):  # 信箱驗證
    if request.method == "POST":
        try:
            # print("11111111111")
            data = request.body
            # 使用UTF-8，將byte轉換成str ，也可使用str()
            data = bytes.decode(data, 'UTF-8')
            data = json.loads(data)  # json.load解析非str format json，loads 解析str
            email = data['email']
            # account = data['account']
            # print("2222222222")
            # token_use = email_token()
            print(token)
            token_use = email_token()
            email = token_use.confirm_validate_token(token)
            # print("22222233333")
            print(email)
            # print("33333333333333333")
            user = UserProfile.objects.get(email=email)
            print("user = ", user)
            print("4444444444444444444")
            user.is_active = True
            user.save()
            message = {"status": "0"}
        except:
            message = {"status": "1"}

        return JsonResponse(message)


@csrf_exempt
def forgot(request):  # 忘記密碼(找回)
    if request.method == "POST":
        # data = request.body
        # data = bytes.decode(data,'UTF-8')    #使用UTF-8，將byte轉換成str ，也可使用str()
        # data = json.loads(data)    #json.load解析非str format json，loads 解析str

        try:
            email = request.POST['email']
            user = UserProfile.objects.get(email=email)  # 利用email，取得使用者資訊
            userSet = UserSet.objects.get(uid=user.uid)
            chars = string.ascii_letters+string.digits  # 輸出所有字母(大小寫字母)，數字0~9
            new_pw = ''.join([choice(chars)for i in range(4)])  # 隨機密碼
            user.set_password(new_pw)  # 修改Usetprofile.password
            user.save()
            userSet.must_change_password = True  # 找過密碼
            title = "找回密碼"
            sender = settings.EMAIL_HOST_USER
            print("1111111")
            meg = "\n".join(["歡迎".format(user.username),
                             "新的密碼為:\n", new_pw])
            send_mail(title, meg, sender, [email])
            print("222222")
            message = {"status": "0"}
            print("忘記密碼成功")
        except Exception as e:
            print("e", e)
            message = {"status": "1"}
        return JsonResponse(message)


@csrf_exempt
def reset(request):  # 重設密碼(1120)
    if request.method == "POST":
        idd = request.user.id
        # print("idd",idd)
        user_uid = request.user.uid
        # print("iddd",user_uid)
        data2 = request.POST
        # print("data2",data2)
        # user = UserProfile.objects.get(id=s['_auth_user_id'])                              #找尋已驗證使用者資訊-2
        user = UserProfile.objects.get(uid=user_uid)  # 找尋已驗證使用者資訊-3
        # print("user",user)
        a = request.user.is_authenticated
        # print("a",a)
        # print("01010101")
        try:
            new_pw = request.POST['password']
            # print("12")
            user.set_password(new_pw)
            # print("34")
            user.must_change_password = False  # 找回密碼重設過
            user.save()
            message = {"status": "0"}
        except Exception as e:
            print("e", e)
            message = {"status": "1"}
        return JsonResponse(message)


@csrf_exempt
def registercheck(request):  # 註冊確認(1119測試完成)
    if request.method == 'GET':
        try:
            # user = UserProfile.objects.get(username=account)
            account = request.GET["account"]
            message = {'status': '0'}
        except Exception as e:
            print(e)
            message = {'status': '1'}
        return JsonResponse(message)


@csrf_exempt
def userset(request):
    if request.method == 'PATCH':  # 7.個人資訊(身高體重)上傳
        data = request.body
        data = bytes.decode(data, 'UTF-8')  # 使用UTF-8，將byte轉換成str ，也可使用str()
        data = re.split("&|=", data)
        print(data)
        '''
        # address = urllib.request.unquote(data[1])
        # birthday = data[3]
        # email = urllib.request.unquote(data[5])
        # gender = data[7]
        # height = data[9]
        # name = urllib.request.unquote(data[11])
        # phone = data[13]
        # weight = data[15]
        '''
        user = UserSet.objects.get(uid=request.user.uid)  # 登入後可直接取user值
        print(request.user.is_authenticated)
        try:
            if request.user.is_authenticated == True:
                # update method 1
                # print("1")
                # user.name = urllib.request.unquote(data[11])
                # print("2")
                # user.birthday =data[3]
                # print("3")
                # user.height = float(data[9])
                # print("4")
                # user.weight = float(data[15])
                # print("5")
                # user.gender = data[9]
                # print("5")
                # user.address = urllib.request.unquote(data[1])
                # print("5")
                # user.phone = data[13]
                # print("5")
                # user.email = urllib.request.unquote(data[5])
                # print("5")
                # user.save()
                # update method 2
                UserSet.objects.filter(uid=request.user.uid).update(birthday=data[3], email=urllib.request.unquote(
                    data[5]), phone=data[13], weight=data[15], address=urllib.request.unquote(data[1]), name=urllib.request.unquote(data[11]), height=data[9], gender=data[7])
                print("6")
                message = {"status": "0"}
                print("個人資訊設定成功")
            else:
                message = {"status": "1", "status": "帳號未登入"}
        except Exception as e:
            print("e", e)
            message = {"status": "1"}
        return JsonResponse(message, safe=False)
    if request.method == 'GET':   # 12.個人資訊
        print("1")
        s = Session.objects.all()[0]
        print("2")
        s.expire_date
        print("3")
        s = Session.objects.get(
            pk=request.META.get('HTTP_COOKIE', '')[-32:]).get_decoded()
        print("4")
        # s = Session.objects.get(pk=request.GET['token']).get_decoded()#postman
        UserProfiledata = UserProfile.objects.get(id=s['_auth_user_id'])
        # print("UserProfiledata",UserProfiledata)
        UserSetdata = UserSet.objects.get(uid=UserProfiledata.uid)
        # print("UserSetdata",UserSetdata)
        Userdeflat = deflat.objects.get(uid=UserProfiledata.uid)
        # print("Userdeflat" ,Userdeflat)
        try:
            message = {
                "status": "0",
                "user": {
                    "id": UserProfiledata.id,
                    "name": UserSetdata.name,
                    "account": UserSetdata.name,
                    "email": UserSetdata.email,
                    "phone": UserSetdata.phone,
                    "fb_id": UserProfiledata.fb_id,
                    "status": UserSetdata.status,
                    "group": UserSetdata.group,
                    "birthday": UserSetdata.birthday,
                    "height": UserSetdata.height,
                    "weight": UserSetdata.weight,
                    "gender": UserSetdata.gender,
                    "address": UserSetdata.address,
                    "unread_records": [int(UserSetdata.unread_records_one), UserSetdata.unread_records_two, int(UserSetdata.unread_records_three)],
                    "verified": int(UserSetdata.verified),
                    "privacy_policy": UserSetdata.privacy_policy,
                    # "must_change_password":1 if UserSetdata.must_change_password else 0,
                    "fcm_id": UserSetdata.fcm_id,
                    "badge": int(UserSetdata.badge),
                    "login_time": int(UserSetdata.login_times),
                    "created_at": datetime.strftime(UserProfiledata.created_at, "%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.strftime(UserProfiledata.updated_at, "%Y-%m-%d %H:%M:%S")},



                "default": {
                    "id": UserProfiledata.id,
                    "user_id": Userdeflat.uid,
                    "sugar_delta_max": int(Userdeflat.sugar_delta_max),
                    "sugar_delta_min": int(Userdeflat.sugar_delta_min),
                    "sugar_morning_max": int(Userdeflat.sugar_morning_max),
                    "sugar_morning_min": int(Userdeflat.sugar_morning_min),
                    "sugar_evening_max": int(Userdeflat.sugar_evening_max),
                    "sugar_evening_min": int(Userdeflat.sugar_evening_min),
                    "sugar_before_max": int(Userdeflat.sugar_before_max),
                    "sugar_before_min": int(Userdeflat.sugar_before_min),
                    "sugar_after_max": int(Userdeflat.sugar_after_max),
                    "sugar_after_min": int(Userdeflat.sugar_after_min),
                    "systolic_max": int(Userdeflat.systolic_max),
                    "systolic_min": int(Userdeflat.systolic_min),
                    "diastolic_max": int(Userdeflat.diastolic_max),
                    "diastolic_min": int(Userdeflat.diastolic_min),
                    "pulse_max": int(Userdeflat.pulse_max),
                    "pulse_min": int(Userdeflat.pulse_min),
                    "weight_max": int(Userdeflat.weight_max),
                    "weight_min": int(Userdeflat.weight_min),
                    "bmi_max": int(Userdeflat.bmi_max),
                    "bmi_min": int(Userdeflat.bmi_min),
                    "body_fat_max": int(Userdeflat.body_fat_max),
                    "body_fat_min": int(Userdeflat.body_fat_min),
                    "created_at": datetime.strftime(UserProfiledata.created_at, "%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.strftime(UserProfiledata.updated_at, "%Y-%m-%d %H:%M:%S")},


                "setting": {
                    "id": UserProfiledata.id,
                    "user_id": Userdeflat.uid,
                    "after_recording": int(UserSetdata.after_recording),
                    "no_recording_for_a_day": int(UserSetdata.no_recording_for_a_day),
                    # "over_max_or_under_min": int(UserSetdata.over_max_or_under_min),
                    "after_meal": int(UserSetdata.after_mael),
                    "unit_of_sugar": int(UserSetdata.unit_of_sugar),
                    "unit_of_weight": int(UserSetdata.unit_of_weight),
                    "unit_of_height": int(UserSetdata.unit_of_height),
                    "created_at": datetime.strftime(UserSetdata.created_at, "%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.strftime(UserSetdata.updated_at, "%Y-%m-%d %H:%M:%S")}
            }
            print("end")
        except Exception as e:
            print("e2", e)
            message = {"status": "1"}
        return JsonResponse(message, safe=False)


@csrf_exempt
def userdefault(request):  # 12.個人預設值
    message = {"status": "1"}
    try:
        print("10")
        data = json.loads(bytes.decode(request.body, 'UTF-8'))
        print("01")
        user = deflat.objects.get(uid=request.user.uid)
        print("user = ", user)
        if request.method == 'PATCH':
            print("111111111", request.GET)
            print("222222222", request.POST)
            print("333333333", request.body)
            print("000000000000000")
            f = PersonalDefaultForm(data)
            if f.is_valid():
                data = f.cleaned_data
                filtered = {i: data[i] for i in data if data[i]}
                if filtered:
                    for i in filtered:
                        setattr(user, i, filtered[i])
                        print(7777777777777)
                    user.save()
            message = {"status": "0"}
    except:
        pass
    return JsonResponse(message)


@csrf_exempt
def userdata(request):
    if request.method == 'PATCH':  # 35.個人設定上傳
        # data = json.loads(bytes.decode(request.body,'UTF-8'))
        data = bytes.decode(request.body, 'UTF-8')
        data = re.split("&|=", data)
        print(data)
        user = UserSet.objects.get(uid=request.user.uid)
        print("user =", user)
        try:
            print("1")
            user.after_recording = data[1]
            print("2")
            user.no_recording_for_a_day = data[3]
            print("3")
            user.over_max_or_under_min = data[5]
            print("3")
            # user.after_mael = data['after_mael']
            # print("2")
            # user.unit_of_sugar = data['unit_of_sugar']
            # print("1")
            # user.unit_of_weight = data['unit_of_weight']
            # user.unit_of_height = data['unit_of_height']
            user.save()
            message = {"status": "0"}
            print("個人設定上傳成功")
        except:
            message = {"status": "1"}
        return JsonResponse(message, safe=False)


@csrf_exempt
def notification(request):  # 親友團通知!
    uid = request.user.id
    if request.method == 'POST':
        nowtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = json.loads(bytes.decode(request.body, "utf-8"))
        # data = request.body
        # data = str(data, encoding="utf-8")
        # data = {
        #     i.split('=')[0]: i.split('=')[1]
        #     for i in data.replace("%40","@").split('&') if i.split('=')[1]
        # }
        message = data['message']
        try:
            friend_list = Friend_data.objects.filter(
                uid=uid, friend_type=1, status=1)  # 抓符合status =1 (接受好友邀請) 且 身分類型為1的人
            for friend in friend_list:
                Notification.objects.create(
                    uid=uid, member_id=1, reply_id=friend.relation_id, message=message, updated_at=nowtime)
                output = {"status": "0"}
        except:
            output = {"status": "1"}
        # else:
        #     output = {"status":"0"}
        return JsonResponse(output, safe=False)


@csrf_exempt
def showHbA1c(request):  # 展示醣化血色素
    if request.method == 'GET':
        # print("GET", request.GET)
        # print("POST", request.POST)
        # print("body", request.body)
        uid = request.user.uid
        # HbA1cdata = HbA1c.objects.get(uid=uid)
        # print(HbA1cdata)
        HbA1cdata = HbA1c.objects.filter(uid=uid)
        print("HbA1cdata", HbA1cdata)
        UserProfiledata = UserProfile.objects.get(uid=uid)
        a1cs_data = []
        try:
            for data in HbA1cdata:
                print("data展示", data.id)
                a1cs_inside_data = {
                    "id": data.id,
                    "user_id": int(UserProfiledata.id),
                    "a1c": data.a1c,
                    "created_at": datetime.strftime(data.created_at, "%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.strftime(data.updated_at, "%Y-%m-%d %H:%M:%S"),
                    "recorded_at": datetime.strftime(data.recorded_at, "%Y-%m-%d %H:%M:%S"),
                }
                a1cs_data.append(a1cs_inside_data)
            print(a1cs_data)
            message = {
                "status": "0",
                "a1cs": a1cs_data}
            # message = {
            #     "status": "0",
            #     "a1cs": {
            #         # "id": int(UserProfiledata.id),
            #         "user_id": int(UserProfiledata.id),
            #         "a1c": float(HbA1cdata.a1c),
            #         "created_at": datetime.strftime(HbA1cdata.created_at, "%Y-%m-%d %H:%M:%S"),
            #         "updated_at": datetime.strftime(HbA1cdata.updated_at, "%Y-%m-%d %H:%M:%S"),
            #         "recorded_at": datetime.strftime(HbA1cdata.recorded_at, "%Y-%m-%d %H:%M:%S")
            #     }}
            # message = message
            print(message)
            print("展示醣化血色素成功")
        except Exception as e:
            print(e)
            message = {'status': '1'}
        return JsonResponse(message)

    if request.method == 'POST':  # 醣化血色素資訊上傳
        uid = request.user.uid
        print("uid1", uid)
        print("PST", request.POST)
        # data = json.loads(bytes.decode(request.body,"utf-8"))
        profiledata = UserProfile.objects.get(uid=uid)
        print("profiledata", profiledata)
        # user = HbA1c.objects.get(uid=uid)
        # print("user", user)
        time = datetime.now()
        nowtime = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            HbA1c.objects.create(
                uid=uid, a1c=str(request.POST["a1c"]), recorded_at=nowtime, updated_at=nowtime, created_at=nowtime)
            # user.a1c = request.POST["a1c"]
            # user.recorded_at = nowtime
            # timeprint= str(nowtime)
            # recorded_at = timeprint
            # updated_at = timeprint
            # created_at = timeprint
            # user.recorded_at = nowtime
            # user.updated_at = nowtime
            # user.created_at = created_at
            # user.save()
            status = {"status": "0"}
            print("醣化血色素資訊上傳成功")
        except Exception as e:
            print(e)
            status = {"status": "1"}
        return JsonResponse(status)
    if request.method == 'DELETE':  # 醣化血色素資訊刪除
        uid = request.user.uid
        print(request.GET)
        HbA1c_id = request.GET.getlist("ids[][]")
        print("HbA1c_id", HbA1c_id)
        # data = json.loads(bytes.decode(request.body, "utf-8"))
        # user = HbA1c.objects.get(uid=uid, id=request.GET['ids[][]'])
        # print(user)
        try:
            # deletedwho = int(request.GET['ids[][]'])  # 利用上一次上傳結果來刪除
            if HbA1c_id != []:
                for HbA1c_id_data in HbA1c_id:
                    print("刪除", HbA1c_id_data)
                    count = HbA1c.objects.filter(
                        uid=uid, id=HbA1c_id_data).delete()
                    # user.a1c = 0
                    # user.save()
                    print(HbA1c_id_data)
                    print("delete count", count)
                    message = {'status': '0'}
                print("醣化血色素資訊刪除成功")
        except:
            message = {'status': '1'}
        return JsonResponse(message)


@ csrf_exempt
def Medical_information(request):
    if request.method == 'GET':  # 就醫資訊展示
        uid = request.user.uid
        medicalinformationdata = medicalinformation.objects.get(uid=uid)
        print(medicalinformationdata)
        UserProfiledata = UserProfile.objects.get(uid=uid)
        try:
            message = {
                "status": "0",
                "medical_info": {
                    "id": int(UserProfiledata.id),
                    "user_id": int(UserProfiledata.id),
                    "diabetes_type": int(medicalinformationdata.diabetes_type),
                    "oad": int(medicalinformationdata.oad),
                    "insulin": int(medicalinformationdata.insulin),
                    "anti_hypertensivers": int(medicalinformationdata.anti_hypertensivers),
                    "created_at": datetime.strftime(UserProfiledata.created_at, "%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.strftime(UserProfiledata.updated_at, "%Y-%m-%d %H:%M:%S")
                }}
            print("就醫資訊展示成功")
            # message = message

        except Exception as e:
            message = {'status': '1'}
        return JsonResponse(message, safe=False)

    if request.method == 'PATCH':  # 就醫資訊新增
        uid = request.user.uid
        # data = json.loads(bytes.decode(request.body,"utf-8"))
        user = medicalinformation.objects.get(uid=uid)
        try:
            # user.user_id = data['account']
            user.diabetes_type = request.POST['diabetes_type']
            user.oad = request.POST['oad']
            user.insulin = request.POST['insulin']
            user.anti_hypertensivers = request.POST['anti_hypertensivers']
            user.save()
            # time = datetime.now()
            # timeprint = datetime.strftime(time,"%Y-%m-%d %H:%M:%s")
            # user.updated_at = updated_at
            status = {"status": "0"}
            print("就醫資訊新增成功")
        except:
            status = {"status": "1"}
        return JsonResponse(status)


@ csrf_exempt
def drug(request):
    if request.method == 'GET':  # 藥物資訊展示
        data = request.body
        print(data)
        print("PST", str(request.GET))
        print("11111", request.POST)
        print("22222", request.body)
        print("33333", request.GET['type'])
        uid = request.user.uid
        # data = json.loads(bytes.decode(request.body,"utf-8"))
        druginformationdata = druginformation.objects.filter(
            uid=uid)
        print("druginformationdata", druginformationdata)
        first = druginformation.objects.filter(
            uid=uid).last()
        print("fisrt", first)
        print("fist_type", first.drugtype)
        UserProfiledata = UserProfile.objects.get(uid=uid)
        UserSetdata = UserSet.objects.get(uid=uid)
        message_outside = []
        try:
            if first.drugtype == "0":
                print("0")
                for druginfo in druginformationdata:
                    print("druginfo.drugtype", druginfo.drugtype)
                    print(type(druginfo.drugtype))
                    if druginfo.drugtype == "0":
                        message_box = {
                            "id": druginfo.id,
                            "user_id": UserProfiledata.id,
                            "type": 0,
                            "name": druginfo.drugname,
                            "recorded_at": druginfo.recorded_at
                        }
                        message_outside.append(message_box)
                        print("藥物資訊展示0成功")
            if first.drugtype == "1":
                print("1")
                for druginfo in druginformationdata:
                    print("1")
                    if druginfo.drugtype == "1":
                        print("0")
                        message_box = {
                            "id": druginfo.id,
                            "user_id": UserProfiledata.id,
                            "type": 1,
                            "name": druginfo.drugname,
                            "recorded_at": druginfo.recorded_at
                        }
                        message_outside.append(message_box)
                        print("藥物資訊展示1成功")
            if len(druginformationdata) != 0:
                print("message_outside", message_outside)
                message = {"status": "0", "drug_useds": message_outside}
            # print(message)
            # first = druginformation.objects.filter(
            #     uid=uid).last()
            # print("fisrt", first)
            # print("fist_type", first.drugtype)
        except Exception as e:
            print(e)
            message = {'status': '1'}
        return JsonResponse(message, safe=False)

    if request.method == 'POST':  # 藥物資訊上傳
        uid = request.user.uid
        print("pst1", request.POST)
        try:
            # data = json.loads(bytes.decode(request.body,"utf-8"))
            nowtime = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
            user = druginformation.objects.create(
                uid=uid, drugname=request.POST["name"], drugtype=request.POST["type"], recorded_at=request.POST["recorded_at"])
            status = {"status": "0"}
            print(user)
        except:
            status = {"status": "1"}
        return JsonResponse(status)

    if request.method == 'DELETE':  # 藥物資訊刪除
        try:
            uid = request.user.uid
            print(request.GET)
            # data = json.loads(bytes.decode(request.body, "utf-8"))
            deletedwho = request.GET.getlist('ids[][]')  # 輸入藥名
            for delete in deletedwho:
                user = druginformation.objects.filter(
                    uid=uid, id=delete).delete()  # 抓取使用者藥物資訊並刪除
                print("藥物刪除成功", user)
            message = {'status': '0'}
            # print("藥物刪除成功", user)
        except Exception as e:
            print(e)
            message = {'status': '1'}
        return JsonResponse(message)


@ csrf_exempt
def share(request):  # 分享!
    if request.method == 'POST':
        uid = request.user.uid
        share_id = request.POST['id']
        data_type = request.POST['type']
        relation_type = request.POST['relation_type']
        try:
            Share.objects.create(
                uid=uid, fid=share_id, data_type=data_type, relation_type=relation_type)
        except:
            output = {"status": "1"}
        else:
            output = {"status": "0"}
        return JsonResponse(output, safe=False)


@ csrf_exempt
def badge(request):
    # 39.更新badge
    status = {"status": "1"}
    try:
        s = Session.objects.get(
            pk=request.headers.get('Authorization', '')[7:]).get_decoded()
        user = UserSet.objects.get(id=s['_auth_user_id'])
        if request.method == 'PUT':
            print("123:", request.POST)
            print("456:", request.GET)
            print("789:", request.PUT)
            data = request.body.decode("utf-8")
            data = {
                i.split('=')[0]: i.split('=')[1]
                for i in data.replace('%40', '@').split('&') if i.split('=')[1]
            }
            if 'badge' in data:
                user.badge = data['badge']
                user.save()
                status = {"status": "0"}
    except:
        pass
    return JsonResponse(status)


@ csrf_exempt
def newnews(request):  # 最新消息
    if request.method == 'GET':
        # s = Session.objects.get(
        #     pk=request.META.get('HTTP_COOKIE','')[-32:]).get_decoded()
        # user = UserProfile.objects.get(id=s['_auth_user_id'])
        user_uid = request.user.uid
        # user = UserProfile.objects.get(uid=user_uid)
        # print("user_id",user.id)
        UserSet_data = UserSet.objects.get(uid=user_uid)
        # print("user_data_id",UserSet_data.id)
        Notificationdata = Notification.objects.get(uid=user_uid)
        print("Notificationdata", Notificationdata)
        try:
            message = {
                'status': '0',
                'news': {
                    'id': UserSet_data.id,
                    'member_id': Notificationdata.member_id,
                    'group': UserSet_data.group,
                    'message': Notificationdata.message,
                    'pushed_at': datetime.strftime(UserSet_data.pushed_at, "%Y-%m-%d %H:%M:%S"),
                    'created_at': datetime.strftime(UserSet_data.created_at, "%Y-%m-%d %H:%M:%S"),
                    'updated_at': datetime.strftime(UserSet_data.updated_at, "%Y-%m-%d %H:%M:%S")
                    # "id": 2,
                    # "member_id": 1,
                    # "group": 1,
                    # "message": "456",
                    # "pushed_at": "2017-11-16 16:33:06",
                    # "created_at": null,
                    # "updated_at": null
                }
            }
        except:
            message = {'status': '1'}
        return JsonResponse(message)


@ csrf_exempt
def share_check(request, relation_type):  # 查看分享（含自己分享出去的）!
    uid = request.user.id
    print(uid)
    if request.method == 'GET':
        if Share.objects.filter(relation_type=relation_type):
            share_checks = Share.objects.filter(relation_type=relation_type)
            datas = []
            for share_check in share_checks:
                if share_check.uid != uid:
                    Friend_data.objects.get(
                        uid=uid, relation_id=share_check.uid, status=1, friend_type=relation_type)
                    user_pro = UserProfile.objects.get(id=share_check.uid)
                    user = UserSet.objects.get(uid=user_pro.uid)
                else:
                    user_pro = UserProfile.objects.get(id=uid)
                    user = UserSet.objects.get(uid=user_pro.uid)
                if share_check.data_type == '0':
                    share_data = Blood_pressure.objects.get(
                        uid=share_check.uid, id=share_check.fid)
                    created_at = datetime.strftime(
                        share_data.created_at, '%Y-%m-%d %H:%M:%S')
                    recorded_at = datetime.strftime(
                        share_data.recorded_at, '%Y-%m-%d %H:%M:%S')
                    created_at_userfile = datetime.strftime(
                        user.created_at, '%Y-%m-%d %H:%M:%S')
                    updated_at_userfile = datetime.strftime(
                        user.updated_at, '%Y-%m-%d %H:%M:%S')
                    r = {
                        "id": share_data.id,
                        "user_id": share_data.uid,
                        "systolic": share_data.systolic,
                        "diastolic": share_data.diastolic,
                        "pulse": share_data.pulse,
                        "recorded_at": recorded_at,
                        "created_at": created_at,
                        "type": 0,
                        "user": {
                            "id": user_pro.uid,
                            "name": user.name,
                            "account": user.email,
                            "email": user.email,
                            "phone": user.phone,
                            "fb_id": user_pro.fb_id,
                            "status": user.status,
                            "group": user.group,
                            "birthday": user.birthday,
                            "height": user.height,
                            "gender": user.gender,
                            "verified": user.verified,
                            "privacy_policy": user.privacy_policy,
                            "must_change_password": user.must_change_password,
                            "badge": user.badge,
                            "created_at": created_at_userfile,
                            "updated_at": updated_at_userfile
                        }
                    }
                if share_check.data_type == '1':
                    share_data = Weight.objects.get(
                        uid=share_check.uid, id=share_check.fid)
                    created_at = datetime.strftime(
                        share_data.created_at, '%Y-%m-%d %H:%M:%S')
                    recorded_at = datetime.strftime(
                        share_data.recorded_at, '%Y-%m-%d %H:%M:%S')
                    created_at_userfile = datetime.strftime(
                        user.created_at, '%Y-%m-%d %H:%M:%S')
                    updated_at_userfile = datetime.strftime(
                        user.updated_at, '%Y-%m-%d %H:%M:%S')
                    r = {
                        "id": share_data.id,
                        "user_id": share_data.uid,
                        "weight": float(share_data.weight),
                        "body_fat": float(share_data.body_fat),
                        "bmi": float(share_data.bmi),
                        "recorded_at": recorded_at,
                        "created_at": created_at,
                        "type": 1,
                        "user": {
                            "id": user_pro.uid,
                            "name": user.name,
                            "account": user.email,
                            "email": user.email,
                            "phone": user.phone,
                            "fb_id": user_pro.fb_id,
                            "status": user.status,
                            "group": user.group,
                            "birthday": user.birthday,
                            "height": user.height,
                            "gender": user.gender,
                            "verified": user.verified,
                            "privacy_policy": user.privacy_policy,
                            "must_change_password": user.must_change_password,
                            "badge": user.badge,
                            "created_at": created_at_userfile,
                            "updated_at": updated_at_userfile
                        }
                    }
                if share_check.data_type == '2':
                    share_data = Blood_sugar.objects.get(
                        uid=share_check.uid, id=share_check.fid)
                    created_at = datetime.strftime(
                        share_data.created_at, '%Y-%m-%d %H:%M:%S')
                    recorded_at = datetime.strftime(
                        share_data.recorded_at, '%Y-%m-%d %H:%M:%S')
                    created_at_userfile = datetime.strftime(
                        user.created_at, '%Y-%m-%d %H:%M:%S')
                    updated_at_userfile = datetime.strftime(
                        user.updated_at, '%Y-%m-%d %H:%M:%S')
                    r = {
                        "id": share_data.id,
                        "user_id": share_data.uid,
                        "sugar": float(share_data.sugar),
                        "timeperiod": int(share_data.timeperiod),
                        "recorded_at": recorded_at,
                        "created_at": created_at,
                        "type": 2,
                        "user": {
                            "id": user_pro.id,
                            "name": user.name,
                            "account": user.email,
                            "email": user.email,
                            "phone": user.phone,
                            "fb_id": user_pro.fb_id,
                            "status": user.status,
                            "group": user.group,
                            "birthday": user.birthday,
                            "height": user.height,
                            "gender": user.gender,
                            "verified": user.verified,
                            "privacy_policy": user.privacy_policy,
                            "must_change_password": user.must_change_password,
                            "badge": user.badge,
                            "created_at": created_at_userfile,
                            "updated_at": updated_at_userfile
                        }
                    }
                if share_check.data_type == '3':
                    share_data = Diary_diet.objects.get(
                        uid=share_check.uid, id=share_check.fid)
                    created_at = datetime.strftime(
                        share_data.created_at, '%Y-%m-%d %H:%M:%S')
                    recorded_at = datetime.strftime(
                        share_data.recorded_at, '%Y-%m-%d %H:%M:%S')
                    created_at_userfile = datetime.strftime(
                        user.created_at, '%Y-%m-%d %H:%M:%S')
                    updated_at_userfile = datetime.strftime(
                        user.updated_at, '%Y-%m-%d %H:%M:%S')
                    image = str(share_data.image)
                    r = {
                        "id": share_data.id,
                        "user_id": share_data.uid,
                        "description": share_data.description,
                        "meal": int(share_data.meal),
                        "tag": share_data.tag,
                        "image": str(image),
                        "lat": share_data.lat,
                        "lng": share_data.lng,
                        "recorded_at": recorded_at,
                        "created_at": created_at,
                        "type": 3,
                        "user": {
                            "id": user_pro.uid,
                            "name": user.name,
                            "account": user.email,
                            "email": user.email,
                            "phone": user.phone,
                            "fb_id": user_pro.fb_id,
                            "status": user.status,
                            "group": user.group,
                            "birthday": user.birthday,
                            "height": user.height,
                            "gender": user.gender,
                            "verified": user.verified,
                            "privacy_policy": user.privacy_policy,
                            "must_change_password": user.must_change_password,
                            "badge": user.badge,
                            "created_at": created_at_userfile,
                            "updated_at": updated_at_userfile
                        }
                    }
                datas.append(r)
            output = {"status": "0", "records": datas}
        else:
            output = {"status": "1"}
        return JsonResponse(output)
