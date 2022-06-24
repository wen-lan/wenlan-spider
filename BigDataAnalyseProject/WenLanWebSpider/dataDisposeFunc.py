import csv
# 用于编写一些处理dic的函数
def csv_writer(lst_dic, path):
	# header = []
	# for i in lst_dic[0].keys():  # 把字典的键取出来
	# 	header.append(i)
	# print(header)
	data = []
	for dic in lst_dic:
		temp = []
		for i in dic.values():
			temp.append(i)
		data.append(temp)
	# 以添加的方式继续写入文件
	f = open(path, mode='a', encoding='GB18030', newline='')  # 一定记得newline
	csvwriter = csv.writer(f)
	csvwriter.writerows(data)
	f.close()
# for data in sorted()
# header = a  # 把列名给提取出来，用列表形式呈现
# with open('成绩更新.csv', 'a', newline='', encoding='utf-8') as f:
# 	writer = csv.DictWriter(f, fieldnames=header)  # 提前预览列名，当下面代码写入数据时，会将其一一对应。
# 	writer.writeheader()  # 写入列名
# 	writer.writerows()  # 写入数据
# print("数据已经写入成功！！！")



