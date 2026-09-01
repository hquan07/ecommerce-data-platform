import pytest

def test_app_initialization():
    try:
        from dashboard.app import app
        assert app.layout is not None
        assert app.title == "E-commerce Dashboard"
    except Exception as e:
        pytest.fail(f"Dashboard app failed to import or initialize: {e}")
