import os
import sys
import markdown
import yaml
import collections
# import settings

from flask import Flask
from flask import render_template
from flask import Markup
from flask import url_for
from flask import abort
from flask import request
from flask.ext.frozen import Freezer
from werkzeug import cached_property
from werkzeug.contrib.atom import AtomFeed

POST_FILE_EXTENSION  = '.md'
POST_FILES_DIR       = 'posts'
SECRET_KEY  		 = 'not-so-secret'
FREEZER_BASE_URL     = 'http://localhost'

class SortedDict(collections.MutableMapping):
	"""docstring for SortedDict"""
	def __init__(self, items=None, key=None, reverse=False):
		self._items   = {}
		self._keys    = []
		self._reverse = reverse
		if key:
			self._key_fn = lambda k: key(self._items[k])
		else:
			self._key_fn = lambda k: self._items[k]

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
	"""docstring for Blog"""
	def __init__(self, app, root_dir='', file_ext=None):
		self._app     = app
		self._cache   = SortedDict(key=lambda p: p.date, reverse=True)
		self.root_dir = root_dir
		self.file_ext = file_ext if file_ext is not None else app.config['POST_FILE_EXTENSION']
		self._initialize_cache()

	@property
	def posts(self):
		if self._app.debug:
			return self._cache.values()
		else:
			return [post for post in self._cache.values() if post.published]

	def get_post_or_404(self, path):
		"""
			Return the Post object for the given path or raises a NotFound exception
		"""
		try:
			return self._cache[path]
		except KeyError:
			abort(404)

	def _initialize_cache(self):
		"""
			Walk the root directory and adds all posts to the cache
		"""
		for (root, dirpaths, filepaths) in os.walk(self.root_dir):
			for filepath in filepaths:
				filename, ext = os.path.splitext(filepath)
				if ext == self.file_ext:
					path = os.path.join(root, filepath).replace(self.root_dir, '')
					post = Post(path, root_dir=self.root_dir)
					self._cache[post.urlpath] = post

class Post(object):
	"""docstring for Post"""
	def __init__(self, path, root_dir = ''):
		self.urlpath   = os.path.splitext(path.strip('/'))[0]
		self.filepath  = os.path.join(root_dir, path.strip('/'))
		self.published = False
		self._initialize_metadata()

	def url(self, _external=False):
		return url_for('post', path=self.urlpath, _external=_external)

	@cached_property
	def html(self):
		with open(self.filepath, 'r') as fn:
			content = fn.read().split('\n\n', 1)[1].strip()
		return Markup(markdown.markdown(content, extensions=['codehilite']))

	def _initialize_metadata(self):
		content = ''
		with open(self.filepath, 'r') as fn:
			for line in fn:
				if not line.strip():
					break

				content += line
		self.__dict__.update(yaml.load(content))

app     = Flask(__name__)
# Loading configuration
# app.config.from_object(settings)
# app.config.from_pyfile('settings.py')
# app.config.from_envvar('SETTINGS_FILE')
#  pygmentize -S default -f html > static/css/syntax.css
app.config.from_object(__name__)
blog    = Blog(app, root_dir=POST_FILES_DIR)
freezer = Freezer(app)



@app.template_filter('date')
def format_date(value, format='%B %d, %Y'):
	return value.strftime(format)

@app.route('/')
def index():
	# posts = [Post('hello.md', root_dir='posts')]
	return render_template('index.html', posts=blog.posts)

@app.route('/blog/<path:path>/')
def post(path):
	post = blog.get_post_or_404(path)
	return render_template('post.html', post=post)

@app.route('/feed.atom')
def feed():
	feed = AtomFeed('Recent Articles',
		feed_url=request.url,
		url =request.url_root)

	posts = blog.posts[:10]
	title = lambda p: '%s: %s' % (p.title, p.subtitle) if hasattr(p, 'subtitle') else p.title

	for post in posts:
		feed.add(title(post),
			unicode(post.html),
			content_type='html',
			author='Admin',
			url=post.url(_external=True),
			updated=post.date,
			published=post.date)

	return feed.get_response()

if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1] == 'build':
		freezer.freeze()
	else:
		post_files = [post.filepath for post in blog.posts]
		app.run(port=8000, debug=True, extra_files=post_files)