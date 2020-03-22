# coding: utf-8
# 2020/03 by florakl


import re
import pandas as pd
import jieba.analyse
from pyecharts import options as opts
from pyecharts.charts import Bar, WordCloud, Page
from util import data_sort
from data_analysis import read_json


def text_statistics(content):
    wordnum = []  # 中文字符数
    picnum = []  # 图片数
    paranum = []  # 段落数
    wordnumpp = []  # 每段字数

    for text in content:
        data = re.sub('[\u4E00-\u9FA5]', "", text)
        a = len(text) - len(data)  # 中文字符数
        b = text.count('data-actualsrc')  # 图片数
        c = text.count('<p>')  # 段落数标记1
        if c == 0:
            c = text.count('<br/>') // 2  # 段落数标记2
        if c == 0:
            c = 1  # 其余情况按段落数=1处理
        d = int(a / c)  # 每段字数
        wordnum.append(a)
        picnum.append(b)
        paranum.append(c)
        wordnumpp.append(d)

    return wordnum, picnum, paranum, wordnumpp


def text_distribution(voteup, wordnum, picnum, paranum, wordnumpp, content):
    cutpoint = [0, 100, 1000, 4000, 10000, 20000, 40000, 400000]
    label = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    cut = pd.cut(voteup, cutpoint, right=False, labels=label)
    data = {'分类': cut, '赞数': voteup, '回答字数': wordnum, '图片数': picnum,
            '段落数': paranum, '每段字数': wordnumpp, '回答内容': content}
    df = pd.DataFrame(data)
    return df


def text_bar(category, df):
    x = ['所有回答', '千赞以上回答', '赞数1k-4k', '赞数4k-10k', '赞数10k-20k', '赞数20k-40k', '赞数>40k']
    total_mean = df[category].mean()
    part_mean = df[~df['分类'].isin(['A', 'B'])][category].mean()
    y = [total_mean, part_mean]
    mean = df[category].groupby(df['分类']).mean()
    y += list(mean)[2:]
    y = ['%.2f' % a for a in y]

    bar = (
        Bar(init_opts=opts.InitOpts(width="600px", height="300px"))
            .add_xaxis(x)
            .add_yaxis(category, y)
            .extend_axis(yaxis=opts.AxisOpts(axislabel_opts=opts.LabelOpts()))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=True), linestyle_opts=opts.LineStyleOpts(width=2))
            .set_global_opts(
            title_opts=opts.TitleOpts(title=f'赞数-平均{category}统计'),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=30), name='赞数'),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts())
        )
    )

    filename = f'赞数-平均{category}统计.html'
    bar.render(filename)
    print('图表创建成功')

    return bar


def wordnum_analysis(df):
    # 万赞以上回答的字数分布
    cutpoint = list(range(0, 10100, 100))
    cutpoint.append(24000)  # 最大字数在24000字以内
    words = list(df[df['分类'].isin(['E', 'F', 'G'])]['回答字数'])
    cut = pd.cut(words, cutpoint, right=False)
    counts = pd.value_counts(cut)
    x = list(counts.index)
    y = list(counts)
    _, y0 = data_sort(x, y)

    labels = []
    for i in range(100, 10100, 100):
        label = str(i)
        labels.append(label)
    labels.append('>10000')

    bar = (
        Bar()
            .add_xaxis(labels)
            .add_yaxis('回答数', y0)
            .extend_axis(yaxis=opts.AxisOpts(axislabel_opts=opts.LabelOpts()))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False), linestyle_opts=opts.LineStyleOpts(width=2))
            .set_global_opts(
            title_opts=opts.TitleOpts(title='万赞以上回答字数分布统计'),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(), name='中文字数'),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts())
        )
    )

    filename = '万赞以上回答字数分布统计.html'
    bar.render(filename)
    print('图表创建成功')

    return bar


def char_filter(df):
    contents = list(df[~df['分类'].isin(['A', 'B'])]['回答内容'])
    filename = 'contents.txt'
    with open(filename, 'w', encoding='utf-8') as f:
        for text in contents:
            data = re.sub(u"\\<.*?\\>", "", text)
            f.write(data)
            print("回答写入完毕")


def wordcloud(path):
    with open(path, 'r', encoding='utf-8') as f:
        contents = f.read()

    jieba.analyse.set_stop_words('stopwords.txt')  # 停止词文件路径
    weights = jieba.analyse.extract_tags(contents, topK=100, withWeight=True)  # 取前100个词汇
    data = []
    for word, weight in weights:
        flag = True
        for ch in word:
            # 只保留中文分词结果
            if not (u'\u4e00' <= ch <= u'\u9fff'):
                flag = False
                break
        if flag:
            tup = (word, str(int(weight * 10000)))
            data.append(tup)

    (
        WordCloud()
            .add(series_name="高频词语分析", data_pair=data, word_size_range=[12, 100])
            .set_global_opts(
            title_opts=opts.TitleOpts(title="高频词语分析"),
            tooltip_opts=opts.TooltipOpts(is_show=True),
        )
            .render("高频词语分析.html")
    )


if __name__ == '__main__':
    # 读取文本内容和赞数
    voteup, _, _, content = read_json()
    # 计算文本各项数据
    wordnum, picnum, paranum, wordnumpp = text_statistics(content)
    # 根据赞数进行分组
    df = text_distribution(voteup, wordnum, picnum, paranum, wordnumpp, content)

    # 合并图表
    page = Page(layout=Page.SimplePageLayout)
    page.add(
        text_bar('回答字数', df),
        text_bar('图片数', df),
        text_bar('段落数', df),
        text_bar('每段字数', df)
    )
    page.render("赞数-文本数据统计分析.html")

    # 字数分布统计
    wordnum_analysis(df)

    # 词云
    char_filter(df)
    wordcloud('contents.txt')
