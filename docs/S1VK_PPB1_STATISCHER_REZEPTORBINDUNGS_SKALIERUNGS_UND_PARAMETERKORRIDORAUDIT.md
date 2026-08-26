# S1-VK: PPB-1 statischer Rezeptorbindungs-, Skalierungs- und Parameterkorridoraudit

## Freigabe und Grenze

S1-VK prueft den in S1-VJ abgenommenen privaten PPB-1-Referenzkern statisch
gegen die vorhandenen auditiven und visuellen Rezeptorgeometrien. Gebunden
werden nur:

- vorhandene Geometrie- und Traegerprofile;
- direkte private Bindbarkeit an `ReceptorContactFrame`;
- logische Speicher- und Distanzbudgets;
- getrennte Audio- und Video-Parameterkorridore;
- Stopp- und Skalierungsgrenzen vor jedem groesseren privaten Schritt.

S1-VK implementiert keinen Profilbinder, fuehrt keinen Test und keinen
Audio-/Videolauf aus und veraendert weder Feldkern, Runtime, `current_api`
noch Snapshot.

## Vorhandene Rezeptorbindung

Der aktive Rezeptorvertrag liefert PPB-1 bereits alle benoetigten Rollen:

- `modality_id`;
- `geometry_id`;
- geordnete `carrier_ids`;
- normalisierte reduzierte `values`;
- technische Quellclock und geordnetes Fensterende.

`from_auditory_receptor_state` und `from_visual_receptor_state` erzeugen
vollstaendige `ReceptorContactFrame`-Werte ohne Audio-Samples oder Bildframes.
PPB-1 muss deshalb keinen Rohmedienadapter und keine neue
Rezeptortransformation einfuehren.

Die vorhandenen technischen Kennungen entsprechen der privaten
PPB-1-Identifiergrenze. Die Traegerreihenfolge wird von den Rezeptoren fest
erzeugt und vom PPB-Kern exakt validiert.

## Vier vorhandene Geometrieprofile

Der Audit unterscheidet vier bereits im Projekt gebundene Profile. Sie werden
nicht zu einer gemeinsamen Produktionskonfiguration vermischt.

| Profil | Auditive Konfiguration | auditive Traeger | visuelle Konfiguration | visuelle Traeger | gesamt |
|---|---|---:|---|---:|---:|
| Browser-Smoke/-Timing | 8 logarithmische Baender | 8 | Raster 3 mal 2 mal 3 Kanaele | 18 | 26 |
| kontrollierte AV-Testwelt | 12 logarithmische Baender | 12 | Raster 6 mal 4 mal 3 Kanaele | 72 | 84 |
| oeffentlicher AV-Pfad | 48 logarithmische Baender | 48 | Raster 10 mal 8 mal 3 Kanaele | 240 | 288 |
| Standard-/Livepfad | 48 logarithmische Baender | 48 | Raster 12 mal 8 mal 3 Kanaele | 288 | 336 |

Die 336 Traeger des Standard-/Liveprofils stimmen mit dem dokumentierten
realen Audio-Video-Feldkontakt aus 48 auditiven und 288 visuellen Traegern
ueberein.

## Exakte Geometrie-IDs

### Browserprofil

```text
auditory.log8.50-3000.w800.h80.v1
visual.grid3x2.channels3.source120x80.v1
```

### Kontrolliertes Profil

```text
auditory.log12.50-1500.w400.h40.v1
visual.grid6x4.channels3.source24x16.v1
```

### Oeffentliches AV-Profil

```text
auditory.log48.50-18000.w4800.h480.v1
visual.grid10x8.channels3.source320x240.v1
```

### Standard-/Liveprofil

```text
auditory.log48.50-18000.w4800.h480.v1
visual.grid12x8.channels3.source1920x1080.v1
```

Die Geometrie-ID ist Teil der Bankkonfiguration. Ein Zustandswechsel der
Geometrie innerhalb derselben Bank ist fail-closed unzulaessig.

## Wertebereiche

Auditive und visuelle Zustandswerte gelangen ueber den bestehenden
`ReceptorContactFrame` in den gemeinsamen normalisierten Bereich minus eins
bis plus eins. Die heute erzeugten auditiven Energien und visuellen
Kanalmittel liegen technisch nichtnegativ; PPB-1 erweitert oder
reinterpretisiert diesen Inhalt nicht.

