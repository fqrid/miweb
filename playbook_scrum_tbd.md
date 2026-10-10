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

## 5. Definition of Done (DoD) Definitivo — Cierre Taller 3

Una historia o incremento se considera formalmente **DONE** solo si cumple con la totalidad de los siguientes criterios:

### 🛠️ Criterios Técnicos y de Calidad:
- [x] **Suite de pruebas en verde y análisis estático (Linter) superado:**
  - Código validado al 100% con `ruff check .` (0 advertencias/errores de estilo).
  - Todas las pruebas unitarias y de integración pasando con éxito (`pytest src/test.py`).
- [x] **Pipeline de CI en GitHub Actions en VERDE:**
  - Los jobs `test` y `build_and_push` ejecutados exitosamente en [.github/workflows/ci.yaml](file:///Users/faridzemanate/Docs/miweb/.github/workflows/ci.yaml).
  - Generación y publicación del contenedor Docker en GHCR (`ghcr.io/fqrid/miweb:latest`).
- [x] **Código nuevo o incompleto oculto de forma segura tras un Feature Toggle (ConfigCat):**
  - Cualquier funcionalidad no lista para el usuario final está protegida mediante el SDK de ConfigCat (`dark_mode_enabled` en Dark Launch al 0%).
- [x] **Revisión de código obligatoria:**
  - Al menos una aprobación registrada en Pull Request sin permitir push directo a `master`.

### 🚀 Criterios de Despliegue e Infraestructura:
- [x] **Desplegado automáticamente en Render desde la rama master/main:**
  - Conexión continua activa con Render Web Service para despliegue automático tras cada merge en la rama principal.
  - Endpoint de salud (`/healthz`) respondiendo HTTP 200 (`status: healthy`).
- [x] **Capacidad de Rollback inmediato:**
  - Política de desactivación instantánea mediante ConfigCat (apagar flag en < 1 segundo) o redeploy de commit anterior en Render.

### 💼 Criterios de Negocio:
- [x] Criterios de aceptación verificados y validados en el entorno de despliegue.
- [x] Product Owner con control autónomo sobre los porcentajes de activación del toggle (0% -> 10% -> 100%).
- [x] Sin regresiones en la experiencia previa de usuario ni ruptura de compatibilidad hacia atrás.

---

## 6. Planificación de Sprint Orientada a Flujo e Integración Diaria

### 🎯 Formato y Ejemplo de Sprint Goal
* **Formato estándar:** *"Al final del sprint los usuarios podrán [Valor visible X], aunque [Funcionalidad Y] todavía esté detrás de toggle."*
* **Ejemplo para MiWeb (Sprint Actual):**  
  > *"Al final del sprint los usuarios podrán alternar entre modo claro y modo oscuro en el dashboard con persistencia local, mientras que la entrega continua a Render y el gobierno de flags en ConfigCat operan de forma automatizada y transparente."*

### 📊 Acuerdos para Ordenar el Sprint Backlog
1. **Regla del Día 1:** El primer ítem del Sprint Backlog debe poder integrarse a `master` idealmente el **Día 1 o 2**.
2. **Matriz de Priorización:** Se ordena por **Valor de negocio + Menor riesgo técnico + Dependencias de integración**.
3. **Tablero de Integración Diaria (Ejemplo 3 - Modo Oscuro):**
   * **Día 1–2 (Ticket 1):** Variables CSS y tema oscuro detrás de flag `dark_mode_enabled` en OFF (0% - Dark Launch).
   * **Día 3–4 (Ticket 2):** Botón toggle en UI con alternancia en vivo para segmento canario (10% en ConfigCat).
   * **Día 5–6 (Ticket 3):** Persistencia de tema con `localStorage` y apertura al 100% de la base de usuarios.
   * **Día 7–8:** Cierre formal del DoD, configuración de Auto-Deploy en Render y actualización de métricas DORA.

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

## 8. Checklist de Cierre de Fase 1 (Taller 3) — Completado al 100% ✅

Todos los compromisos y pendientes de la Fase 1 han sido implementados, probados y formalizados:

| Compromiso / Pendiente Fase 1 | Estado | Evidencia Técnica en el Repositorio |
| :--- | :---: | :--- |
| **1. Auto-deploy desde `master`/`main` a Render** | ✅ **Completado** | Configuración de Web Service en Render con auto-deploy activo y verificación por endpoint `/healthz`. |
| **2. Feature Toggle con ConfigCat funcionando** | ✅ **Completado** | SDK `configcat-client` integrado en [src/main.py](file:///Users/faridzemanate/Docs/miweb/src/main.py) con soporte para Dark Launch (0%), Rollout (10%) y General Availability (100%). |
| **3. Definition of Done (DoD) formalizado y aplicado** | ✅ **Completado** | Sección 5 actualizada y aprobada por el equipo incluyendo calidad, despliegue continuo y control de toggles. |
| **4. Pipeline más robusto con automatización de pruebas** | ✅ **Completado** | Suite ampliada a 10 tests pasando en verde (`pytest src/test.py`) y análisis estático con `ruff check .` integrado en CI. |

---

## 9. Compromisos y Acciones Inmediatas para el Próximo Sprint

### 📌 3 Acciones Concretas:
1. **Filtro DoR Estricto:** Toda historia nueva debe cumplir los 5 criterios del *Definition of Ready* antes de ser admitida en el Sprint Planning. Si no se puede integrar en ≤ 1 día, se rechaza y se re-rebanada.
2. **Revisión Prioritaria:** Ningún PR permanecerá más de 2 horas sin revisión. Todo miembro del equipo prioriza revisar un PR pendiente antes de iniciar una tarea nueva.
3. **Primer Merge Día 1:** El ítem prioritario del Sprint debe quedar integrado a `master` en las primeras 24 horas del Sprint.

### 🔄 Ronda Final: “¿Qué cambia en nuestra próxima Planning después de este taller?”
* **Antes:** Planificábamos pensando en qué íbamos a *"terminar"* dentro de 15 días, aceptábamos historias grandes con UI y backend acoplados, y asumíamos el estrés del merge al final del Sprint.
* **A partir de mañana:** Planificamos pensando en **qué vamos a integrar a `master` cada día**. Las historias entran rebanadas en vertical con su Feature Toggle identificado. Salimos de la Planning sabiendo con certeza qué Pull Request estará en verde el primer día y con el compromiso colectivo de no dejar envejecer ninguna rama.

---

## Anexo: Gobernanza de Continuous Deployment

### Nuevo enfoque del Sprint Review
Las demos se centrarán en incrementos que ya se encuentran en producción (activables por toggles) y en demostrar el valor real entregado, no solo en un recuento de "qué se programó".

### Nuevos focos de la Retrospective
Añadimos la revisión obligatoria de:
* **Salud del pipeline:** Tiempos de CI y despliegues fallidos.
* **Métricas de TBD:** Frecuencia de integraciones diarias a `main`/`master`.
* **Limpieza de deuda técnica:** Retiro de Feature Toggles antiguos.

### Política de Liberación Segura (Feature Toggles)
* **Despliegue Incremental:** El rollout siempre será progresivo (ej. internos -> % -> 100%).
* **Monitoreo Obligatorio:** Observación de métricas técnicas (latencia, errores) y de negocio (conversión) durante las primeras 48h.
* **Rollback Inmediato (Kill Switch):** El equipo técnico tiene plena autoridad para ejecutar un apagado de emergencia si los errores superan los umbrales definidos, sin necesidad de permisos o aprobaciones.
