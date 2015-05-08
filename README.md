## Python写的托管在Github上的静态博客

### 介绍
基于[Flask](http://flask.pocoo.org/), [Frozen-Flask](https://pythonhosted.org/Frozen-Flask/)和[Bootstrap](http://getbootstrap.com/)，
托管在[Github Pages](http://pages.github.com/)上。


### 使用方法
1.克隆源代码安装依赖

    # 获取源码
    git clone git@github.com:WhiteWorld/blog.git
    git checkout master

    # 安装库
    pip install -r requirements.txt

    # 测试
    python generator.py
    # 浏览器打开地址 http://127.0.0.1:8000/

2.配置

    #edit the config.py
    cd blog
    vim config.py
    #参考https://pythonhosted.org/Frozen-Flask/#configuration 修改 FREEZER_BASE_URL 和 FREEZER_DESTINATION

3.在posts文件夹下添加markdown格式的文章

    cd blog/posts
    touch my_post.md
    vim my_post.md
    # 在md文件的开头填写文章的元信息,如
    date: 2012-11-18
    title: "第一次马拉松2012杭州国际马拉松"
    tags: ["马拉松"]
    # 然后空一行
    # 然后写文章的内容
    # ...

4.生成静态博客并发布

    cd blog
    python generator.py build
    # 这时在FREEZER_DESTINATION文件夹下已经生成了静态blog了，可以上传到[Github Pages](http://pages.github.com/)或者自己的服务器上了。
