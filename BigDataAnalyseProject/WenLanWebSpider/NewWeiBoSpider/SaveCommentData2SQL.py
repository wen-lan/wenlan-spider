# -- coding: utf-8 --**
import random
import time

import WenLanWebSpider.NewWeiBoSpider.InnerPart as weiboInPart
import WenLanWebSpider.databaseInput as db
from dateutil.parser import parse

# 走热门似乎是需要cookie的并且 ip检测很严重，
# 可以设置一个精选模块才需要使用热门查询

class SaveCommentData2SQL:
	def __init__(self):
		self.my_db = db.dataBaseInput('127.0.0.1', 'root', '123456', 'weibo', 3306)
		self.sql_update_jingxuna = 'update main_table_url set if_jingxuan = 1 where url_kry = %s'
		# 测试用 limit 30
		# 测试状态 == 111
		# 目前是测试状态，记得未来把代码还回来！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
		sql = """
			select url_kry,com_num,ifnull(true_num,0),rate,jingxuan from(
			select url_kry,com_num,ifnull(true_num,0),ROW_NUMBER() over() as true_num ,ifnull(true_num/com_num,0) as rate,if_jingxuan as jingxuan from 
			(select * from main_table_url) as t1
			left join 
			(select url_key, count(1) as true_num from weibo_comment group by url_key) as t2
			on t1.url_kry = t2.url_key) t2 
		"""
		self.aim_url = []
		url_tuple = self.my_db.sql_execute(sql,[])
		for url in url_tuple:
			# 如果 rate小于0.5 那么会添加需要捕获的url
			if url[4]== 0:
				# 这是不是精选评论 或者没有扫描过的
				if url[1] <1001:
					# 暂时修改
					if url[3] <0.2:
						self.aim_url.append(url[0])
				elif url[1] <10000 and url[1] >1000:
					if url[3] <0.2:
						self.aim_url.append(url[0])
				else:
					if url[3] <0.13:
						self.aim_url.ap3pend(url[0])
		self.len =len(self.aim_url)
		print('需要获取',self.len)
		self.aim_count = 1
		#####################
		# from dateutil.parser import parse
		# parse(date1).strftime('%Y-%m-%d %H:%M:%S')
		# 时间处理
		self.base_url = 'https://weibo.com/ajax/statuses/show?id='
		for i in self.aim_url:
			# i 是 对应的索引
			print('------------------------------------------')
			print('↓↓↓↓↓↓↓↓↓↓↓↓',self.base_url+i,'开始获取')
			datas = weiboInPart.InnerPart(self.base_url+i)

			if datas.jingxuan ==1:
				# 如果他是一个精选 那么意味着我们需要修改
				try:
					self.my_db.sql_execute(self.sql_update_jingxuna, i)
					self.my_db.conn.commit()
					print("------------------------")
					print('修改精选成功')
					print("------------------------")
				except Exception as e:
					print(e)
					print("------------------------")
					print('失败修改精选')
					print("------------------------")
					self.my_db.conn.rollback()
			# 存储数据
			for data in datas.get_data():
				if data == {}:
					continue
				dic_comment = {'url_key': i, 'com_content': data['comment'], 'com_time': time_clean(data['time']),
							   'user_id': data['user_id']}
				dic_user = {'user_id': data['user_id'], 'user_name':data['user_name'], 'user_location':data['user_location']}
				# 接下来是写入data 首先要判断数据是否存在， 先从user开始，然后再从comment 开始
				# 评论表，判断数据是否存在依据 用户id 和创建时间
				# user表 根据用户id判断
				# 插入用户表
				self.find_insert_user_table(dic_user)
				self.find_insert_comment_table(dic_comment)

			print('当前完成度', self.aim_count * 100 / self.len, '%')
			self.aim_count += 1
			time.sleep(10*random.random() + 5)

	# self.data = weiboInPart.InnerPart()
	# 查询用户表是否存在 存在就插入

	def find_insert_user_table(self,dic):
		sql = """
			select user_id from weibo_user where user_id = %s limit 1
		"""
		num = self.my_db.sql_execute(sql,dic['user_id'])
		if num == ():
			self.my_db.insert_sql('weibo_user',dic)

	def find_insert_comment_table(self,dic):
		sql = """
					select user_id from weibo_comment where user_id = %s and com_time = %s limit 1
				"""
		num = self.my_db.sql_execute(sql, [dic['user_id'],dic['com_time']])
		if num == ():
			self.my_db.insert_sql('weibo_comment',dic)
# 很方便的时间处理函数
def time_clean(time_str):
	return parse(time_str).strftime('%Y-%m-%d %H:%M:%S')