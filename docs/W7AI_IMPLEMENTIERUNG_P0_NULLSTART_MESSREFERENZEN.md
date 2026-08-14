# W7-AI: Implementierung der P0-Nullstartmessreferenzen

## Entscheidung

`P0_ZERO_START_MEASUREMENT_REFERENCES_COMPLETE`

W7-AI implementiert den statischen Vertrag W7-AH vollstaendig im
Arbeitsspeicher. Es wurden keine CAP/P0-Werte verglichen und kein
Forschungslauf, Browser oder Report erzeugt.

## 1. Implementierter Umfang

- genau 35 Referenzen fuer sieben W7-Y-Pfade und Checkpoints 0 bis 4;
- je Rolle ein frischer substrat- und entwicklungsfreier P0-Zustand;
- S = H = 0 am jeweiligen Checkpointtick;
- getrennte Zustands- und Feldobjekte fuer alle sieben Starts eines
  Checkpoints;
- dieselbe W7-Y-Probe, Uhr, Geometrie und P0-Parameterbindung wie W7-R;
- insgesamt 3.185 passive S/H-Samples an echten Abschlussgrenzen;
- genau eine `W7PFieldMeasurement(model_id = "p0")` je Rolle.

## 2. Passive W7-R-Beobachtung

`produce_w7r_p0_s_completion_states` besitzt nun einen privaten optionalen
Beobachter. Er erhaelt ausschliesslich schreibgeschuetzte S/H-Arrays und muss
`None` zurueckgeben. Der bestehende Produktions- und Zustandsdigest bleibt
davon unberuehrt; es gibt keinen neuen Export aus Paketwurzel oder
`current_api`.

Fuer jede Rolle stimmen beobachtete, unbeobachtete und mit vertauschter
Modalitaetseingangsreihenfolge erzeugte W7-R-Produktion ueberein. Die
beobachteten S-Werte treffen alle W7-R-Ereigniszustaende, das letzte S/H-
Sample trifft den exakten W7-R-Endzustand.

## 3. Gegenkontrollen

- kanonische und umgekehrte Verarbeitung der 35 Rollen sind je Rolle
  digestgleich;
- alle sieben Nullstarts eines Checkpoints sind wertgleich und
  objektgetrennt;
- P0 enthaelt weder M noch Kapazitaets-, Regions- oder Entwicklungsrollen;
- W7-AA-, W7-AC-, W7-AE- und W7-AG-Eingangsdigests bleiben unveraendert;
- Ergebnisobjekte lehnen veraenderte Digests ab.

Der globale Digest lautet:

`8b194514f4ac4074039891d6ba0e0db0ffdd9f28c157ce8a2bac66b238d771f5`

## 4. Verifikation

- W7-AI fokussiert: `10 tests, OK` in 419,411 Sekunden;
- direkt betroffene W7-R-Suite: `13 tests, OK`;
- Python-Kompilation der beiden Module und der W7-AI-Tests: erfolgreich.

## 5. Aussagegrenze

`p0_absolute_comparison_ready = true` bedeutet nur, dass fuer alle 35 Rollen
eine technisch gebundene, passive und gegen W7-R gepruefte P0-Messseite
vorliegt. Es ist kein CAP/P0-Vergleichsergebnis und kein Nachweis fuer
Memory, Feldzeit, Organisation, Topologie, Semantik, Selbstregulation oder
KI.

## 6. Verwendete Quellen

- `docs/W7AH_VERTRAG_P0_NULLSTART_MESSREFERENZEN.md`
- `mcm_field_organism/w7r_p0_s_completion_producer.py`
- `mcm_field_organism/w7y_seven_path_source_plan.py`
- `mcm_field_organism/w7ag_passive_cap_measurement_handoff.py`
- `mcm_field_organism/w7ai_p0_zero_start_measurement_reference.py`
- `tests/test_w7r_p0_s_completion_producer.py`
- `tests/test_w7ai_p0_zero_start_measurement_reference.py`

## 7. Naechster Schritt

W7-AJ soll statisch festlegen, wie die vorhandenen 35 CAP- und 35 P0-
Feldmessungen rollen- und tickgleich gepaart werden duerfen. Der Vertrag muss
zulaessige absolute Messdifferenzen und Gegenkontrollen vorregistrieren, ohne
bereits Werte zu berechnen, Schwellen nachzuziehen oder einen Befund zu
formulieren.
