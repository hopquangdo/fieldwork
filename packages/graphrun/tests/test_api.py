import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from graphrun.api import create_app

client = TestClient(create_app())


def test_health_and_features():
    assert client.get("/health").json() == {"ok": True}
    names = [f["name"] for f in client.get("/features").json()]
    assert "photo-sort" in names


def test_run_unknown_feature_404():
    r = client.post("/features/nope/run", json={"input": ".", "output": "."})
    assert r.status_code == 404


def test_job_lifecycle(tmp_path):
    (tmp_path / "1.a").mkdir(parents=True)
    _img = pytest.importorskip("PIL.Image")
    import io

    buf = io.BytesIO()
    _img.new("RGB", (2, 2), "white").save(buf, format="JPEG")
    (tmp_path / "1.a" / "x.jpg").write_bytes(buf.getvalue())
    (tmp_path / "DataX ok").mkdir()
    (tmp_path / "DataX ok" / "TABLEBia.txt").write_text("Loại cột: Dây co\n", encoding="utf-8")

    r = client.post(
        "/features/photo-sort/run?wait=true",
        json={"input": str(tmp_path), "output": str(tmp_path / "out"),
              "apply": False, "overrides": {"vision_assist": False}},
    )
    body = r.json()
    assert r.status_code == 200 and body["status"] in ("done", "error")
    if body["status"] == "done":
        sec = body["report"]["sections"]
        assert sec["images_before"] == sec["images_after"]
        assert body["report"]["aborted"] is False
    assert client.get(f"/jobs/{body['id']}").json()["id"] == body["id"]
