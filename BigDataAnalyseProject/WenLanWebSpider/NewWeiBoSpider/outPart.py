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
import WenLanWebSpider.databaseInput as db
#
# 将google浏览器添加至环境路径然后启动cmd在命令行输入以下内容
# chrome.exe --remote-debugging-port=9222 --user-data-dir="D:\chromeselenium"
# 会打开一个网页 在这个网页可以实现登录 然后挂起然后运行下面的代码 令selenium接管浏览器


# 一条 修改数据成功 这代表 一条数据被修改了
# 如果是插入数据，那么则不会显示

#俄乌局势tag
# 获取一页到数据完成需要10s多 10 * 50 = 12 分钟
# 时间计算，每翻一页等个20-30s 50个需要 50*30s = 25分钟
# 点一个页面需要等待，假设全部是有效信息 24* 5s * 50 = 100分钟
# 假设查询需要时间 但是有索引 所以 一个按1s计算 读取写入
# 预测大概需要3h爬取索引信息


class OutPart:
	def __init__(self):

		# 关注俄乌局势最新进展# 今日阅读4090.7万
		# https://s.weibo.com/weibo?q=%23%E5%85%B3%E6%B3%A8%E4%BF%84%E4%B9%8C%E5%B1%80%E5%8A%BF%E6%9C%80%E6%96%B0%E8%BF%9B%E5%B1%95%23
		# 热评
		# https://s.weibo.com/hot?q=%23%E5%85%B3%E6%B3%A8%E4%BF%84%E4%B9%8C%E5%B1%80%E5%8A%BF%E6%9C%80%E6%96%B0%E8%BF%9B%E5%B1%95%23&xsort=hot&suball=1&tw=hotweibo&Refer=realtime_hot
		# tag 俄乌局势 今日阅读1359.1万
		# https://s.weibo.com/weibo/%23%E4%BF%84%E4%B9%8C%E5%B1%80%E5%8A%BF%23&page=1
		# 俄乌局势 热评
		# https://s.weibo.com/hot?q=%23%E4%BF%84%E4%B9%8C%E5%B1%80%E5%8A%BF%23&xsort=hot&suball=1&tw=hotweibo&Refer=weibo_hot
		# 乌克兰局势# 今日阅读566.1万
		# https://s.weibo.com/weibo/%23%E4%B9%8C%E5%85%8B%E5%85%B0%E5%B1%80%E5%8A%BF%23
		# #乌克兰# 今日阅读424.6万
		# https://s.weibo.com/weibo?q=%23%E4%B9%8C%E5%85%8B%E5%85%B0%23
		# tag 俄乌局势最新进展 今日阅读81.8万
		# https://s.weibo.com/weibo?q=%23%E4%BF%84%E4%B9%8C%E5%B1%80%E5%8A%BF%E6%9C%80%E6%96%B0%E8%BF%9B%E5%B1%95%23
		#
		self.__url = 'https://s.weibo.com/weibo/%23%E4%B9%8C%E5%85%8B%E5%85%B0%E5%B1%80%E5%8A%BF%23'
		self.__chrome_options = Options()
		self.my_db = db.dataBaseInput('127.0.0.1', 'root', '123456', 'weibo', 3306)
		self.__chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")  # 前面设置的端口号
		self.__web = webdriver.Chrome(options=self.__chrome_options)  # executable执行webdriver驱动的文件
		self.__page_num = 1
		self.__data = []
		self.__web.get(self.__url)
		# 查询是否存在这样的url_key 如果有那么返回1
		self.sql_select_url_key = 'select com_num from main_table_url where url_kry = %s limit 1'
		# 修改num值
		# 传递两个参数 第一个参数是 数目 num 第二个是key
		self.sql_update_num = 'update main_table_url set com_num = %s where url_kry = %s'
		# 登录时间
		time.sleep(5)
		print('目标定向中')
		while self.__page_num<=50:
			self.__get_start()
		print('定向结束')

	# 每一页进行操作
	#  {'num': '24', 'aim_url': 'LuWQ3kiR6'} 返回这样的list表
	def __get_start(self):
		temp_num = 0
		while temp_num<5:
			try:
				webs = self.__web.find_elements(By.XPATH,'//div[@action-type="feed_list_item"]')
				break
			except:
				time.sleep(5)
				temp_num+=1
		for page in webs:
			dic = {}
			# 偷个懒就不写现在的日期了
			try:
				num = page.find_element(By.XPATH,'.//div[@class="card-act"]/ul/li[2]/a').text.strip()
			except:
				num = 0

			if num == '评论':
				continue
			# 重复技术
			count = 0
			if int(num)>11:
				time.sleep(3)
				comfirmdel = page.find_element(By.XPATH,'.//div[@class="card-act"]/ul/li[2]/a')
				self.__web.execute_script("arguments[0].click();", comfirmdel)
				time.sleep(3+random.random())
			else:
				continue
			while count <5 :
				try:

					url = page.find_element(By.XPATH,
									  './/div[@node-type="feed_list_repeat"]/div/div[3]/a').get_attribute('href')
					break
				except:
					count+=1
					print("继续等待中，尝试重新点击")
					comfirmdel = page.find_element(By.XPATH, './/div[@class="card-act"]/ul/li[2]/a')
					self.__web.execute_script("arguments[0].click();", comfirmdel)
					time.sleep(6)
			if count>5:
				print('一条消息获取失败')
				continue
			dic['com_num'] = num
			try:
				print(url)
			except:
				pass
			dic['url_kry'] = url.split('/')[-1]
			self.__data.append(dic)

		print(self.__data)
		for i in self.__data:
			self.write_database(i)
		self.__data = []
		print('第',self.__page_num,'页读取并写入完毕')
		self.__page_num += 1


		# 查询 下一页 ，不然那会点到上一页 a[text() = "下一页"]

		try:
			button_next_page = self.__web.find_element(By.XPATH, '//div[@class="m-page"]/div/a[text() = "下一页"]')
			self.__web.execute_script("arguments[0].click();", button_next_page)
		except:
			time.sleep(5)
			try:
				button_next_page = self.__web.find_element(By.XPATH, '//div[@class="m-page"]/div/a[text() = "下一页"]')
				self.__web.execute_script("arguments[0].click();", button_next_page)
			except:
				print('没有下一页了')
				self.__page_num = 99999
				return -1
		time.sleep(5 + random.random()*3)


	def write_database(self,dic):
		num = self.my_db.sql_execute(self.sql_select_url_key, dic['url_kry'])
		if num !=():
			try:

				self.my_db.sql_execute(self.sql_update_num,[dic['com_num'],dic['url_kry']])
				self.my_db.conn.commit()
				print('修改数据成功')
			except Exception as e:
				print(e)
				print('失败修改')
				self.my_db.conn.rollback()
		else:
			self.my_db.insert_sql('main_table_url',dic)


	def get_data(self):
		return self.__data