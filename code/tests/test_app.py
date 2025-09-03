# 放在 test_app.py 顶部的 imports 之后
from datetime import datetime, timedelta

def _mk_ci_mock(monkeypatch, current_actual=100, start="2025-08-14T10:00:00",
                series=(80,70,60,50,40,90)):
    """Mock Carbon Intensity API：
    - /intensity 返回当前 actual
    - /intensity/{from}/{to} 返回给定 series（半小时粒度）
    """
    base = datetime.fromisoformat(start)

    class R:
        def __init__(self, data, status=200):
            self._data = data; self.status_code = status
        def json(self): return self._data
        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception("boom")

    def fake_get(url, *a, **k):
        if url.endswith("/intensity"):
            return R({"data":[{"from":start,"to":start,"intensity":{"actual":current_actual,"forecast":120}}]})
        if "/intensity/" in url:
            data = []
            for i, f in enumerate(series):
                frm = (base + timedelta(minutes=30*i)).isoformat()
                data.append({"from": frm, "to": frm, "intensity": {"forecast": f}})
            return R({"data": data})
        return R({"data": []})

    monkeypatch.setattr("requests.get", fake_get)

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

# --- 追加在文件末尾 ---
def test_recommendation_skip_missing_points(client, login, monkeypatch):
    """含 None 的窗口要被跳过，最佳应来自无缺失的片段"""
    _mk_ci_mock(monkeypatch, series=[80, None, 60, 50, 40, 90])
    client.post("/appliances", data={"name":"Washer","category":"Laundry","wattage":500}, follow_redirects=True)
    resp = client.get("/smart-recommendation")
    recs = resp.get_json()["recommendations"]
    assert resp.status_code == 200 and len(recs) == 1
    # 期望最优均值为 45（50+40）/2，对应 11:30–12:30
    assert recs[0]["windows"][0]["avg_ci"] == 45.0
    assert recs[0]["windows"][0]["time"] == "11:30–12:30"

def test_recommendation_tie_break_by_time(client, login, monkeypatch):
    """并列均值时按开始时间更早者优先"""
    _mk_ci_mock(monkeypatch, series=[50,70,70,50])  # [50,70] 与 [70,50] 平均同为 60
    client.post("/appliances", data={"name":"Dishwasher","category":"Kitchen","wattage":1800}, follow_redirects=True)
    resp = client.get("/smart-recommendation")
    top = resp.get_json()["recommendations"][0]["windows"][0]
    assert top["avg_ci"] == 60.0
    assert top["time"] == "10:00–11:00"   # 起点 10:00Z → 早者优先

def test_recommendation_insufficient_points(client, login, monkeypatch):
    """少于 1 小时（k=2）不足形成窗口时，应返回空推荐列表"""
    _mk_ci_mock(monkeypatch, series=[80])  # 只有一个半小时点

    # 保证有设备，但根据当前实现这不影响早退逻辑
    client.post(
        "/appliances",
        data={"name": "Dryer", "category": "Laundry", "wattage": 2200},
        follow_redirects=True,
    )

    resp = client.get("/smart-recommendation")
    assert resp.status_code == 200
    recs = resp.get_json()["recommendations"]
    assert recs == []   # 端点在点数不足时整体返回空列表


def test_recommendation_requires_login_redirect(client, monkeypatch):
    """未登录访问受保护接口，应重定向到 /login"""
    _mk_ci_mock(monkeypatch)  # 数据不重要，只验证重定向
    resp = client.get("/smart-recommendation")
    assert resp.status_code in (301, 302)
    assert "/login" in resp.headers.get("Location", "")

def test_recommendation_api_failure_graceful(client, login, monkeypatch):
    """外部 API 异常时，接口应优雅兜底返回空推荐而非 500"""
    import requests
    def boom(*a, **k): raise requests.exceptions.RequestException("boom")
    monkeypatch.setattr("requests.get", lambda *a, **k: boom())
    client.post("/appliances", data={"name":"Kettle","category":"Kitchen","wattage":1500}, follow_redirects=True)
    resp = client.get("/smart-recommendation")
    assert resp.status_code == 200
    assert resp.get_json()["recommendations"] == []
