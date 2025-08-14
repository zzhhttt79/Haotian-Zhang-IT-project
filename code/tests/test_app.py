# tests/test_app.py
def test_homepage(client):
    resp = client.get("/")
    assert resp.status_code == 200
def test_dashboard_requires_login(client):
    resp = client.get("/dashboard")
    assert resp.status_code in (301, 302)
    assert "/login" in resp.headers.get("Location","")

def test_login_logout_flow(client, user):
    resp = client.post("/login", data={"username":"alice","password":"password123"}, follow_redirects=True)
    assert resp.status_code == 200
    assert client.get("/dashboard").status_code == 200
    assert client.get("/logout", follow_redirects=True).status_code == 200

def test_dashboard_data_logged_in(client, login, mock_ci):
    resp = client.get("/api/dashboard-data")
    j = resp.get_json()
    assert resp.status_code == 200
    assert j["intensity"] == 100
    assert len(j["labels"]) == 6 and len(j["values"]) == 6
    assert j["appliances"] == []

def test_carbon_data_endpoint(client, mock_ci):
    resp = client.get("/carbon-data")
    j = resp.get_json()
    assert resp.status_code == 200
    assert len(j["labels"]) == 6 and len(j["values"]) == 6

def test_current_intensity_endpoint(client, mock_ci):
    resp = client.get("/current-intensity")
    j = resp.get_json()
    assert resp.status_code == 200
    assert j["intensity"] == 100
    assert j["datetime"].startswith("2025-08-14T10:00:00")

from models import Appliance, db, User

def test_add_and_delete_appliance(client, login):
    # 新增
    resp = client.post("/appliances",
                       data={"name":"Microwave","category":"Kitchen","wattage":1200},
                       follow_redirects=True)
    assert resp.status_code == 200
    obj = Appliance.query.filter_by(name="Microwave").first()
    assert obj is not None
    # 删除
    del_resp = client.post(f"/delete-appliance/{obj.id}", follow_redirects=True)
    assert del_resp.status_code == 200
    assert Appliance.query.get(obj.id) is None

def test_smart_recommendation(client, login, mock_ci):
    client.post("/appliances", data={"name":"Dishwasher","category":"Kitchen","wattage":1800}, follow_redirects=True)
    client.post("/appliances", data={"name":"Dryer","category":"Laundry","wattage":2200}, follow_redirects=True)
    resp = client.get("/smart-recommendation")
    recs = resp.get_json()["recommendations"]
    assert resp.status_code == 200 and len(recs) >= 1
    for rec in recs:
        assert len(rec["windows"]) == 3
        assert rec["windows"][0]["time"] == "11:30–12:30"
        assert rec["windows"][0]["avg_ci"] == 45.0

def test_preferences_save(client, login):
    resp = client.post("/preferences",
                       data={"weight_ci":2,"weight_price":1,"weight_flex":1},
                       follow_redirects=True)
    assert resp.status_code == 200
    u = User.query.filter_by(username="alice").first()
    total = (u.weight_ci or 0)+(u.weight_price or 0)+(u.weight_flex or 0)
    assert abs(total-1.0) < 1e-6
    assert abs(u.weight_ci-0.5) < 1e-6
    assert abs(u.weight_price-0.25) < 1e-6
    assert abs(u.weight_flex-0.25) < 1e-6
# 设备越权删除（确保权限逻辑没问题）
def test_delete_appliance_unauthorized(client, app):
    from models import db, User, Appliance
    u1 = User(username="alice2"); u1.set_password("pw")
    u2 = User(username="bob");    u2.set_password("pw")
    db.session.add_all([u1, u2]); db.session.commit()
    owned = Appliance(name="Washer", category="Laundry", wattage=500, user_id=u2.id)
    db.session.add(owned); db.session.commit()

    # 登录 alice2，试图删 bob 的设备
    client.post("/login", data={"username":"alice2","password":"pw"}, follow_redirects=True)
    resp = client.post(f"/delete-appliance/{owned.id}")
    assert resp.status_code in (301, 302)
    assert db.session.get(Appliance, owned.id) is not None

# 外部 API 异常分支（网络崩/服务挂）
def test_dashboard_data_api_error(client, login, monkeypatch):
    import requests
    def boom(*a, **k):
        raise requests.exceptions.RequestException("boom")
    monkeypatch.setattr("requests.get", lambda *a, **k: boom())

    resp = client.get("/api/dashboard-data")
    j = resp.get_json()
    # 你的视图里 try/except 已经兜底：强度/预测为空数组
    assert resp.status_code == 200
    assert j["intensity"] is None
    assert j["labels"] == []
    assert j["values"] == []
