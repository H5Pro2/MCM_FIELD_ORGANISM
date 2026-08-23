# S1-VV: Statischer PPB-1-Einmallauf-, Handoff-, Ergebnis- und Fehlervertrag

## Auftrag und Grenze

S1-VV bindet vor jeder Integration die einzige zulaessige private
Orchestrierung zwischen dem korrigierten S1-VQ-Runner und der S1-VT-
Ergebnispipeline.

Der Vertrag legt fest:

- eine feste atomare Handoffreihenfolge;
- eine dauerhaft verbrauchbare Einmallauffreigabe;
- eine prozessuebergreifende Wiederholungssperre;
- genau ein vollstaendiges Erfolgs- oder Fehlerobjekt;
- kanonische persistente Artefakte ausserhalb des Git-Bestands;
- feste Digest-, Aufruf- und Fehlerrollen;
- synthetische Integrationsgrenzen fuer den naechsten Schritt.

S1-VV implementiert nichts und fuehrt keinen Test oder Matrixfall aus. Eine
reale Ausfuehrungsfreigabe wird nicht erteilt.

## Unveraenderte technische Grundlage

Verbindlich bleiben:

```text
Elternplan:          384 Pfade
Korrekturplan:       528 Pfade
PPB-Aufrufe:         9.476
Baselineaufrufe:    66.332
Gesamtaufrufe:      75.808
```

```text
Elternplandigest:
35c1e589f749f1c1f1f24900f611fd43f8329d803a4b82ca94584d1925067ba3

Korrekturplandigest:
f307363400ba66e53a49ec9cd21bc17973f93f240f3946eade2c6a7dbdcd1210

S1-VU-Preflightdigest:
31147b026d7f7faacba93f15e607e077fa55ace537500bf4c450f8c7d278258c
```

S1-VQ, S1-VT, S1-VO-v1, Feldkern, Medienpfade, Snapshot und oeffentliche API
bleiben in S1-VV unveraendert.

## Genau eine private Handoffreihenfolge

Eine spaetere Produktionsorchestrierung darf genau diese Reihenfolge
besitzen:

```text
H0  statische Quellen-, Plan-, Gate-, Artefakt- und Ressourcenpruefung
H1  Einmallauffreigabe dauerhaft verbrauchen
H2  privaten S1-VQ-Ausfuehrungskoerper genau einmal aufrufen
H3  altes S1-VQ-Resultat vollstaendig vorvalidieren
H4  dessen 528 Receipts atomar mit S1-VT versiegeln
H5  genau 48 Armrecords und Evidenzledger komponieren
H6  korrigierten S1-VT-v2-Auswerter genau einmal anwenden
H7  terminales Erfolgsobjekt bilden und atomar publizieren
```

Keine Stufe darf uebersprungen, wiederholt, parallelisiert oder nach einem
Resultat angepasst werden. Insbesondere ist kein direkter Weg vom alten
S1-VQ-Resultat zu S1-VO-v1 zulaessig.

## Vorstartpruefung H0

Vor Verbrauch der Freigabe und vor jedem registrierten Aufruf muessen
gemeinsam bestehen:

- S1-VU-Preflightdigest und spaeterer S1-VV-Vertragsdigest;
- Eltern- und Korrekturplandigest;
- Quellcodedigests der gebundenen S1-VQ-, S1-VT- und
  Produktionsorchestrierungsmodule;
- exakt 528 Pfade und 75.808 Aufrufe;
- unverbrauchte, exakt gebundene Projekteignerfreigabe;
- unbenutzte Ausfuehrungs-ID und noch nicht vorhandener Sperrmarker;
- freie Erfolgs-, Fehler- und Temporaerartefaktpfade;
- ein eigener spaeter gebundener Ressourcen-Gate-Digest;
- unmittelbar ausreichender freier Arbeitsspeicher und Speicherplatz gemaess
  diesem Ressourcen-Gate;
- weiterhin geschlossene oeffentliche API-, Snapshot- und Feldkerngrenzen.

Scheitert H0, gilt ein Nullstart: keine Freigabe wird verbraucht, kein
registrierter Pfad wird aufgerufen und kein Resultat uminterpretiert.

## Projekteignerfreigabe

