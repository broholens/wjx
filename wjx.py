"""
刷问卷星
"""
import re
import os
import time
import random
import urllib.request
from itertools import combinations, chain
import requests
import xlwt
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
                'referer': f'https://www.wjx.cn/m/{self.q_id}.aspx'
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
        total_count = resp.text.split('jidx')[-1].split('&')[0].strip('=')
        print('已答卷数: ', total_count)
        self.s.close()


def create_model(q_id):
    """
    item type:
        1: 填空　非必填
        3: 单选　必填
        4: 多选　必填
        6: 单选　符合情况
        9: 填空　必填
    """
    if os.path.exists(f'./tmps/{q_id}.xlsx'):
        return
    html = requests.get(f'https://www.wjx.cn/m/{q_id}.aspx').text     
    # wjx = WJX(q_id)
    # wjx.set_wjx_headers()
    # html = wjx.s.get(f'https://www.wjx.cn/m/{q_id}.aspx').text
    # wjx.s.close()
    tree = etree.HTML(html)
    wb, sheet = new_excel()
    row = 1
    for q in tree.xpath('//div[@data-role="fieldcontain"]'):
        item_type = q.xpath('./@type')[0]
        item_numbers = q.xpath('.//input/@id')
        if item_type == '3':
            count = len(q.xpath('.//a'))
            sheet.write(row, 0, q.xpath('./@topic')[0])
            sheet.write(row, 1, iter_to_str(range(1, count+1)))
            row += 1
        elif item_type == '4':
            count = len(q.xpath('.//a'))
            if count >= 4:
                options = combine_chain(range(1, count+1), range(2, 5))
            else:
                options = combine_chain(range(1, count+1), range(1, 4))
            sheet.write(row, 0, q.xpath('./@topic')[0])
            sheet.write(row, 1, ','.join(options))
            row += 1
        elif item_type == '6':
            count = len(q.xpath('./table/colgroup/col'))
            for i in q.xpath('.//tr[@tp="d"]/@id'):    
                sheet.write(row, 0, i.lstrip('drv')) 
                sheet.write(row, 1, iter_to_str(range(1, count+1)))
                row += 1
        elif item_type == '9':
            sheet.write(row, 0, item_numbers[0].split('_')[0].lstrip('q'))
            row += 1
        else:
            raise ValueError('unknown item type')
        wb.save(f'./tmps/{q_id}.xlsx')


def iter_to_str(int_iter, sep=','):
    return f'{sep}'.join([str(i) for i in int_iter])


def combine_chain(lst1, lst2):
    for i in lst2:
        for j in combinations(lst1, i):
            yield iter_to_str(j, '|')


def new_excel():
    wb = xlwt.Workbook()
    sheet = wb.add_sheet('sheet', cell_overwrite_ok=True)
    columns = tuple('题号 选项 占比'.split())
    for i in range(len(columns)):
        sheet.write(0, i, columns[i])
    return wb, sheet
