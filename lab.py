# coding:utf8
from __future__ import unicode_literals
import os
import time
import xlwt


# 获取日期
def getTime():
	ISOTIMEFORMAT = '%Y-%m-%d'
	localtime = time.strftime(ISOTIMEFORMAT, time.localtime())
	return localtime


# 活动专题链接
def writeSession_txt(sessions):
	time = getTime()+" "+"sessions.txt"
	f = open(time, 'w')
	for session in sessions:
		txt = session['sessionname']+"|"+session['sessionurl']
		f.write(txt.encode('utf8'))
		f.write('\n')


def writeSession_xls(sessions):
	#time = getTime()+" "+"sessions.txt"

	pass


# 专题下书籍信息
def writeBook_txt(books,n=""):	
	time = getTime()+" "+"book{0}.txt".format(n)
	f = open(time, 'w')
	for book in books:
		I = "||".encode('utf8')
		A = "@@".encode('utf8')
		txt = book['bookname']+I+book['price']+I+book['booklink']+I+book['bookpic']+A
		f.write(txt)
	f.write('\n')


# 全部书籍详细信息
def writeData_txt(datas,name='datas.txt'):
	time = getTime()+" "+"{0}".format(name)
	f = open(time, 'w')
	for data in datas:
		I = "||".encode('utf8')
		A = "@@".encode('utf8')
		txt = \
			str(data['price'])+I+data['ddbookname']+I+data['dbbookname']+I+str(data['rank'])\
			+I+data['rankpeople']+I+data['ddlink']+I+data['dblink']+A
		f.write(txt)
		

def deleteShit(name):
	time = getTime()+" "+"{0}".format(name)
	datas = []
	f = open(time, 'r')
	shits = f.read()
	shits = shits.decode('utf8').split("@@".encode('utf8'))
	for shit in shits:
		if len(shit.split("少于")) >1:
			continue
		if len(shit.split("目前")) >1:
			continue			
			
		data = {}
		s = shit.split('||'.encode('utf8'))
		#print s
		data['price'] = s[0].encode('utf8')
		try:
			data['ddbookname'] = s[1].encode('utf8')
		except IndexError:
			continue
		data['dbbookname'] = s[2].encode('utf8')
		data['rank'] = s[3].encode('utf8')
		data['rankpeople'] = s[4].encode('utf8')
		data['ddlink'] = s[5].encode('utf8')
		data['dblink'] = s[6].encode('utf8')
		datas.append(data)	
	
	print "afterbooks:", len(datas)
	return datas



sessions = [\
	{'sessionname': 'sessionname1', 'sessionurl': 'sessionurl1'},
	{'sessionname': 'sessionname2', 'sessionurl': 'sessionurl2'}]


books = [\
	{'bookname':'bookname1','price':'price1','booklink':'booklink1','bookpic':'bookpic1'},
	{'bookname':'bookname2','price':'price2','booklink':'booklink2','bookpic':'bookpic2'}]


data = [\
	{
	'ddbookname':'书名11' ,
	'ddlink': 'link1',
	'dbbookname': '书名2',
	'dblink': 'link22',
	'price': 12.0,
	'rank': 5.0,
	'rankpeople':'232人' 
	},
	{
	'ddbookname':'书名12' ,
	'ddlink': 'link2',
	'dbbookname': '书名3',
	'dblink': 'link221',
	'price': 13.0,
	'rank': 6.0,
	'rankpeople':'11人' 
	}]	

#-----------------------------
#datas = deleteShit('2015-12-14 datas.txt')
#writeData_txt(datas,'shit.txt')


#writeSession_txt(sessions)
#writeBook_txt(books)

