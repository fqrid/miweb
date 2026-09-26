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

## 4. Definition of Ready (DoR) para TBD

Una historia o incremento está **READY** para entrar al Sprint Backlog solo si cumple con:

- [ ] **Slice ≤ 1 día:** Está rebanada verticalmente para implementarse, probarse e integrarse a `master` en 24 horas o menos.
- [ ] **Acceptance Criteria verificables post-despliegue:** Criterios claros y comprobables directamente en staging o producción (tests automáticos y validación funcional).
- [ ] **Estrategia de Feature Toggle definida:** Se definió explícitamente si requiere flag, la clave del toggle en ConfigCat (ej. `FEATURE_OPS_EXTRA`, `FEATURE_HISTORIAL`) y su estado inicial (OFF 0% o Canario 10%).
- [ ] **Sin dependencias bloqueantes externas:** No depende de APIs de terceros no disponibles, accesos pendientes ni bloqueos de otros equipos.
- [ ] **Validación clara para el equipo:** El equipo tiene consenso sobre cómo se probará (`pytest`, `ruff`), qué endpoints/métodos se tocan y cómo se valida el comportamiento antes del merge.

---

## 5. Definition of Done (DoD) Preliminar

Una historia o incremento se considera **DONE** solo si cumple con:

### Criterios Técnicos:
- [ ] Código implementado con tipado limpio y sin errores de linter (`ruff check .` = 0 advertencias).
- [ ] Pruebas unitarias escritas y ejecutándose al 100% de éxito con Pytest (`pytest src/test.py`).
- [ ] Pipeline de CI en GitHub Actions ([.github/workflows/ci.yaml](file:///Users/faridzemanate/Docs/miweb/.github/workflows/ci.yaml)) finalizado con estado VERDE en el PR.
- [ ] Al menos 1 aprobación registrada en el Code Review (humano o asistido).
- [ ] Integrado a `master` mediante Squash & Merge / Merge commit y rama efímera eliminada.
- [ ] Job `build_and_push` ejecutado exitosamente generando el contenedor Docker en GHCR (`ghcr.io/fqrid/miweb:latest`).
- [ ] Si la funcionalidad está en desarrollo o rollout progresivo, cuenta con su toggle configurado en ConfigCat.

### Criterios de Negocio:
- [ ] Criterios de aceptación del Issue / Slice verificados.
- [ ] Product Owner informado con control sobre el flag de activación en ConfigCat.
- [ ] Sin regresiones en el comportamiento funcional previo ni incompatibilidad de contratos públicos.

---

## 6. Planificación de Sprint Orientada a Flujo e Integración Diaria

### 🎯 Formato y Ejemplo de Sprint Goal
* **Formato estándar:** *"Al final del sprint los usuarios podrán [Valor visible X], aunque [Funcionalidad Y] todavía esté detrás de toggle."*
* **Ejemplo para MiWeb (Sprint Actual):**  
  > *"Al final del sprint los usuarios podrán realizar cálculos con suma y resta en la interfaz web, mientras que las operaciones avanzadas (multiplicación, división) y el historial estarán completamente integradas a master en backend y protegidas detrás de Feature Toggles para validación interna."*

### 📊 Acuerdos para Ordenar el Sprint Backlog
1. **Regla del Día 1:** El primer ítem del Sprint Backlog debe poder integrarse a `master` idealmente el **Día 1 o 2**.
2. **Matriz de Priorización:** Se ordena por **Valor de negocio + Menor riesgo técnico + Dependencias de integración**.
3. **Tablero de Integración Diaria:**
   * **Día 1–2:** Slice de frontend de resta (`FEATURE_RESTA` al 10% de rollout interno).
   * **Día 3–4:** Core de Multiplicación y División en `src/main.py` + tests unitarios (Dark Launch al 0%).
   * **Día 5–7:** Módulo de Historial en memoria + tests unitarios + conexión de botones avanzados en frontend (Rollout canario al 10%).
   * **Día 8–10:** Validación del DoD Fase 1 y conmutación de toggle al 100% en ConfigCat (General Availability).

### ⏱️ Ajuste de Capacidad Realista
La capacidad del equipo se calcula con un **buffer técnico explícito (~20%)** contemplando:
* Tiempo de Code Review continuo (< 15–30 min por PR).
* Tiempo de ejecución de pipelines en GitHub Actions (~1 min por ciclo).
* **Protocolo de "Master Roto":** Si el pipeline en `master` se pone en rojo, se detiene el trabajo nuevo hasta restaurar el estado verde.

---

## 7. Adaptación de Ceremonias

| Ceremonia | Enfoque Tradicional | Adaptación a TBD + CD | Pregunta Clave de la Ceremonia |
| :--- | :--- | :--- | :--- |
| **Sprint Planning** | Planear lotes grandes de trabajo para entregar al final de 2 semanas. | Descomponer historias en slices verticales de pocas horas con estrategia de Feature Flags y calendario de integración diaria. | *"¿Cómo cortamos esta historia para mergear un primer slice funcional a master hoy mismo?"* |
| **Daily Scrum** | "¿Qué hice ayer? ¿Qué haré hoy? ¿Qué bloqueos tengo?" | Enfocado en el flujo de integración continua, salud del trunk y estado de los PRs. | *"¿Qué voy a integrar a master hoy? ¿Tengo algún PR esperando revisión? ¿Está master en verde?"* |
| **Sprint Review** | Presentar demos de ramas locales o esperar despliegues manuales estresantes. | Demostración en vivo en producción alternando Feature Toggles en tiempo real (ConfigCat). | *"¿Qué valor ya está integrado y desplegado? ¿Qué porcentaje de rollout activaremos para usuarios?"* |
| **Sprint Retrospective** | Enfocada principalmente en dinámicas interpersonales. | Análisis del flujo técnico de entrega: tiempo de vida de ramas, fallos en CI y deuda de flags a retirar. | *"¿Cuántos flags obsoletos debemos limpiar? ¿Qué fricciones tuvimos en el pipeline de CI/CD?"* |

---

## 8. Decisiones Pendientes y Próximos Pasos

1. **Integración formal del SDK de ConfigCat:**
   * Agregar `configcat-client` a [src/requirements.txt](file:///Users/faridzemanate/Docs/miweb/src/requirements.txt).
   * Implementar la verificación del flag en [src/main.py](file:///Users/faridzemanate/Docs/miweb/src/main.py) con clave inyectada por variable de entorno (`CONFIGCAT_SDK_KEY`).
2. **Automatización del Despliegue Continuo (CD Runtime):**
   * Configurar un webhook o GitHub Action de despliegue continuo desde GHCR hacia la plataforma de hosting en la nube (Render, Fly.io o AWS).
3. **Métricas DORA del Repositorio:**
   * Medir *Deployment Frequency* (frecuencia con que se empuja a master y GHCR).
   * Medir *Lead Time for Changes* (tiempo transcurrido desde el primer commit en la rama efímera hasta el merge a master).
4. **Política de limpieza técnica de Feature Toggles:**
   * Establecer que una vez una funcionalidad alcance el 100% de rollout (Issue #4), en el siguiente Sprint se elimine el bloque condicional del flag del código.

---

## 9. Compromisos y Acciones Inmediatas para el Próximo Sprint

### 📌 3 Acciones Concretas:
1. **Filtro DoR Estricto:** Toda historia nueva debe cumplir los 5 criterios del *Definition of Ready* antes de ser admitida en el Sprint Planning. Si no se puede integrar en ≤ 1 día, se rechaza y se re-rebanada.
2. **Revisión Prioritaria:** Ningún PR permanecerá más de 2 horas sin revisión. Todo miembro del equipo prioriza revisar un PR pendiente antes de iniciar una tarea nueva.
3. **Primer Merge Día 1:** El ítem prioritario del Sprint debe quedar integrado a `master` en las primeras 24 horas del Sprint.

### 🔄 Ronda Final: “¿Qué cambia en nuestra próxima Planning después de este taller?”
* **Antes:** Planificábamos pensando en qué íbamos a *"terminar"* dentro de 15 días, aceptábamos historias grandes con UI y backend acoplados, y asumíamos el estrés del merge al final del Sprint.
* **A partir de mañana:** Planificamos pensando en **qué vamos a integrar a `master` cada día**. Las historias entran rebanadas en vertical con su Feature Toggle identificado. Salimos de la Planning sabiendo con certeza qué Pull Request estará en verde el primer día y con el compromiso colectivo de no dejar envejecer ninguna rama.
