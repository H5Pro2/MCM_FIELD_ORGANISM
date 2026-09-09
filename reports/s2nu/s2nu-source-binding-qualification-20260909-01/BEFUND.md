# S2-NU: neutrale Quellenbindungsqualifikation

- Lauf-ID: `s2nu-source-binding-qualification-20260909-01`.
- Ergebnis: `S2NU_SOURCE_BINDING_QUALIFIED`, **16/16**, Exit-Code `0`.
- Genau ein vorregistrierter Testaufruf, kein Retry. Inventar und Grenzen:
  [Qualifikationsbindung](../QUALIFIKATIONSBINDUNG.md),
  [Vorregistrierung](preregistration.json), [Protokoll](stderr.txt).
- Ergebnisdigest: `4626a137b517fe82c78d2e412cd138732ab4276f5e7b7b5193baf47b8e189d7d`.
- Alle elf gebundenen Dokument-/Quellhashes vor und nach dem Aufruf identisch;
  vollstaendige Werte in [result.json](result.json).

Geprueft wurden Quellen- und Rezeptidentitaeten, native Zeitindizes,
s02/s03-Permutation bei getrennten Herkunftsbindungen, Phasenpositionen,
lokale beziehungsweise fortlaufende Synthesezeit, einmalige Float32-Rundung,
Nullmultiplikatoren, getrennte Planwurzeln, Manipulationsabwehr,
Unveraenderlichkeit sowie feste Groessen- und Ausgabegrenzen.

Die numerischen Generatorpruefungen verwendeten ausschliesslich abweichende
neutrale Partialparameter und wenige Samples. Keine NU-Payloads, Rezeptoren,
NJ-Projektionen, Banddifferenzen, Ordnungskriterien oder Systempfade wurden
ausgefuehrt. Planmetadaten wurden geprueft, nicht deren spaetere Messwerte.

Die ungeordnete Kontrolle akzeptiert als gebundene funktionale Felder nur
`profile_digest` und `values_f64le_sorted`. Zusaetzliche Herkunfts-/Zeitfelder
wurden neutral abgewiesen. Das qualifiziert diese Vertragsbindung, noch
keinen zukuenftigen funktionalen Kontrollarm mit realen Rezeptorwerten.

Der vorhandene Sealer stellt weiterhin Kanonisierung, Umgebungsbindung,
Publikation und Kollisionsgruppierung bereit. Kein historischer Haupteinstieg
wurde umgewidmet oder aufgerufen. `MAIN_GATE=False`.
