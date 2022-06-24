import requests
import time
import WenLanWebSpider.databaseInput as db
import random
from lxml import etree
import re

# 获取一个人的信息

cookie = ''

class WeiBoUserGet:
	def __init__(self):
		self.my_db = db.dataBaseInput('127.0.0.1', 'root', '123456', 'weibo', 3306)
		my_sql = """
		select t.id from(
		select t1.user_id as id ,ifnull(t2.user_sex,'0') as sex
		from weibo_user t1 left join weibo_user_sex t2 on t1.user_id = t2.user_id) t
		where t.sex = '0';
		"""
		self.user_id_tuple = self.my_db.sql_execute(my_sql,[])
		self.num = 1
		self.len = len(self.user_id_tuple)
		for user_id_br in self.user_id_tuple:
			user_id = user_id_br[0]
			resp = my_requests_get(user_id)
			dic = toDic(resp)
			dic['user_id'] = user_id
			if dic ==-1:
				pass
			else:
				self.my_db.insert_sql('weibo_user_sex',dic)
			print('-----------------------------------')
			print(user_id,'插入结束')
			print('当前进度',str(self.num*100/self.len)[:6],'%')
			self.num += 1
			print('-----------------------------------')
			time.sleep(0.5)


def toDic(resp):
	try:
		resp.encoding = 'utf-8'
		htmlEX = etree.HTML(resp.content)
		data = htmlEX.xpath('//div[7]/text()')
		dic = {}
		for i in data:
			if '性别' in i:
				dic['user_sex'] = i.split(':')[-1]
			elif '简介' in i:
				if len(i.split(':')[-1])>50:
					dic['user_intro'] = i.split(':')[-1][:50]
				else:
					dic['user_intro'] = i.split(':')[-1]
			elif '生日' in i :
				if '座' in i:
					pass
				elif '0001-00-00' ==i:
					pass
				elif len(i.split(':')[-1]) == len('01-01'):
					pass
				elif i.split(':')[-1] == '0001-00-00':
					pass
				else:
					dic['user_bir'] = i.split(':')[-1]
			else:
				pass

		print('↓↓',dic,'↓↓')

		# try:
		# 	print(dic['user_sex'],' ',dic['user_bir'],' ',dic['user_intro'])
		# except:
		# 	pass
		return dic
	except:
		return -1

def my_requests_get(user_id):
	user_id = user_id
	url = 'https://weibo.cn/{user_id}/info'.format(user_id=user_id)
	num = 0
	header = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
					  'Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31', 'cookie': cookie}
	while num < 5:
		try:
			resp = requests.get(url, timeout=60, headers=header)
			return resp
		except:
			print('出现差错重试中')
			num += 1
			time.sleep(random.random() * 0.1 + 0.05)
	print('出现差错，重试无效，请检查网络')