Die L1-Distanz bleibt fuer alle vier Profile dimensionsnormalisiert im
gleichen Bereich null bis zwei. Daraus folgt jedoch nicht, dass dieselbe
Matchschwelle fuer Audio und Video fachlich sinnvoll ist.

## Getrennte Kapazitaetskorridore

Fuer die erste private Skalierungsstufe werden nur folgende endliche
Explorationskorridore zugelassen:

| Rolle | Auditive Bank | Visuelle Bank |
|---|---:|---:|
| Mindestkapazitaet | 8 Slots | 4 Slots |
| Hoechstkapazitaet | 32 Slots | 16 Slots |

Die groessere auditive Slotzahl ist aufgrund der deutlich kleineren
Traegerdimension zulaessig. Diese Werte sind keine Aussage ueber eine
erforderliche Anzahl von Wahrnehmungszustaenden.

Eine spaetere private Konfiguration muss genau einen Wert innerhalb ihres
Korridors binden. Dynamisches Wachstum bleibt gesperrt.

## Logische Speicherobergrenze

Die vollstaendige Prototypnutzlast wird statisch durch
`Slotzahl mal Traegerdimension` begrenzt. Bei 32 auditiven und 16 visuellen
Slots ergeben sich:

| Profil | Prototypwerte gesamt | gepackte float64-Nutzlast | Orientierung fuer Python-Floatwerte |
|---|---:|---:|---:|
| Browser | 544 | 4.352 Byte | etwa 17.408 Byte |
| kontrolliert | 1.536 | 12.288 Byte | etwa 49.152 Byte |
| oeffentlich AV | 5.376 | 43.008 Byte | etwa 172.032 Byte |
| Standard/Live | 6.144 | 49.152 Byte | etwa 196.608 Byte |

Die gepackte Spalte ist nur das mathematische float64-Aequivalent der
Prototypwerte. Der aktuelle Python-Referenzkern verwendet Tupel und
Python-Floats. Die Orientierungsspalte setzt dafuer grob 32 Byte pro Wert an,
ist aber keine plattformunabhaengige Messung und enthaelt weder Tupel,
Dataclasses, Kennungen noch Digest- und JSON-Arbeitsobjekte.

Verbindlich ist deshalb die endliche Anzahl der Prototypwerte, nicht eine
behauptete Bytegenauigkeit der Python-Runtime.

## Distanz- und Schrittaufwand

Eine voll belegte Bank benoetigt pro Eingang hoechstens
`Slotzahl mal Traegerdimension` komponentenweise Distanzterme:

| Profil | auditive Distanzterme pro Audioeingang | visuelle Distanzterme pro Videoeingang |
|---|---:|---:|
| Browser | 256 | 288 |
| kontrolliert | 384 | 1.152 |
| oeffentlich AV | 1.536 | 3.840 |
| Standard/Live | 1.536 | 4.608 |

Beim Standard-/Liveprofil mit 100 auditiven Rezeptorzustaenden und 30
visuellen Rezeptorzustaenden pro Sekunde entspricht dies statisch hoechstens
291.840 komponentenweisen Distanztermen pro Sekunde. Hinzu kommen
Aktualisierung, Validierung, Objektanlage und kanonische Digests.

Dies ist eine Operationszaehlung und kein Laufzeitbefund. Vor einer realen
Medienausfuehrung sind private dimensionsskalierte Zeit- und Speicherchecks
erforderlich.

## Getrennte Matchschwellenkorridore

Die normalisierte L1-Distanz bleibt die einzige Distanzfamilie. Fuer eine
spaetere synthetische Auswahl werden folgende breite Korridore gebunden:

| Rolle | Auditive Bank | Visuelle Bank |
|---|---:|---:|
| `match_threshold` | 0,02 bis 0,25 | 0,01 bis 0,20 |

Die Korridore sind absichtlich nicht identisch. Auditive Spektralenergie und
visuelle lokale Kanalwerte besitzen unterschiedliche Verteilungen und
Traegerdimensionen.

