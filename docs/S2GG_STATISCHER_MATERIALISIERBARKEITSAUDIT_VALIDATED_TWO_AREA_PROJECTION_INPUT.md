# S2-GG: Materialisierbarkeitsaudit des kombinierten Eingangs

## Auftrag

S2-GG prueft rein statisch, ob der in S2-GF gebundene
`ValidatedTwoAreaProjectionInput` aus den bestehenden S2-GC- und
S2-FS-Artefakten eindeutig, quellgebunden und nichtzirkulaer materialisiert
werden kann.

Es wurden keine Dateien der Implementierung geaendert, keine Tests angelegt,
keine Funktionen aufgerufen und keine Speicher- oder Feldzustaende gelesen.

## Gebundener Stand

Technischer Ausgangsstand:

`05691296ff4ed4e3620d57fe3840d4588b23b9c5`

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| S2-GC-Bundle | `tools/_s2gb_private_perceptual_context_bundle.py` | `0fba7b0323fe772c481eb5261b9640e4a5b00d7da3ceb1a7e0f81c6d9f54bf49` |
| S2-FS-read-only-Finding | `tools/_s2fs_b4_tspm1_private_coordinator.py` | `95ee05ccc0eeb14abbcda036971da5c33ac79363dd546789f4878aace5677db0` |
| Korrekturvertrag | `docs/S2GF_STATISCHER_VERTRAG_VALIDATED_TWO_AREA_PROJECTION_INPUT.md` | `b482a1e2784359cf076ee141c4a502b03630a61d121ee01e99df014741549df0` |

## Ergebnisuebersicht

| Prueffeld | Ergebnis |
| --- | --- |
| S2-GC-Bundlefelder fuer oeffentliche Kandidaten | bestanden |
| S2-FS-Felder fuer instabile Slotwerte und Support | vorhanden |
| gemeinsame Composite- und Probendigestbindung | vorhanden |
| prospektiver atomarer Einmal-Owner | materialisierbar |
| endliche Kandidaten- und Slotgrenzen | vorhanden |
| vollstaendige Bindung instabiler Distanz und Stabilitaet | nicht bestanden |
| eindeutige historische Bundle-/Finding-Paarung | nicht bestanden |
| expliziter Fast-Zustandsdigest in beiden Artefakten | nicht vorhanden |
| vollstaendig azyklischer neuer Digestplan | statisch moeglich, aber wegen fehlender Eingangsnachweise nicht ausreichend |

Gesamtergebnis:

`FAIL_S2GG_COMBINED_INPUT_NOT_MATERIALIZABLE_FROM_EXISTING_ARTIFACTS`

## Vorhandene und nutzbare Felder

### Bundle

Das `PerceptualContextBundle` enthaelt die fuer die oeffentliche A/B-Abbildung
notwendigen Felder:

- Konfigurations-, Composite-Zustands-, Probe-, Quellen- und Bundledigest;
- genau drei Rollenfindings;
- vorhandene B4-, Fast- und stabile Slow-Kandidaten;
- getrennten B4-Folgenbefund;
- identische Vor- und Nachzustandsdigests;
- Ressourcenledger und `automatic_selection = None`.

Damit kann das Bundle weiterhin alleinige Autoritaet fuer oeffentliche
Kandidaten, Verfuegbarkeit und A/B-Zuordnung sein.

### S2-FS-Finding

Die beiden `SlowBankFinding` enthalten je belegtem Slot nominell:

- `slot_id` und `slot_digest`;
- `prototype_values`;
- `support_count`;
- `last_selected_step`;
- `stable`;
- `native_distance`.

Die instabile Support-`1`-Evidenz ist damit als Python-Datenfeld vorhanden.
Die beiden Bankfindings besitzen ausserdem Modalitaet, Bankidentitaet,
Bankzustandsdigest und endliche Slotlisten.

Das Vorhandensein eines Feldes genuegt jedoch nicht. Fuer den kombinierten
Eingang muss sein Wert eindeutig an den validierten Ursprungsbefund gebunden
und bei erneuter Annahme fail-closed pruefbar sein.

## Bestandene Zuordnungen

Folgende Beziehungen sind statisch eindeutig herstellbar:

1. Bundle und Finding tragen denselben Composite-Zustandsdigest.
2. Beide tragen denselben Probendigest.
3. Der Bundle-Projektionsbinding kann Konfiguration, Quelle, Geometrie,
   Clock, Zeitfenster und Probe-Wertedigest binden.
4. Das B4-Finding traegt den Probe-Wertedigest und den B4-Zustandsdigest.
5. Stabile Bundlekomponenten koennen anhand von Modalitaet, Bank, Slot,
   Werten, Support, Distanz und abgeleitetem Komponentenquelldigest mit dem
   S2-FS-Finding verglichen werden.
6. Ein neuer Owner kann prospektiv genau eine konkrete Belegpaarung
   autorisieren und atomar verbrauchen.
7. B4, Fast und beide Slow-Baenke besitzen endliche, bestehende
   Kapazitaetsgrenzen.

Die Gleichheit des Composite-Zustandsdigests bindet die verwendete
Konfiguration und den gesamten TSPM-Zustand indirekt. Sie ersetzt aber keinen
fehlenden expliziten Fast-Zustandsdigest, wenn dieser als eigener
Abnahmewert verlangt wird.

## Materialisierungsblocker

### `GG-B01`: Findingdigest bindet instabile Slotliste nicht

`B4TSPM1ReadOnlyFinding.payload_without_digest()` bindet fuer Slow nur:

```text
tspm_slow_bank_digests = [auditory_bank_digest, visual_bank_digest]
```

Die im `SlowBankFinding` enthaltenen Slotobjekte beziehungsweise ihre
Slotdigests werden nicht in den `finding_digest` aufgenommen. Das
`SlowBankFinding` besitzt selbst keinen eigenen Findingdigest und keine
`__post_init__`-Abnahme.

Damit kann aus dem vorhandenen Top-Level-Digest nicht nachgewiesen werden,
dass genau die uebergebene instabile Slotliste zum urspruenglich validierten
Finding gehoert.

### `GG-B02`: Instabile Distanz ist nicht digestgebunden

Der `slot_digest` eines PPB-1-Prototyps bindet:

- Slotidentitaet;
- Belegung;
- Prototypwerte;
- Support;
- letzten Auswahlschritt.

Er bindet nicht die spaeter berechnete `native_distance`. Auch der
S2-FS-`finding_digest` bindet diese Distanz nicht.

Eine unabhaengige Neuberechnung waere nur mit den tatsaechlichen
Probevektoren moeglich. Der kombinierte Bestand traegt jedoch nur deren
Digest, nicht die acht auditiven und 18 visuellen Probevektorwerte. Deshalb
ist die instabile Distanz weder direkt belegt noch aus den zugelassenen
Artefakten pruefbar.

### `GG-B03`: Stabilitaetsentscheidung ist nicht unabhaengig pruefbar

Der instabile Slot besitzt ein Boolfeld `stable`, aber sein Slotdigest bindet
dieses Feld nicht. Die Stabilitaet wird aus `support_count >= stable_after`
abgeleitet.

Der konkrete `stable_after`-Wert befindet sich in der PPB-Konfiguration. Das
Bundle und das S2-FS-Finding tragen fuer diese Pruefung nur Digests und keinen
materialisierten Konfigurationswert. Ohne zusaetzliche Konfigurationsquelle
kann der kombinierte Eingang nicht nachweisen, ob ein Support in dieser Bank
tatsaechlich stabil oder instabil ist.

### `GG-B04`: Bundle bindet den urspruenglichen Findingdigest nicht

Das `PerceptualContextBundle` bindet Rollenfinding-, Sequenz-, Ledger-,
Quellen- und Zustandsdigests. Es speichert nicht den
`B4TSPM1ReadOnlyFinding.finding_digest`, aus dem es erzeugt wurde.

Die oeffentlichen Bundlewerte koennen mit einem Finding verglichen werden.
Instabile Slow-Slots beeinflussen diese oeffentlichen Werte aber gerade
nicht. Mehrere Findings mit gleich dargestellten oeffentlichen Kandidaten,
aber unterschiedlich behaupteter instabiler Sidecar-Evidenz koennten daher
dasselbe Bundle erfuellen. Ein neuer `relation_digest` wuerde nur die jetzt
vorgelegte Paarung binden, nicht beweisen, dass genau dieses Finding die
historische Bundlequelle war.

