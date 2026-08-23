# S1-VI: PPB-1 statischer Daten-, Distanz-, Lebenszyklus- und Testmatrixvertrag

> **Technische Abnahme:** S1-VJ implementiert den privaten reinen Referenzkern
> und besteht mit `30 von 30` registrierten PPB-Pfaden sowie `18 von 18`
> Aktivkern-Grenztests. Feldintegration und reale Medienausfuehrung bleiben
> aus.

## Freigabe und Grenze

S1-VI konkretisiert den in S1-VH freigegebenen Engineeringvertrag fuer
`PPB-1`. Gebunden werden private Schemarollen, genau eine Distanzfamilie,
deterministische Zuordnung, Prototypaktualisierung, Stabilisierung, Vergessen,
Kapazitaetskonflikt und eine endliche synthetische Vertragstestmatrix.

S1-VI enthaelt:

- keine Implementierung und keine Testausfuehrung;
- keine Feld-, Runtime-, API- oder Snapshotaenderung;
- keine reale Audio- oder Videoausfuehrung;
- keine Semantik, Woerter oder Objektklassen;
- keinen Forschungs- oder Memory-Funktionsbefund.

PPB-1 bleibt eine bewusst programmierte, transparente Engineeringkomponente.

## Private Schemafamilie

Alle nachfolgenden Rollen bleiben private Direktimportrollen. Keine Rolle wird
in `current_api`, Root-Lazy-Exports oder `SharedMCMFieldSnapshot` aufgenommen.

### PPB1BankConfig

Eine Bankkonfiguration enthaelt genau:

| Rolle | Bindung |
|---|---|
| `schema_version` | feste private PPB-1-Schemaversion |
| `bank_id` | eindeutige technische Bankkennung |
| `modality_id` | genau `auditory` oder `visual` |
| `geometry_id` | genau eine gebundene Rezeptorgeometrie |
| `carrier_ids` | nicht leere, eindeutige und geordnete Traegerliste |
| `capacity` | positive endliche Ganzzahl |
| `match_threshold` | endlicher Wert im Distanzbereich |
| `update_rate` | endlicher konvexer Aktualisierungsanteil |
| `stable_after` | positive endliche Ganzzahl |
| `expire_after_steps` | positive endliche Ganzzahl |

Audio und Video besitzen getrennte Konfigurationen. Ihre Geometrien,
Traegerlisten, Kapazitaeten und Schwellen duerfen verschieden sein. Beide
verwenden dieselbe Distanzfamilie und denselben Lebenszyklus.

### PPB1PrototypeSlot

Jede Bank besitzt bei jeder gueltigen Lage exakt `capacity` Slots in
kanonischer Slot-ID-Reihenfolge. Ein Slot enthaelt genau:

| Rolle | Freier Slot | Belegter Slot |
|---|---|---|
| `slot_id` | erforderlich | erforderlich |
| `occupied` | falsch | wahr |
| `prototype_values` | leer | fest dimensioniert und endlich |
| `support_count` | null | positiv und hoechstens `stable_after` |
| `last_selected_step` | null | positive Bankschrittnummer |

`stabilized` ist keine zusaetzliche gespeicherte Rolle. Der Zustand wird
kanonisch daraus abgeleitet, ob `support_count` den Wert `stable_after`
erreicht hat.

Ein Slot speichert keine Eingangs-ID, kein Zeitfenster, keine Rohdatenfolge,
keinen Replayzeiger und kein Label.

### PPB1BankState

Der Bankzustand enthaelt genau:

- `schema_version`;
- `bank_id`;
- `config_digest`;
- `accepted_step_count`;
- `source_clock_id`;
- `last_source_window_end_tick`;
- alle Slots in kanonischer Reihenfolge;
- kanonischen Zustandsdigest.

`accepted_step_count` zaehlt nur atomar akzeptierte Bankeingaben. Ungueltige
Eingaben veraendern weder diesen Zaehler noch irgendeinen Slot.

Im leeren Anfangszustand sind `source_clock_id` und
`last_source_window_end_tick` null. Der erste akzeptierte Eingang bindet die
Quellclock und sein Fensterende; danach gelten beide Reihenfolgenpruefungen.

