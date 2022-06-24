# -- coding: utf-8 --**
import random
import time
import datetime
import re
from WenLanWebSpider import dataDisposeFunc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests

# 这是微博爬虫，根据评论区url 返回所有的值，使用get_data获取，数据存储
# 格式为 list的字典，字典的对应
# 用户数据 可以通过cn端口进行访问 这意味着我们现在数据库写一点东西，然后接着去查询
# comment 评论内容 time utc形式的时间 comment_location 发送信息时地址 user_id 用户id 用来标识唯一用户  user_name 普通的名称 user_location 用户所在地
# time 数据库中写的是 com_time comment 数据库中写的是com_content
# 传入参数为 评论区url
# 之前没有定义存放data 的对象，直接用 __data 出现了不少差错 ，很可怕， 居然能跑，毫无问题，简直令人震撼 后面改成自己的list了
# 遇到过 这样的问题，他卡在那里 不报错 ， 我查过感觉不是循环问题， 感觉是request 请求太久， 我把request 改成了timeout =60 最多60s 就结束

#修改热门请修改 两处 热门可以查询那些精选内容
# 热门需要cookie 给一个就行
# 然后热门似乎给的速度也很奇怪
cookie = ''
class InnerPart:
	def __init__(self, url):
		# 获取cookie 不需要cookie
		# 'https://weibo.com/6545577536/LuWPAB6Ru' 转换
		# 'https://weibo.com/ajax/statuses/show?id=LuWPAB6Ru'
		# self.url = 'https://weibo.com/ajax/statuses/show?id='+url.split('/')[-1]
		self.url = url
		self.num = 1
		# 设置等待时间 ，如果出现空包 休息 且增加等待时间
		self.wait = 0
		self.__data_my = []
		self.te_url = []
		self.jingxuan = 0
		self.__session = requests.Session()
		self.__session.headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
						  'Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31'}
		# 这里应该设计url
		bad = 0
		try:
			resp = self.__session.get(self.url,timeout=60)
			temp = resp.json()
			self.mid = temp['topic_struct'][0]['actionlog']['ext'].split('|')[0].split(':')[1]
			self.uid = temp['topic_struct'][0]['actionlog']['ext'].split('|')[5].split(':')[1]
			print('mid,uid获取成功')
		except Exception as e:
			print(e)
			time.sleep(10)
			try:
				print("重试中")
				resp = self.__session.get(self.url)
				temp = resp.json()
				self.mid = temp['topic_struct'][0]['actionlog']['ext'].split('|')[0].split(':')[1]
				self.uid = temp['topic_struct'][0]['actionlog']['ext'].split('|')[5].split(':')[1]
			except Exception as e:
				print(e)
				time.sleep(1.5+self.wait)
				try :
					print("排除另外类型的微博")
					resp = self.__session.get(self.url)
					temp = resp.json()
					self.mid = temp['mid']
					self.uid = ''
				except Exception as e:
					print(e)
					bad = -1
		if bad == -1:
			print('mid,uid获取失败')
			self.__data_my.append({})
		else:

			# 这个uid 很莫名其妙 我不明白，但他用一种莫名其妙的方法实现了莫名其妙的数据获取
			# 虽然可以没他，但是按道理应该有6个数据的包 不是很清楚为什么
			# 一个程序是否正确的标记，正常是1
			self.good = 1
			self.__data_my = []
			# 这是第一次访问的起始url
			# https://weibo.com/ajax/statuses/buildComments?flow=1&id=4773759908844516&is_show_bulletin=2&is_mix=0&count=10&uid=6545577536
			# 热门的url
			# https://weibo.com/ajax/statuses/buildComments?is_reload=1&id=4740446158588734
			# &is_show_bulletin=2&is_mix=0&count=10&uid=1682207150
			'https://weibo.com/ajax/statuses/buildComments?is_reload=1&id={mid}' \
			'&is_show_bulletin=2&is_mix=0&count=10&uid={uid}'.format(mid=self.mid, uid=self.uid)
			# 普通的
			self.fir_url = 'https://weibo.com/ajax/statuses/buildComments?flow=1&is_reload=1&id={mid}' \
						   '&is_show_bulletin=2&is_mix=0&count=10&uid={uid}'.format(mid=self.mid, uid=self.uid)
			# 热门的
			# self.fir_url = 'https://weibo.com/ajax/statuses/buildComments?is_reload=1&id={mid}' \
			# '&is_show_bulletin=2&is_mix=0&count=10&uid={uid}'.format(mid=self.mid, uid=self.uid)


			resp = my_requests_get(self.fir_url)


			#### 尝试解决精选评论 标记
			try:
				print(resp.json()['header_text'])
				if resp.json()['header_text'].strip() == '以下为博主精选评论':
					self.jingxuan = 1

			except:
				pass

			try:
				# 目前看到的几种类型
				# trendsText: "博主已开启评论精选"#
				# trendsText: "已过滤不当言论，部分评论暂不展示"
				# trendsText: "已加载全部评论"  这个已加载全部评论 只是部分加载全部评论 而不是真的是全部评论 武士就好
				print(resp.json()['trendsText'])
				if resp.json()['trendsText']=='博主已开启评论精选' or resp.json()['trendsText']=='已过滤不当言论，部分评论暂不展示':
					self.jingxuan = 1
			except:
				pass

			#########

			if resp == -1:
				# 处理请求
				print('差错')
				self.good = -1
			else:
				rs = resp.json()
				self.__json_solve(rs)
				# 设置新的max id
				try:
					self.max_id = rs['max_id']
				except:
					self.max_id = 0
				while self.max_id!=0:
					self.__get_data()
					if self.good==-1:
						print('出现差错，该评论区获取失败')
						break
					time.sleep(random.random()*1+self.wait)


				print('共获取', len(self.__data_my), '条评论')
				print('↑↑↑↑↑↑↑↑↑↑↑↑',self.url,'获取结束')
				print('------------------------------------------')

	# 获取每页的评论
	def __get_data(self):
		# 普通的
		url = 'https://weibo.com/ajax/statuses/buildComments?flow=1&is_reload=1&id={mid}&is_show_bulletin=2' \
			  '&is_mix=0&max_id={max_id}&count=20&uid={uid}' \
			.format(mid=self.mid, max_id=self.max_id, uid=self.uid)
		# 热门的
		# url = 'https://weibo.com/ajax/statuses/buildComments?flow=0&is_reload=1&id={mid}&is_show_bulletin=2' \
		# 	  '&is_mix=0&max_id={max_id}&count=20&uid={uid}' \
		# 	.format(mid=self.mid, max_id=self.max_id, uid=self.uid)


		resp = my_requests_get(url)

		# 严查精选评论 后面根据这个来给精选加标签 啧啧
		if resp==-1:
			self.good=-1
		else:
			print('尝试获取第', self.num, '个模块', url)
			self.num += 1
			try:
				rs = resp.json()
			except Exception as e:
				# 可能返回数据不是json  看看问题
				print(e)
				print(resp.text)
				rs = {}
			# 初始化子评论列表
			self.te_url = []
			self.__json_solve(rs)
			# 看看是否存在子评论，如果存在评论评论 那么执行 评论评论捕获器
			if len(self.te_url) == 0:
				pass
			else:
				for url in self.te_url:
					mid = url.split('?')[-1].split('&')[0].split('=')[-1]
					self.__get_data_com(mid,0)


			# 查询是否存在下一页
			try:
				self.max_id = rs['max_id']
			except Exception as e:
				print(e)
				# 这里报错 就是 rs有问题 跳到下一个去
				self.max_id = 0

			# 这个解决是不正确的 因为不是精选评论似也有，可能造成没精选但是没数据的问题
			# 尝试排除精选评论 莫名其妙传送的现象
			try:

				trendsText = rs['trendsText']
				if trendsText == "已加载全部评论" and rs['data']==[]:
					# 下面的语句 代表被ip可能被查封抓获了，获取不到信息
					if self.max_id !=0:
						# 休息平均75s再说 看看能不能ip解脱
						time.sleep(50+random.random()*50)
						# 然后整体运行时间增加1秒
						if self.wait<3:
							self.wait += 0.25
						else:
							self.max_id = 0


			except:
				pass



	# 用于获取评论评论的
	def __get_data_com(self,mid,max_id):
		url = 'https://weibo.com/ajax/statuses/buildComments?flow=1&is_reload=1&id={mid}&is_show_bulletin=2' \
			  '&is_mix=0&fetch_level=1&max_id={max_id}&count=20&uid={uid}' \
			.format(mid=mid, max_id=max_id, uid=self.uid)
		resp = my_requests_get(url)
		if resp == -1:
			self.good = -1
		else:
			try:
				rs = resp.json()
			except Exception as e:
				print(e)
				rs = {}

			self.__json_solve_com(rs)
			# 查询是否存在子评论
			try:
				max_id = rs['max_id']
			except:
				max_id = 0
			if str(max_id) == '0':
				return
			else:
				return self.__get_data_com(mid,max_id)

	def __json_solve(self, rs):
		if rs == {}:
			print('报错继续')
			return
		for i in rs['data']:
			# 查询该条评论是否有子评论 如果有添加到子评论里面去
			try:
				te_url = i['more_info']['scheme']
				# sinaweibo://detailbulletincomment?comment_id=4740395764814277&is_show_bulletin=2
				# 目标 https://weibo.com/ajax/statuses/buildComments?is_reload=1&id=4740395764814277
				# &is_show_bulletin=2&is_mix=1&fetch_level=1&max_id=0&count=20&uid=1925878362
				self.te_url.append(te_url)
			except:
				pass

			dic = {}
			dic['comment'] = i['text_raw']
			dic['time'] = i['created_at']
			# 发微博的地点
			# dic['comment_location'] = i['source']
			dic['user_id'] = i['user']['id']
			dic['user_name'] = i['user']['name']
			dic['user_location'] = i['user']['location']
			self.__data_my.append(dic)

	# 子评论数据获取
	def __json_solve_com(self, rs):
		if rs == {}:
			print('报错继续')
			return
		for i in rs['data']:
			dic = {}
			dic['comment'] = i['text_raw']
			dic['time'] = i['created_at']
			# 发微博的地点
			# dic['comment_location'] = i['source']
			dic['user_id'] = i['user']['id']
			dic['user_name'] = i['user']['name']
			dic['user_location'] = i['user']['location']
			self.__data_my.append(dic)

	def get_data(self):
		return self.__data_my


def my_requests_get(url):
	num = 0
	header = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
						  'Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31','cookie':cookie}
	while num < 5:
		try:
			resp = requests.get(url,timeout=60,headers=header)
			return resp
		except:
			print('出现差错重试中')
			num += 1
			time.sleep(random.random() * 2 + 0.7)
	print('出现差错，重试无效，请检查网络')
	return -1
