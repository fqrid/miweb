import os

from flask import Flask, jsonify, render_template_string, request

try:
    import configcatclient
    from configcatclient.user import User
except ImportError:  # pragma: no cover
    configcatclient = None
    User = None


# --- 1. Lógica de Dominio (Calculadora con retrocompatibilidad) ---
class Calculator:
    def suma(self, a: int, b: int) -> int:
        return a + b

    def resta(self, a: int, b: int) -> int:
        return a - b

    # Alias para compatibilidad hacia atrás
    def sum(self, a: int, b: int) -> int:
        return self.suma(a, b)


# Alias en minúscula para compatibilidad con tests existentes
calculator = Calculator


# --- 2. Integración de Feature Toggle (ConfigCat) ---
CONFIGCAT_SDK_KEY = os.environ.get(
    "CONFIGCAT_SDK_KEY",
    "configcat-sdk-1/hCHfCO3blUmOGtb4M93ArQ/Yyqu66vw20iaZ0vuvQ6hWg",
).strip()
_configcat_client = None

if CONFIGCAT_SDK_KEY and configcatclient:
    try:  # pragma: no cover
        from configcatclient import ConfigCatOptions, PollingMode

        options = ConfigCatOptions(
            polling_mode=PollingMode.auto_poll(poll_interval_seconds=5)
        )
        _configcat_client = configcatclient.get(CONFIGCAT_SDK_KEY, options=options)
        print("[ConfigCat] Cliente inicializado correctamente con auto-polling cada 5s.")
    except Exception as exc:  # noqa: BLE001  # pragma: no cover
        print(f"[ConfigCat] Advertencia al inicializar cliente: {exc}")


def is_dark_mode_enabled(user_id: str | None = None) -> bool:
    """Evalúa el Feature Toggle 'dark_mode_enabled' en ConfigCat.

    Si DARK_MODE_ENABLED está definido en el entorno (pruebas/CI), tiene prioridad.
    En producción (Render), consulta directamente al SDK de ConfigCat en vivo.
    """
    if "DARK_MODE_ENABLED" in os.environ:
        return os.environ.get("DARK_MODE_ENABLED", "false").strip().lower() in (
            "true",
            "1",
            "yes",
        )

    if _configcat_client and configcatclient:
        user = User(user_id) if (user_id and User) else None
        val = _configcat_client.get_value("dark_mode_enabled", None, user)
        if val is None:
            val = _configcat_client.get_value("darkModeEnabled", None, user)
        if val is not None:
            return bool(val)

    return False


def is_auto_theme_enabled(user_id: str | None = None) -> bool:
    """Evalúa el Feature Toggle 'auto-theme-v1' en ConfigCat."""
    if "AUTO_THEME_ENABLED" in os.environ:
        return os.environ.get("AUTO_THEME_ENABLED", "false").strip().lower() in ("true", "1", "yes")

    if _configcat_client and configcatclient:
        user = User(user_id) if (user_id and User) else None
        val = _configcat_client.get_value("auto-theme-v1", None, user)
        if val is None:
            val = _configcat_client.get_value("autoThemeV1", None, user)
        if val is not None:
            return bool(val)

    return False


def get_theme_context(user_id: str | None = None) -> dict:
    """Lógica de tema raíz protegida por Feature Toggle."""
    flag_enabled = is_dark_mode_enabled(user_id=user_id)
    auto_theme_enabled = is_auto_theme_enabled(user_id=user_id)

    # Carga inicial por defecto en claro; el botón JS alterna en vivo
    is_dark = False

    theme_class = "dark-theme" if is_dark else "light-theme"
    data_theme = "dark" if is_dark else "light"

    return {
        "feature_flag_enabled": flag_enabled,
        "auto_theme_enabled": auto_theme_enabled,
        "configcat_connected": bool(_configcat_client is not None),
        "configcat_sdk_key_configured": bool(CONFIGCAT_SDK_KEY),
        "dark_mode_active": is_dark,
        "theme_class": theme_class,
        "data_theme": data_theme,
    }


