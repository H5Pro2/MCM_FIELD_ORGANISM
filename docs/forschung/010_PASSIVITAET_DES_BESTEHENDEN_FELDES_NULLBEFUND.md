# Passivität des bestehenden Feldes - Nullbefund

## Fragestellung

Die konstitutive Sättigungsgrenze ließ genau eine letzte Nullfrage offen:

```text
Erzwingt ein lokales Passivitäts- oder Feldarbeitsprinzip
einen eigenständigen Materialzustand?
```

Die Prüfung beobachtet ausschließlich die vorhandene neutrale Feldgleichung.
Sie ergänzt keinen Zustand und verändert keine Transition.

## Quadratische Bilanz

Für den vorhandenen Aktivierungsvektor `x` wird die mathematische
Speicherfunktion verwendet:

```text
S(x) = 1/2 * x^T x
```

Aus dem bestehenden Generator `G` und der bestehenden Rezeptorrandwirkung `b`
folgt:

```text
dx/dt = Gx + b
```

Die beobachtete Änderungsrate wird exakt zerlegt:

```text
dS/dt
= Rezeptorzufuhr
- Nachbardissipation
- Rezeptordissipation
```

mit:

```text
Rezeptorzufuhr       = x^T b
Nachbardissipation   = -x^T L x
Rezeptordissipation  = -x^T (G - L) x
```

`L` ist der bereits vorhandene kontaktfreie Diffusionsgenerator.

## Kanonischer Befund

### Kontaktfrei

```text
quadratische Speicherung:          0.12455260490562436
Änderungsrate:                    -0.2439243989417683
Rezeptorzufuhr:                    0.0
Nachbardissipation:                0.2439243989417683
Rezeptordissipation:              -0.0
Bilanzfehler:                      0.0
größter Generatoreigenwert:       -5.0450834795003976e-17
```

Die minimale numerische Abweichung des größten Eigenwerts von null ist
Rundungsrauschen. Kontaktfrei wächst die quadratische Speicherfunktion nicht.

### Mit Rezeptorkontakt

```text
quadratische Speicherung:          0.12455260490562436
Änderungsrate:                    -0.5269229166756766
Rezeptorzufuhr:                   -0.033893307922659516
Nachbardissipation:                0.2439243989417683
Rezeptordissipation:               0.24910520981124873
Bilanzfehler:                      0.0
größter Generatoreigenwert:       -1.0
```

Auch mit Kontakt schließt die gewählte Bilanz exakt.

## Nullkontrollen

Sechs fokussierte Unit-Tests bestätigen:

1. kontaktfreie quadratische Dissipation;
2. exakte kontaktgetriebene Bilanz;
3. unveränderten Felddigest;
4. unveränderte Verteilungsdigests;
5. fehlende Akkumulation und fehlenden Runtime-Zustand;
6. keine Behauptung physischer Energie oder eines Memory-Kandidaten.

## Interpretation

Das vorhandene Feld besitzt bereits eine mathematisch passive Darstellung.
Die Bilanz ist vollständig aus aktuellem Aktivierungszustand, Generator und
Rezeptorverteilung rekonstruierbar.

Sie trägt keine neue Information:

```text
quadratische Speicherung
+ Zufuhr
+ Dissipation
= andere Darstellung der vorhandenen Feldgleichung
```

Der Observer speichert keine Arbeitsgeschichte. Nach Angleichung des schnellen
Feldzustands wäre auch diese Bilanz angeglichen.

## Keine physische Energiebehauptung

`activation` ist eine normierte Feldgröße. Sie besitzt im aktuellen Modell
keine physikalische Energieeinheit. Ebenso sind Rezeptorwert und Aktivierung
nicht als experimentell kalibriertes Kraft-Fluss- oder Spannung-Strom-Paar
begründet.

`S(x)` ist deshalb eine mathematische Speicherfunktion im Sinn der
Systemtheorie. Sie ist weder:

- gemessene Energie;
- metabolische Ressource;
- Feldarbeit eines realen Materials;
- organisches Memory.

## Negativbefund

Der Befund zeigt:

> Passivität erzwingt keinen zusätzlichen Memory- oder Materialzustand. Die
> bestehende schnelle Feldruntime erfüllt bereits eine passive Bilanz.

Ein passives System kann prinzipiell innere Memory-Zustände besitzen. Deren
konstitutive Gleichung folgt aber nicht aus der Passivitätsbedingung allein.

## Freigabegrenze

```text
mathematische Passivitätsbilanz bestätigt:     ja
physische Energie identifiziert:               nein
neuer Informationsgehalt:                      nein
Materialzustand erzwungen:                     nein
Memory-Kandidat zugelassen:                    nein
Runtime-Erweiterung freigegeben:               nein
```

## Schlussfolgerung

Das Passivitäts- und Feldarbeitsprinzip schließt die konstitutive Lücke nicht.
Es liefert eine wichtige Schutzbedingung für spätere Hypothesen, wählt aber
keine davon aus.

Damit ist die abstrakte und passivitätsbasierte Substratherleitung
ausgeschöpft.
