date: 2012-10-29
layout: post
title: "读书笔记--Agile Web Development with Rails 4th edition"
description: ""
category: "读书笔记"
tags: [读书, 笔记]

##第一章

* 安装了Ruby、Rails、SQLite 3
* 编辑器选择Sublime Text 2

##第二章

* 创建新的应用程序`rails new demo`
* 启动本地服务器`rails server webrick`
* 创建新的控制器`rails generate controller Say hello goodbye`
* .html.erb中嵌入Ruby代码`<%= ... =%>`
* 在控制器中定义变量@time，在视图中可直接使用
* `link_to`使用`link_to "something", link_path`
* 控制器中的每一个方法对应视图中的同名文件

##第三章
这章内容依然不多。简单的介绍了模型、视图、控制器。

关系模型与面向对象编程语言结合一般两种方式：

* 以数据库为中心组织应用程序
* 以应用程序为中心组织数据库

Active Record是Rails采用的对象关系映射(ORM)层

##第四章  
介绍ruby

- Ruby语言操控的任何内容都是对象
- 命名规则
	- 局部变量名、方法参数名和方法名：以小写字母或下划线开始
	- 实例变量名：‘@’是前缀
	- 类名、模块名和常量名以大写字母作为首字母

##第五章 
Depot应用程序，开发一个购物车应用程序的前期准备  
使用纸和铅笔绘图

##第 六章
这章开始真正的进行代码级的开发  
进行到后面时发现我的rails版本是3.2.8,而书上的例程是基于3.0.5版的。为了避免不必要的版本问题影响正常的阅读，我又装了rails 3.0.5。  
创建程序时，使用`rails _3.0.5_ `代替原来的`rails`就可以使用指定的版本了,之后除非修改Gem文件，否则一直使用创建时的版本。

这章创建了应用程序，生成基本的商品列表。

##第七章
关于测试。validates验证 单元测试assert 静态测试 test fixtures yaml文件

##第八章
第六章创建了product，相当于是所有商品的类，卖家可以在后台可以添加删除商品。这一章又创建了store，是与消费者交互的*商店*。

然后使用各种css美化布局。

##第九章
创建一个购物车cart  
创建了在线商品`line_item`。  
添加了一个按钮，我这一步的`rake test:functionals`出了错误
>test_should_create_line_item(LineItemsControllerTest):
NoMethodError: undefined method `product=' for #<LineItem:0xb9392ec>

解决办法：
>Go to /models/line_item.rb and add the following …
class LineItem < ActiveRecord::Base
belongs_to :product
belongs_to :cart
attr_accessible :cart_id, :product_id, :quantity
end

之后又出现错误
> undefined method `title' for nil:NilClass

网上也有类似的[错误](http://ruby-china.org/topics/5176)，纠结半天还是没有解决。。  
果断从书上的例子中的文件夹depot\_f出发，运行之前要先设置一下，先依次两条命令：`rake db:setup`和`rake db:migrate`之后就可以运行本地server了`rake server`

###练习题  
修改`<%=  image_tag(product.image_url) %>`为`<%= link_to image_tag(product.image_url), line_items_path(:product_id => product), html_options={:method => "post"} %>`，这样点击图片和Add to Cart按钮都会添加到cart

##第十章
为购物车中的产品添加计数器。在Cart的Modle里添加add\_product方法，判断要添加的产品是否已在购物车中。同时修改控制器里的create方法，以及相应的show  
添加同类商品的单行显示  

###关于数据迁移
当使用命令`rails generate migration [迁移名]...`时就会在db文件夹下产生一个相应的文件。文件的内容就是实际要对数据库进行修改的内容，有两个方法：down 、up
- up方法：定义数据库要如何改变
- down方法：定义数据库如何从up之后，回滚到原来的状态

两者是相反的操作过程，使用`rake db:rollback`则调用当前的down方法，使用`rake db:migration`则调用当前up方法。

###错误处理
错误处理应该包括安全性和美观性两个方面进行考虑。

##第十一章
引入了Ajax技术

##第十二章
创建了订单模型

##第十三章
发送电子邮件

