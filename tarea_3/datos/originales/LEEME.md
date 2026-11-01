# Datos originales (descargados el 01/11/2026 con `scripts/obtener_datos.py`)

| Archivo | Fuente | Consulta |
|---|---|---|
| `ocde_global_revenue_statistics.csv` | OCDE, Global Revenue Statistics (DF_RSGLOBAL v2.1) | Gobierno general (S13), impuestos `_T, 1000, 1100, 1200, 1300, 2000, 3000, 4000, 5000, 5110, 5111, 5120, 6000`, % PIB, 2000–2024, todos los países |
| `ocde_socx/socx_publico_total_pib.csv` | OCDE, SOCX (DF_SOCX_AGG v1.0) | Gasto social público (ES10), total, % PIB, 2000–2024 |
| `banco_mundial/*.json` | Banco Mundial, WDI (API v2) | SI.POV.GINI, GC.TAX.TOTL.GD.ZS, NY.GDP.PCAP.PP.KD, SP.POP.TOTL; 2000–2024 |
| `cepalstat/ind_3127.json`, `ind_4407.json` | CEPALSTAT (API v1) | Gasto público social por funciones (% PIB); gasto social metodología SOCX (% PIB) |
| `wid/WID_data_XX.csv` (**no versionados**, ~400 MB) y `wid/WID_metadata_XX.csv` | WID.world, ZIP oficial `wid_all_data.zip` | Solo 15 países (PE, AR, BO, BR, CL, CO, EC, MX, PY, UY, DK, FI, NO, SE, IS), leídos con descargas parciales |
