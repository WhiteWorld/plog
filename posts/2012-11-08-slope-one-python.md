date: 2012-11-08
layout: post
title: "Slope One算法的Python实现"
description: ""
category: "学习"
tags: [slope one, python]
published: true

关于基于项目评价数量的加权的Slope One算法，Bryan O'Sullivan在2006年有个Python实现。使用迭代开发的方法，首先在该程序的基础上进行基于项目评价的加权的Slope One算法。然后整合两种加权算法实现，得到最终的改进算法实现。

基于项目评价数量的加权算法实现
==============================
Bryan O'Sullivan写的的Python代码如下。程序的数据集较为简单，包括4个用户、4个项目以及用户对项目的评分。最终程序根据用户对一个项目的评分，预测出该用户对其他项目的评分。代码实现较为简洁，update方法负责更新数据集到程序中并分别计算了任意两个项目的共同的用户的评价数量和项目的相似度矩阵。

	{% highlight python %}
	class SlopeOne(object):
	    def __init__(self):
	        self.diffs = {}
	        self.freqs = {}

	    def predict(self, userprefs):
	        preds, freqs = {}, {}
	        for item, rating in userprefs.iteritems():
	            for diffitem, diffratings in self.diffs.iteritems():
	                try:
	                    freq = self.freqs[diffitem][item]
	                except KeyError:
	                    continue
	                preds.setdefault(diffitem, 0.0)
	                freqs.setdefault(diffitem, 0.0)
	                preds[diffitem] += (freq**0.5 )* (diffratings[item] + rating)
	                freqs[diffitem] += freq**0.5
	        return dict([(item, value / freqs[item])
	                     for item, value in preds.iteritems()
	                     if item not in userprefs and freqs[item] > 0])

	    def update(self, userdata):
	        for ratings in userdata.itervalues():
	            for item1, rating1 in ratings.iteritems():
	                self.freqs.setdefault(item1, {})
	                self.diffs.setdefault(item1, {})
	                for item2, rating2 in ratings.iteritems():
	                    self.freqs[item1].setdefault(item2, 0)
	                    self.diffs[item1].setdefault(item2, 0.0)
	                    self.freqs[item1][item2] += 1
	                    self.diffs[item1][item2] += rating1 - rating2
	        for item1, ratings in self.diffs.iteritems():
	            for item2 in ratings:
	                ratings[item2] /= self.freqs[item1][item2]

	if __name__ == '__main__':
	    userdata = dict(
	        alice=dict(squid=1.0,
	                   cuttlefish=0.5,
	                   octopus=0.2),
	        bob=dict(squid=1.0,
	                 octopus=0.5,
	                 nautilus=0.2),
	        carole=dict(squid=0.2,
	                    octopus=1.0,
	                    cuttlefish=0.4,
	                    nautilus=0.4),
	        dave=dict(cuttlefish=0.9,
	                  octopus=0.4,
	                  nautilus=0.5),
	        )
	    s = SlopeOne()
	    s.update(userdata)
	    print s.predict(dict(squid=0.4))
	    {% endhighlight  %}

基于项目评价的加权算法实现
==========================
基于项目评价的算法实现只需要在上述代码的基础上修改predict方法即可，因为这两种算法只是加权方式不一样，而加权方式只在代码的predict方法中。这里只给出predict方法

    {% highlight python %}
    def predict(self, userprefs):
         preds, freqs = {}, {}
         d = 1.0
         for item, rating in userprefs.iteritems():
             for diffitem, diffratings in self.diffs.iteritems():
                 try:
                     freq = self.freqs[diffitem][item]
                 except KeyError:
                     continue
                 preds.setdefault(diffitem, 0.0)
                 freqs.setdefault(diffitem, 0.0)
                 preds[diffitem] += (d-abs(diffratings[item])) * (diffratings[item] + rating)
                 freqs[diffitem] += (d-abs(diffratings[item]));
         return dict([(item, value / freqs[item])
                      for item, value in preds.iteritems()
                      if item not in userprefs and freqs[item] > 0])
    {% endhighlight %}

这里定义了一个变量d，即评分区间。

混合的加权算法实现
====================
混合了以上两种加权的算法实现同样只要修改predict函数即可。

	{% highlight python %}
	def predict(self, userprefs):
	        preds, freqs = {}, {}
	        preds1, freqs1 = {}, {}
	        preds2, freqs2 = {}, {}
	        d = 1
	        alpha = 0.5

	        for item, rating in userprefs.iteritems():
	            for diffitem, diffratings in self.diffs.iteritems():
	                try:
	                    freq = self.freqs[diffitem][item]
	                except KeyError:
	                    continue
	                preds.setdefault(diffitem, 0.0)
	                freqs.setdefault(diffitem, 0)
	                preds1.setdefault(diffitem, 0.0)
	                freqs1.setdefault(diffitem, 0)
	                preds2.setdefault(diffitem, 0.0)
	                freqs2.setdefault(diffitem, 0.0)

	                preds1[diffitem] += (freq**0.5 )* (diffratings[item] + rating)
	                freqs1[diffitem] += freq**0.5

	                preds2[diffitem] += (d-abs(diffratings[item])) * (diffratings[item] + rating)
	                freqs2[diffitem] += (d-abs(diffratings[item]));
	                
	        for item, value in preds.iteritems():
	            preds[item] = alpha*preds1[item]/freqs1[item]+(1-alpha)*preds2[item]/freqs2[item]
	            
	        return dict([(item, value)
	                     for item, value in preds.iteritems()
	                     if item not in userprefs and freqs[item] > 0])
	{% endhighlight %}
这里定义了两个字典分别用来存储两种加权算法计算的结果，最后再更新到最终的字典中。