Eine reale Freigabe muss spaeter als eigenes typisiertes Objekt mindestens
binden:

- eine eindeutige Ausfuehrungs-ID;
- exakt einen noch festzulegenden Autorisierungstext;
- S1-VV-Vertrags-, S1-VU-Preflight- und Ressourcen-Gate-Digest;
- Eltern- und Korrekturplandigest;
- 528 Faelle und 75.808 maximale Aufrufe;
- den allein zulaessigen Produktionsentrypoint;
- `retry_permitted = false`;
- einen kanonischen Autorisierungsdigest.

Der genaue Autorisierungstext wird erst durch einen bestandenen spaeteren
Post-Integrations-Preflight festgelegt. Der aktuelle Befehl `ok weiter` und
fruehere Freigaben anderer Laeufe sind keine reale S1-VV-
Ausfuehrungsautorisierung.

## Dauerhafter Verbrauch und Wiederholungssperre H1

Nach bestandener H0-Pruefung wird die Freigabe unmittelbar vor dem ersten
registrierten Pfad dauerhaft verbraucht. Dazu muss ein Sperrmarker exklusiv
und atomar neu angelegt werden. Existiert er bereits, ist jeder Start
verboten.

Der Marker bindet mindestens:

- Schemafassung und Ausfuehrungs-ID;
- Autorisierungs-, Vertrags-, Preflight- und Ressourcen-Gate-Digest;
- Eltern- und Korrekturplandigest;
- Quellcodedigests;
- erwartete Fall- und Aufrufbudgets;
- `authorization_consumed = true`;
- `retry_permitted = false`;
- kanonischen Markerdigest.

Der Sperrmarker wird weder bei Erfolg noch bei Fehler geloescht oder
ueberschrieben. Nach H1 ist jeder zweite Produktionsaufruf mit derselben
Ausfuehrungs-ID verboten, auch nach Prozessneustart oder fehlgeschlagenem
Lauf. Ein Prozessabbruch unmittelbar nach erfolgreicher Markeranlage gilt
ebenfalls als verbrauchter Versuch und darf nicht wiederholt werden.

## Alter S1-VQ-Ausgang H2/H3

Der Produktionsproducer ist ausschliesslich der vorhandene private
S1-VQ-Ausfuehrungskoerper. Er darf genau einmal aufgerufen werden.

Sein `S1VQMatrixResult` wird noch nicht als gueltiges Endresultat behandelt.
Vor H4 muessen mindestens bestehen:

- gebundener Korrekturplandigest;
- genau 528 geordnete Receipts;
- exakt 75.808 akzeptierte Aufrufe;
- genau 144 vorhandene alte Wiederholungsvergleichseintraege;
- keine fremde Familie, kein fremder Parameter und keine fremde Modalitaet;
- kein bereits ausgewertetes oder publiziertes Teilresultat.

Die alten verkleinerten Wiederholungsvergleichseintraege sind nur eine
Vorpruefung. S1-VT muss die vollstaendigen R0/R1-Vergleiche aus den Receipts
erneut atomar bilden.

## Versiegelung, Komposition und Auswertung H4-H6

H4 uebergibt ausschliesslich die vollstaendige Receiptfolge an
`seal_s1vt_matrix_result`. Nur ein gueltiges `S1VTSealedMatrixResult` darf H5
erreichen.

H5 uebergibt dieses versiegelte Objekt genau einmal an
`compose_s1vt_arm_records`. Nur ein vollstaendiges geordnetes
48-Arm-Kreuzprodukt mit 48 Evidenzledgern darf H6 erreichen.

H6 uebergibt die Komposition genau einmal an `evaluate_s1vt_composition`.
Nur die zwei geordneten Modalitaetsentscheidungen `auditory` und `visual`
duerfen das Erfolgsobjekt erreichen.

Zwischen H2 und H7 wird kein Zwischenobjekt nach aussen zurueckgegeben,
persistiert oder als Ergebnis geloggt.

## Terminales Erfolgsobjekt

Ein spaeteres typisiertes Erfolgsobjekt muss mindestens tragen:

- Schemafassung, Ausfuehrungs-ID und Status `SUCCESS`;
- alle Autorisierungs-, Vertrags-, Preflight-, Ressourcen-, Plan- und
  Quellcodedigests;
