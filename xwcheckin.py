import requests
import os
import platform
import time
from datetime import datetime

def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')  # Windows
    else:
        os.system('clear')  # Linux/Mac

def login(username, password):
    url = "https://api.nobeliumbiz.com/user/login"
    headers = {
        "Host": "api.nobeliumbiz.com",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Hospital": "xuanwu",
        "Authorization": "Bearer",
        "Charset": "utf-8",
        "Referer": "https://servicewechat.com/wxe0d6a3f51d535e25/20/page-frame.html",
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 12; SM-F926U Build/V417IR; wv) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
            "Chrome/101.0.4951.61 Safari/537.36 MMWEBID/2183 "
            "MicroMessenger/8.0.61.2880(0x28003D34) "
            "WeChat/arm64 Weixin NetType/WIFI Language/en ABI/arm64 MiniProgramEnv/android"
        ),
        "Accept-Encoding": "gzip, deflate, br"
    }

    data = {
        "num": username,
        "password": password
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data
        )

        if (response.status_code == 200):
            try:
                response_data = response.json()  # 将响应体解析为字典
                code = response_data["code"]
                if (code == 0):
                    access_token = response_data["data"]["access_token"]  # 提取嵌套值
                    year_id = response_data["data"]["user"]["year_id"]
                    print(f"登录成功，信息已存储\ntoken: {access_token}\nyear_id: {year_id}")
                    with open("logininfo.txt", "w", encoding="utf-8") as f:
                        f.write(access_token+"\n"+str(year_id))
                else:
                    message = response_data["message"]
                    print(f"登录失败，错误代码：{code}\n报错信息：{message}")
            except KeyError:
                print("错误：未得到token")
        else:
            print(f"请求失败，状态码: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def get_attendence_info(lng, lat):
    
    if os.path.exists("logininfo.txt"):
        with open("logininfo.txt", "r", encoding="utf-8") as f:
            content = f.readlines()
            url = "https://api.nobeliumbiz.com/student/check_in/list"

            params = {
                "lng": str(lng),
                "lat": str(lat),
                "teaching_year_id": content[1]
            }

            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Hospital": "xuanwu",
                "Authorization": "Bearer " + content[0].rstrip(),
                "Charset": "utf-8",
                "Referer": "https://servicewechat.com/wxe0d6a3f51d535e25/20/page-frame.html",
                "User-Agent": (
                    "Mozilla/5.0 (Linux; Android 12; SM-F926U Build/V417IR; wv) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
                    "Chrome/101.0.4951.61 Safari/537.36 MMWEBID/2183 "
                    "MicroMessenger/8.0.61.2880(0x28003D34) "
                    "WeChat/arm64 Weixin NetType/WIFI Language/en ABI/arm64 MiniProgramEnv/android"
                ),
                "Accept-Encoding": "gzip, deflate, br"
            }
            try:
                response = requests.get(url, headers=headers, params=params)
                if (response.status_code == 200):
                    response_text = response.json()
                    attendance_config_id = response_text["data"]["list"][0]["attendance_config_id"]
                    attendance_config_name = response_text["data"]["list"][0]["attendance_config_name"]
                    check_in_location = response_text["data"]["list"][0]["check_in_location"]
                    print(f"定位成功，当前：\nattendance_config_id: {attendance_config_id}\n"+
                          f"attendance_config_name: {attendance_config_name}\n"+
                          f"check_in_location: {check_in_location}")
                    return attendance_config_id
                else:
                    print(f"请求失败，状态码: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
    else:
        print("请先登录获取token")

def check_in(lng, lat, attendance_id):
    if os.path.exists("logininfo.txt"):
        with open("logininfo.txt", "r", encoding="utf-8") as f:
            content = f.readlines()
            url = "https://api.nobeliumbiz.com/student/check_in"

            headers = {
                "accept": "application/json",
                "x-hospital": "xuanwu",
                "authorization": "Bearer " + content[0].rstrip(),
                "content-type": "application/json",
                "charset": "utf-8",
                "referer": "https://servicewechat.com/wxe0d6a3f51d535e25/20/page-frame.html",
                "user-agent": "Mozilla/5.0 (Linux; Android 12; SM-F926U Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/101.0.4951.61 Safari/537.36 MMWEBID/2183 MicroMessenger/8.0.61.2880(0x28003D53) WeChat/arm64 Weixin NetType/WIFI Language/en ABI/arm64 MiniProgramEnv/android",
                "accept-encoding": "gzip, deflate, br"
            }

            data = {
                "lng": str(lng),
                "lat": str(lat),
                "attendance_config_id": attendance_id,
                "teaching_year_id": content[1]
            }
            try:
                response = requests.post(url, json=data, headers=headers)
                response_text = response.json()
                code = response_text["code"]
                message = response_text["message"]
                if (code == 0):
                    print("打卡成功")
                elif (code == 500):
                    print(f"打卡失败，错误信息：{message}")
                else:
                    print("打卡失败，其他错误")
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
    else:
        print("请先登录获取token")

def run_background(lng, lat):
    if os.path.exists("schedule.txt"):
        with open("schedule.txt", "r", encoding="utf-8") as f:
            target_times = [line.rstrip('\n') for line in f]
            print("检测到schedule.txt，正在运行定时程序。程序每半分钟检测一次，请勿关闭窗口......")
            while True:
                now = datetime.now().strftime("%H:%M")
                for t in target_times:
                    if (now == t):
                        attendance_id = get_attendence_info(lng, lat)
                        check_in(lng, lat, attendance_id)
                        time.sleep(60)
                time.sleep(30)
    else:
        print("未找到schedule.txt，将生成默认时间表文件。请自行修改并重新运行定时程序\n格式为每行一个时间，使用24h制")
        with open("schedule.txt", "w", encoding="utf-8") as f:
            f.write("\n7:35\n11:55\n13:35\n17:35\n18:35\n23:35")

if (__name__ == "__main__"):
    lng = 116.36239963107639
    lat = 39.891154513888885
    attendance_id = 0

    while True:
        operation = input("1.登录\n2.获取签到信息\n3.签到\n4.定时程序\n0.退出\n请输入数字选择操作并回车: ")
        if (operation == "1"):
            user = input("输入用户id：")
            passwd = input("输入用户密码：")
            login(user, passwd)
        elif (operation == "2"):
            use_default_location = input("是否使用默认定位：\n1.是\n2.否\n请输入数字选择操作并回车:")
            if (use_default_location == "1"):
                pass
            elif (use_default_location == "2"):
                lng = input("请输入经度：")
                lat = input("请输入纬度：")
            else:
                print("请输入正确数字")
            attendance_id = get_attendence_info(lng, lat)
        elif (operation == "3"):
            if (attendance_id == 0):
                print("请先获取签到信息")
            else:
                check_in(lng, lat, attendance_id)
        elif (operation == "4"):
            run_background(lng, lat)
        elif (operation == "0"):
            break
        else:
            print("请输入正确数字！")
        
        input("回车以继续...")
        clear_screen()