# Kandidatenfamilien und C2-Baselinegrenze

## Status

Konzeptioneller Familienvergleich auf `E0 / NO_CANDIDATE_SELECTED`.

Dieses Dokument setzt den
[C2-Zulassungsvertrag](043_ZULASSUNGSVERTRAG_PASSIVER_C2_ORGANISATIONSKANDIDAT.md)
um, ohne eine Kandidatenmechanik auszuwählen. Es enthält keine
Updategleichung, keinen neuen Zustand und keine Runtime-Freigabe.

## Prüffrage

Gesucht wird nicht die technisch auffälligste Mechanik. Geprüft wird:

> Welche allgemeine Kandidatenfamilie könnte prinzipiell die
> Zustandsentwicklung unter B durch eine frühere A-Geschichte verändern,
> natürlich vollständig lösbar bleiben und danach eine neue B-Wirkung tragen,
> ohne das Ergebnis bereits durch Kante, Gewinner, Kapazität oder Zielstruktur
> einzubauen?

„Feldintelligenz“ ist dabei kein Auswahlkriterium. Sie bleibt lediglich eine
mögliche Fernhypothese.

## K1: unabhängige lokale Zeitspuren

### Grundidee

Jedes Neuron trägt eine oder mehrere eigene Spuren seiner lokalen
Feldgeschichte. Eine spätere Leserfunktion kombiniert diese Spuren mit der
gegenwärtigen Feldlage.

### Bewertung

```text
lokale Geschichtswirkung: möglich
Bildung unter B durch A verändert: nicht notwendig
natürliche Lösung: nur durch Leck oder Reset
Faktorisierbarkeit: vollständig
```

Diese Familie umfasst Leaky Traces, mehrere feste Zeitkonstanten,
Produktintegratoren und lokale Sättigung. C1 liegt in dieser Familie.

### Entscheidung

**Verworfen.**

K1 zerfällt strukturell in unabhängige lokale Integratoren plus festen Leser
und wird durch B1 bis B4 abgedeckt.

## K2: lokale Empfänglichkeit oder Metadisposition

### Grundidee

Ein lokaler Zustand verändert, wie stark ein Neuron spätere Feldwirkung
aufnimmt oder weiterleitet.

### Bewertung

Bleibt die Empfänglichkeit jedes Neurons unabhängig, ist K2 nur eine anders
benannte K1-Spur. Eine fest programmierte Modulation der späteren Ausgabe
wiederholt die C1-Leserwirkung.

Erst wenn die Empfänglichkeit eines Bereichs die **Zustandsänderung** eines
überlappenden Bereichs mitprägt, verlässt K2 die unabhängige Familie. Dann ist
sie keine eigenständige Familie mehr, sondern fällt unter K6.

### Entscheidung

**In unabhängiger Form verworfen.**

Eine bloß langsamere oder nichtlinearere Empfänglichkeit ist kein C2.

## K3: explizite Beziehung, Kante oder Partnerzustand

### Grundidee

Zwischen zwei Trägern wird eine Beziehung mit Stärke, Alter oder Kontinuität
gespeichert.

### Bewertung

Diese Form kann A-B-Wirkung technisch direkt tragen. Sie setzt jedoch bereits
voraus:

- welche Träger Partner sind,
- wo eine Kante liegt,
- welcher Zustand zu welcher Beziehung gehört,
- und häufig, wann eine Beziehung erzeugt oder gelöscht wird.

Damit würde die gesuchte Organisation als Datenstruktur vorgegeben.

### Entscheidung

**Verworfen.**

K3 wiederholt die statische Verdrahtungssackgasse und verletzt die
Darstellungsoffenheit.

## K4: lokale oder globale Normalisierung

### Grundidee

Mehrere lokale Aktivitäten oder Zustände teilen eine feste Summe, Norm oder
Kapazität. Stärkere Beanspruchung bei A reduziert dadurch B.

### Bewertung

Normalisierung kann den gewünschten Interaktionsrest unmittelbar erzeugen.
Die Konkurrenz folgt dann aber aus der programmierten Norm:

```text
Summe begrenzt
-> A größer
-> B kleiner
```

Globale Normalisierung verletzt zusätzlich die U-Kontrolle. Lokale
Normalisierung bleibt eine bindende Baseline, wenn Radius und Norm fest
vorgegeben sind.