- Sperrmarkerdigest;
- exakt 528 Faelle und 75.808 akzeptierte Aufrufe;
- S1-VQ-Ausgangsdigest;
- S1-VT-Matrixresultat-, Kompositions- und Auswertungsdigest;
- die vollstaendigen typisierten S1-VT-Matrix-, Kompositions- und
  Auswertungsobjekte;
- `authorization_consumed = true`;
- `exactly_once_completed = true`;
- `retry_permitted = false`;
- `s1vo_v1_bypassed = false`;
- `partial_result_exposed = false`;
- kanonischen terminalen Erfolgsdigest.

Das Objekt darf erst konstruiert werden, wenn H2 bis H6 vollstaendig
bestanden sind.

## Terminales Fehlerobjekt

Jeder Fehler nach Verbrauch der Freigabe erzeugt genau ein typisiertes
Fehlerobjekt ohne Teilresultat. Es muss mindestens tragen:

- Schemafassung, Ausfuehrungs-ID und Status `ERROR`;
- Autorisierungs-, Vertrags-, Preflight-, Ressourcen-, Plan- und
  Quellcodedigests;
- Sperrmarkerdigest;
- genau eine Fehlerstufe aus `H2`, `H3`, `H4`, `H5`, `H6` oder `H7`;
- einen gebundenen stabilen Fehlercode;
- Digest der normalisierten Fehlerrolle ohne Traceback oder private Daten;
- letzte vollstaendig bestandene Stufe;
- bekannte akzeptierte Aufrufzahl oder explizit `None`;
- `authorization_consumed = true`;
- `exactly_once_completed = false`;
- `retry_permitted = false`;
- `partial_result_exposed = false`;
- kanonischen terminalen Fehlerdigest.

Zulaessige Fehlercodes sind mindestens:

```text
PRODUCER_FAILED
LEGACY_RESULT_INVALID
S1VT_SEAL_FAILED
S1VT_COMPOSITION_FAILED
S1VT_EVALUATION_FAILED
TERMINAL_PUBLICATION_FAILED
```

Das Fehlerobjekt darf keine Receipts, Armrecords, Evidenzledger oder
Teilentscheidungen enthalten. Ein Fehler darf nicht automatisch erneut
ausgefuehrt werden.

## Persistente Artefaktgrenze

Spaetere Produktionsartefakte liegen ausschliesslich unter:

```text
data/generated/ppb1/one_shot/
```

Dieser Bereich ist bereits vom Git-Bestand ausgeschlossen. Pro
Ausfuehrungs-ID sind genau diese Rollen zulaessig:

```text
<execution_id>.lock.json
<execution_id>.success.json
<execution_id>.error.json
<execution_id>.tmp
```

Der Lock wird exklusiv neu erzeugt. Erfolg oder Fehler werden zunaechst als
kanonische Bytes in die Temporaerdatei geschrieben und danach im selben
Verzeichnis atomar auf genau einen Terminalpfad verschoben. Erfolgs- und
Fehlerartefakt duerfen nie gleichzeitig existieren.

Scheitert die terminale Dateipublikation, bleibt der Sperrmarker bestehen.
Die Funktion gibt dann ein in-memory Fehlerobjekt mit
`TERMINAL_PUBLICATION_FAILED` zurueck; ein Retry bleibt verboten.

Es wird keine Systemzeit als kausale oder entscheidungsrelevante Rolle
gespeichert. Reihenfolge entsteht ausschliesslich aus Stufenrolle,
Ausfuehrungs-ID, Digests und Aufrufzaehlern.

## Synthetische Integrationsgrenze

Die naechste Implementierungsabnahme darf den realen S1-VQ-Producer nicht
aufrufen. Zulaessig ist genau ein injizierter synthetischer Producer, der ein
vollstaendiges konstruiertes `S1VQMatrixResult` liefert.

Der synthetische Pfad muss getrennt vom Produktionsentrypoint bleiben. Er
darf:

- Handoff, Versiegelung, Komposition, Auswertung und Terminalobjekte pruefen;
- verbrauchten Token und Wiederholungsstopp in einem temporaeren
  Testverzeichnis pruefen;
