# Source Material (extracted from user's USB: `E:\valuationapp\Trascender 2023`)

These files are the **methodological foundation** of the latam-valuation-engine CANVAS module.

They are stored here for **provenance and credit**, not as canonical sources. The methodology
they describe (Osterwalder, Bland, Giraldo+Ramos) is implemented in
`src/core/canvas/model.py`, `src/core/canvas/experiments.py`, and `src/core/comparables/bigfour.py`.

## Business Model Canvas (Osterwalder & Pigneur)

| File | What it gives us |
|------|-------------------|
| `29703_1_Lienzo_del_modelo_de_negocio.pdf` | The 9-block BMC: Segmentos, Propuesta de Valor, Canales, Relaciones, Ingresos, Recursos, Actividades, Aliados, Costos |
| `29708_1_El_lienzo_de_la_propuesta_de_valor.pdf` | The Value Proposition Design canvas: Trabajos / Frustraciones / Alegrías + Productos, Aliviadores, Creadores |

## 3 Types of Fit (Osterwalder et al.)

| File | What it gives us |
|------|-------------------|
| `29705_1_3_tipos_de_encaje.pdf` | Encaje problema-solución → producto-mercado → modelo de negocio. Implemented as `FitScore` in `core/canvas/model.py` |

## Value Proposition Design (worksheets)

| File | What it gives us |
|------|-------------------|
| `29720_1_Identifica_trabajos_de_gran_valor.pdf` | 5-dimension job scoring (importance, satisfaction, frequency, etc.) → opportunity_score |
| `29719_1_Hoja_de_trabajo_Un_dia_en_la_vida.pdf` | Ethnographic template — observing customer in their world |

## Strategic context

| File | What it gives us |
|------|-------------------|
| `29701_1_Del_fracaso_al_exito.pdf` | Common failure modes when scaling ideas |
| `29702_1_Innovar_en_empresas_establecidas.pdf` | Corporate innovation patterns |
| `29704_1_Vendeles_a_tus_colegas_el_diseno_de_la_propuesta_de_valor.pdf` | How to pitch PV design internally |

## Your own material

| File | What it gives us |
|------|-------------------|
| `Guía Usuario.pdf` | "Planeación Financiera bajo CANVAS" — the methodology that ties CANVAS blocks to PyG and DCF. Authored by Andrés Felipe Giraldo M. & Harold Mauricio Ramos P. The PyG/CANVAS mapping in `core/canvas/model.py::BusinessModel.to_financial_inputs()` is derived from this guide. |

## Licensing

All Osterwalder/Strategyzer material is Creative Commons BY-SA 3.0 (Business Model Foundry AG).
"Guía Usuario" is your own work — used with permission as the methodological anchor.
"Testing Business Ideas" (Bland & Osterwalder) full book not stored here due to size (61 MB);
only chapter excerpts in `D:/Temp/` were extracted for methodology review.
