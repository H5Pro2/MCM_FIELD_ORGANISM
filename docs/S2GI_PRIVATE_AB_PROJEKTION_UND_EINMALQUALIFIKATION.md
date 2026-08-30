# S2-GI: Private A/B-Projektion und Einmalqualifikation

## Auftrag und Grenze

S2-GI implementiert die in S2-GH korrigierte, funktional verlustfreie und
diagnostisch begrenzte A/B-Schattenprojektion. Einziger Eingang ist ein
bereits validiertes `PerceptualContextBundle` aus S2-GC.

Die Projektion fuehrt keine Speicherabfrage, Zustandsfortschreibung,
Match-Neuberechnung, Kontextverwendung oder Feldwirkung aus.

Qualifikations-ID:

`s2gi-two-area-projection-qualification-20260830-01`

Technischer Ausgangsstand:

`b4955cc1319d9372d17247c77e20cec8c8bf0801`

## Implementierter Umfang

Neu angelegt wurden genau:

1. `tools/_s2gi_private_two_area_context_projection.py`;
2. `tests/test_s2gi_private_two_area_context_projection.py`.

Die Projektion erzeugt exakt zwei oeffentliche Bereiche:

- `A_RECENT` mit getrennten Referenzen auf `B4_RECENT`, `TSPM_FAST` und den
  B4-Kurzfolgenbefund;
- `B_STABLE` mit dem unveraenderten `TSPM_SLOW`-Rollenfinding.

Ein `NO_STABLE_SLOW_MATCH` bleibt `ABSENT_VALID`. Es werden keine Supports,
Slots, Distanzen oder Ursachen rekonstruiert. Gleiche Inhalte aus B4 und Fast
bleiben getrennte, quellgebundene Findings.

Die Ausgabe ist unveraenderlich und bindet unveraendert:

- S2-GC-Bundledigest;
- Binding-, Konfigurations-, Composite-Zustands-, Probe- und Quelldigest;
- Vor- und Nachzustandsdigest;
- alle drei Rollenfindingdigests;
- Kurzfolgen- und Ressourcenledgerdigest.

`automatic_selection` bleibt `None`.

## Statischer Vorlauf

Vor der Ausfuehrung wurden statisch bestaetigt:

- beide neuen Dateien sind syntaktisch gueltig;
- das Projektionsmodul importiert direkt ausschliesslich die private
  S2-GC-Bundlegrenze;
- genau 14 geordnete Testdefinitionen sind vorhanden;
- S2-GC-Implementierung und bestehende S2-GC-Tests sind unveraendert;
- keine Speicher-, Koordinator-, API-, Snapshot- oder Feldfunktion wurde in
  das Projektionsmodul aufgenommen.

Quellbindungen des Abschlussstands:

| Quelle | SHA-256 |
| --- | --- |
| `tools/_s2gi_private_two_area_context_projection.py` | `21bc206dc37f8a9f477c02eac7d14ff22e6924bbdb54eb5153122ec296cdd587` |
| `tests/test_s2gi_private_two_area_context_projection.py` | `592b51525c553d856b5c2d861d4c7a47ce682a96d4835ca45584f203a43efb56` |
| `tools/_s2gb_private_perceptual_context_bundle.py` | `0fba7b0323fe772c481eb5261b9640e4a5b00d7da3ceb1a7e0f81c6d9f54bf49` |
| `tests/test_s2gb_private_perceptual_context_bundle.py` | `a557defc4a5309b86b3f9b7d56d78c3db3e61784b67706335cc3922a9519e55e` |

## Einmalige neutrale Qualifikation

Es erfolgte genau ein Aufruf:

```text
python -m unittest tests.test_s2gi_private_two_area_context_projection -v
```

Ergebnis:

```text
Ran 14 tests in 0.025s

OK
EXIT_CODE=0
```

Die 14 neutralen Tests decken ab:

1. vollstaendige Belegung und exakt zwei Bereiche;
2. partielle stabile Slow-Belegung;
3. vollstaendige gueltige Abwesenheit;
4. getrennte B4- und Fast-Teilrollen ohne Verschmelzung;
5. Kurzfolge ausschliesslich in A;
6. beide stabilen Slow-Komponenten in B;
7. deterministische bytegleiche Ausgabe;
8. Unveraenderlichkeit von Eingang und Ausgabe;
9. beschaedigten Bundledigest;
10. falsche Rollenreihenfolge;
11. ungueltige Quellenbindung;
12. falsche Komponentendimension;
13. Ueberschreitung der Folgenkapazitaet;
14. Zurueckweisung eines dritten oeffentlichen Bereichs.

## Statischer Abschlussaudit

Der Abschlussabgleich bestaetigt:

- genau ein neues privates Projektionsmodul und eine neue Testdatei;
- alleiniger Projektionsinput ist der exakte S2-GC-Bundletyp;
- B4, Fast und Kurzfolge bleiben in `A_RECENT` getrennt;
- nur stabile vollstaendige oder partielle Slow-Befunde gelangen nach
  `B_STABLE`;
- `ABSENT_VALID` erzeugt keinen Kandidaten und keine Diagnosewerte;
- alle Projektionsergebnisse sind unveraenderlich, digestgebunden und
  ressourcenbegrenzt;
- S2-GC, B4, TSPM-1, PPB-1, Koordinator, API, Snapshot und Feldpfad blieben
  unveraendert;
- es gab keinen Kontextvergleich und keinen Funktionslauf zur
  Kontextverwendung.

Technischer Abschlussstatus:

`PRIVATE_READ_ONLY_TWO_AREA_CONTEXT_PROJECTION_VALID`

Dieser Status bestaetigt nur die private A/B-Schattenprojektion. Ein Nutzen
von `CURRENT_PERCEPTION_PLUS_TWO_AREA_CONTEXT` gegen
`CURRENT_PERCEPTION_ONLY` ist noch nicht kontrahiert oder geprueft.
