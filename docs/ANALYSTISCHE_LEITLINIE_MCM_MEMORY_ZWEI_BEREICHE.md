# Analystische Leitlinie: MCM-Memory als Zwei-Bereich-Architektur

Stand: 2026-08-30

Status: `ANALYSTISCHE_ORIENTIERUNG_KEIN_NEUER_FORSCHUNGSBEFUND`

## Zweck

Dieses Dokument bindet die fachliche Orientierung fuer die weitere Analyse
und Forschungslenkung. Es ersetzt keine bestehenden Vertraege, Befunde oder
Abnahmen. Insbesondere darf die hier beschriebene Zielarchitektur nicht
rueckwirkend als bereits implementiert oder bestaetigt ausgegeben werden.

## Zielvorhaben

Das Projekt entwickelt einen technischen MCM-Wahrnehmungskern und daran
anschliessbare, endliche perzeptive Memory-Bausteine. Gespeichert werden keine
unbegrenzten Rohmedien und zunaechst keine semantischen Begriffe. Erhalten und
wiederverwendet werden reduzierte auditive und visuelle Wahrnehmungszustaende,
ihre kurze Ordnung sowie durch Wiederholung stabilisierte Prototypen.

Das unmittelbare Entwicklungsziel ist ein kontrolliert nutzbarer innerer
perzeptiver Kontext. Eine Rueckwirkung auf das MCM-Feld ist eine spaetere,
separat zu pruefende Option und kein Bestandteil des gegenwaertigen Ziels.

## Bestaetigter Ist-Zustand

1. Das MCM-Feld ist der primaere dynamische Wahrnehmungskern. Es besitzt einen
   technischen Gegenwartszustand, Feldzeit und lokale Dynamik, ist aber nicht
   als langfristiges Memory-Medium bestaetigt.
2. S2-FZ bestaetigt fuer eine begrenzte synthetische Geschichte den atomaren
   B4-/TSPM-1-Verbund: kurze Folge in B4, voruebergehende Fast-Spur,
   Wiederholungsstabilisierung in TSPM-Slow und kontrolliertes Nichtabrufen
   einer zu schwach stabilisierten Spur.
3. Die aktuell implementierten read-only Rollen lauten `B4_RECENT`,
   `TSPM_FAST` und `TSPM_SLOW`. Es gibt keine automatische Gesamtauswahl.
4. S2-GC qualifiziert die unveraenderliche `PerceptualContextBundle`-
   Projektion technisch mit `12/12`. Eine funktionale Kontextverwendung ist
   dadurch noch nicht bestaetigt.
5. Koordinator, Ledger, Receipt und Bundle sind Kontroll- oder
   Schnittstellenrollen. Sie sind keine weiteren Memory-Bereiche.

## Fachliches Zielbild

Die langfristig anzustrebende Produkt- und Forschungsdarstellung besitzt zwei
endliche Memory-Bereiche:

```text
kontrollierter Weltkontakt
-> Rezeptoren und Docks
-> gegenwaertiges MCM-Wahrnehmungsfeld
-> quellgebundenes reduziertes perzeptives Ereignis
-> Bereich A: nah, geordnet, kurzlebig
-> atomar gebundener Verdichtungsuebergang A -> B
-> Bereich B: stabiler, inhaltsbezogen, ungeordnet
-> read-only Kontextdarstellung A_RECENT | B_STABLE
```

### Bereich A: naher perzeptiver Bereich

Bereich A soll juengste Inhalte, Bildungsordnung, kurze Folgen und eine
kurzlebige Spur tragen. B4 und die heutige TSPM-Fast-Dynamik koennen darin
zunaechst als getrennte interne Mechanismen fortbestehen. `Fast` soll jedoch
langfristig keine dritte oeffentliche Memory-Ebene darstellen.

Eine spaetere physische Zusammenlegung von B4 und Fast ist keine reine
Umbenennung. Sie ist nur zulaessig, wenn Funktionsgleichheit, Ressourcenbilanz,
Verdrangung, Ablauf, Reihenfolge und Fail-Closed-Verhalten separat belegt sind.

### Bereich B: stabilisierter perzeptiver Bereich

Bereich B soll wiederholungsstabilisierte auditive und visuelle
Wahrnehmungsprototypen tragen. Er besitzt keine Reihenfolgekoordinate und
keine allgemeine episodische Historie. Er darf weder Semantik noch
Objektidentitaet vortaeuschen.

In der Zielarchitektur wird Bereich B nur durch einen vollstaendig
quellgebundenen Verdichtungskandidaten aus Bereich A veraendert. Direkter
ungepruefter Rezeptorzugriff, synthetisches Replay oder ein paralleler
unabhaengiger Schreibweg sind ausgeschlossen.

## Atomare Grenze

Die Atomaritaet gilt fuer den gemeinsamen Memory-Schritt, nicht rueckwirkend
fuer die bereits entstandene Feldwahrnehmung.

- Ein gueltiger Memory-Schritt endet mit konsistentem A-/B-Nachzustand oder
  ohne sichtbaren A-/B-Teilcommit.
- Ein Memoryfehler loescht oder widerruft keinen bereits erzeugten
  MCM-Feldzustand.
- Normaler Kapazitaetsdruck ist durch vorab definierte lokale Verdrangung zu
  behandeln und darf die Weltaufnahme nicht blockieren.
- Fehlerhafte Herkunft, unvollstaendige Belege oder widerspruechliche
  Zustaende stoppen den Memory-Schritt fail-closed.
