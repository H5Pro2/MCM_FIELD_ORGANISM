# S1-VH: PPB-1 statischer Engineering-, Funktions-, Sicherheits- und Integrationsvertrag

> **Fortschreibung:** S1-VI bindet private Schemata, Distanz, Lebenszyklus und
> eine synthetische 30-Pfade-Matrix. Implementierung und Feldintegration
> bleiben weiterhin aus.

## Ausdrueckliche Richtungsentscheidung

S1-VG ist fachlich abgenommen. `MPZ-1` bleibt als eigenstaendiger
Forschungskandidat terminal geschlossen. Es wird kein weiterer kuenstlicher
Substratkandidat geoeffnet.

Die technische Entwicklung wird stattdessen in genau einer transparenten
Engineeringrichtung fortgesetzt:

```text
PPB-1 - MCM-kompatible perzeptive Prototypbank fuer getrennte
        auditive und visuelle Wahrnehmungszustaende
```

`PPB-1` ist eine bewusst programmierte Speicherkomponente. Sie ist keine
endogene Feldursache, kein neuer Kandidatenbefund und kein Nachweis einer
vorhandenen Memory-Funktion des MCM-Feldes.

## Auftrag und Grenze

S1-VH legt den statischen Engineeringvertrag vor jeder Mathematik und
Implementierung fest. Der Vertrag definiert Funktionsumfang,
Komponentengrenzen, Sicherheitsregeln, Baselines, Abnahmekriterien und
Stoppbedingungen.

Noch nicht freigegeben sind:

- Gleichung, Distanzmetrik, Parameter oder Kapazitaetswert;
- Implementierung, Fixture, Test oder Lauf;
- Einbindung in `current_api` oder Root-Lazy-Exports;
- Aenderung von `SharedMCMField`, Feldsnapshot oder Restore;
- direkter Schreibzugriff auf den aktiven Feldkern;
- reale Audio- oder Videoausfuehrung;
- Semantik, Woerter, Objektklassen oder externe Inhaltslabels;
- Aussagen zu Bewusstsein, Gefuehl oder organischer Memory;
- Gleichsetzung von PPB-1 mit einer endogenen MCM-Feldursache.

## Technischer Zweck

PPB-1 soll wiederholte bereits reduzierte auditive oder visuelle
Rezeptorzustaende in einem endlichen technischen Bestand zeitlich verdichten.
Bei einem spaeteren aehnlichen Rezeptorzustand soll die Bank einen
nachvollziehbaren technischen Wahrnehmungszustand ausgeben koennen, ohne eine
vollstaendige Roh- oder Rezeptorhistorie zu archivieren.

Der Engineeringnutzen besteht aus:

- begrenztem Speicherbedarf;
- nachvollziehbarer Aehnlichkeitszuordnung;
- kontrollierter Aktualisierung und Stabilisierung;
- explizitem Vergessen und Kapazitaetskonflikt;
- reproduzierbarem technischen Readout;
- klarer Trennung vom MCM-Feldkern.

Diese Funktionen werden programmiert. Sie werden nicht als spontan aus der
Feldphysik entstanden beschrieben.

## Komponentengrenze

Der zulaessige Datenfluss ist statisch wie folgt gebunden:

```text
reduzierter auditiver Rezeptorzustand -> private auditive Prototypbank
                                     -> privater auditiver Readout

reduzierter visueller Rezeptorzustand -> private visuelle Prototypbank
                                      -> privater visueller Readout

modalitaetseigener Readout -> spaeterer opt-in Rueckgabeadapter -> MCM-Pfad
```

S1-VH gibt den Rueckgabeadapter noch nicht frei. PPB-1 darf den Feldkern nicht
importieren, mutieren oder umgehen. Der aktive Rezeptor-/Feldpfad muss bei
PPB-OFF unveraendert und bitgleich fortsetzbar bleiben.

