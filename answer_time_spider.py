# coding: utf-8
# 2020/03 by florakl

from util import url_get


def question_info_get(qid):
    q_url = f'https://www.zhihu.com/api/v4/questions/{qid}?include=answer_count'
    q_res = url_get(q_url)
    if q_res:
        total = q_res['answer_count']  # 回答数
        title = q_res['title']  # 问题标题
        created_time = q_res['created']  # 创建时间
        return total, title, created_time


def answer_time_get(qid, interval, offset, q_time):
    voteup = []
    ans_time = []
    ans_url = f'https://www.zhihu.com/api/v4/questions/{qid}/answers?include=content,comment_count,voteup_count&limit={interval}&offset={offset}&sort_by=default'
    ans_res = url_get(ans_url)
    answers = ans_res['data']
    for answer in answers:
        voteup.append(answer['voteup_count'])
        ans_time.append(answer['created_time'])
        # ans_time.append(answer['created_time'] - q_time)
    return voteup, ans_time


def data_get(qid, number):
    total, title, created_time = question_info_get(qid)
    interval = 20
    offset = 0
    voteup = []
    ans_time = []
    while offset < total:
        print(f'正在爬取第{offset}-{offset + interval - 1}个回答')
        v, a = answer_time_get(qid, interval, offset, created_time)
        # 单次爬取回答个数上限为20
        voteup += v
        ans_time += a
        offset += interval
    print(f'第{number}个问题爬取成功，id={qid}，标题=“{title}”，总回答数={total}')
    return voteup, ans_time, title


if __name__ == '__main__':
    # qids = [314644210, 30265988, 26933347, 33220674, 264958421, 31524027]
    qids = [30265988]
    number = 1
    for qid in qids:
        voteup, ans_time, title = data_get(qid, number)
        number += 1
        filename = 'answer_time.txt'
        with open(filename, 'a') as f:
            f.write(str(qid) + '\n')
            f.write(title + '\n')
            for item in ans_time:
                f.write(str(item) + ',')
            f.write('\n')
            for item in voteup:
                f.write(str(item) + ',')
            f.write('\n')
            print('数据保存成功')
