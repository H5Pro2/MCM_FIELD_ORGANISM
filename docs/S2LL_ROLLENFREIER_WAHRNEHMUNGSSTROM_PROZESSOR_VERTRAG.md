# S2-LL - Rollenfreier Wahrnehmungsstrom-Prozessor

## Status und Zweck

`S2LL_STATIC_FUNCTION_AND_FALSIFICATION_CONTRACT_COMPLETE`

S2-LL bindet einen privaten, endlichen und online auswertbaren
Wahrnehmungsstrom:

```text
kanonische zeitgeordnete RGB-/PCM-Quelle
-> unveraenderte Rezeptoren
-> strukturelle Ereignisklassifikation
-> Feldkontakt
-> genau eine atomare Memoryformation oder genau ein read-only Teilhinweisabruf
-> getrennte A_RECENT-/B_STABLE-Hypothese oder Enthaltung
```

Der Vertrag implementiert und startet nichts. Er fuehrt keine neue
Rezeptorfunktion, Lernregel, Memoryschicht, Kandidatenrangfolge oder
Feldrueckwirkung ein. Er verallgemeinert ausschliesslich die bereits
qualifizierten Einzelpfade zu einer rollenfreien Ablaufgrenze.

Ausgangscommit ist `95104bbe6a6a2c17e6cb1894538239624f4f9c63`.

## Gebundene technische Quellen

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| kanonische AV-Grenze | `tools/_s2jo_private_canonical_av_boundary.py` | `50a39fb3865fbd11b3577f79db2983f9dd3260262dee0f199ae5f884bed4ef71` |
| zeitgeordneter Feldpfad | `tools/_s2jt_private_timed_field_projection.py` | `91604184325192b6a6291785f713c44fc8fac1d7614234279f635032160c4a4e` |
| atomare Zwei-Bereich-Memory | `tools/_s2jw_profiled_memory_coordinator.py` | `c9676ea9a740bfb82d66a91c00c559d1ff4d3759bd7bfed12c55afb9820dea81` |
| visueller Teilhinweisscan | `tools/_s2kq_private_partial_cue_retrieval_336.py` | `669e3f7de6957640ed37e79d6608d94d7839d81e959ee1f48d7942526a86e422` |
| auditiver Teilhinweisscan | `tools/_s2kz_private_auditory_partial_cue_retrieval_336.py` | `58bb0f7e9265278ced70d38bfe2858081b2e2eb134753c3457e4e03ba01eb04b` |
| bestaetigte E2E-Referenz | `tools/_s2lj_coherent_av_runner.py` | `5f2b4e568cc44e873720a3ed5facac08aeec589880ac291780d23e4249141bc1` |

Diese Quellen sind Funktionsreferenzen, keine Eingaben fuer eine
Sollentscheidung. Historische Ergebnisdateien liefern weder Zustand noch
Kandidaten fuer einen spaeteren S2-LL-Lauf.

## Rollenfreiheit

Im Laufpfad sind ausschliesslich neutrale technische Kennungen erlaubt:

- Stream-ID, Ereignisordinalzahl und Ereignistyp;
- Quell-, Payload-, Rezeptor-, Profil-, Zeit- und Geometriedigests;
- Owner-, Vorzustands-, Nachzustands-, Receipt- und Ledgerdigests;
- Masken- beziehungsweise Bandplan als unabhaengige technische Form;
- mechanische Scan-, Kandidaten-, Bereichs- und Enthaltungsbefunde.

Verboten sind in Eingaben, IDs, Pfaden, Receipts, Fehlermeldungen und
Steuerzweigen:

- `TARGET`, `DISTRACTOR`, `POSITIVE`, `NEGATIVE`, Sollklasse oder Fallrolle;
- Objekt-, Bedeutungs-, Kategorie-, Belohnungs- oder Semantiklabels;
- erwarteter Bereich, erwarteter Kandidat oder erwartete Entscheidung;
- Zielwerte, Rekonstruktionsziel oder Evaluationsstatus.

Ein Ereignistyp ist keine fachliche Rolle. Er beschreibt nur, welche
Sensorbestandteile tatsaechlich vorliegen und welche Operation dadurch
zulaessig ist.

