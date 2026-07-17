# Blinde Holdout-Feldwirkung

## 1. Status

Beobachtungs- und Funktionsvertrag auf Evidenzstufe E0.

Der Vertrag folgt auf Befund 040. Er definiert eine mögliche spätere
Feldprobe, ohne Übergangsdisposition, Ressource, Leserform oder neue
Runtime-Mechanik einzuführen.

## 2. Ausgangspunkt

Befund 040 zeigt einen engen Repräsentationsrest:

```text
unabhängige lokale Übergangsspuren
→ keine konkurrenzgekoppelte Lösung

globale Normalisierung
→ Absenkung, aber Verletzung der Lokalität
```

Dieser Rest begründet noch keine neue Zustandsrolle.

Insbesondere fehlt eine Feldfunktion, an der eine mögliche veränderte
Organisation später beobachtet werden könnte, ohne nur denselben gespeicherten
Übergang erneut abzufragen.

## 3. Warum eine vollständig leserfreie Probe unmöglich ist

Ein innerer Zustand ist nur dann funktional, wenn er eine spätere Feldwirkung
verändert.

Damit benötigt jede Prüfung einen Wirkungspfad:

```text
innerer Zustand
+ spätere Weltprobe
→ beobachtbare Feldantwort
```

Eine vollständig leserfreie Wirkung wäre unbeobachtbar.

Die methodische Grenze lautet daher nicht:

```text
keine Kopplung zwischen Zustand und Feld
```

sondern:

```text
keine direkte Abfrage einer zuvor adressierten Übergangskante
keine vorgegebene Sollantwort
keine branchspezifische Leserregel
```

## 4. Tautologische adressierte Probe

Nicht ausreichend wäre:

```text
Geschichte enthält 0 → 1
spätere Probe wiederholt 0 → 1
gespeicherter Wert für 0 → 1 wird gelesen
→ größere Ausgabe
```

Ein positiver Befund wäre bereits durch die Konstruktion eines
Übergangszählers oder einer gewichteten Kante vorgegeben.

Er würde nur kausale Mediation eines adressierten Speichers zeigen.

## 5. Gesuchte nicht adressierte Funktion

Die kleinste strengere Funktion lautet:

> Kann eine zusammenhängende lokale Weltgeschichte die spätere Aufnahme zweier
> noch nicht erlebter, aber lokal anschließender Zukunftskontakte verschieden
> beeinflussen?

Die Prüfung fragt nicht, welcher Kontakt richtig ist.

Sie fragt ausschließlich, ob:

```text
gleiche spätere Gegenwart
+ andere zusammenhängende Geschichte
→ andere kausale Aufnahme einer neuen lokalen Fortsetzung
```

## 6. Technische Ringwelt

Die vorhandene periodische MCM-Sensoranatomie stellt sieben lokale Positionen
bereit:

```text
0, 1, 2, 3, 4, 5, 6
```

Die Ringgeometrie ist technische Versuchsanatomie. Sie trägt keine Richtung,
Bewegungsklasse oder Bedeutung in die Runtime.

Pro Takt ist höchstens eine Position aktiv.

## 7. Zwei richtungsinvertierte Geschichten

Die primären Geschichten lauten:

```text
H+ : 1 → 2 → 3 → 4 → 5 → 6 → 0 → - → -
H- : 6 → 5 → 4 → 3 → 2 → 1 → 0 → - → -
```

Beide besitzen exakt:

- dieselbe Dauer,
- dieselbe Gesamtenergie,
- dieselbe Positionshäufigkeit,
- denselben Endkontakt `0`,
- dieselbe Zahl lokaler Übergänge,
- dieselbe Zahl kontaktloser Takte.

Sie unterscheiden sich nur in der lokalen zeitlichen Ordnung.

`H+` und `H-` sind ausschließlich äußere Forschungsnamen.

## 8. Permutationskontrolle

Eine angeglichene, aber lokal unzusammenhängende Geschichte lautet:

```text
HP : 1 → 3 → 5 → 2 → 6 → 4 → 0 → - → -
```

Sie enthält dieselben sieben Kontakte und endet ebenfalls an Position `0`.

Kein aufeinanderfolgendes Kontaktpaar in `HP` ist auf dem Ring lokal
benachbart.

Die konkrete Permutation wird vor einem Versuch festgeschrieben und nicht an
ein Ergebnis angepasst.

## 9. Keine erlebte ausgehende Holdout-Kante

Alle Geschichten enden an Position `0` und werden anschließend unterbrochen.

Dadurch enthält keine Geschichte:

```text
0 → 1
0 → 6
```

Die beiden späteren Holdout-Übergänge sind in jedem Zweig neu.

Ein exakter Zähler oder eine adressierte Leaky-Spur für `0 → 1` und `0 → 6`
beginnt daher in allen Zweigen bei null.

## 10. Vollständige Schnellfeldangleichung

