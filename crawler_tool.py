import requests
from bs4 import BeautifulSoup
import urllib.parse ## url 相關應用
import datetime as dt

## 如果遇到已被刪除的文章，結構不同，自行生成<a>
not_exist = BeautifulSoup('<a>(本文已被刪除)</a>', 'lxml').a

##############################################
## 爬取一頁的文章
def get_onepage(soup, service, num):
    articles = []
    ## 判斷日期模式（依照日期爬取文章）
    if service == 1:
        diff = dt.timedelta(days = num - 1)
        end_date = dt.datetime.today().date()
        start_date = end_date - diff
        end_date = end_date.strftime('%m-%d')
        start_date = start_date.strftime('%m-%d')

        ## 紀錄文章標題、判別日期
        for i in soup.find_all('div', 'r-ent'):
            meta = i.find('div', 'title').find('a') or not_exist
            date = dt.datetime.strptime(i.find('div', 'date').getText().strip(), '%m/%d').strftime('%m-%d')
            if meta.getText().strip() != '(本文已被刪除)' and start_date <= date <= end_date:
                articles.append({
                    'title': meta.getText().strip(),
                    'date': i.find('div', 'date').getText(),
                    'link': 'https://www.ptt.cc' + meta.get('href'),
                })
    ## 純判斷頁數模式
    else:
        for i in soup.find_all('div', 'r-ent'):
            meta = i.find('div', 'title').find('a') or not_exist
            if meta.getText().strip() != '(本文已被刪除)':
                articles.append({
                    'title': meta.getText().strip(),
                    'date': i.find('div', 'date').getText(),
                    'link': 'https://www.ptt.cc' + meta.get('href'),
                })
    ## 紀錄推噓
    for j in articles:
        req = requests.Session()
        req.cookies.set('over18', '1')
        response2 = req.get(j['link'])
        soup2 = BeautifulSoup(response2.text, 'lxml')

        j['like'] = j['dislike'] = j['other'] = 0
        for i in soup2.find_all('div', 'push'):
            temp = i.find('span')
            if temp == None:
                break
            else:
                if temp.getText() == '推 ':
                    j['like'] += 1
                elif temp.getText() == '噓 ':
                    j['dislike'] += 1
                else:
                    j['other'] += 1
        j['total'] = j['like'] + j['dislike'] + j['other']

    # next_link = soup.find('div', 'btn-group-paging').find_all('a', 'btn')[1].get('href') ## 控制頁面選項(上一頁)
    
    return articles

##############################################
## 計算關鍵字出現的頻率，當標題中含有這些關鍵字就會 + 1
def calculate_freq(txt, brand_name_list, brand_name):
    brand = ''
    for keyword in brand_name_list:
        if keyword in txt:
            brand = brand_name
    return brand