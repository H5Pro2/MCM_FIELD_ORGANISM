# S2-NK: private Profilintegration der auditiven Skalenuebertragung

Status: `STATISCH_GEBUNDEN_KEINE_AUSFUEHRUNGSFREIGABE`, 2026-09-07.
Keine Lauf-ID. Grundlage: [S2-NI](S2NI_STATISCHER_AUDITIVER_REZEPTOR_KONTAKT_SKALIERUNGSVERTRAG.md)
und [S2-NJ, 16/16](../reports/s2nj/s2nj-private-output-half-qualification-20260907-01/BEFUND.md).
Ausgangsskala, zugehoerige auditive Distanzgrenzen und die feste Umrechnung
der Audio-Rangdistanz werden prospektiv gebunden. Analystenentscheidung vom
2026-09-07: relative Audio-/Visual-Gewichtung der Memoryauswahl erhalten.
Keine Quellenkalibrierung, neue Lernregel oder Produktionsumstellung.

## 1. Konkrete Bindung und Inventar

Zwei zentrale neue Werte, ausschliesslich im neuen privaten Profil:

| Konfigurationsrolle | Alt | Neu |
| --- | --- | --- |
| `tspm_config.fast_config.auditory_match_threshold` | `0.2` | `0.1` |
| `tspm_config.profile.auditory_config.match_threshold` | `0.02` | `0.01` |

Der im Koordinator/Scanner verwendete zweite Zugriff
`config.profile.profile.auditory_config.match_threshold` muss dieselbe
auditive Bankbindung bezeichnen, keine unabhaengige Kopie. Alle Konsumenten
einschliesslich Verifikatoren und Baselines lesen diese gebundenen Felder.
Kein impliziter Rueckfall auf Defaultwerte, kein Monkeypatching.

Binary64-Bindung prospektiv: `0.2 = 0x1.999999999999ap-3`,
`0.1 = 0x1.999999999999ap-4`, `0.02 = 0x1.47ae147ae147bp-6`,
`0.01 = 0x1.47ae147ae147bp-7`. Jeweils genau `alt * 0.5`, kein neues
Runden auf Dezimalstellen. Die spaetere Qualifikation prueft diese Bits.

| Tatsachlicher Konsument / lesende Fundstelle | Rechnung / neue Grenze |
| --- | --- |
| `_s2jw_default_live_profile.py:119-126`, historische Fabrik | Vorbild fuer **neue private** Bindung: Audio-PPB `(8,0.01,0.05,3,256)`, Visual-PPB unveraendert `(4,0.01,0.05,3,64)`, Fast `(3,0.1,0.2,0.5,2,8)`; historische Fabrik nicht editieren |
| `_tspm1_private.py:1391-1402`, Fast-Formation; Relationspruefung `1559-1570` | Audio `math.fsum(abs(delta))/48 <= 0.1`; Visual `<=0.2`; gemeinsamer Match bleibt AND |
| `_ppb1_reference.py:444-455,608-611`, auditive PPB-Zuordnung | `math.fsum(abs(delta))/48 <= 0.01`, auch bei instabilen belegten Slots |
| `_s2kz_private_auditory_partial_cue_retrieval_336.py:531-543,619-679`, historische A-/Slow-Scans | B4/Fast: historisches `sum(terms)/24 <= 0.1`; stabiler Auditory-Slow: dasselbe `sum(terms)/24 <= 0.01` |
| `_s2ne_private_auditory_transfer.py:74-94`, alternativer A-Scan | Nur B4/Fast: `max(terms) <= 0.1`; Slow bleibt der vorige Mittelwertscan |
| `_s2kz_private_direct_auditory_slot_scan_baseline.py:119-127,208-258` | Unabhaengiger historischer Direktarm liest A `0.1`, Slow `0.01`; `sum(terms)/24` |
| `_s2ne_private_direct_and_verification.py:15-29,76-94` | Alternative Direktbaseline und Belegnachrechnung: A `max(terms)<=0.1`; Referenz-A `sum/24<=0.1`; Slow beider Arme `sum/24<=0.01` |
| `_s2jw_profiled_memory_read_only.py:148-255`, Vollproben-Anschluss | B4/Fast Audio `fsum/48<=0.1` mit unveraenderter visueller AND-Bedingung; Auditory-Slow `fsum/48<=0.01` und Stabilitaet |
| `_tspm1_private.py:2876-2894,2964-2987` und `_ppb1_s1wu_read_only_perceptual_probe.py:211-222` | Native Vollproben und ihre Validatoren: Fast Audio `0.1`, auditive stabile PPB-Probe `0.01`, jeweils `normalized_mean_l1_distance` |

