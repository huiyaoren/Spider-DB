import re

import requests
from lxml import etree
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class Spider:
    def __init__(self):
        self.url_dangdang = 'http://v.dangdang.com/book'
        self.url_douban = 'http://book.douban.com'
        self.browser = webdriver.Chrome()

    def get_response(self, url):
        headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
        resp = requests.get(url=url, headers=headers)
        return resp.text

    def get_urls_session(self):
        ''' 获取各活动专题链接 '''
        page = self.get_response(self.url_dangdang)
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

    def get_books_rank(self, book_title="环界asdfasdf"):
        ''' 获取书籍的豆瓣评分 '''
        book_title = book_title.replace("，", "+").replace(" ", "+")
        url = '{0}/subject_search?search_text={1}&cat=1001'.format(self.url_douban, book_title)
        browser = self.browser
        browser.get(url)
        book = {}

        def book_rank(num, book):
            book['rank'] = browser.find_element_by_xpath(
                '//*[@id="root"]/div/div[2]/div[1]/div[1]/div[{0}]/div/div[2]/span[2]'.format(num)).text
            book['book_title'] = browser.find_element_by_xpath(
                '//*[@id="root"]/div/div[2]/div[1]/div[1]/div[{0}]/div/div[1]/a'.format(num)).text
            book['rank_count'] = browser.find_element_by_xpath(
                '//*[@id="root"]/div/div[2]/div[1]/div[1]/div[{0}]/div/div[2]/span[3]'.format(num)).text

        rank = []
        try:
            book_rank(1, book)
        except NoSuchElementException:
            try:
                book_rank(2, book)
            except NoSuchElementException:
                pass
        except:
            pass
        else:
            rank = [book]
        return rank


# 查找某专题页书目
def find_book(details, book_title="中"):
    books = []
    for detail in details:
        if re.findall(book_title, detail['book_title'], re.S):
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
            # writeBook_txt(details)
            n += 1
            print("《{0}》".format(detail['book_title']))
            book_title = detail['book_title']  # 这里有问题
            ranks = spider.get_books_rank(book_title)  # 出错
            if len(ranks) == 0:
                print("该书尚未有人评价")
                continue
            print("￥" + detail['book_price'], ranks[0]['book_title'], ranks[0]['rank'], ranks[0]['rank_count'])
            data = {
                'ddbook_title': detail['book_title'],
                'ddlink': detail['book_page_url'],
                'dbbook_title': ranks[0]['book_title'],
                # 'dblink': ranks[0]['rankurl'],
                'price': float(detail['book_price']),
                'rank': float(ranks[0]['rank']),
                'rankpeople': ranks[0]['rank_count']}
            datas.append(data)
    datas = sorted(datas, key=lambda data: data['price'])
    datas = sorted(datas, key=lambda data: data['rank'], reverse=True)
    for data in datas:
        print(data['rank'])
        # writeData_txt(datas)


if __name__ == '__main__':
    main()
