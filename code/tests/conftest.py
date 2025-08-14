# tests/conftest.py
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # 兜底，确保能 import app/models

import pytest
from datetime import datetime, timedelta

from app import app as flask_app
from models import db, User, Appliance


@pytest.fixture()
def app():
    # 使用内存数据库，避免污染 instance/database.db
    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
        LOGIN_DISABLED=False,
    )
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def user(app):
    """创建一个测试用户：alice / password123"""
    u = User(username="alice")
    u.set_password("password123")
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture()
def login(client, user):
    """快捷登录为 alice"""
    client.post(
        "/login",
        data={"username": "alice", "password": "password123"},
        follow_redirects=True,
    )


@pytest.fixture()
def mock_ci(monkeypatch):
    """Mock 碳强度 API，测试离线可重复"""
    def fake_get(url, *args, **kwargs):
        class R:
            def __init__(self, data): self._data = data; self.status_code = 200
            def json(self): return self._data
            def raise_for_status(self): pass

        # 当前强度
        if url.endswith("/intensity"):
            return R({"data":[{
                "from":"2025-08-14T10:00:00",
                "to":"2025-08-14T10:30:00",
                "intensity":{"forecast":120,"actual":100}
            }]})

        # 未来 24 小时（6 个半小时槽，够覆盖你的窗口逻辑）
        if "/intensity/" in url:
            start = datetime(2025,8,14,10,0)
            series = [80,70,60,50,40,90]
            data=[]
            for i,f in enumerate(series):
                frm = start + timedelta(minutes=30*i)
                data.append({
                    "from": frm.isoformat(),
                    "to": (frm + timedelta(minutes=30)).isoformat(),
                    "intensity": {"forecast": f, "actual": None}
                })
            return R({"data": data})

        return R({"data": []})

    monkeypatch.setattr("requests.get", fake_get)