Die Quellzeit dient nur der monotonen Reihenfolge innerhalb derselben
Modalitaetsbank. Vergessen verwendet keine Wand-, Geraete- oder Systemzeit,
sondern ausschliesslich akzeptierte PPB-Bankschritte.

### PPB1Readout

Ein erfolgreicher Schritt erzeugt genau einen privaten modalitaetseigenen
Readout mit:

- Schemaversion, Bank- und Modalitaetskennung;
- Ereignis `MATCHED`, `CREATED` oder `REPLACED`;
- ausgewaehlter Slot-ID;
- Matchdistanz vor Aktualisierung bei `MATCHED`, sonst null;
- abgeleitetem Stabilisierungsstatus nach dem Schritt;
- `support_count` nach dem Schritt;
- Prototypwerten nach dem Schritt;
- Prestate-, Input-, Poststate-, Config- und Readoutdigest.

Ein Validierungsfehler erzeugt keinen Erfolgsreadout und keinen Poststate.

## Kanonisierung und Digests

Konfiguration, Zustand, Inputprojektion und Readout werden als JSON-sichere
Werte mit sortierten Schluesseln, festen Feldnamen, verbotenen NaN-/Infinity-
Werten und kompakter UTF-8-Kodierung kanonisiert. Der Digest ist SHA-256 ueber
genau diese Kodierung.

Slotreihenfolge, Traegerreihenfolge und Flieszahldarstellung duerfen nicht von
Dictionary-, Hash- oder Plattformreihenfolge abhaengen.

## Eingangsprojektion

Ein Bankeingang ist genau ein vollstaendiger `ReceptorContactFrame`. Vor jeder
Distanzbildung werden statisch geprueft:

- Modalitaet entspricht der Bank;
- Geometrie entspricht der Konfiguration;
- `carrier_ids` stimmen in Inhalt und Reihenfolge exakt ueberein;
- Werteanzahl entspricht der Traegerzahl;
- alle Werte sind endlich und liegen im normalisierten Bereich von minus eins
  bis plus eins;
- Quellclock stimmt mit dem ersten akzeptierten Eingang der Bank ueberein;
- das Fensterende ist gegenueber dem zuletzt akzeptierten Fensterende strikt
  fortgeschritten.

Nur die geordnete Wertetupelrolle gelangt in Distanz und Aktualisierung.
Snapshot-ID, Fensterticks und Clock-ID werden nie Bestandteil eines
Prototypwertes.

## Genau eine Distanzfamilie

PPB-1 verwendet die normalisierte mittlere L1-Distanz zwischen zwei
gleichdimensionalen Wertetupeln:

```text
distance(x, p) = Summe der komponentenweisen Absolutdifferenzen
                 geteilt durch die Anzahl der Komponenten
```

Bei Eingabewerten im Bereich minus eins bis plus eins liegt die Distanz im
geschlossenen Bereich null bis zwei.

Gebundene Eigenschaften:

- identische Tupel besitzen Distanz null;
- Vertauschen der beiden Tupel aendert die Distanz nicht;
- jede Komponente traegt mit demselben Gewicht bei;
- die Dimension veraendert den Wertebereich nicht;
- ungleiche Dimensionen sind ein Validierungsfehler;
- es gibt keine semantischen, modalitaetsfremden oder trainierten Gewichte.

Ein belegter Slot passt genau dann, wenn seine Distanz nicht groesser als der
konfigurierte `match_threshold` ist.

## Deterministische Zuordnung

Fuer einen gueltigen Eingang wird ein Kandidatenschritt auf einer privaten
Kopie des Vorzustands bestimmt:

1. Bankschrittnummer als naechster akzeptierter Schritt festlegen.
2. Vor der Distanzbildung alle faelligen Slots gemaess Vergessensregel auf der
   Kopie freigeben.
