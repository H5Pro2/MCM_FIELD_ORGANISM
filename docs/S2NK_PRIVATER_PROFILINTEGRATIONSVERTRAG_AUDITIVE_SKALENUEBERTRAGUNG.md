# S2-NK: private Profilintegration der auditiven Skalenuebertragung

Status: `STATISCH_GEBUNDEN_KEINE_AUSFUEHRUNGSFREIGABE`, 2026-09-07.
Keine Lauf-ID. Grundlage: [S2-NI](S2NI_STATISCHER_AUDITIVER_REZEPTOR_KONTAKT_SKALIERUNGSVERTRAG.md)
und [S2-NJ, 16/16](../reports/s2nj/s2nj-private-output-half-qualification-20260907-01/BEFUND.md).
Nur Ausgangsskala und zugehoerige auditive Distanzgrenzen werden prospektiv
uebertragen. Keine Quellenkalibrierung, neue Lernregel oder Produktionsumstellung.

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

**Offene Entscheidung vor einer Zusage systemweiter Bedeutungserhaltung:**
Die jetzige Freigabe halbiert Grenzwerte, nicht den gemischten Auswahlmechanismus.
Keine eigenmaechtige Abstandsgewichtung, Rueckskalierung fuer Ranking oder
neue Auswahlregel. Ohne gesonderte Entscheidung ist nur die Erhaltung der
einzelnen Matchpraedikate Ziel, nicht die Gleichheit der Slot-/Supportfolge.

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
Das obige Fast-Mehrtrefferbeispiel kommt als getrennte Auswahlkontrolle hinzu.

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

Heute nur lesendes Inventar und dieser Vertrag; keine Implementierung,
Tests, Materialisierung oder Systemausfuehrung. S2-NH bleibt `NOT_EVALUABLE`,
S2-NG/S2-NJ historisch gueltig, Gates `False`, Belege und Bootstrap unberuehrt.

WEITER: Am besten geht es jetzt mit der Analystenentscheidung zur getrennten
Erhaltung von Matchpraedikaten und gemischter Fast-Slotwahl weiter, bevor
die neue private Profilanbindung implementiert wird.
