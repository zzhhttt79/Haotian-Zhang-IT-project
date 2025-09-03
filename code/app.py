from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os

import requests
from datetime import datetime, timedelta, timezone
from statistics import mean
from models import db, User, Appliance
from forms import RegisterForm, LoginForm, ApplianceForm
from config import Config

from dotenv import load_dotenv
load_dotenv()
def utcnow():
    # 返回时区感知的 UTC 时间，避免 datetime.utcnow() 弃用警告
    return datetime.now(timezone.utc).replace(microsecond=0)

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def index():
    return render_template('homepage.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'error')
        else:
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registered successfully!')
            return redirect(url_for('register_success'))
    return render_template('register.html', form=form)

@app.route('/register_success')
def register_success():
    return render_template('register_success.html')

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

@app.route('/api/dashboard-data')
@login_required
def dashboard_data():
    # 1) 当前强度
    try:
        resp1 = requests.get('https://api.carbonintensity.org.uk/intensity')
        ci = resp1.json()['data'][0]['intensity']['actual']
    except:
        ci = None

    # 2) 24h 预测
    now = utcnow()
    ft = now.strftime('%Y-%m-%dT%H:00Z')
    tt = (now + timedelta(hours=24)).strftime('%Y-%m-%dT%H:00Z')
    try:
        resp2 = requests.get(f'https://api.carbonintensity.org.uk/intensity/{ft}/{tt}')
        forecast = resp2.json()['data']
        labels = [e['from'][11:16] for e in forecast]
        values = [e['intensity']['forecast'] for e in forecast]
    except:
        labels, values = [], []

    # 3) 用户电器
    apps = Appliance.query.filter_by(user_id=current_user.id).all()
    appliances = [{'name': a.name, 'wattage': a.wattage} for a in apps]

    return jsonify({
        'intensity': ci,
        'labels': labels,
        'values': values,
        'appliances': appliances
    })

@app.route('/api/ci/forecast48h')
@login_required
def ci_forecast_48h():
    # 中文注释：未来 48 小时预测；只返回有 forecast 的点，并转成数字
    start = utcnow().replace(minute=0, second=0)
    end   = start + timedelta(hours=48)
    url = (
        "https://api.carbonintensity.org.uk/intensity/"
        f"{start.strftime('%Y-%m-%dT%H:00Z')}/{end.strftime('%Y-%m-%dT%H:00Z')}"
    )
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        items = r.json().get('data', [])

        labels, values = [], []
        for it in items:
            fc = it.get('intensity', {}).get('forecast')
            if fc is None:
                continue  # 跳过空值，避免前端画不出线
            # 标签显示 "MM-DD HH:MM" 更清晰
            lab = it['from'][5:16].replace('T', ' ')
            labels.append(lab)
            values.append(int(fc))

        return jsonify({'labels': labels, 'values': values})
    except Exception as e:
        print('forecast48h error:', e)
        return jsonify({'labels': [], 'values': []}), 500


@app.route('/api/ci/history')
@login_required
def ci_history():
    # 中文注释：历史数据，默认 2 天（≈48 小时）
    days = int(request.args.get('days', 2))
    end   = utcnow().replace(minute=0, second=0)
    start = end - timedelta(days=days)
    url = (
        "https://api.carbonintensity.org.uk/intensity/"
        f"{start.strftime('%Y-%m-%dT%H:00Z')}/{end.strftime('%Y-%m-%dT%H:00Z')}"
    )
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        items = r.json().get('data', [])

        labels, actuals, forecasts = [], [], []
        for it in items:
            a = it.get('intensity', {}).get('actual')
            f = it.get('intensity', {}).get('forecast')
            # 两个都空就跳过，避免整行无意义
            if a is None and f is None:
                continue
            lab = it['from'][5:16].replace('T', ' ')
            labels.append(lab)
            # 保留 None 作为“折线断点”，其它转为数字
            actuals.append(None if a is None else int(a))
            forecasts.append(None if f is None else int(f))

        return jsonify({'labels': labels, 'actuals': actuals, 'forecasts': forecasts})
    except Exception as e:
        print('history error:', e)
        return jsonify({'labels': [], 'actuals': [], 'forecasts': []}), 500


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/carbon-data')
def carbon_data():
    now = utcnow()
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
@login_required
def smart_recommendation():
    print("smart_recommendation FIX v3 is running")
    # 1) 读取当前用户设备
    appliances = Appliance.query.filter_by(user_id=current_user.id).all()
    if not appliances:
        return jsonify(recommendations=[])

    # 2) 拉取未来 24h 预测（URL 显式带 Z；整点对齐）
    now = utcnow().replace(minute=0, second=0, microsecond=0)
    to = now + timedelta(hours=24)
    ci_url = (
        f"https://api.carbonintensity.org.uk/intensity/"
        f"{now.strftime('%Y-%m-%dT%H:00Z')}/{to.strftime('%Y-%m-%dT%H:00Z')}"
    )

    try:
        resp = requests.get(ci_url, timeout=10)
        resp.raise_for_status()
        entries = resp.json().get('data', [])
    except Exception as e:
        # PythonAnywhere 免费版可能拦外网；兜底避免 500
        print("smart_recommendation fetch error:", e)
        return jsonify(recommendations=[])

    # 3) 解析 '...Z' 时间为 fromisoformat 可识别
    def _parse_ci_time(s: str):
        if isinstance(s, str) and s.endswith('Z'):
            s = s[:-1] + '+00:00'
        return datetime.fromisoformat(s)

    ci_series = []
    for e in entries:
        frm = e.get('from')
        intensity = e.get('intensity') or {}
        fc = intensity.get('forecast')
        if not frm or fc is None:
            continue
        try:
            dt = _parse_ci_time(frm)
        except Exception as err:
            print("smart_recommendation parse err:", err, frm)
            continue
        ci_series.append((dt, fc))

    if len(ci_series) < 2:
        return jsonify(recommendations=[])

    # 4) 为每个设备找 Top-3 最低平均碳强度 1 小时时窗
    window_size = 2  # 两个 30 分钟段 = 1 小时
    recommendations = []

    for app_ in appliances:
        windows = []
        for i in range(len(ci_series) - window_size + 1):
            slice_ = ci_series[i:i + window_size]
            avg_ci = mean(v for _, v in slice_)
            start = slice_[0][0]
            end = start + timedelta(minutes=30 * window_size)
            windows.append({
                "time": f"{start.strftime('%H:%M')}–{end.strftime('%H:%M')}",
                "avg_ci": round(avg_ci, 1)
            })

        best3 = sorted(windows, key=lambda w: w["avg_ci"])[:3]
        note = (
            f"Recommended period：{best3[0]['time']}，avg carbon intensity {best3[0]['avg_ci']} gCO₂/kWh。"
            if best3 else "No window available."
        )
        recommendations.append({"name": app_.name, "windows": best3, "note": note})

    return jsonify(recommendations=recommendations)



@app.route('/appliances', methods=['GET', 'POST'])
@login_required
def appliances():
    form = ApplianceForm()
    if form.validate_on_submit():
        appliance = Appliance(
            name=form.name.data,
            category=form.category.data,
            wattage=form.wattage.data,
            user_id=current_user.id
        )
        db.session.add(appliance)
        db.session.commit()
        flash('Appliance added successfully!')
        return redirect(url_for('appliances'))

    user_appliances = Appliance.query.filter_by(user_id=current_user.id).all()
    total_appliances = len(user_appliances)
    total_wattage = sum(a.wattage for a in user_appliances)
    categories = len({a.category for a in user_appliances})
    return render_template(
        'appliances.html',
        form=form,
        appliances=user_appliances,
        total_appliances=total_appliances,
        total_wattage=total_wattage,
        categories=categories
    )

@app.route('/delete-appliance/<int:appliance_id>', methods=['POST'])
@login_required
def delete_appliance(appliance_id):
    appliance = db.get_or_404(Appliance, appliance_id)
    if appliance.user_id != current_user.id:
        flash("Unauthorized access.")
        return redirect(url_for('appliances'))

    db.session.delete(appliance)
    db.session.commit()
    flash("Appliance deleted.")
    return redirect(url_for('appliances'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)