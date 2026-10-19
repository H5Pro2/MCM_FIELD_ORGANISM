# U/L: analytische Vorprüfung, 2026-10-04

**Ergebnis: STOPP für den vorgeschlagenen großen U/L-Vergleich auf dieser
Quellenstruktur.** Nach dem festen Aufnahmepräfix unterscheiden sich die
Vorhersagen nur an binary64-Grenzen. Unterschiedliche geglättete Fehlerwerte
erzeugen hier keine reguläre Abwägung zwischen Stabilität und Wechselreaktion.
Die frühere Erwartung einer stabilen Überlegenheit von U ist damit für diesen
Vergleich nicht tragfähig. LZ1-Abnahme und Projektbefunde bleiben unverändert.

## Herleitung für die zwei Originalnachfolger

Bezeichne die Fortsetzungen mit A und B, um den Vergleichsarm L davon zu
unterscheiden. Am Y-Ziel ist P der Mittelpunkt H2. Alle 48 Komponenten
unterscheiden sich um dieselben dyadischen Abstände. Daher liefert auch die
implementierte sequenzielle mae48-Summation exakt: Kontextfehler 0 bzw. 1/2,
Persistenzfehler 1/4. Der gemeinsame j/4096-Anteil fällt exakt weg.

Für jede warme Zelle bleibt EP=1/4, unabhängig vom Alter ihrer Historie:
Initialisierung mit ep=1/4, danach (1/2)(1/4)+(1/2)(1/4)=1/4.
Die Regel wählt ein eindeutiges negatives Minimum EC−1/4, sonst P.
Kaltes ist kein Nullfehler und nimmt nicht an der Auswahl teil.

Seien a und b die bisherigen EC-Werte der warmen A-/B-Zellen, jeweils in
[0,1/2]. Nach Rückmeldung A gilt in exakter Arithmetik:

    a' = a/2 <= 1/4
    b' = b/2 + 1/4 >= 1/4

U wählt A genau dann, wenn a<1/2. Bei a=1/2 wählt es P, nicht B.
Nach Rückmeldung B symmetrisch: U wählt B genau dann, wenn b<1/2,
sonst P. L speichert (0,1/2) bzw. (1/2,0) und wählt stets die zuletzt
rückgemeldete Fortsetzung, sobald beide Zellen regulär warm sind.
Entscheidend: Beide Hypothesen werden auch bei Nichtauswahl aktualisiert.
Auswahlabhängiges Feedback würde diese Herleitung ungültig machen.

## Initialisierung und festes Aufnahmepräfix

Das feste Präfix A,A,B,B erzeugt nach seiner letzten Y-Rückmeldung
EC_A=3/8, EC_B=0, jeweils EP=1/4. A wurde an den Zielen 7,11,15
mit Fehlern 0,1/2,1/2 bewertet; B erstmals an 15 mit Fehler 0.
Bei der direkten Promotion bleibt dieses Fehlerpaar erhalten. B,B,A,A
liefert denselben Zustand mit vertauschten Fortsetzungsnamen.
Die Zellen besitzen also gerade NICHT identische Anfangshistorien und
ihre EC-Summe ist anfangs 3/8, nicht 1/2.

Die frühe Auswahl ist bei U/L gleich: an Ziel 3 kein Kontext, an 7 kalt,
an 11 die erste Fortsetzung; an 15 P, weil die erste U-Zelle den Wert
1/4 hat und die neue zweite Zelle noch kalt ist. Bei L ist die erste Zelle
an 15 sogar schlechter als P, aber die Ausgabe bleibt ebenfalls P.

Nach dem Präfix bleibt in exakter Arithmetik

    EC_A + EC_B = 1/2 − (1/8)·2^(−n)

für n gemeinsame Y-Rückmeldungen. Beide Einzelwerte bleiben strikt unter
1/2; Multiplikation mit 1/2 und Addition von 1/4 erhalten diese Eigenschaft.
Damit wählt U nach jeder Y-Rückmeldung dieselbe Fortsetzung wie L, auch
unmittelbar nach einem Wechsel. Es gibt keinen mathematischen EMA-Nachlauf.
Am ersten Y nach dem Präfix wählen beide B (bzw. A beim spiegelbildlichen Präfix).
Gerüstziele verwenden andere Hinweise/Offsets und verändern diese Y-Zellen
nicht; dort ist die Persistenz bereits exakt. Die Behauptung betrifft den
gebundenen Bestand ohne Verlust, Ersatz oder zusätzliche Konkurrenten.

Eine wichtige Grenze außerhalb dieses festen Präfixes: Werden beide Zellen
gleichzeitig mit A initialisiert, entsteht (0,1/2). Ein folgendes B liefert
exakt (1/4,1/4): U gibt P aus, L B. Dies ist ein echter arithmetischer
Initialisierungseffekt, aber kein Gegenbeispiel im festgelegten LZ1-Präfix.
Andere Initialisierungen dürfen nicht nachträglich als neue Testwelt dienen.

## binary64, Gleichstände und erreichbarer Unterschied

