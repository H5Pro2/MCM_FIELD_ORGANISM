# S2-KX - Read-only auditiver Teilhinweisabruf aus der Zwei-Bereich-Memory 336

## Status und Zweck

`S2KX_STATIC_AUDITORY_PARTIAL_CUE_RETRIEVAL_336_CONTRACT_COMPLETE`

S2-KX bindet genau eine neue, begrenzte Funktion:

```text
reales PCM_F32LE-Teilhinweisfenster
+ unabhaengiger auditiver Bandplan
+ validierter bestehender 336-Werte-Memoryzustand
-> alle belegten auditiven Memoryslots auf beobachteten Baendern pruefen
-> B4 und Fast intern zu A_RECENT aufloesen
-> zwischen A_RECENT und B_STABLE_AUDITORY zulassen oder enthalten
-> getrennte auditive Kontexthypothese oder Enthaltung
```

Eine vorherige Vollprobe ist verboten. Es werden keine 48-Werte-Vektoren
eingespeist. Jeder auditive Probevektor muss aus einem tatsaechlichen,
validierten `PCM_F32LE`-Fenster durch den unveraenderten
`LogSpectralReceptor` entstehen.

S2-KX ist ausschliesslich ein statischer Funktions-, Materialisierungs- und
Falsifikationsvertrag. Er implementiert oder startet nichts. Er fuehrt keine
Memory-, Kontext-, Feld- oder Rezeptorfunktion aus.

## Gebundener Ausgangsstand

