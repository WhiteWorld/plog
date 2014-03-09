import os
import sys
import platform
import collections
import codecs

from flask import Flask, render_template, url_for, abort, request
from flask.ext.frozen import Freezer
from werkzeug import cached_property
from werkzeug.contrib.atom import AtomFeed
import markdown
import yaml

from helpers import Pagination
from config import PER_PAGE


is_windows = False
if platform.system() == 'Windows':
    is_windows = True

class SortedDict(collections.MutableMapping):
    def __init__(self, items=None, key=None, reverse=False):
        self._items = {}
        self._keys = []
        if key:
            self._key_fn = lambda k: key(self._items[k])
        else:
            self._key_fn = lambda k: self._items[k]
        self._reverse = reverse

        if items is not None:
            self.update(items)

    def __getitem__(self, key):
        return self._items[key]

    def __setitem__(self, key, value):
        self._items[key] = value
        if key not in self._keys:
            self._keys.append(key)
            self._keys.sort(key=self._key_fn, reverse=self._reverse)

    def __delitem__(self, key):
        self._items.pop(key)
        self._keys.remove(key)

    def __len__(self):
        return len(self._keys)

    def __iter__(self):
        for key in self._keys:
            yield key

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self._items)

class Blog(object):
    def __init__(self, app, root_dir='', file_ext=None):
        self.root_dir = root_dir
        self.file_ext = file_ext if file_ext is not None else app.config['POSTS_FILE_EXTENSION']
        self._app = app
        self._cache = SortedDict(key=lambda p: p.date, reverse=True)
        self._initialize_cache()

    @property
    def posts(self):
        if self._app.debug:
            return self._cache.values()
        else:
            return [post for post in self._cache.values() if post.published]

    def get_post_or_404(self, path):
        """Returns the Post object for the given path or raises a NotFound exception
        """
        try:
            return self._cache[path]
        except KeyError:
            abort(404)

    def get_next_pre_or_404(self,path):
        try:
            keys=self._cache.keys()
            items=self._cache.items()
            index = items.index((path,self._cache[path]))
            if index == len(keys)-1:
                return self._cache[keys[index]],self._cache[keys[index-1]]
            if index == 0:
                return self._cache[keys[index+1]],self._cache[keys[index]]
            return self._cache[keys[index+1]],self._cache[keys[index-1]]
        except KeyError:
            abort(404)

    def _initialize_cache(self):
        """Walks the root directory and adds all posts to the cache
        """
        for (root, dir_paths, file_paths) in os.walk(self.root_dir):
            for file_path in file_paths:
                filename, ext = os.path.splitext(file_path)
                if ext == self.file_ext:
                    path = os.path.join(root, file_path).replace(self.root_dir, '')
                    post = Post(path, root_dir=self.root_dir)
                    self._cache[post.url_path] = post


class Post(object):
    def __init__(self, path, root_dir=''):
        if is_windows:
            self.url_path = os.path.splitext(path.strip('\\'))[0]
            self.file_path = os.path.join(root_dir, path.strip('\\'))
        else:
            self.url_path = os.path.splitext(path.strip('/'))[0]
            self.file_path = os.path.join(root_dir, path.strip('/'))
        self.published = False
        self._initialize_metadata()

    @cached_property
    def html(self):
        with codecs.open(self.file_path, mode='r',encoding='utf-8') as fin:
            if is_windows:
                content = fin.read().split('\r\n\r\n', 1)[1].strip()
            else:
                content = fin.read().split('\n\n', 1)[1].strip()
        return markdown.markdown(content, extensions=['codehilite'])

    def url(self, _external=False):
        return url_for('post', path=self.url_path, _external=_external)

    def _initialize_metadata(self):
        content = ''
        with open(self.file_path, 'r') as fin:
            for line in fin:
                if not line.strip():
                    break
                content += line
        self.__dict__.update(yaml.load(content))

app = Flask(__name__)
app.config.from_object('config')
blog = Blog(app, root_dir='posts')
freezer = Freezer(app)

@app.template_filter('date')
def format_date(value, format='%B %d, %Y'):
    return value.strftime(format)

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page




@app.route('/',defaults={'page':1})
@app.route('/page/<int:page>/')
def index(page):
    pagination = Pagination.Pagination(page, PER_PAGE, len(blog.posts))
    posts=[p for i,p in enumerate(blog.posts) if i >= (page-1)*PER_PAGE and i < page*PER_PAGE]
    return render_template('index.html', posts=posts,pagination=pagination,cur_page=page)



@app.route('/<path:path>/')
def post(path):
    post = blog.get_post_or_404(path)
    next,pre = blog.get_next_pre_or_404(path)
    return render_template('post.html', post=post,next=next,pre=pre)


@app.route('/tag/<string:tag>/')
def tag(tag):
    tagged = [p for p in blog.posts if tag in p.tags]
    return render_template('tag.html', posts=tagged, tag=tag)


 
@app.route('/tags/')
def tags():
    tags=[tag for p in blog.posts for tag in p.tags]
    tags=collections.Counter(tags)
    tags=sorted(tags.iteritems(),key=lambda d:d[1],reverse=True)
    return render_template('tags.html',tags=tags)

@app.route('/archive/')
def archive():
    archives={}
    for p in blog.posts:
        if not archives.has_key(p.date.year):
             archives[p.date.year]=[]
        archives[p.date.year].append(p)

    return render_template('archive.html', archives=archives)

@app.route('/feed.atom')
def feed():
    feed = AtomFeed('Recent Articles',
                    feed_url=request.url,
                    url=request.url_root)
    posts = blog.posts[:10]
    title = lambda p: '%s: %s' % (p.title, p.subtitle) if hasattr(p, 'subtitle') else p.title
    for post in posts:
        feed.add(title(post),
            unicode(post.html),
            content_type='html',
            author='Christopher Roach',
            url=post.url(_external=True),
            updated=post.date,
            published=post.date)
    return feed.get_response()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'build':
        freezer.freeze()
    else:
        post_files = [post.file_path for post in blog.posts]
        app.run(port=8000, debug=True, extra_files=post_files)