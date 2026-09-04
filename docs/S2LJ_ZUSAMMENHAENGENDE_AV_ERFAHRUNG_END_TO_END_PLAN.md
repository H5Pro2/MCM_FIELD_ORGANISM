# S2-LJ - Zusammenhaengende AV-Erfahrung bis zum Kontextnutzen

## Status und Ziel

`S2LJ_PRIVATE_INTEGRATION_COMPONENTS_QUALIFIED_MAIN_NOT_RUN`

S2-LJ bindet genau einen endlichen, zusammenhaengenden Funktionspfad:

```text
kanonische RGB-/PCM-Quelle
-> unveraenderte Rezeptoren
-> derselbe reduzierte AV-Zustand an Feld und atomare Zwei-Bereich-Memory
-> Wiederholung und Verdichtung
-> Ablenkung und Verlust aus A_RECENT
-> visueller beziehungsweise auditiver Teilhinweis ohne Vollprobe
-> eindeutige Kontextzulassung oder Enthaltung
-> CURRENT_PERCEPTION_ONLY gegen PLUS_ADMITTED_CONTEXT
```

Der Vertrag fuehrt keine neue Memorymechanik, keine automatische Rangfolge,
keine Semantik und keine Feldrueckwirkung ein. Kontext bleibt eine getrennte
Hypothese und wird nie als beobachteter Rezeptorwert oder Feldkontakt
ausgegeben. Die private Fixture-, Runner- und Verifikatorgrenze ist neutral
qualifiziert; die gebundene Hauptgeschichte wurde nicht ausgefuehrt.

## Gebundener Ausgangsstand

Ausgangscommit ist `6eb03d023717a2cff470a3fc3da2a509e0d5f310`.

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| Default-Live-Rohfixtures | `tools/_s2jx_default_live_memory_fixtures.py` | `5313888d81b946c7ca87f6cf140a04d7810fdb0ecd1eaa0650e9fc1bb1854936` |
| Feldzeitprojektion | `tools/_s2jt_private_timed_field_projection.py` | `91604184325192b6a6291785f713c44fc8fac1d7614234279f635032160c4a4e` |
| AV-Paarung | `tools/_s2jw_default_live_av_pairing.py` | `4ec7d8660bb2269f858db8a025749764b193cd3511934b9ae143bb07359958db` |
| atomare 336-Werte-Memory | `tools/_s2jw_profiled_memory_coordinator.py` | `c9676ea9a740bfb82d66a91c00c559d1ff4d3759bd7bfed12c55afb9820dea81` |
| visueller Teilhinweisscan | `tools/_s2kq_private_partial_cue_retrieval_336.py` | `669e3f7de6957640ed37e79d6608d94d7839d81e959ee1f48d7942526a86e422` |
| visuelle Direktbaseline | `tools/_s2kq_private_direct_slot_scan_baseline.py` | `8e26b07671c901a1a1ab660b39bdf7e6478e39646703c59c4f13af8d47823d28` |
| auditiver Teilhinweisscan | `tools/_s2kz_private_auditory_partial_cue_retrieval_336.py` | `58bb0f7e9265278ced70d38bfe2858081b2e2eb134753c3457e4e03ba01eb04b` |
| auditive Direktbaseline | `tools/_s2kz_private_direct_auditory_slot_scan_baseline.py` | `8d49715c3d59fa5d5b61855a198fb472cbbf3f34a82819e026714f9933084618` |
| visueller read-only Verbraucher | `tools/_s2kk_visual_context_consumer.py` | `9d40a48025b9c2b77bceb737fac50c21f070fb6af6ef9d8c0cda4eac1bad02ec` |
| direkte Fuellbaseline | `tools/_s2kk_context_utility_baselines.py` | `3a9ab561d78a89ba60f6233918ebb6f9e2b65f1e043cc98b2a478fe657c6d57a` |
| bestaetigter visueller Teilhinweisbefund | `reports/s2ks/s2ks-real-partial-cue-336-20260903-02/result.json` | `8ed34a26c7924702b648c2b7f4228175f8e909f6b566718a9f53fa8d31505f9f` |
| bestaetigter auditiver Teilhinweisbefund | `reports/s2ld/s2li-auditory-partial-cue-confirmation-336-20260904-01/result.json` | `a97159bc520476421f34dc2fe673f503ca9b40b5d42bb9bf6bbbf9353fce3ad3` |

