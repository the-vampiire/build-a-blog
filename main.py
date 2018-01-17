from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime as dt
from private import DB_URI # stores credentials (blocked from push in .gitignore)

app = Flask(__name__)
app.config['DEBUG'] = False      # displays runtime errors in the browser, too

# ----------------- DB CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI # imported from private.py
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model
class Blog(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(140), nullable = False)
  body = db.Column(db.Text, nullable = False)
  created_at = db.Column(db.String(25), nullable = False, default = dt.now().strftime('%B %d, %Y')) # inserts as 'Month[name] Day, Year'

  def __init__(self, title, body):
    self.title = title
    self.body = body

  def __repr__(self):
    return "<Blog Post: {}>".format(self.title)

# ----------------- SERVER

# DB Helper Functions

def get_blog_post(id):
  return Blog.query.get(id)

def get_blog_posts():
  return Blog.query.all()

def add_blog_post(title, body):
  new_post = Blog(title, body)
  db.session.add(new_post)
  db.session.commit()
  return new_post

# ----------------- ROUTES
@app.route('/post', methods=["POST"])
def add_post():
  title = request.form["title"]
  body = request.form["body"]

  title_error = False
  body_error = False
  if not title: title_error = "Must provide a unique title for the blog entry."
  if not body: body_error = "Must provide a valid body for the blog entry."
  if title_error or body_error:
    return render_template("index.html", blog_posts = get_blog_posts(), title_error = title_error, body_error = body_error)

  new_post = add_blog_post(title, body)
  return render_template("index.html", blog_posts = get_blog_posts(), new_post = new_post)

"""
Alternate: http://flask.pocoo.org/docs/0.12/quickstart/#variable-rules

@app.route('/blog/<int:id>', methods=["GET"])
def blog_page(id):
  # use id as a variable in route handling
"""

@app.route('/blog', methods=["GET"])
def blog_page():
  blog_post_id = request.args.get('id')
  try:
    blog_post_id = int(blog_post_id) # only accept integer IDs to prevent trolling robots
  except ValueError:
    return 'Nice try silly robot'

  return render_template("new_post.html", blog=get_blog_post(blog_post_id))

@app.route('/', methods=["GET"])
def index():
  return render_template("index.html", blog_posts=get_blog_posts())

if __name__ == "__main__":
  app.run()
