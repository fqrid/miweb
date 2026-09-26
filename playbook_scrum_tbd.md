# 📘 Scrum + TBD Playbook — Proyecto MiWeb
**Equipo:** Mi Web / Control de Chanchitos  
**Contexto:** Adaptación de Scrum a Trunk-Based Development (TBD) y Despliegue Continuo (CD)  
**Repositorio:** https://github.com/fqrid/miweb

---

## 1. Principios Acordados (Máximo 5)

1. **`master` siempre verde, estable y releasable:** La rama principal nunca se rompe. Si el pipeline de CI falla, arreglarlo es la máxima prioridad de todo el equipo antes de escribir código nuevo.
2. **Batches pequeños y ramas efímeras:** El trabajo se divide en micro-cambios (vertical slices). Las ramas de Git viven horas, nunca días ni semanas (vida útil < 1 día).
3. **Desacoplar Despliegue de Lanzamiento:** Desplegar código a producción mediante CD no obliga a activar la funcionalidad para el usuario final; se utilizan Feature Toggles (Dark Launching).
4. **Calidad automatizada antes del merge:** Ningún código entra a `master` sin validación estática con Ruff (`ruff check .`) y pruebas unitarias con Pytest (`pytest src/test.py`) pasando al 100%.
5. **Responsabilidad colectiva del pipeline:** Todos los miembros del equipo son dueños de la calidad, la estabilidad del repositorio y la entrega continua de valor.

---

## 2. Roles Adaptados y Compromisos (Post-its)

### 🎯 Product Owner (PO)
* **Responsabilidades adaptadas:**
  * Prioriza historias por valor considerando el tamaño del batch y el riesgo de despliegue.
  * Participa activamente en el refinamiento técnico para cortar historias en slices de pocas horas.
  * Gobierna el ciclo de vida de los Feature Toggles: decide porcentajes de rollout (0% -> 10% -> 100%) y fechas de activación/retiro.
* **Post-it de compromiso PO:**
  > *"Acepto historias que no tengan UI terminada si aportan lógica probada y segura a master, y asumo el control de encender o apagar funcionalidades en producción desde ConfigCat."*

### 💻 Developers
* **Responsabilidades adaptadas:**
  * Mantienen la rama principal siempre verde e integrable.
  * Diseñan cambios compatibles hacia atrás (Backward Compatibility) sin romper contratos existentes de APIs.
  * Escriben y mantienen pruebas unitarias automatizadas para cada funcionalidad o bugfix.
  * Realizan revisiones de código (Code Review) ágiles (< 15 minutos) priorizándolas sobre iniciar tareas nuevas.
* **Post-it de compromiso Developers:**
  > *"Hago ramas que duran horas, integro a master el mismo día respaldado por tests automáticos en CI y uso Feature Flags para código en progreso."*

### 🛡️ Scrum Master (SM)
* **Responsabilidades adaptadas:**
  * Facilita la disciplina de integración frecuente y remueve bloqueos en PRs, CI o revisiones.
  * Elimina el miedo a romper la rama principal fortaleciendo la red de seguridad automatizada.
  * Monitorea la salud del flujo de trabajo y métricas de entrega continua (lead time, tiempo de PR abierto).
* **Post-it de compromiso Scrum Master:**
  > *"Velo porque ningún PR quede estancado más de 2 horas y protejo la disciplina de integración continua diaria sin permitir ramas de larga duración."*

---

## 3. Reglas de Oro de Integración a `master`

1. **Vida útil de la rama < 24 horas:** Ramas pequeñas creadas desde `master` y reintegradas el mismo día (`feature/resta-calculator`).
2. **Branch Protection mandatoria (Ruleset en `master`):**
   * Prohibido el push directo a `master`.
   * Requiere Pull Request con al menos 1 revisión aprobada (`required_approving_review_count: 1`).
   * Verificación obligatoria de estado estricto de CI en verde antes del merge.
