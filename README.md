# wenlan-spider
自用爬虫包，能爬取微博、知乎和观察者网。大数据案例分析课程用的，只用于课程的学习与研究。
# 微博
```import WenLanWebSpider.NewWeiBoSpider.InnerPart as nwip
a = nwiph.InnerPart('https://weibo.com/ajax/statuses/show?id=Lp2ddrgqm')
print(a.get_data())```

把id改了就好，哪个微博id就改哪个，可能有数目对不上，要不就是精选要么就是被夹了。精选用InnerPartHot那里面的，记得加cookie不然没法跑

# 知乎

知乎用到了selenium，所以需要装谷歌内核，chromedriver.exe下载后添加到环境变量，然吼cmd输入`chrome.exe --remote-debugging-port=9222 --user-data-dir="D:\chromeselenium"
`就可以接着跑了，后面的引号里面的是随意的路径呀。

这个是知乎文章下面的评论，**不是问答的**

```import WenLanWebSpider.zhiHuComment as zhi
# 知乎获取 注意这里的知乎内容是文章，而不是回答
b = zhi.ZhiHuComment('https://zhuanlan.zhihu.com/p/473942764')
# test.csv可以替换为指定路径下的csv文件
num = b.save_data('test.csv')
# 判断是否完成写入，如果没有则返回url 否则返回-1 如果多个url可以用list来装```