Dateien mit `_s2...` liegen in `tools/`, die anderen Kernmodule in
`mcm_field_organism/`. Vollproben sind hier inventarisierte vorhandene
Anschluesse, **keine** neu verlangten Runtimeoperationen. S2-NG bindet Regeln
und Konfiguration, fuehrt aber keine weitere auditive Distanzgrenze ein.

Abgrenzung: B4-Formation selbst hat keine Matchinggrenze. Der S2-JW-Aufruf
`_advance_b4_candidate` delegiert an die reine FIFO-Fortschreibung
`_tspm1_s2dr_private_comparison._advance_b4` (Zeile 1452). Dessen andere
historische Versuchsarme mit festen 26-Werte-Grenzen werden nicht uebernommen.
Ebenso bleibt `S2LG.SLOW_THRESHOLD=0.02` samt alter LC02-Digests historisch;
nur die PPB-Rechenreihenfolge ist ein Vorbild, nicht jener fest gebundene Auswerter.
Die NC/ND-`statistics.mean`-Arme werden nicht in diese Referenz umgedeutet.

Unveraendert: visuelle Fast-Grenze `0.2`, visuelle PPB-/Slow-Grenze `0.01`,
Fast-Updatefaktor `0.5`, PPB-Updaterate `0.05`, Fast-Supportgrenze `2`,
Slow-Stabilitaet `3`, Ablaufwerte `8/256/64`, B4/Fast/Slow-Kapazitaeten
`9/3/8+4`, native Uhren und Zeitparameter. Keine globale Literalersetzung.
Auch technische Normalform-/Distanzdomaenen `[0,1]` beziehungsweise `[0,2]`
sind keine zu halbierenden Matchschwellen.

## 2. Einmalige gemeinsame Wahrnehmungsprojektion

`unveraenderter Audiorezeptor -> S2-NJ einmal -> neue kanonische AV-Bindung`
ist der einzige vorgesehene Weg. `HalfScaleAuditory48V1` liefert dieselben
48 Audiowerte an Feld und Memory, neben denselben unveraenderten 288 Visualwerten.
Nicht separat in beiden Zweigen skalieren. Keine nachtraegliche Skalierung
bereits gebildeter Prototypen oder importierter historischer Zustaende.
Feld-/Memoryzweige bleiben unabhaengig; nur B4/TSPM ist atomar.

Neue Quellenprofil-, auditive Geometrie-, PPB-Bankkonfigurations-, Fast-,
Koordinator-, Cue-, Regel- und Receiptbindungen muessen Ausgangsprofil
`s2nj.auditory.hann48.output-half.v1` und beide neuen Grenzwerte eindeutig
einschliessen. Alte/neue Zustaende, Cues oder Owner zu mischen stoppt fail-closed.
Die gemeinsamen neuen Bankkonfigurationen muessen konsistent sein; Visual-
Parameter bleiben inhaltlich gleich, auch wenn ein uebergeordneter Digest wechselt.

Die heutigen Default-Live-Fabriken erzwingen alte Digests; die PPB-Profil-ID-
Liste ist geschlossen. Das neue Profil ist deshalb **kein** ungepruefter
Parameterwechsel am historischen Haupteinstieg. Eine spaetere private
Anbindung muss diese Typ-/Profilgrenze explizit und mit Negativtests behandeln,
ohne alte Validatoren zu lockern oder neue Werte als altes Profil auszugeben.

## 3. Wichtige Grenze: Matchmenge ist nicht Slotwahl

In reeller Arithmetik gilt fuer jede der genannten reinen Audiovergleichs-
funktionen `d(x/2,y/2)=d(x,y)/2`; mit halbierter Grenze bleibt das einzelne
Matchpraedikat erhalten. Das garantiert **nicht** dieselbe Memorygeschichte.

