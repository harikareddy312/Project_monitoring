from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'dhfskdi2334325345'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:----------@localhost/projectmonitoring'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class EndUser(db.Model):
    __tablename__ = 'enduser'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_role = db.Column(db.String(50))
    user_email = db.Column(db.String(100), unique=True, nullable=False)
    user_password = db.Column(db.String(100), nullable=False)

    def __init__(self, user_email, user_password, user_role):
        self.user_email = user_email
        self.user_password = generate_password_hash(user_password)
        self.user_role = user_role

class Projects(db.Model):
    __tablename__ = 'projects'
    project_id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(50))
    project_status = db.Column(db.String(50))
    project_issues = db.Column(db.String(255))

class UndertakeProject(db.Model):
    __tablename__ = 'undertake_projects'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('enduser.user_id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'))
    from_date = db.Column(db.Date)
    to_date = db.Column(db.Date)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        admin = EndUser.query.filter_by(user_email=email, user_role='admin').first()
        if admin and check_password_hash(admin.user_password, password):
            session['user_id'] = admin.user_id
            session['role'] = 'admin'
            return redirect(url_for('dashboard_admin'))
        else:
            return "Invalid admin credentials"
    return render_template('login_admin.html')

@app.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        new_admin = EndUser(user_email=email, user_password=password, user_role='admin')
        db.session.add(new_admin)
        db.session.commit()
        return redirect(url_for('login_admin'))
    return render_template('register_admin.html')

@app.route('/login_user', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = EndUser.query.filter_by(user_email=email, user_role='user').first()
        if user and check_password_hash(user.user_password, password):
            session['user_id'] = user.user_id
            session['role'] = 'user'
            return redirect(url_for('dashboard_user'))
        else:
            return "Invalid user credentials"
    return render_template('login_user.html')

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        new_user = EndUser(user_email=email, user_password=password, user_role='user')
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login_user'))
    return render_template('register_user.html')

@app.route('/dashboard_admin')
def dashboard_admin():
    if 'user_id' in session and session['role'] == 'admin':
        return render_template('dashboard_admin.html')
    return redirect(url_for('index'))

@app.route('/dashboard_user')
def dashboard_user():
    if 'user_id' in session and session['role'] == 'user':
        return render_template('dashboard_user.html')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('index'))

@app.route("/project_status",methods=['GET','POST'])
def project_status():
    project_details = None 
    if request.method == 'POST':
        project_id = request.form['id']
        project_details = Projects.query.filter_by(project_id=project_id).first()

    return render_template("project_status.html", project_details=project_details)

@app.route("/addproject" , methods=['GET','POST'])
def addproject():
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('login_user'))  
    if request.method == 'POST':
        project_id = request.form['id']
        title = request.form['title']
        new_project = Projects(project_id=project_id, project_name=title, project_status='0%', project_issues="")
        db.session.add(new_project)
        db.session.commit()
        user_id = session['user_id']
        undertake_entry = UndertakeProject(user_id=user_id, project_id=project_id)
        db.session.add(undertake_entry)
        db.session.commit()

        return redirect(url_for('dashboard_user'))    

    return render_template("addproject.html")
@app.route("/update_project", methods=['GET', 'POST'])
def update_project():
    if request.method == "POST":
        project_id = request.form.get("id")  # Make sure the form field has name="id"
        new_status = request.form.get("status")
        new_title = request.form.get("title")

        print(f"Received project_id: {project_id}, new_status: {new_status}")

        project = db.session.get(Projects, project_id)  
        if project:
            print(f"Before Update: {project.project_status}")  

            if new_status:
                project.project_status = new_status 
                db.session.flush()  
                db.session.commit()  
                print(f"After Update: {project.project_status}")  

                flash("Project updated successfully!", "success")
            else:
                flash("Invalid status update!", "warning")
        else:
            print("Project not found!")
            flash("Project not found!", "danger")

        return redirect(url_for("update_project"))

    return render_template("update_project.html")

if __name__ == '__main__':
    app.run(debug=True)
