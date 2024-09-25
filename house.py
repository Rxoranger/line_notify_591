# %%
import requests
from bs4 import BeautifulSoup
import re
import emoji
# %%
# 取得591租屋資訊
#要抓取頁面的Url
url = "https://rent.591.com.tw/list?kind=2&region=3&section=37,38&price=10000_20000&layout=1&sort=posttime_desc"

#自訂 Request Headers
headers = {
    "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding" : "gzip, deflate, br",
    "Accept-Language" : "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection" : "keep-alive",
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
    "Upgrade-Insecure-Requests" : "1",
    "Cache-Control" : "max-age=0",
    "Host" : "rent.591.com.tw",   
    "Cookie" : "urlJumpIp=8; urlJumpIpByTxt=%E5%8F%B0%E4%B8%AD%E5%B8%82; is_new_index=1; is_new_index_redirect=1; T591_TOKEN=0mgp6gnmca0m1aes0a653qpk76; _ga=GA1.3.1853129893.1614755590; tw591__privacy_agree=0; _ga=GA1.4.1853129893.1614755590; _fbp=fb.2.1614755592267.503379817; new_rent_list_kind_test=0; _gid=GA1.3.990458239.1615170698; _gid=GA1.4.990458239.1615170698; webp=1; PHPSESSID=ugspv0rqvnetihun53ane0jlc4; XSRF-TOKEN=eyJpdiI6ImloZzR5Qm9SRk1XNVd4bmJ2VG8zNUE9PSIsInZhbHVlIjoiSExCSnRITEZjSE8rWktjVEptSnlEd1AxNEs1cHRcL1dEYktOR0dvUUNwdU9vNVVPUHlaK3UyXC9pOWpCVElxV0JJdzZGWFF0bytcL3MrSGNGSlpyQk96OGc9PSIsIm1hYyI6IjQ5NDgzZjc1YWExYTkyZDQ2YWRjZWQwZDI5YTIwODZhMTJkYzNlMmZiYzUwNmZmMzY2YjNhZjQ4NGI4OGY2NjMifQ%3D%3D; 591_new_session=eyJpdiI6ImpYUE9QWDJWYVwvaVlJc3dUK0ZiY3h3PT0iLCJ2YWx1ZSI6ImVMYnpSQ2ZhNG9VZHNSdWZNMjZTSG5nUTZOaWZlZ05kQkRXVkNLZDAxQlBqWWJneXVZbXZEWmd6SVRrMU5ZbGtrOU9tVG9RZm1CM2ZKUnNYQVlJaTNRPT0iLCJtYWMiOiIwN2UzODgzYWE0OGM2YTlkMDI1YTVjYjkzNmUyYWJiMzA5M2JmN2M0M2Q4NDQ1ODhlYTZkM2E3NzFkMjVjMWZlIn0%3D"
}

response = requests.get(url=url, headers=headers)

print(response)
# %%
soup = BeautifulSoup(response.text, "html.parser")

# 輸出排版後的HTML
print(soup.prettify())

# %%
# 檢查是否是6小時內更新的內容
def is_within_six_hours(uptime):
    # 檢查是否是以小時更新
    hour_pattern = re.compile(r'(\d+)\s*小時內更新')
    hour_match = hour_pattern.search(uptime)

    if hour_match:  # 如果找到了小時
        hours = int(hour_match.group(1))
        if hours <= 6:
            return True

    # 檢查是否是以分鐘更新
    minute_pattern = re.compile(r'(\d+)\s*分鐘內更新')
    minute_match = minute_pattern.search(uptime)

    if minute_match:  # 如果找到了分鐘
        minutes = int(minute_match.group(1))
        if minutes <= 360:  # 360分鐘等於6小時
            return True

    return False

# %%
# 儲存所有房源的列表
property_list = []

