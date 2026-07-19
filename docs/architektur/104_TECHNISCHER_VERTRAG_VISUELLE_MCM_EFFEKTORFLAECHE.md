# Technischer Vertrag der visuellen MCM-Effektorfläche

## Status

```text
Vertragstyp:                         technische Kausalgrenze
Ausgangsquelle:                      abgeschlossene MCM-Feldaktivierung
Ausgabemedium:                       digitale Fläche umgesetzt
Rückkehr:                            reale Bildschirm-/Kamerastufe offen
Semantik, Auswahl oder Reward:       ausgeschlossen
Effektor-Runtime:                    nicht implementiert
minimale digitale Implementierung:   umgesetzt
Evidenzstufe:                        E0
```

Dieser Vertrag setzt die
[Grundlagenentscheidung zur feldgebundenen Weltwirkung](103_GRUNDLAGENENTSCHEIDUNG_FELDGEBUNDENE_WELTWIRKUNG.md)
technisch eng um.

Er erzeugt noch keine Bildschirmwirkung. Er legt fest, was eine spätere
minimale Implementierung unverändert erfüllen muss.

## 1. Zweck

Die Effektorfläche soll genau einen Kausalpfad ermöglichen:

```text
abgeschlossener MCM-Feldzustand
-> technisch definierte Lichtfläche
-> reale Bildschirmwirkung
-> reale Kameraaufnahme
-> visueller Rezeptorkontakt
-> gemeinsames MCM-Feld
```

Der Vertrag prüft keine Handlung, Kommunikation oder gewünschte
Weltveränderung.

## 2. Zulässige Feldquelle

Die erste Effektorfläche liest ausschließlich:

- `field_id`;
- `geometry_id`;
- abgeschlossene Organismuszeit;
- Neuronenidentitäten;
- zweidimensionale Neuronenpositionen;
- aktuelle `activation`.

Sie liest nicht:

- `afterimage`;
- lokale Feldproben;
- Rezeptorkontakte;
- Dock- oder Modalitätsbedeutung;
- frühere Feldzustände;
- Memory-, Beziehungs- oder Semantikrollen;
- Observerprotokolle.

Die Begrenzung auf `activation` ist funktional begründet: Im ersten
Kausalnachweis wird nur die gegenwärtige Feldwirkung physisch ausgedrückt.
Der schnelle Nachhall darf nicht zusätzlich als verdeckter zweiter
Ausgabepfad wirken.

## 3. Abgeschlossener Eingang

Eine Ausgabe darf nur aus einem unveränderlichen
`SharedMCMFieldSnapshot` entstehen.

Für jeden Ausgaberahmen gilt:

```text
window_start_tick < window_end_tick
snapshot.tick ist abgeschlossen
alle Neuronen besitzen denselben Tick
alle Positionen sind eindeutig
alle Aktivierungen liegen in [-1, 1]
```

Ein noch laufender Feldtakt, eine teilweise Neuronenschicht oder eine
Mischung verschiedener Ticks wird abgelehnt.

## 4. Feste zweidimensionale Geometrie

Die vorhandene Audio-Video-Live-Runtime legt alle Docks in einer gemeinsamen
zweidimensionalen Neuronengeometrie ab.

Die erste Effektorfläche akzeptiert ausschließlich diese
zweidimensionale Form:

```text
Position eines Neurons = (row, column)
```

Die Ausgabegeometrie wird ohne Sortier- oder Auswahlregel aus dem kleinsten
umschließenden Rechteck aller Feldpositionen gebildet.

Mit den kleinsten vorhandenen Koordinaten `r_min` und `c_min` wird jede
Position zuerst nur technisch auf den Ausgabeursprung verschoben:

```text
r_out = r - r_min
c_out = c - c_min
```

Jeder Feldort erhält genau zwei horizontal benachbarte Ausgabeflächen:

```text
Feldposition (r, c)
-> Ausgabeposition (r_out, 2*c_out)
-> Ausgabeposition (r_out, 2*c_out + 1)
```

Nicht belegte Feldpositionen innerhalb des Rechtecks erhalten die neutrale
Ausgabe. Es werden keine Zellen übersprungen, verdichtet, priorisiert oder
nach Modalität gruppiert.

## 5. Feste technische Übertragung

Sei `a` die validierte Aktivierung eines Feldortes mit:

```text
-1 <= a <= +1
```

Die beiden normierten Grauintensitäten lauten:

```text
I_left  = 0.50 + 0.25 * a
I_right = 0.50 - 0.25 * a
```

Damit gilt:

