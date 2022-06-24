import re
import time
import datetime
import requests
from WenLanWebSpider import dataDisposeFunc


# 设计思路
# 这个类可以根据初始传入的url对指定观察者网页面进行查询
# 传递参数为指定页面url
# good 参数对应的是否有成功的获取url 如果没有则返回-1
# 返回的数据以字典列表存储，可以调用get_data()方法获取数据
#

# 这是文字清理的函数，用于对获取的评论进行加工
def text_clean(text):
	# 一个需要删除的词汇表 把里面的词语替换成空字串
	cle_text = ['\n', '【', '】', '】', '【', '\u3000', '\xa0']
	# 下面一个用于清除<img src> <strong> 这样
	re_text = text
	# 这里使用.* 贪婪匹配 .*？只匹配一次 .*全部匹配
	obj2 = re.compile(r'<img.*/>', re.S)
	re_text = obj2.sub('', re_text)
	obj2 = re.compile(r'</strong>', re.S)
	re_text = obj2.sub('', re_text)
	obj2 = re.compile(r'<strong>', re.S)
	re_text = obj2.sub('', re_text)
	obj2 = re.compile(r'</br>', re.S)
	re_text = obj2.sub('', re_text)
	obj2 = re.compile(r'<br>', re.S)
	re_text = obj2.sub('', re_text)
	obj2 = re.compile(r'< br /\>', re.S)
	re_text = obj2.sub('', re_text)

	for i in cle_text:
		re_text = re_text.replace(i, '')
	re_text = re_text.strip()
	return re_text


# 用于处理时间的，用于返回对应的时间
def time_clean(mytime):
	return_time = ''
	if "小时" in mytime:
		# 几小时前
		obj_temp = re.compile(r'\d+')
		this_time = obj_temp.findall(mytime)[0]
		return_time = (datetime.datetime.now() - datetime.timedelta(hours=int(this_time))).strftime('%Y-%m-%d %H')
	elif "分钟" in mytime:
		# 几分钟前
		obj_temp = re.compile(r'\d+')
		this_time = obj_temp.findall(mytime)[0]
		return_time = ((datetime.datetime.now()) - datetime.timedelta(minutes=int(this_time))).strftime('%Y-%m-%d %H')
	elif "秒" in mytime:
		# 几秒前
		return_time = datetime.datetime.now().strftime('%Y-%m-%d %H')
	elif len(mytime) == 16:
		# '2020-10-11 16:55'
		return_time = datetime.datetime.strptime(mytime, '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H')
	elif "昨天" in mytime:
		# '昨天 08:34 '
		temp = (datetime.datetime.now() - datetime.timedelta(hours=24)).strftime('%Y-%m-%d') + ' ' + mytime[3:]
		return_time = datetime.datetime.strptime(temp, '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H')
	elif "前天" in mytime:
		# '前天 08:34 ' 不知道有没有前天，总之先加上
		temp = (datetime.datetime.now() - datetime.timedelta(hours=24)).strftime('%Y-%m-%d') + ' ' + mytime[3:]
		return_time = datetime.datetime.strptime(temp, '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H')
	else:
		# '03-26 13:49'
		return_time = datetime.datetime.strptime('2022-' + mytime, '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H')
	return return_time


