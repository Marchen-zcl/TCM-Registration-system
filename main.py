import time
import requests
from urllib.parse import parse_qs
import winsound
import random
import json

requests.packages.urllib3.disable_warnings()  # 禁用安全请求警告
mode = input("请输入模式：1.线上 2.线下 3.线上+线下\n")  # 模式选择
cookies = {"PHPSESSID": "" or input("请输入cookie:")}  # cookie
deptHisId = "" or input("请输入科室id:")  # 科室id
docHisId = "" or input("请输入医生id:")  # 医生id
base_url = "https://his.mobimedical.cn"  # 基础url
flag = 0  # 是否锁号成功
times = 1  # 查询次数
re_times = 1  # 重试次数
homeUrl = "/index.php?g=Wap&m=CloudIndex&a=index&wx=MbTXcN1k"
CardUrl = "/index.php?&g=Weixin&m=CloudRegisterThree&a=cardList"
periodUrl = "/index.php?&g=Weixin&m=CloudRegisterThree&a=getSchedulePeriod&scheduleId="  # 时间段URL
OrderUrl = "/index.php?&g=Wap&m=CloudPlusRegister&a=ajaxPlusList"  # 订单URL
CreateUrl = "/index.php?g=Weixin&m=CloudRegisterThree&a=createOrder"  # 创建订单URL
PreScheduleUrl = f"/index.php?g=Weixin&m=CloudRegisterThree&a=four&deptHisId={deptHisId}||ZK&docHisId={docHisId}&regType=0&districtCode=2"  # 预加载线下URL
PreOnlineScheduleUrl = f"/index.php?g=Weixin&m=CloudRegisterThree&a=four&deptHisId={deptHisId}&docHisId={docHisId}&regType=0&districtCode=1"  # 预加载线上URL
BillsUrl = "/index.php?g=Weixin&m=CloudUserCenter&a=ajaxGetBills"  # 账单URL
ScheduleUrl = PreScheduleUrl.replace("a=four", "a=getDocScheduleList")  # 线下URL
OnlineScheduleUrl = PreOnlineScheduleUrl.replace(
    "a=four", "a=getDocScheduleList"
)  # 线上URL
CardData = ""
data = ""
params = parse_qs(ScheduleUrl.split("?")[1])  # 获取参数
docHisId = params["docHisId"][0]  # 医生id
fail = False


def getTime():  # 获取当前时间
    current_time = time.time()
    local_time = time.localtime(current_time)
    time_str = time.strftime("%H:%M:%S", local_time)
    return time_str


def play(frequency, duration, times):
    for i in range(times):
        winsound.Beep(frequency, duration)
        time.sleep(0.1)


def checkTime():
    time_str = getTime()
    hour = int(time_str[0:2])
    min = int(time_str[3:5])
    if hour >= 23 or hour <= 5 or (hour == 6 and min < 28):
        return 0
    elif hour == 6 and (30 >= min and min >= 28):
        return 2
    else:
        return 1


def countDown(min):
    countdown_time = min * 60
    while countdown_time > 0:
        minutes = countdown_time // 60
        seconds = countdown_time % 60

        print(f"\r支付剩余时间: {minutes:02d}:{seconds:02d}", flush=True, end="")
        countdown_time -= 1
        time.sleep(1)


