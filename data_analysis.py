# coding: utf-8
# 2020/03 by florakl

import json
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Page
from pyecharts.commons.utils import JsCode
from util import data_sort


def read_json():
    voteup = []
    comment = []
    follower = []
    content = []
    # 整合读取json数据
    for i in range(0, 400, 10):
        with open(f'data/data{i}.json', 'r') as f:
            data = json.load(f)
            for q in data:
                for answer in q['answers']:
                    voteup.append(answer['voteup_count'])
                    comment.append(answer['comment_count'])
                    follower.append(answer['author_follower_count'])
                    content.append(answer['content'])
    return voteup, comment, follower, content


def distribution(voteup, comment, follower):
    # 赞数的分布统计

    # 按照赞数区间进行数据分类
    cutpoint = [0, 100, 1000, 4000, 10000, 20000, 40000, 400000]
    label = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    cut = pd.cut(voteup, cutpoint, right=False, labels=label)
    data = {'分类': cut, '赞数': voteup, '评论数': comment, '粉丝数': follower}
    df = pd.DataFrame(data)

    # 分组统计
    counts = df.groupby(['分类']).size()  # 赞数区间的频数统计
    c_mean = df['评论数'].groupby(df['分类']).mean()
    f_mean = df['粉丝数'].groupby(df['分类']).mean()
    # 提取千赞以上回答的数据
    x = ['(A) <0.1k', '(B) 0.1k-1k', '(C) 1k-4k', '(D) 4k-10k', '(E) 10k-20k', '(F) 20k-40k', '(G) >40k'][2:]
    y1 = list(map(int, c_mean))[2:]
    y2 = list(map(int, f_mean))[2:]

    df1 = df[df['分类'].isin(['C'])]['粉丝数']
    df2 = df[df['分类'].isin(['D'])]['粉丝数']
    df3 = df[df['分类'].isin(['E'])]['粉丝数']
    df4 = df[df['分类'].isin(['F'])]['粉丝数']
    df5 = df[df['分类'].isin(['G'])]['粉丝数']
    bins = [0, 50, 100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000, 5000000]
    label = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    # 在每个赞数区间内，进一步划分粉丝数区间
    f_cut1 = pd.cut(df1, bins, right=False, labels=label)
    c1 = pd.value_counts(f_cut1)
    f_cut2 = pd.cut(df2, bins, right=False, labels=label)
    c2 = pd.value_counts(f_cut2)
    f_cut3 = pd.cut(df3, bins, right=False, labels=label)
    c3 = pd.value_counts(f_cut3)
    f_cut4 = pd.cut(df4, bins, right=False, labels=label)
    c4 = pd.value_counts(f_cut4)
    f_cut5 = pd.cut(df5, bins, right=False, labels=label)
    c5 = pd.value_counts(f_cut5)

    return counts, x, y1, y2, c1, c2, c3, c4, c5


def multi_follower_counts(c1, c2, c3, c4, c5):
    # 不同赞数区间内的粉丝数分布统计
    _, y1 = data_sort(list(c1.index), list(c1))
    _, y2 = data_sort(list(c2.index), list(c2))
    _, y3 = data_sort(list(c3.index), list(c3))
    _, y4 = data_sort(list(c4.index), list(c4))
    _, y5 = data_sort(list(c5.index), list(c5))
    x = ['<50', '50-100', '100-500', '0.5k-1k', '1k-5k', '5k-10k', '1w-5w', '5w-10w', '10w-50w', '50w-100w', '>100w']

    line = (
        Line()
            .add_xaxis(x)
            .add_yaxis('赞同数为1k-4k', y1)
            .add_yaxis('赞同数为4k-10k', y2)
            .add_yaxis('赞同数为10k-20k', y3)
            .add_yaxis('赞同数为20k-40k', y4)
            .add_yaxis('赞同数为40k以上', y5)
            .extend_axis(yaxis=opts.AxisOpts(axislabel_opts=opts.LabelOpts()))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False), linestyle_opts=opts.LineStyleOpts(width=2))
            .set_global_opts(
            title_opts=opts.TitleOpts(title='赞数-粉丝数统计'),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=30), name='粉丝数'),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts()),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_left="right")
        )
    )

    filename = '赞数-粉丝数统计-line.html'
    line.render(filename)
    print('图表创建成功')

    bar = (
        Bar()
            .add_xaxis(x)
            .add_yaxis('赞同数为1k-4k', y1)
            .add_yaxis('赞同数为4k-10k', y2)
            .add_yaxis('赞同数为10k-20k', y3)
            .add_yaxis('赞同数为20k-40k', y4)
            .add_yaxis('赞同数为40k以上', y5)
            .extend_axis(yaxis=opts.AxisOpts(axislabel_opts=opts.LabelOpts()))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False), linestyle_opts=opts.LineStyleOpts(width=2))
            .set_global_opts(
            title_opts=opts.TitleOpts(title='赞数-粉丝数统计'),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=30), name='粉丝数'),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts()),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_left="right")
        )
    )

    filename = '赞数-粉丝数统计-bar.html'
    bar.render(filename)
    print('图表创建成功')

    page = Page(layout=Page.SimplePageLayout)
    page.add(line, bar)
    page.render("赞数-粉丝数统计.html")
    print('图表创建成功')


def comment_follower_mean(x, y1, y2):
    # 不同赞数区间内的平均评论数和粉丝数统计
    bar = (
        Bar(init_opts=opts.InitOpts(width="800px", height="500px"))
            .add_xaxis(x)
            .add_yaxis('平均评论数', y1)
            .extend_axis(yaxis=opts.AxisOpts(axislabel_opts=opts.LabelOpts(), name='粉丝数'))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
            title_opts=opts.TitleOpts(title='赞数-粉丝数&评论数'),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(), max_=5000, name='评论数')
        )
    )

    line = (
        Line()
            .add_xaxis(x)
            .add_yaxis("平均粉丝数", y2, yaxis_index=1, label_opts=opts.LabelOpts(is_show=False))
    )

    bar.overlap(line)
    filename = '赞数-粉丝数&评论数.html'
    bar.render(filename)
    print('图表创建成功')


def voteup_counts(counts):
    # 赞数分布的区间与频数统计
    x = ['(A) <0.1k', '(B) 0.1k-1k', '(C) 1k-4k', '(D) 4k-10k', '(E) 10k-20k', '(F) 20k-40k', '(G) >40k']
    y = list(counts)

    bar = (
        Bar()
            .add_xaxis(x)
            .add_yaxis('该赞数区间内的回答数', y)
            .extend_axis(yaxis=opts.AxisOpts(axislabel_opts=opts.LabelOpts()))
            .set_series_opts(label_opts=opts.LabelOpts(
            is_show=True,
            # formatter=JsCode("function(x){return Number(x.data/3970*100).toFixed(2) + '%';}")
        )
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title='赞数分布统计'),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(), )
        )
    )

    filename = '赞数分布统计.html'
    bar.render(filename)
    print('图表创建成功')


if __name__ == '__main__':
    voteup, comment, follower, content = read_json()
    counts, x, y1, y2, c1, c2, c3, c4, c5 = distribution(voteup, comment, follower)
    voteup_counts(counts)
    comment_follower_mean(x, y1, y2)
    multi_follower_counts(c1, c2, c3, c4, c5)