Kein Wert innerhalb des Korridors ist damit fachlich bestaetigt. Ein spaeterer
Vertrag muss Schwellen vor der Ausfuehrung aus kontrollierten, labelfreien
synthetischen Abstaenden waehlen und getrennt gegen Immer-Match und
Nie-Match pruefen.

## Aktualisierungs- und Stabilisierungskorridore

| Rolle | Auditive Bank | Visuelle Bank |
|---|---:|---:|
| `update_rate` | 0,05 bis 0,50 | 0,05 bis 0,50 |
| `stable_after` | 3 bis 16 | 3 bis 12 |

Kleine Aktualisierungsanteile bewahren laenger den bisherigen Prototyp;
groessere reagieren schneller auf neue zugeordnete Zustaende. Der Audit
entscheidet nicht, welcher Verlauf nuetzlicher ist.

`stable_after` bleibt ein saettigender technischer Zaehler. Er darf nicht als
Qualitaet, Sicherheit oder semantische Gewissheit interpretiert werden.

## Vergessenskorridore

Vergessen bleibt an akzeptierte Schritte derselben Bank gebunden:

| Rolle | Auditive Bank | Visuelle Bank |
|---|---:|---:|
| `expire_after_steps` | 256 bis 8.192 | 64 bis 2.048 |

Die Korridore vermeiden Wand- oder Systemzeit und verhindern, dass die
Audiorate visuelle Prototypen altern laesst. Ihre ungefaehre zeitliche Wirkung
haengt von der jeweiligen Eingangsrate ab und ist kein Bestandteil des
gespeicherten Prototyps.

Vor einer spaeteren Konfiguration muessen kurze und lange Korridorenden gegen
sofortiges Vergessen, dauerhafte Belegung und LRU-Dominanz verglichen werden.

## Profilbindungsregeln

Ein spaeterer privater Profilbinder muss:

1. genau eine vorhandene Rezeptorkonfiguration entgegennehmen;
2. Geometrie-ID und Traeger-IDs ausschliesslich aus den vorhandenen
   Rezeptorklassen ableiten;
3. Audio und Video in getrennte PPB-Konfigurationen ueberfuehren;
4. Kapazitaet und Parameter nur innerhalb der S1-VK-Korridore akzeptieren;
5. den Config-Digest vor dem ersten Eingang festlegen;
6. bei jeder Geometrie- oder Traegerabweichung fail-closed abbrechen;
7. weder Medienquelle noch Feldkern importieren;
8. keinen Prototypzustand im Feldsnapshot registrieren.

Eine automatische Parameterwahl aus spaeteren Ergebnissen ist nicht
zulaessig.

## Sicherheits- und Datenschutzgrenze

PPB-1 speichert keine Rohhistorie. Ein visueller Prototyp besitzt jedoch bis
zu 288 lokale Kanalwerte und kann einem zeitlich gemittelten reduzierten Bild
aehneln. Ein auditiver Prototyp kann ein wiederkehrendes reduziertes
Spektralmuster darstellen.

Daher gelten weiterhin:

- keine Behauptung von Anonymisierung oder Nichtinvertierbarkeit;
- kein persistenter Export ohne eigenen Vertrag;
- keine Aufnahme von Dateinamen, Quellenkennungen oder Snapshot-IDs;
- kein Logging vollstaendiger Prototypwerte im spaeteren Standardpfad;
- keine Semantik- oder Labelanreicherung.

## Baseline- und Skalierungskontrollen

Vor jeder realen Bindung bleiben mindestens folgende Kontrollen erforderlich:

| Kontrolle | Stoppfrage |
|---|---|
| ein gleitender Mittelwert pro Modalitaet | liefert eine einzelne Spur denselben gebundenen Engineeringnutzen? |
| feste Prototypliste | sind Aktualisierung und Vergessen technisch notwendig? |
| kleine Kapazitaet | verbessert groessere Kapazitaet den gebundenen Readout oder nur den Speicherverbrauch? |
| Schwellenextreme | erzeugt der Korridor Immer-Match oder Nie-Match? |
| Digest-Ablation | dominiert Kanonisierung die Laufzeit des reinen Kerns? |
| PPB-OFF | bleibt der aktive Rezeptor-/Feldpfad bitgleich? |