def getUrl(url):
    headers = {
        "Connection": "keep-alive",
        "sec-ch-ua-mobile": "?0",
        "Cache-Control": "no-cache",
        "sec-ch-ua-platform": "Windows",
        "Upgrade-Insecure-Requests": "1",
        "sec-ch-ua": '"Chromium";v = "118", "Google Chrome";v = "118", "Not=A?Brand";v = "99"',
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept": "application/json, text/plain, */*",
        "host": "his.mobimedical.cn",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    }
    response = requests.Session().get(
        base_url + url, headers=headers, cookies=cookies, verify=False
    )
    # 可以根据需要处理响应结果，比如获取页面内容、状态码等
    if response.status_code == 200:
        return response
    else:
        return None


def postUrl(url, body, referer=""):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "his.mobimedical.cn",
        "Origin": "https://his.mobimedical.cn",
        "Pragma": "no-cache",
        "Referer": referer,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }
    response = requests.Session().post(
        base_url + url, headers=headers, cookies=cookies, data=body, verify=False
    )
    # 可以根据需要处理响应结果，比如获取页面内容、状态码等
    if response.status_code == 200:
        return response
    else:
        return None


def getOrder(userId):
    return getUrl(OrderUrl + f"&id={userId}").json()["data"]


def getCard():
    return getUrl(CardUrl).json()["data"][0]


def pushMsg(name, dept):  # 微信PushPlus推送消息，可选，自行注册
    headers = {"Content-Type": "application/json"}
    body = {
        "token": "",  # 微信PushPlus推送token
        "title": f"{name}挂号{dept}成功,待缴费",
        "content": f"<style>button{{width:200px;height:50px;background-color:#7cd1ff;border-radius:5px;border:none;outline:none;cursor:pointer;font-weight:600;}}buttona{{display:block;text-decoration:none;font-size:16px;text-align:center;line-height:50px;}}</style><h3>{name}挂号{dept}成功,待缴费</h3><button><a href='https://his.mobimedical.cn/index.php?g=Wap&m=CloudPlusRegister&a=addRegister&wx=MbTXcN1k'>点击缴费</a></button><h3 style='color:red'>若无法支付，则手动从公众号—就医服务—门诊服务中的“自助取号”进入支付</h3>",
        "topic": "957549315",
        "template": "html",
        "channel": "wechat",
    }
    response = requests.Session().post(
        "http://www.pushplus.plus/send",
        headers=headers,
        data=json.dumps(body).encode(encoding="utf-8"),
        verify=False,
    )
    # 可以根据需要处理响应结果，比如获取页面内容、状态码等
    if response.json()["code"] == 200:
        print("推送代缴费成功！")
    else:
        print("推送代缴费失败!")


def judge():
    global data, CardData, fail, mode
    if fail != True:
        if mode == "1":
            OlineData = getUrl(OnlineScheduleUrl).json()["data"]
            for item in OlineData:
                item["Online"] = 1
            data = OlineData
            if len(data) == 0:
                print("无线上门诊，切换线下查询！")
                UnderData = getUrl(ScheduleUrl).json()["data"]
                data = UnderData
                mode = "2"
        elif mode == "2":
            UnderData = getUrl(ScheduleUrl).json()["data"]
            data = UnderData
            if len(data) == 0:
                print("无线下门诊，切换线上查询！")
                OlineData = getUrl(OnlineScheduleUrl).json()["data"]
                for item in OlineData:
                    item["Online"] = 1
                data = OlineData
                mode = "1"
        else:
            OlineData = getUrl(OnlineScheduleUrl).json()["data"]
            UnderData = getUrl(ScheduleUrl).json()["data"]
            for item in OlineData:
                item["Online"] = 1
            data = OlineData + UnderData
            if len(data) == 0:
                print("线上线下均无门诊，退出！")
                exit()
            elif len(OlineData) == 0:
                print("无线上门诊，只查询线下！")
                mode = "2"
            elif len(UnderData) == 0:
                print("无线下门诊，只查询线上！")
                mode = "1"

    else:
        print("cookie失效，重新获取cookie！")
        exit()


# 一个用于选择时间段数组中间时间段的函数
def getMiddleTime(timeList):
    if len(timeList) % 2 == 0:
        return (len(timeList) // 2) - 1
    else:
        return len(timeList) // 2


def getBills(OrderCode):
    timestamp = time.time()
    # 将时间戳转换为结构化时间
    struct_time = time.localtime(timestamp)
    # 格式化时间，只保留年份和月份
    date_string = time.strftime("%Y-%m", struct_time)
    bill = postUrl(BillsUrl, f"type=MbTXcN1k&date={date_string}").json()
    if bill["data"][0]["his_order_number"] == OrderCode:
        return True
    else:
        return False


def getdata():
    global times, flag, data, CardData
    judge()
    # 循环遍历每个字典
    print(f"—————————查询次数：{times}——————————")
    print(f"——————查询时间：{getTime()}——————")
    for item in data:
        availableAppNum = int(item["availableAppNum"])
        if availableAppNum > 0:
            if item.get("Online", False) == 1:
                getUrl(PreOnlineScheduleUrl)
            else:
                getUrl(PreScheduleUrl)
            period = getUrl(f'{periodUrl + item["id"]}').json()
            if period["msg"] == "ok":
                starttime = period["data"]["periodList"][
                    getMiddleTime(period["data"]["periodList"])
                ]["beginTime"]
                endtime = period["data"]["periodList"][
                    getMiddleTime(period["data"]["periodList"])
                ]["endTime"]
            else:
                starttime = ""
                endtime = ""
            postdata = f"userId={CardData['id']}&deptHisId={item['LocRowIdNew']}&docHisId={docHisId}&scheduleCode={item['RBASId']}&periodScheduleCode=&scheduleDate={item['date']}&schedulePeriod={item['period']}&startTime={starttime}&endTime={endtime}&queueNo=&periodCode=&schedulId={'null' if item.get('Online', False) == 1 else item['RBASId']}&showDeptName={item['deptName']}&periodStr={item['periodStr']}&ysdThree=1&payMethod="

            post = postUrl(
                CreateUrl,
                postdata.encode("utf-8"),
                base_url
                + item["url"]
                + f"&startTime={starttime}&endTime={endtime}&schedulId={'null' if item.get('Online', False) == 1 else item['RBASId']}&queueNo=",
            ).json()
            if post["code"] == 200:
                print(
                    f"{'线上' if item.get('Online', False) == 1 else '线下'}",
                    item["date"],
                    item["week"],
                    item["periodStr"],
                    f"{starttime}-{endtime}" if starttime != "" else "",
                    "\n锁号成功！,余号：",
                    availableAppNum - 1,
                )
                flag = 1
                print("查询订单中...")
                time.sleep(0.5)
                order = getOrder(CardData["id"])
                orderNum = len(order)
                if orderNum == 0:
                    print("订单生成失败,尝试重试！")
                    getdata()
                else:
                    pushMsg(CardData["userName"], item["deptName"])
                    print("订单生成成功，待支付订单：", orderNum, "个")
                    getUrl(homeUrl)  # 防止支付单失败
                    play(3000, 200, 5)  # 提示音
                    countDown(5)
                    if getBills(order[0]["OrderCode"]):
                        print("\r查询到支付成功！")
                        exit()
                    else:
                        print("\r支付超时！,尝试重新抢号！")
                        getdata()
            else:
                print(post["msg"])

        else:
            print(
                f"{'线上' if item.get('Online', False) == 1 else '线下'}",
                item["date"],
                item["week"],
                item["periodStr"],
                "余号：",
                availableAppNum,
            )
    times += 1


def main():
    global times, flag, cookies, fail, CardData, re_times
    # 获取Card信息从中截取用户信息
    if getUrl(CardUrl).text.find("非法请求") != -1:
        fail = True
    else:
        CardData = getCard()
        getUrl(homeUrl)  # 预加载防止获取失败
    while 1:
        if checkTime() == 2:
            if flag == 0:
                getdata()
                re_times = 1
                time.sleep(random.random())
            else:
                break
        elif checkTime() == 1:
            if flag == 0:
                if (times % 20) == 20:
                    print(f"——————暂停查询30s——————")
                    time.sleep(30)
                getdata()
                re_times = 1
                time.sleep(random.randint(5, 10))
            else:
                break
        else:
            print("夜间停挂时间！")
            getCard()
            re_times = 1
            time.sleep(random.randint(30, 60))


try:
    main()
except ConnectionResetError:
    if re_times <= 5:
        print(f"远程主机连接超时，尝试重连......{re_times}次")
        re_times += 1
        main()
    else:
        print("远程主机连接超时，尝试重连失败！")
        exit()
