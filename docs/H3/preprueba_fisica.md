# Alcance de las comprobaciones físicas disponibles

Los ensayos físicos del equipo ya se realizaron y no se efectuarán más para esta
entrega. El protocolo previo permanece en Git; esta ficha registra su cobertura,
sin convertir lo no observado en tareas obligatorias.

| Caso del protocolo anterior | Evidencia disponible |
|---|---|
| F-A01 Órdenes simples | USR-02/03/06: funcionamiento nominal por texto/voz comunicado; frases exactas no documentadas |
| F-A02 Secuencias | USR-04/07: cola y secuencias físicas correctas; número exacto de acciones y tiempos no aportados |
| F-A03 Parada/cierre | Comportamiento software probado; resultado físico específico no documentado |
| F-A04 Fallo de enlace | Reenvío corregido y probado con puerto falso; no revalidado físicamente |
| F-A05 Audio ajeno | USR-09: falsas acciones en simulación con micrófono; no confundir con ensayo físico |
| F-A06 Error de captura | Pruebas con sustitutos, no fallo físico provocado |
| F-A07/F-A08 Precisión/latencia | Sin mediciones; no se dan porcentajes ni tiempos físicos |
| F-A09 Offline | Arquitectura local; no consta sesión física documentada sin Internet |
| F-A10 Coreografías/BLE | Sin evidencia individual completa; funcionalidad conservada |

Detalle y origen: [validacion_usuario.md](validacion_usuario.md). El registro
[registro_h4.csv](registro_h4.csv) distingue casos sin registro específico y resultados
comunicados. No se asignan vídeos, firmas, fechas de ensayo o aprobaciones inexistentes.
