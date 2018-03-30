"""
刷问卷星
"""
import re
import time
import random
import requests
from lxml import etree


class WJX:

    # 查找rn参数
    rndum_ptn = re.compile('var rndnum=(.*?);')

    def __init__(self, q_id):
        self.q_id = q_id
        self.s = requests.Session()
        self.set_wjx_headers()

    def set_wjx_headers(self, times=1):
        """设置请求头 get和post不一样 默认get"""
        if times == 1:
            self.s.headers = {}
            self.s.headers.update({
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'cache-control': 'max-age=0',
                'upgrade-insecure-requests': '1'
            })
        if times == 2:
            self.s.headers.pop('cache-control')
            self.s.headers.pop('upgrade-insecure-requests')
            self.s.headers.update({
                'x-requested-with': 'XMLHttpRequest',
                'accept': 'text/plain, */*; q=0.01',
                'origin': 'https://www.wjx.cn',
                'referer': 'https://www.wjx.cn/m/20103155.aspx'
            })

    def get_post_params(self):
        """通过get问卷星页面　获取post所需参数"""
        resp = self.s.get(f'https://www.wjx.cn/m/{self.q_id}.aspx')
        tree = etree.HTML(resp.text)
        start_time = tree.xpath('//input[@id="starttime"]/@value')[0]
        rn = self.rndum_ptn.findall(resp.text)[0].strip('"')
        t = int(time.time() * 1000)
        return start_time, rn, t
    
    def post_data(self, data):
        """刷"""
        start_time, rn, t = self.get_post_params()
        post_url = f'https://www.wjx.cn/joinnew/processjq.ashx?curid={self.q_id}&starttime={start_time}&source=directphone&submitttype=1&rn={rn}&t={t}'
        self.set_wjx_headers(2)
        # 作答时间
        time.sleep(60)
        resp = self.s.post(post_url, data={'submitdata': data})
        total_count = resp.text.split('jidx')[-1].split('&')[0]
        print('已答卷数: ', total_count)
        self.s.close()
# 13 14没有则是-3
# 15多选 3|5
# 28 29 符合程度
# '1$厦门}2$1}3$1}4$4}5$3}6$3}7$1}8$1}9$5}10$2}11$2}12$2}13$-3}14$-3}15$3|5}16$4}17$3}18$5}19$2}20$2}21$4}22$2}23$2}24$9}25$2}26$4}27$4}28$1!5,2!4,3!5,4!4,5!6,6!6,7!5,8!5,9!5,10!6,11!5,12!6,13!5,14!5,15!6}29$1!5,2!4,3!6,4!6,5!6,6!5,7!6,8!6,9!5,10!6,11!6,12!5,13!6,14!6,15!5,16!6,17!6,18!6,19!6,20!6,21!5,22!5,23!6,24!6'
if __name__ == '__main__':
    data = '1$厦门}2$1}3$1}4$4}5$3}6$3}7$1}8$1}9$5}10$2}11$2}12$2}13$-3}14$-3}15$3|5}16$4}17$3}18$5}19$2}20$2}21$4}22$2}23$2}24$9}25$2}26$4}27$4}28$1!5,2!4,3!5,4!4,5!6,6!6,7!5,8!5,9!5,10!6,11!5,12!6,13!5,14!5,15!6}29$1!5,2!4,3!6,4!6,5!6,6!5,7!6,8!6,9!5,10!6,11!6,12!5,13!6,14!6,15!5,16!6,17!6,18!6,19!6,20!6,21!5,22!5,23!6,24!6'
    for _ in range(1):
        WJX('20103155').post_data(data)