import os
import markdown
import yaml

from flask import Flask
from flask import render_template
from flask import Markup
from flask import url_for
from werkzeug import cached_property

app                  = Flask(__name__)
POSTS_FILE_EXTENSION = '.md'
POSTS_FILE_DIR       = 'posts'
SECRET_KEY  		 = 'not-so-secret'

class Post(object):
	"""docstring for Post"""
	def __init__(self, path, root_dir=''):
		self.urlpath  = os.path.splitext(path.split('/'))[0]
		self.filepath = os.path.join(root_dir, path.strip('/'))
		self._initialize_metadata()

	@cached_property
	def url(self):
		return url_for('post', path=self.urlpath)

	@cached_property
	def html(self):
		with open(self.filepath, 'r') as fn:
			content = fn.read().split('\n\n', 1)[1].strip()
		return Markup(markdown.markdown(content))

	def _initialize_metadata(self):
		content = ''
		with open(self.filepath, 'r') as fn:
			for line in fn:
				if not line.strip():
					break

				content += line
		self.__dict__.update(yaml.load(content))

@app.template_filter('date')
def format_date(value, format='%B %d, %Y'):
	return value.strftime(format)

@app.route('/')
def index():
	posts = [Post('hello.md', root_dir='posts')]
	return render_template('index.html', posts=posts)

@app.route('/blog/<path:path>')
def post(path):
	post = Post(path + POSTS_FILE_EXTENSION, root_dir='posts')
	return render_template('post.html', post=post)

if __name__ == '__main__':
	app.debug = True
	app.run(port=8000)