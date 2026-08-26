# S2-DE: TSPM-1 privater Implementierungsvertrag

## Auftrag und Grenze

S2-DE bindet ausschliesslich die spaetere private Implementierung von
`TSPM-1`. Der Vertrag legt Quellen, Typen, schnelle Zustandsregeln,
Konsolidierung, Digests, read-only Abruf und Fail-Closed-Grenzen fest.

Es wurden keine Projektmodule importiert, keine Zustands- oder Probefunktion
ausgefuehrt und keine Implementierung geaendert. Oeffentliche API,
Feldsnapshot, Feldwirkung, Produktion, Semantik und reale Ausfuehrung bleiben
gesperrt. PPB-1 wird weder geaendert noch umgangen.

## Gebundene Originalexposition

Ein spaeterer `TSPM1BoundExposure` darf ausschliesslich aus genau einem
auditiven und einem visuellen
`PPB1ActiveReceptorTimedFrameBinding` derselben validierten
`PPB1ActiveReceptorBatchEnvelope` entstehen.

Die Exposition muss binden:

- Envelope-, Quellbatch- und Profilbindingdigest;
- beide Timed-Frame-Provenienzdigests;
- beide unveraenderten PPB-1-Eingabeprojektionen;
- gemeinsame Feldclock und positiv ueberlappende Feldfenster;
- getrennte Modalitaet, Geometrie, Traegerordnung und Quellclock;
- einen kanonisch aus diesen Quellen berechneten Expositionsdigest.

Eine extern gewaehlte Paar-, Welt-, Ergebnis- oder Memory-ID ist unzulaessig.
Die beiden `ReceptorContactFrame`-Objekte bleiben die einzigen spaeter an
PPB-1 uebergebbaren Eingaben. Werte aus einem Fast-Slot duerfen niemals in
neue Frames zurueckverwandelt werden.

## Private Typen

Die erste Implementierung darf genau folgende private Rollen einfuehren:

1. `TSPM1FastConfig`: Architektur-ID, Kapazitaet, auditive und visuelle
   Matchschwelle, Updatefaktor, Konsolidierungsgrenze und Ablaufgrenze.
2. `TSPM1FastSlot`: feste Slot-ID, Belegung, auditive und visuelle reduzierte
   Werte, Support, letzter Auswahlschritt, Konsolidierungszahl und letzter
   Konsolidierungsexpositionsdigest.
3. `TSPM1FastState`: Konfigurationsdigest, akzeptierte Expositionszahl,
   modalitaetsspezifische Quellclock- und Endtickgrenzen sowie feste Slots.
4. `TSPM1CompositeState`: Fast-Zustand und die zwei unveraenderten Typen
   `PPB1BankState` fuer Audio und Video sowie ein Composite-Generations- und
   Vorzustandsdigest. Der Initialzustand entsteht nur aus drei frischen
   Bankzustaenden; jeder Folgezustand nur aus einem erfolgreichen TSPM-1-
   Koordinatorschritt.
5. `TSPM1TransitionReceipt`: Quell-, Vorzustands-, Ereignis-,
   Konsolidierungs-, PPB-Readout- und Nachzustandsdigests.
6. `TSPM1StepResult`: genau ein atomarer Composite-Nachzustand und genau ein
   dazu passendes Receipt.
7. `TSPM1ReadOnlyFinding`: getrennte Fast-, Audio-PPB- und Video-PPB-Befunde
   sowie eine deterministische Kontextquellenentscheidung ohne Nachzustand.
8. `TSPM1CoordinatorOwner`: private Einmaligkeitsgrenze mit
   `AUTHORIZED`, `CONSUMED` oder `FAILED` und nicht wiedereintretendem Lock.

Alle Typen sind unveraenderlich, slotgebunden und besitzen kanonische
ASCII-JSON-Darstellungen. Sie werden weder aus `current_api.py` noch aus
Paketroot oder Lazy-Exporten exportiert.

## Konfigurationsgrenzen

Die Konfiguration ist endlich und vor Zustandsbildung digestgebunden:

- `capacity` ist eine positive ganze Zahl;
- beide Matchschwellen liegen in `[0, 2]`;
- der Fast-Updatefaktor liegt in `(0, 1]`;
- `consolidate_after` ist eine ganze Zahl groesser oder gleich `2`;
- `expire_after_exposures` ist positiv und groesser als
  `consolidate_after`;
- auditive und visuelle Traegerdimensionen werden aus den gebundenen PPB-1-
  Konfigurationen uebernommen und nicht separat konfiguriert.

Der Fast-Zustand besitzt exakt `capacity` Slots. Alle Vektorwerte liegen in
`[-1, 1]`. Support wird bei `consolidate_after` gesaettigt;
Konsolidierungszahl und akzeptierte Expositionszahl duerfen die letztere
nicht ueberschreiten.

## Schneller Zustandsuebergang

Ein akzeptierter Schritt erhoeht die Expositionszahl genau einmal. Vor der
Zuordnung werden Slots freigegeben, fuer die gilt:

```text
neuer_schritt - letzter_auswahlschritt >= expire_after_exposures
```

Fuer jeden belegten Slot werden auditive und visuelle normalisierte mittlere
L1-Distanz getrennt berechnet. Ein gemeinsamer Match liegt nur vor, wenn
beide Distanzen ihre jeweilige Schwelle einhalten. Mehrere Matches werden
geordnet nach:

```text
max(auditive_distanz, visuelle_distanz),
auditive_distanz + visuelle_distanz,
slot_id
```

Der kleinste Rang gewinnt eindeutig.

### Match und Aktualisierung

Bei gemeinsamem Match werden beide Komponenten getrennt mit demselben
gebundenen Updatefaktor fortgeschrieben:

```text
neu = (1 - updatefaktor) * bisher + updatefaktor * aktuelle_exposition
```

Support steigt bis zur Konsolidierungsgrenze, der letzte Auswahlschritt wird
aktualisiert. Das Ereignis lautet `FAST_UPDATED`.

### Neue Bindung und Konflikt

Ohne gemeinsamen Match wird eine neue audiovisuelle Bindung angelegt. Passt
nur eine Modalitaet zu einem vorhandenen Slot, ist dies ein
`PARTIAL_ASSOCIATION_CONFLICT`; der bestehende Slot darf dadurch nicht
einseitig umgeschrieben werden.

Ein freier Slot mit lexikographisch kleinster Slot-ID wird zuerst verwendet.
Ist kein Slot frei, wird nach Ablaufbereinigung der Slot mit kleinstem Rang

```text
letzter_auswahlschritt, slot_id
```

atomar ersetzt. Die Ereignisse lauten `FAST_CREATED` oder `FAST_REPLACED`.
Das Receipt bindet bei Ersatz den Digest des vollstaendig verworfenen
Vorzustandsslots. Bei Ablauf bindet es die nach Slot-ID geordnete Menge aller
freigegebenen Slotdigests. Es gibt keinen Teilersatz nur einer Modalitaet.

## Konsolidierungsregel

Nur `FAST_UPDATED` kann Konsolidierung ausloesen. Eine aktuelle Exposition ist
genau dann berechtigt, wenn der aktualisierte Support
`consolidate_after` erreicht hat. Danach darf jede weitere echte passende
Exposition genau einmal konsolidiert werden; ein neuer oder ersetzter Slot
ist im Erzeugungsschritt nie berechtigt.

Die Reihenfolge ist fest:

1. alle Konfigurationen, Vorzustaende, Owner- und Quelldigests pruefen;
2. beide Originalframes und ihre Zeitordnung gegen Fast- und PPB-Vorzustaende
   pruefen;
