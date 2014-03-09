date: 2012-11-22
layout: post
title: "Python 笔记"
description: ""
category: "学习"
tags: [Python, 学习]
published: true

## 记录关于Python的相关笔记
-------------------------
##Section 1
前段时间写《数据挖掘》课的课程报告，凑了一篇烂烂的论文，关于协同滤波算法中Slope One算法的改进的。实验环节使用的是Python。Python不常用，这次用了下次忘所以先记下来吧。直接写在注释里了。

	:::python
	import string #导入string模块
	class SlopeOne(object):
	    def __init__(self):
	        self.diffs = {} #self. 类自己的变量
	        self.freqs = {} #dict初始化为空


	    def predict(self, userprefs):
	        preds, freqs = {}, {}
	        preds1, freqs1 = {}, {}
	        preds2, freqs2 = {}, {}
	        d = 5 # 变量直接赋值
	        alpha = 0.8

	        for item, rating in userprefs.iteritems(): #遍历字典userprefs的方法，userprefs是一个嵌套的dict，.iteritems()是item的遍历，键和value都有
	            for diffitem, diffratings in self.diffs.iteritems():
	                try: #dict中是否有相应的值
	                    freq = self.freqs[diffitem][item] 
	                except KeyError:
	                    continue
	                preds.setdefault(diffitem, 0.0) #设置初始值
	                freqs.setdefault(diffitem, 0)
	                preds1.setdefault(diffitem, 0.0)
	                freqs1.setdefault(diffitem, 0)
	                preds2.setdefault(diffitem, 0.0)
	                freqs2.setdefault(diffitem, 0.0)

	                preds1[diffitem] += (freq**0.5 )* (diffratings[item] + string.atoi(rating)) # ** 代表指数
	                freqs1[diffitem] += freq**0.5

	                preds2[diffitem] += (d-abs(diffratings[item])) * (diffratings[item] + string.atoi(rating))
	                freqs2[diffitem] += (d-abs(diffratings[item]));
	                
	        for item, value in preds.iteritems():
	            preds[item] = alpha*preds1[item]/freqs1[item]+(1-alpha)*preds2[item]/freqs2[item]
	            
	        return dict([(item, str(int(round(value))))#str整数转字符串，round取大约数
	                     for item, value in preds.iteritems()
	                     if item not in userprefs and freqs1[item] > 0])#这种写法的dict赋值，python中的代码块的用法

	    def update(self, userdata):
	        for ratings in userdata.itervalues():#itervalues()遍历是只遍历字典中的值，这里的值也是一个dict
	            for item1, rating1 in ratings.iteritems():
	                self.freqs.setdefault(item1, {})
	                self.diffs.setdefault(item1, {})
	                for item2, rating2 in ratings.iteritems():
	                    self.freqs[item1].setdefault(item2, 0)
	                    self.diffs[item1].setdefault(item2, 0.0)
	                    self.freqs[item1][item2] += 1
	                    self.diffs[item1][item2] += string.atoi(rating1) - string.atoi(rating2)
	        for item1, ratings in self.diffs.iteritems():#我把diffs想成2维数组。。。
	            for item2 in ratings:
	                ratings[item2] /= self.freqs[item1][item2]

	if __name__ == '__main__':
	    print "读入测试数据到dict..."
	    testdata={}
	    for line in open('u5.test'):#打开同目录下的文件，按行遍历
	        cell = line.split()     #每一行按空格split，结果放在cell数组中
	        c={}                    #数组初始化也是这样    
	        if cell[0] in testdata:
	            testdata[cell[0]][cell[1]]=cell[2]
	        else:
	            c[cell[1]]=cell[2]
	            testdata[cell[0]]=c  
	    print "从文件中载入数据到dict..."
	    userdata={}
	    for line in open('u5.base'):
	        cell = line.split()
	        c={}
	        if cell[0] in userdata:
	            userdata[cell[0]][cell[1]]=cell[2]
	        else:
	            c[cell[1]]=cell[2]
	            userdata[cell[0]]=c
	    s = SlopeOne()
	    print "计算数据，为预测做准备..."
	    s.update(userdata)#载入数据
	    print "计算...."
	    result={}
	    mae=0.0
	    cnt=0
	    for kk,movie in testdata.iteritems():
	        print "计算用户%s..." %kk
	        result=s.predict(userdata[kk])#调用预测方法
	        for kkk in movie:
	            if kkk in result:
	                mae+=abs(string.atoi(result[kkk])-string.atoi(movie[kkk]))#字符串转数字
	                cnt+=1
	    print "MAE for u5"
	    print mae/cnt
	    print "完mae_zzt"
	{% endhighlight %}

相应的Matlab画图代码，跑题了。。
	
	:::matlab
	a=[0.709435096154 0.700410739331 0.700460829493 0.70114654784 0.701763173713];
	t=[0.710486778846 0.699358845923 0.700811460629 0.702698643168 0.703265878581];
	z=[0.708383413462 0.699208575436 0.700410739331 0.701697291343 0.702464435985];
	x=1:1:5;
	plot(x,a,'r:+',x,t,'b:s',x,z,'g:*')

	xlabel('数据分组号')
	ylabel('平均绝对误差(MAE)')
	title('3种算法在5组数据上的比较')
	legend('基于用户评价数加权','基于项目评价加权','混合加权')
	{% endhighlight %}
	
----------
##Section 2
