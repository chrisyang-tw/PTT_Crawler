# 利用 Python + Selenium 製作批踢踢爬文程式

## 1. 前言

本程式能擷取 PTT 各大看板上的文章，統計各篇文章推噓文數，並匯出成 Excel 檔中。若擷取的是行動通訊板，本程式還能判斷各篇文章屬於何種廠牌。可做為監測網路聲量之用途。我也為此程式開發了執行檔 (.exe)，可供不會寫程式的人直接操作使用。

## 2. 程式操作

### Step 1: 檔案確認

確認資料夾中 "chromedriver.exe", "keyword.csv" 兩個檔案皆存在。"chromedriver" 是啟動虛擬瀏覽器的工具，"keyword.csv" 則是用來做關鍵字判斷之用。

### Step 2: 檢查與更新 keyword 檔案

若要爬取行動通訊板 (MobileComm) 的文章，可先檢查近期是否有新機上市、即將上市或有外流新聞。若有，請打開 "keyword.csv" 檔案，並將手機型號新增於 `B1` 至 `B10` 的儲存格中（每列代表的是一個品牌，品牌名稱列於 `A1` 至 `A10` 中），並以逗號 "," 與其他關鍵字區隔。**若要擷取其他看板文章，請忽略此步驟。**

**注意：請不要更動到品牌名稱，也不要更動列數**

### Step 3: 打開主程式並依畫面指示操作

打開 "ptt_crawler_1.5.exe" （以下將以主程式代表此程式），並遵循畫面指示操作。

首先選擇欲爬文的看板名稱，預設的看板包含了行動通訊板、電腦消費板、筆電消費板、科技業板，若想擷取其他看板，也可以選擇「其他」並自行輸入該看板首頁網址（例如想擷取八卦板，請輸入：https://www.ptt.cc/bbs/Gossiping/index.html）。

接著選擇文章的取得方式。取得方式分為兩種：

- 輸入天數：輸入要取得過去幾天內的文章，例如輸入 "14"，程式即會將從現在算起過去兩周的所有文章擷取下來。**由於程式的限制，此方式只適用於擷取當年度的文章，若欲取得跨年度的文章請使用第二種方式。**

- 輸入頁數：輸入程式要從哪一頁開始擷取文章。這時需要開啟瀏覽器並觀察網址列。
以 PTT 行動通訊板為例，當開啟網頁時，應會發現網址列最後一段會顯示 `"index.html"`，這時可以點擊右上角的上頁按鈕 *(如圖一)*，便會發現網址列的最後一段會變更為 `"indexXXXX.html"`，`XXXX` 四位數字便是該頁的頁數 *(如圖二)*。此時便能透過手動修改頁數，觀察該頁的發文日期，來選擇要從哪一頁開始擷取。舉例來說，我想擷取從 2018 年 1 月開始的文章，當現在所在的頁數是第 6500 頁時，我會將網址列 `"index6500.html"` 的 `6500` 更改為 6000, 5500, ...慢慢往前尋找哪一頁的時間點才是 2018 年 1 月的文章，最後找到是第 5038 頁，即可返回程式並輸入 5038，程式就能從此頁開始擷取文章。

    圖一：PTT MobileComm 首頁。
![ptt_index](/md_img/ptt_index.jpg)

    圖二：點擊上頁後，發現網址列有所改變。
![ptt_index](/md_img/ptt_index_02.jpg)

### Step 5: 開始爬蟲

在以上步驟接設定完成後將會開始執行爬蟲。此時程式會自動開啟一個 Chrome 瀏覽器視窗。若您是第一次使用，可能會跳出防火牆訊息，此為正常現象，請將其關閉或接受（拒絕亦可）。另外，主程式上將會顯示擷取的進度，若不確定程式是否有在運作，可以前往主程式上查看。

### Step 6: 執行完畢

爬蟲完畢後，瀏覽器將會關閉，此時會在主程式中看到正在寫入的訊息。寫入完成後，將會發現與程式相同的資料夾中會出現一個 CSV 檔案，可以使用 Excel 打開，但由於 CSV 檔案的特性，**請務必使用 Excel 另存新檔成 xlsx 檔後再開始於 Excel 上操作與分析**。

完成此步驟後，即可開始利用 Excel 的排序與篩選功能，挑選出想要的文章，或觀察各品牌的討論熱門程度。

## 3. 程式碼

首先先讓程式讀取品牌關鍵字。利用 ```dict()``` 將各個品牌與其對應的關鍵字連結。

```python
fh1 = open('./keyword.csv', 'r', encoding = 'big5')
brand_dict = dict()
for line in fh1:
    temp = line.lower().replace('\n', '').replace(' ', '').split('\"')
    brand_dict[temp[0].replace(',', '')] = temp[1].split(',')

a, b, c, d, e, f, g, h, i, j = list(brand_dict.keys())
```

接著選擇看板、文章取得方式和文章取得範圍皆為簡單的 ```input``` 輸入，也做了一些防呆機制，此處程式碼略。

開啟一個空白的瀏覽器並設定 cookie 值。設定 cookie 的原因在於若進入如八卦板等 18 禁看板時，若沒有設定 cookie 將會被阻擋。

```python
driver = webdriver.Chrome('./chromedriver.exe')
driver.get(index)
driver.add_cookie({'name': 'over18', 'value': '1'})
driver.get(index)
```

抓取網頁時會先用 *BeautifulSoup* 得到網頁原始碼，再將其放入自行製作好的 function 中。由於 function 程式碼較為複雜，為了方便修訂與檢閱，我將此區塊獨立存放，可在 *crawler_tool.py* 當中找到。首先先得到每篇文的標題、日期、連結。

```python
for i in soup.find_all('div', 'r-ent'):
    meta = i.find('div', 'title').find('a') or not_exist
    date = dt.datetime.strptime(i.find('div', 'date').getText().strip(), '%m/%d').strftime('%m-%d')
    if meta.getText().strip() != '(本文已被刪除)' and start_date <= date <= end_date:
        articles.append({
            'title': meta.getText().strip(),
            'date': i.find('div', 'date').getText(),
            'link': 'https://www.ptt.cc' + meta.get('href'),
        })
```

接著我們還必須額外紀錄推噓文數。PTT 文章列表上的數字顯示的並不是總留言數，而是推文減去噓文後的數值，忽略了註解的數量。如果想要確切得知總留言數有多少，就必須一篇篇文章進入計算，也就是此段程式在做的事。

```python
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
```

執行完這個 *function* 後輸出的結果只有一個：*articles*。這個 *articles* 是一個 *list*，陣列裡的每一個元素都是 *dictionary*，大概長得像這樣：

```python
articles = [{'title': '[問卦] 有沒有住在陶朱隱園的鄉民？',
             'date': '7/10',
             'link': 'https://www.ptt.cc/bbs/Gossiping/M.1562728765.A.461.html'},
             'like': 7,
             'dislike': 2,
             'other': 6,
             'total': 15},
            {...},
            ...
            ]
```
回到 *ptt_crawler_1.5.py* ，最後是寫入檔案的部分。當運作看板是行動通訊板時，就需要做品牌分類的動作，由於需重複執行，我同樣將此 *function* 獨立成一個區塊。

```python
def calculate_freq(txt, brand_name_list, brand_name):
    brand = ''
    for keyword in brand_name_list:
        if keyword in txt:
            brand = brand_name
    return brand
```