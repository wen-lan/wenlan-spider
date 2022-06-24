import time

import requests
from lxml import etree
import re
import csv
import datetime

# 不太好用的微博爬虫，暂时没法让他很好用
# 用于处理时间的，用于返回对应的时间
def time_clean(mytime):
	# 03月06日 09:54 来自网页
	# 今天 13:20 来自来自河北
	# 8分钟前 来自来自湖南
	return_time = ''
	if "时" in mytime:
		# 几小时前
		obj_temp = re.compile(r'\d+')
		this_time = obj_temp.findall(mytime)[0]
		return_time = (datetime.datetime.now() - datetime.timedelta(hours=int(this_time))).strftime('%Y-%m-%d')
	elif "分钟" in mytime:
		# 几分钟前
		obj_temp = re.compile(r'\d+')
		this_time = obj_temp.findall(mytime)[0]
		return_time = ((datetime.datetime.now()) - datetime.timedelta(minutes=int(this_time))).strftime('%Y-%m-%d')
	elif "秒" in mytime:
		# 几秒前
		return_time = datetime.datetime.now().strftime('%Y-%m-%d')
	elif len(mytime) == len('03月06日') and "月" in mytime:
		temp = '2022-'+mytime.replace('月','-').replace('日','')
		return_time = temp
	elif "今天" in mytime:
		return_time = (datetime.datetime.now()).strftime('%Y-%m-%d')
	elif "昨天" in mytime:
		return_time = ((datetime.datetime.now()) - datetime.timedelta(hours=int(24))).strftime('%Y-%m-%d')
	else:
		return -1
	return return_time

class weiboComment():
	def __init__(self,url,cookie):
		# https://weibo.cn/comment/Limi54s17?uid=1298535315&rl=0&page=1
		self.__cookie = cookie
		self.__header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
								'Chrome/99.0.4844.51 Safari/537.36 ' \
								'Edg/99.0.1150.30 ',
				  'cookie': self.__cookie
				  }
		self.__url = url.split('page')[0]
		self.__data = []
		self.__page = 1
		self.__comment_all =0
		self.__start()
		print(self.__comment_all)
		self.__aim_page = self.__comment_all//10
		self.__num = 1
		self.__time_data = []
		print(self.__aim_page)
		while self.__num < self.__aim_page:
			time.sleep(0.5)
			self.page_get()
			self.__num+=1




	# 获取第几页的内容
	def __start(self):
		num = 0
		print('开始读取', '正在导航')
		while num < 3:
			# 就按照每页十个来设定爬取目标吧
			try:
				resp=requests.get(self.__url+'page='+'1', headers=self.__header)
				resp.encoding='utf-8'
				# 使用正则表达式查找
				obj = re.compile(r";评论.*?\[(\d+)\]", re.S)
				temp = obj.findall(resp.text)
				self.__comment_all = int(temp[0])
				return 1
			except:
				num +=1
				print("获取失败正在重新尝试")
		return -1

		# 每页读取
	def page_get(self):
		num = 0
		while num < 3:
			# 就按照每页十个来设定爬取目标吧
			try:
				print('开始获取第',self.__num,'页')
				print(self.__url+'page='+str(self.__num))
				resp = requests.get(self.__url+'page='+str(self.__num), headers=self.__header)

				resp.encoding = 'utf-8'
				htmlEX = etree.HTML(resp.content)
				# 文字内容
				temp_html_data = htmlEX.xpath('//*[@class="c"]/span[@class="ctt"]')
				temp_time = htmlEX.xpath('//*[@class="c"]/span[@class="ct"]/text()')

				for temp in temp_time:
					te = temp.split()[0]
					self.__time_data.append(time_clean(te))
				for temp in temp_html_data:
					# 注意 这里使用的是./ 代表从上一层文件往下走
					b = temp.xpath('./text()')
					text = ""
					for iq in b:
						text = text + iq.strip()
					if "//" in text:
						text = text.split("//")[0]
					temp_text =text.replace("回复:",'').strip()
					print(temp_text)
					self.__data.append(temp_text)

				print('-----------第',self.__num,'页获取完成-----------')
				return 1
			except:
				num += 1
				print("-------------获取失败正在重新尝试----------")
		return -1


	def save_data(self,path):
		print('--------------------开始写入数据--------------------')
		f = open(path, mode='a', encoding='GB18030', newline='')  # 一定记得newline
		csvwriter = csv.writer(f)
		for i in range(len(self.__data)):
			csvwriter.writerow([self.__data[i],self.__time_data[i]])
		f.close()