Fast sortiert mehrere gemeinsame Treffer nach
`(max(d_audio,d_visual), d_audio+d_visual, slot_id)`;
vgl. `_tspm1_private.py:1406-1429` und die zugehoerige Relationspruefung.
Dasselbe Prinzip findet sich bei nativen Fast-Vollproben und den B4-/Fast-
Vollprobenbeobachtern. Nur Audio zu skalieren ist fuer diesen gemischten
Sortierschluessel keine gemeinsame Skalierung.

Rein algebraisches, exakt binaer darstellbares Gegenbeispiel, kein Memorylauf:

| Passender Slot | `(d_audio,d_visual)` alt | nach Audiohalbierung |
| --- | --- | --- |
| slot-01 | `(3/16,1/32)` | `(3/32,1/32)` |
| slot-02 | `(1/32,1/8)` | `(1/64,1/8)` |

Beide Slots bleiben innerhalb der jeweiligen Audio-/Visualgrenzen.
Alt gewinnt slot-02 mit Maximum `1/8` gegen `3/16`; neu gewinnt slot-01
mit Maximum `3/32` gegen `1/8`. Das ist **kein Rundungsfehler**. Eine andere
Fast-Auswahl kann Updates, Supports und spaetere PPB-Zufuehrungen aendern.
Unveraenderte visuelle Regeln garantieren dann auch keine unveraenderte
visuelle Slow-Geschichte.

Die Teilhinweisscanner selbst besitzen keine solche Rangfolge: voller
`9/3/8`-Scan, exakte 48-Werte-Gleichheit bei der A-Aufloesung und Enthaltung
bei Mehrdeutigkeit bleiben bestehen. Auch diese Gleichheitspruefung kann
durch Subnormalrundung/Unterlauf beeinflusst werden, obwohl Matchmengen gleich bleiben.

### 3.1 Entschiedene profilgebundene Rangskala

Die Analystenentscheidung schliesst die zuvor offene Gewichtungsfrage:
Matching verwendet weiterhin `d_audio_neu` und die halbierte Audiogrenze.
Erst fuer den gemischten Rangschluessel wird einmal
`r_audio = 2.0 * d_audio_neu` berechnet. Fast verwendet danach
`(max(r_audio,d_visual), r_audio+d_visual, slot_id)`.
Keine Rueckskalierung der gespeicherten Werte, Updateeingaenge, Matchdistanzen
oder Feldkontakte. Keine Division durch eine Schwelle, adaptive Gewichtung
oder Fallbackregel. Rangfreie Teilhinweisscans bleiben rangfrei.

Die neue unveraenderliche Profilbindung muss Rangregelversion und den festen
Faktor `2.0` zusaetzlich zu Ausgangsprofil und Grenzwerten digestieren.
Historische Profile behalten ihren bisherigen Schluessel ohne Umrechnung.
Matchdistanz und umgerechnete Rangdistanz sind im spaeteren Pruefbeleg getrennt;
die Umrechnung darf nicht versehentlich zweimal erfolgen.

### 3.2 Anschlussinventar einschliesslich Nachpruefung

| Stelle | Bindung fuer das neue Profil / Abgrenzung |
| --- | --- |
| `_tspm1_private.py:1406-1429`, `advance_tspm1_fast` | Gemischte Fast-Auswahl nach neuer Rangskala; Matchfilter, Slot-ID und nachfolgende Updates nicht umdeuten |
| `_tspm1_private.py:1574-1600`, `_validate_fast_candidate_relations` | Dieselbe Profilregel fuer unabhaengige Rekonstruktion der erwarteten Auswahl; keine Annahme des gelieferten Gewinners |
| `_tspm1_private.py:2976-2989`, `probe_tspm1_read_only`; Relationspruefung `2888-2924` | Native Fast-Vollprobe und erwarteter Slot muessen dieselbe Rangskala binden; berichtete auditive Matchdistanz bleibt auf neuer Skala |
| `_s2jw_profiled_memory_read_only.py:182-188,222-227` | B4-Vollprobe: `(max(r_audio,d_visual),r_audio+d_visual,-formation_index,slot_id)`; Fast-Vollprobe ohne Alterskomponente |
| `_s2jw_profiled_memory_read_only.py:283-316` | Native Probe und Beobachter werden zusammengefuehrt; bisher wird Fast nur auf Erkanntstatus verglichen. Fuer die neue Bindung muss auch die ausgewaehlte Slot-ID/-Bindung uebereinstimmen; Statusgleichheit allein prueft keine Rangtreue |
| `_tspm1_s2dr_private_comparison.py:1504-1516,1905-1907` | Historische generische R0-Direktbaseline: Formation und Vollprobe besitzen eigene gemischte Auswahl. Kein unveraenderter Neu-Profil-Oracle; eine spaetere private Direktnachrechnung muss die Rangskala unabhaengig berechnen |

