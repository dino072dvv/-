#使用API 或是 AJAX爬蟲
import requests
import json
import time
import pymysql

# 設定關鍵字
keyword ="新冠肺炎"
# 起始時間
startDate = "2022-09-30"
# 結束時間。根據格式解析表示時間的字符串
endDate = time.strptime(startDate, "%Y-%m-%d")

index=1 #只是用來顯示新聞篇數
page=0  #搜尋頁數,每迴圈+!
end=0 #為了連續跳離兩個迴圈使用

#定義空陣列
news_list=[]


# 主迴圈
while True:
    # 如果end值等於1就跳出迴圈
    if end==1:
        print("==========已將資料儲存至字典==========")
        break
    # 運用格式化字串，將第二個{}值 修改為上面定義的關鍵字
    # 位址為json格式
    ### API位址取得方式(以Google Chrome為例)開啟F12，修改顯示為下方，
    ### 選取XHR頁面，F5重新讀取網頁，滾輪往下滾直到讀取新聞，這時網站會跟API請求讀取資料，
    ### 所以下面會多出資料，這時用Headers查看可以看到API的出現，輸入Request URL 就能進到發送端的API
    ### search:後面本來是URL編碼中的UrlDecode編碼，可以透過解碼轉回中文
    ### 不過這裡是用GET方法，所以可以直接替換成關鍵字，last_page參數沒有作用，主要是靠前面的page讀取資料
    url="https://udn.com/api/more?page={}&id=search:{}&channelId=2&type=searchword&last_page=10000".\
        format(page+1,keyword)
    # 迴圈執行一次頁數就會加1
    page+=1
    # 取得網頁資料
    r=requests.get(url)
    # 將已編碼的 JSON 字符串解碼為 Python 對象
    data=json.loads(r.text)

    for i in range(len(data['lists'])):
        # 列印新聞篇數
        print("\n這是第{}篇新聞".format(index))
        # 迴圈每執行一次就加一
        index+=1
        
        # 列印第lists第i位的title
        print(data['lists'][i]['title'])
        
        # 列印第lists第i位的titleLink
        print(data['lists'][i]['titleLink'])
        
        # 列印第lists第i位的time 與 date，位置從0到9為止
        print(data['lists'][i]['time']['date'][:10])
        
        # 將lists第0位的['time']['date'] 格式解析成表示時間的字符串
        newsDate=time.strptime(data['lists'][i]['time']['date'][:10], "%Y-%m-%d")
        
        # 利用字典存取資料
        news_data = {}
        news_data['title'] = data['lists'][i]['title']
        news_data['titleLink'] = data['lists'][i]['titleLink']
        news_data['newstime'] = data['lists'][i]['time']['date'][:10]
        news_list.append(news_data)
        
        # 當日期小於指定天數跳出迴圈
        if newsDate < endDate:
            print("本篇新聞小於指定天數,搜尋程式")
            end=1
            break

# 連接資料庫，資料庫為MySQL
db=pymysql.connect(host='127.0.0.1',user='test',password='123456789',
                             database='db')
#db.cursor()是函式不可變更
cursor = db.cursor()

print("==========開始進行資料庫存檔==========")
# 檢查資料庫內是否已存在爬過的資料，初步過濾資料
for i in news_list:
    sql="select * from news where title='{}' and date='{}'".format(i['title'],i['newstime'])
    # 執行 SQL 指令
    cursor.execute(sql)
    # 提交至 SQL
    db.commit()
    # fetchall：取出全部資料，查詢回傳的資料需要以 cursor 物件取得
    data=cursor.fetchall()
    
    # 如果找不到資料就進行寫入資料庫
    if len(data)==0:
        sql="insert into news (title,link,date) value ('{}','{}','{}')".\
        format(i['title'],i['titleLink'],i['newstime'])
        # 執行 SQL 指令
        cursor.execute(sql)
        # 提交至 SQL
        db.commit()
        print(i['title'][:10],"insert")
    # 資料已存在就執行以下程式
    else:
        print(i['title'][:10],"重複，不存")
# 關閉連接資料庫
db.close()

print("==========爬取程序結束==========")