- fuer jede Fehlerstufe einen konstruierten Fehler injizieren;
- atomare Erfolgs-/Fehlerpublikation pruefen.

Er darf nicht:

- den privaten registrierten Runnerkoerper importieren oder aufrufen;
- eine reale Projekteignerfreigabe erzeugen;
- den Produktionsartefaktpfad verwenden;
- das oeffentliche S1-VQ-Gate oeffnen;
- Feldkern, Medienpfad, Snapshot oder API veraendern.

## Stoppbedingungen

Integration oder spaetere Ausfuehrung stoppen fail-closed bei:

- Abweichung eines gebundenen Digests;
- mehrdeutiger oder bereits verbrauchter Autorisierung;
- vorhandenem Lock-, Erfolgs-, Fehler- oder Temporaerpfad;
- unzureichendem Ressourcen-Gate;
- mehr als einem Produceraufruf;
- mehr als einem Aufruf einer S1-VT-Stufe;
- S1-VO-v1-Umgehung;
- Teilpublikation oder gleichzeitigem Erfolg und Fehler;
- Retry nach verbrauchter Freigabe;
- jeder Ergebnisanpassung, neuen Schwelle oder manuellen Uminterpretation.

## Vertragsentscheidung

```text
S1_VV_FIXED_H0_TO_H7_HANDOFF_ORDER_BOUND
S1_VV_DURABLE_PRE_FIRST_CALL_AUTHORIZATION_CONSUMPTION_BOUND
S1_VV_PROCESS_CROSSING_RETRY_BLOCK_BOUND
S1_VV_EXACT_ONE_PRIVATE_PRODUCER_CALL_BOUND
S1_VV_EXACT_ONE_SEAL_COMPOSE_EVALUATE_CHAIN_BOUND
S1_VV_ATOMIC_TERMINAL_SUCCESS_OBJECT_BOUND
S1_VV_TYPED_TERMINAL_ERROR_WITHOUT_PARTIAL_RESULT_BOUND
S1_VV_ATOMIC_GIT_IGNORED_ARTIFACT_PUBLICATION_BOUND
S1_VV_NO_SYSTEM_TIME_ROLE_BOUND
S1_VV_SYNTHETIC_INJECTED_PRODUCER_TEST_BOUNDARY_BOUND
S1_VV_NO_IMPLEMENTATION
S1_VV_NO_TEST_EXECUTION
S1_VV_NO_MATRIX_EXECUTION
S1_VV_ZERO_REGISTERED_CALLS_EXECUTED
```

S1-VV schliesst die drei S1-VU-Blocker auf Vertragsniveau. Es bestaetigt
weder Integration noch reale Ausfuehrungsbereitschaft und erteilt keine
Projekteignerfreigabe.

## Genau ein naechster Schritt

Der einzige Anschluss ist:

```text
S1-VW - private Implementierung und synthetische Abnahme der
        Einmallauf-Handoff- und terminalen Erfolgs-/Fehlerhuelle
```

S1-VW darf ausschliesslich den injizierten synthetischen Producer und
temporaere Testpfade verwenden. Der Produktionsentrypoint muss weiterhin
hart gesperrt bleiben. Der private reale S1-VQ-Ausfuehrungskoerper, alle 528
registrierten Pfade und die Produktionsartefaktgrenze duerfen nicht
aufgerufen werden.

Nach S1-VW ist ein eigener statischer Post-Integrations- und Ressourcen-
Preflight erforderlich. Erst dessen bestandener Stand darf einen exakten
Text fuer eine neue reale Projekteigner-Einmallauffreigabe vorschlagen.

## Grundlagen

- [S1-VU realer Handoff-Preflight](S1VU_PPB1_STATISCHER_REALER_HANDOFF_POST_IMPLEMENTIERUNGS_PREFLIGHT.md)
- [S1-VT private Ergebnispipeline](S1VT_PPB1_PRIVATE_ERGEBNISHUELLE_COMPOSITOR_UND_V2_AUSWERTER_ABNAHME.md)
- [S1-VS Ergebnis-Pipeline-Vertrag](S1VS_PPB1_STATISCHER_ERGEBNIS_PIPELINE_KORREKTURVERTRAG.md)
