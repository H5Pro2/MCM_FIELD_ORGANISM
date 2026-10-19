# Struktur/Lage: tatsächliche PPB-Distanzregel

`structure-location-ppb-20260912-01`: sechs neue Anschlussprüfungen in genau
einem Aufruf bestanden; danach genau eine Offline-Tabelle und eine unabhängige
read-only Prüfung, **EVIDENCE_VALID**. Kein Retry. Historische Prüfungen
nicht wiederholt. Quellen-/Rezeptor-/Form- und Memoryaufrufe: null.

Vollständige 14 Rohvektoren aus dem abgeschlossenen Vergleich wurden gegen
Quellen-, Zeit-, Profil-, Versiegelungs- und Ergebnisbindungen geprüft.
Die heutigen Dateien `_ppb1_reference.py` und `_s2jw_default_live_profile.py`
stimmen mit ihren in der ursprünglichen e03/e04-Diagnose gebundenen Hashes
überein. Verwendet wurde `normalized_mean_l1_distance`, also
`math.fsum(abs(left-right) ...)/288`, mit unverändertem `distance <= 0.01`.
Keine Bank, kein Prototyp und kein neuer Memoryzustand erzeugt.

## Alle Beziehungen

Korrespondierende H0-/H1-Paare liefern jeweils denselben gespeicherten Abstand.
Die folgende Gruppierung zählt trotzdem beide getrennt gebundenen Paare.

| Paar H0/H1 | Beziehung | PPB-Abstand Binary64 | <=0,01 |
| --- | --- | --- | --- |
| 0/10 | A→A/P1, Lage | `0x1.cc7721cc7721cp-7` | nein |
| 1/11 | A→A/P2, Lage | `0x1.0bb6610bb6612p-7` | ja |
| 5/15 | B→B/P1, Lage | `0x1.d72c81d72c820p-8` | ja |
| 6/16 | B→B/P2, Lage | `0x1.0bb6610bb6613p-7` | ja |
| 2/12 | A→B/P0, Struktur | `0x1.0101010101010p-5` | nein |
| 3/13 | A→B/P1, Struktur | `0x1.f74ca1f74ca20p-6` | nein |
| 4/14 | A→B/P2, Struktur | `0x1.13be6913be692p-5` | nein |
| 7/17 | B→A/P0, Struktur | `0x1.0101010101010p-5` | nein |
| 8/18 | B→A/P1, Struktur | `0x1.1e73c91e73c92p-5` | nein |
| 9/19 | B→A/P2, Struktur | `0x1.be2ff713854c6p-6` | nein |
| 20/21 | Exaktkopien H0/H1 | `0x0.0p+0` | ja |

Damit erfüllen **6/8 Lagebeziehungen**, **0/12 Strukturänderungen** und
**2/2 Exaktkontrollen** die Grenze. Die beiden ausgeschlossenen Lagefälle
sind dieselbe Geometrieänderung unter zwei Hintergründen, keine unabhängigen
Robustheitsreplikate. Es gibt hier kein Zusammenfassen unterschiedlicher
Strukturen durch die geprüfte Paargrenze.

**Alle 22 Abstände sind bitgleich zur bisherigen sum-Rechnung.**
Alle gespeicherten Differenzen zwischen beiden Rechnungen sind null;
kein numerischer Wechsel und kein Grenzentscheidungswechsel. Die andere
Summation ist hier keine Erklärung einer ausgebliebenen Stabilisierung.

## Architekturgrenze

Gute Abstandsordnung und Einhaltung der festen Matchgrenze sind verschieden:
Die Rohdarstellung ordnet hier Lage vor Struktur, trotzdem schließt die
feste PPB-Regel A/P1 gegenüber A/P0 aus. Dies begründet die konkrete Frage,
ob ein tatsächlicher Prototypverlauf diese Beziehung verliert oder erhält.
Es beweist keinen solchen Verlauf und erklärt nicht den gesamten realen Film.
Prototypupdates, Konkurrenz, Support und Ablauf wurden nicht ausgeführt.
Keine Schwellenwahl, Formintegration, Objektidentität oder Lernbindung.

## Arbeit und Bilanz

22 produktive Distanzaufrufe: **6.336 Differenzen**. Unabhängig: 6.336 bereits
verifizierte gespeicherte Terme in 22 fsum-Summen, **null neue Differenzen**.
Die Offline-Prüfung ruft den produktiven Helfer nicht erneut auf. Das ist
unabhängige Summation, keine erneute RGB-/Rezeptorrekonstruktion.
Neutrale Zusatzarbeit wurde vor dem Test separat
[präzisiert](PPB_OFFLINE_WORK_BINDING.md).

Vollständige Reservebilanz: **991.054 / 4.194.304 Byte**, Metadaten
**45.623 / 98.304 Byte**, inklusive 8.192 Byte gemeinsamer Berichtreserve
für Arbeitsnachtrag und diesen Befund. Keine Grenzverletzung. Tabelle und
Verifikationsbeleg liegen in der gleichnamigen Laufablage; ihr Tabellendigest:
`bc8ec19ff908272f1260f3667449136da97628b01cdd2aaab38a4f02fcd86cf1`.
Gates blieben False; keine weitere Ausführung freigegeben.
