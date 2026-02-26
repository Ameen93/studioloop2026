from fastapi.testclient import TestClient


def _preflight(client: TestClient, origin: str) -> dict[str, str]:
    response = client.options(
        "/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code in (200, 400)
    return response.headers


def test_local_web_origins_allowed(client: TestClient) -> None:
    for origin in (
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
    ):
        headers = _preflight(client, origin)
        assert headers.get("access-control-allow-origin") == origin


def test_unknown_origin_not_allowed(client: TestClient) -> None:
    headers = _preflight(client, "http://localhost:5999")
    assert "access-control-allow-origin" not in headers