### Entscheidung

**Als Kandidatenfamilie verworfen.**

K4 bleibt als B6 beziehungsweise B7 erhalten.

## K5: Oszillator-, Phasen- oder Resonanzträger

### Grundidee

Lokale Oszillatoren oder Phasenlagen tragen Geschichte und beeinflussen sich
über feste Nachbarschaft.

### Bewertung

Diese Familie kann reichhaltige Muster erzeugen. Für den aktuellen
Funktionsmangel führt sie jedoch zusätzliche Voraussetzungen ein:

- eine innere Takt- oder Phasenvariable,
- eine feste Kopplungsform,
- eine Frequenz- oder Resonanzskala,
- häufig eine feste Synchronisationsbedingung.

Ein interessanter Verlauf wäre noch kein Nachweis von Lösung und
Wiederbindung. Zudem könnte eine feste lokale Rekurrenz dieselbe Dynamik
tragen.

### Entscheidung

**Für C2 verworfen.**

K5 ist für den kleinsten nächsten Kandidaten unnötig reich und würde den
Funktionsmangel mit zusätzlicher Dynamik überladen.

## K6: gekoppelte lokale Feldverformung

### Grundidee

Jeder Feldort besitzt dieselbe darstellungsoffene lokale Zustandsrolle. Deren
Änderung hängt nicht nur von der eigenen Geschichte ab, sondern auch von der
gegenwärtigen Zustandslage im bereits vorhandenen lokalen Feldradius.

Es werden keine Paare, Kanten oder Gewinner bezeichnet. Eine A-Geschichte
könnte eine räumlich verteilte Zustandslage bilden. Weil B denselben lokalen
Bereich teilweise beansprucht, könnte B unter identischer äußerer Evidenz eine
andere Zustandsentwicklung erfahren.

### Warum die Familie den C2-Mangel prinzipiell adressiert

- Die A-Wirkung könnte bereits die Bildung während B verändern.
- Die Kopplung läge im bestehenden lokalen Feldraum, nicht in einer Partner-ID.
- Spiegelung und Übersetzung könnten aus derselben lokalen Bedingung folgen.
- Eine veränderte Weltgeschichte D1 könnte die verteilte Lage weiter
  reorganisieren, statt sie per Löschbefehl zu entfernen.
- Nach vollständiger Lösung könnte B denselben lokalen Raum anders prägen.

### Offene Risiken

- Eine fest gekoppelte lokale Dynamik ist mathematisch weiterhin eine
  Rekurrenz.
- Ein fester Leser könnte die eigentliche Wirkung erneut erst nachträglich
  erzeugen.
- Begrenzte lokale Werte könnten nur Sättigung als scheinbare Ressource
  vortäuschen.
- D1 könnte lediglich einen alten Zustand überschreiben, ohne funktionale
  Lösung zu zeigen.
- Eine zu allgemeine Baseline B5 könnte die gesamte Familie bereits umfassen.

### Entscheidung

**Einzige bedingt zulässige Familie, aber noch nicht als C2 ausgewählt.**

K6 darf erst konkretisiert werden, nachdem die Grenze zu B5 operational und
fair festgelegt ist.

## K7: konservierter Ressourcenträger

### Grundidee

Ein endlicher lokaler Stoff, Token oder Ressourcenwert wird zwischen
Feldorten verschoben. A bindet einen Anteil; B kann dadurch weniger binden.

### Bewertung

Diese Familie erzeugt Freigabe und Wiederbindung direkt aus einer
programmierten Erhaltungs- oder Kapazitätsgröße. Sie beantwortet die
Forschungsfrage, indem sie „Ressource“ zur Mechanik macht.

### Entscheidung

**Verworfen.**

Ressource bleibt eine beobachtbare Funktion, keine vorgegebene Variable.

## K8: Musterarchiv oder Reservoir

### Grundidee

Frühere Feldvektoren oder Projektionen werden in einem lokalen oder globalen
Reservoir bewahrt und später verglichen.

### Bewertung

Diese Familie kann Wiedererkennung technisch leisten, speichert aber
zusätzliche Historie oder Rohmuster. Sie besitzt mehr Zeitpräfix und meist mehr
Zustand als die fairen Baselines. Lösung wäre gewöhnlich Vergessen, Überschreiben
oder explizite Speicherverwaltung.