## Eingangsformen

`PerceptionStreamEvent336V1` ist eine unveraenderliche, diskriminierte Union
aus genau drei Formen.

### `COMPLETE_AV_PERCEPTION`

Die Form bindet:

- genau einen kanonischen `1920 x 1080 RGB8`-Frame;
- genau ein dazu zeitlich ueberlappendes mono `PCM_F32LE`-Fenster bei
  48 kHz, materialisiert als zehn geordnete Hops zu 480 Samples;
- getrennte native Audio- und Videofenster;
- eine gemeinsame Feldzeitgruppe;
- Default-Live-Profil-, Geometrie-, Payload- und Quelldigests.

Nach der Rezeptorreduktion muessen exakt 48 auditive und 288 visuelle Werte
vorliegen. Nur diese 336 Werte werden an Feld- und Memoryprojektion gebunden.

### `PARTIAL_VISUAL_CUE`

Die Form bindet:

- genau einen tatsaechlich analysierten, unvollstaendigen RGB8-Frame;
- eine unabhaengig vorher gebildete Positionsmaske;
- 32 beobachtete und 256 maskierte visuelle Rezeptorpositionen;
- native visuelle Quellenzeit und getrennte gemeinsame Feldzeit;
- keine Vollprobe und keine vollstaendigen Zielwerte.

Die Maske darf weder aus Nullwerten noch aus erwarteten Zielwerten abgeleitet
werden.

### `PARTIAL_AUDITORY_CUE`

Die Form bindet:

- ein tatsaechlich analysiertes mono PCM-Fenster;
- einen unabhaengig vorher gebildeten 24/24-Bandplan;
- 24 beobachtete und 24 maskierte auditive Rezeptorbaender;
- native auditive Quellenzeit und getrennte gemeinsame Feldzeit;
- keine Vollprobe und keine vollstaendigen Zielwerte.

Positive numerische Distanzen werden ausschliesslich gegen die vorhandene
Schwelle ausgewertet; exakte Floatgleichheit wird nicht erfunden.

Andere Kombinationen, doppelte Modalitaeten oder gemischte Voll-/Teilformen
sind ungueltig und stoppen vor Feld- oder Memoryaufruf.

## Zeitordnung und Stromzustand

Ein `PerceptionStreamPlanV1` bindet vor dem ersten Ereignis:

- eine endliche maximale Ereigniszahl;
- genau eine gemeinsame monotone Feldzeitbasis;
- die zugelassenen nativen Audio- und Videouhren;
- feste Rezeptor-, Profil-, Memory- und Ressourcendigests;
- maximale Rohpayload-, Wert-, Feldkontakt-, Scan- und Ergebnisbudgets.

Jedes Ereignisfenster liegt strikt nach dem letzten Fenster derselben
nativen Quelle. Gemeinsame Feldzeit ersetzt niemals native Rezeptorzeit.
Gleichzeitig abgeschlossene Audio- und Videoanteile bilden eine Gruppe und
erhalten keine kuenstliche Reihenfolge.

`PerceptionStreamStateV1` enthaelt nur:

- naechste Ereignisordinalzahl und letzten Ereignisdigest;
- aktuellen Feldzustand;
- aktuellen atomaren B4-/TSPM-Zustand;
- kumuliertes endliches Ressourcenledger;
- Stromstatus `OPEN` oder explizit `CLOSED`.

Der Strom besitzt keinen verbrauchbaren Gesamt-Owner. Jeder einzelne
Ereignisaufruf erhaelt einen neuen `PerceptionEventOwnerV1` mit genau den
Zustaenden `READY`, `PROCESSING`, `CONSUMED` oder `FAILED`. Ein terminaler
Ereignis-Owner kann nicht wiederverwendet werden. Sein Abschluss verbraucht
nur diesen Aufruf; ein `OPEN`-Strom bleibt fuer das naechste zeitlich gueltige
Ereignis verfuegbar.

Es gibt keine verborgene Ereignishistorie und keinen zusaetzlichen
Speicherbestand. Nach jedem Ereignis wird nur der neue Feld-, Memory- und
Kettendigest fortgefuehrt.

