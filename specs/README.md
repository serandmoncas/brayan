# Formato de Especificación (Spec como contrato)

> Toda construcción empieza con una spec versionada en este directorio.
> **Regla de oro:** si algo es importante, vive en la spec (archivo), no solo en el chat.
> Lo que solo existe en la conversación se pierde en el siguiente ciclo.

## Estructura de una spec
Cada archivo `specs/US-NNN-<nombre>.md` sigue este molde fijo:

```
## US-NNN — <Título>
**Como** <rol> que <contexto>
**quiero** <capacidad>
**para** <valor/por qué se paga esto>

**Valor:** <por qué importa para el negocio>
**Prioridad:** alta/media/baja   **Estimación:** S/M/L (1–N ciclos)

### Criterios de aceptación (reglas de NEGOCIO, no detalle técnico)
- [ ] CA1: <resultado observable que el negocio entiende y aprueba>
- [ ] CA2: <comportamiento en borde, ej. fallo sin red>
- [ ] CA3: <límite o invariante de negocio>

### Escenario Gherkin (cuando aplica)
  Dado  <estado inicial de negocio>
  Cuando <acción>
  Entonces <resultado observable>

### Restricciones (lo que el agente NO deduce)
- Idioma de mensajes: español
- Límite de salida: WEB_TRUNCATE_CHARS
- Sin ejecución de código del usuario

### No-objetivos (fuera de este ciclo)
- No se cubre búsqueda por imagen.

### Trazabilidad
- commit: <hash>  ·  test: test_<nombre>.py  ·  intención: sesión 2026-07-22
```

## Reglas
1. **Una spec = un incremento verificable.** Si no cabe en un ciclo, se parte (US-001a, US-001b).
2. **Los criterios son reglas de negocio**, no detalles de implementación (no "el campo X se guarda en tabla Y"). Si al refactorizar tienes que reescribir el criterio, no era criterio: era chequeo técnico.
3. **Cada CA se mapea 1-a-1 a un test.** El test afirma el resultado de negocio, no la mecánica interna.
4. **La spec es viva:** cada ciclo que descubre algo la actualiza. Una spec que diverge del código miente.

## Ejemplo (ya construido): buscar_web
Ver `specs/US-001-buscar-web.md`.
