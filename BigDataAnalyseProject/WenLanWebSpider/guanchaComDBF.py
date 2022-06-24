import WenLanWebSpider.guanChaComment as gcc
import WenLanWebSpider.databaseInput as db

# 初次初始化
# 初次根据全部数据填充表格，这个是评论数据库是空的情况下的
# 先查询所有的评论信息，然后分新闻id依次写入
# 一股脑的先写入就行了
# 另一个方式是查询哪些数据百分比比较低，对比较低的进行重新查询
# 如果新闻表有而聚合后的评论表没有 使用左连接，然后ifnull填充  sql里面 5/0 返回是null 很好
class guanchaComDBF:
	def __init__(self):
		self.my_db = db.dataBaseInput('127.0.0.1', 'root', '123456', 'bigdata', 3306)
		mysql = "select id,n_url from newsdata"
		self.clue = self.my_db.sql_execute(mysql,[])
		# 测试一条数据
		for i in self.clue:
			self.get_one_data(i)
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
