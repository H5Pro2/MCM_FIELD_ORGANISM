# W7-V: Vertrag der additiven symmetrischen Quellenfamilie

## Entscheidung

`ADDITIVE_SYMMETRIC_SOURCE_FAMILY_CONTRACT_BOUND`

W7-V bindet statisch die in W7-U gefundene minimale Quellenerganzung. Der
Vertrag erzeugt noch keine Sequenzen, berechnet keine neuen Digests und
startet keine Pfadmatrix.

## 1. Unveraenderter Bestand

Folgende W7-M-/K2-B-Quellen bleiben byte- und digestgleich:

- A-Praefix `contact_a` auf 0 bis 4;
- vier B-Fortsetzungsschritte `contact_b_steps` auf 4 bis 8;
- vier Unterbrechungsschritte `interruption_steps` auf 4 bis 8;
- fuenf Proben `probes` fuer Checkpoint 0 bis 4;
- alle zugehoerigen vorhandenen Quelldigests;
- W7-M-Matrix- und Regionsdigest.

Die additive Familie ersetzt, verschiebt oder ueberschreibt keinen dieser
Werte.

## 2. Additive Identitaeten

Die neue technische Familie muss genau folgende Rollen besitzen:

```text
family_id = w7v.symmetric-path-source-family.v1

b_prefix_steps_id = w7v.contact-b-prefix.steps.v1
b_prefix_id       = w7v.contact-b-prefix.combined.v1

a_continuation_steps_id = w7v.contact-a-continuation.steps.v1
```

Die Rollen enthalten keine Bedeutung, Klasse, Belohnung oder Zielvorgabe.
A und B sind nur bereits eingefrorene technische Weltkontaktidentitaeten.

## 3. B-Praefix

Der B-Praefix wird ausschliesslich aus `changed.phases[2]` der vorhandenen
kontrollierten Holdout-Weltfamilie erzeugt. Die vorhandene `_phase_steps`-
Mechanik wird gebunden mit:

```text
world_id = w7v.contact-b-prefix
start_second = 0
repetitions = 4
clock_id = organism.mcm_f3_k2b
ticks_per_second = 1_000_000
```

Erforderlich sind:

- vier einzelne B-Praefixschritte auf 0-1, 1-2, 2-3 und 3-4;
- vier Einzelschrittdigests;
- eine verlustfreie Kombination in unveraenderter Modalitaetsreihenfolge;
- ein eigener kombinierter B-Praefixdigest.

Der kombinierte B-Praefix darf nicht aus den vorhandenen B-Schritten durch
blosse Ticksubtraktion erzeugt werden.

## 4. A-Fortsetzung

Die A-Fortsetzung wird ausschliesslich aus `same.phases[0]` erzeugt. Die
vorhandene `_phase_steps`-Mechanik wird gebunden mit:

```text
world_id = w7v.contact-a-continuation
start_second = 4
repetitions = 4
clock_id = organism.mcm_f3_k2b
ticks_per_second = 1_000_000
```

Erforderlich sind vier einzelne A-Schritte auf 4-5, 5-6, 6-7 und 7-8 sowie
vier vorab gebundene Einzelschrittdigests. Eine kombinierte A-Fortsetzung ist
fuer die Siebenpfadmatrix nicht erforderlich und darf nicht als zusaetzliche
Rolle eingefuehrt werden.

## 5. Supportvertrag

Supportgleichheit bedeutet keine Gleichheit der Rezeptorwerte. Geprueft
werden ausschliesslich technische Traeger- und Zeitrollen.

### 5.1 Praefixsymmetrie

Der vorhandene A-Praefix und der additive B-Praefix muessen uebereinstimmen
in:

- Organismusintervall 0 bis 4;
- Modalitaets- und Geometrie-IDs;
- Carrierinventar je Modalitaet;
- Anzahl der vier Einsekundenschritte;
- Audio-/Video-Framezahl je Schritt und insgesamt;
- geordneter Folge aller Abschlussgrenzen;
- Uhr und Tickrate.

### 5.2 Fortsetzungssymmetrie

Die vorhandenen B-Fortsetzungsschritte und die additiven A-
Fortsetzungsschritte muessen uebereinstimmen in:

- den Intervallen 4-5, 5-6, 6-7 und 7-8;
- Modalitaets-, Geometrie- und Carrierrollen;
- Audio-/Video-Framezahl pro korrespondierendem Schritt;
- geordneter Folge relativer Abschlussabstaende innerhalb jedes Schritts;
- Uhr und Tickrate.

Snapshot- und Welt-IDs muessen zwischen A und B verschieden bleiben. Eine
Supportpruefung darf Werte weder angleichen noch normalisieren.

## 6. Additiver Inventarvertrag

Die spaetere unveraenderliche Datenstruktur muss mindestens enthalten:

- `family_id`;
- bestehenden W7-M-Matrix- und Regionsdigest;
- Digest des vollstaendigen vorhandenen K2-B-Quelleninventars;
- vier B-Praefixschritte und ihre Digests;
- kombinierten B-Praefix und dessen Digest;
- vier A-Fortsetzungsschritte und ihre Digests;
- Uhr und Tickrate;
- `prefix_support_matches`;
- `continuation_support_matches`;
- kanonischen `symmetric_inventory_digest`.

