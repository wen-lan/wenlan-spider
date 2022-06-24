import time
import datetime
import re
from WenLanWebSpider import dataDisposeFunc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# 知乎爬虫 需要接管
# 将google浏览器添加至环境路径然后启动cmd在命令行输入以下内容
# chrome.exe --remote-debugging-port=9222 --user-data-dir="D:\chromeselenium"
# 会打开一个网页 在这个网页可以实现登录知乎 然后挂起然后运行下面的代码 令selenium接管浏览器


def time_clean(mytime):
    return_time = ''
    if "小时" in mytime:
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
    elif len(mytime) == len('03-07'):
        temp = '2022-'+mytime
        return_time = temp
    else:
        return_time = mytime
    return return_time


class ZhiHuComment:
    def __init__(self, url):
        self.__url = url
        self.__chrome_options = Options()
        self.__chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")  # 前面设置的端口号
        self.__web = webdriver.Chrome(options=self.__chrome_options)  # executable执行webdriver驱动的文件
        self.__page_num = 1
        self.__data = []
        self.__comment_num=0
        # 总评论数目
        self.comment_page_num = 0
        self.actual_page_num = 1
        self.__title = 0
        self.__get_start()
        self.__save_path = ''

    def __get_start(self):
        print('目标定向中')
        self.__web.get(self.__url)
        # 按照时间排序
        self.__title = self.__web.find_element(By.XPATH,'//h1[@class="Post-Title"]').text
        print("正在爬取标题：",self.__title)
        self.__pull_down()
        time.sleep(5)
        comment_num = self.__web.find_element(By.XPATH,'//h2[@class="CommentTopbar-title"]').text
        obj_temp = re.compile(r'\d+')
        self.comment_page_num =  obj_temp.findall(comment_num)[0]

        # self.__web.find_element(By.XPATH,'/html/body/div[1]/div/main/div/div[2]/div[3]/div/div[1]/div[2]/button').click()
        # 下面是通过js强制执行
        comfirmdel = self.__web.find_element(By.XPATH, '//div[@class="Topbar-options"]/button[@class="Button Button--plain Button--withIcon Button--withLabel"]')
        self.__web.execute_script("arguments[0].click();", comfirmdel)
        time.sleep(3)
        num = 1
        print('开始读取第1页')
        while num != -1:
            self.__get_comment_data()
            num = self.__change_page()
            if num == -1:
                break
            self.__pull_down()
            self.actual_page_num +=1
            time.sleep(3)


    # 该函数用于把页面滑动到最下端
    def __pull_down(self):
        self.__web.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # 用于翻页的函数，如果无法翻页返回-1，认为到尽头了，如果翻页成功返回1
    def __change_page(self):
        num = 0
        # 如果三次都没有翻页成功，可以认为没有下一页，结束翻页
        while num < 3:
            try:
                pages_button = self.__web.find_element(By.XPATH,
                                                       '//button[@class="Button PaginationButton PaginationButton-next Button--plain"]')
                self.__web.execute_script("arguments[0].click();", pages_button)
                print('翻页成功,到达', self.actual_page_num+1, "页")
                return 1
            except:
                if float(self.__comment_num)/float(self.comment_page_num)<0.75:
                    time.sleep(2)
                    print('失败翻页')
                    num += 1
                else:
                    num += 1
                    pass
        print("当前采集结束，请根据good结果判断采集效果")
        return -1

    # 获取评论函数 当到达新的一页就可以调用此方法
    def __get_comment_data(self):
        comment = self.__web.find_elements(By.XPATH,'//ul[@class="NestComment"]')
        for i in comment:
            dic = {}
            # 评论
            com = i.find_element(By.XPATH,'./li/div/div/div[2]/div/div')
            # 名称
            nam = i.find_element(By.XPATH,'./li/div/div/div[1]/span[2]/a')
            # 日期
            tim = i.find_element(By.XPATH,'./li/div/div/div[1]/span[@class="CommentItemV2-time"]')
            dic['user_id'] = nam.text
            dic['user_comment'] = com.text
            dic['comment_time'] = time_clean(tim.text)
            self.__data.append(dic)
            self.__comment_num+=1
        time.sleep(1)
        return

    # 获取数据
    def get_data(self):
        return self.__data

    # 总评论区评论数目
    def get_page_comment(self):
        return self.comment_page_num

    # 实际的页数
    def get_page_actual(self):
        return self.actual_page_num

    def get_title(self):
        return self.__title

    # 判断此页如何 如果70%页面未获取则重试 错误返回-1
    def get_good(self):
        if float(self.__comment_num)/float(self.comment_page_num) <= 0.7:
            return -1
        else:
            return 1

    # 对应的文件保存的path
    def set_save_path(self,path):
        self.__save_path = path

    # 文件存储过程
    def save_data(self, path):
        if self.get_good() == -1:
            print("数据未完整，将返回url")
            return self.__url
        else:
            print("开始写入数据")
            dataDisposeFunc.csv_writer(self.__data, path)
            print("数据成功写入，返回-1")
            return -1

        # time.sleep(20)
        # 可以选择手动登录或者是自动化，我这里登录过就直接登陆了
        # info = self.browser.get_cookies()  # 获取cookies
        # print(info)
    # with open(r"..\download_txt\info.json", 'w', encoding='utf-8') as f:


