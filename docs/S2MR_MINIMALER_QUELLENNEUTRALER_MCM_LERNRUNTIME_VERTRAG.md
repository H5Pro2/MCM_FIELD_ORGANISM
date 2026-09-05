# S2-MR: Minimaler quellenneutraler MCM-Lernruntime

## Status und Zweck

Status: `S2MR_MINIMAL_RUNTIME_CONTRACT_BOUND`

S2-MR konsolidiert ausschliesslich bereits bestaetigte Komponenten zu einem
kleinen privaten, endlichen und zustandstragenden Runtime. Der Runtime nimmt
rollenfreie Wahrnehmungsereignisse an, fuehrt den Feld- und Memoryzweig
unabhaengig fort und gibt bei Teilhinweisen entweder getrennte
Kontextkandidaten oder eine begruendete Enthaltung aus.

S2-MR fuehrt keine neue Lernregel, Memoryebene, Schwelle, Rezeptorfunktion,
Vervollstaendigung oder automatische Erinnerungsauswahl ein.

## Bestaetigte Grundlage

Der Runtime darf nur diese vorhandenen Pfade komponieren:

- S2-LM fuer Ereignisowner, offenen Strom und isolierte Geschwisterzweige;
- S2-JW fuer genau eine atomare B4-/TSPM-Formation eines vollstaendigen
  `48 + 288`-Wahrnehmungszustands;
- den vorhandenen S2-JT/S2-LO-Feldadapter fuer reale Feldkontakte;
- S2-KQ fuer den vollstaendigen visuellen `9/3/4`-Teilhinweisscan;
- S2-KZ fuer den vollstaendigen auditiven `9/3/8`-Teilhinweisscan;
- die jeweils unabhaengigen direkten Slotscan-Baselines.

Die oeffentlichen Memorybereiche bleiben exakt `A_RECENT` und `B_STABLE`.
B4 und Fast sind ausschliesslich interne Evidenz von `A_RECENT`; auditory und
visual Slow sind modalitaetsgetrennte Bestandteile von `B_STABLE`.

## Bewusst ausgeschlossene Pfade

S2-MR importiert oder verwendet nicht:

- S2-MP oder eine andere Bewegungsmessung;
- die S2-MA-Zwei-Blick-Integration oder die S2-MB-Huelle;
- externe S2-LZ-Modell-, Familien- oder Kalibrierungsrollen;
- die in S2-ME untersuchte slotgebundene Anwendbarkeitsevidenz;
- Kontextverbraucher, Maskenfuellung oder zusammengesetzte Ersatzwahrnehmung;
- Browser-, Kamera-, Mikrofon-, Desktop- oder Videoadapter;
- append-only Recorder-, Forschungsfall- oder Auswertungsinfrastruktur.

S2-MI und S2-ME bleiben blockiert. S2-MQ bleibt die belastbare Falsifikation
eines erwarteten zusaetzlichen Bewegungsnutzens auf seinem Korpus und
entsperrt keine Erfahrungsbindung.

## Quellenneutrale Eingangsgrenze

Der erste Runtime beginnt hinter der qualifizierten Rezeptorgrenze. Ein
Eingang ist ein bereits validierter, unveraenderlicher
`PerceptionStreamEvent336V1` mit genau einer dieser technischen Formen:

1. `COMPLETE_AV_PERCEPTION` mit 48 auditiven und 288 visuellen Werten aus
   demselben gebundenen AV-Fenster;
2. `PARTIAL_VISUAL_CUE` mit 288 tatsaechlich analysierten visuellen Werten,
   unabhaengiger Positionsmaske und nativer visueller Zeit;
3. `PARTIAL_AUDITORY_CUE` mit 48 tatsaechlich analysierten auditiven Werten,
   unabhaengigem 24/24-Bandplan und nativer auditiver Zeit.

Der Runtime akzeptiert keine frei eingespeisten Wertvektoren. Ein privater
Ingressadapter muss die vorhandenen visuellen beziehungsweise auditiven
Rezeptorbelege, Quelldigests, Geometrien und Zeitfenster validieren, bevor er
das S2-LM-Ereignis bildet. Der funktionale Ereignisbeleg enthaelt keine
Quellklasse. Auditprovenienz darf nur Quelle und Bytebindung validieren und
darf Routing, Formation, Matching oder Scanentscheidung nicht beeinflussen.

Diese Grenze ist quellenneutral, aber noch kein Nachweis austauschbarer realer
Quellen. Die qualifizierte Simulation bleibt die einzige bestaetigte
kanonische Quelle. Die auf 200 ms begrenzte S2-JO-Episode wird nicht still zu
einem fortlaufenden Liveadapter erweitert.

## Endlicher Runtimezustand

`MinimalMCMRuntimeState336V1` bindet unveraenderlich:

- Runtime- und Stream-ID;
- Status `OPEN` oder `CLOSED`;
- naechste Ereignisordinalzahl und letzten Ereignisdigest;
- den aktuellen Feldzustand samt Digest;
- den aktuellen atomaren B4-/TSPM-Zustand samt Digest;
- kumulative Ereignis-, Feld-, Formations- und Scanzaehler;
- das beim Start fest gebundene maximale Ereignisbudget;
- Profil-, Rezeptor-, Feld-, Memory-, Scan- und Baselinequellhashes;
- den eigenen kanonischen Zustandsdigest.

Der Zustand bleibt zwischen einzelnen Aufrufen im selben endlichen Prozess
erhalten. S2-MR behauptet noch keine dauerhafte Wiederanlaufpersistenz nach
Prozessende. Dateispeicherung, Migration und Crash-Recovery sind nicht Teil
dieses Vertrags.

Hypothesen, Teilhinweiswerte und Scanresultate werden nicht im Runtimezustand
gespeichert. Nach Abschluss eines Ereignisses bleiben nur Feld-, Memory- und
Stromzustand sowie kumulative technische Zaehler erhalten.

## Einmal-Owner und offener Strom

Jedes Ereignis erhaelt einen frischen `PerceptionEventOwner`, der exakt den
aktuellen Streamzustandsdigest und Ereignisdigest bindet. Ein Owner kann
genau einmal `CONSUMED` oder `FAILED` erreichen und nie wiederverwendet
werden.

Der Verbrauch eines Ereignisowners verbraucht den Runtime nicht. Nach jedem
vollstaendig behandelten Ereignis bleibt der Runtime `OPEN`, bis ein eigener
expliziter `close()`-Aufruf den endlichen Strom abschliesst. Nach `CLOSED`
werden neue Ereignisse fail-closed abgewiesen.

## Deterministisches Routing

Der Runtime delegiert genau einen Aufruf an
`RoleFreePerceptionStreamProcessor.process_once`. Er implementiert keine
zweite Routingtabelle und keine eigene Matchingregel.

| Ereignis | Feldzweig | Memoryzweig | Read-only Scan |
| --- | --- | --- | --- |
| vollstaendiges AV | genau ein Kontakt aus 336 Werten | genau eine atomare Formation | keiner |
| visueller Teilhinweis | genau ein Kontakt aus 288 Werten | keine Formation | S2-KQ plus Direktbaseline |
| auditiver Teilhinweis | genau ein Kontakt aus 48 Werten | keine Formation | S2-KZ plus Direktbaseline |

Routing haengt ausschliesslich von der validierten technischen Ereignisform
ab, niemals von Werten, Kandidaten, Rollen oder einem Sollergebnis.

## Unabhaengige Feld- und Memoryfortschreibung

Feld und Memory erhalten Geschwisterprojektionen desselben vollstaendigen
Wahrnehmungsbelegs. Beide binden denselben Wahrnehmungsdigest; keiner ist
Elternbeleg des anderen.

- Ein gueltiger Feldkontakt wird sofort als Feldnachzustand uebernommen.
- Ein Memoryfehler darf diesen Feldkontakt nicht zuruecknehmen.
- Ein Feldfehler verhindert den unabhaengigen Memoryversuch nicht.
- Atomar ist ausschliesslich die gemeinsame B4-/TSPM-Formation.
- Bei deren Fehler bleibt der vollstaendige Memoryvorzustand erhalten.
- Ein Teilhinweis darf den Memoryzustand unter keinem Pfad veraendern.

Ein Ereignis kann deshalb einen gueltigen Feldnachzustand und zugleich einen
Memory- oder Scanfehler tragen. Der technische Ereignisabschluss macht beide
Tatsachen sichtbar, statt den erfolgreichen Geschwisterzweig umzudeuten.

## Rollenfreie Bildung

Jede vollstaendige AV-Wahrnehmung bildet genau einmal Memory. Der Runtime
kennt keine Wiederholung, Ziel-, Distraktor-, Trainings-, Holdout-, Familien-
oder Bedeutungsrolle. Wiederholung, Verdichtung, Instabilitaet und Vergessen
entstehen ausschliesslich aus Ereignisfolge und unveraenderten Memoryregeln.

PPB-Support und Prototypdigests werden aus den tatsaechlichen
`CREATED`-/`MATCHED`-/`REPLACED`-Uebergaengen gebunden. Der Runtime setzt
keine Bitgleichheit eines fortgeschriebenen Prototyps mit seinem ersten
Eingang voraus.

## Teilhinweisabruf und Kandidatenausgabe

Ein Teilhinweis erzeugt zuerst seinen unabhaengigen realen Feldkontakt.
Danach scannen Produktionsarm und Direktbaseline denselben unveraenderten
Memoryzustand vollstaendig.

Die Runtimeausgabe darf genau eine dieser Formen besitzen:

- `CONTEXT_CANDIDATE_AVAILABLE`: Der qualifizierte Scan liefert genau eine
  mechanisch anwendbare Hypothese aus `A_RECENT` oder der passenden
  `B_STABLE`-Modalitaet.
- `ABSTAIN_INTERNAL_AMBIGUITY`: Mehrdeutigkeit innerhalb eines Bereichs.
- `ABSTAIN_AMBIGUOUS_CONTEXT`: anwendbare Kandidaten in beiden Bereichen.
- `ABSTAIN_NO_CONTEXT`: kein gespeicherter Kandidat vorhanden.
- `ABSTAIN_NO_APPLICABLE_CONTEXT`: Kandidaten vorhanden, aber mit dem
  Teilhinweis nicht vereinbar.
- `SCAN_FAILED`: ungueltige oder beschaedigte Evidenz ohne Teilhypothese.

`CONTEXT_CANDIDATE_AVAILABLE` ist keine Erinnerungsauswahl und keine
Vervollstaendigung. Die Hypothese bleibt ein getrenntes unveraenderliches
Objekt mit Bereichs-, Slot-, Quellen-, Masken- beziehungsweise Band- und
Memoryvorgangsdigests. Sie veraendert weder beobachtete Rezeptorwerte noch
Feldkontakte und wird nicht an Memory zurueckgegeben.

Mehrere Kandidaten werden nie gerankt, gemittelt, verschmolzen oder durch
Nearest-Winner reduziert. Es gibt keinen Fallback zwischen `A_RECENT` und
`B_STABLE` und keine crossmodale Ersetzung.

## Direktbaseline

Jeder Teilhinweis fuehrt genau einen Produktionsscan und genau eine
unabhaengige Direktbaseline mit identischen Eingaben und Grenzen aus.
Produktions- und Baselinepfad duerfen keine Scan- oder Entscheidungshilfe
teilen.

Verglichen werden Entscheidung, oeffentlicher Memorybereich, vorgeschlagene
Werte, Masken- beziehungsweise Bandpositionen und Herkunft. Owner- und
resultatspezifische Digests duerfen verschieden sein. Eine Abweichung bleibt
sichtbar und fuehrt im ersten Runtime zu `SCAN_FAILED`; sie darf keine
Hypothese veroeffentlichen.

## Rohdaten- und Semantikgrenze

RGB8-Frames und PCM-Fenster sind nur waehrend der Rezeptoranalyse zulaessig
und werden danach verworfen. Runtimezustand und Schrittresultat enthalten
keine Rohpixel, PCM-Samples, DOM-, HTML-, URL-, Seitentext-, Accessibility-,
Label-, Reward-, Objekt- oder Generatormetadaten.

Fachliche Rollen und Zielwerte duerfen nur in einer nachgelagerten, getrennt
vorversiegelten Evaluationswurzel vorkommen. Sie sind niemals Eltern von
Ingress-, Ereignis-, Feld-, Memory-, Scan-, Hypothesen- oder Runtimebelegen.

## Ressourcen- und Kapazitaetsgrenzen

Die bestehenden Kapazitaeten bleiben unveraendert:

- B4: 9 Slots;
- Fast: 3 Slots;
- auditory Slow: 8 Slots;
- visual Slow: 4 Slots.

Pro Ereignis gelten weiterhin:

| Ereignis | Feldkontakte | Formationen | Vergleiche Produktionsarm | Direktbaseline |
| --- | ---: | ---: | ---: | ---: |
| vollstaendiges AV | 336 | 1 | 0 | 0 |
| visueller Teilhinweis | 288 | 0 | hoechstens 800 | hoechstens 800 |
| auditiver Teilhinweis | 48 | 0 | hoechstens 528 | hoechstens 528 |

Das maximale Ereignisbudget wird beim Initialisieren als positive endliche
Zahl gebunden und kann waehrend des Stroms nicht erhoeht werden. Jeder
Schritt prueft seine kumulativen Zaehler vor Veroeffentlichung. Ein
Runtime-Schrittbeleg bleibt unter 65.536 kanonischen Bytes und enthaelt nur
kompakte Digests, Status, Zaehler und gegebenenfalls genau eine getrennte
Hypothese. Es entsteht kein Recorder und kein Laufjournal.

## Private Schnittstelle

Die Implementierung darf genau diese neue duenne Oberflaeche ergaenzen:

```python
@dataclass(frozen=True, slots=True)
class MinimalMCMRuntimeConfig336V1:
    runtime_id: str
    max_event_count: int
    source_binding_digest: str
    component_binding_digest: str
    config_digest: str

@dataclass(frozen=True, slots=True)
class MinimalMCMRuntimeSnapshot336V1:
    runtime_id: str
    status: str
    stream_state_digest: str
    field_state_digest: str
    memory_state_digest: str
    processed_event_count: int
    snapshot_digest: str

@dataclass(frozen=True, slots=True)
class MinimalMCMRuntimeStep336V1:
    event_digest: str
    prestate_digest: str
    poststate_digest: str
    perception_status: str
    memory_status: str
    context_status: str
    field_receipt_digest: str | None
    memory_receipt_digest: str | None
    scan_receipt_digest: str | None
    baseline_receipt_digest: str | None
    hypothesis: PartialCueContextHypothesis336V1 | AuditoryPartialCueHypothesis48V1 | None
    step_digest: str

class MinimalMCMRuntime336:
    def process_once(self, event: PerceptionStreamEvent336V1) -> MinimalMCMRuntimeStep336V1: ...
    def snapshot(self) -> MinimalMCMRuntimeSnapshot336V1: ...
    def close(self) -> MinimalMCMRuntimeSnapshot336V1: ...
```

Der Runtime besitzt intern genau einen S2-LM-Prozessor und den aktuellen
S2-LM-Stromzustand. Er dupliziert keine Feld-, Memory-, Scan- oder
Entscheidungslogik.

## Fail-Closed-Regeln

Vor jedem Armaufruf fuehren ungueltige Ereignisform, Dimension, Zeit,
Geometrie, Quelle, Maske, Bandplan, Digest oder Ownerbindung zu
`INPUT_REJECTED`; Feld und Memory bleiben unberuehrt.

Nach gueltiger Eingangsbindung gelten getrennte Fehlerabschluesse:

- `FIELD_BRANCH_FAILED` laesst Memoryformation oder Scan weiterlaufen;
- `MEMORY_BRANCH_FAILED` behaelt den Memoryvorzustand und einen bereits
  gueltigen Feldkontakt;
- `PRIMARY_SCAN_FAILED` oder `BASELINE_SCAN_FAILED` veroeffentlicht keine
  Teilhypothese und nimmt den Feldkontakt nicht zurueck;
- Budgetueberschreitung veroeffentlicht keinen ueberbudgetierten
  Schrittbeleg;
- Ownerwiederverwendung und Ereignis nach `CLOSED` werden abgewiesen.

Kein Fehlerpfad darf eine zusammengesetzte Ersatzwahrnehmung oder einen
teilweise fortgeschriebenen B4-/TSPM-Zustand erzeugen.

## Neutrale Qualifikation

Die erste Qualifikation verwendet nur kleine neutrale Ereignisse und keine
Hauptgeschichte. In genau einer fokussierten Suite sind mindestens zu
pruefen:

1. Initialisierung, Snapshot und expliziter Abschluss;
2. alle drei Ereignisformen;
3. gleiche Wahrnehmungsbindung beider Geschwisterzweige;
4. genau eine atomare Formation fuer vollstaendiges AV;
5. keine Formation fuer Teilhinweise;
6. vollstaendiger visueller `9/3/4`-Scan;
7. vollstaendiger auditiver `9/3/8`-Scan;
8. Produktions-/Baselinegleichheit;
9. eindeutiger A- und eindeutiger B-Kandidat als getrennte Hypothese;
10. interne, bereichsuebergreifende, fehlende und unpassende Enthaltung;
11. Feldfehler ohne Memoryverlust;
12. Memory-/Scanfehler ohne Feldrollback;
13. Memory-Read-only bei beiden Teilhinweisen;
14. frischer Einmal-Owner je Ereignis bei weiter `OPEN` bleibendem Runtime;
15. Rollen- und Rohdatenausschluss;
16. Ereignis-, Vergleichs-, Ausgabe- und Kapazitaetsgrenzen.

Die Qualifikation prueft nur die Komposition. Sie ist kein neuer Lern- oder
Kontextnutzenbefund.

## Erster begrenzter Funktionsnachweis

Nach bestandener Qualifikation muss derselbe Runtime zunaechst die bereits
bestaetigte rollenfreie S2-LN-Ereignisfolge reproduzieren. Rollen und
Zielwerte bleiben dabei erneut ausschliesslich beim nachgelagerten Auswerter.
Danach darf genau ein neuer, vorab versiegelter endlicher Ereignisstrom
folgen. Eine echte Livequelle, automatische Vervollstaendigung oder
Erinnerungsauswahl ist dafuer nicht erforderlich und nicht freigegeben.

## Aussagegrenze

Ein bestandener S2-MR-Nachweis bestaetigt einen benutzbaren, endlichen
MCM-Systemkern fuer rollenfreie Wahrnehmung, Feldkontakt, Memorybildung und
read-only Kandidatenabruf. Er bestaetigt keine allgemeine Quellenunabhaengigkeit,
Objektidentitaet, Semantik, autonome Auswahl, Handlung, offene Welt oder
dauerhafte Langzeitpersistenz.

## Gebundener Quellstand

Vertragsbasis ist Commit `b561a69e76556a7cbeb763ef1285c9186f5a1de1`.

| Komponente | SHA-256 |
| --- | --- |
| S2-LM-Stromprozessor | `84c5650f7f52fe13eb0b8248ab73656dbb67f17fbdd93b2dfc520bacfec7e127` |
| S2-JW-Memorykoordinator | `c9676ea9a740bfb82d66a91c00c559d1ff4d3759bd7bfed12c55afb9820dea81` |
| visueller S2-KQ-Scan | `669e3f7de6957640ed37e79d6608d94d7839d81e959ee1f48d7942526a86e422` |
| visuelle Direktbaseline | `8e26b07671c901a1a1ab660b39bdf7e6478e39646703c59c4f13af8d47823d28` |
| auditiver S2-KZ-Scan | `58bb0f7e9265278ced70d38bfe2858081b2e2eb134753c3457e4e03ba01eb04b` |
| auditive Direktbaseline | `8d49715c3d59fa5d5b61855a198fb472cbbf3f34a82819e026714f9933084618` |
| vorhandener S2-LO-Adapterpfad | `42ff7cb1e07446bf07b85cc6e1b47a71efe70f66f56ad00d20b0cfc34034aed0` |
| visueller Rezeptor | `d09cb6ba35fd061e4a243b7ed2112597a194e75abd026d7cc3ab7aa89922c07a` |
| auditiver Rezeptor | `26a6bd8f2d190db60c75ad29f275b3bd8b09b6d26d4ad54e4396176c4a36d2b0` |

Die README wird durch diesen Forschungsvertrag nicht erweitert.