3. Fast-Nachzustand rein lokal berechnen;
4. Konsolidierungsberechtigung aus diesem lokalen Ergebnis bestimmen;
5. falls berechtigt, `advance_ppb1_bank` genau einmal mit dem aktuellen
   auditiven Originalframe und genau einmal mit dem aktuellen visuellen
   Originalframe aufrufen;
6. beide PPB-Ergebnisse und alle Digests pruefen;
7. Fast-Slot-Konsolidierungszahl und letzten Expositionsdigest lokal binden;
8. genau ein vollstaendiges Composite-Ergebnis committen.

Scheitert ein Schritt, wird kein Nachzustand ausgegeben und der Owner wird
terminal `FAILED`. Ein Retry mit demselben Owner ist unzulaessig. Da Fast-
und PPB-Uebergaenge reine Funktionen sind, existiert vor Schritt 8 keine
sichtbare Teilaenderung.

`CONSOLIDATION_COMMITTED` bedeutet ausschliesslich, dass beide PPB-1-Schritte
mit der aktuellen Originalexposition atomar uebernommen wurden. Die beiden
vorhandenen PPB-Readouts berichten davon getrennt, ob ihre Slots bereits
`stabilized` sind.

## Verbotenes synthetisches Replay

Folgende Quellen duerfen niemals an `advance_ppb1_bank` gelangen:

- Fast-Prototypwerte;
- ein frueherer Expositions- oder Receiptinhalt;
- rekonstruierte oder kopierte `ReceptorContactFrame`-Objekte;
- eine Schleife ueber alte Fast-Slots;
- Test-, Ergebnis-, Slot- oder Digestwerte als sensorische Eingabe.

Ohne die beiden aktuellen, unveraenderten und provenancegebundenen
Originalframes lautet der Schritt fail-closed. Konsolidierung darf pro
akzeptierter Exposition hoechstens zwei PPB-Aufrufe erzeugen: genau einen je
Modalitaet.

## Getrennte Ergebnisrollen

Jedes Receipt unterscheidet zwingend:

- `FAST_CAPTURED`: neuer oder ersetzter kurzlebiger Zustand, noch nicht
  konsolidiert;
- `FAST_UPDATED_NOT_READY`: bestaetigte schnelle Bindung unterhalb der
  Konsolidierungsgrenze;
- `CONSOLIDATION_COMMITTED`: beide langsamen PPB-Schritte atomar erfolgt;
- `FAST_EXPIRED` beziehungsweise `FAST_REPLACED`: Digest des verworfenen
  schnellen Zustands, ohne Rueckgabe als aktiver Inhalt;
- `PPB_AUDITORY_STABILIZED` und `PPB_VISUAL_STABILIZED`: getrennte bestehende
  PPB-Readoutrollen, die nicht aus dem Konsolidierungsstatus abgeleitet werden.

Ein Fast-Digestwechsel allein ist weder Konsolidierung noch erfolgreicher
Abruf.

## Read-only Abruf

`probe_tspm1_read_only` erhaelt einen unveraenderten Composite-Zustand und
eine kausal spaetere gebundene Audio-/Video-Probe. Die Funktion:

- prueft beide Probequellen und Vorzustandsdigests vor jeder Distanz;
- sucht einen gemeinsamen Fast-Match mit derselben Rangfolge wie die Bildung;
- ruft die bestehende S1-WU-Probe je PPB-1-Modalitaet hoechstens einmal auf;
  ist die jeweilige PPB-1-Bank noch frisch und ohne akzeptierten Schritt,
  entsteht stattdessen der explizite Befund `SLOW_UNAVAILABLE` ohne
  S1-WU-Aufruf;
- gibt Fast-, Audio-PPB- und Video-PPB-Befund getrennt zurueck;
- gibt keinen Nachzustand und keine Prototypwerte aus;
- bestaetigt nach der Probe die Unveraenderlichkeit aller drei Bankdigests.

Die Kontextquellenentscheidung ist deterministisch:

1. Sind beide PPB-Befunde positiv, lautet sie `SLOW_PPB1_CONTEXT`.
2. Andernfalls liefert ein gemeinsamer Fast-Match `FAST_ASSOCIATIVE_CONTEXT`.
3. Ein einzelner PPB-Treffer oder kein gemeinsamer Fast-Match liefert
   `NO_COMPLETE_CONTEXT`.

Diese Entscheidung ist nur ein privater technischer Abrufbefund. Sie wird
nicht an das Feld uebergeben.

## Digest- und Identitaetsvertrag

Getrennt gebunden werden:

- Fast-Konfigurations- und Fast-Zustandsdigest;
- auditive und visuelle PPB-1-Konfigurations- und Zustandsdigests;
- Expositions- und Probendigest;
- Konsolidierungsentscheidungsdigest aus Berechtigung, den zwei
  Originalinputdigests und den zwei PPB-Readoutdigests;
- Composite-Vor- und Nachzustandsdigest;
- Receipt- beziehungsweise Findingdigest;
- Owner-Vor- und Nachzustandsdigest.

Kein Digest darf als funktionaler Schluessel, Matchwert oder Ersatz fuer
sensorische Werte verwendet werden.

## Fail-Closed-Reihenfolge

Vor jedem Zustandsaufruf wird in dieser Reihenfolge geprueft:

1. exakte private Typen und Schema;
2. Konfigurations- und Vertragsdigests;
3. Ownerstatus, Autorisierung und Einmaligkeit;
4. Composite-, Fast- und beide PPB-Vorzustaende;
5. Envelope-, Stream-, Timed-Frame- und Expositionsprovenienz;
6. Modalitaet, Geometrie und Traegerordnung;
7. getrennte Quellclock- und Endtickordnung sowie Feldfensterueberlappung;
8. erst danach Fast-Uebergang und gegebenenfalls PPB-1-Aufrufe.

Fremde, vertauschte, stale, doppelte, teilweise verbrauchte oder
digestinkonsistente Eingaben erzeugen weder Teilreceipt noch Nachzustand.

## Abnahme- und Testumfang fuer eine spaetere Implementierung

Eine spaetere private Implementierung muss synthetisch mindestens pruefen:

- Erzeugung, Match, Aktualisierung, Ablauf und LRU-Ersatz;
- Teilassoziationskonflikt ohne einseitige Ueberschreibung;
- keine Konsolidierung vor der Grenze;
- genau zwei Originalframe-PPB-Aufrufe ab der Grenze;
- atomaren Nulloutput bei Fehler des zweiten PPB-Schritts;
- terminalen Owner bei Erfolg und Fehler sowie Retry-Verbot;
- getrennte Konsolidierungs- und PPB-Stabilitaetsrollen;
- positiven Fast-Abruf, positiven Slow-Abruf und unvollstaendigen Abruf;
- Zustandsunveraenderlichkeit jeder read-only Probe;
- statischen Ausschluss aus API, Paketroot, Lazy-Export und Feldsnapshot;
- Negativfaelle fuer fremde, vertauschte, stale und rekonstruierte Quellen.

PPB-1-only bleibt die Minimalbaseline. Assoziative-only und Reservoirarme
werden in der ersten Implementierung nicht gebaut oder ausgefuehrt.

## Entscheidung und naechster Schritt

`PASS_TSPM1_PRIVATE_IMPLEMENTATION_CONTRACT_BOUND_PENDING_STATIC_PREFLIGHT`

S2-DE bereitet TSPM-1 als kontrollierte technische Memory-Architektur vor.
Es belegt keine besondere MCM-Speicherfunktion und keine Feldwirkung.

Der naechste Schritt ist S2-DF als ausschliesslich statischer
Vollstaendigkeits-, Nichtzirkularitaets-, Quellen-, Atomaritaets- und
Materialisierbarkeitsaudit dieses Vertrags. Erst bei bestandenem Audit darf
der private Fast-Kern samt synthetischen Vertragstests implementiert werden.
