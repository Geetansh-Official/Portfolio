from flask import Flask, render_template, redirect, flash, url_for
from forms import LoginForm, RegisterForm, AboutEdit
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from extensions import db
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, LoginManager, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ThisIsSecretKey'

# Making the Ckeditor to make changes to the website
ckeditor = CKEditor(app)
bootstrap = Bootstrap5(app)

# Taking care of the Database


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)


from databases import User, Skills, AboutPage

with app.app_context():
    db.create_all()


# Making the Admin User
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Designing the first page
@app.route("/")
def home():
    about_content = db.get_or_404(AboutPage, 1)

    return render_template("index.html", current_user=current_user, about_content=about_content.about_content)


# Making up an Admin Palace
@app.route("/adminpalace", methods=["GET", "POST"])
def admin():
    admin_form = LoginForm()
    if admin_form.validate_on_submit():
        user = User.query.filter_by(email=admin_form.email.data).first()
        if user is not None and check_password_hash(user.password, admin_form.password.data):
            login_user(user)
            return redirect("/")
        else:
            flash("Invalid username or password")
            return redirect(url_for("admin"))

    work = "Hurray! You have learnt something new I guess!"
    return render_template("login.html", form=admin_form, work=work)

# Making a place to register
@app.route('/register_me', methods=['GET', 'POST'])
def register_me():
    form = RegisterForm()
    work = "Hi There! You seem to be friend of Aditya! Register Here"
    if form.validate_on_submit():

        email = form.email.data
        password = generate_password_hash(password=form.password.data, method='pbkdf2:sha256', salt_length=8)
        name = form.username.data
        try:
            user = User.query.filter_by(email=email).first()

            if user:
                flash("You have already registered. Log in instead", category="error")
                return redirect(url_for("admin"))
        except Exception as e:
            flash("An error occurred while registering: " + str(e), category="error")
            return redirect(url_for("admin"))

        new_user = User(email=email, password=password, name=name)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect("/")

    return render_template("login.html", form=form, work=work)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit():
    return render_template("edit.html")


# Making different edit functions for editing different parts of the website
@app.route('/about_edit', methods=['GET', 'POST'])
def about_edit():
    post = db.get_or_404(AboutPage, 1)
    about_form = AboutEdit(body=post.about_content)

    if about_form.validate_on_submit():
        post.about_content = about_form.body.data
        db.session.commit()
        return redirect(url_for('edit'))

    return render_template("editor.html", form=about_form)

# Starting the application
if __name__ == "__main__":
    app.run(debug=True)