# 取得 <div class="item"></div> 內所有元素
listInfoUl = soup.find_all("div", class_="item")
for ul in listInfoUl:
    # 照片
    img = ul.find("img").get("data-src")

    # 標題
    title = ul.find("a").getText()

    # 詳細資訊的 URL
    detailUrl = ul.find("a").get("href") 

    # 抓取價格
    price_elements = ul.find("div", class_="item-info-price").find_all("i")
    price_list = []

    # 根據每個 <i> 標籤的 order 屬性來排序並拼接價格
    for price_element in price_elements:
        style_value = price_element.get("style")
        # 使用正則表達式來精確提取 order 的數值
        order_match = re.search(r'order:(\d+)', style_value)
        if order_match:  # 如果找到了 order 屬性
            order = int(order_match.group(1))  # 提取數字部分
            price_list.append((order, price_element.getText()))  # 把 order 和數字/符號存入列表

    # 按 order 進行排序並拼接成一個價格字串
    price_list.sort(key=lambda x: x[0])
    price = ''.join([item[1] for item in price_list])

    # 刪除數字中多餘的逗號，並確保是數字格式
    price = price.replace(",", "").strip()

    # 簡易說明
    wordDetail = ''

    # 抓取房型描述，例如「獨立套房」
    room_type = ul.find("div", class_="item-info-txt").find("span").getText()

    # 將房型描述加入簡易說明
    wordDetail = wordDetail + room_type

    # 找到所有 <span class="line">，這些包含了面積、樓層等資訊
    for line in ul.find_all("span", class_="line"):
        span_elements = line.find_all("i")  # 在每個 <span> 中抓取 <i> 元素
        details_list = []

        # 迴圈遍歷每個 <i> 元素，提取文本並根據 order 屬性排序
        for element in span_elements:
            style_value = element.get("style")
            order_match = re.search(r'order:(\d+)', style_value)
            if order_match:  # 如果找到了 order 屬性
                order = int(order_match.group(1))  # 提取數字部分
                details_list.append((order, element.getText()))  # 把 order 和數字/符號存入列表

        # 將根據 order 排列好的結果拼接成一段說明
        details_list.sort(key=lambda x: x[0])
        detail_str = ''.join([item[1] for item in details_list])

        # 將拼接好的說明添加到 wordDetail，並加上分隔符號
        wordDetail = wordDetail + " | " + detail_str

    # 去除多餘的空白與符號
    wordDetail = wordDetail.strip(" | ")

    # 更新時間點
    uptime = None
    for up in ul.find_all("span"):
        pattern = re.compile('更新')
        if len(pattern.findall(up.getText())) > 0:
            uptime = up.getText()

    # 將每筆物件的資料存入字典
    property_info = {
        'title': title,
        'img': img,
        'detailUrl': detailUrl,
        'price': price,
        'wordDetail': wordDetail,
        'uptime': uptime
    }

    # 將這筆資料存入 property_list
    property_list.append(property_info)

# # 篩選出更新時間在 3 小時內的物件，並輸出 LINE 訊息
# for property_info in property_list:
#     uptime = property_info['uptime']

#     # 檢查是否是3小時內更新的內容
#     pattern = re.compile('小時內更新')
#     if len(pattern.findall(uptime)) > 0:
#         pattern = re.compile('(.*)(?=小時)')
#         hours_match = re.search(pattern, uptime)

#         # 檢查是否找到了匹配的數字
#         if hours_match:
#             hours = hours_match.group(1)
#             if int(hours) <= 3:
#                 # LINE 訊息
#                 msg = (
#                     emoji.emojize('小幫手來啦~\n')
#                     + '租屋網更新資訊啦！\n'
#                     + '標題：' + property_info['title'] + '\n'
#                     + emoji.emojize('價格：' + property_info['price'] + '元/月\n')
#                     + property_info['wordDetail'] + '\n'
#                     + property_info['uptime'] + '\n'
#                     + emoji.emojize('⬇︎點擊以下看更詳細點網址\n')
#                     + property_info['detailUrl']
#                 )

#                 # 印出要傳送的 LINE 訊息
#                 print(msg)
#                 print('-------------')

# %%
# 篩選出更新時間在 6 小時內的物件，並輸出 LINE 訊息
for property_info in property_list:
    uptime = property_info['uptime']

    # 使用 is_within_three_hours 函數檢查更新時間
    if is_within_six_hours(uptime):
        # LINE 訊息
        msg = (
            emoji.emojize('小幫手來啦~\n')
            + '租屋網更新資訊啦！\n'
            + '標題：' + property_info['title'] + '\n'
            + emoji.emojize('價格：' + property_info['price'] + '元/月\n')
            + property_info['wordDetail'] + '\n'
            + property_info['uptime'] + '\n'
            + emoji.emojize('⬇︎點擊以下看更詳細\n')
            + property_info['detailUrl']
        )

        # 印出要傳送的 LINE 訊息
        print(msg)
        print('-------------')

# %%
# lineNotify設定
def lineNotifyMessage(token, msg, imgUrl):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type":  "application/x-www-form-urlencoded"
    }

    message = {
        'message': msg, 
        'imageThumbnail': imgUrl,  # 縮略圖
        'imageFullsize': imgUrl,   # 全尺寸圖片
        'stickerPackageId': 1,     # 貼圖包 ID
        'stickerId': 13            # 貼圖 ID
    }
    
    # POST 傳送訊息
    req = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=message)
    
    return req.status_code

# 在 sendPropertyUpdates 函數中檢查更新時間
def sendPropertyUpdates(property_list, token):
    for property_info in property_list:
        uptime = property_info['uptime']

        if is_within_six_hours(uptime):  # 使用新函數檢查
            # 構建 LINE 訊息
            msg = (
                emoji.emojize('小幫手來啦~\n')
                + '租屋網更新資訊啦！!!*\n'
                + '標題：' + property_info['title'] + '\n'
                + emoji.emojize('價格：' + property_info['price'] + '元/月\n')
                + property_info['wordDetail'] + '\n'
                + property_info['uptime'] + '\n'
                + emoji.emojize('⬇︎ 點擊以下網誌看更詳細資訊\n')
                + property_info['detailUrl']
            )

            # 發送 LINE 訊息
            status = lineNotifyMessage(token, msg, property_info['img'])
            if status == 200:
                print("訊息已成功發送！")
            else:
                print(f"訊息發送失敗，狀態碼: {status}")

# 呼叫發送函數
token = 'yNwd71SeRNKtJrlFbPkLNz28fgEp7imm0Tge2F5xwHp'  # LINE Notify 的 token
sendPropertyUpdates(property_list, token)