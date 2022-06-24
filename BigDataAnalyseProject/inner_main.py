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
import WenLanWebSpider.NewWeiBoSpider.SaveCommentData2SQL as savec
import WenLanWebSpider.NewWeiBoSpider.WeiBoUserGet as wbug
if __name__ =='__main__':
	# 查询并获取数据
	b = savec.SaveCommentData2SQL()