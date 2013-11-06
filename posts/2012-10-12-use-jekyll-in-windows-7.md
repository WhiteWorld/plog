date: 2012-10-12
layout: post
title: "在Windows下使用jekyll发博客"
description: ""
category: "学习"
tags: [jekyll, MarkdownPad]
published: true

这篇blog就是在Windows下发布的。  
环境是：Windows 7 + ruby + jekyll + MarkdownPad + git  
搭建步骤：

* 首先，在Windows上分别安装git、ruby，设置环境变量
* 其次，在ruby基础上安装jekyll
* 设置github，clone自己的github上的blog项目。（这一步也可通过安装github的windows客户端完成）
* 安装markdown编辑器--MarkdownPad

注意一点：  
MarkdownPad可以可视化markdown格式文章的效果，但会在文章的所在目录下生成相应的.html文件。这些文件不是我们想要的，所以可以使用git的.gitignore文件来忽略掉  
做法：  
在_posts目录下添加文件 .gitignore  
文件内容(两行)：  
.gitignore  
*.html