# 主类
class GuanChaComment:
	def __init__(self, url):
		self.__dic = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
									'Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31'}
		self.__obj = re.compile(r"DOC_ID=\"(?P<a>.*?)\"", re.S)
		# 对应的url
		self.__my_url = url
		# 设定重复请求次数参数
		self.__try_num = 1
		# 对应的传递好坏
		self.__good = 1
		# 下面是调用
		self.__resp = self.__get_first()
		self.__resp.encoding = 'utf-8'
		# ajax请求编码
		self.__my_codeId = 0
		self.__title = ''
		if self.__good == -1:
			print('长时间无法获取数据，请检查网络连接状态')
		else:
			self.__code_ini()
			# 下面不是完整的url 后面还要加上页码和其他
			print('已获取codeID为:', self.__my_codeId)
			self.__comment_url = 'https://user.guancha.cn/comment/cmt-list.json?codeId=' \
								 + self.__my_codeId \
								 + '&codeType=1&pageNo='
			self.__comment_url_back = '&order=1&ff=www'
			# 下方是获取到的数据数目
			self.__comment_count = 0
			# 所有的数据量
			self.__comment_count_all = 0
			# 获取的数据，以字典处理
			self.__comment_data = []
			# 获取评论
			self.__get_comment()
			# 记录时间
			self.when_get_data = datetime.datetime.now()
			# 有效率 查询数目/总数目
			try:
				self.useful_rate = self.__comment_count / self.__comment_count_all
			except:
				# 除数为0 的情况
				self.useful_rate = 9999

	# 这是获取最外层url内容的函数
	def __get_first(self):
		print('---------开始获取外层url----------')
		# 尝试获取最外层url
		try:
			resp11 = requests.get(self.__my_url, headers=self.__dic)
		except:
			print('第', self.__try_num, '次获取失败，正在重新获取')
			self.__try_num += 1
			if self.__try_num > 10:
				'请检查网络，暂时无法获取'
				self.__good = -1
				return
			else:
				# 尝试重新获取最外层url
				time.sleep(10)
				resp11 = self.__get_first()
		return resp11

	# 这是提取第一层codeID的函数
	def __code_ini(self):
		ti = re.compile(r'<title>(.*?)</title>', re.S)
		self.__title = ti.findall(self.__resp.text)[0]
		print("正在获取标题:", self.__title)
		re1 = self.__obj.finditer(self.__resp.text)
		for i in re1:
			temp = i.group('a')
			self.__my_codeId = temp

	# 获取评论函数get的重写
	def __get_next(self, url):
		try_time = 0
		while try_time < 10:
			try:
				resp11 = requests.get(url, headers=self.__dic)
				time.sleep(2)
				break

			except:
				try_time += 1
				print('第', try_time, '读取失败，重新读取中')
				time.sleep(10)
		if try_time > 10:
			print('10次尝试均失败，结束请求，开始访问下一页')
			return []
		else:
			return resp11.json()

	# 获取评论的函数
	def __get_comment(self):
		print('--------------开始读取评论--------------')
		count = 0
		num = 1

		data = ['test']
		commentNumIsChange = 0
		# 如果为空则结束
		while len(data) != 0:
			# ####
			# if num > 2:
			# 	break
			# ####
			data = self.__get_next(self.__comment_url + str(num) + self.__comment_url_back)
			if commentNumIsChange == 0:
				self.__comment_count_all = data['count']
				commentNumIsChange = 1
			if len(data['items']) == 0:
				print('第', num, '页为空，该网址评论以全部停止')
				break
			for i in data['items']:
				dic = {}
				# 用户id 用于做主键 计划
				dic['com_id'] = i['id']
				dic['user_id'] = i['user_id']
				dic['user_name'] = i['user_nick']
				dic['comment'] = text_clean(i['content'])
				# 下面是时间，时间以 2022-05-12 8 为例，最后一个数字是小时
				dic['time'] = time_clean(i['created_at'])
				count += 1
				self.__comment_data.append(dic)
			print('第', num, '页评论读取完成')
			num += 1
		self.__comment_count = count

	# 这个是对应的数据清洗的函数 可以进行修改

	def get_data(self):
		return self.__comment_data

	# 返回查询到的评论数目
	def get_comment_num(self):
		return self.__comment_count

	# 返回全部的评论数目
	def get_comment_all_num(self):
		return self.__comment_count_all

	# 返回codeID的函数
	def get_code(self):
		return self.__my_codeId

	# 返回查询状态函数
	def get_good(self):
		return self.__good

	# 返回查询的url
	def get_url(self):
		return self.__my_url

	def save_data(self, path):
		if self.get_good() == -1:
			print("数据未完整，将返回url")
			return self.__my_url
		else:
			print("开始写入数据")
			dataDisposeFunc.csv_writer(self.__comment_data, path)
			print("数据成功写入，返回-1")
			return -1