Die R0-Formation verwendet nach Maximum/Summe den Slotindex, die R0-Probe
die Slot-ID. Historisch gebundene kanonische Slotreihenfolge nicht stillschweigend
als beliebige Reihenfolge behandeln; ein Direktvergleich muss die Zuordnung
von Index zu Slot-ID explizit pruefen. Alle weiteren Tie-Breaks bleiben bestehen.

Weitere gefundene, **nicht angeschlossene historische** gemischte Schluessel:
S2-DR `_advance_b2` (1410), `_probe_joint_slots` (1783),
`tools/_retention_capacity_read_only.py:249-252,320-322` sowie
`tools/_visual_l1_calibration_probe.py:89`. Sie bleiben unveraendert und sind
keine Neu-Profil-Baselines. Die tatsaechlich wiederverwendete B4-FIFO-Formation
besitzt keinen solchen Schluessel. S2-KZ-/S2-NE-Teilscan-Direktbaselines
benoetigen keine Rangumrechnung; auditive PPB-Auswahl ist rein unimodal.

### 3.3 Kleinster notwendiger Anschluss, noch nicht freigegeben

**Kein bestehender reiner Adapteranschluss fuer die Rangregel:**
`TSPM1FastConfig` (137-224) hat kein Rangskalenfeld; die exakten Typpruefungen
der Configbindung (242,272,814) erlauben auch keinen beliebigen Ersatztyp.
Der S2-JW-Koordinator (652-667) ruft den festen TSPM-Owner auf. Dieser ruft
bei 2489/2494 unmittelbar Fortschreibung und Relationspruefung auf. Ein
ausserhalb korrigierter Kandidat wuerde die interne Rangpruefung nicht ersetzen.
`_validate_step_result_relations` (2352) bindet danach Digests/Owner, bietet
aber keinen Auswahlhook. Monkeypatching, Umordnung von Slots oder ein
duplizierter Memorykern sind kein zulaessiger Ausweg.

Notwendig waere eine eng begrenzte **Kernanschlusserweiterung** in
`_tspm1_private.py`: explizit versionierte, konfigurationsgebundene Rangskala
fuer Fast-Fortschreibung, Kandidatenrelationspruefung und native Vollprobe
samt Relationspruefung. Nur zwei feste Bindungen: historisch unveraendert
und neues Halbprofil mit Audio-Rangfaktor `2.0`; kein frei waehlbarer Callback.
Der neue Konfigurationsdigest muss diese Bindung bis in State, Owner und
Receipt tragen. Alte kanonische Payloads, Digests und Defaults muessen dabei
erhalten bleiben; ein zusaetzliches Feld in allen historischen Payloads
waere keine unveraenderte Altbindung. Neue Profil-/Configversion und deren
exakte Validatorzulassung sowie der S2-JW-Profilanschluss sind eigens noetig.
PPB-Kern und gespeicherte Updatewerte brauchen keine Rangskalenumrechnung.

Diese notwendige Aenderung ist hier **nur benannt, nicht autorisiert oder
implementiert**. Ohne gesonderte Freigabe dieses Kernanschlusses ist die
geforderte Profilintegration ueber den vorhandenen Koordinator nicht moeglich.

## 4. Vorab begrenzter neutraler Vergleich, heute nicht ausgefuehrt

