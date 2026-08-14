# S1-AW: Wiedereroeffnungstor fuer neue Substratkandidaten

## Status

Statischer Auswahlrahmen. Kein Substratkandidat, keine Gleichung, keine
Runtime und kein Forschungslauf.

S1-AW trennt zwei gleichberechtigte Arbeitslinien:

```text
Substratforschung: konzeptionelle Vorpruefung neuer Naturprinzipien
AV-Engineering:    aktive technische Entwicklung und Absicherung
```

## Zweck

Neue Substratideen werden nicht mehr durch weitere Gleichungsvarianten
gesucht. Eine Idee darf erst nach diesem Rahmen in einen Kandidatenvertrag
uebergehen. Besteht sie das Raster nicht, bleibt die Substratlinie pausiert.

## Verbindliches Auswahlraster

### 1. Eigenstaendige lokale Ursache

Die Idee muss benennen, welche vorhandene lokale Feldgroesse den Zustand
veraendert. Die Ursache darf nicht aus dem gewuenschten Memoryergebnis, einem
Label, einer Objektklasse oder einer nachtraeglichen Interpretation stammen.

### 2. Lokale Bilanz und Ressource

Die Idee muss angeben, was begrenzt ist, wie lokale Veraenderung bilanziert
wird und wie Freigabe oder Wiederverwendung technisch moeglich waere. Eine
blosse Begrenzung durch Clipping, globale Normierung oder externe Ablage gilt
nicht als Bilanz.

### 3. Konjugierter Rueckwirkungsweg

Die spaetere Feldwirkung muss aus derselben lokalen Wechselwirkung folgen, die
den Zustand gebildet hat. Getrennte Schreib- und Leseregeln sowie ein
nachtraeglicher Speicher- oder Ausgabezweig sind unzulaessig.

### 4. Gegenprognose vor jeder Implementierung

Die Idee muss mindestens eine messbare Vorhersage liefern, in der sie sich
unter identischem Eingangs- und Probeaufbau von mindestens einer Pflicht-
baseline unterscheidet:

```text
leaky, Integrator, F3, CONST-V, P0
```

Eine groessere Amplitude oder ein anderer Parameterwert reicht nicht.

### 5. Keine Vorprogrammierung

Unzulaessig sind Labels, Rewards, Zielmuster, Wenn-X-dann-Y-Regeln,
vorgegebene Topologien, Objekt-/Episodenkennungen, semantische Kategorien
und externe Rohdaten-, Datenbank- oder Embedding-Speicher.

### 6. Klare Nullkontakt-Prognose

Die Idee muss vorab festlegen, wie sie sich ohne neue Audio-/Video-
Rezeptorframes verhaelt. Feldnachhall, reine Zustandsfortsetzung und die
eigene Substratreaktion muessen getrennt auswertbar sein.

### 7. Klare Freigabe- und Loeseprognose

Die Idee muss beschreiben, wodurch eine lokale Konfiguration abklingt,
freigegeben oder umverteilt wird. Ein Resetkommando, eine feste
Lebenszyklusphase oder ein manuell gesetztes Loeschen ersetzt diese Prognose
nicht.

## Entscheidungslogik

```text
alle sieben Punkte erfuellt
-> Kandidatenvertrag darf formuliert werden

ein Punkt offen oder nur biologisch behauptet
-> STOPP, keine Gleichung und keine Runtime
```

Der Rahmen selbst erzeugt keinen Kandidaten. Er erlaubt nur die saubere
Auswahl oder Zurueckweisung spaeter eingereichter Konzepte.

## Aktive AV-Engineeringlinie

Unabhaengig vom Ergebnis der Substratvorpruefung bleibt folgende Linie aktiv:

```text
kontrollierte AV-Testwelt
-> Rezeptorsequenzen
-> gemeinsames MCM-Feld
-> S/H-Zustand und Nachhall
-> Snapshot/Restore
-> transparente Baselines und Reproduzierbarkeit
```

Diese Linie darf technisch erweitert werden, ohne Memory, Feldzeit,
Organisation, Semantik oder KI zu behaupten.

## Naechster Schritt

Als naechstes duerfen neue Substratideen nur als kurze Konzeptnotizen gegen
S1-AW eingereicht werden. Parallel bleibt die AV-Engineeringpflege aktiv.

## Spaetere technisch-pragmatische Linie S1-BK

S1-BK erlaubt nach neuer Benutzerentscheidung zusaetzlich bewusst
konstruierte lokale Feldplastizitaet. Diese Engineeringlinie muss die strikte
Nichtreduktion gegen bekannte adaptive Baselines nicht vor ihrer
Implementierung belegen. Sie darf deshalb aber auch keine neue
Substratnatur, kein organisches MCM-Memory und keine emergente Organisation
behaupten.

S1-AW bleibt unveraendert das Tor fuer solche staerkeren Aussagen. Ein
technischer Erfolg unter S1-BK besteht S1-AW nicht automatisch.
