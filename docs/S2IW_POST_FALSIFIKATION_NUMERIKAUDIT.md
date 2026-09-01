# S2-IW: Statischer Post-Falsifikations-Numerikaudit

## Grenze

S2-IW untersucht ausschliesslich die zwei abweichenden S2-IV-Faelle `c01`
und `c05`. Der gueltige Lauf `s2iv-five-status-20260901-01`, seine
Falsifikation und alle Belege bleiben unveraendert. Es wurden keine
Zustandsfunktion, kein Test und kein Runner ausgefuehrt. Speichermechanik,
Schwellen und Signallogik wurden nicht geaendert.

## Gebundene Ursache

Der S2-IC-Signalgeber und die unabhaengige Direktbaseline pruefen sichtbare
Werte mit exakter binaerer Gleitkommagleichheit. P1 wird viermal exponiert.
Der visuelle PPB-Prototyp wird dabei nach seiner Erzeugung zweimal mit der
unveraenderten Rate `0.01` gegen denselben Rezeptorwert aktualisiert:

```text
updated = (1 - 0.01) * previous + 0.01 * current
```

Fuer den P1-Hochwert entsteht dadurch:

```text
Probe       210/255 = 0.8235294117647058
Prototyp            = 0.8235294117647056
Abweichung          = 2.220446049250313e-16
ULP-Abstand         = 2
Anteil an 1/255     = 5.6621374255882984e-14
```

Der P1-Niedrigwert `30/255 = 0.11764705882352941` bleibt exakt erhalten.
Damit scheitert die exakte Sichtbarkeitspruefung in `c01` und `c05` genau an
den sichtbaren Hochwertpositionen `0, 2, 4, 6, 8`.

| Position | Probe | B-Prototyp | Betrag | ULP | Anteil an 1/255 | Rezeptorgitter |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0.8235294117647058 | 0.8235294117647056 | 2.220446049250313e-16 | 2 | 5.6621374255882984e-14 | 210 = 210 |
| 2 | 0.8235294117647058 | 0.8235294117647056 | 2.220446049250313e-16 | 2 | 5.6621374255882984e-14 | 210 = 210 |
| 4 | 0.8235294117647058 | 0.8235294117647056 | 2.220446049250313e-16 | 2 | 5.6621374255882984e-14 | 210 = 210 |
| 6 | 0.8235294117647058 | 0.8235294117647056 | 2.220446049250313e-16 | 2 | 5.6621374255882984e-14 | 210 = 210 |
| 8 | 0.8235294117647058 | 0.8235294117647056 | 2.220446049250313e-16 | 2 | 5.6621374255882984e-14 | 210 = 210 |
| 10 | 0.11764705882352941 | 0.11764705882352941 | 0 | 0 | 0 | 30 = 30 |
| 12 | 0.11764705882352941 | 0.11764705882352941 | 0 | 0 | 0 | 30 = 30 |
| 14 | 0.11764705882352941 | 0.11764705882352941 | 0 | 0 | 0 | 30 = 30 |
| 16 | 0.11764705882352941 | 0.11764705882352941 | 0 | 0 | 0 | 30 = 30 |

Die Tabelle gilt identisch fuer `c01` und `c05`, weil beide die maskierte
P1-Signalprobe gegen denselben aus vier P1-Expositionen gebildeten stabilen
B-Prototyp pruefen.

## Vergleichsfaelle

`c02` und `c03` verwenden auf allen sichtbaren Positionen ausschliesslich
die exakt darstellbaren Werte `0.0` und `1.0`. Die wiederholte
PPB-Aktualisierung erzeugt dort keinen binaeren Rest; A und B bleiben auf den
sichtbaren Positionen exakt anwendbar.

Die echten Ein-Stufen-Konflikte sind deutlich getrennt:

| Fall | Position | Probe | Kandidat | Betrag | ULP | Rezeptorgitter |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `c07` | 0 | 254/255 | 1 | 1/255 | 35322350018592 | 254 != 255 |
| `c08` | 2 | 1/255 | 0 | 1/255 | 4571171282956062736 | 1 != 0 |

Der ULP-Wert nahe null ist skalenabhaengig und nicht direkt mit dem ULP-Wert
nahe eins vergleichbar. Der absolute Abstand und die Rezeptorstufe sind hier
die belastbaren Vergleichsgroessen.

## Diagnostischer Regelvergleich

1. Exakte Gleichheit trennt `c07/c08`, verwirft aber auch den funktional
   gittergleichen B-Prototyp in `c01/c05`.
2. Die native normalisierte L1-Distanz beschreibt die Groessenordnung, aber
   die bestehenden Schwellen trennen die beiden Klassen nicht. Der P1-Drift
   betraegt ueber alle 18 Werte `1.1102230246251565e-16`; ein einzelner
   Rezeptorschritt betraegt als 18-Werte-Mittel `1/4590 =
   0.00021786492374727592`. Beide liegen unter der nativen visuellen
   PPB-Schwelle `0.01` und unter `44/765`.
3. Eine rein diagnostische Rueckbindung an das bekannte uint8-Rezeptorgitter
   trennt die vorliegenden Klassen: `round(255 * value)` ist fuer `c01/c05`
   gleich und fuer `c07/c08` um genau eine Stufe verschieden.

Punkt 3 zeigt, dass fuer diese konkreten Belege eine vorab formulierbare
numerische Aequivalenzklasse existiert. Er waehlt sie nicht als neue Regel.
Insbesondere sind Rundungsrichtung, Randfaelle zwischen Gitterzellen und
gemischte Prototypen erst prospektiv mit unabhaengigen Fixtures zu binden und
zu falsifizieren.

## Befund

`c01` und `c05` wurden durch binaeres Rundungsrauschen von zwei ULP auf den
P1-Hochwerten zu `VISIBLE_CONFLICT`. Die echten Kontrollen `c07/c08` tragen
dagegen eine volle Rezeptorstufe. Die beiden Ursachen sind in den
vorliegenden Fixtures eindeutig unterscheidbar.

Status:

`PASS_S2IW_STATIC_POST_FALSIFICATION_NUMERIC_AUDIT_NO_RULE_SELECTED`

S2-IV bleibt fachlich falsifiziert. Ein naechster Schritt waere nur ein neuer
prospektiver Vertrag fuer eine rezeptorgittergebundene Aequivalenzregel mit
unabhaengigen Fixtures; weder Regelwahl noch Wiederholung sind Teil von
S2-IW.
