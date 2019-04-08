'''
@author: xiao-data
'''
from weibo import weibo
import json
import pandas as pd
def load_json(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
        return data
username = ''#用户名
password = ''#密码
page = 10
weibo_crawler = weibo(username, password)
weibo_crawler.log_in()
users = load_json('user.json')
# print (users)
for user in users:
    usr_id = user['user_id']
    usr_name = user['user_name']
    weibo_crawler.get_pages(usr_id, usr_name, page)
    weibo_crawler.get_contents(usr_name, page)
    df = pd.read_json('./output/'+usr_name+'/'+usr_name+'.json')
    df.to_csv('./output/weibo/'+usr_name+'.csv',index = False)
print('done')
