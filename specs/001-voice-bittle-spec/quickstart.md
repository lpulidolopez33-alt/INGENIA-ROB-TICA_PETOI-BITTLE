# Validación rápida H3

Desde la raíz del checkout, PowerShell:

```powershell
.\.venv\Scripts\python.exe voice_bittle.py --demo
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe tools/generar_evidencias.py
```

Instalación y modelos: [GUIA.md](../../GUIA.md). Recuento ejecutado y huella:
[evidencias](../../evidencias/resultados_H3.md). No confundir casos con pruebas
parametrizadas. Los PASS son de lógica, simulación, dobles o inspección.
`--reconocedor vosk` usa audio real con transporte simulado; ensayo manual en la guía.
`--modo fisico` sale bloqueado, código 2. No sustituir componentes para saltarse
[preprueba_fisica.md](../../docs/H3/preprueba_fisica.md).
RR-01/02/03, RF-03 y RS-03 siguen pendientes de validación real según su alcance.
