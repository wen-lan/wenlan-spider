import WenLanWebSpider.guanChaComment as gcc
import WenLanWebSpider.databaseInput as db

# 更新爬虫， 对数据进行更新
# 调用这个，会对已经存在数据的数据库内容进行更新 ，这个比那个初始化多一个查询，更消耗资源
# 如果获取的评论/总的评论 小于 add_rate 那么会对这些数据进行爬取



class guanchaComDBF:
	def __init__(self):
		# 设置的获取评论 与总评论的比例 低于这个数字 那么就会开始爬取
		self.add_rate = 0.8
		self.my_db = db.dataBaseInput('127.0.0.1', 'root', '123456', 'bigdata', 3306)
		# 测试一条数据
		# 查询对应的实际数目， 返回值是 新闻id 新闻评论数目， 爬取评论数目 ，爬取数目与新闻评论数目比率（这个用来查询的）,对应的url
		self.sql_compare_juzi = '''select id,n_num,ifnull(c.cn,0)as cn, ifnull(cn/n_num,0) as rate,n_url from 
		newsdata left outer join(select t_id,count(1) as cn from comdata group by t_id)  
		as c on t_id = id;'''
		self.sql_compare = self.my_db.sql_execute(self.sql_compare_juzi,[])
		self.aim_url =[]
		self.get_id_url()
		print(self.aim_url)
		num = 0
		for clue in self.aim_url:
			# if num > 5:
			# 	break
			self.get_one_data(clue)
			num +=1
		self.my_db.close()

	# 根据clue 返回的线索来进行查询 设想是对一条返回结果 开始爬虫
	def get_one_data(self, oneclue):
		id = oneclue[0]
		url = oneclue[1]
		print('开始读取新闻 id:',id)
		gccT = gcc.GuanChaComment(url)
		data = gccT.get_data()
		for i in data:
			dic = {'t_id': id, 'u_id': i['user_id'], 'u_name': i['user_name'], 'com_id': i['com_id'],
				   'com_content': i['comment'], 'com_time': i['time'] + ':00:00'}
			self.my_db.insert_sql('comdata', dic)


	def get_id_url(self):
		for clue in self.sql_compare:
			if clue[3] > 0.8:
				continue
			else:
				print(clue[0],'的获取率',clue[3],'低于设定值',self.add_rate)
				self.aim_url.append ((clue[0],clue[4]))