```text
0.25 <= I_left  <= 0.75
0.25 <= I_right <= 0.75
I_left + I_right = 1.00
```

Diese Abbildung ist:

- stetig;
- affin;
- umkehrbar innerhalb der technischen Ausgabe;
- für alle Feldorte identisch;
- frei von Schwelle, Clipping, Gewinner und Aktionswahl;
- begrenzt auf einen vorab festen Helligkeitsbereich.

Die beiden Flächen sind Grauflächen. Es werden keine bedeutungstragenden
Farben, Symbole, Texte, Formen oder Objektbilder gerendert.

## 6. Neutrale Ausgabe

Für einen vollständig neutralen Feldzustand gilt:

```text
a = 0
-> I_left = 0.50
-> I_right = 0.50
```

Die gesamte Effektorfläche ist dann gleichmäßig mittelgrau.

Die neutrale Ausgabe enthält:

- kein Rauschen;
- keine zufällige Variation;
- keine Nullpunktbewegung;
- kein Blinken;
- keinen Ruhepuls;
- keine versteckte Ereigniskennung.

Neutral bedeutet hier technisch definierte gleiche Lichtlage, nicht
Abwesenheit von Bildschirmlicht.

## 7. Physische Darstellungsgrenze

Die berechnete Effektorfläche muss als tatsächlich sichtbare
Bildschirmfläche präsentiert werden.

Unzulässig sind:

- direktes Einspeisen des Ausgaberahmens in den visuellen Rezeptor;
- virtuelle Kamera mit internem Frame-Sharing;
- Screenshot als Rezeptorquelle;
- Browser- oder Fenstercapture als Ersatz für die reale Kamera;
- Weitergabe der Feldaktivierung an den Kameraadapter;
- gemeinsame Speicherreferenz zwischen Ausgabe und Rezeptor.

Zulässig ist ausschließlich:

```text
berechnete Lichtfläche
-> physischer Bildschirm
-> optischer Raum
-> reale Kamera
```

## 8. Zeitvertrag

Jeder Kausalschritt verwendet vier abgeschlossene Zeitlagen:

```text
T0: MCM-Feldfenster abgeschlossen
T1: Effektorrahmen daraus unveränderlich erzeugt
T2: Bildschirmdarstellung vollständig begonnen
T3: späteres Kamera-Aufnahmefenster vollständig abgeschlossen
```

Verbindliche Ordnung:

```text
T0 < T1 <= T2 < Beginn(T3) < Ende(T3)
```

Die Kamera darf keinen Frame verwenden, dessen Belichtungs- oder
Aufnahmefenster vor der vollständigen Bildschirmpräsentation begonnen hat.

Die Implementierung muss erfassen:

- Feldfenster `window_start_tick` und `window_end_tick`;
- Erzeugungszeit des Effektorrahmens;
- bestätigte Präsentationszeit;
- Start und Ende des verwendeten Kamera-Aufnahmefensters.

Die Wartezeit wird vor einem Lauf aus gemessener Bildschirm- und Kamerarate
festgelegt. Sie darf nicht abhängig vom Feldwert, dem Kamerabild oder einem
gewünschten Ergebnis verändert werden.

## 9. Aufnahmefenster

Der erste passive Lauf verwendet pro Effektorrahmen genau ein
vorregistriertes Kamera-Aufnahmefenster.

Es gibt:

- kein adaptives Warten auf sichtbare Veränderung;
- keine Auswahl des hellsten Frames;
- keine Mittelung mehrerer Frames nach Ergebnis;
- keine Wiederholung bei unerwünschter Feldantwort;
- keine Glättung oder künstliche Stabilisierung.

Fehlt ein vollständiger Kamera-Frame im vorregistrierten Fenster, gilt der
Schritt als technisch unvollständig. Es wird kein Ersatzframe erzeugt.

## 10. Observerseitige Provenienz

Der passive Observer darf dokumentieren:

- Run-ID;
- Feldsnapshot-Digest;
- Effektorrahmen-Digest;
- Präsentationszeit;
- Kamera-Frame-Index und Aufnahmezeit;
- Sichtlinie offen oder blockiert;
- Effektorfläche aktiv oder neutralisiert;
- technische Bildschirm- und Kameraeinstellungen.

Diese Rollen gelangen nicht in:

- Effektorintensitäten;
- Kamera-Pixel;
- visuellen Rezeptorzustand;
- Rezeptorenverteiler;
- MCM-Neuronenschicht;
- Feldsnapshot.

Der Observer darf weder Ausgabe noch Aufnahmezeit noch Feldtransition
verändern.

## 11. Sicherheitsgrenze

