# /verify — Verificación adversarial + Definition of Done

Uso: `/verify`  (opcional: `/verify <archivo-o-spec>`)

Corre la puerta de calidad antes de cerrar un ciclo. Tu trabajo es **REFUTAR**, no aprobar.

## 1. Verificación adversarial (lentes distintos)
Revisa el diff/cambio con estas gafas, una por vez, y reporta hallazgos con evidencia:
- **Correctitud:** ¿cumple los criterios de aceptación de la spec? ¿hay bordes sin cubrir?
- **Seguridad:** ¿inyección de entrada? ¿secretos en logs? ¿eval/exec de texto del usuario?
  ¿manejo de PII? (ver "problema del 80%": rate limiting, reintentos, circuit breakers, audit).
- **Rendimiento:** ¿timeouts? ¿límites duros respetados (MAX_TOOL_ROUNDS, TOOL_TIMEOUT_S)?
- **¿Se reproduce?:** corre el escenario real al menos una vez; si lo viste "a ojo", dilo
  "verificado manualmente", no "el test pasa".

## 2. Definition of Done (checklist binario)
- [ ] Todos los criterios de aceptación de la spec cubiertos por test.
- [ ] Pasó los niveles aplicables: compila → unit → integración → E2E/real.
- [ ] Se ejecutó de verdad al menos una vez (no solo compiló).
- [ ] Los fallos, si los hubo, se reportaron con su salida (cero parcial silencioso).
- [ ] Decisiones/gotchas no obvios quedaron en memoria.
- [ ] La spec quedó actualizada con lo aprendido.
- [ ] Changelog actualizado si hubo bump de versión.
- [ ] Trazabilidad: commit → spec US-NNN → CA → intención original.

## Reporte
Imprime ✅/❌ por cada ítem. Si hay ❌, NO cierres el ciclo: indica la causa exacta y el
comando para arreglarlo. La velocidad sin disciplina es deuda acelerada.