# 13 14没有则是-3
# 15多选 3|5
# 28 29 符合程度
# '1$厦门}2$1}3$1}4$4}5$3}6$3}7$1}8$1}9$5}10$2}11$2}12$2}13$-3}14$-3}15$3|5}16$4}17$3}18$5}19$2}20$2}21$4}22$2}23$2}24$9}25$2}26$4}27$4}28$1!5,2!4,3!5,4!4,5!6,6!6,7!5,8!5,9!5,10!6,11!5,12!6,13!5,14!5,15!6}29$1!5,2!4,3!6,4!6,5!6,6!5,7!6,8!6,9!5,10!6,11!6,12!5,13!6,14!6,15!5,16!6,17!6,18!6,19!6,20!6,21!5,22!5,23!6,24!6'
if __name__ == '__main__':
    # data1 = '1$西安}2$3}3$1}4$4}5$3}6$3}7$1}8$1}9$5}10$2}11$2}12$2}13$-3}14$-3}15$3|5}16$4}17$3}18$5}19$2}20$2}21$4}22$2}23$2}24$9}25$2}26$4}27$4}28$1!5,2!4,3!5,4!2,5!6,6!3,7!5,8!5,9!5,10!6,11!5,12!6,13!5,14!5,15!5}29$1!5,2!4,3!6,4!6,5!6,6!5,7!6,8!6,9!5,10!6,11!6,12!5,13!6,14!6,15!5,16!6,17!6,18!6,19!6,20!6,21!5,22!5,23!6,24!6'
    # data2 = '1$咸阳}2$4}3$1}4$3}5$2}6$2}7$2}8$1}9$3}10$1}11$1}12$1}13$-3}14$-2}15$3}16$4}17$3}18$4}19$2}20$2}21$4}22$2}23$2}24$9}25$2}26$4}27$4}28$1!5,2!4,3!6,4!5,5!6,6!6,7!3,8!5,9!5,10!3,11!5,12!6,13!5,14!4,15!6}29$1!5,2!4,3!6,4!6,5!6,6!5,7!6,8!6,9!5,10!5,11!6,12!5,13!6,14!3,15!5,16!6,17!6,18!6,19!6,20!5,21!5,22!5,23!5,24!6'
    # data3 = '1$宝鸡}2$3}3$2}4$3}5$2}6$4}7$1}8$1}9$3}10$2}11$1}12$2}13$-2}14$-3}15$4}16$}17$3}18$4}19$2}20$2}21$4}22$2}23$2}24$9}25$2}26$4}27$4}28$1!5,2!4,3!4,4!6,5!4,6!6,7!5,8!5,9!5,10!6,11!5,12!6,13!4,14!5,15!5}29$1!5,2!4,3!6,4!6,5!6,6!5,7!6,8!6,9!5,10!6,11!6,12!5,13!6,14!6,15!5,16!4,17!6,18!6,19!6,20!6,21!5,22!5,23!6,24!5'
    # data4 = '1$咸阳}2$2}3$1}4$3}5$1}6$5}7$2}8$1}9$3}10$2}11$1}12$2}13$-3}14$-3}15$1}16$4}17$3}18$4}19$2}20$2}21$4}22$2}23$2}24$9}25$2}26$4}27$4}28$1!5,2!4,3!3,4!6,5!5,6!6,7!5,8!5,9!5,10!6,11!5,12!6,13!5,14!5,15!6}29$1!5,2!4,3!6,4!6,5!6,6!5,7!6,8!6,9!5,10!6,11!6,12!5,13!6,14!6,15!5,16!6,17!6,18!6,19!6,20!6,21!5,22!5,23!6,24!6'
    # data5 = '1$渭南}2$4}3$2}4$3}5$4}6$4}7$2}8$5}9$5}10$2}11$1}12$2}13$-2}14$-3}15$1}16$4}17$3}18$4}19$2}20$2}21$4}22$2}23$2}24$9}25$2}26$4}27$4}28$1!5,2!4,3!4,4!6,5!4,6!5,7!5,8!5,9!5,10!6,11!5,12!6,13!5,14!5,15!6}29$1!5,2!4,3!6,4!6,5!6,6!5,7!6,8!6,9!5,10!6,11!6,12!5,13!6,14!6,15!5,16!6,17!6,18!6,19!6,20!6,21!5,22!5,23!6,24!6'
    # data6 = '1$西安}2$5}3$1}4$4}5$1}6$3}7$2}8$1}9$3}10$2}11$2}12$2}13$-3}14$-3}15$4}16$4}17$3}18$4}19$2}20$2}21$4}22$2}23$2}24$9}25$2}26$4}27$4}28$1!5,2!4,3!3,4!6,5!2,6!6,7!5,8!5,9!5,10!6,11!5,12!6,13!5,14!5,15!6}29$1!5,2!4,3!6,4!6,5!6,6!5,7!6,8!6,9!5,10!6,11!6,12!5,13!6,14!6,15!5,16!6,17!6,18!6,19!6,20!6,21!5,22!5,23!6,24!6'
    
    # for data in [data1, data2, data3, data4, data5, data6]:
    #     WJX('20020146').post_data(data)
    #     time.sleep(3 * 60)

    # urllib.request.urlretrieve('https://www.wjx.cn/m/20103155.aspx', filename='11.html')
    create_model('20103155')