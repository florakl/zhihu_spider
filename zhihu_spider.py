# coding: utf-8
# 2020/03 by florakl

import json
from datetime import datetime
from util import url_get


def qid_get(interval, offset):
    # 知乎根话题下的精华问题
    tid = 19776749
    url = f'https://www.zhihu.com/api/v4/topics/{tid}/feeds/essence?limit={interval}&offset={offset}'
    res = url_get(url)
    qids = []
    if res:
        for question in res['data']:
            try:
                qid = question['target']['question']['id']
                qids.append(qid)
            except KeyError:
                print('qid无法读取，跳过该问题')
    return qids


def question_info_get(qid):
    # 爬取问题相关信息
    q_url = f'https://www.zhihu.com/api/v4/questions/{qid}?include=answer_count,comment_count,follower_count,excerpt,topics'
    q_res = url_get(q_url)
    if q_res:
        answer_count = q_res['answer_count']
        if answer_count < 20:
            print(f'总回答数为{answer_count}，小于20，跳过该问题')
            return None
        q_info = {}
        q_info['qid'] = qid
        q_info['answer_count'] = answer_count  # 回答数
        q_info['title'] = q_res['title']  # 问题标题
        excerpt = q_res['excerpt']
        if not excerpt:
            excerpt = ' '
        q_info['q_content'] = excerpt  # 问题内容
        topics = []
        for topic in q_res['topics']:
            topics.append(topic['name'])
        q_info['topics'] = topics  # 问题标签
        q_info['comment_count'] = q_res['comment_count']  # 评论数
        q_info['follower_count'] = q_res['follower_count']  # 关注数
        q_info['created_time'] = q_res['created']  # 创建时间
        q_info['updated_time'] = q_res['updated_time']  # 更新时间
        q_info['crawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 爬取时间

        return q_info


def answer_info_get(qid, interval, offset):
    # 爬取回答相关信息
    ans_url = f'https://www.zhihu.com/api/v4/questions/{qid}/answers?include=content,comment_count,voteup_count&limit={interval}&offset={offset}&sort_by=default'
    ans_res = url_get(ans_url)
    if ans_res:
        ans_infos = []
        answers = ans_res['data']
        for answer in answers:
            ans_info = {}
            name = answer['author']['name']
            un = answer['author']['url_token']
            if name == '「已注销」' or name == '匿名用户' or name == '知乎用户':
                ans_info['author'] = 'NoName'
                ans_info['author_follower_count'] = 0
                ans_info['author_voteup_count'] = 0
            elif un:
                ans_info['author'] = un  # 答主用户名
                user_url = f"https://www.zhihu.com/api/v4/members/{un}?include=follower_count,voteup_count"
                user = url_get(user_url)
                if user:
                    ans_info['author_follower_count'] = user['follower_count']  # 答主关注者数
                    ans_info['author_voteup_count'] = user['voteup_count']  # 答主获赞数
                else:
                    # 账号停用等情况处理
                    ans_info['author_follower_count'] = 0
                    ans_info['author_voteup_count'] = 0
            ans_info['author_gender'] = answer['author']['gender']  # 答主性别
            ans_info['content'] = answer['content']  # 回答内容
            ans_info['voteup_count'] = answer['voteup_count']  # 赞同数
            ans_info['comment_count'] = answer['comment_count']  # 评论数
            ans_info['created_time'] = answer['created_time']  # 创建时间
            ans_info['updated_time'] = answer['updated_time']  # 更新时间
            ans_infos.append(ans_info)
        return ans_infos


if __name__ == '__main__':
    number = 1
    for i in range(0, 1000, 10):
        # 单次爬取问题个数上限为10
        qids = qid_get(interval=10, offset=i)
        print(i, qids)
        data = []
        for qid in qids:
            q_info = question_info_get(qid)
            if q_info:
                ans_infos = answer_info_get(qid, interval=10, offset=0)
                print(f'第{number}个问题爬取成功，id = {qid}，总回答数 =', q_info['answer_count'])
                q_info['answers'] = ans_infos
                data.append(q_info)
            else:
                print(f'第{number}个问题爬取失败')
            number += 1

        if data:
            filename = f'data/data{i}.json'
            with open(filename, 'w') as f:
                json.dump(data, fp=f, indent=4)
                print(f'第{i + 1}-{i + 10}个问题的数据保存成功')
