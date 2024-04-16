import os
import uuid
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, render_template_string, \
    send_from_directory, jsonify
from flask_login import UserMixin
from flask_login import current_user, login_required, LoginManager, login_user
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy

from key import key_gmail

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.secret_key = 'kcl-project'
db_folder = os.path.join(app.instance_path, 'db')
os.makedirs(db_folder, exist_ok=True)
db_path = os.path.join(db_folder, 'db.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'kclda01@gmail.com'
app.config['MAIL_PASSWORD'] = key_gmail
app.config['MAIL_DEFAULT_SENDER'] = 'kclda01@gmail.com'

mail = Mail(app)

db = SQLAlchemy(app)

login_manager = LoginManager(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    contact_info = db.Column(db.String(20), nullable=False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % self.username


class Consultant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    company_reg_number = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    emp_id = db.Column(db.String(50), nullable=False)
    daily_rate = db.Column(db.Float, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    delivery_report_date = db.Column(db.Date, nullable=True)  
    project_number = db.Column(db.String(100), nullable=True)  
    client = db.Column(db.String(100), nullable=True)  
    directorate = db.Column(db.String(100), nullable=True)  
    consultancy = db.Column(db.String(100), nullable=True)  
    programme_area = db.Column(db.String(100), nullable=True)  
    total_days_delivered = db.Column(db.Integer, nullable=True)  
    deliverables_status = db.Column(db.String(20), nullable=True)  
    delivery_areas = db.Column(db.Text, nullable=True)  
    total_days_allocated = db.Column(db.Integer, nullable=True)  
    feb_days = db.Column(db.Integer, nullable=True)  
    mar_days = db.Column(db.Integer, nullable=True)  
    apr_days = db.Column(db.Integer, nullable=True)  
    may_days = db.Column(db.Integer, nullable=True)  
    june_days = db.Column(db.Integer, nullable=True)  
    remaining_days = db.Column(db.Integer, nullable=True)  
    delivery_areas_details = db.Column(db.Text, nullable=True)  
    comments = db.Column(db.Text, nullable=True)  
    dependencies = db.Column(db.String(100), nullable=True)  
    rag = db.Column(db.String(20), nullable=True)  
    output = db.Column(db.String(100), nullable=True)  

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    agreement_signed = db.Column(db.Boolean, default=False)
    agreement_filename = db.Column(db.String(255))

    def __repr__(self):
        return f"<Consultant {self.name}>"

    def get_id(self):
        return str(self.id)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)
    project_reference = db.Column(db.String(100), nullable=False)
    client_contact_name = db.Column(db.String(100), nullable=False)
    client_contact_email = db.Column(db.String(100), nullable=False)
    project_description = db.Column(db.Text, nullable=False)
    project_deliverables = db.Column(db.Text, nullable=False)
    project_start_date = db.Column(db.Date, nullable=False)
    project_end_date = db.Column(db.Date, nullable=False)
    duration_in_days = db.Column(db.Integer, nullable=False)
    consultants_requirement_details = db.Column(db.Text, nullable=False)
    number_of_consultants_required = db.Column(db.Integer, nullable=False)
    consultant_phone_number = db.Column(db.String(20), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    consultants = db.relationship('Consultant', backref='project', lazy=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            if user.role == 'Consultant':
                return redirect(url_for('consultant_dashboard2'))
            elif user.role == 'Client':
                return redirect(url_for('client_dashboard2'))
            else:
                return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password. Please try again.'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/client_dashboard')
@login_required
def client_dashboard():
    client_email = current_user.username

    projects = Project.query.filter_by(client_contact_email=client_email).all()

    consultant_data = []
    for project in projects:
        consultants = Consultant.query.filter_by(project_id=project.id).all()
        for consultant in consultants:
            consultant_data.append({
                'name': consultant.name,
                'email': consultant.email,
                'agreement_signed': consultant.agreement_signed
            })

    return render_template('client_dashboard.html', consultant_data=consultant_data)


@app.route('/form')
@login_required
def show_form():
    if current_user.role in ['admin', 'Account Manager']:
        return render_template('form.html')
    else:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))


@app.route('/success')
def success():
    return 'Login successful!'


@app.route('/submit_form', methods=['POST'])
@login_required
def submit_form():
    project_data = {
        'client_name': request.form.get('client_name'),
        'project_name': request.form.get('project_name'),
        'project_reference': request.form.get('project_reference'),
        'client_contact_name': request.form.get('client_contact_name'),
        'client_contact_email': request.form.get('client_contact_email'),
        'project_description': request.form.get('project_description'),
        'project_deliverables': request.form.get('project_deliverables'),
        'project_start_date': datetime.strptime(request.form.get('project_start_date'), '%Y-%m-%d').date(),
        'project_end_date': datetime.strptime(request.form.get('project_end_date'), '%Y-%m-%d').date(),
        'duration_in_days': int(request.form.get('duration_in_days')),
        'consultants_requirement_details': request.form.get('consultants_requirement_details'),
        'number_of_consultants_required': int(request.form.get('number_of_consultants_required')),
        'consultant_phone_number': request.form.get('consultant_phone_number'),
        'user_id': current_user.id
    }

    project = Project(**project_data)
    db.session.add(project)
    db.session.commit()

    client_email = project_data['client_contact_email']
    client_password = 'default_password'
    client_user = User(username=client_email, password=client_password, role='Client',
                       contact_info='')
    db.session.add(client_user)
    db.session.commit()

    send_account_creation_email(client_email, client_password)


    consultants_data = []
    for i in range(1, project_data['number_of_consultants_required'] + 1):
        name = request.form.get(f'name_{i}')
        if name:
            consultant_data = {
                'name': name,
                'phone_number': request.form.get(f'phone_number_{i}'),
                'company_name': request.form.get(f'company_name_{i}'),
                'company_reg_number': request.form.get(f'company_reg_number_{i}'),
                'address': request.form.get(f'address_{i}'),
                'emp_id': request.form.get(f'emp_id_{i}'),
                'daily_rate': request.form.get(f'daily_rate_{i}'),
                'email': request.form.get(f'email_{i}'),
                'delivery_report_date': datetime.strptime(request.form.get(f'delivery_report_date_{i}'),
                                                          '%Y-%m-%d').date() if request.form.get(
                    f'delivery_report_date_{i}') else None,
                'project_number': request.form.get(f'project_number_{i}'),
                'client': request.form.get(f'client_{i}'),
                'directorate': request.form.get(f'directorate_{i}'),
                'consultancy': request.form.get(f'consultancy_{i}'),
                'programme_area': request.form.get(f'programme_area_{i}'),
                'total_days_delivered': request.form.get(f'total_days_delivered_{i}'),
                'deliverables_status': request.form.get(f'deliverables_status_{i}'),
                'delivery_areas': request.form.get(f'delivery_areas_{i}'),
                'total_days_allocated': request.form.get(f'total_days_allocated_{i}'),
                'feb_days': request.form.get(f'feb_days_{i}'),
                'mar_days': request.form.get(f'mar_days_{i}'),
                'apr_days': request.form.get(f'apr_days_{i}'),
                'may_days': request.form.get(f'may_days_{i}'),
                'june_days': request.form.get(f'june_days_{i}'),
                'remaining_days': request.form.get(f'remaining_days_{i}'),
                'delivery_areas_details': request.form.get(f'delivery_areas_details_{i}'),
                'comments': request.form.get(f'comments_{i}'),
                'dependencies': request.form.get(f'dependencies_{i}'),
                'rag': request.form.get(f'rag_{i}'),
                'output': request.form.get(f'output_{i}')
            }
            consultant = Consultant(**consultant_data)
            consultants_data.append(consultant_data)
            project.consultants.append(consultant)
            db.session.add(consultant)

    db.session.commit()

    for consultant_data in consultants_data:
        print('yes 194')
        create_consultant_account(consultant_data['email'], consultant_data['phone_number'])
    db.session.commit()

    flash('Project created successfully!', 'success')
    return redirect(url_for('client_dashboard2'))


def create_consultant_account(email, phone_number):
    print('yes')
    existing_user = Consultant.query.filter_by(email=email).first()
    print(existing_user)
    if existing_user:
        print('yes')
        password = 'default_password'
        role = 'Consultant'
        # new_user = User(username=email, password=password, role=role, contact_info=phone_number)
        # db.session.add(new_user)
        # db.session.commit()
        # send_account_creation_email(email, 'default_password')
    else:
        existing_user.contact_info = phone_number
        db.session.commit()


def send_account_creation_email(email, password):
    print('Mail Sent')
    msg = Message('Account Creation Notification', recipients=[email])
    msg.body = f'Your account has been created. You can now log in using the following credentials:\n\nUsername: {email}\nPassword: {password}'
    mail.send(msg)


@app.route('/agreement')
@login_required
def agreement():
    return send_from_directory(app.static_folder, 'consultant_agreement.pdf', as_attachment=True)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload_agreement', methods=['POST'])
@login_required
def upload_agreement():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        unique_filename = str(uuid.uuid4()) + '.pdf'
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)

        consultant = Consultant.query.filter_by(email=current_user.username).first()
        consultant.agreement_signed = True
        consultant.agreement_filename = unique_filename
        db.session.commit()

        flash('Agreement uploaded successfully', 'success')
        return redirect(url_for('consultant_dashboard'))
    else:
        flash('Invalid file format. Only PDF files are allowed.', 'error')
        return redirect(request.url)


@app.route('/consultant_dashboard')
@login_required
def consultant_dashboard():
    consultant = Consultant.query.filter_by(email=current_user.username).first()
    return render_template('consultant_dashboard.html', consultant=consultant)


@app.route('/client_dashboard2')
@login_required
def client_dashboard2():
    client_email = current_user.username

    projects = Project.query.filter_by(client_contact_email=client_email).all()
    print('Projects', projects, client_email)
    project_data = []
    delivery_metrics = {
        'total_days_delivered': 0,
        'overall_deliverables_status': 'On Track'
    }
    consultancy_allocation = {
        'total_allocated_days': 0,
        'remaining_days': 0
    }
    deliverables_breakdown = []
    dependencies = {
        'relevant_dependencies_status': 'Positive'
    }
    delivered_in_month = 'February 2024'
    output_data = []
    comments_feedback = {
        'comments': 'No comments provided'
    }

    if projects:  # Check if projects exist
        for project in projects:
            consultants = Consultant.query.filter_by(project_id=project.id).all()
            for consultant in consultants:
                project_data.append({
                    'project_number': project.project_reference,
                    'client': project.client_name,
                    'consultant': consultant.name,
                    'directorate': consultant.directorate,
                    'programme_area': consultant.programme_area
                })
                delivery_metrics['total_days_delivered'] += consultant.total_days_delivered or 0
                consultancy_allocation['total_allocated_days'] += consultant.total_days_allocated or 0
                consultancy_allocation['remaining_days'] += consultant.remaining_days or 0
                deliverables_breakdown.append({
                    'delivery_area': consultant.delivery_areas,
                    'feb_days': consultant.feb_days,
                    'mar_days': consultant.mar_days,
                    'apr_days': consultant.apr_days,
                    'may_days': consultant.may_days,
                    'june_days': consultant.june_days,
                    'remaining_days': consultant.remaining_days
                })
                output_data.append({
                    'work_area': consultant.delivery_areas_details,
                    'output': consultant.output,
                    'value_to_trust': consultant.comments
                })

        summary = {
            'track_status': 'On Track' if delivery_metrics[
                                              'overall_deliverables_status'] == 'On Track' else 'Off Track',
            'total_days_delivered': delivery_metrics['total_days_delivered'],
            'remaining_days': consultancy_allocation['remaining_days'],
            'dependencies_status': dependencies['relevant_dependencies_status']
        }

    else:
        summary = {
            'track_status': 'Off Track',
            'total_days_delivered': 0,
            'remaining_days': 0,
            'dependencies_status': 'Positive'
        }

    return render_template('client_dashboard2.html', project_data=project_data, delivery_metrics=delivery_metrics,
                           consultancy_allocation=consultancy_allocation, deliverables_breakdown=deliverables_breakdown,
                           dependencies=dependencies, delivered_in_month=delivered_in_month, output_data=output_data,
                           comments_feedback=comments_feedback, summary=summary)


def display_project_email(project):
    client_name = project.client_name
    project_name = project.project_name
    project_reference = project.project_reference
    project_start_date = project.project_start_date
    project_end_date = project.project_end_date
    duration_in_days = project.duration_in_days
    project_deliverables = project.project_deliverables
    number_of_consultants_required = project.number_of_consultants_required

    user = User.query.get(current_user.id)
    full_name = user.username
    position = user.role
    contact_info = user.contact_info

    email_content = f"""
    Dear {client_name},

    I trust this email finds you well. I am reaching out to discuss the resource requirements for our upcoming project, the {project_name} for {client_name}.

    Project Overview:
    Client: {client_name}
    Project Name: {project_name}
    Project Reference: {project_reference}
    Project Start Date: {project_start_date}
    Project End Date: {project_end_date}
    Duration: {duration_in_days} days

    Resource Needs:
    We are in need of specialised consultants to support various aspects of the project. Here is an initial breakdown:
    Project Deliverables: {project_deliverables}

    Number of Consultants Required: {number_of_consultants_required}

    I would appreciate the opportunity to discuss these requirements further and get your insights on the resource availability and allocation. Could we schedule a meeting at your earliest convenience?

    Your assistance in ensuring we have the right team in place is invaluable to the success of this project.

    Thank you for your time and consideration.

    Best Regards,
    {full_name}
    {position}
    {contact_info}
    """

    print('Mail Sent')
    msg = Message(f'Project Resource Planning - {project_name} Project', recipients=[project.client_contact_email])
    msg.body = email_content
    mail.send(msg)

    return render_template_string("<pre>{{ email_content }}</pre>", email_content=email_content)


@app.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        contact_info = request.form['contact_info']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
            return redirect(url_for('create_user'))

        new_user = User(
            username=username,
            password=password,
            role=role,
            contact_info=contact_info
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('dashboard'))
    else:
        return render_template('create_user.html')


@app.route('/consultant_dashboard2')
@login_required
def consultant_dashboard2():
    month = "April 2023"
    consultancy_details = {
        "project_number": "RM HL7 WP 8",
        "client": "Royal Marsden NHS Trust",
        "name": "Tony Alexander",
        "directorate": "Digital/IT",
        "consultancy": "HL7 SME",
        "programme_area": "Royal Marsden Integration Developer"
    }
    delivery_metrics = {
        "total_days_delivered": 11,
        "overall_deliverables_status": "ON TRACK"
    }
    agreed_deliverables = [
        {
            "total_days_allocated": 55,
            "feb_days": 13,
            "mar_days": 13,
            "apr_days": 13,
            "may_days": 11,
            "june_days": "",
            "remaining_days": 5
        },
    ]
    delivered_this_period = [
        {
            "work_area": "Develop solutions",
            "output": "",
            "value_to_trust": ""
        },
    ]
    dependencies = [
        {
            "dependency": "G",
            "rag": ""
        }
    ]
    comments = "Add any comments or feedback here"

    return render_template('consultant_dashboard2.html',
                           month=month,
                           consultancy_details=consultancy_details,
                           delivery_metrics=delivery_metrics,
                           agreed_deliverables=agreed_deliverables,
                           delivered_this_period=delivered_this_period,
                           dependencies=dependencies,
                           comments=comments)


@app.route('/update_delivered_this_period', methods=['POST'])
@login_required
def update_delivered_this_period():
    try:
        data = request.json
        print(f"Received data: {data}")

        for item in data:
            consultant = Consultant.query.filter_by(email=current_user.username).first()
            if consultant:
                consultant.output = item['output']
                consultant.comments = item['value_to_trust']
                db.session.commit()

        print("Data updated successfully")
        return redirect(url_for('consultant_dashboard2')), 200

    except Exception as e:
        print(f"Error updating data: {e}")
        return jsonify({'message': 'Failed to update data'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
