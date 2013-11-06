date: 2012-10-17
layout: post
title: "数据挖掘学习笔记兼课程报告"
description: ""
category: "学习"
tags: [数据挖掘, 笔记, 报告]
published: true

课程报告《改进的加权Slope One协同过滤算法》已完成,如下：
<iframe src="https://skydrive.live.com/embed?cid=A1E8316CC75B7FBA&resid=A1E8316CC75B7FBA%21442&authkey=AESJsR6CwRt06Uc" width="98" height="120" frameborder="0" scrolling="no"></iframe>




**以下内容可忽略**

-----------------

数据挖掘这个题目貌似大了一点。。。  
主要记录一下《数据挖掘》课程报告的准备，撰写过程。

数据挖掘的主要处理步骤和方法：  
数据的处理步骤：

1. Data Preprocessing
	* Distance Measures
	* Sampling
	* Dimensionality Reduction

2. Analysis
	* Prediction
	* Description

3. Interpretation

特定推荐系统的分类方法：

* Nearest Neighbors
* Decision Trees
* Ruled-based Classifiers
* Bayesian Classifiers
* Artificial Neural Networks
* Support Vector Machines

各种分类方法的性能评估：

* True Positives(TP)：实例的分类为A类，实际分类也是A类的数量
* True Negatives(TN): 实例的分类不是A类，实际分类也不是A类的数量
* False Positives(FP): 实例的分类为A类，实际分类不是A类的数量
* False Negatives(FN): 实例的分类不是A类，实际分类是A类的数量

Accuracy：`(TP+TN)/(TP+TN+FP+FN)`

Precision: 	`P=TP/(TP+FP)`  
Recall：`R=TP/(TP+FN)`  
F1-measure: `F1=2RP/(R+P)=2TP/(2TP+FN+FP)`  





推荐系统：

1. 收集用户信息的行为记录模块
2. 分析用户喜好的模型分析模块
3. 推荐算法模块

推荐系统分类

1. 协同过滤系统
2. 基于内容的推荐系统
3. 基于网络结构的推荐算法
4. 混合推荐算法
5. 其他推荐算法

基于用户的协同过滤

1. 收集使用者资讯。  
2. 最近邻搜索。      对于用户u，计算u与其他每个用户的相似度。把u与其他用户的相似度进行排序，找出top-k个用户
3. 产生推荐结果。    top-N推荐、关联推荐


基于项目的协同过滤

1. 收集使用者资讯。    
2. 针对项目最近邻搜索。    对任意的两个项目计算它们之间的相似度。对任意的项目，根据相似度排序，获取k个最相似的项目
3. 产生推荐结果。          预测用户对项目的喜欢程度


 SlopeOne算法：  
 根据其他users对items的评价以及当前user对其他items的评价，计算出当前user对当前items的评价

参考论文：