## Deterministisches Routing

Nach vollstaendiger Quellen-, Zeit-, Profil- und Budgetvalidierung gilt genau
diese Tabelle:

| Ereignisform | Feld | Memory | Abruf |
| --- | --- | --- | --- |
| `COMPLETE_AV_PERCEPTION` | 48 + 288 Kontakte | genau eine atomare B4-/TSPM-Formation | keiner |
| `PARTIAL_VISUAL_CUE` | 288 aktuelle visuelle Kontakte | keine Formation | genau ein vollstaendiger read-only `9/3/4`-Scan |
| `PARTIAL_AUDITORY_CUE` | 48 aktuelle auditive Kontakte | keine Formation | genau ein vollstaendiger read-only `9/3/8`-Scan |

Routing darf weder vom Inhalt der Werte noch von Evaluationsmetadaten
abhaengen. Ein vollstaendiges Ereignis kann nicht in einen Probevorgang und
ein Teilhinweis nicht in eine Formation umgedeutet werden.

## Vollstaendige AV-Wahrnehmung

Vor dem ersten Armaufruf wird ein `BoundPerception336V1` vollstaendig
materialisiert. Feld- und Memoryzweig muessen dieselben 48 auditiven und 288
visuellen Werte, Wertedigests, Zeiten, Geometrien und Quelldigests binden.

Aus diesem unveraenderlichen Beleg entstehen zwei unabhaengige
Geschwisterprojektionen. Ihre Abschlussregeln sind getrennt:

1. Der Feldzweig verarbeitet genau eine Abschlussgruppe. Ein vollstaendig
   validierter Feldnachzustand wird unmittelbar als gueltiger Feldkontakt
   fortgeschrieben und ist nicht vom Memoryergebnis abhaengig.
2. Der Memoryzweig versucht unabhaengig vom Feldabschluss genau eine
   Formation aus derselben Eingangsbindung. Ausschliesslich B4 und TSPM
   bilden gemeinsam einen atomaren Kandidaten und werden nur zusammen
   veroeffentlicht.
3. Der Ereignisbeleg bindet den Feldreceipt und getrennt entweder den
   vollstaendigen atomaren Memoryreceipt oder einen neutralen Memoryfehler.
4. Feld- und Memoryreceipt muessen auf denselben `BoundPerception336V1`-
   Digest zurueckweisen; keiner ist Elternbeleg des anderen.

Nach gueltiger gemeinsamer Eingangsbindung wird keiner der beiden
Geschwisteraufrufe wegen eines Erfolgs oder Fehlers des anderen ausgelassen.
Ihre Receipts und Fehlerzustaende bleiben getrennt.

Ein Memoryfehler verwirft den lokalen B4-/TSPM-Kandidaten und laesst den
Memoryvorzustand unveraendert. Er darf den bereits gueltigen Feldkontakt
weder loeschen noch zurueckrollen. Ein gebundener Forschungslauf kann dadurch
`NOT_EVALUABLE` werden, waehrend Feldreceipt und fortgeschriebener
Feldzustand als tatsaechlich erfolgte Wahrnehmung bestehen bleiben. Der
Ereignis-Owner endet `FAILED`; der Stromstatus bleibt davon getrennt und kann
weiterhin `OPEN` sein.

## Teilhinweis und Kontextbefund

Ein Teilhinweis erzeugt zuerst seinen realen Feldkontakt. Danach liest der
qualifizierte Slotscan den unveraenderten Memoryzustand:

- B4 und Fast bleiben interne Evidenz von `A_RECENT`;
- visuelles Slow bildet ausschliesslich `B_STABLE_VISUAL`;
- auditives Slow bildet ausschliesslich `B_STABLE_AUDITORY`;
- oeffentlich existieren weiterhin nur `A_RECENT` und `B_STABLE`;
- alle gebundenen Slots werden auch bei fruehem Treffer vollstaendig gescannt.

Der Scan darf genau eine getrennte Hypothese oder eine kontrollierte
Enthaltung ausgeben. Mehrdeutigkeit innerhalb A, innerhalb B oder zwischen A
und B fuehrt zur Enthaltung. Es gibt keine Rangfolge, Nearest-Winner-Regel,
Verschmelzung oder Ausweichlogik.

