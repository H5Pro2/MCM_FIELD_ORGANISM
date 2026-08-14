# W5-E: Richtungsentscheid fuer eine homogene Zweizeiten-MCM-Feldkomponente

Stand: 2026-08-09

Entscheidung: `HOMOGENEOUS_TWO_TIMESCALE_MCM_SUBSTRATE_PATH_OPEN`

Entscheidungsart: Architektur und Forschungsrichtung

Runtimeaenderung: nein

Formaler Forschungslauf: nein

## Anlass

W5-A bis W5-D haben keine externe Naturrolle gefunden, die das harte alte
Wiedereroeffnungstor vollstaendig und nichtreduzierbar erfuellt. Daraus wurde
zu streng abgeleitet, dass ein technisch konstruierter Kandidat nur bei
Nachweis einer neuen Naturphysik untersucht werden duerfe.

Fuer ein digitales kuenstliches System ist diese Forderung nicht notwendig.
Jede Feldgleichung ist eine gesetzte Modellannahme. Wissenschaftlich
entscheidend ist, dass die Annahme transparent, lokal, homogen, begrenzt und
falsifizierbar ist und dass das gewuenschte Ergebnis nicht in ihr kodiert
wird.

## Korrigierte Grundposition

Das Projekt darf eine minimale langsame MCM-Feldkomponente konstruieren und
gegen einfachere Baselines pruefen. Eine Gleichwertigkeit zu adaptivem
Material, Hysterese oder einer langsamen Spur bedeutet dann:

- kein Claim einer neuen irreduziblen Naturklasse;
- keine Umbenennung des Mechanismus in organisches Memory;
- aber kein automatisches Verbot seiner technischen Untersuchung.

Baselinevergleiche bestimmen die Reichweite einer Aussage. Sie entscheiden
nicht mehr allein darueber, ob ein einfacher, offen deklarierter
Entwicklungsprototyp gebaut werden darf.

## Verbindliche Bezeichnung

Der technische Arbeitsbegriff lautet:

> **langsame entwicklungsfaehige MCM-Feldkomponente**

`MCM-Entwicklungssubstrat` darf als kurze Architekturbezeichnung verwendet
werden. `Feldintern` ist nur zulaessig, wenn die Komponente:

1. an denselben lokalen MCM-Orten wie die schnelle Feldkomponente liegt;
2. in derselben atomaren Feldtransition kausal gelesen und fortgeschrieben
   wird;
3. ohne Observer, Datenbank, Episodenabschluss oder externen Leser besteht;
4. Teil desselben Snapshots und derselben fortlaufenden Feldinstanz ist;
5. auf spaetere schnelle Feldentwicklung lokal zurueckwirkt.

Eine getrennte Runtime, nachgeschaltete Memoryschicht oder externe
Speicherstruktur erfuellt diese Bezeichnung nicht.

## Zielarchitektur

```text
kontrollierter Weltkontakt
-> schnelle lokale MCM-Feldkomponente S
<-> langsame lokale MCM-Feldkomponente L
-> spaetere gemeinsame Feldentwicklung
```

Der vorhandene schnelle Nachhall H bleibt eine eigene passive Referenz und
wird nicht in L umbenannt.

```text
S = schnelle aktuelle Feldwirkung
H = schneller passiver Nachhall
L = noch unbestimmte langsame entwicklungsfaehige Feldkomponente
```

S, H und L gehoeren zu einem gemeinsamen MCM-Feld. Sie sind keine drei
Organismen und keine drei Bedeutungsstufen.

## Homogene Grundmechanik und ergebnisoffene Entwicklung

Die lokale Grundregel darf konstruiert werden. Sie muss jedoch an allen
gleichartigen Orten dieselbe sein. Vorgegeben werden duerfen nur:

- lokale Kausalitaet und endlicher Wechselwirkungsradius;
- atomare Berechnung aus demselben abgeschlossenen Vorzustand;
- Werte-, Fluss- oder Ressourcenbegrenzung;
- Kopplungsrichtung zwischen S und L;
- numerische Stabilitaet und ein exakter Nullpfad;
- gemeinsame technische Organismuszeit und Snapshotfaehigkeit.

Nicht vorgegeben werden duerfen:

- das entstehende raeumliche oder zeitliche Muster;
- wichtige Orte, Gewinner, Cluster oder Objektidentitaeten;
- Zielgestalt, Zieltopologie, Bedeutung oder semantische Klasse;
- Schreib-, Lese-, Loesch- oder Trainingsphasen;
- gewuenschte Reaktion auf eine bestimmte Testwelt;
- Memory, innerer Dialog, Selbstwahrnehmung oder KI als Runtimeziel.

## Praezisierung von Emergenz und Topologie

