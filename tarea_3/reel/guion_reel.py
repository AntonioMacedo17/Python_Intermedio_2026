"""Guion aprobado del reel (01/11/2026) y verificación de sus cifras contra web/data/indicadores.json.

Cada escena tiene:
- "frase": lo que dice la voz clonada. Números en palabras y siglas escritas como se pronuncian en el Perú
  (IGV -> "i ge be", PIB -> "pib", OCDE -> "o ce de e").
- "sub": lo mismo para los subtítulos, con cifras y siglas normales.
- "cifra" y "etiqueta": lo que se ve en grande en pantalla.

Uso:  python guion_reel.py      (verifica las cifras y escribe guion.json)
"""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
IND = json.loads((AQUI.parent / "web" / "data" / "indicadores.json").read_text(encoding="utf-8"))

TITULO = "¿Quién financia al Estado peruano?"
SUBTITULO = ("Estructura tributaria, desigualdad y gasto social en el Perú frente a América Latina, "
             "la OCDE y los países nórdicos")
FUENTE = "OCDE, WID.world, Banco Mundial, MEF"

ESCENAS = [
    {"frase": "Cada vez que compras algo, pagas i ge be. Pero ¿quién sostiene realmente al Estado peruano?",
     "sub": "Cada vez que compras algo, pagas IGV. Pero ¿quién sostiene realmente al Estado peruano?",
     "cifra": "", "etiqueta": "¿Quién financia al Estado peruano?"},
    {"frase": "En dos mil veintitrés, el Perú recaudó dieciséis coma siete por ciento de su pib. "
              "La o ce de e, treinta y tres coma siete. Los nórdicos, más de cuarenta y uno.",
     "sub": "En 2023, el Perú recaudó 16.7 % de su PIB. La OCDE, 33.7. Los nórdicos, más de 41.",
     "cifra": "16.7 %", "etiqueta": "del PIB recaudó el Perú en 2023"},
    {"frase": "El i ge be recauda tres coma seis veces lo que la renta de las personas. "
              "Lo directo lo pagan sobre todo las empresas, y sube y baja con la minería.",
     "sub": "El IGV recauda 3.6 veces lo que la renta de las personas. "
            "Lo directo lo pagan sobre todo las empresas, y sube y baja con la minería.",
     "cifra": "3.6×", "etiqueta": "recauda el IGV por cada sol del impuesto a la renta de personas"},
    {"frase": "La mitad de peruanos con menores ingresos recibe apenas ocho coma tres por ciento del ingreso "
              "nacional. Y la propiedad casi no tributa.",
     "sub": "La mitad de peruanos con menores ingresos recibe apenas 8.3 % del ingreso nacional. "
            "Y la propiedad casi no tributa.",
     "cifra": "8.3 %", "etiqueta": "del ingreso nacional va a la mitad con menores ingresos"},
    {"frase": "El gasto social es siete coma cinco por ciento del pib; en la o ce de e, casi veintiuno. "
              "Entre cincuenta países, recaudar y gastar más se asocia con menos desigualdad. Asociación, no causa.",
     "sub": "El gasto social es 7.5 % del PIB; en la OCDE, casi 21. "
            "Entre 50 países, recaudar y gastar más se asocia con menos desigualdad. Asociación, no causa.",
     "cifra": "7.5 %", "etiqueta": "del PIB en gasto social público"},
    {"frase": "Además, el Estado deja de recaudar más de dos por ciento del pib en exoneraciones y otros beneficios.",
     "sub": "Además, el Estado deja de recaudar más de 2 % del PIB en exoneraciones y otros beneficios.",
     "cifra": "2.16 %", "etiqueta": "del PIB en gasto tributario (estimación oficial 2026)"},
    {"frase": "Explora los datos en el dashboard. El enlace está en la descripción.",
     "sub": "Explora los datos en el dashboard. El enlace está en la descripción.",
     "cifra": "", "etiqueta": "Explora el dashboard: enlace en la descripción"},
]


def verificar():
    """Cada cifra del guion contra indicadores.json (redondeo a un decimal, como en pantalla)."""
    r = lambda v, d=1: round(v, d)
    pt, rp, gs, cp = IND["presion_tributaria"], IND["renta_personas_pib"], IND["gasto_social_pib"], \
        IND["correlaciones_parciales_lnPIBpc"]["presion_tributaria~gini_bm"]
    d, dn = IND["desigualdad_PER_2019_2023"], IND["desigualdad_nordicos_2019_2023"]
    chequeos = {
        "año 2023": IND["anio_referencia"] == 2023,
        "Perú 16.7": r(pt["PER"]) == 16.7, "ALC 21.5": r(pt["ALC"]) == 21.5, "OCDE 33.7": r(pt["OCDE"]) == 33.7,
        "nórdicos 41.2 (> 41)": r(pt["Nordicos"]) == 41.2,
        "IGV/renta personas 3.6": r(IND["igv_sobre_renta_personas_PER"]) == 3.6,
        "renta personas 1.8 / OCDE 8.2 / nórdicos 14.4": (r(rp["PER"]), r(rp["OCDE"]), r(rp["Nordicos"])) == (1.8, 8.2, 14.4),
        "empresas > OCDE": IND["renta_empresas_pct"]["PER"] > 2 * IND["renta_empresas_pct"]["OCDE"],
        "50 % inferior 8.3 vs 23.5": (r(d["bottom50_ingreso"]), r(dn["bottom50_ingreso"])) == (8.3, 23.5),
        "propiedad < 1 % PIB": IND["propiedad_pib"]["PER"] < 1,
        "gasto social 7.5 / OCDE 20.8 (casi 21) / nórdicos 24.8": (r(gs["PER"]), r(gs["OCDE"]), r(gs["Nordicos"])) == (7.5, 20.8, 24.8),
        "50 países, ρ parcial < 0 y p < 0.05": cp["n"] == 50 and cp["rho"] < 0 and cp["p"] < 0.05,
    }
    for k, ok in chequeos.items():
        print("OK   " if ok else "FALLA", k)
    # 2.16 % del gasto tributario 2026 no sale de nuestros datos: SUNAT, Informe N.º 000045-2025-SUNAT/1V3000
    return all(chequeos.values())


if __name__ == "__main__":
    assert verificar(), "hay cifras que no coinciden"
    (AQUI / "guion.json").write_text(json.dumps({"titulo": TITULO, "subtitulo": SUBTITULO, "fuente": FUENTE,
                                                 "escenas": ESCENAS}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("palabras:", sum(len(e["frase"].split()) for e in ESCENAS))
