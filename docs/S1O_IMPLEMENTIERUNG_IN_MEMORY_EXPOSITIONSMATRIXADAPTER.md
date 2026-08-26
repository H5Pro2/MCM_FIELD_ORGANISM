# S1-O: Implementierung In-Memory-Expositionsmatrixadapter

Stand: 2026-08-09

Technische Entscheidung: `CELL_WISE_MATRIX_ADAPTER_BOUND_NO_CLASSIFICATION`

Implementierung: abgeschlossen

Vollmatrix ausgefuehrt: nein

Forschungslauf: nein

## Ziel

S1-O setzt die S1-N-Vorregistrierung als zellweise In-Memory-Schnittstelle
um. Die Implementierung kann genau eine explizit angeforderte Matrixzelle
ausfuehren. Sie startet keine automatische Vollmatrix und berechnet keine der
vier vorregistrierten S1-N-Klassifikationen.

## Implementierter Bestand

Der neue Adapter
[`s1o_exposure_retention_matrix.py`](../mcm_field_organism/s1o_exposure_retention_matrix.py)
enthaelt:

- ein unveraenderliches Inventar aus 32 Zellen;
- Dosen 1, 2, 4 und 8;
- `repeated-supports` und `continuous-support`;
- Nullkontaktdauern 0.0, 0.2, 0.8 und 1.6 Sekunden;
- stabile technische Zell-IDs;
- exponierte und zeitlich angeglichene Nullquellen;
- gemeinsame Probe- und Nullsupports;
- F3 bei Verfeinerung 2 oder 4;
- lineare Baseline, P0 und `eta=0` bei Verfeinerung 4;
- optionale uniforme M-Neutralisierung nur fuer F3;
- fluechtige S/H/M-Zustaende und vollstaendige Effektvektoren.

Der Ergebnisvertrag verbietet Klassifikation, Runtime-Rueckschreibung,
Memoryclaim und Lernclaim.

## Quellenmarginalien

Wiederholte und kontinuierliche Quellen besitzen pro Dosis exakt:

- dieselbe externe Gesamtdauer;
- dieselbe integrierte L1-Quelle;
- dieselbe integrierte L2-Quelle;
- dieselben aktiven Rezeptorwerte.

Nur die Ereignissegmentierung unterscheidet sich:

```text
repeated-supports event_count = 2 * dose_count
continuous-support event_count = 2
```

Die passiven Dauerintegrale werden aus ganzzahligen Organismus-Ticks mit
dezimaler Arithmetik gebildet. Dadurch werden mathematisch identische
Quellen nicht durch Gleitkomma-Summierungsreihenfolge verschieden
protokolliert.

## Technische Tests

Die S1-O-Tests pruefen:

1. exakt 32 eindeutige Zellen im vorregistrierten Kreuzprodukt;
2. exakte Dauer- und integrierte L1/L2-Angleichung je Dosis;
3. verschiedene Expositions- und Nullquelldigests;
4. exakte S/H-Angleichung vor der Probe;
5. nichtnegative M-Werte und Gesamtmasse 1.0;
6. gleiche Ereignisbudgets von exponiertem und Nullpfad je Zelle;
7. technische Effektsensitivitaet in einer aktiven F3-Zelle;
8. exakte P0- und `eta=0`-Nullwirkung in allen gebundenen Sentinelzellen;
9. exakte Nullwirkung nach uniformer M-Neutralisierung bei Dosis 8 und
   Nullkontaktdauer 0.0 beziehungsweise 1.6 Sekunden;
10. fehlende Klassifikations- und Rueckschreibungsautoritaet.

## Testergebnis

Der fokussierte angrenzende Verbund besteht mit:

```text
74 passed
36 subtests passed
```

Die bekannte Pytest-Cachewarnung `WinError 183` betrifft nur den lokalen
Cachepfad.

Eine einzelne aktive technische Sensitivitaetszelle wurde innerhalb der
Tests gebunden:

```text
cell_id:                 s1o.d2.repeated.gap-0p0
effect_linf:             0.00015734942154006817
preprobe_mass_linf:      0.0005373258290092622
source_event_count:      8
```

Dieser Einzelwert ist keine Dosis-, Erhaltungs-, Segmentierungs- oder
Mechanikklassifikation.

## Korrektur der passiven Invariantenberechnung

Der erste isolierte Test zeigte nur eine Summierungsabweichung der passiven
Quellenmetrik, etwa `1.1200000000000006` gegen `1.12`. Feldpfad und
Sentinelkontrollen waren davon nicht betroffen. Die Invariantenberechnung
wurde auf dezimale Tick-Arithmetik korrigiert; Gleichung, Quelle und Runtime
blieben unveraendert. Danach bestand der isolierte Verbund vollstaendig.

## Aussagegrenze

S1-O belegt nur, dass die vorregistrierte Matrix technisch und kausal sauber
ausgefuehrt werden kann. Die Vollmatrix wurde nicht ausgefuehrt. Der Stand
belegt nicht:

- Dosisgradation oder laengere Erhaltung;
- Praegung, Lernen oder Vergessen;
- MCM-Memory oder Feldzeitverdichtung;
- Ereignissegmentierung als Organismusfunktion;
- Organisation, Semantik, Topologie, Selbstregulation oder KI.

Es gab keinen Browserstart, keine reale Sensorik, keinen Forschungsrunner,
keinen Report und keine neue Laufnummer. Lauf 194 und Lauf 197 bleiben
unberuehrt.

## Bester naechster Schritt

S1-P implementiert einen begrenzten In-Memory-Vollmatrixkompositor ueber den
unveraenderten S1-O-Zelladapter. Er fuehrt F3 mit Verfeinerung 2 und 4 sowie
die lineare Baseline mit Verfeinerung 4 fuer alle 32 Zellen zusammen und
berechnet anschliessend passiv die vier bereits in S1-N registrierten
Klassifikationen.

S1-P darf keine Schwelle, Quelle oder Zelle veraendern und erzeugt weiterhin
keinen externen Runner, Report oder Laufnummer.

## Spaeterer Auswertungsstand S1-P

S1-P ist inzwischen in der
[`passiven Vollmatrixauswertung`](S1P_PASSIVE_VOLLMATRIXAUSWERTUNG_EXPOSITION_UND_ERHALTUNG.md)
umgesetzt. Alle Kontrollen bestehen. Die Matrix zeigt monotone
Dosisgradation, nichtmonotone Nullkontaktantwort,
Ereignissegmentierungssensitivitaet und eine vollstaendige lineare
Mechanikerlaerung unter 5 Prozent Rest. Naechster Schritt ist die statische
S1-Q-Ursachenpruefung der nichtmonotonen Nullkontaktantwort.