Technischer Ausgangsstand ist Commit
`0404dc6f04d3201fcb7434a00c3cd70347bae329`.

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| unveraenderter Audiorezeptor | `mcm_field_organism/log_spectral_receptor.py` | `26a6bd8f2d190db60c75ad29f275b3bd8b09b6d26d4ad54e4396176c4a36d2b0` |
| TSPM-1-Kern | `mcm_field_organism/_tspm1_private.py` | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` |
| PPB-1-Profile | `mcm_field_organism/_ppb1_receptor_profiles.py` | `28f3ce1de5b0ade465fffaa7dd3064eb51688cfea39ebb6c853cb4328bc0e5e0` |
| Default-Live-Profil | `tools/_s2jw_default_live_profile.py` | `ad5c8f607bc375daa8a6ed70134f6ed716780658a2a5e88bddb77a980da1af6f` |
| atomarer 336-Werte-Zustand | `tools/_s2jw_profiled_memory_coordinator.py` | `c9676ea9a740bfb82d66a91c00c559d1ff4d3759bd7bfed12c55afb9820dea81` |
| visuelle Teilhinweisreferenz | `tools/_s2kq_private_partial_cue_retrieval_336.py` | `669e3f7de6957640ed37e79d6608d94d7839d81e959ee1f48d7942526a86e422` |
| reale auditive PCM-Referenz | `tools/_s2ke_auditory_holdout_fixtures.py` | `2f24c6ed81f505ba6a04318c72aeb299eb6233faf9c589752178cf1267dbdac2` |
| bestaetigter visueller Teilhinweisbefund | `reports/s2ks/s2kw-partial-cue-main-20260903-02-verification/BEFUND.md` | `f18aec4e994165aa9e39bf8561b4d267fe4244b7e1886f6a50fbde7f0e766d9e` |

S2-KW bleibt der bestaetigte visuelle Teilhinweisbefund. Seine Ergebnisdateien,
Kandidaten oder Sollentscheidungen sind kein Eingang fuer S2-KX.

## Profil- und Memorygrenzen

Der erste S2-KX-Umfang verwendet unveraendert das Default-Live-Profil:

| Bindung | Wert |
| --- | ---: |
| PCM-Format | mono `PCM_F32LE` |
| Abtastrate | 48.000 Hz |
| Rezeptorfenster | 4.800 Samples |
| Hop | 480 Samples |
| auditive Rezeptordimension | 48 |
| visuelle Rezeptordimension | 288 |
| B4-Kapazitaet | 9 |
| Fast-Kapazitaet | 3 |
| auditive Slow-Kapazitaet | 8 |
| Fast-Audioschwelle | 0,2 |
| auditive Slow-Schwelle | 0,02 |
| Slow-Stabilitaet | Support mindestens 3 |

Die Schwellen sind vorhandene mechanische Memorygrenzen. S2-KX kalibriert sie
nicht als allgemeine akustische Aehnlichkeit und passt sie nach keinem
Ergebnis an.

## Reale PCM-Herkunft

Jede Formation und jeder Teilhinweis stammt aus einem eigenen, zeitlich
eindeutigen PCM-Quellfenster. Ein gueltiger Quellenbeleg bindet mindestens:

- exakt 4.800 endliche Float32-Samples im Bereich `-1..1`;
- Little-Endian-Byteordnung, Monoformat und 48.000 Hz;
- PCM-Payloaddigest vor der Rezeptoranalyse;
- `auditory_source_clock_id`;
- `auditory_window_start_tick` und `auditory_window_end_tick` in Samples;
- Rezeptorkonfigurations-, Kanalordnungs- und Profilbindingdigest;
- den Digest der tatsaechlich erzeugten 48 Rezeptorwerte.

Das PCM-Fenster wird hoechstens einzeln gestreamt und nach Rezeptorreduktion
verworfen. Rohsamples erscheinen weder im Memoryzustand noch in einem
Funktionsresultat oder Receipt.

Ein Teilhinweis verwendet einen kontinuierlich fortgeschriebenen
`BroadbandHearingPath`. Die 4.800 Samples werden durch zehn geordnete Hops zu
je 480 Samples materialisiert. Ein neuer Audiorezeptor ist nur am Beginn
einer vollstaendig unabhaengigen Fixture erlaubt. Wiederholter Inhalt muss ein
neues, strikt spaeteres Fenster und neue Quelldigests besitzen.

## Getrennte auditive Teilhinweisrolle

Der funktionale Eingang ist ein unveraenderlicher
`MaskedAuditoryCue48V1`. Er wird ausschliesslich aus dem Rezeptorabschluss des
tatsaechlichen Teilhinweis-PCM-Fensters und einem vorher gebildeten
`AuditoryBandPlan48V1` erzeugt.

Der erste Umfang bindet:

```text
OBSERVED_BANDS = 0..23
MASKED_BANDS   = 24..47
```

Die Teilung folgt allein der unveraenderten logarithmischen Kanalordnung und
wird vor jeder Abstandsmessung festgelegt. Sie darf nicht aus Zielwerten,
Memorytreffern oder einem Versuchsergebnis abgeleitet werden.

`MaskedAuditoryCue48V1` enthaelt fuer die 24 beobachteten Baender die real
erzeugten Rezeptorwerte und fuer die 24 verdeckten Baender ausschliesslich den
typisierten Marker `MASKED`. Die verdeckten Werte des Teilhinweisfensters
werden nicht in die Scanform uebernommen. Die Maske darf weder aus Nullwerten
noch aus Spektralenergie abgeleitet werden.

PCM-, Quellen- und Rezeptorwertdigests dienen ausschliesslich der technischen
Validierung. Weder Funktion noch Baseline duerfen aus ihnen Werte ableiten oder
sie als Matchmerkmal verwenden.

Der PCM-Teilhinweis selbst muss eine prospektiv gebundene physische
Teilinformation oder Stoerung enthalten, etwa das Weglassen einer gebundenen
Frequenzkomponente oder eine vorab festgelegte additive Stoerkomponente. Ein
vollstaendiges Zielsignal darf nicht zuerst analysiert und danach nur
rechnerisch maskiert werden.

## Native Zeitbindung

Ein bestehender Zustand und ein auditiver Teilhinweis sind nur gemeinsam
gueltig, wenn:

```text
cue.auditory_source_clock_id == state.fast.auditory_source_clock_id
cue.auditory_window_start_tick >= state.fast.auditory_last_end_tick
cue.auditory_window_end_tick   >  state.fast.auditory_last_end_tick
```

Die Zeitwerte stammen direkt aus dem analysierten PCM-Fenster. Eine eventuell
mitgefuehrte gemeinsame Feldzeit ist davon getrennt und ersetzt die native
Audiouhr nicht. Eine visuelle Uhr wird fuer den rein auditiven Teilhinweis
nicht geprueft.

## Einmaliges Geometrie-Startgate

Vor dem ersten Memoryaufruf eines spaeteren Funktionslaufs muss eine endliche,
read-only PCM-Materialisierung genau einmal abgeschlossen sein. Sie analysiert
alle Trainings-, Teilhinweis-, Stoer- und Distraktorfenster durch den realen
Audiorezeptor und bindet die tatsaechlichen 48-Werte-Ausgaben.

Fuer jedes geplante Cue-/Kandidatenpaar werden ohne Memoryzugriff ausgewiesen:

- die 24 einzelnen Differenzen auf `OBSERVED_BANDS`;
- der maskierte mittlere L1-Abstand;
- der volle 48-Werte-L1-Abstand nur diagnostisch;
- Minimal- und Maximalwert sowie alle nicht endlichen Werte;
- PCM-, Rezeptorwert-, Bandplan- und Paardigest;
- die erwartete mechanische Seite der Schwelle mit festem Sicherheitsabstand.

Die maskierte Distanz ist ausschliesslich:

```text
d_observed(cue, candidate)
    = sum(abs(cue[i] - candidate[i]) for i in 0..23) / 24
```

Fuer B4- und Fast-Slots gilt beim Teilscan die vorhandene Fast-Audioschwelle
`0,2`. Fuer stabile auditive Slow-Slots gilt die vorhandene auditive
Slow-Schwelle `0,02`. Der visuelle Anteil eines AV-Slots darf die auditive
Teilhinweisentscheidung weder bestaetigen noch verhindern.

Die Fixture muss vorab mindestens folgende Beziehungen mit den tatsaechlich
gemessenen Werten materialisieren:

1. genau einen eindeutigen A-Treffer und keinen B-Treffer;
2. keinen A-Treffer und genau einen eindeutigen B-Treffer;
3. je einen A- und B-Treffer als oeffentliche Mehrdeutigkeit;
4. mindestens zwei Treffer innerhalb einer internen A-Bank;
5. genau einen B4- und einen Fast-Treffer mit verschiedenen vollen
   48-Werte-Kandidaten als A-interner Konflikt;
6. zwei stabile auditive Slow-Treffer und keinen A-Treffer;
7. einen vollstaendig leeren Zustand;
8. einen belegten Zustand ohne anwendbaren auditiven Kandidaten.

Ausserdem muessen alle fuer Verdraengung vorgesehenen auditiven Distraktoren
ausserhalb der tatsaechlich relevanten gemeinsamen Fast-Zuordnung liegen.
Da Formation in TSPM-Fast audiovisuell entscheidet, ist diese Bedingung gegen
die echte Regel zu pruefen:

```text
FAST_MATCH = auditory_distance <= 0.2 AND visual_distance <= 0.2
```

Eine bitidentische visuelle Begleitung ist innerhalb einer auditiven
Geschichte zulaessig, sofern neue visuelle Quellen- und Zeitbelege verwendet
werden. Sie darf weder den auditiven Scan noch dessen Auswertung beeinflussen.

Kein Messwert darf nach einem Memoryergebnis veraendert oder erneut gesucht
werden. Verfehlt auch nur eine gebundene Beziehung ihre Seite oder ihren
Sicherheitsabstand, endet die Materialisierung vor jedem Memoryaufruf als:

`S2KX_AUDIO_PARTIAL_CUE_GEOMETRY_NOT_MATERIALIZABLE`

Dieser Status ist kein Memorybefund.

## Direkter Slotbestand

Die spaetere Funktion liest nach vollstaendiger Zustandsvalidierung exakt:

| interne Rolle | maximales Inventar | gelesener Anteil |
| --- | ---: | --- |
| `B4_RECENT` | 9 belegte FIFO-Slots | auditive Werte `0..47` des AV-Eintrags |
| `TSPM_FAST` | 3 belegte Fast-Slots | gespeicherte 48 auditiven Werte |
| `B_STABLE_AUDITORY` | 8 auditive PPB-Slots | nur stabile Prototypen mit Support mindestens 3 |

Alle drei Banken werden immer vollstaendig gescannt. Es gibt keinen
Short-Circuit nach einem Treffer. Freie Slots sind gueltig abwesend.
Instabile auditive Slow-Slots sind interne Diagnoseevidenz, aber keine
oeffentlichen Kandidaten. Die visuelle Slow-Bank wird nicht gescannt.

Ein vorhandener Vollprobenleser oder ein bereits ausgewaehlter Kandidat ist
kein zulaessiger Eingang. Der Scan darf weder Slotalter, Support, Distanz noch
Listenreihenfolge als Rangfolge verwenden.

## Bankbefunde

Jede interne Bank erzeugt genau einen kardinalen Befund:

```text
BANK_ABSENT_VALID
BANK_NO_OBSERVED_MATCH
BANK_UNIQUE_OBSERVED_MATCH
BANK_MULTIPLE_OBSERVED_MATCHES
```

Ein Slot ist ein Match, wenn sein `d_observed` kleiner oder gleich der fuer
seine Bank gebundenen nativen Audioschwelle ist. Alle Distanzen und alle
geprueften Slotdigests werden aufgezeichnet. Ein Mehrfachtreffer bleibt
mehrdeutig, auch wenn Support, Alter oder Distanz verschieden sind.

Jeder Scanbeleg bindet Bankrolle, Kapazitaet, gepruefte Slot-IDs und
Slotdigests, Stabilitaetsbelege, Trefferzahl, geordneten Treffersetdigest,
Probe-, Bandplan-, Profil- und Zustandsdigest.

## Interne Aufloesung von A_RECENT

B4 und Fast bleiben interne Rollen genau eines oeffentlichen Bereichs:

1. Mehrfachtreffer in B4 oder Fast erzeugen
   `A_RECENT_INTERNAL_AMBIGUITY` und keinen A-Kandidaten.
2. Genau ein eindeutiger Treffer in nur einer internen Bank erzeugt einen
   `A_RECENT`-Kandidaten mit diesem Herkunftsbeleg.
3. Je ein eindeutiger Treffer in B4 und Fast mit identischen vollstaendigen
   48-Werte-Kandidaten erzeugt einen A-Kandidaten mit zwei Herkunftsbelegen.
4. Je ein eindeutiger Treffer mit verschiedenen vollstaendigen
   48-Werte-Kandidaten erzeugt `A_RECENT_INTERNAL_CONFLICT` und keinen
   A-Kandidaten.
5. Zwei leere Banken erzeugen `A_RECENT_ABSENT_VALID`.
6. Null Treffer bei mindestens einem belegten internen Slot erzeugen
   `A_RECENT_NOT_APPLICABLE`.

Die Kandidatengleichheit in Punkt 3 ist eine kanonische Gleichheit der
vollstaendigen gespeicherten auditiven Wertetupel und ihrer Digests. S2-KX
fuehrt dafuer weder Rundung noch eine neue Schwelle ein.

## Aufloesung von B_STABLE_AUDITORY

Fuer die auditive Slow-Bank gilt:

- kein stabiler Slot: `B_STABLE_AUDITORY_ABSENT_VALID`;
- stabile Slots, aber kein Treffer: `B_STABLE_AUDITORY_NOT_APPLICABLE`;
- genau ein Treffer: `B_STABLE_AUDITORY_APPLICABLE`;
- mehrere Treffer: `B_STABLE_AUDITORY_INTERNAL_AMBIGUITY`.

Support belegt ausschliesslich Stabilitaet. Er waehlt keinen Kandidaten aus.
Ein fehlender auditiver Slow-Treffer ist kein globales `NO_CONTEXT`, wenn ein
gueltiger A-Kandidat oder ein anderer belegter Bereichszustand vorhanden ist.

## Oeffentliche Zwei-Bereich-Entscheidung

Oeffentlich existieren hoechstens:

```text
A_RECENT
B_STABLE_AUDITORY
```

Harte interne Mehrdeutigkeit oder interner A-Konflikt fuehrt immer zur
Enthaltung. Ohne harten internen Befund gilt:

| A-Kandidat | B-Kandidat | Lage | Ergebnis |
| ---: | ---: | --- | --- |
| 0 | 0 | beide Bereiche gueltig leer | `ABSTAIN_NO_CONTEXT` |
| 0 | 0 | mindestens ein Bereich belegt, aber unpassend | `ABSTAIN_NO_APPLICABLE_CONTEXT` |
| 1 | 0 | eindeutig | `ADMIT_SINGLE_CONTEXT`, `A_RECENT` |
| 0 | 1 | eindeutig | `ADMIT_SINGLE_CONTEXT`, `B_STABLE_AUDITORY` |
| 1 | 1 | zwei Bereiche anwendbar | `ABSTAIN_AMBIGUOUS_CONTEXT` |

Es gibt keine Konsistenzzulassung, Rangfolge, kleinste-Distanz-Wahl,
Verschmelzung oder Ausweichregel.

## Getrennte auditive Hypothese

Nur `ADMIT_SINGLE_CONTEXT` darf eine unveraenderliche
`AuditoryPartialCueHypothesis48V1` erzeugen. Sie enthaelt:

- genau einen oeffentlichen Bereich `A_RECENT` oder
  `B_STABLE_AUDITORY`;
- genau die 24 maskierten Bandordnungen `24..47`;
- genau die 24 vorgeschlagenen auditiven Kandidatenwerte;
- Probe-, Bandplan-, Slot-, Scan-, Bereichs-, Profil-, Zustands- und
  Hypothesendigest;
- bei A einen oder zwei interne Herkunftsbelege, ohne B4 oder Fast als
  oeffentliche Memoryebene auszugeben.

Die Hypothese enthaelt keine beobachteten Werte, kein PCM, keine
Ersatzwahrnehmung, keinen visuellen Wert, keinen Feldkontakt und keine
Behauptung, dass die vorgeschlagenen Werte bereits wahrgenommen wurden.
S2-KX fuehrt keine Audiovervollstaendigung aus.

## Nichtzirkularitaet und Zielwerttrennung

Ein spaeterer Versuch besitzt getrennte Wurzeln:

```text
FormationPlan -> reale PCM/RGB-Quellen -> MemoryState
CuePlan       -> spaeteres reales PCM -> MaskedAuditoryCue48V1
EvaluationPlan -> verborgene Vollwerte und erwarteter Status
```

Der Formation- und Teilhinweispfad enthalten weder Zielwerte noch den
Evaluationplandigest. Das vollstaendige Zielaudiosignal darf nur der
nachgelagerten Auswertung bekannt sein. Es wird nicht als Probe analysiert,
nicht in den Kandidaten kopiert und nicht als Elternbeleg des Scans verwendet.

Erst ein versiegeltes read-only Funktionsergebnis darf mit dem vorab
versiegelten Evaluationsplan verbunden werden.

## Unabhaengige Pflichtbaseline

Die direkte Slotscan-/Bandmaskenbaseline erhaelt denselben validierten Zustand
und denselben `MaskedAuditoryCue48V1`. Sie implementiert unabhaengig:

1. vollstaendige Iteration ueber `9/3/8` Slots;
2. maskierten L1-Vergleich nur auf `OBSERVED_BANDS`;
3. bankbezogene native Audioschwellen;
4. kardinale Bankbefunde ohne Rangfolge;
5. interne A-Aufloesung;
6. oeffentliche A/B-Kardinalitaet;
7. hoechstens eine getrennte auditive Hypothese.

Die Baseline darf keinen Scan-, Projektions-, Entscheidungs- oder
Hypothesenhelfer der S2-KX-Funktion aufrufen. Beide Arme erhalten identische
Inputs und Budgets. Uebereinstimmung zeigt eine transparente Engineering-
Slotscanfunktion, keine besondere MCM-Physik.

## Ressourcen- und Groessengrenzen

Pro Funktionsarm gelten folgende harte Obergrenzen:

| Ressource | Maximum |
| --- | ---: |
| validierte 336-Werte-Memoryzustaende | 1 |
| auditive Teilhinweise / Bandplaene | `1 / 1` |
| gescannte B4-/Fast-/auditive Slow-Slots | `9 / 3 / 8` |
| gesamte gescannte Slots | 20 |
| beobachtete Distanzterme | `20 x 24 = 480` |
| zusaetzlicher B4/Fast-Vollwertvergleich | 48 |
| gesamte funktionale Wertvergleiche | 528 |
| oeffentliche Bereichskandidaten | hoechstens 2 |
| ausgegebene Hypothesenwerte | 24 oder 0 |
| logische Funktionsoperationen | hoechstens 14 |
| Memory-, Rezeptor-, Verbraucher- oder Feldaufrufe im Scan | 0 |
| kanonische Funktionsausgabe | hoechstens 32.768 Byte |

Funktion und Direktbaseline besitzen dieselben Grenzen. Zusammen gelten
hoechstens 40 Slotpruefungen, 1.056 Wertvergleiche, 28 logische Operationen
und 65.536 Byte kanonische Ergebnisdaten. Der validierte Memoryzustand wird
nicht im Ergebnis dupliziert.

Die spaetere PCM-Materialisierung wird getrennt gezaehlt: pro analysiertem
Fenster exakt zehn Hops und ein Rezeptorabschluss. Konkrete Fixture-,
Formations- und Laufbudgets werden erst nach bestandenem Geometrie-Startgate
literal gebunden; sie duerfen nicht durch eine nachtraegliche Suchschleife
entstehen.

## Read-only- und Fail-closed-Grenze

Vor und nach Funktion sowie Baseline werden identische Digests gebunden fuer:

- den gesamten Composite-Memoryzustand;
- B4;
- TSPM-Fast;
- auditive und visuelle PPB-Bank;
- Teilhinweis und Bandplan.

Der Aufruf stoppt ohne Teilscan, Teilentscheidung oder Teilhypothese bei:

- ungueltiger PCM-, Rezeptor-, Profil-, Quellen- oder Zeitbindung;
- fehlendem, ueberlappendem oder nachtraeglich abgeleitetem Bandplan;
- handgeschriebenen oder aus Zielwerten rekonstruierten 48-Werte-Eingaengen;
- mehr als `9/3/8` Slots oder unvollstaendig validierter FIFO-/Fast-/PPB-
  Anatomie;
- nicht endlichen Werten, Dimensions- oder Digestbruch;
- Zielwerten, Fallrollen oder Sollstatus im Funktionsinput;
- Ressourcen- oder Ausgabegroessenueberschreitung;
- irgendeiner Zustandsmutation.

Beschaedigte Evidenz ist niemals `NO_CONTEXT`, `NO_APPLICABLE_CONTEXT` oder
eine andere regulaere Enthaltung.

## Fachliche Falsifikation

Bei vollstaendig gueltiger Evidenz ist die gebundene Funktion falsifiziert,
wenn:

- eine Vollprobe oder ein zuvor ausgewaehlter Kandidat benoetigt wird;
- ein verdecktes Band oder ein visueller Wert die Kandidatensuche beeinflusst;
- nicht alle drei Banken vollstaendig gescannt werden;
- mehrere Treffer durch Distanz, Support, Alter, Slot-ID oder Reihenfolge
  aufgeloest werden;
- B4 oder Fast als dritter oeffentlicher Bereich erscheint;
- ein interner A-Konflikt oder eine Bankmehrdeutigkeit umgangen wird;
- eine Hypothese mehr oder weniger als 24 maskierte Werte enthaelt;
- Funktion und unabhaengige Baseline bei identischem Eingang abweichen;
- ein read-only Zugriff einen Memory-, Probe- oder Bandplanzustand veraendert.

Ein technisch vollstaendiger spaeterer Lauf mit abweichendem Status ist ein
echter Funktionsbefund. Nur Quellen-, Beleg-, Digest-, Lifecycle- oder
Aufzeichnungsbruch ergibt `NOT_EVALUABLE`.

## Aussagegrenze und naechster Schritt

S2-KX bindet auditiven Teilhinweisabruf direkt aus den beiden bestehenden
Memorybereichen. Es behauptet noch keine reale Materialisierbarkeit der
benoetigten PCM-Geometrie, keinen Funktionslauf, keine Klangsemantik, keine
Crossmodalitaet, keine automatische Maskenerkennung, keine Vervollstaendigung
und keine Feldwirkung.

Als naechster Schritt ist ausschliesslich eine kleine, einmalige PCM-
Materialisierung der acht gebundenen Beziehungsklassen zulaessig. Erst wenn
deren reale 48-Werte-Abstaende das Startgate ohne Suche oder
Schwellenanpassung bestehen, duerfen eine private read-only Slotscanfunktion,
eine unabhaengige Baseline und neutrale Tests implementiert werden. Eine neue
Runner- oder Recorderarchitektur ist dafuer nicht begruendet.