### Entscheidung

**Verworfen.**

K8 verschiebt das Projekt in Richtung Musterbank oder Datenbank.

## Zusammenfassung des Familienaudits

| Familie | Ergebnis | Hauptgrund |
|---|---|---|
| K1 unabhängige Spuren | verworfen | vollständig faktorisiert |
| K2 lokale Empfänglichkeit | verworfen | C1-Leserwirkung ohne Kopplung |
| K3 Kante oder Partnerzustand | verworfen | Organisation vorgegeben |
| K4 Normalisierung | verworfen | Konkurrenz programmiert |
| K5 Oszillator oder Phase | verworfen | überlädt den Funktionsmangel |
| K6 gekoppelte Feldverformung | bedingt offen | Bildung unter B prinzipiell gekoppelt |
| K7 Ressourcenträger | verworfen | Kapazität direkt programmiert |
| K8 Archiv oder Reservoir | verworfen | zusätzliche Historienbank |

Der Vergleich wählt K6 noch nicht aus. Er zeigt nur, dass K6 als einzige
Familie nicht bereits durch eine verbotene Datenstruktur oder eine bekannte
einfache Baseline ausgeschlossen ist.

## Entdeckte Baseline-Unschärfe

Die Bezeichnung:

```text
B5 = statische lokale Rekurrenz
```

ist für eine Kandidatenauswahl noch nicht ausreichend operational.

Zwei Lesarten sind möglich:

### Enge Lesart

Eine feste lineare oder vorregistrierte einfache lokale Rekurrenz mit
zustandsunabhängigen Koeffizienten.

Diese Baseline ist ein starkes, aber begrenztes Gegenmodell.

### Unbegrenzte Lesart

Jede beliebige nichtlineare lokale Zustandsfortschreibung mit endlichem
Radius.

Diese Klasse enthält zwangsläufig auch jeden digitalen K6-Kandidaten. Unter
dieser Lesart könnte kein C2 jemals einen eigenen Befund tragen, weil seine
vollständige Mechanik selbst als B5 bezeichnet würde.

## Methodische Konsequenz

Vor einer C2-Vorregistrierung müssen B1 bis B6 als konkrete, endliche
Hypothesenklassen beschrieben werden. Dabei müssen feststehen:

- Zahl persistenter Zustandswerte,
- erlaubte lineare und nichtlineare Operationen,
- lokale Reichweite,
- Parameterzahl und Präzision,
- gelesene Feldrollen,
- verfügbare Vergangenheit,
- Leserform,
- Bildungs- und Lösungsmöglichkeiten.

Die Baselines dürfen weder absichtlich schwach sein noch durch unbegrenzte
Funktionsfreiheit jeden Kandidaten nachträglich imitieren.

## Keine Auswahl durch gewünschtes Ergebnis

K6 darf nicht deshalb gewählt werden, weil gekoppelte Dynamik organischer
klingt. Vor einer Auswahl muss eine konkrete Hypothese erklären:

1. warum A die Zustandsbildung unter B vor dem Leser verändert,
2. warum U keine entsprechende Organisationswirkung erzeugt,
3. warum D1 vollständige Lösung statt bloßes Überschreiben erlaubt,
4. warum neue B-Evidenz danach eine neue Feldfunktion trägt,
5. warum B1 bis B6 mit fairem Budget dies nicht gleich erklären.

Kann diese Begründung nicht vor einer Implementierung gegeben werden, bleibt
C2 geschlossen.

## Freigabegrenze

```text
Kandidatenfamilien verglichen:       ja
bekannte Sackgassen ausgesondert:    ja
bedingt offene Familie gefunden:     ja, K6
konkreter C2 ausgewählt:              nein
Baseline B5 operational abgegrenzt:  nein
Updategleichung festgelegt:           nein
persistenter Zustand implementiert:   nein
Runtime-Erweiterung:                  nein
```

## Nächster Schritt

Als Nächstes werden ausschließlich die C2-Baselineklassen B1 bis B6
operational definiert und gegeneinander abgegrenzt. Erst wenn B5 stark, aber
nicht unbegrenzt ist, darf geprüft werden, ob K6 einen kleinsten fairen
Kandidatenvorschlag tragen kann.
