# Trazabilidad requisito → prueba → resultado (H3)

Commit base `e3c0ba25ebf6744c25f5f815b714427c64d02da5` · 2026-11-12T10:18:34.342710+00:00

SHA-256 del conjunto de código/configuración/pruebas: `b1ee128ddaa79e9749c1b02b623bfca3eb54b4623cd29cec7cdb16e9c37b8f66`. Manifiesto y cambios locales en `ejecucion_H3.json`.

Python 3.12.10, pytest 9.2.0; 124 pruebas; código de salida 0. Solo simulación/dobles/inspección. PASS no acredita un requisito completo.

| Requisito | Modo de verificación (H1 6.3) | Casos sin robot | Estado H3 |
|---|---|---|---|
| RD-01 | software | TEST-10, TEST-36 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RD-02 | software | TEST-01, TEST-34 | Dobles del adaptador; falta Vosk con modelos ES/EN reales |
| RFI-01 | software | TEST-31, TEST-33, TEST-34 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RF-01 | integración | TEST-01, TEST-03, TEST-04, TEST-14, TEST-19 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RF-02 | software | TEST-07, TEST-14 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RFI-02 | software | TEST-08, TEST-25, TEST-26, TEST-34 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RF-03 | físico | TEST-15, TEST-23 | Registro/estado simulado; postura física no observada |
| RF-04 | software | TEST-02, TEST-03, TEST-06, TEST-28, TEST-29, TEST-30, TEST-37 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RF-05 | software | TEST-24, TEST-27 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RF-06 | software | TEST-14, TEST-15, TEST-24, TEST-28 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RF-07 | software | TEST-19, TEST-20 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RF-08 | físico | TEST-21, TEST-22 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RF-09 | físico | TEST-24 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RF-10 | software | TEST-17, TEST-18, TEST-35, TEST-37 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RI-01 | integración | TEST-08 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RI-02 | integración | TEST-05, TEST-07, TEST-14 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RI-03 | software | TEST-11, TEST-12, TEST-25 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RI-04 | software | TEST-12, TEST-19 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RI-05 | software | TEST-11, TEST-12, TEST-30 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RI-06 | software | TEST-17, TEST-35 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RI-07 | software | TEST-17, TEST-18, TEST-24 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RM-01 | software | TEST-09, TEST-14, TEST-15, TEST-17, TEST-23, TEST-28, TEST-32 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RM-02 | software | TEST-09, TEST-25, TEST-26, TEST-31, TEST-32 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RO-01 | físico | — | Pendiente (ensayo físico/integración) |
| RO-02 | software | TEST-11, TEST-12, TEST-25 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RR-01 | integración | TEST-29 | Rechazo lógico probado; precisión no medida (OPEN-13) |
| RR-02 | integración | TEST-16 | Latencia simulada; estimación Vosk con dobles, sin medida física |
| RR-03 | software | TEST-10 | Inspección estática; falta reconocimiento real sin Internet |
| RS-01 | software | TEST-02, TEST-03, TEST-05, TEST-07, TEST-11, TEST-13, TEST-28, TEST-29, TEST-30, TEST-33, TEST-34, TEST-35, TEST-37 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RS-02 | software | TEST-08, TEST-25, TEST-26, TEST-27, TEST-33 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RS-03 | físico | TEST-05, TEST-22 | Controles software auxiliares; intervención independiente pendiente |
| RU-01 | software | TEST-12, TEST-19, TEST-20 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RU-02 | software | TEST-28, TEST-30 | Casos software PASS; alcance parcial, integración/aceptación pendiente |
| RU-03 | software | TEST-11, TEST-12, TEST-13, TEST-21, TEST-31, TEST-35 | Casos software PASS; alcance parcial, integración/aceptación pendiente |

Los requisitos de modo «integración» y «físico» se cierran en H4 (docs/H3/casos_de_prueba.md §3).
