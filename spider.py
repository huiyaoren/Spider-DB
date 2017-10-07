# coding:utf-8
# from booklist import *
import urllib
import re
import time
from lxml import etree
# from lab import *
from requests import Request, Session
import requests


class Spider:
    def __init__(self):
        self.url_dangdang = 'http://v.dangdang.com/book'
        self.url_douban = 'http://book.douban.com'

    def get_response(self, url):
        resp = requests.get(url=url)
        return resp.text

    def get_urls_session(self):
        ''' 获取各活动专题链接 '''
        page = self.get_response(self.url_dangdang)

        # html源码中寻找字段
        html = etree.HTML(page)
        result = html.xpath('/html/body/div/div/div/div/div/ul/li/a')
        session_list = [{'session_name': r.xpath('@title')[0] or r.xpath('span[1]/text()')[0].strip(),
                         'session_url': r.xpath('@href')[0]}
                        for r in result if len(r.xpath('span[1]/text()')) > 0]
        return session_list

    def get_books_detail(self, url_session='http://v.dangdang.com/pn0_10005415_3.html'):
        ''' 获取书籍的书名、购买地址、预览图地址、价格 '''
        page = self.get_response(url_session)
        html = etree.HTML(page)
        result = html.xpath("/html/body/div/div/div[@class='v_shop_box ']/div[@class='con v_shop_box_list']/ul/li")
        book_list = [{'book_title': r.xpath('p[1]/a/text()')[0].strip(),
                      'book_page_url': r.xpath('a/@href')[0],
                      'book_image': r.xpath('a/img/@src')[0],
                      'book_price': ''.join([r.xpath('p[2]/span[2]/span[2]/text()')[0].strip(),
                                             r.xpath('p[2]/span[2]/span[3]/text()')[0].strip()])}
                     for r in result]
        return book_list

    # 获取书籍的豆瓣评分
    def get_books_rank(self, book_title="无聊的人生，我死也不要"):
        book_title = book_title.replace("，", "+").replace(" ", "+")
        url = '{0}/subject_search?search_text={1}&cat=1001'.format(self.url_douban, book_title)
        print(url)
        # url = self.url_douban + "/subject_search?search_text={0}&cat=1001".format(book_title)
        # 文件头
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = {'User-Agent': user_agent}
        # 页面源码
        page = self.get_response(url)
        print(page)

        # request = urllib.Request(url.encode('utf8'))  # somethingwrong
        # response = urllib.urlopen(request)
        # page = response.read()
        # print len(page)

        pattern = re.compile( \
            r"(<h2.*?</h2>.*?allstar.*?pl.*?</span>)", re.S)

        items = re.findall(pattern, page)

        ranks = []
        for item in items:

            try:
                item = item.decode('utf8')  # fucking miss
            except UnicodeDecodeError:
                continue

            # 若项目无评分则丢弃项目
            if len(item.split("nums\"".encode('utf8'))) <= 1:
                continue

            rankurl = item.split("\"", 4)[3]  # bug
            book_title = item.split("title=\"", 1)[1].split("\"", 1)[0]
            rank = item.split("nums\">", 1)[1].split("<", 1)[0]
            rankpeople = item.split("pl\">\n", 1)[1].split("</span>", 1)[0].split("(", 1)[1].split(")", 1)[0]

            rank = {
                'rankurl': rankurl,
                'book_title': book_title,
                'rank': rank,
                'rankpeople': rankpeople}
            ranks.append(rank)

        return ranks

    # 完整输出+排序
    def output(self):
        pass


# 查找某专题页书目
def find_book(details, book_title="中"):
    books = []

    for detail in details:

        if re.findall(book_title.encode('utf8'), detail['book_title'], re.S):
            print(detail['book_title'], detail['booklink'], detail['price'])
            book = detail
            books.append(book)

    return books


def main():
    spider = Spider()

    print("\n")
    print("获取专题链接...")
    slinks = spider.get_urls_session()
    print("获取到{0}个专题链接".format(len(slinks)))

    datas = []
    for url in slinks:
        print("获取专题名...")
        print("------", url['session_name'], "------")

        print("获取书目...")
        details = spider.get_books_detail(url['session_url'])
        print("获取到{0}本书籍".format(len(details)))

        n = 1
        for detail in details:
            #
            #         # writeBook_txt(details)
            n += 1
            print("《{0}》".format(detail['book_title']))

            book_title = detail['book_title']  # 这里有问题
            ranks = spider.get_books_rank(book_title)  # 出错
            if len(ranks) == 0:
                print("该书尚未有人评价")
                continue
            print("￥" + detail['book_price'], ranks[0]['book_title'], ranks[0]['rank'], ranks[0]['rankpeople'])

            data = {
                'ddbook_title': detail['book_title'],
                'ddlink': detail['booklink'],
                'dbbook_title': ranks[0]['book_title'],
                'dblink': ranks[0]['rankurl'],
                'price': float(detail['price']),
                'rank': float(ranks[0]['rank']),
                'rankpeople': ranks[0]['rankpeople']}
            datas.append(data)
    datas = sorted(datas, key=lambda data: data['price'])
    datas = sorted(datas, key=lambda data: data['rank'], reverse=True)
    for data in datas:
        print(data['rank'])
        # writeData_txt(datas)


if __name__ == '__main__':
    main()
