# -- coding: utf-8 --**
import WenLanWebSpider.guanChaComment as gc
import WenLanWebSpider.zhiHuComment as zhi
import WenLanWebSpider.weiBoComment as wb
import WenLanWebSpider.guanchaGetUrl as gcg
import WenLanWebSpider.guanchaUpdateUrlComNum as gcun
import WenLanWebSpider.guanchaComDBF as gccDBF
import WenLanWebSpider.guanchaComDBUsual as gccDBU
import WenLanWebSpider.NewWeiBoSpider.outPart as nwbo
import WenLanWebSpider.NewWeiBoSpider.InnerPart as nwip
import WenLanWebSpider.NewWeiBoSpider.InnerPartHot as nwiph
import WenLanWebSpider.NewWeiBoSpider.SaveCommentData2SQL as savec
import WenLanWebSpider.NewWeiBoSpider.WeiBoUserGet as wbug
if __name__ == '__main__':
	# # 知乎获取 注意这里的知乎内容是文章，而不是回答
	# b = zhi.ZhiHuComment('https://zhuanlan.zhihu.com/p/473942764')
	# # test.csv可以替换为指定路径下的csv文件
	# num = b.save_data('test.csv')
	# # 判断是否完成写入，如果没有则返回url 否则返回-1 如果多个url可以用list来装
	#
	# # 后面是观察者网对应的的url
	# c = gc.GuanChaComment('https://www.guancha.cn/internation/2022_05_13_639507.shtml')
	# # test2.csv可以替换为指定路径下的csv文件
	# print(c.get_data())
	# num2 = c.save_data('test2.csv')
	#
	# # 这里填写你的cookie
	# cookie = ''
	# # 这里对应旧版微博的位置
	# url = 'https://weibo.cn/comment/Limi54s17?uid=1298535315&rl=0&page=1'
	# # 开始获取
	# wbo_test3 = wb.weiboComment(url,cookie)
	# # 结果保存
	# wbo_test3.save_data('test3.csv')

	# 数据库读写大堆数据
	# gcg.guanchaGetUrl()

	# 数据修改
	#gcun.guanchaUpdateUrlComNum()

	#新数据插入
	# gccDBF.guanchaComDBF()

	# 判断后插入
	# gccDBU.guanchaComDBF()




	# print(b.get_data())
	# #
	# a = nwip.InnerPart('https://weibo.com/ajax/statuses/show?id=LvhJfAAmw')
	# print(a.get_data())

	a = nwiph.InnerPart('https://weibo.com/ajax/statuses/show?id=Lp2ddrgqm')
	print(a.get_data())
	# https://weibo.com/ajax/statuses/show?id=LuY1rf7Wm

	# 爬取外侧
	# b = nwbo.OutPart()

	#
	# 存储过程
	# b = savec.SaveCommentData2SQL()

	# 更新用户信息
	# a = wbug.WeiBoUserGet()