Nach der Geschichte wird so lange kontaktlos fortgeschritten, bis in allen
Zweigen exakt gilt:

```text
activation = 0
afterimage = 0
aktueller Rezeptorkontakt = 0
```

Eine nur toleranznahe Angleichung genügt nicht.

Falls die vorhandene Runtime nicht endlich exakt null erreicht, müssen
Restspuren mathematisch vorhergesagt und zusätzlich durch einen exakten
Resetzweig getrennt werden.

## 11. Identische gemeinsame Probe

Nach der Angleichung erhalten alle Zweige denselben einzelnen Kontakt:

```text
Probe P: Kontakt an Position 0
```

Die Probe enthält:

- keine Übergangsrolle,
- keine Richtungsangabe,
- keine Fortsetzung,
- keine Zielposition,
- keine Belohnung.

Der vollständig abgeschlossene Zustand nach P wird unverändert eingefroren.

## 12. Kontrafaktische Zukunftsgabel

Aus demselben eingefrorenen Zustand entstehen zwei unabhängige
Weltfortsetzungen:

```text
F1: nächster realer Kontakt an Position 1
F6: nächster realer Kontakt an Position 6
```

Beide Zukunftskontakte werden geprüft.

Der Organismus wählt keinen Kontakt aus. Die äußere Versuchswelt erzeugt zwei
getrennte kontrafaktische Zweige.

## 13. Primäre funktionale Messung

Gemessen wird die vollständige kausal abgeschlossene MCM-Feldantwort auf F1
und F6.

Für jede Geschichte entsteht ein Kontrast:

```text
D(H) = Feldantwort(H, F1) - Feldantwort(H, F6)
```

Die konkrete kanonische Darstellung des Feldunterschieds muss vor einer
Implementierung festgelegt werden.

Unzulässig ist, nur einen eigens eingeführten Dispositionswert auszulesen.

## 14. Keine vorgegebene richtige Richtung

Der Runtime wird nicht vorgegeben:

```text
H+ soll F1 bevorzugen
H- soll F6 bevorzugen
```

Die zulässige primäre Frage lautet nur:

```text
Spiegelt sich ein geschichtsabhängiger Feldkontrast
unter vollständiger Spiegelung der Weltgeschichte?
```

Eine mögliche Wirkung muss mit der gespiegelten Geschichte kanonisch
mitwandern. Ihr Vorzeichen ist keine semantische Klasse.

## 15. Stärkere Holdout-Bedingung

Ein nicht adressierter Funktionsbefund verlangt gemeinsam:

1. `0 → 1` und `0 → 6` wurden zuvor nie erlebt.
2. F1 und F6 beginnen aus demselben eingefrorenen Zustand.
3. H+ und H- sind in Energie und Positionshäufigkeit identisch.
4. Die schnelle Feldlage ist vor P exakt angeglichen.
5. Der Feldkontrast verändert sich mit der Geschichte.
6. Unter Spiegelung wandert der Kontrast kanonisch mit.
7. Unter Neutralisierung der geschichtlich entstandenen Organisation
   kollidieren die Zukunftszweige wieder entsprechend ihrer Symmetrie.

## 16. Kausale Wirkung statt Observer-Ähnlichkeit

Ein äußerer Observer darf Feldantworten vergleichen.

Er darf jedoch:

- keine Antwort in die Runtime zurückschreiben,
- keine Gewinnerposition auswählen,
- keine Ähnlichkeitsschwelle liefern,
- keine Geschichte klassifizieren,
- keine Disposition erzeugen.

Die Feldantwort muss vor der Observerauswertung vollständig feststehen.

## 17. Pflichtablationen

Ein späterer Kandidat benötigt mindestens:

- unveränderte entstandene Organisation,
- exakt neutralisierte Organisation,
- Tausch der Organisation zwischen H+ und H-,
- unterbrochene lokale Geschichte,
- permutierte Geschichte HP,
- blockierte lokale MCM-Proben,
- blockierte Rezeptoraufnahme bei F1 und F6,
- vollständigen Neuaufbau jedes Zweigs,
- entfernten Observer.

Eine Wirkung, die beim Tausch nicht mitwandert, wird nicht von der
geschichtlich entstandenen Organisation vermittelt.

## 18. Rotations- und Spiegelkontrolle

Die vollständige Welt wird auf alle sieben Ringpositionen rotiert.

Zusätzlich werden Ringorientierung, Zweigreihenfolge, Neuronenreihenfolge und
lokale Probenreihenfolge invertiert.

Nach kanonischer Rückabbildung müssen entsprechende Feldantworten kollidieren.

Eine technische Vorzugsposition oder Iterationsrichtung entwertet den Befund.

## 19. Pflichtbaselines

Mindestens zu prüfen sind:

```text
B0  unverändertes schnelles MCM-Feld
B1  unabhängige Positionshäufigkeiten
B2  exakte lokale Übergangszähler
B3  mehrere feste Leaky-Übergangsspuren
B4  fester globaler Orientierungszähler
B5  fester endlicher Geschwindigkeits- oder Fortsetzungsautomat
B6  feste lokale Ringrekurrenz
B7  äußerer Sequenz- oder Templatevergleich
```

B4 bis B7 sind unzulässige Organismusmechanismen, aber notwendige starke
Forschungsbaselines.

## 20. Bedeutung der Baseline-Trennung

B2 und B3 dürfen für die Holdout-Kanten nur tragen:

```text
count(0 → 1) = 0
count(0 → 6) = 0
```

Damit können sie die neue Fortsetzung nicht direkt adressieren.

Ein globaler Orientierungszähler oder fester Fortsetzungsautomat kann die
Geschichten dagegen voraussichtlich unterscheiden und die Holdout-Wirkung
vorhersagen.

Falls B4 oder B5 den gesamten Effekt erklärt, ist keine entwickelte
Feldorganisation gezeigt.

## 21. Verhältnis zur Übergangsdisposition

Die blinde Holdout-Probe ist strenger als der Vertrag einer einzelnen lokalen
Übergangsdisposition.

Eine Sammlung unabhängiger adressierter Kanten muss an dieser Probe scheitern,
weil die ausgehenden Holdout-Kanten nie erlebt wurden.

Ein positiver Befund würde deshalb nicht automatisch eine einzelne
Übergangsdisposition bestätigen. Er würde zunächst auf eine verteilte
geschichtsabhängige Feldorganisation oder auf ein einfacheres globales
Fortsetzungsmodell hinweisen.

Diese Ebenen dürfen nicht vermischt werden.

## 22. Verhältnis zur verdichteten Feldform

Die Probe speichert keine Bilder, Objekte oder Sequenzen.

Sie prüft erstmals eine eng begrenzte Übertragung:

```text
mehrere zusammenhängende lokale Weltkontakte
→ gegenwärtige verteilte Organisationsbereitschaft
→ Wirkung auf einen neuen lokalen Anschluss
```

Das wäre noch keine innere Bezeichnung. Es wäre höchstens eine notwendige
Vorstufe einer wiedererzeugbaren Feldform.

## 23. Erwarteter Nullbefund der vorhandenen Runtime

Die derzeitige Rezeptorprojektion ignoriert lokale Feldproben und besitzt nach
vollständiger Leerung keine Geschichte.

Daher wird erwartet:

```text
H+, H- und HP
+ identische Probe P
+ F1 oder F6
→ nur aktuell rezeptorbestimmte Feldantwort
```

Alle geschichtsabhängigen Holdout-Kontraste müssen unter B0 kollidieren.

Dieser Nullbefund wäre korrekt und würde keine neue Mechanik freigeben.

## 24. Stärkstes Gegenargument

Die Probe könnte lediglich verlangen, dass das System eine globale
Bewegungsrichtung schätzt und auf einen neuen Ort überträgt.

Ein fester Richtungsakkumulator oder Fortsetzungsautomat könnte diese Funktion
ohne organische Feldentwicklung erfüllen.

Deshalb sind B4 und B5 bindend. Eine scheinbar vorausschauende Antwort darf
nicht als Feldintelligenz bezeichnet werden, wenn ein solcher Automat sie
vollständig erklärt.

## 25. Evidenzgrenze

Eine spätere erfolgreiche Null- und Baselineprüfung kann höchstens tragen:

```text
nicht adressierte Holdout-Weltfunktion: E1
Angleichung und Kausaltrennung:          E2
Grenze exakter Kantenzähler:             E2
geschichtsabhängige Feldwirkung:         E0
verteilte Feldorganisation:              E0
verdichtete Feldform:                    E0
Feldintelligenz:                         E0
```

## 26. Stopplinie

Nicht freigegeben sind:

- Übergangsdisposition oder Ressourcenvariable,
- Richtungs- oder Bewegungszustand,
- Fortsetzungsautomat,
- adaptive Kante oder Gewicht,
- Lern- oder Zerfallsrate,
- spontane Feldaktivierung,
- Gewinnerwahl oder Zielposition,
- Reward, Handlung oder Semantik,
- Runtime-Rückwirkung.

## 27. Bester nächster Schritt

Vor jeder Mechanik wird Methodik 038 als passive Null- und Baselineprüfung
vorregistriert.

Sie muss die exakten Ringfolgen, Zustandsangleichung, Zukunftsgabel,
kanonische Feldmetrik, Rotationen, Spiegelungen, B0 bis B7 und Scheiterkriterien
festlegen.

Erst danach darf geprüft werden, ob die vorhandene Runtime erwartungsgemäß
kollidiert und welche einfacheren Gegenmodelle die Holdout-Funktion bereits
tragen könnten.
