# S2-MG: Vorversiegelter Korpus fuer slotgebundene Anwendbarkeit

## Status

`S2MG_CORPUS_PRESEALED_AWAITING_RECEPTOR_PPB_MATERIALIZATION`

S2-MG materialisiert genau einen neuen neutralen Quellenkorpus fuer den
entscheidenden S2-ME-Starttest. Die Quellen wurden vor jeder Rezeptor-,
Distanz- oder PPB-Auswertung erzeugt und versiegelt. Es wurden keine
Rezeptor-, PPB-, Memory-, Kontext- oder Feldfunktionen aufgerufen.

Die Versiegelung ist kein positiver Lernbefund und keine
Implementierungsfreigabe. Sie friert Quellen, Ereignisfolge, Train-/Holdout-
Trennung, Generationsdigest-Schema und Artefaktgrenzen ein, bevor die reale
PPB-Zuordnung bekannt ist.

## Einmalige Planbindung

```text
Plan-ID:
s2mg-slot-applicability-corpus-20260905-01

Quellseed:
s2mg-neutral-source-seed-20260905-v1

Plandigest:
ff2d0f6955e1a8b60d3a4784626b2239c61459c4a75bb12b5f4b972278c50f33

Datei-SHA-256:
02d0834a64a762ad3c9751564d3c650ca7dbe6c6c1e9b6aeb7c171682620ae45

Kanonische Dateigroesse:
34.529 Byte
```

Planartefakt:

```text
reports/s2mg/s2mg-slot-applicability-corpus-20260905-01/presealed-plan.json
```

Der Zielpfad existierte vor der Versiegelung nicht. Das private Gate war vor
dem Aufruf `False`, wurde nur fuer genau einen Aufruf geoeffnet und endete
wieder bei `False`. Ein zweiter Aufruf, neuer Seed, Quellentausch oder Retry
unter dieser Plan-ID ist verboten.

## Generatorbindung

Der Korpus verwendet weiterhin:

- `1920 x 1080` RGB8;
- Hintergrundwert `32`;
- die vorhandenen Generatorarten `FOUR_SQUARES`, `FILLED_DIAMOND`,
  `SQUARE_RING`, `DIAGONAL_BAND` und `OFFSET_BARS`;
- dieselbe rastergenaue Integererzeugung wie S2-LZ;
- dieselben zwei disjunkten, koordinatengebundenen 96er-Masken und dieselbe
  192er-Vereinigung.

Die vier Trainings- und zwei Holdout-Transformationen wurden gegenueber
S2-LZ nicht verkleinert oder an eine Memorygrenze angepasst:

```text
Training:
(  0,    0, size=120, foreground=224)
(-180,   0, size=120, foreground=224)
( 180,   0, size=120, foreground=224)
(  0,    0, size=140, foreground=224)

Holdout:
(  0, -140, size=120, foreground=224)
(  0,  140, size=120, foreground=176)
```

Der neue Seed waehlt ohne Rezeptor- oder Distanzkenntnis genau zwei
Grundlayouts aus einem literal gebundenen Pool. Die versiegelten Layouts
lauten:

```text
Layout 1:
(-260,-160), (140,-220), (-120,220), (260,140)

Layout 2:
(-220,-240), (220,-120), (-260,120), (160,240)
```

Der Pooldigest lautet:

```text
3f30f7cc153f237d81fbdc886ebd9677ca9e156525eb7950bb77558a5ff016b3
```

## Quelleninventar

Der Plan bindet genau `27` Quellenpayloads:

- `8` Trainingsvarianten, vier pro Evaluationsfamilie;
- `4` vollstaendig zurueckgehaltene Varianten;
- `4` unbekannte Formen;
- `2` Zwischenformen;
- `9` unabhaengige Druckquellen.

