# coding:utf-8
from __future__ import unicode_literals
#from booklist import *
import urllib2
import re
import time
from lab import *


class Spider:


	def __init__(self):
		self.dangdangURL = 'http://v.dangdang.com/book'
		self.doubanURl = 'http://book.douban.com'


	# 获取各活动专题链接 
	def getSessionlink(self):
		
		request = urllib2.Request(self.dangdangURL) 
		response = urllib2.urlopen(request) # urlopen(url, data, timeout)
		page = response.read().decode('gbk') 

		# html源码中寻找字段
		pattern = re.compile(\
			r'(<a href="http://v.dangdang.com/pn0_\d*_3.html.*?</span>)', re.S)
			#r'(<a href="http://v.dangdang.com/pn0_\d*_3.html)', re.S)

		items = re.findall(pattern, page) # findall(pattern, string, flags=0)
		
		# 从链接所处字符串位置截取链接
		sessions = []
		for item in items:		
			
			sessionurl = item[9:50]
			
			if len(item.split("\"")) == 7:
				sessionname = item.split("\"", 7)[6].split("-",1)[1].split("<",1)[0]
				
			elif len(item.split("\"")) == 33:
				sessionname = item.split("\"", 10)[9].split("-",1)[1]
				
			else:
				print "获取专题名出错"

			session = {'sessionname': sessionname, 'sessionurl': sessionurl}
			sessions.append(session)

		# 将专题链接地址写入txt文件	
		writeSession_txt(sessions) 
		
		return sessions


	# 获取书籍的书名、购买地址、预览图地址、价格 
	def getBookdetail(self, link='http://v.dangdang.com/pn0_10005415_3.html'):
				
		# page
		request = urllib2.Request(link)
		response = urllib2.urlopen(request)
		page = response.read().decode('gbk')

		# pattern
		pattern = re.compile(\
			r'(<li.*?</span></span>)', re.S)

		# findall(pattern, page)
		items = re.findall(pattern, page) # 查找字段		
		items = items[1:] # 去掉第一项无用html字段		

		# 整理信息
		books = []
		for item in items:

			# 剔除售罄书目
			if re.findall('mix_over', item):
				items.remove(item)
				continue

			# 每本书html信息用等号拆分
			item = item.split("=")

			# 书名中含有等号=会导致切分错误，懒得改直接跳过
			if len(item) != 18:
				continue

			# 将拆分后的每项信息整理			
			book = {}
			book['booklink'] = item[5].split("\"", 2)[1].encode('utf8')
			book['bookpic'] = item[7].split("\'", 2)[1].encode('utf8') # bug
			book['bookname'] = \
				item[8].split("\'", 2)[1].split("（",1)[0].split("(",1)[0].split("—",1)[0].split("-",1)[0].split("：",1)[0].encode('utf8')
			yuan = item[16].split(">",1)[1].split("<",1)[0].encode('utf8')		
			jiao = item[17].split(">",1)[1].split("<",1)[0].encode('utf8')
			book['price'] = yuan + jiao
			books.append(book)		

		return books


	# 获取书籍的豆瓣评分
	def getBookrank(self, bookname="无聊的人生，我死也不要"):
		#books = self.getBookdetail
		
		bookname = bookname.replace("，", "+").replace(" ", "+").encode('utf8') # 
		
		url = self.doubanURl + "/subject_search?search_text={0}&cat=1001".format(bookname.decode('utf8'))

		# 文件头
		user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' 
		headers = { 'User-Agent' : user_agent }

		# 页面源码
		request = urllib2.Request(url.encode('utf8')) # somethingwrong
		response = urllib2.urlopen(request)
		page = response.read()
		#print len(page)

		pattern = re.compile(\
			r"(<h2.*?</h2>.*?allstar.*?pl.*?</span>)", re.S)
		
		items = re.findall(pattern, page)
		
		ranks = []
		for item in items:

			try:				
				item = item.decode('utf8') # fucking miss
			except UnicodeDecodeError:
				continue

			# 若项目无评分则丢弃项目			 
			if len(item.split("nums\"".encode('utf8'))) <= 1: 
				continue

			rankurl = item.split("\"",4)[3].encode('utf8') # bug
			bookname = item.split("title=\"",1)[1].split("\"",1)[0].encode('utf8')
			rank = item.split("nums\">",1)[1].split("<",1)[0].encode('utf8')
			rankpeople = item.split("pl\">\n",1)[1].split("</span>",1)[0].split("(",1)[1].split(")",1)[0].encode('utf8')
			
			rank = {
				'rankurl': rankurl,
				'bookname': bookname,
				'rank':rank,
				'rankpeople': rankpeople}
			ranks.append(rank)
		
		return ranks


	# 完整输出+排序	
	def output():
		pass


# 查找某专题页书目
def findBook(details, bookname="中"):

	books = []
		
	for detail in details:

		if re.findall(bookname.encode('utf8') , detail['bookname'], re.S):
			print detail['bookname'], detail['booklink'], detail['price']
			book = detail
			books.append(book)

	return books


##############################################################


spider = Spider()

print "\n"
print "获取专题链接...".encode('utf8')
slinks = spider.getSessionlink()
print "获取到{0}个专题链接".format(len(slinks)).encode('utf8')

datas = []
for url in slinks:

	print "获取专题名...".encode('utf8')
	print "------",url['sessionname'].encode('utf8'),"------"

	print "获取书目...".encode('utf8')
	details = spider.getBookdetail(url['sessionurl'])
	print "获取到{0}本书籍".format(len(details)).encode('utf8')

	n = 1
	for detail in details:

		#writeBook_txt(details)
		n += 1
		print "《{0}》".format(detail['bookname'].decode('utf8')).encode('utf8')
	
		bookname = detail['bookname'].decode('utf8') # 这里有问题
		ranks = spider.getBookrank(bookname) # 出错
		if len(ranks) == 0:
			print "该书尚未有人评价".encode('utf8')
			continue
		print "￥".encode('utf8')+detail['price'], ranks[0]['bookname'], ranks[0]['rank'], ranks[0]['rankpeople'] 

		data = {\
			'ddbookname': detail['bookname'],
			'ddlink': detail['booklink'],
			'dbbookname': ranks[0]['bookname'],
			'dblink': ranks[0]['rankurl'],
			'price': float(detail['price']),
			'rank': float(ranks[0]['rank']),
			'rankpeople': ranks[0]['rankpeople']}		
		datas.append(data)
datas = sorted(datas, key=lambda data:data['price'])
datas = sorted(datas, key=lambda data:data['rank'], reverse=True)
for data in datas:
	print data['rank']
writeData_txt(datas)

	


'''
#print spider.getBookdetail()[0]['bookname']
'''

# 设置文件头
'''
url = 'http://www.server.com/login'  

values = {'username' : 'cqc',  'password' : 'XXXX' } 
data = urllib.urlencode(values) # urlencode()

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' 
headers = {'User-Agent': user_agent} 

request = urllib2.Request(url, data, headers) 

response = urllib2.urlopen(request)  
page = response.read()
'''

