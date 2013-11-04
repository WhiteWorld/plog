import sys

from flask import Flask, render_template,request,url_for
#from flask.ext.flatpages import FlatPages
from flask_frozen import Freezer
from Pagination import Pagination

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'

FREEZER_DESTINATION = '../newblog'
FREEZER_DESTINATION_IGNORE='.git*'
FREEZER_BASE_URL='/newblog/'


PER_PAGE = 10
COUNT = 60

POSTS_FILE_EXTENSION = '.md'





app = Flask(__name__)
app.config.from_object(__name__)
#pages = FlatPages(app)
freezer = Freezer(app)

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page



@app.route('/',defaults={'page':1})
@app.route('/page/<int:page>')
def index(page):
    pagination = Pagination(page,PER_PAGE,COUNT)
    posts=[p for i,p in enumerate(pages) if i >= (page-1)*PER_PAGE and i < page*PER_PAGE]
    return render_template('index.html',posts=posts, pagination=pagination)

@app.route('/tag/<string:tag>/')
def tag(tag):
    tagged = [p for p in pages if tag in p.meta.get('tags', [])]
    return render_template('tag.html', posts=tagged, tag=tag)

@app.route('/tags/')
def tags():
    tags=[]
    for p in pages:
        tags.extend(p.meta.get('tags',[]))
    tags=list(set(tags))
    return render_template('tags.html',tags=tags)


@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/<path:path>/')
def page(path):
    page = pages.get_or_404(path)
    return render_template('page.html', page=page)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer.freeze()
    else:
        app.run(port=8000)