Die Bank ist ein Sidecar zum Wahrnehmungspfad. Sie ist weder Teil eines
Rezeptors noch Teil von S oder H und wird nicht im bestehenden Feldsnapshot
gespeichert.

## Getrennte Modalitaetsbanken

Die erste PPB-1-Stufe besitzt genau zwei unabhaengige Banken:

### Auditive Bank

Sie akzeptiert ausschliesslich vollstaendige reduzierte auditive
Rezeptorzustaende mit der gebundenen auditiven Geometrie. Visuelle Werte oder
gemeinsame Audio-Video-Paarcodes sind unzulaessig.

### Visuelle Bank

Sie akzeptiert ausschliesslich vollstaendige reduzierte visuelle
Rezeptorzustaende mit der gebundenen visuellen Geometrie. Auditive Werte oder
gemeinsame Audio-Video-Paarcodes sind unzulaessig.

Kapazitaet, Zuordnung, Aktualisierung, Stabilisierung und Vergessen werden pro
Bank getrennt bilanziert. Eine modalitaetsuebergreifende Verknuepfung ist
nicht Bestandteil von PPB-1.

Ein spaeterer Bankschritt darf genau einen abgeschlossenen Rezeptorzustand
genau einer Modalitaet verarbeiten und erzeugt genau einen modalitaetseigenen
Readout. Eine gemeinsame Transporthuelle duerfte beide Readouttypen nur
unveraendert sammeln; sie duerfte sie weder fusionieren noch zeitlich paaren.

## Zulaessiger Eingangsvertrag

PPB-1 darf nur Rollen aus einem abgeschlossenen `ReceptorContactFrame`
verwenden, die fuer die technische Verarbeitung notwendig sind:

- Modalitaet zur Wahl der fest zugeordneten Bank;
- Rezeptorgeometrie zur Dimensionspruefung;
- geordnete Traegerkennungen zur eindeutigen Werteposition;
- bereits normalisierte reduzierte Rezeptorwerte;
- kausale Feldzeit nur fuer Reihenfolge und Altersfortschreibung.

Nicht als Prototypinhalt gespeichert werden duerfen:

- Audio-Samples oder Bildframes;
- Dateinamen, Geraete- oder Quellenkennungen;
- Snapshot-ID des Eingangs;
- Wort-, Objekt-, Klassen- oder Bedeutungslabel;
- Ergebnisarm, erwarteter Match oder Comparatorentscheidung;
- eine Liste frueherer Eingaben oder Replayzeiger.

## Verdichtete Zustandsrepraesentation

Ein Prototyp ist eine feste technische Zusammenfassung mehrerer zugeordneter
reduzierter Rezeptorzustaende derselben Modalitaet. Verdichtung bedeutet hier
primaer zeitliche Zusammenfassung: Die Bank bewahrt keinen Record pro
Exposition auf.

Jeder Prototyp darf spaeter nur einen vorab gebundenen festen Satz technischer
Rollen besitzen, mindestens:

- Bank- und Slotidentitaet;
- feste Rezeptorgeometrie;
- fest dimensionierte verdichtete Werte;
- begrenzter Stabilisierungsstand;
- Alters- oder Nutzungsstand fuer explizites Vergessen;
- belegter oder freier Slotstatus.

Die konkrete Darstellung wird erst im Folgeauftrag gebunden. S1-VH behauptet
nicht, dass ein Prototyp anonym, nicht invertierbar oder semantisch neutral
ist, nur weil er keine Rohdatenfolge speichert. Ein spaeterer Sicherheitscheck
muss Rekonstruktions- und Datenabflussrisiken gesondert pruefen.

## Aehnlichkeitszuordnung und Bildung

Fuer jeden zulaessigen Eingang muss PPB-1 spaeter deterministisch genau einen
der folgenden Ausgaenge erzeugen:

- Zuordnung zu genau einem vorhandenen Prototyp;
- Bildung in genau einem freien Slot;
- kontrollierter Kapazitaetskonflikt ohne Zustandsaenderung;
- kontrollierte Ersetzung nach einer vorab gebundenen Regel;
- fail-closed Ablehnung eines ungueltigen Eingangs.