Diese Quellen bleiben Referenzen. Alte Ergebnisdateien liefern weder Zustand
noch Kandidaten fuer S2-LJ. Der Lauf muss alle Zustaende frisch bilden.

## Profil und unveraenderte Mechanik

Gebunden bleibt das bestaetigte Default-Live-Profil:

- visuell `1920 x 1080 RGB8`, `12 x 8 x 3 = 288` Werte;
- auditiv mono `PCM_F32LE`, 48 kHz, 4.800 Samples, 48 Werte;
- zusammen 336 reduzierte Wahrnehmungswerte;
- B4-Kapazitaet 9;
- TSPM-Fast-Kapazitaet 3 und gemeinsame Fast-Regel
  `audio <= 0.2 AND visual <= 0.2`;
- auditive PPB-Kapazitaet 8, Schwelle `0.02`;
- visuelle PPB-Kapazitaet 4, Schwelle `0.01`;
- PPB-Update `0.05`, stabil ab Support 3;
- keine 336-zu-26-Kompression und kein Feldsnapshot als Memoryeingang.

Schwellen werden nicht neu kalibriert. Sie gelten nur als vorhandene
mechanische Regeln fuer die gebundene Fixture.

## Eine prospektive Episode

Die Laufseite kennt nur neutrale Quellenordnungen `e01..e15`, eine auditive
Cuequelle `qa16` und eine visuelle Cuequelle `qv17`. Die folgende fachliche
Zuordnung liegt ausschliesslich im getrennt versiegelten Auswertungsplan:

```text
e01 e02 e03 e04  = TARGET_AV
e05 ... e13      = DISTRACTOR_AV_1 ... DISTRACTOR_AV_9
qa16             = TARGET_AUDITORY_PARTIAL_CUE
qv17             = TARGET_VISUAL_OCCLUDED_CUE
```

Die vier Zielbildungen verwenden bitidentische Rohinhalte bei jeweils neuer
Quelle und strikt spaeterem Zeitfenster:

- visuell die bestaetigte Default-Live-X-Fixture;
- auditiv die bestaetigte P-Fixture aus der S2-LI-Linie.

Die neun Distraktoren verwenden:

- visuell die neun getrennten Default-Live-Fixtures D1 bis D9;
- auditiv jeweils den bestaetigten `D_FAR`-Inhalt bei neuer Quelle und Zeit.

Die unterschiedliche visuelle Komponente muss bei jedem Distraktor den
gemeinsamen Fast-Match ausschliessen. Daher aktualisieren die neun
Distraktoren keinen gemeinsamen Fast-Slot und erzeugen keine unbeabsichtigte
Slow-Konsolidierung. Vor dem ersten Memoryaufruf werden alle tatsaechlichen
Rezeptorwerte und diese neun Fast-Entscheidungen einmal gebunden. Bei einer
Abweichung endet die Materialisierung ohne Memorybefund.

Erwartete, aber nicht in den Laufpfad eingespeiste Zustandsfolge:

1. Formation 1 erzeugt die kurzfristige Zielspur.
2. Formationen 2 bis 4 erzeugen drei PPB-Aufrufe und Support 3 in beiden
   Slow-Banken.
3. Formationen 5 bis 13 verdraengen den Zielinhalt vollstaendig aus B4 und
   TSPM-Fast.
4. Der auditive und der visuelle Zielprototyp bleiben in `B_STABLE` stabil.

Ein vollstaendig gueltiger, davon abweichender Memoryverlauf ist eine
funktionale Falsifikation und kein Infrastrukturfehler.

### Verbindliche Slow-Uebergangsableitung

