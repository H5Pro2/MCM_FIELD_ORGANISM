# Methodik 023: Lokale visuelle Phasenprofile

## 1. Ausgangspunkt

Die reale Ruhe-Nullbasis fasst 288 visuelle MCM-Neuronen jeweils zu einem
globalen Phasenmittel zusammen. Eine räumlich begrenzte Veränderung kann darin
verdünnt werden, obwohl sie an einzelnen lokalen Trägern deutlich wirkt.

Vor jeder neuen Feldmechanik wird deshalb geprüft, ob die bereits vorhandenen
lokalen Größen ausreichen, wenn ihre räumliche Herkunft observerseitig erhalten
bleibt.

## 2. Unveränderte Eingänge

Für jedes Neuron und jedes vollständig zugeordnete Zeitfenster werden nur zwei
bereits vorhandene Größen gemittelt:

```text
|aktueller Rezeptorkontakt - eigene Voraktivierung|

mittleres |lokale Voraktivierung - benachbarte Voraktivierung|
```

Der erste Initialisierungsframe und zeitliche Grenzframes bleiben wie in
Methodik 022 ausgeschlossen.

## 3. Was erhalten bleibt

Ein lokales Phasenprofil enthält ausschließlich:

- technische Neuronidentität,
- feste räumliche Position im offenen Rezeptorraster,
- Anzahl gültiger Frames,
- mittlere absolute Rezeptoränderung,
- mittlere absolute lokale Aktivierungsdifferenz.

Es enthält kein Bild, keinen Bildausschnitt und keine Objektbeschreibung.

## 4. Was ausdrücklich nicht entsteht

- keine Rangliste aktiver Neuronen,
- kein Gewinner,
- keine Schwelle,
- keine Bewegungsmaske,
- keine Richtung oder Geschwindigkeit,
- keine Ähnlichkeitssuche,
- kein Vektor-Embedding,
- keine Pattern-ID,
- kein Memory und keine Feldrückwirkung.

Die räumlichen Profile sind ausschließlich äußere Forschungsmaße. Der
Organismus erhält sie nicht als zusätzlichen Eingang.

## 5. Nullkontrollen

1. Profil und Zeitmarkierung müssen aus demselben vollständigen Probe-Lauf
   stammen.
2. Jede Phase muss dieselbe technische Feldgeometrie bewahren.
3. Eine synthetisch lokale Änderung darf nur an den tatsächlich berührten
   Rezeptorpositionen Rezeptoränderung erzeugen.
4. Wiederholung derselben Feldgeschichte muss exakt dasselbe Profil liefern.
5. Die Observerauswertung darf den Digest der Feldzustände nicht verändern.
6. Globale Mittelwerte bleiben als B0-Vergleich erhalten.

## 6. Entscheidung

Trägt ein späterer realer Veränderungslauf ein lokales Profil, obwohl das
globale Mittel nahezu unverändert bleibt, ist nur gezeigt:

> Die vorhandene visuelle Feldhülle bewahrt lokale Veränderung, und die globale
> Auswertung hat sie verdeckt.

Das wäre noch keine Bewegungserkennung und keine neue Feldfunktion.

Bleiben auch lokale Profile zwischen nachweislicher Veränderung und Ruhe ohne
trennbare Struktur, ist die aktuelle Rezeptorprojektions-Baseline für diese
Funktion nicht ausreichend. Auch dann wird keine neue Mechanik automatisch
freigegeben.

## 7. Evidenzgrenze

```text
lokaler Profilbeobachter: passiver Methodenkandidat
Runtime-Änderung:         keine
maximales Evidenzziel:    E2
Memory-Freigabe:          keine
```

## 8. Bester nächster Schritt

Nach synthetischer Ortsnullprüfung wird derselbe reale Veränderungslauf wie in
Methodik 022 wiederholt. Globale Mittel und lokale Profile müssen aus genau
demselben Lauf stammen. Eine neue visuelle Feldregel bleibt bis dahin
geschlossen.
