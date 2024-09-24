# %%
# 取得591租屋資訊

import requests

#要抓取頁面的Url
url = "https://rent.591.com.tw/?kind=0&region=8&section=98,102,101,99,100&rentprice=0,15000&pattern=2&order=posttime&orderType=desc"

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
#### 產生結果
#### <Response [200]>
#### Response Status Code 200，代表成功

# %%
from bs4 import BeautifulSoup

soup = BeautifulSoup(response.text, "html.parser")

# 輸出排版後的HTML
print(soup.prettify())

# %%
#正則
import re

# 取得 <ul class="listInfo clearfix"></ul> 內所有元素
listInfoUl = soup.find_all("ul", class_="listInfo clearfix")
num = 0
for ul in listInfoUl:
    # 照片
    img = ul.find("img").get("data-original")

    # 標題
    title = ul.find("a").getText()

    # 詳細資訊的 URL
    detailUrl = ul.find("a").get("href") 

    # 價格
    price = ul.find("div", class_="price").getText().strip()

    # 簡易說明
    wordDetail = ''   
    for de in ul.find_all("p", class_="lightBox"):
        wordDetail = wordDetail + " | " + de.getText().replace(" ", "").replace("\n", "")

    # 更新時間點
    for up in ul.find_all("em"):
        pattern = re.compile('更新')
        if len(pattern.findall(up.getText())) > 0:
            uptime = up.getText()           
    
    #印出擷取結果
    print(
            'title: ' + title + ", " + 
            'img: ' + img + "," + 
            'detailUrl:' + detailUrl + ", " + 
            'price: ' + price + ", " + 
            'detail:' + wordDetail + ", " + 
            'update' + uptime
        )
    print("--------------")

# %%
#表情符號
import emoji

#取得3小時內更新的內容
pattern = re.compile('小時內更新')
if len(pattern.findall(uptime)) > 0:
    pattern = re.compile('(.*)(?=小時)')
    hours = re.search(pattern, uptime).group(1)    
    if int(hours) <= 3:
        #LINE訊息
        msg = emoji.emojize('\n小幫手來啦~ :relaxed: \n租屋網更新資訊啦! :boom: \n :mega:  ', use_aliases=True) + title + emoji.emojize('\n :dollar:  ', use_aliases=True) + price + emoji.emojize('\n :memo:  ', use_aliases=True) + wordDetail + emoji.emojize('\n :alarm_clock:  ', use_aliases=True) + uptime + emoji.emojize('\n\n :tada:  看更詳細點↓網址 \n https:', use_aliases=True) + detailUrl
        
        #印出要傳送的LINE訊息
        print(msg)
        print('-------------')

# %%
#lineNotify設定
def lineNotifyMessage(token, msg, imgUrl):

    # hearders 這兩項必帶
    # token 為 LINE Notinfy 申請的權杖
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type":  "application/x-www-form-urlencoded"
    }

    # message : 要顯示的文字
    # imageThumbnail、imageFullsize : 要顯示的圖片
    # stickerPackageId、stickerId : 貼圖
    message = {'message': msg, 'imageThumbnail':imgUrl,'imageFullsize':imgUrl,'stickerPackageId':1,'stickerId':13}
    
    #透過 POST 傳送
    req = requests.post("https://notify-api.line.me/api/notify", headers = headers, data = message)
    
    return req.status_code


# 傳送LINE訊息
lineNotifyMessage("申請的權杖1", msg, img)  