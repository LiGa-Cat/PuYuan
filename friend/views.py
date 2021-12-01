from json import decoder, loads
from django.http import HttpResponse, JsonResponse
from django.contrib import auth
import requests
from requests.sessions import Request
from .models import *
from user.models import *
from body.models import *
from datetime import date, datetime
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.


@csrf_exempt
def friend_code(request):  # 獲取"自己"的控糖團邀請碼!
    print("10100101", request)
    user_id = request.user.id
    if request.method == "GET":
        try:
            # uid = request.POST.get("uid")            #新增輸入被加好友的uid
            user_friend = Friend.objects.get(uid=user_id)  # 抓自己的邀請碼出來
            output = {
                "status": "0",
                "invite_code": user_friend.invite_code
            }
        except:
            output = {"status": "1"}
        return JsonResponse(output)


@csrf_exempt
def friend_list(request):  # 我(uid)獲取的控糖團列表!
    uid = request.user.id
    if request.method == 'GET':
        if Friend_data.objects.filter(uid=uid, status=1):  # 接受我好友邀請的朋友列表
            friends = []
            friends_list = Friend_data.objects.filter(
                uid=uid, status=1)  # 接受我好友邀請的朋友列表
            for friend in friends_list:
                user_pro = UserProfile.objects.get(id=friend.relation_id)
                relation = UserSet.objects.get(uid=user_pro.uid)
                created_at_userfile = datetime.strftime(
                    relation.created_at, '%Y-%m-%d %H:%M:%S')
                updated_at_userfile = datetime.strftime(
                    relation.updated_at, '%Y-%m-%d %H:%M:%S')
                r = {  # 以下為我好友資料
                    "id": user_pro.id,
                    "name": relation.name,
                    "account": relation.email,
                    "email": relation.email,
                    "phone": relation.phone,
                    "fb_id": user_pro.fb_id,
                    "status": relation.status,
                    "group": relation.group,
                    "birthday": str(relation.birthday),
                    "height": relation.height,
                    "gender": relation.gender,
                    "verified": relation.verified,
                    "privacy_policy": relation.privacy_policy,
                    "must_change_password": relation.must_change_password,
                    "badge": int(relation.badge),
                    "created_at": created_at_userfile,
                    "updated_at": updated_at_userfile,
                    "relation_type": friend.friend_type
                }
                friends.append(r)
            output = {"status": "0", "friends": friends}
        else:
            output = {"status": "1"}
    return JsonResponse(output)


@csrf_exempt
def friend_requests(request):  # 獲取控糖團邀請!(別人加我的邀請)
    uid = request.user.id
    print("1")
    print(uid)
    try:
        requests_list = Friend_data.objects.filter(
            relation_id=uid, status=0)  # 我(uid)加好友的交友申請資料
        print("requests_list", requests_list)
        requests = []
        for data in requests_list:
            print(data)
            print(data.uid)
            user_pro = UserProfile.objects.get(id=data.uid)  # 以下為好友的資料
            user = UserSet.objects.get(uid=user_pro.uid)
            print(user)
            print(user.height)
            print(type(user.height))
            created_at_friendata = datetime.strftime(
                data.created_at, '%Y-%m-%d %H:%M:%S')
            updated_at_friendata = datetime.strftime(
                data.updated_at, '%Y-%m-%d %H:%M:%S')
            created_at_userfile = datetime.strftime(
                user.created_at, '%Y-%m-%d %H:%M:%S')
            updated_at_userfile = datetime.strftime(
                user.updated_at, '%Y-%m-%d %H:%M:%S')
            r = {
                "id": int(data.id),
                "user_id": int(data.uid),
                "relation_id": int(data.relation_id),
                "type": int(data.friend_type),
                "status": int(data.status),
                "created_at": created_at_friendata,
                "updated_at": updated_at_friendata,
                "user":
                {
                    "id": int(user.id),
                    "name": user.name,
                    "account": user.email,
                    "email": user.email,
                    "phone": user.phone,
                    "fb_id": user_pro.fb_id,
                    "status": user.status,
                    "group": user.group,
                    "birthday": str(user.birthday),
                    "height": float(user.height),
                    "gender": user.gender,
                    "verified": user.verified,
                    "privacy_policy": user.privacy_policy,
                    "must_change_password": user.must_change_password,
                    "badge": int(user.badge),
                    "created_at": created_at_userfile,
                    "updated_at": updated_at_userfile

                }
            }
            requests.append(r)
        output = {"status": "0", "requests": requests}
        print("獲取控糖團邀請成功")
    except Exception as e:
        print("2", e)
        output = {"status": "1"}
    return JsonResponse(output)


