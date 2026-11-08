# Reglas del proyecto · Tarea 4 (agente de investigación socioeconómica)

Estas reglas valen para cualquier sesión de Claude Code abierta en `tarea_4/`.

1. **Ninguna cifra escrita a mano ni inventada.** Todo número sale de código (herramientas MCP del BCRP o
   scripts de las Skills de ENAHO) y se valida antes de usarlo. Si una cifra no viene de una salida
   guardada o de una llamada repetible, no se escribe.
2. **Ponderar siempre con el factor correcto.** Personas (módulo 02 unido a sumaria): `facpob07`.
   Hogares (sumaria): `factor07` (y `factor07 × mieperho` para llevar a personas). Nunca promedios simples
   cuando corresponde una estimación ponderada.
3. **Asociación, no causalidad.** Las relaciones entre series del BCRP y la pobreza de ENAHO son descriptivas;
   se dice "se asocia" o "coincide con", nunca "causa" o "explica". Si se cruzan datos de distinto nivel de
   agregación o periodo, se reconoce la limitación.
4. **Citar siempre** el código de serie del BCRP, el periodo y la fuente (URL de la API o del INEI) junto a
   cada cifra.
5. **Commits descriptivos por avance**, repartidos a lo largo del trabajo.
6. **Si algo falla, decirlo.** Si una herramienta no responde, no encuentra datos o una validación no pasa,
   se informa el problema; no se rellenan ni se "corrigen" resultados para que coincidan con la referencia.
7. Los microdatos (`datos/`), el entorno (`.venv/`), cachés y claves nunca se versionan.
