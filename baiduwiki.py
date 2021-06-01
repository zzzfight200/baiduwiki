from bs4 import BeautifulSoup
import json
import requests
import datetime
import os

def CrawlBaiduWikiData():
    '''
    从百度百科返回的html中解析得到列有选手信息的table
    '''
    url = "https://baike.baidu.com/item/%E9%9D%92%E6%98%A5%E6%9C%89%E4%BD%A0%E7%AC%AC%E4%B8%89%E5%AD%A3"
    Headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0 "}
    try:
        Response = requests.get(url, headers=Headers)
        soup = BeautifulSoup(Response.text,'html.parser')
        #content = soup.findAll("p")
        #print(soup)
        tables = soup.find_all('table', {'log-set-param': 'table_view'},{'data-sort':'sortDisabled'})
        TableTitle = "参赛选手"
        # print(tables)
        for table in tables:
            # 对当前节点前面的标签和字符串进行查找
            TableTitles = table.find_previous('div').find_all('h3')
            # print(TableTitles)
            for title in TableTitles:
                if (TableTitle in title):
                    return table
    except Exception as e:
        print(e)

def ParseWikiData(table_html):
    '''
    从百度百科返回的html中解析得到选手信息，以当前日期作为文件名，存JSON文件,保存到work目录下
    '''
    bs = BeautifulSoup(str(table_html),'html.parser')
    all_trs = bs.find_all('tr')
    # print(all_trs)
    # error_list = ['\'','\"']
    stars = []
    for tr in all_trs[1:]:
         all_tds = tr.find_all('td')
         star = {}
         #姓名
         star["name"]=all_tds[0].text
         #个人百度百科链接
         star["link"]= 'https://baike.baidu.com' + all_tds[0].find('a').get('href')
         #籍贯
         star["zone"]=all_tds[1].text
         #身高
         star["height"]=all_tds[2].text
         #体重
         star["weight"]=all_tds[3].text
         #公司
         star["company"]=all_tds[4].text
         stars.append(star)
         # print(star)
         #print(stars)
    json_data = json.loads(str(stars).replace("\'","\""))
    with open('G:\\Project\\python\\baiduwiki\\' + today + '.json', 'w', encoding='UTF-8') as f:
        json.dump(json_data, f, ensure_ascii=False)

def CrawlPicUrls():
    '''
    爬取每个选手的百度百科图片，并保存
    '''
    with open('G:\\Project\\python\\baiduwiki\\'+ today + '.json', 'r', encoding='UTF-8') as file:
         json_array = json.loads(file.read())
    Headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0 "}
    for star in json_array:
        name = star['name']
        link = star['link']
        response = requests.get(link,headers=Headers)
        bs = BeautifulSoup(response.text,'html.parser')
        # print(bs)
        try:
            PicListUrl = bs.select('div .summary-pic')[0].find('a').get('href')
            #print(type(PicListUrl))
            #print(PicListUrl)
            PicListUrl = 'https://baike.baidu.com' + PicListUrl
            pic_list_response = requests.get(PicListUrl,headers=Headers)
            bsPic = BeautifulSoup(pic_list_response.text,'html.parser')
            PicListHtml = bsPic.select('.pic-list img')
            PicUrls = []
            for PicHtml in PicListHtml:
                PicUrl = PicHtml.get('src')
                PicUrls.append(PicUrl)
                print(PicUrl)
                #根据图片链接列表pic_urls, 下载所有图片，保存在以name命名的文件夹中
            DownPic(name,PicUrls)
        except Exception as e:
            print('Error！！'+ str(e))

def DownPic(name,PicUrls):
    '''
    根据图片链接列表pic_urls, 下载所有图片，保存在以name命名的文件夹中,
    '''
    path = 'G:\\Project\\python\\baiduwiki\\'+'pics\\'+name+'\\'
    if not os.path.exists(path):
        os.makedirs(path)
    for i, PicUrl in enumerate(PicUrls):
        try:
            pic = requests.get(PicUrl, timeout=15)
            string = str(i + 1) + '.jpg'
            with open(path+string, 'wb') as f:
                f.write(pic.content)
                print('成功下载第%s张图片: %s' % (str(i + 1), str(PicUrl)))
        except Exception as e:
            print('下载第%s张图片时失败: %s' % (str(i + 1), str(PicUrl)))
            print(e)
            continue
def ShowPicPath(path):
    '''
    遍历所爬取的每张图片，并打印所有图片的绝对路径
    '''
    PicNum = 0
    for (DirPath,DirNames,FileNames) in os.walk(path):
        for FileName in FileNames:
           PicNum += 1
           print("第%d张照片：%s" % (PicNum,os.path.join(DirPath,FileName)))
    print("共爬取《青春有你3》选手的%d照片" % PicNum)

if __name__ == '__main__':
    today = datetime.date.today().strftime('%Y%m%d')
    print(today)
    html=CrawlBaiduWikiData()
    ParseWikiData(html)
    CrawlPicUrls()
    ShowPicPath('G:\\Project\\python\\baiduwiki\\pics')