Fuer Audio und Video gilt die qualifizierte S2-LF-Regel getrennt. Der finale
stabile Prototyp wird niemals als bitgleich zum urspruenglichen P- oder
X-Rezeptorvektor vorausgesetzt. Er wird mit exakt derselben Binary64-
Operationsreihenfolge wie PPB-1 aus den drei tatsaechlichen
Konsolidierungseingaengen abgeleitet:

```text
CREATED  support 1: prototype_1 = input_1
MATCHED  support 2: prototype_2 = (1 - 0.05) * prototype_1 + 0.05 * input_2
MATCHED  support 3: prototype_3 = (1 - 0.05) * prototype_2 + 0.05 * input_3
```

Gebunden werden Ereignisreihenfolge, Supportfolge, jeder Eingangsdigest,
jeder resultierende Prototypdigest und der finale Slotdigest. Der tatsaechlich
gespeicherte auditive beziehungsweise visuelle Slow-Prototyp muss exakt dem
jeweils abgeleiteten `prototype_3` entsprechen. Integritaetsgleichheit dieser
Uebergangskette und funktioneller Teilhinweis-Match bleiben zwei getrennte
Befunde; es gibt weder Float-Rundung noch einen Vergleich gegen den
unveraenderten Ausgangsvektor.

## Gemeinsame Quellenbindung fuer Feld und Memory

Jede der 13 Formationen erzeugt genau einen unveraenderlichen gebundenen
AV-Zustand mit getrennten nativen Audio- und Videozeiten. Aus genau diesem
Beleg entstehen zwei Geschwisterprojektionen:

```text
BoundPerception336
|-- Feldprojektion: 48 auditive + 288 visuelle Kontakte
`-- Memoryprojektion: dieselben 48 + 288 Werte und Wertedigests
```

Weder Feld noch Memory darf Werte des anderen Arms lesen. Insbesondere liest
die Memory keinen Feldsnapshot. Der atomare Koordinator gilt nur fuer B4 und
TSPM; S2-LJ behauptet keine neue felduebergreifende Transaktion.

Fuer jeden Bildungsschritt muessen Audio-, Visual-, AV- und
Rezeptorwertedigest in beiden Projektionen identisch sein. Eine Abweichung
ist ein Quellenbruch und ergibt `NOT_EVALUABLE`.

Das Feld beginnt frisch im Nullzustand. Ein zweiter frischer Direktarm
erhaelt dieselben zeitgeordneten Kontakte. Simultane Audio-/Videoabschluesse
bleiben ungeordnet innerhalb derselben Abschlussgruppe. Beobachtungs- und
Direktarm muessen nach jedem Schritt denselben Zustandsdigest besitzen.

## Spaetere Teilhinweise

Nach Formation 13 folgen zwei strikt spaetere, voneinander getrennte
read-only Proben. Es gibt vorher und waehrenddessen keine Vollprobe.

### Auditiver Teilhinweis

Ein neues echtes PCM-Fenster wird durch den unveraenderten Audiorezeptor
analysiert. Die unabhaengige S2-KZ-Bandmaske bindet 24 beobachtete und 24
maskierte Baender. Der Cue verwendet die bestaetigte L-Geometrie gegen den
stabilen P-Prototypen. Die auditive Slotsuche scannt vollstaendig:

```text
9 B4 + 3 Fast + 8 auditive Slow-Slots
```

Vor Memorybeginn muss fuer den konkreten Endbestand belegt sein:

- kein beobachteter A-Treffer gegen `D_FAR`;
- genau ein stabiler auditiver B-Treffer;
- hoechstens 528 Wertvergleiche je Funktionsarm.

### Visueller Teilhinweis

Ein neuer echter RGB8-Frame behaelt die 32 vorab gebundenen sichtbaren
X-Carrier und ersetzt ausschliesslich die 256 maskierten Carrier durch den
gebundenen Okkluderwert. Die Maske ist ein unabhaengiges Artefakt und wird
niemals aus Pixel- oder Rezeptorwerten abgeleitet. Die visuelle Slotsuche
scannt vollstaendig:

```text
9 B4 + 3 Fast + 4 visuelle Slow-Slots
```

Vor Memorybeginn muss fuer den konkreten Endbestand belegt sein:

- kein beobachteter A-Treffer gegen D1 bis D9;
- genau ein stabiler visueller B-Treffer;
- hoechstens 800 Wertvergleiche je Funktionsarm.

Beide Cues besitzen eigene native Quelluhren und Fenster. Gemeinsame
Feldzeit darf die native Zeitvalidierung nicht ersetzen. Die Cuewerte duerfen
den Zustand nur lesen und niemals eine Formation, Fast-Aktualisierung oder
PPB-Aktualisierung ausloesen.

## Zulassung und drei Vergleichsarme

Die beiden Modalitaeten werden getrennt ausgewertet. Es gibt keine
crossmodale Verschmelzung und keine gemeinsame Gewinnerrolle.

Fuer jede Modalitaet gilt nach vollstaendig abgeschlossenem Slotbestand:

- genau ein oeffentlicher Kandidat: `ADMIT_SINGLE_CONTEXT`;
- kein Kandidat: Enthaltung;
- mehr als ein Kandidat oder interner A-Konflikt: Enthaltung;
- beschaedigte Evidenz: fail-closed ohne Hypothese.

Die Zielgeschichte erwartet fuer beide Cues genau einen Kandidaten aus
`B_STABLE`. Eine andere Rolle darf weder bevorzugt noch als Fallback genutzt
werden.

Jede Modalitaet besitzt drei getrennte Arme mit identischem Cue, gleicher
Maske und gleichem Budget:

1. `CURRENT_PERCEPTION_ONLY` behaelt beobachtete Werte und laesst maskierte
   Positionen unbelegt.
2. `CURRENT_PERCEPTION_PLUS_ADMITTED_CONTEXT` uebernimmt nur die Werte der
   zugelassenen Hypothese an den maskierten Positionen.
3. Die unabhaengige Direktbaseline scannt, laesst nach derselben
   Zwei-Bereich-Kardinalitaet zu und fuellt direkt, ohne Produktionshelfer
   fuer Scan, Entscheidung oder Fuellung zu verwenden.

Sichtbare Werte muessen in allen Armen bitidentisch zur aktuellen
Rezeptorwahrnehmung bleiben. Der Plus-Arm darf genau 24 auditive
beziehungsweise 256 visuelle Hypothesenwerte ergaenzen. Die zusammengesetzte
Ausgabe ist eine Kontextrekonstruktion, kein Rezeptorstate und kein
Feldkontakt.

## Feldgrenze

Das Feld erhaelt die 13 vollstaendigen Bildungswahrnehmungen sowie die beiden
tatsaechlichen Teilhinweiswahrnehmungen. Damit entstehen genau 15 geordnete
Feldabschlussgruppen:

- 13 simultane AV-Gruppen mit je 336 Kontakten;
- eine rein auditive Cuegruppe mit 48 Kontakten;
- eine rein visuelle Cuegruppe mit 288 Kontakten.

Das sind 4.704 Feldkontakte je Feldarm. Nach der jeweiligen Cueuebergabe wird
der Felddigest eingefroren. Slot scan, Zulassung, Plus-Arm, Direktbaseline und
Auswertung duerfen keine Feldfunktion aufrufen und muessen den Felddigest
unveraendert lassen.

## Zielwert- und Rollenisolierung

Der Ausfuehrungspfad kennt nur neutrale Quellen-, Zeit-, Masken-, Profil- und
Operationsbindungen. Er enthaelt weder `TARGET`, `CORRECT`, erwartete
Bereichsrollen noch Sollentscheidungen.

Der vorab versiegelte Evaluationsplan ist eine unabhaengige Wurzel. Er bindet:

- die neutrale Quellenordnung an die fachlichen Rollen;
- die vollstaendigen auditiven und visuellen Zielwerte;
- erwartete Support-, Verlust-, Zulassungs- und Armregeln;
- die Verlustfunktion und die terminale Entscheidung.

Erst nach vollstaendig erzeugten Armresultaten darf ein
`EvaluationRunBinding` Ausfuehrungsbeleg und Evaluationsplan verbinden. Ziel-
oder Sollwerte sind keine Eltern von Quelle, Rezeptor, Feld, Formation,
Slotscan, Zulassung oder Verbraucher.

## Read-only- und Zustandsinvarianten

Vor und nach jedem Teilhinweisscan, jeder Zulassung und jedem Arm werden
kanonisch verglichen:

- kompletter Composite-Memorydigest;
- B4-, Fast-, auditory-Slow- und visual-Slow-Digest;
- Feldzustandsdigest;
- Cue-, Masken- und Hypothesendigest.

Memory- und Felddigests muessen vor und nach allen read-only Schritten
identisch sein. Ein Hypothesendigest darf sich nur auf den jeweiligen Cue,
die unabhaengige Maske, den zugelassenen Bereich und die Herkunftsbelege
beziehen.

## Ressourcenobergrenzen

Der spaetere Lauf bleibt innerhalb folgender statischer Maxima:

| Ressource | Grenze |
| --- | ---: |
| Memoryformationen | 13 |
| RGB8-Frames | 14 |
| PCM-Hops zu je 480 Samples | 140 |
| reduzierte Rezeptorabschluesse | 28 |
| Feldabschlussgruppen je Arm | 15 |
| Feldkontakte je Arm | 4.704 |
| Feldkontakte in Beobachtungs- und Direktarm | 9.408 |
| Produktions-Slotscans | 2 |
| unabhaengige Baseline-Slotscans | 2 |
| visuelle Wertvergleiche beider Scans | hoechstens 1.600 |
| auditive Wertvergleiche beider Scans | hoechstens 1.056 |
| Kontext-/Vergleichsarmresultate | 6 |
| funktionale Top-Level-Arbeit | hoechstens 240 Operationen |
| gleichzeitig gehaltene Rohpayloads | hoechstens 1 RGB-Frame und 1 PCM-Hop |
| insgesamt gestreamte Rohbytes | 87.360.000 |

Rohframes und PCM werden nach der jeweiligen Rezeptorreduktion verworfen.
Sie duerfen weder Memory, Feldsnapshot, Kontext, Ergebnis noch Receipt
enthalten. Laufzeit, Spitzen-RSS, kanonische Ergebnisgroesse und die
profilabgeleiteten Memory-L1-Terme muessen vor einer Implementierungsfreigabe
aus den konkreten Aufrufen materialisiert werden; die obigen Grenzen duerfen
dabei nicht erhoeht werden.

## Belegfolge

Die spaetere Beweiskette ist vorwaertsgerichtet:

```text
ExecutionPlanSeal
-> CanonicalSourceReceipt[e01..e15, qa16, qv17]
-> ReceptorReceipt
-> BoundPerception336
-> FieldStepReceipt + AtomicMemoryFormationReceipt[e01..e13]
-> FinalMemoryStateReceipt
-> AuditoryCueReceipt / VisualCueReceipt
-> ProductionSlotScanReceipt / IndependentSlotScanReceipt
-> ContextAdmissionReceipt
-> CurrentOnlyResult / PlusContextResult / DirectBaselineResult
-> ExecutionEvidencePackage