Eine einfachere Konfiguration wird bevorzugt, wenn sie denselben technischen
Nutzen unter kleinerem Budget erreicht.

## Auditentscheidung

```text
S1_VK_EXISTING_RECEPTOR_FRAMES_DIRECTLY_BINDABLE
S1_VK_BROWSER_8_18_PROFILE_BOUND
S1_VK_CONTROLLED_12_72_PROFILE_BOUND
S1_VK_PUBLIC_48_240_PROFILE_BOUND
S1_VK_DEFAULT_LIVE_48_288_PROFILE_BOUND
S1_VK_SEPARATE_AUDIO_8_TO_32_SLOT_CORRIDOR_BOUND
S1_VK_SEPARATE_VISUAL_4_TO_16_SLOT_CORRIDOR_BOUND
S1_VK_LOGICAL_MAX_6144_PROTOTYPE_VALUES_BOUND
S1_VK_NORMALIZED_L1_PARAMETER_CORRIDORS_BOUND
S1_VK_STEP_BASED_FORGETTING_CORRIDORS_BOUND
S1_VK_STATIC_BINDING_AND_SCALING_ADMISSIBLE
S1_VK_PARAMETER_SUITABILITY_AND_RUNTIME_COST_OPEN
S1_VK_NO_ADAPTER_NO_TEST_NO_FIELD_OR_MEDIA_RUN
S1_VK_NO_MEMORY_OR_FIELD_CAUSE_FINDING
```

S1-VK bestaetigt nur die statische Bindbarkeit und endliche Skalierung. Der
Audit belegt nicht, dass die Korridorwerte gute Wahrnehmungszustaende bilden
oder dass PPB-1 fuer reale Medien geeignet ist.

## Genau ein naechster Schritt

**Abschlussstand:** Dieser in S1-VK vorregistrierte Schritt wurde mit S1-VL
umgesetzt und synthetisch abgenommen. Die nachstehende Freigabe ist damit
verbraucht. Der aktuelle Anschluss ist der in S1-VL gebundene statische
S1-VM-Vertrag.

Der einzige fachlich begruendete Anschluss ist:

```text
S1-VL - privater PPB-1-Rezeptorprofilbinder und dimensionsskalierte
        synthetische Abnahme
```

S1-VL darf ausschliesslich implementieren und pruefen:

- private feste Config-Binder fuer die vier vorhandenen Geometrieprofile;
- exakte Geometrie- und Traegerableitung aus bestehenden Rezeptorklassen;
- Ablehnung aller Werte ausserhalb der S1-VK-Korridore;
- synthetische leere, kleine und maximal zulaessige Bankzustaende;
- logische Prototypwert- und Distanztermobergrenzen;
- PPB-OFF-, Import- und Snapshotregression.

Nicht zulaessig bleiben Feldintegration, oeffentliche API, Snapshotumbau,
reale Medienausfuehrung, Persistenz oder Semantik.

## Projektgrundlagen

- [S1-VJ privater PPB-1-Referenzkern](S1VJ_PPB1_PRIVATER_REINER_REFERENZKERN_UND_SYNTHETISCHE_VERTRAGSABNAHME.md)
- [S1-VI PPB-1-Konstruktionsvertrag](S1VI_PPB1_STATISCHER_DATEN_DISTANZ_LEBENSZYKLUS_UND_TESTMATRIXVERTRAG.md)
- [Logarithmischer auditiver Rezeptor](../mcm_field_organism/log_spectral_receptor.py)
- [Visueller Rasterrezeptor](../mcm_field_organism/finite_video_path.py)
- [Aktiver Rezeptorvertrag](../mcm_field_organism/receptor_contract.py)
- [Kontrollierte Audio-Video-Testwelt](../mcm_field_organism/controlled_audio_video_test_world.py)
- [Oeffentlicher Audio-Video-Rezeptorpfad](../mcm_field_organism/public_av_receptor_run.py)
- [Gemeinsamer Audio-Video-Feldkontakt](architektur/026_GEMEINSAMER_AUDIO_VIDEO_FELDKONTAKT.md)
