# -- coding: utf-8 --**
import pymysql
# 这是相关数据库操作


class dataBaseInput:
	def __init__(self, host: object, user: object, password: object, database: object, port: object) -> object:
		# conn = pymysql.connect(host ='127.0.0.1',user='root',password='123456',database='bigdata',port=3306)
		self.conn = pymysql.connect(host=host, user=user, password=password, database=database, port=port)
		self.cursor = self.conn.cursor()

	# 插入
	# 第一个是链接coon
	# 第二个是创建的游标
	# 第三个是要插入的表名
	# 第四个是键值对字典
	def insert_sql(self, tablename, toinserts_values):
		keys = ", ".join(toinserts_values.keys())
		qmark = ", ".join(["%s"] * len(toinserts_values))
		sql_insert = "insert into %s (%s) values (%s)" % (tablename, keys, qmark)
		try:
			self.cursor.execute(sql_insert, list(toinserts_values.values()))
			self.conn.commit()
		except Exception as e:
			print(e)
			self.conn.rollback()
			print("插入失败")

	# 查询sql,传sql语句 和 execute多个的一样 lst需要是list 或者单个
	def sql_execute(self, sql, lst):
		self.cursor.execute(sql, lst)
		# b == () 这样判断是否有返回结果
		return self.cursor.fetchall()


	def close(self):
		self.cursor.close()
		self.conn.close()