EvaluationPlanSeal
-> EvaluationRunBinding(ExecutionEvidencePackage, EvaluationPlanSeal)
-> FunctionalEvaluation
```

Kein Kind darf einen zukuenftigen Digest enthalten. Eine Hypothese ist kein
Elternbeleg eines Feld- oder Memoryschritts.

## Entscheidung und Falsifikation

`S2LJ_COHERENT_AV_MEMORY_CONTEXT_UTILITY_CONFIRMED` ist nur zulaessig, wenn
gemeinsam gilt:

1. Feld und Memory erhielten in allen 13 Bildungen exakt dieselben reduzierten
   Wahrnehmungswerte aus derselben Quelle.
2. Beide frischen Feldarme erzeugten eine endliche, nichttriviale und
   digestgleiche 15-Punkte-Trajektorie.
3. Der Zielinhalt erreichte in beiden Slow-Banken Support 3 und war nach den
   neun Distraktoren vollstaendig aus B4 und Fast verschwunden.
4. Beide Teilhinweise fanden ohne Vollprobe genau einen passenden
   `B_STABLE`-Kandidaten und keinen A-Kandidaten.
5. `CURRENT_PERCEPTION_ONLY` erfand keinen maskierten Wert.
6. Der Plus-Arm ergaenzte ausschliesslich die 24 auditiven beziehungsweise
   256 visuellen Maskenpositionen und verringerte in beiden Modalitaeten den
   nachgelagert berechneten Rekonstruktionsfehler.
7. Sichtbare Werte, Memory, Feld, Cue, Maske und Zulassungsbelege blieben
   unveraendert.
8. Die unabhaengige Direktbaseline reproduzierte Zulassung und Rekonstruktion
   beider Modalitaeten vollstaendig.

Ein vollstaendiger, technisch gueltiger Lauf mit abweichender Memorybildung,
Kandidatenkardinalitaet, Rekonstruktion oder Baseline ist
`S2LJ_FUNCTION_FALSIFIED`.

Quellen-, Dimensions-, Zeit-, Digest-, Owner-, Ledger-, Read-only- oder
Aufzeichnungsbruch ergibt `NOT_EVALUABLE`. Daraus darf kein Funktionsbefund
abgeleitet werden. Es gibt keinen Retry und keine nachtraegliche
Parameterkorrektur.

## Aussagegrenze und Stopp

Ein spaeteres Bestehen bestaetigt fuer genau diese synthetische, reale
RGB-/PCM-Episode den zusammenhaengenden Pfad Wahrnehmen, Verdichten,
Vergessen, Teilhinweis, eindeutige Zulassung und messbaren Kontextnutzen.

Es bestaetigt keine automatische Maskenerkennung, keine semantische
Erinnerung, keine Rangfolge zwischen mehreren Kontexten, keine Feldwirkung
des Kontextes und keine besondere MCM-Physik. Die unabhaengige direkte
Slotscan-, Kardinalitaets- und Fuellbaseline bleibt die erwartete vollstaendige
Engineeringerklaerung.

Nach einem gueltigen Funktionslauf wird dieser Integrationszweig geschlossen.
Weitere Beleg- oder Runnerinfrastruktur ist nicht Bestandteil von S2-LJ.

## Neutrale technische Qualifikation

Qualifikations-ID:

```text
s2lj-neutral-qualification-20260904-01
```

Einziger Testaufruf:

```text
python -m unittest discover -s tests -p test_s2lj_coherent_av_qualification.py -v
```

Ergebnis:

```text
Ran 12 tests in 0.599s

