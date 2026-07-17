# Methodik 025: Passive sensorische Belastungs- und Erholungsprüfung

## 1. Status

Vorregistrierte passive Nullprüfung auf Evidenzstufe E0.

Diese Methodik führt weder einen Empfindlichkeitszustand noch eine
Rezeptorrückwirkung ein. Sie prüft zuerst die bekannte feste Rezeptorfläche und
grenzt deren Funktionsumfang gegen einfachere technische Regelungen ab.

## 2. Forschungsfrage

Kann die vorhandene Architektur dieselbe spätere Außenanregung nach
unterschiedlichen lokalen Belastungs- und Erholungsgeschichten verschieden
aufnehmen?

Die erwartete Antwort für die gegenwärtige Runtime lautet:

```text
gleiche spätere Außenanregung
+ unveränderte feste Rezeptorabbildung
→ exakt gleiche spätere Rezeptorlage
```

Ein bestätigter Nullbefund ist kein Fehler. Er benennt den konkreten
Funktionsmangel, der vor jedem späteren Mechanikkandidaten belegt sein muss.

## 3. Unveränderte Systemgrenze

Die Prüfung endet unmittelbar hinter der jeweiligen Rezeptorabbildung:

```text
kontrollierte synthetische Weltfolge
→ vorhandener passiver Rezeptor
→ unveränderliche Rezeptorlage
→ äußerer passiver Observer
```

Nicht Teil der Primärmessung sind:

- sensorischer Nachhall,
- MCM-Neuronenübergänge,
- MCM-Verteiler,
- multimodale Feldkonstellation,
- Reflexion,
- Memory,
- Geräte- oder Betriebssystemregelung.

Dadurch wird eine Rezeptorwirkung nicht mit späterer Feldgeschichte
verwechselt.

## 4. Kontrollierte Geschichten

Jede Modalität erhält dieselbe lokale Prüfposition `p` und eine getrennte
Nachbarposition `q`.

```text
K0: Ruhegeschichte
    Nullkontakt → Ruhe → Probe an p

K1: lokale Belastung
    wiederholter starker Kontakt an p → Ruhe → dieselbe Probe an p

K2: benachbarte Belastung
    wiederholter starker Kontakt an q → Ruhe → dieselbe Probe an p

K3: verteilte Belastung
    gleiche Gesamtanregung auf mehreren Positionen → Ruhe → dieselbe Probe an p
```

Die Probe ist in allen Zweigen bitgleich. Nur die vorherige Geschichte
unterscheidet sich.

## 5. Erholungsfamilie

Die vier Geschichten werden mit drei klar getrennten Pausenlagen geprüft:

```text
R0: keine zusätzliche Ruhe
R1: kurze Nullkontaktphase
R2: lange Nullkontaktphase
```

Die Pausenlängen sind äußere Versuchsparameter. Sie werden nicht als
Anpassungsrate oder Erholungsziel in die Runtime übernommen.

## 6. Modalitäten

Der erste Lauf bleibt vollständig synthetisch und verwendet nur bereits
vorhandene passive Rezeptoren:

1. auditive lokale Frequenzlage,
2. visuelle lokale Rasterlage,
3. kontrollierte lokale Rezeptorfläche als taktiler Stellvertreter.

Die Modalitäten werden getrennt ausgewertet. Es gibt keine Fusion und keinen
modalitätsübergreifenden Gewinner.

## 7. Primärmessungen

Für jede Modalität und jeden Zweig werden an der identischen Abschlussprobe
gemessen:

1. exakte Gleichheit der vollständigen Rezeptorlage,
2. lokale Differenz an `p`,
3. unbeabsichtigte Differenz an `q`,
4. Differenz der gesamten endlichen Rezeptorressource,
5. Digest der kanonischen Rezeptorausgabe.

Die bindende Nullvorhersage lautet:

```text
Ausgabe(K0, Rn) = Ausgabe(K1, Rn)
                = Ausgabe(K2, Rn)
                = Ausgabe(K3, Rn)
```

für jede geprüfte Ruhephase `Rn`.

## 8. Technische Kontrollen

- Die Abschlussprobe wird einmal erzeugt und unverändert an alle Zweige
  übergeben.
- Die Reihenfolge der Zweigauswertung wird vollständig permutiert.
- Jeder Zweig beginnt mit einer frischen Rezeptorinstanz.
- Observer an und aus müssen denselben Digest ergeben.
- Ein exakter Reset muss den Referenzdigest wiederherstellen.
- Kein Weltframe, Audiopuffer oder Rohsensorinhalt wird gespeichert.
- Zustände aus MCM-Feld, Nachhall oder Neuronenschicht dürfen nicht in die
  Rezeptorprüfung einfließen.

## 9. Baselines

Die Nullprüfung trennt noch keine organische Selbstregulation. Sie bereitet nur
den später notwendigen Vergleich vor:

```text
B0: unveränderte feste Rezeptorabbildung
B1: feste Verstärkung
B2: statisches Clipping
B3: gewöhnliche automatische Gain-Regel
B4: lokaler Ermüdungs-/Erholungsintegrator
B5: mehrere feste Leaky-Zeitskalen
```

B0 bis B2 dürfen in diesem ersten Lauf exakt oder analytisch geprüft werden.
B3 bis B5 bleiben äußere Vergleichsmodelle und erhalten keinen Zugriff auf die
Organismus-Runtime.

## 10. Entscheidung

### Erwarteter Nullbefund

Sind alle Abschlussausgaben exakt gleich, trägt der Versuch:

> Die vorhandenen Rezeptoren bewahren keine Belastungs- oder
> Erholungsgeschichte. Sie können deshalb ihre spätere lokale Aufnahme nicht
> aus eigener Weltteilnahme verändern.

Dies belegt nur den Funktionsmangel der festen Rezeptorabbildung.

### Unerwarteter Unterschied

Bleibt trotz identischer Abschlussprobe ein Unterschied, wird nicht von
Selbstregulation gesprochen. Zuerst sind zu prüfen:

- versteckter Adapter- oder Gerätezustand,
- nicht frische Rezeptorinstanz,
- veränderte Probe,
- Rundungs- oder Reihenfolgeartefakt,
- Observer-Rückwirkung,
- versehentlich einbezogener Feld- oder Nachhallzustand.

## 11. Stopplinie

Nach einem erwarteten Nullbefund bleiben gesperrt:

- Empfindlichkeitszustand,
- Gain- oder Schwellenanpassung,
- automatische Zielpegelregelung,
- Rezeptorrückschreibung,
- globale Aufmerksamkeit,
- Reflexionsbefehl,
- semantische Steuerung,
- Geräte- und Weltkontrolle.

Der Nullbefund gibt keine Mechanik frei.

## 12. Evidenzgrenze

Maximal E1 für die reproduzierbare Scheitergrenze der vorhandenen festen
Rezeptorabbildung.

E0 bleiben:

- lokale sensorische Disposition,
- organische Selbstregulation,
- funktionale Verbesserung,
- Ressourcenanpassung,
- Feldintelligenz.

## 13. Bester nächster Schritt

Nach Freigabe dieser Vorregistrierung folgt genau ein synthetischer passiver
Nullversuch über die drei vorhandenen Rezeptorfamilien. Erst danach wird
entschieden, ob überhaupt eine von B3 bis B5 getrennte fehlende Funktion
formuliert werden kann.
