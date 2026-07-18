# MINI_DIO-Abgleich zum Memory-Substrat

## Status

Forensischer Architekturabgleich auf `E1 / ARCHITECTURE_AUDIT`.

```text
MINI_DIO gelesen:                 ja
übertragbare Funktionen benannt: ja
statische Sackgassen abgegrenzt: ja
Memory-Darstellung ausgewählt:   nein
Runtime-Erweiterung freigegeben: nein
```

Dieser Abgleich erfüllt den nächsten Schritt des
[darstellungsoffenen Memory-Substratvertrags](048_DARSTELLUNGSOFFENER_MEMORY_SUBSTRATVERTRAG.md).
Er übernimmt keine alte Variable oder Mechanik aus MINI_DIO.

## Fragestellung

MINI_DIO wird nicht danach gelesen, welche alte Topologie in das gemeinsame
MCM-Feld eingebaut werden könnte. Geprüft wird ausschließlich:

1. Welche notwendige Memory-Substratfunktion war tatsächlich kausal getragen?
2. Welche Wirkung entstand nur aus fester Programmstruktur?
3. Welche Erfahrungsschicht blieb passiv oder außerhalb des laufenden Feldes?
4. Welche offene Funktion bleibt für `MCM_FIELD_ORGANISM` übrig?

## Tatsächlich getragene Teilfunktionen

### 1. Kontinuierliche Feldkausalität

Wird dieselbe MCM-Feldinstanz über Kontaktgrenzen weitergeführt, wirkt ihr
Vorzustand in den folgenden Weltkontakt. Die Wirkung ist real, reproduzierbar
und ohne externen Memory-Leser vorhanden.

Der Träger ist jedoch der bereits bekannte schnelle Nachhall. Unter reizfreier
Fortsetzung schwächt sich die Wirkung stark ab und alle geprüften Pfade
konvergieren wieder zum Resetfeld. MINI_DIO trägt damit:

```text
kontinuierliches Feld
+ kurze geschichtsabhängige Gegenwart
+ natürliche Relaxation der schnellen Spur
```

Es trägt damit noch kein Memory über die schnelle Spur hinaus.

### 2. Intrinsisch lesbare Eigenform

Aus aufeinanderfolgenden eigenen Feldzuständen lassen sich relationale
Änderungsformen und eine variable Eigenzeit rekonstruieren. Dafür ist kein
Vergleich mit einem parallelen Resetfeld notwendig.

Das ist eine wichtige Funktionsgrenze: Ein laufendes Feld kann Unterschiede
seiner eigenen Bewegung tragen, ohne dass zuvor ein Objekt, Wort oder
Episodenlabel gespeichert wurde.

Die konkrete MINI_DIO-Form ist aber nicht übertragbar. Ihre Neuronenmitglieder,
Eingangsgewichte und gerichtete Nachbarschaft folgen einer festen
Indexarchitektur. Die beobachtete Form ist daher teilweise Form dieser
Programmstruktur.

### 3. Bewegliche Beziehungsgeschichte

Die passive MINI_DIO-Beziehungsschicht kann aus wiederholter Erfahrung eine
bewegliche Ordnung bilden, ohne dauerhaft dieselben Beziehungspartner zu
konservieren. Ereignispräfixe reichen dabei als Quelle aus; zusätzliche
abgeleitete Zustände waren häufig redundant.

Diese Ordnung entsteht jedoch erst aus abgeschlossenen Weltprofilen und wird
bei der Weltfinalisierung aufgebaut. Sie ist nicht während des laufenden
Kontakts als kausaler Feldzustand verfügbar und wirkt nicht in das Feld zurück.

Damit trägt MINI_DIO eine passive Erfahrungsauswertung, aber kein
feldinternes Memory-Substrat.

## Durch Code bestätigte Sackgassen

### Feste Kettenarchitektur

Das alte `MiniMCMField` führt die Neuronen in Indexreihenfolge aus. Jedes
folgende Neuron erhält die Aktivierung seines Vorgängers mit dem konstanten
Faktor `0.12`. Auch die Eingangs- und Aktionsgewichte werden deterministisch
aus dem Neuronenindex initialisiert.

Diese Architektur kann Koordination, Rangformen und scheinbare Mikrotopologie
erzeugen. Sie darf nicht als organisch entstandene Kopplung gelesen werden.

Nicht übernommen werden:

- feste Indexrichtung;
- fester Nachbarschaftsfaktor;
- indexabhängige Gewichtsidentität;
- Rangordnung als Memory-Darstellung;
- Koordination als Wachstumssignal.

### Observer- und Finalisierungsschichten

Die stärkste bewegliche Beziehungsschicht wird aus passiven
Nachbarschaftsereignissen aufgebaut. Ihre Aktualisierung hängt ausdrücklich an
einem `finalization_index` und an bereits abgeschlossenen Weltprofilen.

Nicht übernommen werden:

- Welt- oder Episodenfinalisierung als innere Naturbedingung;
- passive JSON-Strukturen als Organismusmemory;
- nachträgliche Rang-, Pareto- oder Nachbarschaftsauswahl;
- externe Weltlabels und fertige Episodensymbole;
- Observerbeziehungen als Feldzustand.

### Extern organisierte Offline-Phasen

Die alten Schlaf- und Konsolidierungsschichten sind passiv, werden extern
gestartet und wirken nicht in Feld oder Handlung zurück. Sie belegen keine
endogene Offline-Erholung desselben laufenden Organismusfeldes.

## Belastbar übertragbare Architekturgrenzen

Aus MINI_DIO werden nur folgende Grenzen übernommen:

1. **Dieselbe Feldinstanz muss weiterlaufen.**
   Ein nach jedem Weltabschnitt neu erzeugtes Feld besitzt keine fortlaufende
   eigene Kausalgeschichte.

2. **Bildung muss im laufenden Feld stattfinden.**
   Ein erst nach Welt- oder Episodenabschluss erzeugter Datensatz ist kein
   feldlokales Memory.

3. **Die Quelle muss kausal minimal bleiben.**
   Abgeleitete Profile dürfen keinen zweiten Zustand vortäuschen, wenn ihr
   Ereignispräfix bereits vollständig genügt.

4. **Der Zustand muss vor dem Observer verfügbar sein.**
   Diagnose darf eine innere Form sichtbar machen, aber sie nicht erzeugen.

5. **Identität und Richtung dürfen nicht vorgegeben sein.**
   Neuronenindex, Sensorkanal, Weltlabel und Episodenname dürfen keine spätere
   Bindung bestimmen.

6. **Alte Wirkung muss vollständig funktionslos werden können.**
   Ein unverlierbares Archiv, eine konservierte Kante oder bloße passive
   Rückkehr erfüllt den Memory-Substratvertrag nicht.

7. **Neue Weltgeschichte muss danach erneut prägen können.**
   Diese Offenheit darf nicht durch einen freien Speicherplatz oder eine
   programmierte Wiederbindungsoperation hergestellt werden.

## Zentrale Schlussfolgerung

MINI_DIO liefert keinen fertigen Memory-Substratmechanismus. Es liefert zwei
getrennte, belastbare Vorbedingungen:

```text
laufendes Feld
-> kausale, selbstlimitierende Vorzustandsspur
-> intrinsisch beobachtbare eigene Zustandsänderung

abgeschlossene Erfahrung
-> passiv rekonstruierbare bewegliche Beziehungsordnung
```

Die erste Seite ist feldlokal, aber durch eine feste Architektur geprägt und
zu kurzlebig. Die zweite Seite ist erfahrungsgebildet, aber nicht feldlokal und
nicht kausal zurückgelesen. Ihre direkte Verbindung würde genau die alte
Sackgasse wieder einführen.

Der verbleibende Funktionsmangel lautet darstellungsoffen:

> Während kontinuierlichen Weltkontakts muss eine lokal verfügbare
> Erfahrungsprägung entstehen können, die spätere Feldbildung kausal
> mitverändert, unter weiterer Erfahrung vollständig funktionslos werden und
> danach neu prägbar sein kann. Ihre Identität, Richtung und Bedeutung dürfen
> weder durch Neuronenindex noch durch Observer oder Weltfinalisierung
> vorgegeben sein.

Das ist eine Funktionsgrenze. Sie fordert weder Beziehung, Kante, Topologie,
Rang noch eine bestimmte Zustandsvariable.

## Freigabegrenze

```text
kontinuierlicher Feldträger bestätigt:    ja
intrinsische Zustandsänderung bestätigt:  ja
passive Erfahrungsordnung bestätigt:      ja
fertiges Memory-Substrat in MINI_DIO:      nein
alte Kopplungsmechanik übertragbar:        nein
neuer Kandidat bestimmt:                  nein
Runtime-Erweiterung freigegeben:           nein
```

## Nächster Schritt

Vor einer Memory-Darstellung wird die **lokale Ereignisquellgrenze** der
aktuellen MCM-Runtime geprüft:

```text
abgeschlossener lokaler Vorzustand
+ gegenwärtige lokale Weltevidenz
-> welche Zustandsänderung liegt bereits innerhalb des Feldfortschritts vor?
```

Dabei wird ausschließlich geklärt:

- was ein MCM-Neuron während seines atomaren Schritts selbst kausal besitzt;
- was erst eine spätere Feldprobe oder ein Observer berechnet;
- ob eine lokale Zustandsänderung ohne Rang, Episode oder Beziehungs-ID
  offengelegt werden kann;
- welche Teile davon bereits vollständig durch `activation` und `afterimage`
  erklärt sind.

Erst danach kann entschieden werden, ob überhaupt eine kleinste digitale
Darstellung untersucht werden darf. Bis dahin bleiben Gleichung, Kandidat und
Runtime geschlossen.