Mehrdeutige Gleichstaende muessen durch eine feste technische Regel aufgeloest
werden. Iterationsreihenfolge, Hashreihenfolge oder zufaellige Auswahl duerfen
das Ergebnis nicht unbeabsichtigt bestimmen.

Die Aehnlichkeitsmetrik, Bildungsschwelle und Gleichstandsregel werden in
S1-VH noch nicht festgelegt. Sie muessen vor einer Implementierung fuer Audio
und Video getrennt begruendet werden.

## Aktualisierung und Stabilisierung

Ein zugeordneter Eingang darf nur den ausgewaehlten Prototyp derselben Bank
aktualisieren. Eine Aktualisierung muss:

- fest dimensioniert bleiben;
- den Wertebereich des Eingangsvertrags einhalten;
- deterministisch sein;
- den frueheren Prototyp nicht als versteckte Historie anhaengen;
- einen begrenzten Stabilisierungsstand fortschreiben;
- alle anderen Slots unveraendert lassen, sofern kein Kapazitaetskonflikt
  vorliegt.

Stabilisierung bezeichnet ausschliesslich einen technischen Zustand der Bank.
Sie ist kein Lern- oder Feldbefund. Ein spaeterer Vertrag muss festlegen, wie
Wiederholung, Streuung und Alter den Stabilisierungsstand beeinflussen.

## Vergessen und Kapazitaetskonflikt

Jede Bank besitzt eine feste endliche Slotkapazitaet. Sie darf waehrend einer
Ausfuehrung nicht still wachsen.

Ist kein passender Prototyp und kein freier Slot vorhanden, muss genau eine
vorab registrierte Konfliktpolitik greifen:

- Eingang ablehnen und Zustand unveraendert lassen; oder
- einen eindeutig bestimmten Prototyp kontrolliert ersetzen.

Vergessen muss explizit, messbar und reproduzierbar sein. Zulaessige
Engineeringrollen koennen Alter, ausbleibende Nutzung, geringe Stabilisierung
oder kontrollierte Konkurrenz sein. S1-VH waehlt noch keine Regel.

Unzulaessig sind stilles Loeschen, unbegrenzte Verkleinerung, globaler Reset,
armabhaengige Ersetzung und eine nach Ergebniskenntnis geaenderte Politik.

Ein freigegebener Slot muss vollstaendig leer, ohne alten Readoutrest und fuer
einen neuen Prototyp wiederverwendbar sein.

## Privater technischer Wahrnehmungszustand

Der PPB-1-Readout darf nur technische Rollen enthalten:

- Modalitaet und Bankidentitaet;
- gueltiger Treffer, Neuanlage, Konflikt oder Ablehnung;
- ausgewaehlte Slotidentitaet;
- gebundener Aehnlichkeits- oder Distanzwert;
- begrenzter Stabilisierungsstand;
- verdichtete Prototypwerte nur soweit fuer einen spaeteren Adapter noetig;
- kanonischer Digest fuer Reproduzierbarkeit.

Der Readout ist keine Klassifikation und keine semantische Aussage. Er darf
keine Woerter, Objektidentitaeten oder interpretierte Bedeutung enthalten.

## Spaetere Rueckgabe an den MCM-Pfad

Eine spaetere Rueckgabe darf nur ueber einen separaten, explizit aktivierten
Adapter erfolgen. Der Adapter muss:

- PPB-1 als externe Engineeringquelle offen deklarieren;
- die Bank vom Feldkern getrennt halten;
- einen begrenzten technischen Kontakt erzeugen;
- aktuelle Rezeptoreingabe und Prototypreadout getrennt messbar lassen;
- Kandidat-OFF beziehungsweise PPB-OFF bitgleich erhalten;
- eine Rueckkopplungsschleife mit erneuter Bankaufnahme verhindern oder
  ausdruecklich bilanzieren;
