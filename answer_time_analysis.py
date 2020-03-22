# coding: utf-8
# 2020/03 by florakl

import pandas as pd
from datetime import datetime, timedelta
from pyecharts import options as opts
from pyecharts.charts import Bar, Scatter, Page
from util import time_format, data_sort


def readdata(filename):
    # 读取单个问题的所有回答
    with open(filename) as f:
        lines = f.readlines()
    qids = []
    titles = []
    ans_times = []
    voteups = []
    for i in range(0, len(lines), 4):
        qids.append(lines[i].strip())
        titles.append(lines[i + 1].strip())
        ans_times.append(list(map(int, lines[i + 2].strip()[:-1].split(','))))
        voteups.append(list(map(int, lines[i + 3].strip()[:-1].split(','))))
    return qids, titles, ans_times, voteups


def data_full(x, y):
    # 日期缺失值补全
    date_list = x[:]
    datestart = datetime.strptime(x[0], '%Y-%m-%d')
    dateend = datetime.strptime(x[-1], '%Y-%m-%d')
    while datestart < dateend:
        datestart += timedelta(days=1)
        temp = datestart.strftime('%Y-%m-%d')
        if temp not in x:
            date_list.append(temp)
            y.append(0)
    x1, y1 = data_sort(date_list, y)
    return x1, y1


def visualize(voteup, ans_time, qid, title):
    # 将所有回答按时间排序，并获取每个回答的年月日格式日期
    d, v = data_sort(ans_time, voteup)
    dates = []
    for i in d:
        dates.append(time_format(i))

    # 提取前n个高赞回答作为标记点
    n = 5
    max_voteup = []
    max_dates = []
    z = sorted(zip(v, dates), reverse=True)
    for i, j in z[:n]:
        max_voteup.append(i)
        max_dates.append(j)
    max_data = []
    for i in range(n):
        markpoint = {}
        markpoint['coord'] = [max_dates[i], max_voteup[i]]
        markpoint['name'] = str(i + 1)
        max_data.append(markpoint)

    # 分组统计
    data = {'日期': dates, '赞数': v}
    df = pd.DataFrame(data)
    groupnum = df.groupby(['日期']).size()
    voteupsum = df['赞数'].groupby(df['日期']).sum()
    voteupmax = df['赞数'].groupby(df['日期']).max()
    voteupmean = df['赞数'].groupby(df['日期']).mean()
    # 默认访问values，提取index需要写明
    x = list(groupnum.index)
    y1 = list(groupnum)
    y2 = list(voteupsum)
    y3 = list(voteupmax)
    y4 = list(map(int, voteupmean))

    # 日期补全
    x0, y1 = data_full(x, y1)
    _, y2 = data_full(x, y2)
    _, y3 = data_full(x, y3)
    _, y4 = data_full(x, y4)

    # 获取相对天数列表
    x1 = list(range(len(x0)))

    bar = (
        Bar(init_opts=opts.InitOpts(width="700px", height="350px"))
            .add_xaxis(x0)
            .add_yaxis('回答数', y1)
            .extend_axis(xaxis_data=x1,
                         xaxis=opts.AxisOpts(
                             axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                             axisline_opts=opts.AxisLineOpts(
                                 is_on_zero=False, linestyle_opts=opts.LineStyleOpts()
                             ),
                         ))
            .extend_axis(yaxis=opts.AxisOpts(axislabel_opts=opts.LabelOpts()))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
            title_opts=opts.TitleOpts(title=title, title_link=f'https://www.zhihu.com/question/{qid}'),
            xaxis_opts=opts.AxisOpts(
                axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                axisline_opts=opts.AxisLineOpts(
                    is_on_zero=False, linestyle_opts=opts.LineStyleOpts()
                ),
            ),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts()),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_left="right"))
    )

    scatter = (
        Scatter()
            .add_xaxis(x0)
            .add_yaxis("当日总赞数", y2, yaxis_index=1)
            .add_yaxis("当日最高赞数", y3, yaxis_index=1,
                       markpoint_opts=opts.MarkPointOpts(data=max_data,
                                                         symbol='pin', symbol_size=50,
                                                         label_opts=opts.LabelOpts(color='#fff')))
            .add_yaxis("当日平均赞数", y4, yaxis_index=1)
    )

    bar.overlap(scatter)
    filename = f'{qid}-回答统计分析.html'
    bar.render(filename)
    print(f'{qid}-图表创建成功')

    return bar


if __name__ == '__main__':
    qids, titles, ans_times, voteups = readdata('answer_time.txt')
    page = Page(layout=Page.SimplePageLayout)
    # 循环add生成组合图表
    for i in range(len(qids)):
        # visualize(voteups[i], ans_times[i], qids[i], titles[i])
        page.add(visualize(voteups[i], ans_times[i], qids[i], titles[i]))
    page.render("回答统计分析.html")