### `GG-B05`: Expliziter Fast-Zustandsdigest fehlt

Das Bundle traegt fuer einen vorhandenen Fast-Kandidaten einen aus dem
Fast-Slotdigest abgeleiteten Komponentenquelldigest. Das S2-FS-Finding traegt
ebenfalls nur den ausgewaehlten Fast-Slotdigest. Keines der beiden Artefakte
legt den vollstaendigen Fast-Zustandsdigest separat offen.

Der gemeinsame Composite-Zustandsdigest bindet den Fast-Zustand indirekt,
aber der in S2-GF verlangte explizite Vergleich eines eigenen
Fast-Zustandsdigests ist aus den beiden konkreten Datentypen nicht
materialisierbar.

## Owner- und Nichtzirkularitaetsbefund

Der neue Owner ist materialisierbar, wenn er erst nach Vorlage aller
Eingangsbelege entsteht und vor jeder Validierung exakt Bundle-, Finding-,
Quellenrelations- und Sequenzevidenzdigest autorisiert. Sein eigener
Vorzustandsdigest kann ohne Resultatdigest gebildet werden; der terminale
Nachzustand bindet anschliessend den validierten Eingangs- oder Fehlerdigest.

Der in S2-GF definierte Digestgraph ist damit azyklisch konstruierbar:

```text
bestehende Quelldigests
-> Owner-Vorzustand
-> Relationsdigest
-> Ressourcenledger
-> validierter Eingang
-> Owner-Nachzustand
```

Diese Nichtzirkularitaet behebt die Blocker `GG-B01` bis `GG-B05` nicht. Ein
neuer Digest kann fehlende historische Herkunft oder nicht pruefbare Werte
nicht rueckwirkend erzeugen.

## Ressourcenbefund

Die bestehenden Obergrenzen sind endlich:

- maximal neun B4-Referenzen;
- maximal ein oeffentlicher B4-Kandidat;
- maximal ein oeffentlicher Fast-Kandidat;
- maximal zwei oeffentliche stabile Slow-Komponenten;
- endliche auditive und visuelle PPB-Slotmengen aus der gebundenen
  Konfiguration;
- keine neue Memory-Kapazitaet im kombinierten Eingang.

Ein spaeteres Ledger waere zaehlbar. Wegen der fehlenden Belegbindungen darf
dieser positive Ressourcenbefund nicht als Gesamtfreigabe verwendet werden.

## Erforderliche technische Grundlage fuer eine spaetere Wiederaufnahme

S2-GE darf erst erneut geoeffnet werden, wenn ein prospektiv erzeugter
read-only Detailbeleg mindestens kanonisch bindet:

1. den vollstaendigen S2-FS-Findingdigest;
2. die Slotdigests aller belegten Slow-Slots je Modalitaet;
3. die konkreten Probevektorwerte oder einen bereits validierten
   Distanzbeleg je Slot;
4. den materialisierten `stable_after`-Wert und zugehoerigen
   Konfigurationsdigest;
5. die Stabilitaetsentscheidung jedes Slots;
6. den expliziten Fast-Zustandsdigest, falls dieser weiterhin einzeln
   gefordert wird;
7. den Digest dieses Detailbelegs im spaeter erzeugten Bundle oder in einem
   gleichzeitig atomar erzeugten Paarreceipt.

Eine solche Grundlage muss bei der read-only Erzeugung prospektiv entstehen.
Sie darf nicht nachtraeglich aus S2-FZ-Erwartungen, Recorderdateien oder
Fixture-Labels rekonstruiert werden. Das bestehende S2-GC-Bundle darf dabei
nicht still veraendert oder rueckwirkend neu qualifiziert werden.

## Entscheidung

Mindestens ein erforderlicher Wert beziehungsweise Herkunftsnachweis fehlt in
den bestehenden Artefakten. Nach der ausdruecklichen S2-GG-Regel bleibt S2-GE
daher gesperrt.

Status:

`FAIL_S2GG_COMBINED_INPUT_NOT_MATERIALIZABLE_FROM_EXISTING_ARTIFACTS`

Nicht freigegeben sind A/B-Projektionscode, die 14 Tests, ein Testaufruf,
neue Speicherabfragen, Kontextverwendung und Feldintegration.
