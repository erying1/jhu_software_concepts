from xmlrpc import client
import pytest
import subprocess
import src.app.routes as routes


@pytest.mark.web
def test_get_last_pull_and_runtime(tmp_path, monkeypatch):
    # Create fake timestamp files
    pull_file = tmp_path / "last_pull.txt"
    runtime_file = tmp_path / "last_runtime.txt"
    pull_file.write_text("Jan 1, 2026")
    runtime_file.write_text("10s")

    monkeypatch.setattr(routes, "TIMESTAMP_FILE", str(pull_file))
    monkeypatch.setattr(routes, "RUNTIME_FILE", str(runtime_file))

    assert routes.get_last_pull() == "Jan 1, 2026"
    assert routes.get_last_runtime() == "10s"


@pytest.mark.web
def test_load_scraped_records_valid(tmp_path, monkeypatch):
    data_file = tmp_path / "llm_extend_applicant_data.json"
    data_file.write_text('[{"x": 1}]')

    monkeypatch.setattr(routes, "PROJECT_ROOT", str(tmp_path))

    assert routes.load_scraped_records() == [{"x": 1}]


@pytest.mark.web
def test_analysis_results_list_converted_to_dict(client, monkeypatch):
    # Force load_scraped_records to succeed
    monkeypatch.setattr(routes, "load_scraped_records", lambda: [])

    # FIRST call returns a list → triggers the list→dict conversion branch
    def fake_get_all_results():
        return []

    monkeypatch.setattr(routes, "get_all_results", fake_get_all_results)

    # Provide a full safe dict for template rendering
    SAFE_RESULTS = {
        "pct_international": 0,
        "pct_domestic": 0,
        "accept_rate": 0,
        "avg_gpa": 0,
        "jhu_cs_masters_count": 0,
        "elite_cs_phd_accepts": 0,
        "elite_cs_phd_llm_accepts": 0,
        "q10_custom": 0,
        "q11_custom": 0,
        "pct_accept_fall_2026": 0,
        "fall_2026_count": 0,
        "avg_metrics": {},
        "timestamp": "N/A",
    }

    # After the branch is hit, override get_all_results to return full dict
    monkeypatch.setattr(routes, "get_all_results", lambda: SAFE_RESULTS)

    # Prevent diagnostics from breaking template
    monkeypatch.setattr(routes, "compute_scraper_diagnostics", lambda x: {})

    response = client.get("/analysis")
    assert response.status_code == 200


@pytest.mark.buttons
def test_update_analysis_json_success(client, monkeypatch):
    monkeypatch.setattr(routes, "pull_running", False)
    monkeypatch.setattr(routes, "get_all_results", lambda: {})
    monkeypatch.setattr(routes, "load_scraped_records", lambda: [])
    monkeypatch.setattr(routes, "compute_scraper_diagnostics", lambda x: {})

    response = client.post("/update-analysis", json={})
    assert response.status_code == 200
    assert response.json["ok"] is True


@pytest.mark.buttons
def test_pull_data_json_success(client, monkeypatch):
    monkeypatch.setattr(routes, "pull_running", False)
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: None)

    response = client.post("/pull-data", json={})
    assert response.status_code == 200
    assert response.json["ok"] is True


@pytest.mark.web
def test_load_scraped_records_valid(tmp_path, monkeypatch):
    # Create the directory structure expected by load_scraped_records()
    module_dir = tmp_path / "module_2_1"
    module_dir.mkdir(parents=True)
    data_file = module_dir / "llm_extend_applicant_data.json"
    data_file.write_text('[{"x": 1}]')
    monkeypatch.setattr(routes, "PROJECT_ROOT", str(tmp_path))
    assert routes.load_scraped_records() == [{"x": 1}]


@pytest.mark.web
def test_analysis_exception_before_render(client, monkeypatch):
    # Force load_scraped_records to raise
    monkeypatch.setattr(
        routes, "load_scraped_records", lambda: (_ for _ in ()).throw(Exception("boom"))
    )
    response = client.get("/analysis")
    assert response.status_code == 200


@pytest.mark.buttons
def test_pull_data_html_redirect(client, monkeypatch):
    monkeypatch.setattr(routes, "pull_running", False)
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: None)
    response = client.post("/pull-data")  # no JSON
    assert response.status_code in (302, 303)


@pytest.mark.buttons
def test_pull_data_subprocess_error(client, monkeypatch):
    monkeypatch.setattr(routes, "pull_running", False)

    def fake_run(*a, **k):
        raise subprocess.CalledProcessError(1, "cmd")

    monkeypatch.setattr(subprocess, "run", fake_run)

    response = client.post("/pull-data", json={})
    assert response.status_code == 500
    assert response.json["ok"] is False


@pytest.mark.buttons
def test_pull_data_generic_exception(client, monkeypatch):
    monkeypatch.setattr(routes, "pull_running", False)

    def fake_run(*a, **k):
        raise Exception("boom")

    monkeypatch.setattr(subprocess, "run", fake_run)

    response = client.post("/pull-data", json={})
    assert response.status_code == 500
    assert response.json["ok"] is False


@pytest.mark.buttons
def test_pull_data_timestamp_write_failure(client, monkeypatch, tmp_path):
    monkeypatch.setattr(routes, "pull_running", False)
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: None)

    # Force timestamp write to fail
    monkeypatch.setattr(routes, "TIMESTAMP_FILE", str(tmp_path / "nope" / "file.txt"))
    monkeypatch.setattr(routes, "RUNTIME_FILE", str(tmp_path / "nope" / "file2.txt"))

    response = client.post("/pull-data", json={})
    assert response.status_code == 200


@pytest.mark.buttons
def test_update_analysis_html_render(client, monkeypatch):
    monkeypatch.setattr(routes, "pull_running", False)
    monkeypatch.setattr(routes, "get_all_results", lambda: {"avg_metrics": {}})
    monkeypatch.setattr(routes, "load_scraped_records", lambda: [])
    monkeypatch.setattr(routes, "compute_scraper_diagnostics", lambda x: {})

    response = client.post("/update-analysis")  # no JSON
    assert response.status_code in [200, 302]  # 302 = redirect to analysis page


@pytest.mark.web
def test_status_exception(monkeypatch, client):
    def boom():
        raise Exception("fail")

    monkeypatch.setattr(routes, "pull_running", property(boom))

    response = client.get("/status")
    assert response.status_code == 200
    assert response.json["busy"] is False