OK
Exit-Code: 0
```

Die Qualifikation verwendete genau eine neutrale reale Default-Live-Formation
und eine Feldabschlussgruppe. Sie pruefte das geschlossene Hauptgate, reale
`48 + 288`-Rezeptordimensionen, atomare Memorybildung, getrennte frische
Feldarme, die exakte Slow-Kette `CREATED -> MATCHED -> MATCHED`, unabhaengige
read-only Verifikation, Manipulationsablehnung, Unveraenderlichkeit und
atomare Nichtueberschreibung. Die 13 Hauptformationen, beide Teilhinweise,
Slotscans und Funktionsauswertung wurden nicht ausgefuehrt.

Quellhashes waren vor und nach dem Lauf identisch:

| Quelle | SHA-256 |
| --- | --- |
| Fixture | `6ce2c22eb34e798078ccc47bee6bd5323e578051e377532d3db8f8f5319a0cb8` |
| Runner | `5f2b4e568cc44e873720a3ed5facac08aeec589880ac291780d23e4249141bc1` |
| Verifikator | `83441eecb1051ebfd4e007a84e8e096e54dc24a896f9a5df03a367ebd4dd7276` |
| Qualifikationstest | `bdb2a16b01af68ed7b95f01815d04cb2bda035bf57f8465a3f77d6edf08fc3ce` |

Der technische Status lautet `S2LJ_PRIVATE_INTEGRATION_QUALIFIED`. Das
Hauptgate und `AUTHORIZED_RUN_ID` bleiben geschlossen. Es ist kein neuer
Memory-, Kontext- oder Feldfunktionsbefund entstanden.