Der Inventardigest bindet sowohl die vorhandenen Quelldigests als auch alle
neuen Digests und Supportkontrollen. Er darf keine Modellresultate,
Observerwerte oder Pfadentscheidungen enthalten.

## 7. Vollstaendige Pfadbelegung

Nach technisch bestandener Implementierung ist nur folgende Belegung
zulaessig:

| Pfad | Praefix 0-4 | Fortsetzung 4-8 | Probe |
| --- | --- | --- | --- |
| `AB` | vorhandenes A | vorhandene B-Schritte | vorhandene P0-P4 |
| `AG` | vorhandenes A | vorhandene G-Schritte | vorhandene P0-P4 |
| `UB` | uniform bei 4 | vorhandene B-Schritte | vorhandene P0-P4 |
| `UG` | uniform bei 4 | vorhandene G-Schritte | vorhandene P0-P4 |
| `BA` | additives B | additive A-Schritte | vorhandene P0-P4 |
| `BG` | additives B | vorhandene G-Schritte | vorhandene P0-P4 |
| `UA` | uniform bei 4 | additive A-Schritte | vorhandene P0-P4 |

Checkpointproben laufen immer auf Zustandskopien. Sie duerfen den
Fortsetzungspfad, P0-Zustand, Observerzustand oder spaeteren Modellzustand
nicht veraendern.

## 8. Explizite W7-R-Zulassung

W7-R akzeptiert derzeit nur Digests aus dem vorhandenen W7-M-Quellenobjekt.
Eine spaetere Implementierung darf diese Grenze nur additiv erweitern.

Erforderlich ist ein unveraenderlicher Autorisierungsvertrag mit:

- W7-M-Matrixdigest;
- vorhandenem Quelleninventardigest;
- `symmetric_inventory_digest`;
- exakt den vier B-Praefixschrittdigests, dem kombinierten B-Praefixdigest
  und den vier A-Fortsetzungsschrittdigests;
- erlaubter technischer Rollenkennung je Digest.

W7-R darf einen additiven Digest nur akzeptieren, wenn der Vertrag explizit
uebergeben wird, alle drei Bindungen stimmen und der uebergebene
Sequenzdigest exakt passt. Ohne Vertrag bleibt das heutige Verhalten
unveraendert. Die Autorisierung wird nicht in `current_api` exportiert.

## 9. Pflichtkontrollen

Eine spaetere Implementierung muss mindestens pruefen:

- deterministischen Wiederaufbau aller neuen Sequenzen und Digests;
- vier B-Praefix- und vier A-Fortsetzungsschritte;
- exakte Intervallgrenzen;
- Praefix- und Fortsetzungssupportgleichheit;
- verlustfreie Kombination des B-Praefixes;
- unveraenderte vorhandene Quelldigests;
- unveraenderten W7-M-Matrix- und Regionsdigest;
- vollstaendige und eindeutige Siebenpfadbelegung;
- Ablehnung unbekannter, falsch gerollter oder falsch gebundener Digests;
- fehlende Exporte aus `__init__` und `current_api`;
- keine Reports, Browserstarts oder Forschungslaufmarker.

## 10. Harte Stopplinien

Die Implementierung muss stoppen, wenn:

- vorhandene W7-M-/K2-B-Sequenzen oder Digests veraendert werden;
- B-Praefix oder A-Fortsetzung aus nachtraeglich verschobenen Objekten ohne
  neue Reduktion entstehen;
- Supportgleichheit aus Rezeptorwertgleichheit statt Traeger- und Zeitrollen
  abgeleitet wird;
- A- und B-Werte angeglichen, normalisiert oder nach Resultaten angepasst
  werden;
- mehr als die zwei erforderlichen additiven Quellenrollen entstehen;
- der Inventardigest Modell- oder Observerresultate enthaelt;
- W7-R additive Digests ohne expliziten Autorisierungsvertrag akzeptiert;
- eine Hauptmatrix vor bestandener Quellen- und Autorisierungsabnahme startet.

## 11. Aussagegrenze

W7-V ist nur ein statischer Quellenvertrag. Es wurden keine neuen Sequenzen
oder Digests erzeugt. Vollstaendige Pfadbelegbarkeit ist daher noch nicht
technisch nachgewiesen. Daraus folgen keine Feldfunktion, kein Memory, keine
Ressourcenwiederverwendung, keine Feldzeit, Organisation, Semantik,
Selbstregulation oder KI.

## 12. Verwendete Quellen

- `docs/W7U_AUDIT_SYMMETRISCHE_PFADQUELLEN_SUFFIZIENZ.md`
- `mcm_field_organism/mcm_f3_k2b_source.py`
- `mcm_field_organism/controlled_audio_video_test_world.py`
- `mcm_field_organism/mcm_f3_controlled_history_source.py`
- `mcm_field_organism/w7m_capacity_function_matrix.py`
- `mcm_field_organism/w7r_p0_s_completion_producer.py`

## 13. Naechster Schritt

W7-W darf die additive symmetrische Quellenfamilie, ihren Inventardigest,
Supporttests und den engen optionalen W7-R-Autorisierungsvertrag
implementieren. Noch keine Pfadmatrix, kein Browser, Report oder
Forschungslauf.
