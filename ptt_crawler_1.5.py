# 抓取 PTT MobileComm 上的文章（幾天前的文章）

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from crawler_tool import get_onepage, calculate_freq
import datetime as dt

#####################################
## 品牌關鍵字讀檔，a 列到 j 列十個品牌
fh1 = open('./keyword.csv', 'r', encoding = 'big5')
brand_dict = dict()
for line in fh1:
    temp = line.lower().replace('\n', '').replace(' ', '').split('\"')
    brand_dict[temp[0].replace(',', '')] = temp[1].split(',')

a, b, c, d, e, f, g, h, i, j = list(brand_dict.keys())

#####################################
## 步驟一：起始頁面，選擇欲爬文看板
print('============================\n  歡迎使用 PTT 看板爬文程式！\n============================\n')
while True:
    board_name = input('※ 請選擇欲爬文的看板名稱：\n 1. MobileComm 行動通訊板\n 2. PC_Shopping 電腦消費板\n 3. NB-shopping 筆電消費板\n 4. Tech_Job 科技業板\n 5. 其他（請在下一步驟輸入該板首頁網址）\n>> 請輸入數字代碼並按下 enter 鍵：')
    if board_name == '1':
        index = 'https://www.ptt.cc/bbs/MobileComm/index.html'
        break
    elif board_name == '2':
        index = 'https://www.ptt.cc/bbs/PC_Shopping/index.html'
        break
    elif board_name == '3':
        index = 'https://www.ptt.cc/bbs/nb-shopping/index.html'
        break
    elif board_name == '4':
        index = 'https://www.ptt.cc/bbs/Tech_Job/index.html'
        break
    elif board_name == '5':
        index = input('\n>> 請輸入該板首頁網址：')
        break
    else:
        print('輸入錯誤，請重新輸入數字代碼！')

#####################################
## 步驟二：選擇文章取得方式
while True:
    try:
        service = int(input('\n※ 請選擇文章取得方式：\n 1. 輸入天數(取得過去幾天內的文章)\n 2. 輸入頁數(從何頁開始取得)：\n>> 請輸入數字代碼並按下 enter 鍵：'))
        if service != 1 and service != 2:
            print('輸入錯誤，請重新輸入數字代碼！')
        else:
            break
    except ValueError:
        print('輸入錯誤，請重新輸入數字代碼！')

#####################################
## 步驟三：選擇文章取得範圍
while True:
    try:
        if service == 1:
            num = int(input('\n>> 請輸入要取得幾天以內的文章，並按下 enter 鍵 (ex:7)：'))
            break
        else:
            first_page = int(input('\n>> 請輸入想從第幾頁開始取得，並按下 enter 鍵 (ex:6500)：'))
            break
    except ValueError:
        print('您輸入了非數值之字元，請重新輸入數字代碼！')

if service == 1:
    diff = dt.timedelta(days = num - 1)

    end_date = dt.datetime.today().date()
    start_date = end_date - diff

    end_date = end_date.strftime('%m-%d')
    start_date = start_date.strftime('%m-%d')

    print('\n>> 即將取得從 %s 到 %s 內的文章。'%(start_date, end_date))
else:
    print('\n>> 即將取得第 %s 頁到最新頁的文章'%first_page)

#####################################
## 步驟四：開啟虛擬瀏覽器
print('\n>> 請注意，程式執行完畢後會自動關閉 Chrome 瀏覽器，請勿手動關閉以免程式錯誤。\n若出現防火牆訊息，可點選關閉或接受。')
input('---請按下 Enter 鍵以開始爬蟲---')

print('>> 正在開啟瀏覽器...')
driver = webdriver.Chrome('./chromedriver.exe')
print('>> 開啟網頁中...')
driver.get(index)
driver.add_cookie({'name': 'over18', 'value': '1'})
driver.get(index)
print('>> 完成！')

#####################################
## 爬取網頁
all_articles = []
num_per_page = 1

if service == 1:
    while num_per_page != 0:
        print('>> 正在抓取此網頁...', driver.current_url)
        soup = BeautifulSoup(driver.page_source, 'lxml') ## 得到網頁原始碼
        articles = get_onepage(soup, service, num)
        num_per_page = len(articles)
        all_articles += articles
        driver.find_element_by_css_selector('div.btn-group-paging a:nth-child(2)').click()
        print('>> 完成！')
else:
    last_page = int(driver.find_element_by_css_selector('div.btn-group-paging a:nth-child(2)').get_attribute('href').replace('.html', '').split('index')[1])
    num = last_page - first_page + 1
    for k in range(num):
        print('>> 正在抓取此網頁...', driver.current_url)
        soup = BeautifulSoup(driver.page_source, 'lxml') ## 得到網頁原始碼
        articles = get_onepage(soup, service, num)
        all_articles += articles
        driver.find_element_by_css_selector('div.btn-group-paging a:nth-child(2)').click()
        print('>> 完成！')

print('>> 正在關閉瀏覽器...')
driver.close()
print('>> 完成！')

#####################################
## 寫入檔案
board = index.split('/')[-2] ## 取出看板名
if service == 1:
    csv = open('./ptt_%s版_過去%d天內之貼文.csv'%(board, num), 'w', encoding='big5') ## 檔名格式，'a+'代表可覆寫
else:
    csv = open('./ptt_%s版_第%d頁至第%d頁之貼文.csv'%(board, first_page, last_page), 'w', encoding='big5') ## 檔名格式，'a+'代表可覆寫

csv.write('請記得先另存新檔成xlsx檔，謝謝！,\n')
csv.write('推,噓,箭頭,總留言數,品牌分類（僅適用於行動通訊板）,標題,發文日期,Link,\n')
for l in all_articles:
    title = l['title'].lower().replace(' ', '')
    print('>> 正在寫入...', l['title'])
    l['brand'] = ''
    l['brand'] += calculate_freq(title, brand_dict[a], a) + ' '
    l['brand'] += calculate_freq(title, brand_dict[b], b) + ' '
    l['brand'] += calculate_freq(title, brand_dict[c], c) + ' '
    l['brand'] += calculate_freq(title, brand_dict[d], d) + ' '
    l['brand'] += calculate_freq(title, brand_dict[e], e) + ' '
    l['brand'] += calculate_freq(title, brand_dict[f], f) + ' '
    l['brand'] += calculate_freq(title, brand_dict[g], g) + ' '
    l['brand'] += calculate_freq(title, brand_dict[h], h) + ' '
    l['brand'] += calculate_freq(title, brand_dict[i], i) + ' '
    l['brand'] += calculate_freq(title, brand_dict[j], j) + ' '
    l['brand'] = l['brand'].strip()

    l['title'] = l['title'].replace(',', '，') ## 與用來分隔的逗點作區別
    # print(l['like'], l['dislike'], l['other'])
    try:
        csv.write(str(l['like']) + ',' + 
                str(l['dislike']) + ',' +
                str(l['other']) + ',' +
                str(l['total']) + ',' +
                l['brand'] + ',' +
                l['title'] + ',' + 
                l['date'] + ',' + 
                l['link'] + ',\n')
    except:
        csv.write('>> 寫入錯誤！,\n')
    #print(l['title'])
csv.close()
print('\n>> csv 檔案已儲存在與程式相同的資料夾中！執行完畢！')

#####################################
## 寫成 exe 檔
## pyinstaller -F D:\OneDrive\ASUS_INTERN\PTT_Crawler\ptt_crawler_1.5.py