- keine oeffentliche API oder Snapshotrolle ohne eigene Freigabe einfuehren.

S1-VH definiert weder Adapteranatomie noch Feldwirkung. Die Rueckgabe bleibt
nur eine spaetere Integrationsanforderung.

## Trennung von spaeterer Semantik

PPB-1 endet beim technischen Prototypreadout. Eine spaetere semantische
Schicht waere ein separates Projektmodul mit eigener Freigabe und duerfte
PPB-1 nur ueber eine dokumentierte Einweggrenze lesen.

Semantische Labels duerfen nicht in Prototypbildung, Aehnlichkeitsmetrik,
Kapazitaet, Vergessen oder Feldrueckgabe zurueckwirken. S1-VH gibt keine solche
Schicht frei.

## Engineeringbaselines

PPB-1 wird nicht auf eine neue Naturursache geprueft. Die Baselines pruefen
stattdessen Nutzen, Transparenz, Begrenzung und Nichtduplizierung.

| Baseline | Engineeringvergleich |
|---|---|
| Rohdaten- oder Rezeptor-Replay | Speicherbedarf, Datenschutzgrenze und spaeterer Readout ohne vollstaendige Historie |
| gleitender Mittelwert oder einfache gleitende Statistik | Nutzen mehrerer begrenzter Prototypen gegen eine einzige verdichtete Spur |
| schneller Nachhall H | Wirkung ueber die kurze passive Feldspur hinaus, ohne H umzubenennen |
| Leaky oder Integrator | Zuordnung und Kapazitaetskonflikt gegen einen einzelnen fortgeschriebenen Wert |
| einfacher externer Key-Value-Speicher | Nutzen der aehnlichkeitsbasierten Zuordnung ohne vorgegebenen Schluessel oder Inhaltslabel |
| feste Prototypliste ohne Aktualisierung | Nutzen kontrollierter Aktualisierung, Stabilisierung und Vergessen |

Erreicht eine einfachere Baseline denselben Funktionsumfang unter gleichem
Speicher-, Zeit- und Schnittstellenbudget, wird die einfachere Engineeringform
bevorzugt. Dies ist kein Forschungsstopp, sondern eine
Komplexitaetsentscheidung.

## Sicherheits- und Fail-Closed-Regeln

Eine spaetere PPB-1-Implementierung muss fail-closed reagieren bei:

- falscher Modalitaet oder unbekannter Rezeptorgeometrie;
- nicht endlichen oder ausserhalb des Vertrags liegenden Werten;
- Dimensions- oder Traegerreihenfolgenkonflikt;
- unvollstaendigem Prototypzustand;
- mehrfach belegtem oder negativem Slotbestand;
- uneindeutiger Zuordnung ohne gebundene Gleichstandsregel;
- Kapazitaetsueberschreitung;
- unerlaubtem Rohdaten-, Label- oder Replayinhalt;
- direktem Feld-, Snapshot- oder Public-API-Zugriff;
- nicht deterministischem Ergebnis bei identischem Vorzustand und Eingang.

Ein Fehler darf weder einen Teilzustand committen noch den aktiven Feldkern
veraendern.

## Abnahmekriterien vor Integration

Eine private Referenzimplementierung waere erst zulaessig, wenn ein weiterer
statischer Vertrag mindestens bindet:

1. kanonisches Schema fuer Bank, Slot, Prototyp und Readout;
2. getrennte Audio- und Video-Dimensionen;
3. Aehnlichkeitsmetrik und Gleichstandsregel;
4. Bildung, Aktualisierung und Stabilisierungsgrenzen;
5. Vergessens- und Konfliktpolitik;
6. feste Kapazitaets- und Wertebereichsgrenzen;
7. atomaren Einzelschritt und unveraenderten Fehlerpfad;
8. Vergleichsmatrix gegen alle Engineeringbaselines;
9. PPB-OFF-Regression und Importgrenzen;
10. expliziten Ausschluss von Feldintegration und Snapshotumbau.