Die Hypothese enthaelt nur die fuer maskierte Positionen vorgeschlagenen
Werte und ihre Bereichs- und Herkunftsbelege. Beobachtete Rezeptorwerte und
Feldkontakte werden nicht ersetzt. Hypothese, Enthaltung und Scanreceipt
werden niemals in Memory oder Feld zurueckgeschrieben.

Vor und nach Abruf muessen Gesamt-, B4-, Fast-, auditory-Slow- und
visual-Slow-Digest identisch sein. Der Feldzustand darf sich nur durch den
aktuellen realen Teilhinweiskontakt aendern, nicht durch Scan oder Hypothese.
Ein Scan-, Evidenz- oder Kontextfehler erzeugt keine Teilhypothese und keine
Memorymutation. Er darf den bereits gueltigen Feldkontakt jedoch weder
loeschen noch zurueckrollen. Der Ereignisbeleg bindet dann den Feldreceipt und
den getrennten neutralen Fehlerabschluss; der Ereignis-Owner endet `FAILED`,
ohne den Strom als Ganzes zu verbrauchen.

## PPB-Integritaet

Jede stabile Slow-Bindung wird aus der tatsaechlichen PPB-Kette abgeleitet:

```text
CREATED  support 1
MATCHED  support 2
MATCHED  support 3
```

Mit `update_rate = 0.05` gilt fuer jede Modalitaet die exakte vorhandene
Binary64-Operationsreihenfolge. Der finale Prototyp darf nicht als bitgleich
zum ersten Rezeptorvektor vorausgesetzt werden. Uebergangsintegritaet und
funktionaler Distanztreffer sind getrennte Befunde.

## Rohdaten- und Provenienzgrenze

RGB-Frames und PCM-Hops existieren nur waehrend der jeweiligen
Rezeptoranalyse. Hoechstens ein Frame und ein Hop duerfen gleichzeitig
gehalten werden. Nach Reduktion werden die Rohpayloads verworfen.

Stromzustand, Memory, Feldreceipt, Scan, Hypothese und Ergebnis duerfen keine
Rohpixel, PCM-Samples, DOM-, URL-, Browser-, Objekt- oder Quelldaten
enthalten. Technische Auditprovenienz ist digestgebunden, darf aber weder
Routing, Matching, Bildung noch Zulassung beeinflussen.

## Ressourcenobergrenzen

Die erste Implementierung muss Grenzen aus dem gebundenen Profil ableiten
und vor Ausfuehrung materialisieren. Mindestens gelten pro Ereignis:

| Ereignis | Feldkontakte | Memoryaufrufe | Scanvergleiche Produktionsarm | Direktbaseline |
| --- | ---: | ---: | ---: | ---: |
| vollstaendiges AV | 336 | genau 1 atomare Formation | 0 | keine |
| visueller Teilhinweis | 288 | 0 | hoechstens 800 | unabhaengig hoechstens 800 |
| auditiver Teilhinweis | 48 | 0 | hoechstens 528 | unabhaengig hoechstens 528 |

Memorykapazitaeten bleiben `9/3/8/4`. Ein Funktionslauf besitzt eine feste
obere Ereignis-, Operations-, Wertvergleichs-, Feldkontakt-, Rohbyte- und
Ergebnisgrenze. Budgetueberschreitung stoppt fail-closed; sie darf nicht
durch Weglassen von Slots oder vorzeitigen Scanabschluss vermieden werden.

## Direktbaselines

Fuer jeden Teilhinweis wird nach dem Produktionsscan eine unabhaengige
Direktbaseline mit identischem Cue, Zustand, Maske und Budget ausgefuehrt.
Sie darf keine Scan-, Aufloesungs- oder Entscheidungshilfe des
Produktionspfads aufrufen.

Produktionspfad und Baseline muessen Bereichskardinalitaet, Enthaltung,
Hypothesenwerte und Herkunft fachlich gleich beurteilen. Owner- und
resultatspezifische Digests duerfen verschieden sein.

## Getrennte Auswertung