Die bestehende Operation ist `.5*old + .5*error`, mit getrennten
Multiplikationen und anschließender Addition, ohne FMA. EP bleibt exakt.
Rundung ist monoton: Nach einem A-Feedback kann der A-Wert höchstens 1/4,
der B-Wert mindestens 1/4 sein. Ein älterer Gegenkontext gewinnt dadurch
nicht; möglich ist nur A oder Persistenz. Entsprechendes gilt für B.
EC−EP wird mit der bestehenden strikten Nullgrenze ausgewertet, ohne Epsilon.

In der Nähe der oberen Grenze kann der falsche Kontextfehler auf 1/2
runden. Ein späteres passendes Feedback halbiert ihn dann exakt auf 1/4.
Auch die andere Zelle kann bei 1/4 landen: U enthält sich mit
NO_ESTIMATED_IMPROVEMENT (kein negatives Minimum), L wählt den letzten Kontext.
Dies ist kein TIED_IMPROVEMENT, denn beide Differenzen sind null.

Konkrete neutral geprüfte erreichbare Fortsetzung des Präfixzustands (3/8,0):
52 weitere B-Rückmeldungen, anschließend A. binary64 ergibt (1/4,1/4).
In exakter Arithmetik lautet der A-Wert 1/4−2^−56, B=1/4; U würde A wählen.
L speichert nach A (0,1/2) und wählt A. Der Unterschied besteht bei der
nächsten Y-Prognose: U=P, L=A. Eine nächste gleiche A-Fortsetzung ergäbe
Fehler 1/4 gegen 0; eine nächste B-Fortsetzung 1/4 gegen 1/2. Das sind
bedingte Fehlerwerte, keine gemessenen Vorteile auf Forschungsfolgen.

Spiegelrichtung aus demselben Anfangszustand: 54 weitere A-Rückmeldungen,
danach B, erzeugen ebenfalls den numerischen Gleichstand. Die unterschiedlichen
Grenzlängen kommen aus den unterschiedlichen Anfangswerten; sie sind keine
gewählten Forschungsparameter. Nach einem weiteren gültigen Feedback aus
(1/4,1/4) entsteht (1/8,3/8) oder (3/8,1/8); die Auswahl stimmt wieder überein.
Subnormal-Unterlauf ist ein weiterer isolierter numerischer Grenzfall,
aber für das 52er-Beispiel nicht erforderlich.

## Kleine neutrale Absicherung

[Prüfskript](check.py), [Ergebnisse](verification.json). Acht Gruppen bestanden:

- T1: dyadische Geometrie und tatsächliche mae48-Arithmetik.
- T2: zwei handgeschriebene, verschobene 16-Frame-Präfixfixtures mit dem
  unveränderten U-Adapter und seiner unabhängigen Referenz; Anfangszellen bestätigt.
- T3: kalt, erste Bewertung und exakter Gleichstand außerhalb des festen Präfixes.
- T4: alle 2.046 binären Fehlerfolgen der Längen 1–10 ab Präfixzustand,
  binary64 gegen rationale Rechnung, stets gleiche Auswahl wie L.
- T5: gleiche Rückmeldungen, einzelner Wechsel und 40 alternierende Rückmeldungen.
- T6: begrenzte skalare Grenzprüfung bis 64 gleiche Rückmeldungen; erste
  Gleichstände bei 54 bzw. 52, jeweils exakte rationale Gegenrechnung.
- T7: benachbarte Floatwerte, kleinste positive Subnormalzahl und Erholung nach Gleichstand.
- T8: exakte Persistenzfehler-Invariante.

Diese endlichen Prüfungen stützen die Herleitung; sie ersetzen nicht ihren
allgemeinen Beweis. Kein L-Produktionsarm und keine Vergleichshülle implementiert.
Keine Forschungsquelle erzeugt, kein vorhandener LZ1-Fall wiederholt.
Vor dem gespeicherten Check: ein Aufruf wegen fehlendem Callback abgewiesen,
einer am ersten Frame wegen ungültiger Profillänge abgewiesen, danach ein
erfolgreiches exploratives 16-Frame-Neutralpräfix. Insgesamt drei erfolgreich
ausgeführte kleine Präfixfixtures mit 48 Frames; die skalaren Checks sind keine
weiteren MCM-Quellenläufe. Diese Versuche sind im Prüfbeleg offengelegt.

## Anschlussentscheidung

STOPP gilt ausschließlich für den großen U/L-Vergleich in dieser Zweifortsetzungs-
quelle. Keine Umsetzung oder Forschungsausführung daraus ableiten. Der behauptete
Stabilitäts-/Wechselkontrast fehlt, abgesehen von numerischen Enthaltungen.

Empfohlener nächster Schritt beim Projektleiter: den Vergleichszweig schließen
und vor einem weiteren Versuch zuerst konzeptionell eine real erreichbare
Bewertungssituation bestimmen, in der die jüngste Beobachtung nicht bereits
die gesamte Auswahl festlegt. Erst eine solche analytische Gegenprognose kann
einen neuen begrenzten Vergleich rechtfertigen. Hier wird weder eine neue Quelle
noch ein anderer Glättungsparameter festgelegt oder freigegeben.