# --- 3. Aplicación Web y Dashboard (Flask) ---
app = Flask(__name__)
calc_service = Calculator()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es" class="{{ theme.theme_class }}" data-theme="{{ theme.data_theme }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MiWeb — Dashboard TBD & CI/CD</title>
    <style>
        /* ========================================================= */
        /* CAP 5: Variables CSS del Tema Claro (Predeterminado)      */
        /* ========================================================= */
        :root, .light-theme {
            --bg-color: #f8fafc;
            --surface-color: #ffffff;
            --surface-border: #e2e8f0;
            --text-primary: #0f172a;
            --text-secondary: #64748b;
            --accent-primary: #3b82f6;
            --accent-hover: #2563eb;
            --badge-bg: #e0f2fe;
            --badge-text: #0369a1;
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        }

        /* ========================================================= */
        /* CAP 5: Variables CSS del Tema Oscuro                      */
        /* ========================================================= */
        .dark-theme, [data-theme="dark"] {
            --bg-color: #0b0f19;
            --surface-color: #1e293b;
            --surface-border: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-primary: #60a5fa;
            --accent-hover: #3b82f6;
            --badge-bg: #1e3a8a;
            --badge-text: #93c5fd;
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.5), 0 2px 4px -2px rgb(0 0 0 / 0.5);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        header {
            background-color: var(--surface-color);
            border-bottom: 1px solid var(--surface-border);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: var(--shadow);
        }

        .logo-area {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .logo-badge {
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            color: white;
            font-weight: bold;
            padding: 0.4rem 0.8rem;
            border-radius: 8px;
            font-size: 0.9rem;
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        /* Botón de cambio de tema (Ticket 2) */
        .theme-toggle-btn {
            background-color: var(--surface-color);
            border: 1px solid var(--surface-border);
            color: var(--text-primary);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            box-shadow: var(--shadow);
        }

        .theme-toggle-btn:hover {
            border-color: var(--accent-primary);
            color: var(--accent-primary);
        }

        .flag-status-pill {
            font-size: 0.8rem;
            padding: 0.3rem 0.75rem;
            border-radius: 9999px;
            font-weight: 600;
        }

        .flag-off {
            background-color: #fee2e2;
            color: #b91c1c;
        }

        .flag-on {
            background-color: #dcfce7;
            color: #15803d;
        }

        .container {
            max-width: 1100px;
            margin: 2rem auto;
            padding: 0 1.5rem;
            flex: 1;
        }

        .hero {
            margin-bottom: 2rem;
        }

        .hero h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }

        .hero p {
            color: var(--text-secondary);
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .card {
            background-color: var(--surface-color);
            border: 1px solid var(--surface-border);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: var(--shadow);
        }

        .card h2 {
            font-size: 1.25rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .ticket-list {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .ticket-item {
            padding: 0.75rem;
            border-radius: 8px;
            background-color: var(--bg-color);
            border: 1px solid var(--surface-border);
            font-size: 0.9rem;
        }

        .ticket-badge {
            font-size: 0.75rem;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-weight: bold;
            margin-right: 0.5rem;
        }

        .calc-form {
            display: flex;
            gap: 0.5rem;
            align-items: center;
            margin-top: 1rem;
        }

        .calc-form input {
            padding: 0.5rem;
            border-radius: 6px;
            border: 1px solid var(--surface-border);
            background: var(--bg-color);
            color: var(--text-primary);
            width: 80px;
            text-align: center;
        }

        .calc-form button {
            background-color: var(--accent-primary);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
        }

        .calc-form button:hover {
            background-color: var(--accent-hover);
        }

        footer {
            text-align: center;
            padding: 1.5rem;
            font-size: 0.85rem;
            color: var(--text-secondary);
            border-top: 1px solid var(--surface-border);
        }
    </style>
</head>
<body>
    <header>
        <div class="logo-area">
            <span class="logo-badge">TBD + CD</span>
            <strong>MiWeb Dashboard</strong>
        </div>
        <div class="header-actions">
            <!-- Ticket 2: Botón de tema -->
            {% if theme.auto_theme_enabled %}
                <button class="theme-toggle-btn" style="opacity: 0.6; cursor: not-allowed;" title="Bloqueado por Auto-Tema">
                    <span>⏰ Auto-Tema Activo</span>
                </button>
            {% elif theme.feature_flag_enabled %}
                <button id="themeToggleBtn" class="theme-toggle-btn" onclick="toggleTheme()">
                    <span id="themeIcon">🌙 Modo Oscuro</span>
                </button>
            {% else %}
                <span style="font-size: 0.8rem; color: var(--text-secondary);">
                    🔒 Modo Oscuro oculto (Flag OFF)
                </span>
            {% endif %}

            <span class="flag-status-pill {{ 'flag-on' if theme.feature_flag_enabled else 'flag-off' }}">
                Feature Flag: dark_mode_enabled = {{ 'ON' if theme.feature_flag_enabled else 'OFF' }}
            </span>
        </div>
    </header>

    <main class="container">
        <section class="hero">
            <h1>Panel de Control & TBD Workflow</h1>
            <p>Demostración práctica del <strong>Taller 3</strong>: CI/CD, Despliegue en Render y Feature Toggles con ConfigCat.</p>
        </section>

        <div class="grid">
            <!-- Card 1: Feature Toggle ConfigCat -->
            <!-- Card 1: Feature Toggle ConfigCat -->
            <div class="card">
                <h2>🚩 Feature Toggle (ConfigCat)</h2>
                <p style="margin-bottom: 0.5rem; color: var(--text-secondary);">
                    Flags evaluados: <code>dark_mode_enabled</code>, <code>auto-theme-v1</code>
                </p>
                <div style="margin-bottom: 0.75rem; font-size: 0.85rem;">
                    <strong>Origen de datos:</strong>
                    {% if theme.configcat_connected %}
                        <span style="color: #15803d; font-weight: 600;">🟢 ConfigCat SDK en vivo (refresco 5s)</span>
                    {% elif theme.configcat_sdk_key_configured %}
                        <span style="color: #d97706; font-weight: 600;">🟡 SDK Key configurada</span>
                    {% else %}
                        <span style="color: #64748b; font-weight: 600;">⚪ Modo local (Variable DARK_MODE_ENABLED)</span>
                    {% endif %}
                </div>
                <div style="margin-bottom: 1rem;">
                    <strong>Estado actual:</strong>
                    {% if theme.feature_flag_enabled %}
                        <span style="color: #15803d; font-weight: bold;">● ACTIVADO (ON)</span>
                    {% else %}
                        <span style="color: #b91c1c; font-weight: bold;">● APAGADO (OFF)</span>
                    {% endif %}
                </div>
                <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                    {% if theme.feature_flag_enabled %}
                        ✅ <em>Activo:</em> El botón de modo oscuro es visible e interactivo para los usuarios.
                    {% else %}
                        🛡️ <em>Desactivado:</em> El modo oscuro está apagado y el botón se mantiene oculto.
                    {% endif %}
                </p>
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--surface-border);">
                    <strong>Tema Automático (auto-theme-v1):</strong>
                    {% if theme.auto_theme_enabled %}
                        <span style="color: #15803d; font-weight: bold;">ACTIVADO (ON)</span>
                    {% else %}
                        <span style="color: #64748b; font-weight: bold;">DESACTIVADO (OFF)</span>
                    {% endif %}
                </div>
            </div>

            <!-- Card 2: División de Historias (Ejemplo 3) -->
            <div class="card">
                <h2>📋 Slicing: Modo Oscuro</h2>
                <ul class="ticket-list">
                    <li class="ticket-item">
                        <span class="ticket-badge" style="background: #dcfce7; color: #15803d;">Ticket 1 (Completado)</span>
                        Variables CSS y lógica raíz integradas tras Dark Launch (Flag OFF).
                    </li>
                    <li class="ticket-item">
                        <span class="ticket-badge" style="background: #dcfce7; color: #15803d;">Ticket 2 (Completado)</span>
                        Botón toggle expuesto condicionalmente al Feature Flag.
                    </li>
                    <li class="ticket-item">
                        <span class="ticket-badge" style="background: #dbeafe; color: #1e40af;">Ticket 3 (Completado - Rollout 100%)</span>
                        Persistencia con localStorage y disponibilidad al 100%.
                    </li>
                </ul>
            </div>

            <!-- Card 3: Estado del Pipeline & Despliegue -->
            <div class="card">
                <h2>🚀 Pipeline & Render</h2>
                <p style="margin-bottom: 0.5rem;"><strong>Healthcheck:</strong> <code>/healthz</code></p>
                <p style="margin-bottom: 0.5rem;"><strong>Entorno:</strong> Render Cloud</p>
                <p style="margin-bottom: 1rem;"><strong>Regla:</strong> Push a <code>master</code> activa tests, build Docker y deploy automático.</p>
                <a href="/healthz" target="_blank" style="color: var(--accent-primary); font-size: 0.9rem; text-decoration: none;">
                    Ver endpoint de salud &rarr;
                </a>
            </div>

            <!-- Card 4: Calculadora Interactiva (Test en vivo) -->
            <div class="card">
                <h2>🧮 Servicio Calculadora</h2>
                <p style="color: var(--text-secondary); font-size: 0.9rem;">
                    Prueba rápida de la lógica de negocio subyacente:
                </p>
                <div class="calc-form">
                    <input type="number" id="numA" value="7">
                    <span>+</span>
                    <input type="number" id="numB" value="5">
                    <button type="button" onclick="calculateSum()">Sumar</button>
                    <strong id="calcResult" style="margin-left: 0.5rem;">= 12</strong>
                </div>
            </div>
        </div>
    </main>

    <footer>
        <p>Equipo MiWeb &copy; 2026 — Trunk-Based Development & Continuous Deployment</p>
    </footer>

    <script>
        // Ticket 3: Aplicar tema y actualizar icono del botón
        function applyTheme(theme) {
            const html = document.documentElement;
            html.setAttribute('data-theme', theme);
            html.className = theme === 'dark' ? 'dark-theme' : 'light-theme';

            const iconSpan = document.getElementById('themeIcon');
            if (iconSpan) {
                iconSpan.textContent = theme === 'dark' ? '☀️ Modo Claro' : '🌙 Modo Oscuro';
            }
        }

        // Ticket 3: Alternar tema y persistir en localStorage
        function toggleTheme() {
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

            applyTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        }

        // Ticket 3: Carga Inicial (On Load)
        document.addEventListener('DOMContentLoaded', () => {
            const flagEnabled = {{ 'true' if theme.feature_flag_enabled else 'false' }};
            const autoThemeEnabled = {{ 'true' if theme.auto_theme_enabled else 'false' }};
            
            if (autoThemeEnabled) {
                // Si auto-theme está activo, forzamos la hora e ignoramos decisiones manuales
                const hour = new Date().getHours();
                if (hour >= 18 || hour < 6) {
                    applyTheme('dark');
                } else {
                    applyTheme('light');
                }
            } else if (flagEnabled) {
                // Si auto-theme está apagado pero el modo oscuro manual está activo, respetamos el localStorage
                const savedTheme = localStorage.getItem('theme');
                if (savedTheme) {
                    applyTheme(savedTheme);
                }
            } else {
                // Ambos flags apagados
                applyTheme('light');
                localStorage.removeItem('theme');
            }
        });

        function calculateSum() {
            const a = parseInt(document.getElementById('numA').value) || 0;
            const b = parseInt(document.getElementById('numB').value) || 0;
            document.getElementById('calcResult').textContent = '= ' + (a + b);
        }
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    user_id = request.args.get("user_id") or request.headers.get("X-User-Id")
    theme_context = get_theme_context(user_id=user_id)
    return render_template_string(HTML_TEMPLATE, theme=theme_context)


@app.route("/healthz")
def healthz():
    """Endpoint de verificación de salud para Render / Kubernetes."""
    return (
        jsonify(
            {
                "status": "healthy",
                "service": "miweb-dashboard",
                "feature_toggle_ready": True,
            }
        ),
        200,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)