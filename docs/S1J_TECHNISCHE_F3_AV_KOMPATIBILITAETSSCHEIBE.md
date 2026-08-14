# S1-J: Technische F3-AV-Kompatibilitaetsscheibe

Stand: 2026-08-09

Technische Entscheidung: `F3_CURRENT_AV_GEOMETRY_COMPATIBLE`

Implementierung: abgeschlossen

Forschungslauf: nein

## Ziel

S1-J prueft ausschliesslich, ob die in S1-I gewaehlte transparente
F3-Feldverlaufs-Referenz ohne neue Gleichung oder Parameter auf der heutigen
gemeinsamen AV-Geometrie technisch betrieben werden kann.

Die Scheibe ist kein Wiederholungs-, Praegungs-, Probe- oder Memoryversuch.
Sie verwendet einen synthetischen AV-Kontaktabschluss und ein anschliessendes
Nullkontaktfenster nur zur technischen Pruefung von Ereigniskausalitaet,
Zustandsgrenzen und Serialisierung.

## Implementierter Umfang

Die neue Komposition
[`s1j_f3_av_compatibility.py`](../mcm_field_organism/s1j_f3_av_compatibility.py)
verwendet unveraendert:

- die aktuelle synthetische AV-Fixture mit acht auditiven und achtzehn
  visuellen Feldneuronen;
- den vorhandenen asynchronen Rezeptor-Handoff;
- die vorhandene transiente F3-Runtime;
- die vorhandene F3-Kopplung;
- die vorhandene lineare gekoppelte F3-Baseline;
- Schema-2-Snapshot und Restore.

Es wurde kein neuer Feldalgorithmus eingefuehrt. Der Adapter erlaubt nur die
exakte F3-Kopplung oder die feste lineare gekoppelte Baseline. Er besitzt
keinen Observer-Rueckkanal und schreibt keine Ergebnisdatei.

## Feste Arme

| Arm | lambda | kappa | eta | Rolle |
|---|---:|---:|---:|---|
| `p1.active` | 1.0 | 0.5 | 1.0 | transparente F3-Referenz |
| `p1.active` | 1.0 | 0.5 | 1.0 | lineare gekoppelte Pflichtbaseline |
| `b.eta-null` | 1.0 | 0.5 | 0.0 | Rueckwirkungsablation |
| `p0.null` | 0.0 | 0.5 | 1.0 | exakter Nullarm |

Alle Arme verwenden Gesamtmasse 1.0. Gleichung, Parameter und
26-Neuronen-Geometrie sind nicht adaptiv.

## Technisches Ergebnis

Der fokussierte Verbund besteht mit:

```text
60 passed
19 subtests passed
```

Die Pytest-Cachewarnung `WinError 183` betrifft nur den lokalen Cachepfad und
nicht die Testergebnisse.

| Arm | Methode je Intervall | minimale M-Masse | Gesamtmasse | M-Abweichung Linf |
|---|---|---:|---:|---:|
| F3 | `ssprk33`, `ssprk33` | 0.0378219016309731 | 0.9999999999999998 | 0.0006396368305653655 |
| lineare Baseline | `ssprk33`, `ssprk33` | 0.037819948742795303 | 0.9999999999999998 | 0.0006415897187431602 |
| `eta=0` | `ssprk33`, `ssprk33` | 0.037815616361694865 | 0.9999999999999999 | 0.0006459220998435988 |
| P0 | `p0.exact`, `p0.exact` | 0.038461538461538464 | 1.0 | 0.0 |

Zusaetzlich gilt:

- Jeder Arm verarbeitet exakt vier technische Quellenereignisse.
- Alle 26 Feldneuronen bleiben gebunden.
- Alle M-Werte bleiben nichtnegativ.
- Aktivierung und schneller Nachhall bleiben im normierten Wertebereich.
- P0 besitzt exakt denselben schnellen Endzustandsdigest wie die bestehende
  neutrale Fast-Field-Runtime:
  `d0aa6b96e701a4f2dac427e25b87dcb00c934fabc230026abca7d12f8fe81f18`.
- Unmittelbar am ersten Kontaktabschluss bleibt M exakt uniform. Erst im
  spaeteren Feldintervall kann die vorhandene F3-Kopplung M veraendern.
- Ein Schema-2-Restore liefert am naechsten AV-Feldrand exakt denselben
  Snapshotdigest wie die ununterbrochene Fortsetzung.

## Aussagegrenze

S1-J belegt nur technische Kompatibilitaet. Die kleinen Unterschiede zwischen
F3, linearer Baseline und `eta=0` werden nicht funktional interpretiert. Es
gibt keinen Nachweis fuer:

- Lernen, Praegung oder Vergessen;
- MCM-Memory oder organisches Memory;
- relative Feldzeit oder Feldzeitverdichtung;
- inneren Kontext, Bedeutung oder Semantik;
- Organisation, Topologie oder Selbstregulation;
- feldbasierte KI.

Rohbild-, Audio- oder Weltpayloads werden im Ergebnis nicht gehalten. Es gab
keinen Browserstart, keinen Runner, keinen Report und keine Laufnummer.

## Abgrenzung

S1-J setzt weder 213ZZR bis 213ZZU noch Z4 oder historische K2-Laeufe fort.
W1-O und W1-Q werden nicht wiederholt. Lauf 197 und seine reservierten
Artefakte bleiben unberuehrt.

## Bester naechster Schritt

S1-K bindet vor jeder weiteren Ausfuehrung einen kleinen funktionalen
Pruefvertrag. Er muss eine technisch sinnvolle Minimalfunktion von blosser
Traegerbewegung unterscheiden:

1. gleiche aktuelle S/H-Feldlage vor einer identischen spaeteren Eingabe;
2. unterschiedliche kontrollierte vorherige AV-Kontakte;
3. F3, lineare gekoppelte Baseline, `eta=0` und P0 mit identischem Budget;
4. spaetere kausale Feldwirkung als Messrolle;
5. Neutralisierung und erneute Bindbarkeit als Pflichtgrenzen;
6. kein Memory- oder Lernclaim aus einem einzelnen Unterschied.

S1-K ist zuerst nur eine Vorregistrierung. Es veraendert keine Runtime und
fuehrt noch keinen Versuch aus.

## Spaeterer Vertragsstand S1-K

S1-K ist inzwischen in der
[`Vorregistrierung der minimalen F3-Feldverlaufsfunktion`](S1K_VORREGISTRIERUNG_MINIMALE_F3_FELDVERLAUFSFUNKTION.md)
gebunden. Sie verwendet die aktuelle 8+18-Geometrie, wiederholt Lauf 194
nicht und trennt F3, lineare Baseline, `eta=0`, P0 sowie externe
M-Neutralisierung. Naechster Schritt ist die reine in-memory
S1-L-Testimplementierung ohne Forschungsrunner oder Ausfuehrungsartefakt.