3. **Todo cambio nuevo lleva test unitario:** Ninguna función se mergea sin su prueba correspondiente en [src/test.py](file:///Users/faridzemanate/Docs/miweb/src/test.py).
4. **Dark Launch con Feature Flags para trabajo incompleto:** Toda funcionalidad no lista para el usuario final entra a `master` apagada (Rollout 0% en ConfigCat).
5. **Revisión de PRs como prioridad del equipo:** Revisar el PR de un compañero tiene prioridad sobre empezar una nueva tarjeta para evitar acumulación de inventario (WIP).

---

## 4. Definition of Done (DoD) Preliminar

Una historia o incremento se considera **DONE** solo si cumple con:

### Criterios Técnicos:
- [ ] Código implementado con tipado limpio y sin errores de linter (`ruff check .` = 0 advertencias).
- [ ] Pruebas unitarias escritas y ejecutándose al 100% de éxito con Pytest (`pytest src/test.py`).
- [ ] Pipeline de CI en GitHub Actions (`.github/workflows/ci.yaml`) finalizado con estado VERDE en el PR.
- [ ] Al menos 1 aprobación registrada en el Code Review (humano o asistido).
- [ ] Integrado a `master` mediante Squash & Merge / Merge commit y rama efímera eliminada.
- [ ] Job `build_and_push` ejecutado exitosamente generando el contenedor Docker en GHCR (`ghcr.io/fqrid/miweb:latest`).
- [ ] Si la funcionalidad está en desarrollo o rollout progresivo, cuenta con su toggle configurado en ConfigCat.

### Criterios de Negocio:
- [ ] Criterios de aceptación del Issue / Slice verificados.
- [ ] Product Owner informado con control sobre el flag de activación.
- [ ] Sin regresiones en el comportamiento funcional previo ni incompatibilidad de contratos públicos.

---

## 5. Adaptación de Ceremonias

| Ceremonia | Enfoque Tradicional | Adaptación a TBD + CD | Pregunta Clave de la Ceremonia |
| :--- | :--- | :--- | :--- |
| **Sprint Planning** | Planear lotes grandes de trabajo para entregar al final de 2 semanas. | Descomponer historias en slices verticales de pocas horas con estrategia de Feature Flags. | *"¿Cómo cortamos esta historia para mergear un primer slice funcional a master hoy mismo?"* |
| **Daily Scrum** | "¿Qué hice ayer? ¿Qué haré hoy? ¿Qué bloqueos tengo?" | Enfocado en el flujo de integración continua, salud del trunk y estado de los PRs. | *"¿Qué voy a integrar a master hoy? ¿Tengo algún PR esperando revisión? ¿Está master en verde?"* |
| **Sprint Review** | Presentar demos de ramas locales o esperar despliegues manuales estresantes. | Demostración en vivo en producción alternando Feature Toggles en tiempo real (ConfigCat). | *"¿Qué valor ya está integrado y desplegado? ¿Qué porcentaje de rollout activaremos para usuarios?"* |
| **Sprint Retrospective** | Enfocada principalmente en dinámicas interpersonales. | Análisis del flujo técnico de entrega: tiempo de vida de ramas, fallos en CI y deuda de flags a retirar. | *"¿Cuántos flags obsoletos debemos limpiar? ¿Qué fricciones tuvimos en el pipeline de CI/CD?"* |

---

## 6. Decisiones Pendientes y Próximos Pasos

1. **Integración formal del SDK de ConfigCat:**
   * Agregar `configcat-client` a [src/requirements.txt](file:///Users/faridzemanate/Docs/miweb/src/requirements.txt).
   * Implementar la verificación del flag en [src/main.py](file:///Users/faridzemanate/Docs/miweb/src/main.py) con clave de SDK inyectada por variable de entorno (`CONFIGCAT_SDK_KEY`).
2. **Automatización del Despliegue Continuo (CD Runtime):**
   * Configurar un webhook o GitHub Action de despliegue continuo desde GHCR hacia la plataforma de hosting en la nube (Render, Fly.io o AWS).
3. **Métricas DORA del Repositorio:**
   * Medir *Deployment Frequency* (frecuencia con que se empuja a master y GHCR).
   * Medir *Lead Time for Changes* (tiempo transcurrido desde el primer commit en la rama efímera hasta el merge a master).
4. **Política de limpieza técnica de Feature Toggles:**
   * Establecer que una vez una funcionalidad alcance el 100% de rollout (Issue #4), en el siguiente Sprint se elimine el bloque condicional del flag del código.
