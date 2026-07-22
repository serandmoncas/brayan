## US-007 — Los tests no deben contaminar la memoria real del proyecto
**Como** desarrollador de este repo
**quiero** que correr `pytest` nunca escriba en `memory/long_term.jsonl` real
**para** no perder ni mezclar datos verdaderos del dueño con datos de prueba.

**Valor:** se detectó en vivo que `memory/long_term.jsonl` tenía 12 líneas duplicadas de
`test_remember_recall` — cada corrida de `make test` antes de la demo iba a seguir ensuciando
el archivo que en producción guardaría hechos reales del dueño.
**Prioridad:** alta   **Estimación:** S (1 ciclo)

### Criterios de aceptación (reglas de NEGOCIO)
- [x] CA1: correr la suite de tests no crea ni modifica `memory/long_term.jsonl` en la raíz del proyecto.
- [x] CA2: `remember`/`recall` siguen funcionando igual para el uso real (no regresión funcional).

### Causa raíz
`src/memory/store.py` calculaba `MEMORY_DIR`/`LONG_TERM` como constantes de módulo en el momento
del `import`. El fixture autouse de `tests/conftest.py` hace `monkeypatch.setenv("MEMORY_DIR", ...)`
por test, pero para entonces el módulo ya se había importado (en la fase de colección de pytest)
con la ruta real (`./memory`) ya congelada. El monkeypatch nunca tenía efecto.

### Fix
`_long_term_path()` relee `MEMORY_DIR` en cada llamada a `remember`/`recall`, en vez de usarlo
como constante de import. Mismo patrón que el fix de `AUTHORIZED_WHATSAPP_ID` en US-002.

### Restricciones
- No se cambia el formato del JSONL ni la API pública (`remember`, `recall`, `short_term_window`).

### No-objetivos
- No se cubre migración/backup de datos de memoria ya existentes (el archivo contaminado se
  limpió manualmente porque su contenido completo era de prueba, no dato real del dueño).

### Trazabilidad
- commit: (pendiente, ver git diff)  ·  test: tests/test_memory.py::test_remember_does_not_touch_real_project_memory
  ·  intención: sesión 2026-07-22