3. Distanz zu jedem verbleibenden belegten Slot berechnen.
4. Alle Slots innerhalb der Schwelle bestimmen.
5. Den Slot mit kleinster Distanz waehlen.
6. Bei exakt gleicher Distanz die lexikografisch kleinste Slot-ID waehlen.
7. Ohne Match den lexikografisch kleinsten freien Slot belegen.
8. Ohne Match und freien Slot die gebundene LRU-Ersetzung anwenden.
9. Poststate und Readout vollstaendig validieren.
10. Nur bei vollstaendiger Gueltigkeit atomar committen.

Die Reihenfolge der Slots im Eingabeobjekt darf die Entscheidung nicht
veraendern.

## Prototypbildung und Aktualisierung

Bei `CREATED` oder `REPLACED` werden die Eingabewerte als erster verdichteter
Prototyp des Slots gesetzt. `support_count` beginnt bei eins und
`last_selected_step` wird auf den aktuellen Bankschritt gesetzt.

Bei `MATCHED` wird jede Prototypkomponente durch eine konvexe Mischung aus
altem Prototyp und aktuellem Eingang aktualisiert:

```text
updated = alter Prototypanteil plus aktueller Eingangsanteil
```

Der aktuelle Eingangsanteil ist genau `update_rate`; der alte Anteil ist sein
Komplement. `update_rate` muss groesser als null und hoechstens eins sein.

`support_count` steigt bei jedem Match um eins, aber niemals ueber
`stable_after`. Der Slot gilt ab Erreichen dieser Grenze als stabilisiert.
Diese Saettigung verhindert einen unbegrenzt wachsenden Expositionszaehler.

## Schrittbasiertes Vergessen

Ein belegter Slot ist vor der Matchsuche faellig, wenn der Abstand zwischen
dem neuen Bankschritt und `last_selected_step` mindestens
`expire_after_steps` betraegt.

Ein faelliger Slot wird auf der privaten Arbeitskopie vollstaendig freigegeben:

- `occupied` wird falsch;
- Prototypwerte werden geleert;
- `support_count` und `last_selected_step` werden null;
- kein alter Wert darf im Readout oder in einer spaeteren Distanz erscheinen.

Wird der freigegebene Slot im selben Schritt neu belegt, lautet das Ereignis
`CREATED`, nicht `MATCHED` oder `REPLACED`.

Da Audio und Video getrennte akzeptierte Bankschritte besitzen, kann hohe
Audiorate keinen visuellen Slot altern lassen und umgekehrt.

## Kapazitaetskonflikt und LRU-Ersetzung

Wenn nach der Vergessensphase kein Match und kein freier Slot vorliegt, wird
genau ein Slot ersetzt:

1. kleinstes `last_selected_step` waehlen;
2. bei Gleichstand lexikografisch kleinste Slot-ID waehlen;
3. alten Slotinhalt vollstaendig entfernen;
4. neuen Prototyp wie bei einer Erstanlage setzen;
5. Ereignis `REPLACED` ausgeben.

Stabilisierung schuetzt einen Slot nicht vor LRU-Ersetzung. Damit bleibt die
Konfliktpolitik einfach, transparent und ohne versteckte Prioritaet.

## Atomarer Einzelschritt

Der spaetere reine Referenzkern muss Vorzustand und Eingangsframe als
unveraenderliche Werte behandeln. Er berechnet Poststate und Readout zunaechst
vollstaendig privat.

Ein Commit ist nur zulaessig, wenn:

- Konfiguration, Vorzustand und Eingang gueltig sind;
- Slotanzahl und Slot-IDs exakt der Konfiguration entsprechen;
- alle Prototypwerte endlich und dimensionsrichtig sind;
- Poststate und Readout intern uebereinstimmen;
- alle gebundenen Digests reproduzierbar sind.

Bei jedem Fehler bleiben beide Modalitaetsbanken, Feldkern und aktive Runtime
unveraendert.

## Gebundene synthetische Referenzkonfiguration

Die erste private Testwelt verwendet fuer beide Modalitaeten getrennt:

| Rolle | Referenzwert |
|---|---|
| Kapazitaet | zwei Slots |
| Traegerdimension | vier Werte |
| Matchschwelle | 0,25 |
| Aktualisierungsanteil | 0,50 |
| stabilisiert ab | drei Unterstuetzungen |
| faellig nach | vier akzeptierten Bankschritten Abstand |

Diese Werte gelten nur fuer synthetische Vertragstests. Sie sind keine
Produktionsparameter und keine Feldparameter.

## Gebundene 30-Pfade-Testmatrix

S1-VI registriert die folgenden synthetischen Pfade, fuehrt sie aber nicht
aus.

### Schema und Fail-Closed

| ID | Pfad | Erwartung |
|---|---|---|
| V01 | leere oder doppelte Traeger-ID | Ablehnung ohne Poststate |
| V02 | falsche Modalitaet fuer Bank | Ablehnung; andere Bank unveraendert |
| V03 | falsche Geometrie | Ablehnung ohne Zaehlerfortschritt |
| V04 | ungleiche Traegerreihenfolge | Ablehnung trotz gleicher Wertemenge |
| V05 | NaN, Infinity oder Wert ausserhalb des Bereichs | Ablehnung ohne Teilcommit |
| V06 | nicht fortschreitendes Quellfenster | Ablehnung ohne Zustandsaenderung |
| V07 | fehlerhafte Slotanzahl oder doppelte Slot-ID | Vorzustand ungueltig |
| V08 | belegter Slot mit leerem oder falschem Prototyp | Vorzustand ungueltig |

### Distanz und Zuordnung

| ID | Pfad | Erwartung |
|---|---|---|
| V09 | identische Tupel | Distanz null |
| V10 | Argumentreihenfolge vertauscht | identische Distanz |
| V11 | gleiches mittleres Delta in verschiedener Dimension | dimensionsnormierter gleicher Wert |
| V12 | Distanz genau auf Matchschwelle | Match zulaessig |
| V13 | Distanz knapp ueber Schwelle | kein Match |
| V14 | zwei Slots mit exakt gleicher Distanz | kleinste Slot-ID gewinnt |

### Bildung, Aktualisierung und Stabilisierung

| ID | Pfad | Erwartung |
|---|---|---|
| V15 | erster Eingang in leere Bank | `CREATED` im kleinsten Slot |
| V16 | passender zweiter Eingang | `MATCHED`, konvexe Aktualisierung |
| V17 | dritter passender Eingang | `support_count` erreicht Stabilisierung |
| V18 | weitere Matches | Zaehler bleibt gesaettigt |
| V19 | nicht ausgewaehlter Slot | bitgleich unveraendert |

### Kapazitaet, Vergessen und Wiederverwendung

| ID | Pfad | Erwartung |
|---|---|---|
| V20 | zwei unpassende Muster bei zwei freien Slots | zwei getrennte Prototypen |
| V21 | drittes unpassendes Muster bei voller Bank | LRU-Slot wird `REPLACED` |
| V22 | LRU-Gleichstand | kleinste Slot-ID wird ersetzt |
| V23 | Slot erreicht Faelligkeitsabstand | Freigabe vor Matchsuche |
| V24 | Eingang belegt im selben Schritt faelligen Slot | `CREATED`, kein alter Rest |
| V25 | Audio-Schritte ohne Videoeingang | visueller Alterungsstand unveraendert |

### Reproduzierbarkeit und Grenzen

| ID | Pfad | Erwartung |
|---|---|---|
| V26 | identischer Vorzustand und Eingang zweimal | bitgleicher Poststate und Readoutdigest |
| V27 | Slotobjekte in anderer Lieferreihenfolge | kanonisch identisches Ergebnis |
| V28 | Eingangs-Snapshot-ID und Fensterticks variieren bei gleichen Werten | Prototypwerte bleiben inhaltsgleich |
| V29 | PPB-OFF-Pfad | aktiver Rezeptor-/Feldpfad bitgleich zum Bestand |
| V30 | Importgrenzpruefung | keine PPB-Rolle in `current_api`, Root-Exports oder Feldsnapshot |

## Engineeringbaseline-Matrix

Die spaetere Abnahme muss dieselben synthetischen Eingangsfolgen mindestens
gegen folgende einfachere Module stellen:

| Baseline | Gebundene Vergleichsfrage |
|---|---|
| Replay | speichert PPB-1 nachweislich keine Eingangsfolge oder Rohdaten? |
| ein gleitender Mittelwert | bleiben zwei getrennte wiederkehrende Muster mit zwei Slots unterscheidbar? |
| schneller Nachhall | bleibt der Bankzustand nur bis zur expliziten Schrittfaelligkeit statt nach H-Zeitkonstante erhalten? |
| einfacher Key-Value-Speicher | kann ein nahe gelegener Eingang ohne exakten externen Schluessel zugeordnet werden? |
| feste Prototypliste | sind Aktualisierung, Stabilisierung und Vergessen technisch wirksam und messbar? |

Das Ergebnis darf eine einfachere Baseline bevorzugen. PPB-1 wird dadurch
nicht zum Forschungskandidaten und erhaelt keinen besonderen Claim.

## Stoppbedingungen

Die private Implementierung wird nicht freigegeben, wenn vor ihrem Beginn:

- eine Schemarolle unbestimmt oder redundant ist;
- dieselbe Bank Audio und Video mischen muesste;
- die Distanzfamilie dimensions- oder reihenfolgeabhaengig unkontrolliert ist;
- Gleichstaende, Vergessen oder Ersetzung nicht deterministisch sind;
- ein Prototyp Rohhistorie, Label oder Replayzeiger benoetigt;
- der atomare Fehlerpfad nicht ohne Feld- oder Snapshotaenderung darstellbar
  ist;
- die 30 Pfade nicht vollstaendig aus dem Vertrag ableitbar sind.

## Verbindlicher Vertragsstand

```text
S1_VI_PRIVATE_SCHEMA_FAMILY_BOUND
S1_VI_SEPARATE_AUDITORY_VISUAL_BANK_STATES_BOUND
S1_VI_NORMALIZED_MEAN_L1_DISTANCE_BOUND
S1_VI_LOWEST_SLOT_TIE_BREAK_BOUND
S1_VI_CONVEX_PROTOTYPE_UPDATE_BOUND
S1_VI_SATURATING_STABILITY_COUNT_BOUND
S1_VI_ACCEPTED_BANK_STEP_FORGETTING_BOUND
S1_VI_LRU_REPLACEMENT_BOUND
S1_VI_ATOMIC_FAIL_CLOSED_STEP_BOUND
S1_VI_SYNTHETIC_30_PATH_MATRIX_BOUND_NOT_RUN
S1_VI_PRIVATE_IMPLEMENTATION_SURFACE_STATICALLY_ADMISSIBLE
S1_VI_NO_FIELD_API_SNAPSHOT_OR_SEMANTIC_INTEGRATION
S1_VI_NO_MEMORY_OR_ENDOGENOUS_FIELD_CAUSE_FINDING
```

## Genau ein naechster Schritt

Der einzige zulaessige Anschluss ist:

```text
S1-VJ - privater reiner PPB-1-Referenzkern und synthetische
        30-Pfade-Vertragsabnahme
```

S1-VJ darf ausschliesslich implementieren:

- private unveraenderliche Config-, Slot-, Bankstate- und Readoutrollen;
- normalisierte mittlere L1-Distanz;
- genau einen atomaren modalitaetseigenen Bankschritt;
- kanonische Digests;
- die gebundenen synthetischen Vertragstests V01 bis V30.

Nicht zulaessig bleiben Feldintegration, Adapter, `current_api`, Root-Export,
Snapshotumbau, reale Audio-/Videoausfuehrung und Semantik.

## Projektgrundlagen

- [S1-VH statischer PPB-1-Engineeringvertrag](S1VH_PPB1_STATISCHER_ENGINEERING_FUNKTIONS_SICHERHEITS_UND_INTEGRATIONSVERTRAG.md)
- [Aktiver Rezeptorvertrag](../mcm_field_organism/receptor_contract.py)
- [Aktiver Audio-Video-Feldpfad](../mcm_field_organism/audio_video_neutral_field_runtime.py)
- [Aktivkern-Konsolidierungsabschluss](S1UZ_STATISCHER_ABSCHLUSSAUDIT_AKTIVKERN_KONSOLIDIERUNG.md)
