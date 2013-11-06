date: 2012-09-25
layout: post
title: "Learning Ruby on Rails 1"
description: ""
category: "学习"
tags: [ROR, ruby, rails]
published: true

1. **Install Ruby,Rails**
-----------------
### Three ways:
- Compiling Ruby--source code
- Third Party Tools,eg.RVM,RubyInstaller
- Package Management Systems

*done*
2. Read [Ruby on Rails Guides](http://guides.rubyonrails.org/)
------
- Run Server
		$ rails new blog
		$ cd blog
		$ rake db:create
		这步提示没有JavaScript runtime
		解决办法：
		$ sudo apt-get install nodejs
		$ rails server
- Say Hello
		$ rails generate controller home index
		$ vim app/views/home/index.html.erb
		 <h1>Hello, Rails!</h1>
		$ rm public/index.html
		$ vim config/routes.rb
		Blog::Application.routes.draw do

  		\#...
  		\# You can have the root of your site routed with "root"
  		\# just remember to delete public/index.html.
  		root :to => "home#index"
*done*