Beide Seiten rechnen selbst: alter Vektor/alte Grenze gegen einmal mit S2-NJ
halbierten Vektor/halbierte Grenze. Nicht bloss einen alten Ergebnisabstand
halbieren. Alte/neue Konfigurationen und Zustaende getrennt. Die alten
Vergleichseingaenge liegen im gemeinsamen gueltigen Bereich `[0,1]^48`;
Rohrezeptorwerte oberhalb Eins sind kein gueltiger alter Memoryeingang.

Fuenf Routen: Fast-`fsum/48`, PPB-`fsum/48`, Referenz-A-`sum/24`,
Alternative-A-`max ueber 24 Baender` und Slow-`sum/24`. Pro Route sechs feste Paare:
Nullabstand; uniforme Differenz `t`; `nextafter(t,0)`; `nextafter(t,+inf)`;
`4*t` auf dem ersten Viertel der verglichenen Positionen und sonst Null;
sowie `x=1/4`, `y=fl(1/4+t)` uniform. Fuer die ersten fuenf Paare ist
`x=0`; `y` traegt die angegebene Differenz. `t` ist die jeweils alte Grenze.
Damit 30 Vergleichspaare, ohne Suche nach einer Abweichung. Beobachtete
Positionen bleiben `0..23`, verdeckte Werte dienen nur der Kandidatengleichheit.

Zusaetzlich drei feste Subnormalpaare, nur Position 47 verschieden, sonst Null:
`(s,0)`, `(3*s,4*s)`, `(m,nextafter(m,0))`, mit kleinster positiver
Binary64-Subnormalzahl `s` und kleinstem normalem Wert `m`. Abstaende,
Unterlaufmarker, Vektorgleichheit und A-Konflikt/Gleichheit getrennt pruefen.

PPB separat: zwei neutrale Vier-Schritt-Ketten uniformer 48er-Vektoren,
`[1/8,1/8,1/8,1/8]` sowie `[1/8,17/128,15/128,1/8]`, je einmal pro Skala
aus eigener Nullbank. Unveraendert pro Komponente
`(1.0-update_rate)*previous + update_rate*current`, `update_rate=0.05`,
kein FMA und keine algebraische Umordnung. Eingangs-/Ereigniskette, Slotwahl,
Support, alle Zwischenprototypen und Digests aufzeichnen. Verglichen werden
`PPB_neu(x/2)` und `PPB_alt(x)/2`, nicht pauschal gleiche Gesamtdigests.
Das obige Fast-Mehrtrefferbeispiel ist verpflichtend in drei Sichten:
historisch slot-02; halbierte Werte ohne Rangumrechnung slot-01;
halbierte Werte mit `r_audio=2.0*d_audio_neu` wieder slot-02.
Im letzten Fall werden die beiden historischen Schluessel exakt wiederhergestellt.
Das ist eine algebraische Kontrolle, noch kein beobachteter Binary64-Test.

Matchmenge, komplette Rangtupel, gewaehlte Slot-ID und Tie-Breaks sind separat
zu pruefen. Feste weitere Kontrollen: gleiches Maximum bei verschiedener
Summe; gleiche Maximum-/Summenwerte bei verschiedenen Slot-IDs; bei B4
zusaetzlich verschiedenes Formationsalter vor dem Slot-ID-Tie-Break.
Verifikation und Direktbaseline duerfen keinen vorgegebenen Gewinner uebernehmen.
Danach Fast-Update mit unveraendertem Faktor `0.5`, Support, Konsolidierungs-
berechtigung, PPB-Zufuehrung und PPB-Updates in beiden Modalitaeten getrennt
vergleichen. Gleiche Slotwahl allein beweist keine identischen Folgewerte.

Binary64 rechnet erst `r_audio=2.0*d_audio_neu`, dann `max` und Addition.
Unterlauf beim Halbieren, Distanzsummation/-division und Updates bleiben
jeweils sichtbar; die Rangumrechnung kann verlorene Bits nicht rekonstruieren.
Die vorgesehenen Subnormal-/Nachbarwertfaelle muessen daher auch Matchmenge,
Rangtupel und Tie-Break dokumentieren, nicht nur den abschliessenden Treffer.