Emergenz bezeichnet in diesem Projekt keine unerkaerliche oder
nichtdeterministische Wirkung. Zulaessig ist:

> Aus einer homogenen lokalen deterministischen Grundmechanik und konkreter
> Welt- und Feldgeschichte entsteht eine nicht als Endform programmierte
> raeumlich-zeitliche Differenzierung.

Drei Begriffe werden getrennt:

1. **Traegertopologie:** technisch feste Nachbarschaft und Geometrie der
   MCM-Orte.
2. **Feldform:** momentane oder wiederkehrende Werteverteilung auf dieser
   Topologie.
3. **Entwickelte Kopplungstopologie:** geschichtlich veraenderte wirksame
   Kopplungsstruktur. Dieser Begriff ist erst nach eigenem Kausalnachweis
   zulaessig.

MINI_DIO zeigte reproduzierbare Feldformen auf einer stark vorstrukturierten
gerichteten Traegertopologie. Das ist eine wichtige Musterbildungsbaseline,
aber kein Nachweis einer gewachsenen Kopplungstopologie.

## Entwicklungsziel der ersten Stufe

Die erste Stufe soll noch kein Memory erzeugen. Sie soll nur pruefbar machen,
ob eine langsame lokale MCM-Komponente technisch folgende Grundrollen tragen
kann:

1. lokale Veraenderung durch normale schnelle Feldteilnahme;
2. langsamere Fortwirkung als S und H;
3. lokale Rueckwirkung auf spaetere S-Entwicklung;
4. Begrenzung ohne unbegrenzte Akkumulation;
5. Veraenderbarkeit durch weitere normale Feldgeschichte;
6. exakte Deaktivierbarkeit zur heutigen Runtime.

Erst nach einem technischen Nachweis dieser sechs Rollen darf ein separater
Lebenszyklus untersuchen, ob alte Wirkung funktionslos und dieselbe Faehigkeit
anders nutzbar werden kann.

## Mindestbaselines

Der erste Kandidat wird mindestens verglichen mit:

- heutiger S/H-Runtime ohne L;
- einer lokalen Leaky-Spur;
- einer langsamen identischen Feldkopie;
- einem Produktintegrator mit festem Leser;
- adaptivem lokalem Gain oder Mobilitaetszustand;
- unabhaengiger glatter Hysterese.

Ein gleichwertiger Baselinebefund stoppt nur weitergehende Aussagen. Er darf
den Kandidaten als transparenten technischen Referenzprototyp bestehen lassen.

## Verhaeltnis zu W5-A bis W5-D und S1-AB

Die Quellen- und Kandidatenaudits bleiben gueltig:

- Es wurde keine neue Naturklasse gefunden.
- Das endliche umverteilbare Medium ist als adaptive Mobilitaets- oder
  Standardmaterialform erklaerbar.
- Externe Quellen belegen noch kein MCM-Entwicklungssubstrat.

W5-E aendert nur die Entwicklungsentscheidung: Diese Negativbefunde verbieten
nicht laenger einen offen konstruierten Minimalprototyp. Sie begrenzen dessen
Bezeichnung und spaetere Claims.

## Freigabe und Sperre

```text
homogener Zweizeiten-Architekturweg:       freigegeben
funktionaler Vertrag fuer L:               freigegeben
konkrete L-Gleichung:                      noch nicht ausgewaehlt
Runtimeimplementierung:                    noch nicht freigegeben
technischer Referenzprototyp:              nach Vertrag zulaessig
Memory-, Emergenz- oder Topologieclaim:    gesperrt
```

Die ausdrueckliche Benutzerentscheidung zur Weiterentwicklung liegt vor.
Vor Code bleibt genau ein funktionaler Vertrag erforderlich, der Ursache,
Rueckwirkung, Begrenzung, Nullpfad und staerkste Baseline bindet.

## Aussagegrenze

W5-E belegt keine entwickelte Feldform, Kopplungstopologie, Praegung,
Feldzeit, Memory, innere Wahrnehmung, Organisation, Semantik,
Selbstregulation oder KI. Er oeffnet einen technisch realistischen und
falsifizierbaren Entwicklungsweg. Lauf 197 bleibt reserviert und unberuehrt.

## Bester naechster Schritt

W6-A erstellt den minimalen Funktionsvertrag fuer L. Er legt noch keine
Formel fest, sondern bindet pro lokalem Ort Eingangsursache, Zustandsgrenze,
S-zu-L- und L-zu-S-Richtung, Ressourcen- oder Saettigungsgrenze, Nullpfad,
Snapshotrolle und staerkste Baseline. Danach darf genau eine minimale
Gleichungsfamilie fuer einen opt-in Referenzprototyp ausgewaehlt werden.
