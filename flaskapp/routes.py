from flaskapp.models import User, Post
from flask import render_template, url_for, flash, redirect, request
from flaskapp.forms import RegistrationForm, LoginForm, PostForm
from flaskapp import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
	posts = Post.query.all()
	return render_template('home.html', posts=posts)

#decorators
@app.route("/about")
def about():
	return render_template('about.html', title='About')

@app.route("/register", methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	#calls RegistrationForm() class from forms.py
	form = RegistrationForm()
	#when form is submitted passes requirements, an account is created
	#and the user is rerouted to home page. A message will appear to inform user
	#the account was created.
	if form.validate_on_submit():
		#hashing password
		hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password = hashed_pw)
		db.session.add(user)
		db.session.commit()
		#end hashing
		flash(f'Account created. Please Log into your account', 'Success')
		return redirect(url_for('login'))
	return render_template('register.html', form=form)

@app.route("/login", methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			return redirect(url_for('home'))
		else:
			flash(f'Login unsuccessful. Please verify credentials', 'danger')
	return render_template('login.html', form=form)


@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))

@app.route("/post/new", methods=['GET','POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title=form.title.data, content=form.content.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Created!', 'success')
		return redirect(url_for('home'))
	return render_template('create_post.html', title='New Post', form=form)

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))