## Stopp- und Vereinfachungsbedingungen

Die PPB-1-Engineeringentwicklung wird gestoppt oder vereinfacht, wenn:

- keine verdichtete Darstellung ohne Rohhistorie definierbar ist;
- auditive und visuelle Geometrien nicht sauber getrennt validierbar sind;
- Zuordnung oder Konfliktpolitik nicht deterministisch gebunden werden kann;
- der Zustand bei Fehlern nur teilweise fortgeschrieben werden kann;
- ein einfacher gleitender Zustand denselben gebundenen Nutzen erbringt;
- eine Rueckgabe den Feldkern, dessen Snapshot oder oeffentliche API
  voraussetzen wuerde;
- Semantik oder externe Labels fuer die technische Funktion notwendig werden;
- Speicher- und Laufzeitgrenzen nicht vorab endlich festgelegt werden koennen.

Ein vereinfachtes Ergebnis bleibt als Engineeringbaseline einordenbar. Es
darf nicht nachtraeglich als Forschungskandidat bezeichnet werden.

## Verbindlicher Vertragsstand

```text
S1_VH_S1VG_ACCEPTED_MPZ1_RESEARCH_CLOSED
S1_VH_PPB1_ENGINEERING_DIRECTION_OPENED
S1_VH_SEPARATE_AUDITORY_AND_VISUAL_BANKS_REQUIRED
S1_VH_REDUCED_RECEPTOR_STATE_INPUT_ONLY
S1_VH_NO_RAW_HISTORY_NO_REPLAY_STORAGE
S1_VH_BOUNDED_CAPACITY_AND_EXPLICIT_CONFLICT_REQUIRED
S1_VH_DETERMINISTIC_ASSIGN_UPDATE_STABILIZE_FORGET_REQUIRED
S1_VH_PRIVATE_TECHNICAL_READOUT_ONLY
S1_VH_FIELD_CORE_AND_SEMANTIC_LAYER_SEPARATE
S1_VH_ENGINEERING_BASELINE_REDUCTION_ACCEPTED
S1_VH_NO_ENDOGENOUS_FIELD_CAUSE_OR_MEMORY_FINDING
S1_VH_NO_EQUATION_NO_PARAMETER_NO_IMPLEMENTATION_NO_TEST_NO_RUN
```

## Genau ein naechster Schritt

Der einzige zulaessige Anschluss ist:

```text
S1-VI - statischer PPB-1-Daten-, Distanz-, Lebenszyklus- und
        Testmatrixvertrag
```

S1-VI darf konkrete private Schemarollen, genau eine nachvollziehbare
Distanzfamilie, deterministische Zuordnung, Slotlebenszyklus, Konfliktpolitik
und synthetische Vertragstestfaelle binden. Es darf noch keine
Implementierung, Testausfuehrung, Feldintegration, oeffentliche API,
Snapshotaenderung oder reale Audio-/Videoausfuehrung enthalten.

## Projektgrundlagen

- [S1-VG terminaler MPZ-1-Baselineaudit](S1VG_MPZ1_STATISCHER_UEBERGANGSQUELLEN_UND_BASELINE_NICHTDUPLIZIERUNGSAUDIT.md)
- [S1-VF MPZ-1-Anatomieaudit](S1VF_MPZ1_STATISCHER_ANATOMIE_URSACHEN_UND_BILANZVOLLSTAENDIGKEITSAUDIT.md)
- [Aktiver Rezeptorvertrag](../mcm_field_organism/receptor_contract.py)
- [Aktiver Rezeptorenverteiler](../mcm_field_organism/receptor_distributor.py)
- [Aktiver Audio-Video-Feldpfad](../mcm_field_organism/audio_video_neutral_field_runtime.py)
- [Aktivkern-Konsolidierungsabschluss](S1UZ_STATISCHER_ABSCHLUSSAUDIT_AKTIVKERN_KONSOLIDIERUNG.md)
