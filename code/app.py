from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from models import db, User
from forms import RegisterForm, LoginForm
import os

import requests
from flask import jsonify
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'database.db')

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('homepage.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists')
        else:
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registered successfully!')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/carbon-data')
def carbon_data():
    now = datetime.utcnow()
    from_time = now.strftime('%Y-%m-%dT%H:00Z')
    to_time = (now + timedelta(hours=24)).strftime('%Y-%m-%dT%H:00Z')
    url = f'https://api.carbonintensity.org.uk/intensity/{from_time}/{to_time}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()['data']
        labels = [entry['from'][11:16] for entry in data]
        values = [entry['intensity']['forecast'] for entry in data]
        return jsonify({'labels': labels, 'values': values})
    except Exception as e:
        print('Error fetching API:', e)
        return jsonify({'labels': [], 'values': []}), 500


@app.route('/current-intensity')
def current_intensity():
    url = 'https://api.carbonintensity.org.uk/intensity'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()['data'][0]
        intensity = data['intensity']['actual']
        datetime_value = data['from']
        return jsonify({'intensity': intensity, 'datetime': datetime_value})
    except Exception as e:
        print('Error fetching current intensity:', e)
        return jsonify({'intensity': None, 'datetime': None}), 500

@app.route('/smart-recommendation')
def smart_recommendation():
    url = 'https://api.carbonintensity.org.uk/intensity'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()['data'][0]
        intensity = data['intensity']['actual']

        if intensity < 100:
            recommendation = "Great time to use high-energy devices like EV charger or dryer."
        elif intensity < 150:
            recommendation = "Good time to run your washing machine or dishwasher."
        elif intensity < 200:
            recommendation = "Fair time to use small electronics or do light chores."
        else:
            recommendation = "Try to delay high energy tasks until carbon intensity drops."

        return jsonify({'recommendation': recommendation})
    except Exception as e:
        print('Error fetching recommendation:', e)
        return jsonify({'recommendation': "Unable to fetch recommendation."}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)