@csrf_exempt
def friend_send(request):  # 19.送出控糖團邀請!(加好友)
    uid = request.user.id
    print(uid)
    if request.method == 'POST':
        # data = json.loads(bytes.decode(request.body,"utf-8"))
        nowtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        friend_type = request.POST['type']
        invite_code = request.POST['invite_code']
        try:
            user_friend = Friend.objects.get(
                invite_code=invite_code)  # 找出被加好友的資料
            friend_uid = user_friend.uid
        except:
            output = {"status": "1"}  # 1: 邀請碼無效
        else:
            try:
                # 關係資料表，若無則接129建立關係資料表
                Friend_data.objects.get(uid=uid, relation_id=friend_uid)
            except:
                try:
                    Friend_data.objects.create(
                        uid=uid, relation_id=friend_uid, status=0, friend_type=friend_type, updated_at=nowtime)
                    # Friend_data.objects.create(
                    #     uid=friend_uid, relation_id=uid, status=0, friend_type=friend_type, updated_at=nowtime)  # 新增
                except:
                    output = {"status": "1"}
                else:
                    output = {"status": "0"}
            else:
                output = {"status": "2"}  # 2: 已經成為好友
    return JsonResponse(output, safe=False)


@csrf_exempt
def friend_accept(request, friend_data_id):  # 接受控糖團邀請!
    # print(request.GET)
    # print(request.POST)
    # print(request.body)
    print(friend_data_id)
    data = Friend_data.objects.get(id=friend_data_id)
    # print("friend_data_id", friend_data_id)
    uid = request.user.id
    # print(uid)
    nowtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(1234)
    if request.method == "GET":
        try:
            check = Friend_data.objects.filter(uid=data.uid, relation_id=uid, status=0).update(
                read=True, status=1, updated_at=nowtime, imread=True)
            # check1 = Friend_data.objects.filter(uid=data.uid, relation_id=uid, status=0).update(
            #     read=True, status=1, updated_at=nowtime, imread=True)  # 新增
            Friend_data.objects.create(
                uid=uid, relation_id=data.uid, status=1, read=True, friend_type="0", updated_at=nowtime, imread=True)
            # check1 = Friend_data.objects.create(
            #     uid=uid, relation_id=data.uid, read=True, status=1, updated_at=nowtime, imread=True)  # 新增
            # Friend_data.objects.create(uid=uid, relation_id=check.uid, status=1, read=True, imread=True, friend_type=check.friend_type, updated_at=nowtime)
            # check.read = True
            # check.status = 1
            # check.updated_at = nowtime
            # check.save()
            print(check)
            print(check1)
            print("11111")
            output = {"status": "0"}
            print("接受控糖團邀請成功")
        except Exception as e:
            print(e)
            output = {"status": "1"}
    return JsonResponse(output, safe=False)