* 个性化推荐系统的研究进展   赵亮  计算机研究与发展
* Slope One Predictors for Online Rating-Based Collaborative Filtering
* [协同过滤基础](http://superangevil.wordpress.com/2010/03/16/basic_collaborative_filtering/)
* [推荐系统之协同过滤概述](http://www.vanjor.org/blog/2011/05/rs-collaborative-filtering/)
* [SLOPE ONE Python实现](http://www.serpentine.com/blog/2006/12/12/collaborative-filtering-made-easy/)
* [K-Means 算法](http://coolshell.cn/articles/7779.html)
* [推荐系统五大问题](http://www.resyschina.com/2010/03/five_problems_of_resys.html)

idea:  
slope one,增加纬度？  
slope one混合其他方法

<del>新的想法：  
Slope One的论文提到的The SLOPE ONE Scheme。论文中采用的是item-base。我的想法是考虑使用user-base 与 item-base相结合的方式预测。
</del>

报告题目： 改进的加权Slope One协同过滤算法  
英文题目: Improved Weighted Slope One Algorithm for Collaborative Filtering  
关键词：协同滤波，Slope One 算法，加权  
报告的初步提纲：

摘要：  
为了减小传统的Slope One算法在少数奇异点数据上给预测值带来的消极影响，对Slope One进行加权处理。分别对了使用用户评价数和评价相似度作为权值的情况进行分析，总结两者的优势和不足。结合这两种权值，这样就同时考虑了用户聚集评价某些项目的情况和某些项目评价相似度高的情况。通过调节这两种权值在新权值中所占的比例，达到对特定数据集的更加适应的目的。
最后了给出完整的算法流程。实验结果表明，与原算法相比，这种改进权值的Slope One 算法在推荐性能上有一定的提高。

1. 引言
	- 推荐算法的历史发展  

	随着互联网技术的发展，给信息的生成和传播创造了便利的条件。互联网上的推荐系统使用户在众多信息中快速而精准的获取对自己有用的信息成为可能。现在互联网上普遍使用推荐系统有购物网站(如Amazon.com)、社交网络(如weibo.com)和音乐电影推荐(如douban.com)等。一般推荐系统主要是解决给特定的用户推送特定内容的问题。
	
	众多的推荐系统从研究对象上，大体分为三类：基于内容的推荐、协同过滤推荐和混合推荐。其中协同过滤推荐获取了广泛的成功。协同滤波基本分为三类：基于用户协同过滤、基于项目协同过滤和基于模型协同过滤。基于用户的协同过滤和基于项目的协同滤波区别在于前者计算相似用户用以推荐后者计算相似项目用于推荐。基于模型的协同过滤是基于原始数据中抽取出的模型用于推荐。

	Slope One是一系列应用于 协同过滤的算法的统称。由 Daniel Lemire和Anna Maclachlan于2005年发表的论文中提出。该系列算法的简洁特性使它们的实现简单而高效，而且其精确度与其他复杂费时的算法相比也不相上下。基本的Slope One没有充分考虑到少数奇异点给预测值带来的消极影响。采用加权的办法可以一定程度上解决这个问题。加权值的考虑对算法的精确性很有影响。现在的加权值有基于两个项目用户数量的和基于项目相似度的两种。本文给出一种新的加权算法，结合了这两种加权算法，并给出完整的算法流程。由于推荐系统的应用场景复杂多变，同一个用户群在不同时期表现的兴趣差异也会很大。本文通过调节权值的比例来达到适应各种应用场景的目的。

	- 各个推荐算法的介绍
	- Slope One协同滤波算法面临的一般问题
	- 本文做了哪些工作，工作有什么用
2. 相关工作
	- 基本的Slope One算法
		- 简介
		Slope One算法是指协同滤波处理中使用的一系列算法，最初由Daniel Lemire 和 Anna Maclachlan在2005年的论文中出现。算法定义计算两个项目的之间相似度的方法。对于任意的两个项目，分别找出同时评价了这两个项目的用户，计算所有找到的用户对这两个项目评价的差值的和，然后除以同时评价这两个项目的用户总数，得出项目的相似度。用户对某一个项目的评价依赖于该用户已经评价的项目和待评价的项目之间的相似度。
		- 使用符号说明
		我们使用下面的符号对算法进行描述。使用u表示用户，使用Ui表示这个用户u对项目i
		的评分。S(u)表示用户u已经评分的项目集合。设X为推荐系统中所有的评价结合。num(S)表示集合S中的元素个数。用户U已经评价项目的平均值是u-。Si(X)表示X中所有评价了项目i的用户的集合。Si,j(X)表示同时评价了项目i和项目j的用户集合。
		- Slope One算法模型
		给一个数据集合X和任意两个项目i,j。计算项目i和项目j的评价偏差：
		公式1
		- 加权的Slope One算法
	- 现有的加权方法
	基本的Slope One算的一个缺点是评价的数量没有考虑在内。例如，我们要根据用户A对项目J、K的评价来预测L的评价。如果2000个用户对J和L进行了评价，但是只有20个用户对K和L进行评价，这时用户A对L的评价应该更多考虑A对项目J的评价。为此Slope One算法的作者又提出了加权的算法。这个加权算法改进增加了用户评价数作为权值：
	公式2


3. 改进的加权Slope One算法
	- 加权的Slope One算法的不足
	当直接采用的评价的用户数作为权值可能会增大用户数多的项目评分的比例，在现在这个多元化的社会，人的兴趣是广泛的。我们必须承认有很多小众化的、非主流的群体存在。所以适当提高用户数小的项目的评分比重，可能更适应当代社会用户的习惯。把权值改为用户数的平方根，可以改进提高小用户团体的评分比重。
	公式3
	- 修改用户数的权值（把用户数平方根）
	- 基于评分相似度的权值
	除了基于项目用户数的加权方式，还有一种基于项目评分的变换作为权值的加权方式。
	公式4 --权值公式

	- 两者的比较
	基于用户数的加权算法和基于评分系数各自从不同角度在调整了评价的重点。基于用户数的加权算法考虑了用户评价数分布的不平衡性，一定程度解决了奇异数据分布问题。基于评分系数的考虑到评价越接近的项目在预测时候应该具有更高的参考价值，应该赋予较大的权值。
	从用户场景上分析，。。。。。。
	- 改进的算法
	公式5，综合公式
	- 算法流程
	。。。。
4. 实验结果及分析
5. 结论
6. 参考文献  
[1] Towards the Next Generation of Recommender Systems: A Survey of the State-of-the-Art and Possible Extensions