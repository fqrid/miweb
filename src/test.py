from main import (
    Calculator,
    app,
    calculator,
    get_theme_context,
    is_dark_mode_enabled,
)


# --- 1. Pruebas Unitarias de la Calculadora (CI Reparado) ---
def test_sum():
    """Verifica compatibilidad con la firma original 'sum' y clase en minúscula."""
    calc = calculator()
    assert calc.sum(2, 2) == 4


def test_suma():
    """Verifica método suma en clase Calculator."""
    calc = Calculator()
    assert calc.suma(10, 5) == 15


def test_resta():
    """Verifica método resta en clase Calculator."""
    calc = Calculator()
    assert calc.resta(10, 4) == 6


# --- 2. Pruebas de Feature Toggle (Ticket 1 y Ticket 2) ---
def test_feature_flag_evaluation_states(monkeypatch):
    """Verifica que el Feature Toggle responda dinámicamente a los estados ON y OFF."""
    monkeypatch.setenv("DARK_MODE_ENABLED", "true")
    assert is_dark_mode_enabled() is True

    monkeypatch.setenv("DARK_MODE_ENABLED", "false")
    assert is_dark_mode_enabled() is False


def test_theme_context_when_flag_off(monkeypatch):
    """Ticket 1: Verifica que con flag OFF no se active tema oscuro."""
    monkeypatch.setenv("DARK_MODE_ENABLED", "false")
    context = get_theme_context()
    assert context["feature_flag_enabled"] is False
    assert context["dark_mode_active"] is False
    assert context["theme_class"] == "light-theme"
    assert context["data_theme"] == "light"


def test_theme_context_when_flag_on(monkeypatch):
    """Ticket 2: Verifica que con flag ON se informe el flag activo."""
    monkeypatch.setenv("DARK_MODE_ENABLED", "true")
    context = get_theme_context()
    assert context["feature_flag_enabled"] is True


# --- 3. Pruebas de la Aplicación Web y Renderizado Condicional del Botón ---
def test_healthz_endpoint():
    """Verifica el endpoint de salud requerido para Render (/healthz)."""
    client = app.test_client()
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "miweb-dashboard"


def test_index_renders_toggle_button_when_flag_on(monkeypatch):
    """Ticket 2: Con el flag ON, el botón DEBE renderizarse en el HTML."""
    monkeypatch.setenv("DARK_MODE_ENABLED", "true")
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # El botón toggle existe en el DOM
    assert 'id="themeToggleBtn"' in html
    assert "dark_mode_enabled = ON" in html
    assert "toggleTheme()" in html


def test_index_hides_toggle_button_when_flag_off(monkeypatch):
    """Ticket 1 (Validación inversa): Con el flag OFF, el botón NO DEBE existir en el DOM."""
    monkeypatch.setenv("DARK_MODE_ENABLED", "false")
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # El botón NO existe en el DOM
    assert 'id="themeToggleBtn"' not in html
    assert "dark_mode_enabled = OFF" in html
    assert "Modo Oscuro oculto (Flag OFF)" in html


def test_ticket_3_localstorage_persistence_script_present(monkeypatch):
    """Ticket 3: Verifica que el script incluya la persistencia y carga desde localStorage."""
    monkeypatch.setenv("DARK_MODE_ENABLED", "true")
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    assert "localStorage.setItem('theme', newTheme)" in html
    assert "localStorage.getItem('theme')" in html
    assert "DOMContentLoaded" in html
    assert "Ticket 3 (Completado - Rollout 100%)" in html

