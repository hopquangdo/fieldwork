from fastapi.testclient import TestClient

from bts_organizer.api import create_app

client = TestClient(create_app())


def test_scan_and_organize(station, tmp_path, monkeypatch):
    monkeypatch.setenv("BTS_NO_VISION", "1")
    workspace = station.parent

    r = client.post("/scan", json={"root": str(workspace)})
    assert r.status_code == 200
    body = r.json()
    assert body["stations"] and body["stations"][0]["name"] == station.name

    r = client.post("/organize", json={"root": str(station), "dry_run": True, "no_vision": True})
    assert r.status_code == 200
    rep = r.json()
    assert rep["images_before"] == rep["images_after"]
    assert "steps" in rep and "tree" in rep and rep["aborted"] is False
