# Skill: Desarrollo dirigido por especificación (Spec-Driven)

Flujo que debe seguir CUALQUIER construcción en este repo, inspirado en el
"Ciclo de Desarrollo de Software Moderno" (Jorge Johnson / Claude Opus 4).

## El ciclo (8 fases, cada una con su puerta)
1. **Intención** — expresa el PROBLEMA, no la solución. Una intención por ciclo.
2. **Spec** — convierte la intención en un contrato verificable en `specs/US-NNN-*.md`.
   Behavior observable + criterios de aceptación (negocio) + restricciones + no-objetivos + ejemplos.
3. **Diseño/Plan** — puerta de plan: el agente propone archivos y orden; el humano aprueba
   antes de escribir una línea. Para cambios triviales, el plan es una frase.
4. **Build (TDD)** — escribe PRIMERO el test derivado del criterio de aceptación.
   Luego implementa hasta que pase. Incrementos pequeños; compila/ejecuta tras cada cambio.
5. **Verificación** — pirámide: compila → unitaria → integración → E2E/real.
   Orden: edit → compila → unit → integración → real. Ningún nivel se salta "porque seguro está bien".
6. **CI/CD** — trunk-based, lotes pequeños, sin ramas eternas.
7. **Operación/Observabilidad** — logs de cada tool call `{tool, args, ok, ms}`.
8. **Feedback** — lo aprendido va a memoria persistente y se actualiza la spec.

## Reglas duras (lo que la IA no hace sola, hay que exigirlo)
- **Spec primero.** Sin `specs/US-NNN-*.md` no hay build. El chat no es el contrato.
- **TDD con agentes.** El test del criterio le da al agente un objetivo verificable y previene
  "tests que confirman un comportamiento ya roto".
- **Verificación adversarial.** Un revisor (humano o agente distinto al que generó) cuya
  tarea es REFUTAR, no aprobar. Lentes: correctitud, seguridad, rendimiento, "¿se reproduce?".
- **Definition of Done** antes de cerrar (ver command `/verify`).
- **Puertas de aprobación** en lo irreversible: push, deploy, borrar, publicar → confirmación explícita.
- **Lotes pequeños** (<~50 líneas de diff por revisión). Revisar 2000 líneas es exponencial.
- **Regenerable ≠ verificado.** El código se regenera desde la spec; la aceptación es humana y cara.
- **Trazabilidad** spec → código → test. Lo que no se rastrea, se pudre.
- **Principios de diseño** (la IA los nombra pero no los aplica): SRP, Open/Closed, SoC,
  DRY, KISS, YAGNI, IoC, AHA (avoid hasty abstractions). El agente NO sobre-genera ni duplica.
- **Sin ejecución de código del usuario.** Nunca `eval`/`exec` de texto del usuario.
