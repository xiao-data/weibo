'''
@author: xiao-data
模拟登录部分参考https://github.com/moaiweishui/weibo_crawler
'''
import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
import random
class weibo():
    def __init__(self, username, password):
        self.user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKi    t/601.1.46 (KHTML, like Gecko) Version/9.0 '
            'Mobile/13B143 Safari/601.1]',
            'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWeb    Kit/537.36 (KHTML, like Gecko) '
            'Chrome/48.0.2564.23 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWe    bKit/537.36 (KHTML, like Gecko) '
            'Chrome/48.0.2564.23 Mobile Safari/537.36']
        self.headers = {
            'User_Agent': random.choice(self.user_agents),
            'Referer': 'https://passport.weibo.cn/signin/login?entry=mwei    bo&res=wel&wm=3349&r=http%3A%2F%2Fm.weibo.cn%2F',
            'Origin': 'https://passport.weibo.cn',
            'Host': 'passport.weibo.cn'}
        self.post_data = {
            'username': '',
            'password': '',
            'savestate': '1',
            'ec': '0',
            'pagerefer': 'https://passport.weibo.cn/signin/welcome?entry=    mweibo&r=http%3A%2F%2Fm.weibo.cn%2F&wm=3349&vt=4',
            'entry': 'mweibo'}
        self.login_url = 'https://passport.weibo.cn/sso/login'
        self.username = username
        self.password = password
        self.session = requests.session()

    def log_in(self):
        self.post_data['username'] = self.username
        self.post_data['password'] = self.password
        response = self.session.post(self.login_url, data=self.post_data, headers=self.headers)
        if response.status_code == 200:
            print ('-'*40 + '\n')
            print ("模拟登陆成功,当前登陆账号为：" + self.username)
        else:
            raise Exception("模拟登陆失败")
    def get_page(self, url):
        page = self.session.get(url)
        return page.content

    def get_homepage(self, user_id):
        baseURL = 'https://weibo.cn/u/' + user_id
        home_page = BeautifulSoup(self.get_page(baseURL), 'lxml').prettify()
        return home_page

    def get_pages(self, user_id, nickname, page):
        print ('\n' + '-'*40 + '\n')
        print ('开始获取用户%s的前%d页微博内容...\n' % (nickname, page))
        dir_path = './output/' + nickname + '/'
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
            print ('Create fold: "' + dir_path + '" succeed.')
        for p in [i+1 for i in range(page)]:
            filename = dir_path + nickname + str(p) +'.txt'
            with open(filename, 'w') as f:
                base_url = 'https://weibo.cn/u/' + user_id
                url = base_url + '?filter=1&page=' + str(p)
                time.sleep(2)
                info = self.get_page(url)
                if info:
                    soup = BeautifulSoup(info, 'lxml')
                    print ("Get page succeed:",)
                    print (url, )
                    f.write(soup.prettify())
                    print ('\n获取内容完成，文件保存于：' + filename + '\n')    
    def get_contents(self, nickname, page):
        weibos = []
        for p in [i+1 for i in range(page)]:
            fn = './output/'+nickname+'/'+nickname + str(p)+'.txt'
            with open(fn, 'r') as fr:
                soup = BeautifulSoup(fr, 'lxml')
                microb = soup.find_all('div',{'class':'c'},id=True)
                for mb in microb:
                    weib = dict()
                    mb = str(mb)
                    grouped = re.search('<span class="ctt">(.*?)</span>.*赞\[(.*?)\].*转发\[(.*?)\].*评论\[(.*?)\].*<span class="ct">(.*?)</span>', mb, re.S)
                    bowen = grouped.group(1).strip()
                    attitude = int(grouped.group(2).strip())
                    repost = int(grouped.group(3).strip())
                    comment = int(grouped.group(4).strip())
                    date = grouped.group(5).strip()
                    tmp = re.search('<a href="/comment/(.*?)">', bowen)
                    if tmp != None:
                        url = 'https://weibo.cn/comment/'+tmp.group(1)
                        time.sleep(2)
                        info = self.get_page(url)
                        if info:
                            soup = BeautifulSoup(info, 'lxml')
                            bowen = soup.find('span',{'class':'ctt'})
                            bowen = str(bowen)[19:-7]
                    bowen = re.sub('<a href=\".*?>|</a>|\ |\n|;', '', bowen)
                    weib['bowen'] = bowen
                    weib['attitude'] = attitude
                    weib['repost'] = repost
                    weib['comment'] = comment
                    if date[4] == '-':
                        weib['date'] = date[:16]
                    else:
                        date = date[:12]
                        date = re.sub('月', '-', date)
                        date = re.sub('日', '', date)
                        weib['date'] = '2017-'+date
                    weibos.append(weib)
        fn = './output/'+nickname+'/'+nickname+'.json'    
        with open(fn, 'w') as fw:
            json.dump(weibos, fw , ensure_ascii=False)
            print('%s的微博内容解析完成，保存于%s\n'%(nickname, fn))
if __name__ == '__main__':
    username = '' #用户名
    password = '' #密码
    weibo_crawler = weibo(username, password)
    weibo_crawler.log_in()
    page = 10
    usr_id = '1863847262'
    weibo_crawler.get_homepage(usr_id)
    weibo_crawler.get_pages(usr_id, '吴京', page)
    weibo_crawler.get_contents('吴京', page)
