import time
import datetime
import re
import random
from WenLanWebSpider import dataDisposeFunc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from WenLanWebSpider import databaseInput

# 数据写入 与刷新 不是更改评论数目的
# 负责查询并 获取外层页面数据 观察者网
# chrome.exe --remote-debugging-port=9222 --user-data-dir="D:\chromeselenium"

class guanchaGetUrl():
	def __init__(self):
		# 设置停止时间 数字 加上数字乘以（0~1）
		self.time_sleep = 1
		# 查询第几条新闻
		self.new_num = 1
		# 相关参数设定
		chrome_options = Options()
		# chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
		chrome_options.add_argument("headless")
		self.web = webdriver.Chrome(options=chrome_options)  # executable执行webdriver驱动的文件
		# conn = pymysql.connect(host ='127.0.0.1',user='root',password='123456',database='bigdata',port=3306)
		self.web.get('https://www.guancha.cn/api/search.htm?click=news&keyword=%E4%BF%84%E4%B9%8C%E5%B1%80%E5%8A%BF')
		# 调整为时间顺序
		time.sleep(self.random_time())
		self.stop = 1
		self.web.find_element(By.XPATH, '//span[@class="hot-topic-type-sort sort-time"]').click()
		time.sleep(self.random_time())
		self.__pull_down()
		temp = '查看更多内容...'
		self.db = databaseInput.dataBaseInput('127.0.0.1','root','123456','bigdata',3306)
		while temp == '查看更多内容...':
			# 数据获取
			if self.stop == -1:
				print('发现重复数据，数据更新停止')
				break
			self.get_data()
			# 返回一个值 代表数据是否存在于数据库之中
			# 数据下拉
			temp = self.__pull_down_and_next_page()
			print(temp)
			# self.web.close()
		self.db.close()

	def get_data(self):
		# 临时计数 一次采集20个 count 最多是19
		count = 0
		# 这个是默认的查询位置 后面添加数字 查询数字在默认设置里面改
		xpath_first = '//ul[@class="article-list search-news-list"]/li['
		while count < 20:
			# 大标题
			b = xpath_first+str(self.new_num)+']/div[1]/h4/a'
			cou = 0
			while cou <10:
				try:
					news_name = self.web.find_element(By.XPATH,b).text
					# 标题网页
					news_url = self.web.find_element(By.XPATH,xpath_first+str(self.new_num)+']/div[1]/h4/a').get_attribute('href')
					# 评论数目
					news_com_num = self.web.find_element(By.XPATH,xpath_first+str(self.new_num)+']/div[2]/ul/li[2]/a/span').text
					# 新闻发布时间
					news_time = self.web.find_element(By.XPATH,xpath_first+str(self.new_num)+']/div[2]/span').text
					insert_dic = {'n_name': news_name, 'n_url': news_url, 'n_time': news_time, 'n_num' : news_com_num}
					break
				except:
					print('似乎数据访问到了终点正在确认')
					time.sleep(self.random_time()*0.5)
					cou +=1
			# 这里修改成一个数据存储 写入sql 如果发现重复的，那么中止运行
			# 看看数据是否存在
			if cou>=10:
				print('无法获取到新数据')
				self.stop = -1
				break
			test = self.db.sql_execute('select n_name from newsdata where n_time=%s limit 1',news_time)
			print(test)
			if test == ():
				self.db.insert_sql('newsdata',insert_dic)
				print('开始写入数据',news_name)
			else:
				print('数据已存在')
				self.stop = -1
				break
			count+=1
			self.new_num+=1

	# 产生随机停止时间
	def random_time(self):
		return random.random() * self.time_sleep + self.time_sleep

	# 页面下拉
	def __pull_down(self):
		self.web.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(self.random_time())

	# 该函数用于把页面滑动到最下端 并点击
	def __pull_down_and_next_page(self):
		time.sleep(2)
		self.web.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(self.random_time())
		# 这是找到查看剩下内容的
		self.web.find_element(By.XPATH, '//button[@class="add-more add-more1 index-add-more"]').click()
		# 查看更多内容...
		# 没有更多数据了
		time.sleep(self.random_time())
		return self.web.find_element(By.XPATH, '//button[@class="add-more add-more1 index-add-more"]').text
