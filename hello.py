from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from wtforms.widgets import TextArea

#create flask instance
app = Flask(__name__)

#New MySQL DB
app.config['SQLALCHEMY_DATABASE_URI']= 'mysql+pymysql://root:Bombaz.542@localhost/our_users'

#Old SQLite DB
#app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///users.db'
#SECRET KEY
app.config['SECRET_KEY'] = "my_secret_key"
#Initialize the Database
db=SQLAlchemy(app)
migrate = Migrate(app, db)

#create a Blog Post Model
class Posts(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(255))
    content=db.Column(db.Text)
    author=db.Column(db.String(255))
    date_posted=db.Column(db.DateTime, default=datetime.utcnow)
    slug=db.Column(db.String(255))

#Create a Post Form
class PostForm(FlaskForm):
    title=StringField("Title", validators=[DataRequired()])
    content=StringField("Content", validators=[DataRequired()], widget=TextArea())
    author=StringField("Author", validators=[DataRequired()])
    slug=StringField("Slug", validators=[DataRequired()])
    submit=SubmitField("Submit")

@app.route('/posts')
def posts():
    #Grab all the posts from the database
    posts=Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)

@app.route('/posts/<int:id>')
def post(id):
    post=Posts.query.get_or_404(id)
    return render_template('post.html', post=post)


#Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form=PostForm()

    if form.validate_on_submit():
        post=Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
        #clear the form
        form.title.data=''
        form.content.data=''
        form.author.data=''
        form.slug.data=''

        #Add post data to database
        db.session.add(post)
        db.session.commit()

        #return a message
        flash("Blog Post Submitted Sucesfully!")

    #redirect to webpage
    return render_template("add_post.html", form=form)

#Json Thing
@app.route('/date')
def get_current_date():
    return {"Date: ": date.today()}

#delete from database:
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete=Users.query.get_or_404(id)
    name = None
    form=UserForm()
    
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Sucesfully!!")
        
        our_users=Users.query.order_by(Users.date_added)
        return render_template("add_user.html", form=form, name=name, our_users=our_users)
    
    except:
        flash("Whoops! There was a problem deleting User")
        return render_template("add_user.html", form=form, name=name, our_users=our_users)

#Create a Model
class Users(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(200), nullable=False)
    email=db.Column(db.String(120), nullable=False, unique=True)
    favorite_color=db.Column(db.String(120))
    date_added=db.Column(db.DateTime, default=datetime.utcnow)
    #Do some password stuff
    password_hash=db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('Password is not readable attribute!')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    #Create a String
    def __repr__(self):
        return '<Name %r>' % self.name

#create Form Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color=StringField("Favorite Color")
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit") 
    
#udate Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if  request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash("User updated Sucesfully")
            return render_template("update.html", form=form, name_to_update=name_to_update)
        except:
            flash("Looks like there was an Error")
            return render_template("update.html", form=form, name_to_update=name_to_update)
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update, id=id)

#Password Form
class PasswordForm(FlaskForm):
    email = StringField("Whats your Email", validators=[DataRequired()])
    password_hash = PasswordField("Whats your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")          
      
#create Form Class
class NamerForm(FlaskForm):
    name = StringField("Whats your name", validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form=UserForm()
    if form.validate_on_submit():
        user=Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the passwords
            hashed_pw=generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name=form.name.data
        form.name.data=''
        form.email.data=''
        form.favorite_color.data=''
        form.password_hash=''
        flash("User Added Successfully")
    our_users=Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)
    
#create a route decorator
@app.route('/')
#create a function to return html in local host
def index():
    first_name="John"
    stuff="This is <strong>Bold</strong>Text"
    favorite_pizza=["pepperonix", "salami", "meat", "ham", 542]
    return render_template("index.html", 
        first_name=first_name,
        stuff=stuff,
        favorite_pizza=favorite_pizza)

#localhost:5000/user/jhon
@app.route('/user/<name>')

def user(name):
    return render_template("user.html", name=name)

#create custom error pages
#invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
#internal server error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

#create Passsword Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email=None
    password=None
    pw_to_check=None
    passed=None
    form = PasswordForm()

    #validate form
    if form.validate_on_submit():
        email = form.email.data
        password=form.password_hash.data
        #clear the form
        form.email.data=''
        form.password_hash.data=''
        #check User by email Email Address
        pw_to_check=Users.query.filter_by(email=email).first()
        #check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)

        #flash("Form Submitted Successfully")
        
    return render_template("test_pw.html",
                           email=email,
                           password=password,
                           pw_to_check=pw_to_check,
                           passed=passed,
                           form=form)

#create name page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    #validate form
    if form.validate_on_submit():
        name = form.name.data
        #clear our form
        form.name.data = ''
        flash("Form Submitted Successfully")
        
    return render_template("name.html",name=name,form=form)

