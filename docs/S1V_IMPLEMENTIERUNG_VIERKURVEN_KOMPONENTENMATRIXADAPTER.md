# S1-V: Implementierung Vierkurven-Komponentenmatrixadapter

Stand: 2026-08-09

Implementierungsstatus: `CELL_ADAPTER_IMPLEMENTED_NOT_CLASSIFIED`

Formaler Forschungslauf: nein

## Ziel

S1-V implementiert den zellweisen Adapter fuer die in S1-T gebundene
Vierkurven-Komponentenpruefung. Er trennt fruehe kumulative Ledger von
tatsaechlich geschachtelten spaeten Intervallledgern und stellt vier
Modellarme bereit, ohne die Gesamtmatrix zu klassifizieren.

## Methodische Korrektur vor Implementierung

Die fruehen S1-R-Grenzen 0.025, 0.050 und 0.100 Sekunden besitzen jeweils
einen eigenen Nullsupport. Sie duerfen deshalb nicht als Abschnitte einer
einzigen Trajektorie subtrahiert werden.

S1-V bindet stattdessen:

```text
frueh kumulativ: 0 -> 0.025, 0.050, 0.100, 0.200 s
spaet kausal:    0.200 -> 0.400 s
                0.400 -> 0.800 s
                0.800 -> 1.600 s
```

Nur die spaeten Intervalle besitzen identische geschachtelte
0.100-Sekunden-Supportpfade. Ein nicht geschachteltes Fruehintervall wird vom
Adapter abgewiesen.

## Inventar

Fuer Dosis 1/8 und beide Quellenformen entstehen:

```text
16 fruehe kumulative Ledgerzellen
12 spaete Intervallledgerzellen
28 eindeutige Ledgerzellen insgesamt
```

Jede Zelle kann explizit mit Verfeinerung 2 oder 4 und einem der vier Arme
ausgefuehrt werden:

- F3;
- lineare gekoppelte Baseline;
- `kappa=0` ohne aktivierungsgetriebenen M-Beitrag;
- `eta=0` ohne M-Rueckwirkung auf S.

## Technische Beispielzelle

Fuer Dosis 8, wiederholte Supports und das geschachtelte Intervall
0.200 bis 0.400 Sekunden ergibt Verfeinerung 4:

| Arm | Transport-Linf | Antrieb-Linf | M-Inkrement-Linf | Bilanzrest-Linf |
|---|---:|---:|---:|---:|
| F3 | 0.002001301976056882 | 0.0014721537935324426 | 0.0010175967410791867 | 1.0167105872482818e-16 |
| linear | 0.0019110195967945469 | 0.0013874696116906806 | 0.0009756367432616833 | 1.1340754724198376e-16 |
| `kappa=0` | 0.0 | 0.0 | 0.0 | 0.0 |
| `eta=0` | 0.002016863407840678 | 0.0014792513076788017 | 0.001036465542050155 | 5.3939058081153846e-17 |

`kappa=0` bleibt aus uniformem M ohne aktivierungsgetriebene Verschiebung
vollstaendig uniform. Dies bestaetigt die technische Armidentitaet in dieser
Zelle, ist aber noch keine Vierkurvenklassifikation.

## Kontrollen

| Kontrolle | Ergebnis |
|---|---|
| 28 eindeutige Zellen | bestanden |
| frueh kumulativ / spaet geschachtelt getrennt | bestanden |
| unzulaessiges Fruehintervall | abgewiesen |
| vier Armidentitaeten | bestanden |
| Komponentenbilanz je Beispielarm | bestanden |
| Observertransparenz je Beispielarm | bestanden |
| `kappa=0`-Antrieb | exakt null |
| 2/4-Boeden je Arm | endlich und bildbar |
| keine Klassifikations-/Runtimeautoritaet | bestanden |

## Testergebnis

Der fokussierte S1-V-Verbund besteht mit:

```text
5 passed
16 subtests passed
6.67 s
```

Der gemeinsame Runtime-, S1-J-, S1-U- und S1-V-Verbund besteht mit:

```text
23 passed
27 subtests passed
10.10 s
```

Die bekannte Pytest-Cachewarnung `WinError 183` betrifft nur den lokalen
Cachepfad.

## Aussagegrenze

S1-V hat nicht alle 28 Zellen ueber alle vier Arme und beide Verfeinerungen
komponiert. Die S1-T-Rollen zu direktem Antrieb, reziproker Rueckwirkung und
linearer Erklaerung bleiben unausgefuehrt.

Es gibt keinen Befund zu Memory, Lernen, Vergessen, Feldzeit, innerem
Kontext, Semantik, Organisation, Topologie, Selbstregulation oder KI. Es gab
keinen Browserstart, keine reale Sensorik, keinen externen Runner, keinen
Report und keine neue Laufnummer. Lauf 197 bleibt unberuehrt.

## Bester naechster Schritt

S1-W implementiert den begrenzten passiven Vollkompositor fuer die 28
Ledgerzellen. Er berechnet getrennte 2/4-Boeden, prueft Bilanzschluss und
Observertransparenz und wendet danach exakt die drei in S1-T
vorregistrierten Rollen an. Fruehe kumulative Ledger duerfen nur deskriptiv
ausgegeben werden; die Ursachenentscheidungen verwenden ausschliesslich die
drei geschachtelten spaeten Intervalle.

## Spaeterer Auswertungsstand S1-W

S1-W hat die 28 Zellen inzwischen passiv und reproduzierbar komponiert.
`kappa=0` entfernt alle spaeten Anstiege; `eta=0` veraendert alle 12 spaeten
Ledger. Ein direkter Komponentenrest von maximal 5.7524 Prozent liegt knapp
oberhalb der linearen Grenze und muss vor weiterer Deutung gezielt bei
Verfeinerung 4/8 repliziert werden.
