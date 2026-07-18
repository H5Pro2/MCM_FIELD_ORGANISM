# Befund 009: Breitband-Stillebasis bei festem Pegel

## 1. Bezug und Pegelgrenze

Nach Befund 008 wurde der Windows-Aufnahmepegel des Mikrofons manuell
abgesenkt. Deshalb darf dieser Befund nicht quantitativ mit den absoluten
Energien aus Befund 008 verglichen werden.

Bei danach unverändertem Aufnahmepegel wurden zwei getrennte technische
Stilleläufe S0 und S0R durchgeführt.

## 2. Ausführung

```text
Gerät:                 Mikrofon (USB PnP Device(Echo-058))
Abtastrate:            48000 Hz
Dauer je Lauf:         5.0 Sekunden
Eingabe je Lauf:       500 x 10 ms
Ausgaben je Geometrie: 491
Bandzahlen:            24 / 48 / 64
Überläufe:             0 / 0
Rohdatenspeicherung:   keine
```

Jeder Lauf öffnete und schloss einen eigenen endlichen Stream.

## 3. Gesamtenergie innerhalb gleicher Geometrie

Absolute Gesamtenergien bleiben nur innerhalb derselben Bandzahl vergleichbar:

```text
Bänder   S0 Mittel      S0R Mittel     relative Abweichung
24       0.00047319     0.00047011     0.65 Prozent
48       0.00065600     0.00065256     0.53 Prozent
64       0.00075191     0.00074850     0.45 Prozent
```

Die höheren Summen bei mehr Bändern folgen auch aus Überlappung und feinerer
Aufteilung. Sie sind kein Hinweis auf mehr Weltenergie.

## 4. Wiederholbarkeit der Spektrallandschaft

Korrelation der normierten mittleren Stillelandschaft zwischen S0 und S0R:

```text
24 Bänder: 0.99930
48 Bänder: 0.99902
64 Bänder: 0.99881
```

Korrelation zwischen den Bandgeometrien innerhalb der einzelnen Läufe:

```text
S0:  0.9831 bis 0.9935
S0R: 0.9841 bis 0.9933
```

Damit ist der technische Grundpegel über zwei unabhängige Streams und drei
Auflösungen sehr stabil verteilt.

## 5. Spektraler Schwerpunkt

Median des geometrischen Spektralschwerpunkts:

```text
Bänder   S0          S0R
24       2113.7 Hz   2128.0 Hz
48       2177.6 Hz   2192.4 Hz
64       2206.4 Hz   2218.4 Hz
```

Die Schwerpunktlage ist zwischen den Wiederholungen eng, verschiebt sich aber
leicht mit der Geometrie. Sie bleibt eine Observermessung.

## 6. Dominante Stillebereiche

Die stärksten mittleren Bänder lagen bei diesem abgesenkten Pegel überwiegend
im Hochfrequenzbereich:

```text
24 Bänder: 13935.7 Hz
48 Bänder: 15881.2 Hz
64 Bänder: 16394.4 Hz
```

Die 50-Hz-Randenergie war vorhanden, aber nicht dominant:

```text
S0:  ungefähr 0.0000168 bis 0.0000175
S0R: ungefähr 0.0000152 bis 0.0000158
```

Der Hochfrequenzgrund kann aus Mikrofon, USB-Elektronik, Raum, Rechner oder
Rezeptortransformation stammen. Ohne weitere Kontrollen wird er nicht als
äußeres Geräusch und nicht als interner Feldzustand bezeichnet.

## 7. Abgrenzung zu Befund 008

In Befund 008 gehörten 50 bis 60 Hz zu den stärksten Bereichen des laufenden
Audios. Im jetzigen Stillelauf dominiert dieser Rand nicht.

Eine kausale Zuordnung ist trotzdem noch unzulässig, weil zwischen den
Befunden der Aufnahmepegel verändert wurde. Erst ein Audiolauf beim jetzigen
Pegel kann Audio und Stille gültig trennen.

## 8. Nicht freigegeben

- keine Subtraktion des Stilleprofils,
- keine automatische Rauschunterdrückung,
- keine Hochpass- oder Tiefpasskorrektur,
- keine adaptive Verstärkung,
- keine Auswahl einer Bandzahl,
- keine Spike- oder Feldschwelle.

Der Grundpegel bleibt Teil der beobachteten technischen Rezeptorlage.

## 9. Evidenz

**E1 für eine reproduzierbare technische Breitband-Stillebasis bei festem
Aufnahmepegel.**

Weiterhin **E0** für die Quelle des Hochfrequenzgrundes, natürliche
Rezeptorgeometrie, auditives MCM-Feld und Feldintelligenz.

## 10. Bester nächster Schritt

Beim unveränderten aktuellen Aufnahmepegel wird externes Audio eingeschaltet
und zweimal über je fünf Sekunden durch dieselben 24/48/64-Flächen geführt.

Der Vergleich muss prüfen:

- welche Regionen über die reproduzierte Stillebasis hinaus reagieren,
- ob 50 bis 60 Hz erneut dominant werden,
- ob der Hochfrequenzgrund bestehen bleibt oder überlagert wird,
- ob die grobe Landschaft über alle drei Geometrien stabil bleibt.

Die Stillebasis wird dabei nur verglichen, nicht aus der Rezeptorlage entfernt.