- Bereich B schreibt nicht in Bereich A zurueck. Eine spaetere Wirkung auf
  Wahrnehmung waere ein eigener Kontext- oder Feldkopplungsvertrag.

## Zwei Bereiche sind keine nachtraegliche Behauptung

Der aktuelle Code und die bestaetigten Befunde arbeiten weiterhin mit den
drei getrennten Sichtrollen `B4_RECENT`, `TSPM_FAST` und `TSPM_SLOW`. Die
Zwei-Bereich-Darstellung ist deshalb vorerst eine Zielarchitektur.

Bestehende Dokumente, Tests und Befunde werden nicht still umbenannt oder
umgedeutet. Eine Umstellung benoetigt mindestens:

1. eine exakte Abbildung von B4 und Fast auf Bereich A;
2. eine exakte Abbildung von Slow auf Bereich B;
3. einen materialisierten A-nach-B-Uebergang mit Quellen- und
   Ressourcenbindung;
4. eine Gegenpruefung gegen den bestehenden Drei-Rollen-Verbund;
5. die unveraenderte Reproduktion aller S2-FZ-Funktionen;
6. eine Begruendung, welche Komplexitaet tatsaechlich entfaellt.

## Verbindliche methodische Regeln

1. Kein Claim, Memory entstehe im MCM-Feld. Kurzlebige Felddynamik bleibt
   Wahrnehmungszustand, solange keine eigene Memory-Funktion belegt ist.
2. Kein `BEST_MEMORY`, Winner-take-all oder verdecktes Ranking.
3. Keine Folgenordnung in Bereich B beziehungsweise TSPM-Slow.
4. Keine automatische Verschmelzung von naher Spur und stabilem Prototyp.
5. Keine neue Speicherebene ohne eigene notwendige Funktion, Bilanz und
   Falsifikationsprognose.
6. Keine biologischen Gleichsetzungen. Begriffe wie Hippocampus oder
   Complementary Learning Systems duerfen hoechstens als lose Inspiration,
   nicht als Projektbefund verwendet werden.
7. Keine Semantik-, Bewusstseins-, Gefuehls- oder Bedeutungsbehauptung.
8. Keine Rohbild-, Rohvideo-, Roh-Audio-, Label-, Reward- oder unbegrenzte
   Replayablage im Memory-Pfad.
9. Gleichwertigkeit mit bekannten Speicherverfahren ist kein Scheitern. Sie
   wird als Engineeringbefund ausgewiesen und begrenzt nur den Neuheitsclaim.
10. Messung, Interpretation, Zielarchitektur und Hypothese bleiben in jeder
    Rueckmeldung getrennt.

## Brauchbare externe Anregungen

Folgende Anregungen werden als methodisch brauchbar festgehalten:

- Memory-Funktion und Feldwahrnehmung klar trennen;
- zwei oeffentliche Memory-Bereiche statt drei Produktflaechen anstreben;
- Fast als moegliche interne Dynamik von Bereich A behandeln;
- Repraesentationsqualitaet und Abrufadressierung vor einem weiteren
  Speicherkern verbessern;
- partielle und einmodale Hinweise spaeter gegen einfache assoziative
  Baselines pruefen;
- Interferenz, endliche Kapazitaet, funktionales Vergessen und
  Wiederverwendung dauerhaft als Pflichtpruefungen behalten.

Nicht als unmittelbare Richtung uebernommen werden synthetisches Replay,
biologische Gleichsetzungen, eine sofortige Feldrueckwirkung oder die
physische Entfernung der funktionierenden Fast-Mechanik ohne
Gleichwertigkeitsnachweis.

## Naechste methodische Reihenfolge

1. Den bestaetigten S2-FZ- und S2-GC-Stand unveraendert erhalten.
2. Vor jeder Codeumstellung einen statischen Zwei-Bereich-Migrations- und
   Falsifikationsvertrag erstellen.
3. Zuerst eine reine A-/B-Projektion aus dem bestehenden Verbund pruefen.
   Dadurch wird die gewuenschte Produktgrenze getestet, ohne funktionierende
   Speichermechanik vorschnell zu entfernen.
4. Nur bei verlustfreier Abbildung eine interne Zusammenlegung von B4 und
   Fast untersuchen.
5. Danach eine einzelne Kontextverwendungsfunktion gegen
   `CURRENT_PERCEPTION_ONLY`, korrekten Kontext, fremden Kontext und eine
   einfache direkte Kontextbaseline pruefen.
6. Erst anschliessend reichere Wahrnehmungsrepraesentationen, partielle Cues
   und modalitaetsuebergreifende Adressierung erweitern.
7. Feldrueckwirkung, Replay und automatische Kontextwahl bleiben eigene,
   spaetere Richtungsentscheidungen.

## Analystische Entscheidungsregel

Kuenftige Forscherantworten werden daran gemessen, ob sie:

- das Zwei-Bereich-Ziel unterstuetzen, ohne den bestaetigten Ist-Zustand zu
  verfalschen;
- den inneren perzeptiven Kontext schrittweise funktionsfaehig machen;
- keine unnoetige dritte Memory-Ebene oder neue Feldphysik erzwingen;
- eine einfachere Engineeringerklaerung als gueltiges Ergebnis akzeptieren;
- und den naechsten Schritt klein, messbar, ressourcenbegrenzt und
  falsifizierbar halten.
