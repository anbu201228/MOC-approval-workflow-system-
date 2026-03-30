from flask import Flask, render_template, request, redirect, flash, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta  # Add timezone
import os
import json
import secrets
print(secrets.token_hex(32))
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import threading
from flask_mail import Mail, Message
from flask import request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'alstom-moc-secret-key-2024'

# Use environment variable (recommended)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:Anbu%402803200@db.hqgosnkmtlpbxneegiph.supabase.co:5432/postgres"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"connect_args": {"check_same_thread": True}}

db = SQLAlchemy(app)

# Email Configuration - REPLACE WITH YOUR DETAILS
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'anbukkarasan2004@gmail.com'  # ← YOUR GMAIL
app.config['MAIL_PASSWORD'] = 'uhzn vvmg ffbd yhcx'         # ← YOUR APP PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = ('MOC System', 'alstom.moc.system@gmail.com')

mail = Mail(app)

@app.context_processor
def inject_now():
    return {'datetime': datetime, 'timedelta': timedelta}



# ========== DATABASE MODELS ==========

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='employee')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # Fixed
    is_active = db.Column(db.Boolean, default=True)

class MOC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    moc_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())  # Fixed
    
    change_category = db.Column(db.Text)
    change_type = db.Column(db.String(50))
    change_impact = db.Column(db.Text)
    
    checkpoints = db.Column(db.Text)
    
    hira_review_required = db.Column(db.Boolean, default=False)
    aspect_impact_review_required = db.Column(db.Boolean, default=False)
    additional_comments = db.Column(db.Text)
    
    dap_ref_no = db.Column(db.String(100))
    dvr_ref_no = db.Column(db.String(100))
    control_measures = db.Column(db.Text)
    
    status = db.Column(db.String(50), default='Draft')
    current_step = db.Column(db.Integer, default=0)
    total_steps = db.Column(db.Integer, default=6)
    
    submitted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approver1_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    approver2_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    approver3_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    approver4_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    approver5_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    approver6_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    approver1_status = db.Column(db.String(20), default='Pending')
    approver2_status = db.Column(db.String(20), default='Pending')
    approver3_status = db.Column(db.String(20), default='Pending')
    approver4_status = db.Column(db.String(20), default='Pending')
    approver5_status = db.Column(db.String(20), default='Pending')
    approver6_status = db.Column(db.String(20), default='Pending')
    
    approver1_date = db.Column(db.DateTime)
    approver2_date = db.Column(db.DateTime)
    approver3_date = db.Column(db.DateTime)
    approver4_date = db.Column(db.DateTime)
    approver5_date = db.Column(db.DateTime)
    approver6_date = db.Column(db.DateTime)
    
    approver1_comments = db.Column(db.Text)
    approver2_comments = db.Column(db.Text)
    approver3_comments = db.Column(db.Text)
    approver4_comments = db.Column(db.Text)
    approver5_comments = db.Column(db.Text)
    approver6_comments = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # Fixed
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # Fixed
    
    submitter = db.relationship('User', foreign_keys=[submitted_by])
    approver1 = db.relationship('User', foreign_keys=[approver1_id])
    approver2 = db.relationship('User', foreign_keys=[approver2_id])
    approver3 = db.relationship('User', foreign_keys=[approver3_id])
    approver4 = db.relationship('User', foreign_keys=[approver4_id])
    approver5 = db.relationship('User', foreign_keys=[approver5_id])
    approver6 = db.relationship('User', foreign_keys=[approver6_id])

class ApprovalHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    moc_id = db.Column(db.Integer, db.ForeignKey('moc.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50))
    step = db.Column(db.Integer)
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # Fixed
    
    moc = db.relationship('MOC', backref='history')
    user = db.relationship('User')

# ========== HELPER FUNCTIONS ==========

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user = User.query.get(session['user_id'])
            if user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def generate_moc_number():
    today = datetime.now()
    count = MOC.query.filter(
        db.extract('year', MOC.created_at) == today.year,
        db.extract('month', MOC.created_at) == today.month,
        db.extract('day', MOC.created_at) == today.day
    ).count() + 1
    return f"MOC-{today.year}{today.month:02d}{today.day:02d}-{count:03d}"

def get_default_approvers():
    approvers = {}
    approver1 = User.query.filter_by(role='approver1').first()
    approver2 = User.query.filter_by(role='approver2').first()
    approver3 = User.query.filter_by(role='approver3').first()
    approver4 = User.query.filter_by(role='approver4').first()
    approver5 = User.query.filter_by(role='approver5').first()
    approver6 = User.query.filter_by(role='approver6').first()
    
    if approver1: approvers['approver1'] = approver1.id
    if approver2: approvers['approver2'] = approver2.id
    if approver3: approvers['approver3'] = approver3.id
    if approver4: approvers['approver4'] = approver4.id
    if approver5: approvers['approver5'] = approver5.id
    if approver6: approvers['approver6'] = approver6.id
    
    return approvers

# ========== ROUTES ==========

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username, is_active=True).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['name'] = user.name
            session['role'] = user.role
            session['department'] = user.department
            
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

from flask import request, render_template, redirect, url_for, flash, session

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            employee_id = request.form.get('employee_id')
            name = request.form.get('name')
            department = request.form.get('department')
            username = request.form.get('username')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return redirect(url_for('register'))
            
            # TEMP: skip DB check to avoid crash
            # if User.query.filter_by(username=username).first():
            #     flash('Username already exists', 'danger')
            #     return redirect(url_for('register'))
            
            # TEMP: skip DB insert
            # user = User(...)
            # db.session.add(user)
            # db.session.commit()
            
            flash('Registration successful! (Test Mode)', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            return f"Error: {str(e)}", 500
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    
    total_mocs = MOC.query.filter_by(submitted_by=user.id).count()
    pending_approval = MOC.query.filter(
        ((MOC.approver1_id == user.id) & (MOC.approver1_status == 'Pending')) |
        ((MOC.approver2_id == user.id) & (MOC.approver2_status == 'Pending')) |
        ((MOC.approver3_id == user.id) & (MOC.approver3_status == 'Pending')) |
        ((MOC.approver4_id == user.id) & (MOC.approver4_status == 'Pending'))
    ).count()
    approved_mocs = MOC.query.filter_by(submitted_by=user.id, status='Approved').count()
    
    pending_for_me = MOC.query.filter(
        ((MOC.approver1_id == user.id) & (MOC.approver1_status == 'Pending')) |
        ((MOC.approver2_id == user.id) & (MOC.approver2_status == 'Pending')) |
        ((MOC.approver3_id == user.id) & (MOC.approver3_status == 'Pending')) |
        ((MOC.approver4_id == user.id) & (MOC.approver4_status == 'Pending'))
    ).limit(5).all()
    
    recent_mocs = MOC.query.order_by(MOC.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html',
                         user=user,
                         total_mocs=total_mocs,
                         pending_approval=pending_approval,
                         approved_mocs=approved_mocs,
                         pending_for_me=pending_for_me,
                         recent_mocs=recent_mocs)

# ========== ONLY ONE new_moc ROUTE - REMOVE DUPLICATES ==========

@app.route('/moc/new', methods=['GET', 'POST'])
@login_required
def new_moc():
    user = get_current_user()
    
    if request.method == 'POST':
        moc_number = generate_moc_number()
        
        # Create checkpoints from form data
        checkpoints = {}
        for i in range(1, 23):  # 22 questions
            answer = request.form.get(f'checkpoint_{i}_answer', 'No')
            remarks = request.form.get(f'checkpoint_{i}_remarks', '')
            
            # Hardcode the questions (simplified version)
            questions = [
                "Is the original design intent being changed?",
                "Has there been any change to materials of construction?",
                "Could this change hinder access to other equipment?",
                "Has this design been previously changed?",
                "Could this change impact the supply or consumption of utilities?",
                "Could this change create any new hazards during installation / construction or in later service?",
                "Is there any change to procedures or operating conditions?",
                "Are there any upstream or downstream effects as a result of the change?",
                "Is additional protection required as a result of this change?",
                "Are there any legal requirements involved for this change?(Layout change, Environment Consent change, Additional waste generation)",
                "Is there any impact on existing safety equipment (Trips, alarms etc.)?",
                "Is there any impact on fire protection / preventive facilities?",
                "Will the performance characteristics of the equipment, facility or system be altered?",
                "Are there any changes required to training or procedures as a result of this change?",
                "Is there any increase in hazardous or flammable material inventory?",
                "Will the change cause or increase housekeeping concern?",
                "Will this change increase or cause consumption of resources including natural resources?",
                "Will this change increase or cause wastage of any resources including natural resources?",
                "Will the change increase the existing risk or create new risk to occupational health (acute or chronic)?",
                "Will the change cause risk of damage of any equipment / property (during erection/operation)?",
                "Impact on waste generation and recycling as well as end-of-life management is part of the specifications and selection.",
                "Will the change cause any Ergonomical issues / impact ( Man/Machine/Material )"
            ]
            
            if i <= len(questions):
                checkpoints[i] = {
                    'question': questions[i-1],
                    'answer': answer,
                    'remarks': remarks
                }
        
        moc = MOC(
            moc_number=moc_number,
            title=request.form.get('title', 'Window installation - Manual Lifting'),
            date=datetime.strptime(request.form.get('date'), '%Y-%m-%d').date(),
            change_category=request.form.get('change_category', 'Process & Methods Change'),
            change_type=request.form.get('change_type', 'Temporary'),
            change_impact=request.form.get('change_impact', 'Safety'),
            checkpoints=json.dumps(checkpoints),
            hira_review_required=request.form.get('hira_review') == 'yes',
            aspect_impact_review_required=request.form.get('aspect_impact_review') == 'yes',
            dap_ref_no=request.form.get('dap_ref_no', ''),
            dvr_ref_no=request.form.get('dvr_ref_no', ''),
            additional_comments=request.form.get('additional_comments', ''),
            control_measures=request.form.get('control_measures', ''),
            status='Draft',
            submitted_by=user.id,
            current_step=0
        )
        
        approvers = get_default_approvers()
        if approvers:
            moc.approver1_id = approvers.get('approver1')
            moc.approver2_id = approvers.get('approver2')
            moc.approver3_id = approvers.get('approver3')
            moc.approver4_id = approvers.get('approver4')
            moc.approver5_id = approvers.get('approver5')
            moc.approver6_id = approvers.get('approver6')
        
        db.session.add(moc)
        db.session.commit()
        
        flash(f'MOC created successfully! MOC Number: {moc_number}', 'success')
        return redirect(url_for('view_moc', moc_id=moc.id))
    
    # Get the 22 checkpoint questions
    checkpoints = [
        "Is the original design intent being changed?",
        "Has there been any change to materials of construction?",
        "Could this change hinder access to other equipment?",
        "Has this design been previously changed?",
        "Could this change impact the supply or consumption of utilities?",
        "Could this change create any new hazards during installation / construction or in later service?",
        "Is there any change to procedures or operating conditions?",
        "Are there any upstream or downstream effects as a result of the change?",
        "Is additional protection required as a result of this change?",
        "Are there any legal requirements involved for this change?(Layout change, Environment Consent change, Additional waste generation)",
        "Is there any impact on existing safety equipment (Trips, alarms etc.)?",
        "Is there any impact on fire protection / preventive facilities?",
        "Will the performance characteristics of the equipment, facility or system be altered?",
        "Are there any changes required to training or procedures as a result of this change?",
        "Is there any increase in hazardous or flammable material inventory?",
        "Will the change cause or increase housekeeping concern?",
        "Will this change increase or cause consumption of resources including natural resources?",
        "Will this change increase or cause wastage of any resources including natural resources?",
        "Will the change increase the existing risk or create new risk to occupational health (acute or chronic)?",
        "Will the change cause risk of damage of any equipment / property (during erection/operation)?",
        "Impact on waste generation and recycling as well as end-of-life management is part of the specifications and selection.",
        "Will the change cause any Ergonomical issues / impact ( Man/Machine/Material )"
    ]
    
    # Default data for the form
    default_data = {
        'title': 'Window installation - Manual Lifting',
        'change_category': 'Process & Methods Change',
        'change_type': 'Temporary',
        'change_impact': 'Safety',
        'additional_comments': """1 Window lifting jig clearance stopped due to window breakage incident
2 Manual lifting until root cause and actions aligned with CFT
3 Gloves, Safety goggles to be mandatory for manual lifting
4 Foam to be kept on platform as required to avoid accidental breakage of window - temporary""",
        'control_measures': 'All Control measures to be in place before handing over it to the user'
    }
    
    return render_template('new_moc.html', 
                         user=user,
                         checkpoints=checkpoints,
                         default_data=default_data)

@app.route('/moc/<int:moc_id>/submit')
@login_required
def submit_moc(moc_id):
    user = get_current_user()
    moc = MOC.query.get_or_404(moc_id)
    
    if moc.submitted_by != user.id and user.role != 'admin':
        flash('You can only submit your own MOCs', 'danger')
        return redirect(url_for('view_moc', moc_id=moc_id))
    
    moc.status = 'Submitted'
    moc.current_step = 1
    
    history = ApprovalHistory(
        moc_id=moc.id,
        user_id=user.id,
        action='Submitted',
        step=0,
        comments='MOC submitted for approval'
    )
    db.session.add(history)
    db.session.commit()
    
    # Send email to approver 1
    if moc.approver1_id:
        notify_approver(moc.id, 1, moc.approver1_id, 'Pending')
    
    notify_submitter(moc.id, 'Submitted')
    
    flash('MOC submitted for approval! Email sent to approver.', 'success')
    return redirect(url_for('view_moc', moc_id=moc.id))

@app.route('/moc/<int:moc_id>/approve', methods=['GET', 'POST'])
@login_required
def approve_moc(moc_id):
    user = get_current_user()
    if user.role == 'employee':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    moc = MOC.query.get_or_404(moc_id)
    
    user_step = None
    if user.id == moc.approver1_id and moc.approver1_status == 'Pending':
        user_step = 1
    elif user.id == moc.approver2_id and moc.approver2_status == 'Pending':
        user_step = 2
    elif user.id == moc.approver3_id and moc.approver3_status == 'Pending':
        user_step = 3
    elif user.id == moc.approver4_id and moc.approver4_status == 'Pending':
        user_step = 4
    elif user.id == moc.approver5_id and moc.approver5_status == 'Pending':
        user_step = 5
    elif user.id == moc.approver6_id and moc.approver6_status == 'Pending':
        user_step = 6
    
    if not user_step and user.role != 'admin':
        flash('This MOC is not pending your approval', 'warning')
        return redirect(url_for('view_moc', moc_id=moc_id))
    
    if request.method == 'POST':
        action = request.form.get('action')
        comments = request.form.get('comments', '')
        
        now = datetime.now(timezone.utc)
        if user_step == 1:
            moc.approver1_status = 'Approved' if action == 'approve' else 'Rejected'
            moc.approver1_date = now
            moc.approver1_comments = comments
            if action == 'approve':
                moc.current_step = 2
            else:
                moc.status = 'Rejected'
                moc.current_step = 0
                
        elif user_step == 2:
            moc.approver2_status = 'Approved' if action == 'approve' else 'Rejected'
            moc.approver2_date = now
            moc.approver2_comments = comments
            if action == 'approve':
                moc.current_step = 3
            else:
                moc.status = 'Rejected'
                moc.current_step = 0
                
        elif user_step == 3:
            moc.approver3_status = 'Approved' if action == 'approve' else 'Rejected'
            moc.approver3_date = now
            moc.approver3_comments = comments
            if action == 'approve':
                moc.current_step = 4
            else:
                moc.status = 'Rejected'
                moc.current_step = 0
                
        elif user_step == 4:
            moc.approver4_status = 'Approved' if action == 'approve' else 'Rejected'
            moc.approver4_date = now
            moc.approver4_comments = comments
            if action == 'approve':
                moc.current_step = 5
            else:
                moc.status = 'Rejected'
                moc.current_step = 0
                
        elif user_step == 5:
            moc.approver5_status = 'Approved' if action == 'approve' else 'Rejected'
            moc.approver5_date = now
            moc.approver5_comments = comments
            if action == 'approve':
                moc.current_step = 6
            else:
                moc.status = 'Rejected'
                moc.current_step = 0
                
        elif user_step == 6:
            moc.approver6_status = 'Approved' if action == 'approve' else 'Rejected'
            moc.approver6_date = now
            moc.approver6_comments = comments
            if action == 'approve':
                moc.status = 'Approved'
                moc.current_step = 7
            else:
                moc.status = 'Rejected'
                moc.current_step = 0
        
        history = ApprovalHistory(
            moc_id=moc.id,
            user_id=user.id,
            action='Approved' if action == 'approve' else 'Rejected',
            step=user_step,
            comments=comments
        )
        
        db.session.add(history)
        db.session.commit()
        
        if action == 'approve':
            # Notify next approver
            next_step = user_step + 1
            if next_step <= 6:
                next_approver_id = getattr(moc, f'approver{next_step}_id')
                if next_approver_id:
                    notify_approver(moc.id, next_step, next_approver_id, 'Pending')
        
        action_text = 'approved' if action == 'approve' else 'rejected'
        flash(f'MOC {action_text} at step {user_step}!', 'success')
        return redirect(url_for('view_moc', moc_id=moc_id))
    
    return render_template('approve_moc.html',
                         user=user,
                         moc=moc,
                         user_step=user_step)

@app.route('/moc/list')
@login_required
def list_moc():
    user = get_current_user()
    
    if user.role == 'admin':
        mocs = MOC.query.order_by(MOC.created_at.desc()).all()
    elif user.role.startswith('approver'):
        mocs = MOC.query.filter(
            (MOC.approver1_id == user.id) |
            (MOC.approver2_id == user.id) |
            (MOC.approver3_id == user.id) |
            (MOC.approver4_id == user.id) |
            (MOC.approver5_id == user.id) |
            (MOC.approver6_id == user.id) |
            (MOC.submitted_by == user.id)
        ).order_by(MOC.created_at.desc()).all()
    else:
        mocs = MOC.query.filter_by(submitted_by=user.id).order_by(MOC.created_at.desc()).all()
    
    return render_template('list_moc.html', user=user, mocs=mocs)

@app.route('/moc/<int:moc_id>')
@login_required
def view_moc(moc_id):
    user = get_current_user()
    moc = MOC.query.get_or_404(moc_id)
    
    if not (user.role == 'admin' or 
            moc.submitted_by == user.id or
            moc.approver1_id == user.id or
            moc.approver2_id == user.id or
            moc.approver3_id == user.id or
            moc.approver4_id == user.id or
            moc.approver5_id == user.id or
            moc.approver6_id == user.id):
        flash('You do not have permission to view this MOC', 'danger')
        return redirect(url_for('list_moc'))
    
    checkpoints_data = {}
    if moc.checkpoints:
        try:
            checkpoints_data = json.loads(moc.checkpoints)
        except:
            pass
    
    history = ApprovalHistory.query.filter_by(moc_id=moc_id).order_by(ApprovalHistory.created_at).all()
    
    # Calculate hours since last action for escalation tracking
    hours_pending = 0.0
    if moc.status == 'Submitted' and moc.current_step > 0:
        now = datetime.now(timezone.utc)
        last_action_date = None
        
        if moc.current_step == 1:
            # Step 1 starts when MOC is submitted.
            submitted_event = ApprovalHistory.query.filter_by(moc_id=moc.id, action='Submitted').first()
            last_action_date = submitted_event.created_at if submitted_event else moc.created_at
        else:
            # Step N starts when Step N-1 was approved
            prev_step = moc.current_step - 1
            last_action_date = getattr(moc, f'approver{prev_step}_date')
            
        if last_action_date:
            if last_action_date.tzinfo is None:
                last_action_date = last_action_date.replace(tzinfo=timezone.utc)
            hours_pending = round((now - last_action_date).total_seconds() / 3600, 1)

    return render_template(
        "view_moc.html",
        moc=moc,
        user=user,
        history=history,
        checkpoints_data=checkpoints_data,
        hours_pending=hours_pending
    )

@app.route('/moc/<int:moc_id>/delete')
@login_required
def delete_moc(moc_id):
    user = get_current_user()
    moc = MOC.query.get_or_404(moc_id)
    
    # Check permissions: Only Admin or the person who submitted it can delete
    if not (user.role == 'admin' or moc.submitted_by == user.id):
        flash('You do not have permission to delete this MOC', 'danger')
        return redirect(url_for('list_moc'))
    
    try:
        # First delete associated history to avoid foreign key constraints issues
        ApprovalHistory.query.filter_by(moc_id=moc.id).delete()
        
        # Delete the MOC
        db.session.delete(moc)
        db.session.commit()
        
        flash(f'MOC {moc.moc_number} has been deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting MOC: {str(e)}', 'danger')
        
    return redirect(url_for('list_moc'))


@app.route('/workflow/status')
@login_required
def workflow_status():
    user = get_current_user()
    
    if user.role == 'admin':
        active_mocs = MOC.query.filter(MOC.status.in_(['Submitted'])).all()
    elif user.role.startswith('approver'):
        active_mocs = MOC.query.filter(
            ((MOC.approver1_id == user.id) & (MOC.approver1_status == 'Pending')) |
            ((MOC.approver2_id == user.id) & (MOC.approver2_status == 'Pending')) |
            ((MOC.approver3_id == user.id) & (MOC.approver3_status == 'Pending')) |
            ((MOC.approver4_id == user.id) & (MOC.approver4_status == 'Pending')) |
            ((MOC.approver5_id == user.id) & (MOC.approver5_status == 'Pending')) |
            ((MOC.approver6_id == user.id) & (MOC.approver6_status == 'Pending'))
        ).all()
    else:
        active_mocs = MOC.query.filter_by(submitted_by=user.id, status='Submitted').all()
    
    return render_template('workflow_status.html',
                         user=user,
                         active_mocs=active_mocs)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_panel():
    user = get_current_user()
    
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        name = request.form.get('name')
        email = request.form.get('email')
        department = request.form.get('department')
        position = request.form.get('position')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # Check if username or employee_id already exists
        if User.query.filter((User.username == username) | (User.employee_id == employee_id)).first():
            flash('Username or Employee ID already exists!', 'danger')
        else:
            new_user = User(
                employee_id=employee_id,
                name=name,
                email=email,
                department=department,
                position=position,
                username=username,
                password_hash=generate_password_hash(password),
                role=role
            )
            try:
                db.session.add(new_user)
                db.session.commit()
                flash(f'Successfully added {name} as {role}! Credentials: Username: {username}, Password: {password}', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding approver: {str(e)}', 'danger')
        
        return redirect(url_for('admin_panel'))
    
    # Get all users who are not regular employees (approvers and admins)
    approvers = User.query.filter(User.role != 'employee').all()
    
    return render_template('admin.html', 
                         user=user, 
                         approvers=approvers)

@app.route('/admin/user/<int:user_id>/delete')
@login_required
@role_required('admin')
def delete_user(user_id):
    if user_id == session['user_id']:
        flash('You cannot delete your own admin account!', 'danger')
        return redirect(url_for('admin_panel'))
    
    user = User.query.get_or_404(user_id)
    try:
        # Before deleting user, check if they are assigned to any MOCs
        # To avoid complex cascades, we'll just deactivate them or warn
        # For this request, we'll proceed with deletion but handle history
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.name} has been removed.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing user: {str(e)}', 'danger')
        
    return redirect(url_for('admin_panel'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

def get_admin_emails():
    """Get all administrator emails from the database"""
    admins = User.query.filter_by(role='admin').all()
    return [admin.email for admin in admins if admin.email]

def send_email(to_emails, subject, body, html_body=None):
    """Send email notification to one or more recipients"""
    if isinstance(to_emails, str):
        recipients = [to_emails]
    else:
        recipients = to_emails

    msg = Message(
        subject=subject,
        recipients=recipients,
        body=body,
        html=html_body
    )
    try:
        mail.send(msg)
        print(f"✓ Email sent to {recipients}")
        return True
    except Exception as e:
        print(f"✗ Email failed: {e}")
        return False

def get_user_email(user_id):
    """Get user email"""
    user = User.query.get(user_id)
    return user.email if user and user.email else None

def notify_approver(moc_id, approver_step, approver_id, action='Pending'):
    """Send notification to specific approver"""
    moc = MOC.query.get(moc_id)
    approver = User.query.get(approver_id)
    
    if not approver or not approver.email:
        return False
    
    subject = f"MOC {moc.moc_number} - {action} for Approval"
    body = f"""
MOC #{moc.moc_number} - {moc.title}

Status: {action} - Step {approver_step}
Change Category: {moc.change_category}
Submitted by: {moc.submitter.name}

Please review: http://localhost:5000/moc/{moc_id}

Thank you,
MOC System
    """
    
    html_body = f"""
    <h3>MOC #{moc.moc_number} - {moc.title}</h3>
    <p><strong>Status:</strong> {action} - Step {approver_step}</p>
    <p><strong>Change Category:</strong> {moc.change_category}</p>
    <p><strong>Submitted by:</strong> {moc.submitter.name}</p>
    <p><a href="http://localhost:5000/moc/{moc_id}" style="background:#007bff;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">Review MOC</a></p>
    """
    
    # Get all administrators
    admin_emails = get_admin_emails()
    recipients = [approver.email] + admin_emails
    # Remove duplicates but keep order
    unique_recipients = []
    for email in recipients:
        if email not in unique_recipients:
            unique_recipients.append(email)

    return send_email(unique_recipients, subject, body, html_body)

def notify_submitter(moc_id, status):
    """Notify submitter of status change"""
    moc = MOC.query.get(moc_id)
    submitter_email = get_user_email(moc.submitted_by)
    
    if not submitter_email:
        return False
    
    subject = f"MOC {moc.moc_number} - Status Updated: {status}"
    body = f"MOC #{moc.moc_number} status changed to {status}. Check dashboard."
    
    # Also notify admins
    admin_emails = get_admin_emails()
    recipients = [submitter_email] + admin_emails
    # Remove duplicates
    unique_recipients = list(set(recipients))
    
    return send_email(unique_recipients, subject, body)

def check_escalations():
    """Check for pending approvals > 3 hours and escalate"""
    three_hours_ago = datetime.now(timezone.utc) - timedelta(hours=3)
    
    # Find MOCs needing escalation
    escalations = MOC.query.filter(
        MOC.status == 'Submitted',
        MOC.current_step > 0
    ).all()
    
    # Fetch admin/system user for history
    admin_user = User.query.filter_by(role='admin').first()
    system_user_id = admin_user.id if admin_user else 1
    
    for moc in escalations:
        print(f"Checking escalation for MOC ID: {moc.id}, Step: {moc.current_step}")
        # Determine the "start time" of the current task
        task_start_time = None
        
        if moc.current_step == 1:
            # Step 1 starts when MOC is submitted (or updated to Submitted status)
            task_start_time = moc.updated_at
        elif moc.current_step > 1:
            # Step N starts when Step N-1 was approved
            prev_step = moc.current_step - 1
            prev_approver_date = getattr(moc, f'approver{prev_step}_date')
            task_start_time = prev_approver_date

        if task_start_time:
            # Ensure timezone awareness
            if task_start_time.tzinfo is None:
                task_start_time = task_start_time.replace(tzinfo=timezone.utc)

            if task_start_time < three_hours_ago:
                # Time to escalate!
                next_step = moc.current_step + 1

                if next_step <= 6:
                    # Mark current step as Timeout (or Skipped/Escalated)
                    current_status_field = f'approver{moc.current_step}_status'
                    setattr(moc, current_status_field, 'Timeout')

                    # Move to next step
                    moc.current_step = next_step
                    next_status_field = f'approver{next_step}_status'
                    setattr(moc, next_status_field, 'Pending')

                    # Record history
                    history = ApprovalHistory(
                        moc=moc,  # Use object
                        user_id=system_user_id,
                        action='Escalated - Timeout',
                        step=moc.current_step - 1, # Action happened on the timed-out step
                        comments=f'Approver {moc.current_step - 1} timeout (>3 hrs) - Auto-escalated to Step {next_step}'
                    )
                    db.session.add(history)

                # Notify next approver
                next_approver_id = getattr(moc, f'approver{next_step}_id')
                if next_approver_id:
                    notify_approver(moc.id, next_step, next_approver_id, 'URGENT - Escalated')

                # Notify the person who timed out (optional but good practice)
                timeout_approver_id = getattr(moc, f'approver{moc.current_step - 1}_id')
                if timeout_approver_id:
                     notify_approver(moc.id, moc.current_step - 1, timeout_approver_id, 'Timeout - Escalated')
                
                print(f"✓ Queued auto-escalation for MOC {moc.moc_number} to step {next_step}")

    # Commit all changes at once
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error during escalation commit: {e}")
    
    # Release connection back to pool
    db.session.remove()

def run_escalation_checker():
    import time
    with app.app_context():
        while True:
            check_escalations()
            time.sleep(300)  # 30 minutes

# Start background thread
def start_escalation_service():
    """Start the background escalation thread"""
    import threading
    escalation_thread = threading.Thread(target=run_escalation_checker, daemon=True)
    escalation_thread.start()
    return escalation_thread

# ========== INITIALIZE DATABASE ==========


def init_database():
    with app.app_context():
        db.create_all()
        
        default_users = [
            {
                'employee_id': 'ADM001', 
                'name': 'System Administrator', 
                'department': 'IT',
                'position': 'Admin',
                'email': 'anbukkarasan2004@gmail.com', 
                'username': 'admin', 
                'password': 'admin123', 
                'role': 'admin'
            },
            {
                'employee_id': 'EHS001', 
                'name': 'EHS Manager', 
                'department': 'EHS',
                'position': 'EHS Manager',
                'email': 'baluanbukkarasan@gmail.com', 
                'username': 'ehs', 
                'password': 'ehs123', 
                'role': 'approver1'
            },
            {
                'employee_id': 'ENG001', 
                'name': 'Engineering Head', 
                'department': 'Engineering',
                'position': 'Engineering Manager',
                'email': 'banbu9318@gmail.com', 
                'username': 'engineer', 
                'password': 'eng123', 
                'role': 'approver2'
            },
            {
                'employee_id': 'QLT001', 
                'name': 'Quality Head', 
                'department': 'Quality',
                'position': 'Quality Manager',
                'email': 'solaitamil28@gmail.com', 
                'username': 'quality', 
                'password': 'qlt123', 
                'role': 'approver3'
            },
            {
                'employee_id': 'MGT001', 
                'name': 'Plant Manager', 
                'department': 'Management',
                'position': 'Plant Manager',
                'email': 'manager@example.com', 
                'username': 'manager', 
                'password': 'mgr123', 
                'role': 'approver4'
            },
            {
                'employee_id': 'FIN001', 
                'name': 'Finance Head', 
                'department': 'Finance',
                'position': 'Finance Manager',
                'email': 'finance@example.com', 
                'username': 'finance', 
                'password': 'fin123', 
                'role': 'approver5'
            },
            {
                'employee_id': 'OPS001', 
                'name': 'Operations Head', 
                'department': 'Operations',
                'position': 'Operations Manager',
                'email': 'operations@example.com', 
                'username': 'ops', 
                'password': 'ops123', 
                'role': 'approver6'
            },
            {
                'employee_id': 'EMP001', 
                'name': 'John Doe', 
                'department': 'Production',
                'position': 'Operator',
                'email': 'employee@example.com',
                'username': 'employee', 
                'password': 'emp123', 
                'role': 'employee'
            }
        ]
        
        for user_data in default_users:
            if not User.query.filter_by(username=user_data['username']).first():
                user = User(
                    employee_id=user_data['employee_id'],
                    name=user_data['name'],
                    department=user_data['department'],
                    position=user_data['position'],
                    email=user_data['email'],
                    username=user_data['username'],
                    password_hash=generate_password_hash(user_data['password']),
                    role=user_data['role']
                )
                db.session.add(user)
        
        db.session.commit()
        print("✓ Database initialized with default users")

if __name__ == '__main__':
    init_database()
 
    #start escalation checher
    print("ALSTOM MOC Workflow with Email & Auto-Escalation")
    print("=" * 60)
    print("Email configured - check your SMTP settings")
    print("Auto-escalation running every 30 mins")
    print("ALSTOM MOC Workflow System Started")
    print("=" * 60)
    print("URL: http://localhost:5000")
    print("Login with: admin / admin123")
    print("=" * 60)
    
    # Start escalation service only when running app directly
    start_escalation_service()
    
    app.run(debug=True, port=5000)