Pruefbeleg je Fall: Eingangs-/Grenz-/Abstandsbits als Binary64-Hex, jeweilige
Rechenfolge, Matchstatus, gegebenenfalls Slotwahl und Updatezwischenwerte.
Direktbaselines erhalten dieselben Grenzbindungen, berechnen ihre Ergebnisse
unabhaengig; eine rationale Referenz dient nur dem getrennten Auswerter.
Keine Toleranz, Rundung, Ersatzwerte oder Weglassen unguenstiger Faelle.
Numerische Abweichung, strukturelle Auswahlabweichung und technische
Belegverletzung werden getrennt gemeldet. Endliche Tests beweisen weiterhin
keine universelle Gleitkommagarantie. Kein neuer Korpus und kein NH-Aufruf.

## 5. Feldwirkung und Abschluss

Halbierte auditive Kontakte bei unveraendertem Visualzweig veraendern die
Anregung und koennen die Trajektorie veraendern. Kein kompensierender Feldgain,
keine alte/neue Feldzustands- oder Trajektoriengleichheit als Erfolgskriterium.
Spaeter separat zu pruefen: gueltige endliche Feldschritte und identische
kanonische Eingangswerte innerhalb der neuen Feld-/Memory-Geschwisterbindung.
Vergleich der Feldwirkungen bleibt von der Matchingqualifikation getrennt.
Die angestrebte Bedeutungserhaltung betrifft Memoryvergleiche einschliesslich
interner Auswahl, nicht die auditive Feldanregung. Der Rangfaktor `2.0` darf
nicht als Feldgain oder Rueckskalierung einer Wahrnehmungsprojektion dienen.

Heute nur lesendes Inventar und dieser Vertrag; keine Implementierung,
Tests, Materialisierung oder Systemausfuehrung. S2-NH bleibt `NOT_EVALUABLE`,
S2-NG/S2-NJ historisch gueltig, Gates `False`, Belege und Bootstrap unberuehrt.

WEITER: Am besten geht es jetzt mit der ausdruecklichen Entscheidung ueber
den notwendigen versionierten TSPM-Rangskalenanschluss weiter. Bis dahin
bleibt die Implementierung der neuen Profilintegration gesperrt.

## 6. Analystenentscheidung nach S2-NM

Nachtrag 2026-09-07: Die vorausgehenden Freigabegrenzen dokumentieren den
historischen Vertragsstand. S2-NL qualifizierte den versionierten Anschluss;
S2-NM belegt bei allen drei gebundenen Subnormalpaaren unter beiden
Teilscanregeln einen Wechsel von A-Konflikt zu eindeutiger A-Zulassung.
Vollstaendige Bedeutungsgleichheit ist damit widerlegt, die technische
Qualifikation bleibt gueltig.

Der Analyst akzeptiert dies ausschliesslich fuer die getrennt versionierte
private Forschungsvariante, **nicht als verlustfreie Migration**.
Kandidatengleichheit bezieht sich auf die tatsaechlich gespeicherten gerundeten
Werte. Eine dadurch aufgeloeste Konfliktsituation ist nicht automatisch ein
richtiger Abruf; ihre Haeufigkeit an realen Quellen bleibt unbekannt.
Keine Restwertspeicherung, Sonderlogik, Toleranz oder Ersatzdarstellung.

Freigegeben ist die kleine private Runtime-Anbindung mit einer einmaligen
neutralen Qualifikation: NJ genau einmal vor der gemeinsamen Bindung,
identische halbierte Audiowerte fuer Feld und Memory, unveraenderte Visualwerte,
getrennte Instanzen fuer beide Audio-Regelarme. Profil, halbierte Audiogrenzen
und feste Rangumrechnung bleiben vollstaendig gebunden. Historische Defaults
und Zustaende werden nicht migriert. Geprueft werden Formation, Fortsetzung,
beide Teilhinweisformen, Fehlerisolation, Read-only-Verhalten und Lifecycle.
Keine Alt-/Neu-Feldgleichheit, Feld-Rueckverstaerkung, NH-Quelle oder
vollstaendige Transfergeschichte. Hauptgates bleiben `False`.