Alle `27` RGB8-Payloaddigests sind untereinander eindeutig. Kein Digest
ueberlappt mit den `32` Quellenpayloads des historischen S2-LZ-Korpus.
Rohpixel befinden sich nicht im Plan; gebunden sind nur Rezept,
Payload-SHA-256, Byteanzahl, RGB-Summe und technischer Quelldigest.

Die fachlichen Gruppen stehen ausschliesslich in `evaluation_root`. In
`execution_root` kommen weder `family`, `holdout`, `model`, `target` noch
erwartete Entscheidungen vor.

## Literale Formationseventfolge

Die Ausfuehrungswurzel bindet genau folgende `19` neutralen
Vollformationen:

```text
event-001 input-001
event-002 input-007
event-003 input-002
event-004 input-008
event-005 input-003
event-006 input-009
event-007 input-004
event-008 input-010
event-009 input-001
event-010 input-007
event-011 input-019
event-012 input-020
event-013 input-021
event-014 input-022
event-015 input-023
event-016 input-024
event-017 input-025
event-018 input-026
event-019 input-027
```

`event-009` und `event-010` sind zeitlich neue Formationsevents mit bereits
versiegeltem, wiederholtem Wahrnehmungsinhalt. Sie materialisieren
prospektiv den fuenften FIFO-Zugriff, falls die jeweils ersten vier
Varianten real derselben PPB-Slotgeneration zugeordnet wurden.

Die neun anschliessenden Quellen sind keine zugesicherten PPB-Ersetzungen.
Sie stellen nur den vorab gebundenen Druckpfad bereit. Ob und welche
`REPLACED`-Uebergaenge tatsaechlich entstehen, entscheidet ausschliesslich
der unveraenderte PPB-Kern.

## Spaetere Zwei-Blick-Faelle

Der Plan bindet `12` Faelle mit je zwei Blickrollen:

- vier zurueckgehaltene bekannte Varianten;
- vier unbekannte Formen;
- zwei Zwischenformen;
- zwei quellenunvereinbare Blickpaare.

Die Masken, Quellen, Payloaddigests, Fallplandigests und maximale
Vorwaertszeit sind bereits gebunden. Diese Faelle sind keine
Formationsevents und duerfen die Slot- oder Huellevidenz spaeter weder
erweitern noch korrigieren.

## Slotgenerationsdigest

Der Plan bindet `s2me.slot-generation.v1` mit genau diesen kanonischen
Feldern:

```text
schema
bank_id
bank_config_digest
slot_id
creation_event
ppb_prestate_digest
ppb_input_digest
ppb_transition_result_digest
ppb_poststate_digest
accepted_step
```

`creation_event` ist ausschliesslich `CREATED` oder `REPLACED`. Der Digest
wird als SHA-256 der kanonischen Form ohne Digestfeld gebildet.

Evidenz-, Eintrags-, Zentroid-, Radius- und Zukunftsdigests sind als Eltern
des Generationsdigests verboten. Damit entsteht die Slotgeneration allein
aus PPB-Erzeugungsereignis, Slot, Prestate, Eingang, Konfiguration und
Transition. Ein `MATCHED`-Ereignis uebernimmt den bestehenden
Generationsdigest und darf keinen neuen erzeugen.

## Kanonische Formen und Groessen

Der Plan bindet ASCII-JSON mit sortierten Schluesseln, kompakten Trennern und
verbotenen NaN-/Infinitywerten. Zusaetzliche Grenzen:

| Rolle | Maximale kanonische Groesse |
| --- | ---: |
| `AssignedFormEvidenceV1` | `8.192` Byte |
| `SlotApplicabilityEvidenceV1` mit hoechstens vier Eintraegen | `40.960` Byte |
| `LearnedSlotEnvelopeV1` | `12.288` Byte |
| Formationreceipt | `12.288` Byte |
| Fehlerreceipt | `4.096` Byte |
| gesamter privater erweiterter Memoryzustand | `262.144` Byte |
| vorversiegelter Plan | `262.144` Byte |

Weiter gebunden sind:

- technische IDs: `[a-z][a-z0-9-]{7,95}`, maximal `96` ASCII-Byte;
- Digests: exakt `64` ASCII-Byte;
- PPB-Schritte: maximal `UINT32_MAX`;
- Quellticks: maximal `UINT64_MAX`;
- kanonischer Floattoken: maximal `32` ASCII-Byte;
- Deskriptor: exakt `144` endliche nichtnegative Binary64-Werte;
- FIFO: hoechstens vier Eintraege pro Slot und vier visuelle Slots.

Die Datentypen binden ihre vollstaendigen Feldlisten im
`slot_evidence_schema_root` des Plans. Receipts enthalten nur Zustands-,
Uebergangs-, Eintrags- und Ergebnisdigests; sie duplizieren weder Rohpixel
noch vollstaendige Rezeptor- oder Memoryobjekte.

Der Schema-Contract-Digest lautet:

```text
361c1894a0eca13344078a9f242e30e7fcd26787106337884056a2b86cd97684
```

## Atomare Grenze

Die spaetere S2-ME-Formation darf erst einen kombinierten Memorypoststate
publizieren, wenn bestehende B4-/TSPM-Formation und zugehoerige
Slot-Evidenzfortschreibung gemeinsam validiert sind. Ein Evidenzfehler laesst
den sichtbaren Memoryzustand beim vollstaendigen Prestate.

Der Feldzweig bleibt unabhaengig. Ein bereits gueltiger Feldkontakt wird bei
einem Memory- oder Evidenzfehler weder geloescht noch zurueckgerollt.

Bei `REPLACED` beginnt eine neue Generationsidentitaet. Der aktuelle
Memoryzustand darf danach weder Eintrags-, Evidenz- noch Huelledigests der
alten Generation referenzieren. Historische technische Receipts duerfen
deren frueheren Zustandsdigest behalten, aber keine alte Evidenz als aktuellen
Kandidaten bereitstellen.

## Offener harter Entscheidungspunkt

S2-MG hat bewusst keine Distanz und keinen PPB-Uebergang berechnet. Die
Ausfuehrungswurzel dokumentiert:

```text
receptor_calls = 0
distance_calls = 0
ppb_calls = 0
memory_calls = 0
context_calls = 0
field_calls = 0
```

Als naechster Schritt ist genau eine Rezeptor- und unveraenderte
PPB-Materialisierung dieses exakten Plandigests zulaessig. Vor dem ersten
Aufruf muessen Planfilehash, Plandigest und alle 27 Payload-Digests erneut
stimmen.

Eine S2-ME-Implementierung ist nur zulaessig, wenn mindestens eine
Slotgeneration folgende reale Folge besitzt:

```text
CREATED -> MATCHED -> MATCHED
```

und dabei mindestens zwei unterschiedliche 288-Werte-Rezeptordigests sowie
zwei unterschiedliche 144-Werte-Formdeskriptordigests gebunden sind.

Verteilen sich die Varianten auf mehrere Slots, lautet der terminale Befund:

```text
S2ME_SLOT_APPLICABILITY_HISTORY_NOT_MATERIALIZABLE
```

Danach sind fuer diese Variationsklasse kein neuer Seed, keine andere
Quelle, keine Umordnung, kein Retry und keine Schwellenanpassung zulaessig.

## Aussagegrenze

S2-MG bestaetigt ausschliesslich die nichtzirkulaere Vorversiegelung. Es
behauptet weder eine gemeinsame PPB-Slotgeneration noch eine gelernte
Anwendbarkeitshuelle. Adapter, Baseline, Runtime und S2-MD bleiben gesperrt.

MD-B02 und MD-B03 bleiben unangetastet. Die README wird nicht erweitert.

## Gebundener Implementierungsstand

Das Korpusmodul besitzt vor dem Commit folgenden SHA-256:

```text
3ed54b65d6eea6d72c5b03b883d25c884ff29fa7482c6451aa8d9a491993a639
```
