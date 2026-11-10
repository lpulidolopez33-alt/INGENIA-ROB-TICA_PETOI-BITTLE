# Lista de comprobación de la especificación — VOICE-BITTLE

**Versión**: 0.3 · **Fecha**: 2026-11-10 · **Spec**: [../spec.md](../spec.md)

## Calidad del contenido
- [x] Una sola fuente de identificadores (H1 v0.2); sin FR-xxx ni REQ-xx.
- [x] Historias con escenarios de aceptación Dado/Cuando/Entonces.
- [x] Todos los escenarios ESC-01 a ESC-13 aparecen en una historia de usuario.
- [x] Las desviaciones respecto al diseño previo están anotadas (plan.md, D-08).

## Completitud de requisitos
- [x] Todos los requisitos de H1 §5 aparecen en spec.md §3 con su modo de verificación.
- [x] Los criterios de éxito son medibles (SC-001 a SC-008).
- [x] Los valores no confirmados están marcados como provisionales (U, T_aviso, T_enlace, T_escucha, RR-02).
- [x] Las cuestiones abiertas OPEN-01 a OPEN-15 tienen estado en spec.md §5.

## Preparación
- [x] Los requisitos no físicos tienen prueba automática y están trazados en `evidencias/trazabilidad_H3.md`.
- [x] Los casos físicos están definidos (TEST-F01 a F10) con campos de resultado en blanco.
- [ ] El equipo ha revisado y aprobado los valores provisionales (T042).
- [ ] OPEN-09 (intervención física independiente) resuelto: **bloquea los ensayos con movimiento**.
- [ ] OPEN-13 (diseño del ensayo RR-01) aclarado con el profesorado.
- [ ] Metadatos del H1 completos: código documental, autores y hash del commit (OPEN-08).