Der Ausfuehrungspfad endet mit einem rollenfreien
`ExecutionEvidencePackageV1`. Erst danach verbindet ein
`EvaluationRunBindingV1` diesen Beleg mit einem unabhaengig vorab versiegelten
Evaluationsplan.

Nur der Auswerter darf Ereignisordnungen nachtraeglich als Wiederholung,
Ablenkung, Ziel, Holdout oder Negativfall benennen und Zielwerte sehen. Diese
Informationen sind keine Eltern eines Laufartefakts.

## Fail-Closed- und Falsifikationsregeln

`NOT_EVALUABLE` gilt bei:

- ungueltiger Ereignisform, Zeitfolge, Quelle, Dimension oder Maske;
- unterschiedlichen Feld-/Memory-Geschwisterwerten;
- keiner oder mehr als einer Memoryformation fuer ein vollstaendiges AV-
  Ereignis;
- Memorymutation waehrend eines Teilhinweises;
- Feldkontakt aus einer Hypothese;
- Ruecknahme eines gueltigen Feldkontakts wegen eines spaeteren Memory-,
  Scan- oder Kontextfehlers;
- Wiederverwendung eines Ereignis-Owners oder Verbrauch des gesamten Stroms
  durch einen einzelnen Aufruf;
- Rollen-, Zielwert- oder Evaluationsleck im Laufpfad;
- unvollstaendigem Scan, Baselinebruch, Digest- oder Budgetfehler.

Ein vollstaendiger, technisch gueltiger Lauf bleibt fachlich auswertbar,
auch wenn Wiederholung nicht verdichtet, Vergessen anders verlaeuft, ein
Teilhinweis keinen Kandidaten findet oder die Baseline abweicht. Solche
Abweichungen sind Funktionsbefunde beziehungsweise Falsifikationen und keine
Infrastrukturfehler.

## Erste spaetere Qualifikation

Eine neutrale Qualifikation darf nur kurze, nicht fachlich benannte
Ereignisse verwenden. Sie muss mindestens pruefen:

1. alle drei Ereignisformen und deterministisches Routing;
2. monotone native Zeit sowie simultane AV-Gruppen ohne Binnenrangfolge;
3. identische Feld-/Memory-Geschwisterprojektion;
4. genau eine atomare Formation je vollstaendigem Ereignis;
5. keinerlei Formation bei beiden Teilhinweisformen;
6. vollstaendige visuelle und auditive Slotscans;
7. getrennte A-/B-Hypothese oder Enthaltung;
8. unabhaengige Direktbaseline;
9. lokale B4-/TSPM- beziehungsweise Hypothesenkandidaten ohne Teilcommit bei
   Fehler, bei gleichzeitig dauerhaftem Erhalt eines bereits gueltigen
   Feldkontakts;
10. vollstaendige Memory-Read-only- und Kontext-ohne-Feldrueckwirkung;
11. frische Einmal-Owner je Ereignis und ein danach weiterhin offener Strom;
12. Rohdatenausschluss und endliches Ledger;
13. isolierte Ablehnung von Rollen-, Zeit-, Quellen-, Masken- und
    Geschwistermanipulationen.

Die Qualifikation ist noch kein Nachweis fortlaufenden Lernens. Ein spaeterer
Funktionslauf benoetigt eine neue, endliche und vorab gebundene
Wahrnehmungsfolge sowie eine getrennte Freigabe.

## Aussagegrenze

S2-LL beschreibt einen begrenzt online verarbeitbaren Wahrnehmungsablauf. Das
System entscheidet anhand der technischen Vollstaendigkeit eines aktuellen
Ereignisses selbst, ob es bildet oder read-only abruft. Wiederholung und
Vergessen entstehen ausschliesslich aus der zeitlichen Wahrnehmungsfolge.

Nicht nachgewiesen oder eingefuehrt werden automatische Maskenerkennung,
semantische Ereignisbildung, Aufmerksamkeit, Belohnungslernen, unbegrenzter
Dauerbetrieb, automatische Auswahl zwischen mehreren Erinnerungen oder eine
Wirkung des Kontextes auf das MCM-Feld.