Die erste Implementierung ist endlich und manuell startbar.

Verbindlich sind:

- kein Vollbildzwang;
- keine Betriebssystem-Helligkeitssteuerung;
- keine Kamerabelichtungssteuerung durch das MCM-Feld;
- kein schnelles Blinken;
- keine Audioausgabe;
- feste maximale Bildrate;
- äußerer Sofort-Stopp;
- nach Stopp sofortige neutrale Mittelgrauausgabe;
- keine automatische Wiederaufnahme.

Die Softwareintensität bleibt immer in `0.25..0.75`. Die physische
Bildschirmhelligkeit wird vor dem Lauf äußerlich festgelegt und während des
Laufs nicht verändert.

## 12. Pflichtzweige

### E0 - neutrale Feldlage

```text
activation = 0 an allen Feldorten
-> homogene Mittelgrauausgabe
```

### E1 - bekannte nichtneutrale Feldlage

Eine abgeschlossene kontrollierte Feldlage wird ohne weitere Verarbeitung
auf die feste Effektorfläche übertragen.

### E2 - identische Wiederholung

Dieselbe abgeschlossene Feldlage muss bitgleich denselben digitalen
Effektorrahmen erzeugen.

### E3 - Feldvariation

Eine kontrolliert veränderte lokale Aktivierung muss ausschließlich die
beiden zugeordneten Ausgabeflächen gemäß derselben affinen Regel verändern.

### B0 - physische Sichtlinie blockiert

Die Effektorfläche wird regulär ausgegeben, aber der optische Weg zur Kamera
wird physisch blockiert.

### B1 - Effektorfläche neutralisiert

Die Kamera sieht denselben Bildschirmbereich, die ausgegebene Fläche bleibt
jedoch homogen mittelgrau.

### P0 - Provenienznull

Identische Feldlage und identische Präsentation werden mit anderer
observerseitiger Run-ID wiederholt. Digitaler Effektorrahmen, reale
Lichtwirkung und Rezeptorfolge müssen unverändert bleiben.

### O0 - Observernull

Der Lauf wird einmal mit vollständigem passivem Observerprotokoll und einmal
mit minimaler technischer Protokollierung ausgeführt. Der Kausalpfad muss
gleich bleiben.

## 13. Entscheidende Kausalkontrollen

Ein physischer Rückkopplungspfad ist erst gestützt, wenn:

1. E0 exakt die neutrale Ausgabe erzeugt.
2. E1 und E3 die affine Übertragung exakt erfüllen.
3. E2 digital bitgleich wiederholbar ist.
4. Die reale Kamera E1 gegenüber B1 unterscheiden kann.
5. B0 die effektspezifische optische Rückkehr entfernt.
6. P0 keine interne Provenienzwirkung zeigt.
7. O0 Observerneutralität bestätigt.
8. Der visuelle Rezeptor ausschließlich den real aufgenommenen Kameraframe
   verarbeitet.
9. Der Rezeptorrahmen keine Effektor- oder Feldmetadaten enthält.
10. Die spätere MCM-Feldlage vollständig über den regulären visuellen
    Rezeptorpfad entsteht.

## 14. Aussagegrenze eines positiven Laufs

Ein positiver Lauf trägt höchstens:

```text
abgeschlossene MCM-Feldlage
-> feste bedeutungsfreie Lichtwirkung
-> reale optische Welt
-> reguläre visuelle Rezeptorrückkehr
```

Er trägt nicht:

- Handlung;
- Agency;
- Selbstregulation;
- Memory;
- Reflexion;
- inneren Dialog;
- Semantik;
- entwickelte MCM-Feldtopologie;
- Feldintelligenz.

Eine veränderte spätere Feldlage wäre zunächst vollständig durch die aktuelle
optische Rückkehr erklärt.

## 15. Abbruchkriterien

Der erste Lauf wird abgebrochen und nicht interpretiert, wenn:

- ein interner Frame oder Feldwert den Kamerapfad umgeht;
- Präsentations- und Aufnahmefenster überlappen;
- eine Ausgabefläche außerhalb `0.25..0.75` liegt;
- eine Schwelle, Auswahl oder Ergebnisregel benötigt wird;
- die Kameraeinstellung feldabhängig verändert wird;
- B0 weiterhin dieselbe effektspezifische Rückkehr zeigt;
- Provenienz oder Observer das Ergebnis verändert;
- ein technischer Ausfall durch Wiederholung kaschiert wird.

## Freigabe

Nach diesem Vertrag war genau eine minimale passive Implementierung
freigegeben:

```text
SharedMCMFieldSnapshot
-> unveränderlicher visueller Effektorrahmen
-> manuell präsentierbare Bildschirmfläche
```

Noch nicht freigegeben ist ein automatischer geschlossener Dauerlauf.
Die reale Kamera-Rückkehr wird erst nach bestandenen digitalen Null- und
Geometriekontrollen zugeschaltet.

## Implementierungsstand

Die digitale Effektorfläche ist in
[`visual_mcm_effector_surface.py`](../../mcm_field_organism/visual_mcm_effector_surface.py)
umgesetzt.

Sie besteht ausschließlich aus:

- `VisualMCMEffectorCell`;
- `VisualMCMEffectorFrame`;
- der puren Funktion `project_visual_mcm_effector_surface`;
- kanonischer Serialisierungs- und Digestbildung;
- expliziten Sperren gegen Rückschreibung, Zustand und Zufallsquelle.

Die Implementierung:

- akzeptiert nur einen validierten `SharedMCMFieldSnapshot`;
- weist nicht zweidimensionale Felder ab;
- normalisiert verschobene Feldkoordinaten nur geometrisch;
- bildet jede Aktivierung exakt durch die affine Graupaar-Regel ab;
- hält unbelegte Rasterorte exakt auf `0.50`;
- prüft `-1..1` erneut und clippt keinen beschädigten Wert;
- verändert den Quellsnapshot nicht;
- besitzt keinen Bildschirm-, Kamera- oder Runtimezugriff.

Die zugehörigen
[`test_visual_mcm_effector_surface.py`](../../tests/test_visual_mcm_effector_surface.py)
prüfen neun digitale Vertragsgruppen. Zusammen mit Snapshot, gemeinsamer
Feldverteilung, Feldsession und Audio-Video-Live-Geometrie bestehen
43 direkt abhängige Tests.

Die begrenzte Bildschirmdarstellung ist zusätzlich in
[`visual_mcm_effector_presenter.py`](../../mcm_field_organism/visual_mcm_effector_presenter.py)
umgesetzt. Sie:

- übernimmt ausschließlich einen bereits abgeschlossenen Effektorrahmen;
- quantisiert dessen Intensitäten deterministisch in gerätefähige
  16-Bit-Grauwerte;
- vergrößert jeden Rasterwert nur durch eine feste quadratische Zellgröße;
- hält den gezeigten Rahmen während der gesamten Präsentation unverändert;
- schließt spätestens nach 30 Sekunden;
- enthält keine Beschriftung, Animation oder nachträgliche Bildverarbeitung;
- verbindet weder Kamera noch Rezeptor oder MCM-Feld;
- schreibt keinen Zustand zurück.

Das manuell startbare Werkzeug
[`present_visual_mcm_effector_frame.py`](../../tools/present_visual_mcm_effector_frame.py)
liest genau einen kanonischen `SharedMCMFieldSnapshot`, erzeugt daraus genau
einen Effektorrahmen und zeigt diesen zeitlich begrenzt. Es startet keinen
Feldlauf und speichert keine Präsentationsdaten im Organismus.

Die acht zusätzlichen Vertragsgruppen in
[`test_visual_mcm_effector_presenter.py`](../../tests/test_visual_mcm_effector_presenter.py)
prüfen Geometrie, exakte Grauwertquantisierung, Neutralität,
Reproduzierbarkeit, Laufzeitgrenzen, Unveränderlichkeit und die Sperren gegen
Rückkanal oder Zusatzmechanik. Mit den direkt abhängigen Kontrollen bestehen
nun 51 Tests.

Damit sind die digitale Stufe und ihre begrenzte Präsentationsfähigkeit
abgeschlossen:

```text
MCM-Feldsnapshot
-> digitaler Effektorrahmen
-> statische Bildschirmdarstellung
```

Die Software kann damit Bildschirmlicht ausgeben. Eine vollständige
physische Welt-Rückkopplung ist noch nicht gezeigt, weil die getrennte
Kamerarückkehr fehlt.

## Wie es am besten weitergeht

Als nächster Schritt wird die statische Präsentation einmal manuell mit einem
realen abgeschlossenen Feldsnapshot geprüft. Dabei werden nur sichtbare
Geometrie, unveränderte Darstellung und zeitgerechtes Schließen bestätigt.

Erst danach folgt als eigener, weiterhin passiver Schritt die getrennte
Kameraaufnahme der Bildschirmfläche. Sie darf den internen Effektorrahmen
nicht lesen und muss über den regulären visuellen Rezeptorpfad zurückkehren.
Ein automatischer Dauerlauf bleibt geschlossen.