@csrf_exempt
def friend_refuse(request, friend_data_id):  # 拒絕控糖團邀請!
    data = Friend_data.objects.get(id=friend_data_id)
    # print("friend_data_id", friend_data_id)
    uid = request.user.id
    nowtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        check = Friend_data.objects.filter(uid=uid, relation_id=data.uid, status=0).update(
            read=True, status=2, updated_at=nowtime)
        check1 = Friend_data.objects.filter(uid=data.uid, relation_id=uid, status=0).update(
            read=True, status=2, updated_at=nowtime)  # 新增
        # check.read = True
        # check.status = 2
        # check.updated_at = nowtime
        # check.save()
        if check == 1 and check1 == 1:
            output = {"status": "0"}
        else:
            output = {"status": "1"}
    except:
        output = {"status": "1"}
    else:
        output = {"status": "0"}
    return JsonResponse(output, safe=False)


@csrf_exempt
def friend_remove(request, friend_data_id):  # 刪除控糖團邀請!
    data = Friend_data.objects.get(id=friend_data_id)
    uid = request.user.id
    print("666666")
    if request.method == 'DELETE':
        try:
            check = Friend_data.objects.filter(
                uid=uid, relation_id=data.uid, status=0).delete()  # 刪掉uid對relation_id的邀請
            if check == 1:
                output = {"status": "0"}
                print("刪除成功")
            else:
                output = {"status": "1"}
        except:
            output = {"status": "1"}
        return JsonResponse(output)


@csrf_exempt
def friend_results(request):  # 控糖團結果!
    uid = request.user.id
    if request.method == 'GET':
        if Friend_data.objects.filter(uid=uid, read=True, imread=False):
            results = []
            result = Friend_data.objects.filter(
                uid=uid, read=True, imread=False).latest('updated_at')
            user_pro = UserProfile.objects.get(
                id=result.relation_id)  # 以下為好友(relation_id)的資料
            relation = UserSet.objects.get(uid=user_pro.uid)
            created_at_friendata = datetime.strftime(
                result.created_at, '%Y-%m-%d %H:%M:%S')
            updated_at_friendata = datetime.strftime(
                result.updated_at, '%Y-%m-%d %H:%M:%S')
            created_at_userfile = datetime.strftime(
                relation.created_at, '%Y-%m-%d %H:%M:%S')
            updated_at_userfile = datetime.strftime(
                relation.updated_at, '%Y-%m-%d %H:%M:%S')
            r = {
                "id": result.id,
                "user_id": result.uid,
                "relation_id": result.relation_id,
                "type": result.friend_type,
                "status": int(result.status),
                "read": result.read,
                "created_at": created_at_friendata,
                "updated_at": updated_at_friendata,
                "relation":
                {
                    "id": user_pro.id,
                    "name": relation.name,
                    "account": relation.email,
                    "email": relation.email,
                    "phone": relation.phone,
                    "fb_id": user_pro.fb_id,
                    "status": relation.status,
                    "group": relation.group,
                    "birthday": str(relation.birthday),
                    "height": relation.height,
                    "gender": relation.gender,
                    "verified": relation.verified,
                    "privacy_policy": relation.privacy_policy,
                    "must_change_password": relation.must_change_password,
                    "badge": int(relation.badge),
                    "created_at": created_at_userfile,
                    "updated_at": updated_at_userfile
                }
            }
            result.imread = True
            result.save()
            results.append(r)
            output = {"status": "0", "results": results}
        else:
            output = {"status": "1"}
    return JsonResponse(output)


@csrf_exempt
def friend_remove_more(request):  # 刪除更多好友!
    # data = Friend_data.objects.get(id=friend_data_id)
    uid = request.user.id
    print(uid)
    print("1111100000")
    try:
        if request.method == 'DELETE':
            print("11111111", request.GET)
            ids_list = request.GET.getlist("ids[]")
            for ids in ids_list:
                data1 = Friend_data.objects.get(
                    uid=ids, relation_id=uid, status=1).delete()
                data2 = Friend_data.objects.get(
                    uid=uid, relation_id=ids, status=1).delete()
                output = {"status": "0"}
                print("1", data1)
                print("2", data2)
                print("成功刪除更多好友")
        else:
            output = {"status": "1"}
    except Exception as e:
        output = {"status": "1"}
    return JsonResponse(output)
