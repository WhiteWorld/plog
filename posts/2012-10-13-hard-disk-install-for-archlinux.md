date: 2012-10-13
layout: post
title: "使用硬盘安装的方法从U盘安装Archlinux"
description: ""
category: "学习"
tags: [archlinux, 硬盘安装]
published: true


###缘起


现在用的旧笔记本上是ubuntu+Windows 7双系统使用起来相当不方便  
打算安装Archlinux+Vbox+XP环境作为这个本本的最后归宿。  

###问题

这个笔记本已是风烛残年了。。。  

*  光驱已经读不出光盘了--> 不能使用光盘安装Archlinux
*  上次修过以后usb口不能启动了 --> 不能简单的从U盘启动安装  

只剩下硬盘或网络安装了  
今天使用的硬盘安装的方式，搜到两篇相关文章参考：

*  [硬盘安装Archlinux 2011.08 ](http://blog.fooleap.org/hard-disk-installation-for-archlinux.html) Windows下引导分区下的iso文件来启动。我使用的最新的iso 2012.10.06
*  [ArchLinux 2011.8 基于grub的硬盘安装简易指南](http://flanker017.sinaapp.com/?p=102#more-102)主要参考的是这篇文章的思路

###解决

我的做法：  
-  U盘拷入archlinux的iso文件
-  重启进入grub界面，按‘c’进入命令行界面
-  使用grub命令找到U盘的iso文件，使用文章中的方法安装系统

安装系统，现在的iso已经没有/arch/setup了，安装方法参照了[ArchLinux2012.09.07安装配置说明](http://www.bestzhou.net/tech/how-to-install-archlinux20120907/)



