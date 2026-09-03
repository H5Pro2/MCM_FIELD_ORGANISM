# S2-KL - Kontrollierte Kontextzulassung bei 336 Werten

## Status und Zweck

`S2KL_STATIC_CONTROLLED_CONTEXT_ADMISSION_336_CONTRACT_COMPLETE`

S2-KL bindet genau eine neue read-only Funktion:

> Fuer eine aktuelle, unabhaengig maskierte visuelle Wahrnehmung werden alle
> vorhandenen visuellen Kandidaten aus `A_RECENT` und `B_STABLE` einzeln auf
> Anwendbarkeit geprueft. Genau ein anwendbarer Kandidat darf als getrennte
> Kontext-Hypothese zugelassen werden. Null oder mehrere anwendbare
> Kandidaten fuehren zur Enthaltung.

Die aktuelle Wahrnehmung wird niemals ergaenzt oder umgeschrieben. S2-KL
erzeugt nur eine gesonderte Hypothese fuer einen spaeteren, ebenfalls
gesonderten Verbraucher. Der Vertrag implementiert und startet nichts.

Nicht freigegeben sind Implementierung, Tests, Runner, Recorder,
Memorybildung, Kontextverbrauch, Feldzugriff, API-Aenderung, Semantik,
Rangfolge, Verschmelzung oder automatische Wahl einer "besten Erinnerung".

## Gebundener Bestand

Technischer Ausgangsstand ist Commit
`1d4bc2a3954cf9f37414c5a95ebc3f9f1980c939`.

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| 336-Werte-Findingbinder | `tools/_s2kj_validated_perceptual_finding_336.py` | `920762c4a29d2baf579829fdb896526c5a2901ffd3629d52ab1658b0436a0b6c` |
| Zwei-Bereich-Kontext 336 | `tools/_s2kj_two_area_perceptual_context_336.py` | `5e2510eb6dd58ffef27901fc545ad700d1f8a5e4d5b3363d09811fe11c0a1d17` |
| S2-KK-Fixture- und Maskengrenze | `tools/_s2kk_context_utility_fixtures.py` | `6b6954381a85704efb6a87c4f1a6a3c49c4d04b4410d19cc3814b0d4077386f6` |
| expliziter S2-KK-B-Verbraucher | `tools/_s2kk_visual_context_consumer.py` | `9d40a48025b9c2b77bceb737fac50c21f070fb6af6ef9d8c0cda4eac1bad02ec` |
| fruehere kontrollierte Zulassungsreferenz | `tools/_s2jh_private_controlled_context_admission.py` | `191c9216703885c24397fabd13dd15d359531445b0b9d4dce70cfda2126258bc` |
| unabhaengige fruehere Tabellenbaseline | `tools/_s2jh_private_direct_admission_baseline.py` | `e151b195d7aa7bda1e4edeee44eb25e83a273f615244409779e5fe525911e340` |
| bestaetigter S2-KK-Funktionsbeleg | `reports/s2kk/s2kk-functional-20260903-02/result.json` | `bc9dce228e30009c2f45280773acb74472ba31f5d27d4821338f96eeec42a589` |

S2-KK ist damit abgeschlossen. Bestaetigt ist der Nutzen eines ausdruecklich
bereitgestellten `B_STABLE_VISUAL`-Kontextes. S2-KL darf diesen Befund nicht
als bereits geloeste Kandidatenauswahl umdeuten.

## Funktionsgrenze

Der einzige zulaessige Pfad lautet:

```text
validierte maskierte 336-Werte-Wahrnehmung
+ validierter TwoAreaPerceptualContext336
-> visuelle Kandidaten einzeln auf sichtbare Vereinbarkeit pruefen
-> Kardinalitaet der anwendbaren Kandidaten bestimmen
-> genau eine getrennte Kontext-Hypothese oder Enthaltung
```

Es findet keine Memoryprobe statt. Die Funktion akzeptiert nur einen bereits
fertigen und validierten `TwoAreaPerceptualContext336` sowie die strikt
spaetere maskierte Wahrnehmung. Alle Quellen-, Probe-, Masken-, Profil-,
Konfigurations-, Zustands- und Bundledigests muessen vor der ersten
Kandidatenpruefung gebunden sein.

Die 48 auditiven Werte bleiben als Teil des 336-Werte-Profils und der
Quellenprovenienz erhalten. Sie duerfen fuer diese rein visuelle
Maskenaufgabe jedoch keinen visuellen Kandidaten bevorzugen, ausschliessen
oder ersetzen. Eine spaetere audiovisuelle Zulassung benoetigt einen eigenen
modalitaetsgetrennten Vertrag.

## Kandidateninventar

Es existieren hoechstens drei visuelle Kandidatenrollen in kanonischer, aber
nicht priorisierender Reihenfolge:

```text
A_RECENT.B4_RECENT.visual
A_RECENT.TSPM_FAST.visual
B_STABLE.VISUAL
```

Ein interner A-Kandidat muss aus einem gueltigen 336-Werte-AV-Kandidaten
stammen; S2-KL liest daraus ausschliesslich dessen 288 visuelle Werte. Der
B-Kandidat muss ein stabiler visueller 288-Werte-Kandidat mit Support
mindestens 3 sein.

Jede Rolle bleibt auch bei identischen Werten ein eigener Kandidat. B4 und
Fast werden weder verschmolzen noch als dritte oeffentliche Memoryebene
dargestellt. Zwei anwendbare Rollen sind daher immer mehrdeutig, selbst wenn
ihre maskierten Vorschlaege zufaellig gleich sind. S2-KL uebernimmt nicht die
fruehere S2-JH-Regel, nach der zwei gleichwertige Rollen gemeinsam zugelassen
werden konnten.

`B_STABLE_AUDITORY` bleibt im Eingangscontext transparent gebunden, ist aber
kein visueller Fuellkandidat.

## Masken- und Beobachtungsgrenze

Die Positionsmaske ist ein unabhaengiger unveraenderlicher Beleg. Sie darf
weder aus Nullwerten noch aus Kandidaten, Zielwerten oder Auswertungsrollen
abgeleitet werden.

Fuer jede Position gilt genau eine Rolle:

- `OBSERVED`: echter aktueller Rezeptorwert; darf nur verglichen und niemals
  veraendert werden;
- `MASKED`: kein beobachteter Zielwert; darf die Anwendbarkeitsentscheidung
  nicht beeinflussen und erscheint nur in einer spaeteren Kontext-Hypothese.

Der aktuelle S2-KK-Fall besitzt 32 sichtbare und 256 maskierte visuelle
Positionen. Eine Implementierung darf diese erste feste Geometrie verwenden,
aber keine Maske automatisch erkennen.

## Anwendbarkeit eines Kandidaten

Jeder vorhandene Kandidat wird separat gegen dieselbe aktuelle Probe und
dieselbe Maske geprueft. Ein Kandidat ist `APPLICABLE`, wenn gemeinsam gilt:

1. Rolle, Dimension, Herkunft, Slot, Zustand und Kandidatendigest sind
   vollstaendig gueltig;
2. sein Finding gehoert exakt zum gebundenen Kontextbundle;
3. alle 32 beobachteten visuellen Positionen sind mit der aktuellen
   Wahrnehmung nachweislich gleich;
4. kein maskierter Wert wurde fuer diese Entscheidung gelesen;
5. Vor- und Nachzustandsdigests sind identisch.

Im ersten S2-KL-Umfang ist die sichtbare Gleichheit nur fuer prospektiv
gebundene, exakt gleiche Rezeptorwerte zulaessig. Der bestaetigte S2-KK-Fall
verwendet auf allen sichtbaren Positionen den exakten Wert `0.0`, der durch
die homogene Prototypaktualisierung unveraendert bleibt. Eine pauschale
Float-Rundung oder eine neue L1-Schwelle ist verboten.

Nichtnull-Prototypwerte duerfen spaeter nur mit prospektiv vorhandener
rezeptorgetreuer Gleichheitsevidenz zugelassen werden. Fehlt diese Evidenz,
ist der Kandidat nicht als regulaer unpassend umzudeuten; der gesamte Aufruf
stoppt fail-closed.

Ein gueltiger vorhandener Kandidat mit mindestens einer belegten sichtbaren
Abweichung erhaelt `VISIBLE_CONFLICT`. Ein gueltig abwesender Rollenbefund
bleibt `ABSENT_VALID`. Beschaedigte oder unvollstaendige Evidenz erhaelt
keinen regulaeren Anwendbarkeitsstatus.

## Verbindliche Entscheidungstabelle

Nach vollstaendiger Einzelpruefung wird ausschliesslich die Anzahl
`APPLICABLE` ausgewertet:

| vorhandene Kandidaten | anwendbare Kandidaten | Entscheidung | Ergebnis |
| ---: | ---: | --- | --- |
| 0 | 0 | `ABSTAIN_NO_CONTEXT` | keine Hypothese |
| mindestens 1 | 0 | `ABSTAIN_NO_APPLICABLE_CONTEXT` | keine Hypothese |
| mindestens 1 | exakt 1 | `ADMIT_SINGLE_CONTEXT` | genau eine getrennte Hypothese |
| mindestens 2 | mindestens 2 | `ABSTAIN_AMBIGUOUS_CONTEXT` | keine Hypothese |

Es gibt keine Rangfolge nach Bereich, Aktualitaet, Support, Distanz,
Slotreihenfolge oder Listenposition. Es gibt keinen Fallback und keine
Teilzulassung.

## Ausgabeform

Ein spaeteres unveraenderliches `ControlledContextAdmission336V1` bindet:

- Entscheidung und neutralen Grund;
- Probe-, Masken-, Kontextbundle-, Konfigurations- und Zustandsdigest;
- die drei Rollenbefunde in kanonischer Reihenfolge;
- Anzahl vorhandener und anwendbarer Kandidaten;
- bei genau einem Treffer dessen Rolle, Finding-, Kandidaten- und
  Wertedigest;
- getrennten Hypothesendigest;
- Read-only-Vor-/Nachzustandsdigests;
- Ressourcenledger und eigenen Ergebnisdigest.

Die optionale `ContextHypothesis336V1` enthaelt ausschliesslich:

- die eine zugelassene Kandidatenrolle und ihre Herkunft;
- exakt die 256 maskierten Positionen;
- exakt die 256 vorgeschlagenen visuellen Werte;
- Masken-, Probe-, Kandidaten-, Kontext- und Hypothesendigest;
- `observed_value_count = 0` und `field_contact_count = 0`.

Sie enthaelt keinen vollstaendig zusammengesetzten Wahrnehmungsvektor. Die
32 beobachteten Werte bleiben ausschliesslich Bestandteil der unveraenderten
Probe. Vorgeschlagene Werte duerfen weder als Rezeptoroutput noch als
Feldkontakt, Beobachtung oder Memoryzustand bezeichnet werden.

Bei Enthaltung ist `hypothesis = null`. Bei einem Fehler entsteht weder eine
Teilentscheidung noch eine Teilhypothese.

## Vier minimale Funktionsfaelle

Die spaetere prospektive Qualifikation beziehungsweise Funktionspruefung muss
mindestens folgende Rollenlagen enthalten. Die Fallnamen sind nur
Auswertungsmetadaten und gelangen nicht in Funktion oder Kandidaten.

### Korrekt

Genau ein visueller Kandidat ist `APPLICABLE`; alle anderen Rollen sind
`ABSENT_VALID` oder `VISIBLE_CONFLICT`. Erwartet werden
`ADMIT_SINGLE_CONTEXT` und genau eine getrennte 256-Werte-Hypothese.

### Falsch

Ein vorhandener Kandidat widerspricht mindestens einer sichtbaren Position;
kein anderer Kandidat ist anwendbar. Erwartet werden
`ABSTAIN_NO_APPLICABLE_CONTEXT` und keine Hypothese.

### Fehlend

Alle drei visuellen Rollen sind `ABSENT_VALID`. Erwartet werden
`ABSTAIN_NO_CONTEXT` und keine Hypothese.

### Mehrdeutig

Mindestens zwei getrennte Rollen sind auf allen sichtbaren Positionen
anwendbar. Ihre maskierten Werte duerfen verschieden oder gleich sein.
Erwartet werden immer `ABSTAIN_AMBIGUOUS_CONTEXT` und keine Hypothese.
Vertauschungen der Rollenbelegung duerfen die Entscheidung nicht aendern.

## Read-only- und Nichtzirkularitaetsgrenze

Der einzige zulaessige Digestgraph ist:

```text
fruehere Wahrnehmungsquellen -> fertiger A/B-Memoryzustand
-> validiertes read-only Finding -> TwoAreaPerceptualContext336

spaetere maskierte Wahrnehmungsquelle -> unabhaengige Maske

Kontext + maskierte Probe + Maske
-> einzelne Anwendbarkeitsbefunde
-> Kardinalitaetsentscheidung
-> optionale getrennte Kontext-Hypothese

vollstaendiges Ziel -> ausschliesslich spaetere Auswertung
```

Zielwerte, Sollentscheidung, Fallname, Verlustwert und Baselineergebnis sind
keine Eltern des Funktionspfads. Kandidaten duerfen nicht aus der spaeteren
Probe rekonstruiert werden. Ein spaeterer Fuell- oder Evaluationsbefund darf
die Zulassung nicht rueckwirkend begruenden.

Memory-, Probe-, Bundle-, Finding- und Feldzustand bleiben vor und nach dem
Aufruf digestgleich. S2-KL ruft keine Rezeptor-, Memory-, Kontextabruf-,
Lern-, Konsolidierungs-, Verbraucher- oder Feldfunktion auf.

## Ressourcenbindung

Pro Aufruf gelten folgende Obergrenzen:

| Ressource | Maximum |
| --- | ---: |
| validierte maskierte Proben | 1 |
| validierte 336-Werte-Kontextbundles | 1 |
| visuelle Kandidatenrollen | 3 |
| referenzierte Kontextwerte im Eingang | hoechstens 1.008 |
| inspizierte visuelle Kandidatenwerte | hoechstens `3 x 288` |
| sichtbare Vergleiche | `3 x 32 = 96` |
| maskierte Werte in einer Hypothese | 256 oder 0 |
| logische Funktionsoperationen | 8 |
| neue Memory-, Rezeptor-, Verbraucher- oder Feldaufrufe | 0 |
| serialisierte Ausgabe | 32.768 Byte |

Die acht maximalen Operationen sind Eingangsvalidierung, Inventarbildung,
bis zu drei Einzelpruefungen, Kardinalitaetsentscheidung, optionale
Hypothesenprojektion sowie Read-only-/Ledgerabschluss. Nicht ausgefuehrte
optionale Arbeit wird nicht als kostenloser Funktionsgewinn gezaehlt.

Die Ausgabe darf das 65.536-Byte-Kontextbundle nicht erneut serialisieren.
Sie bindet dessen Digest und uebernimmt nur die eine optionale
256-Werte-Hypothese. Konkrete kanonische Bytegroessen sind vor einer
Implementierung mit den finalen Datentypen statisch zu materialisieren.

## Unabhaengige Pflichtbaseline

Die staerkste Baseline implementiert unabhaengig dieselbe generische
Zulassungs- und Hypothesenregel:

1. alle drei visuellen Rollen einzeln gegen die sichtbaren Positionen
   pruefen;
2. Anzahl anwendbarer Kandidaten zaehlen;
3. nur bei exakt eins dessen maskierte Werte als getrennte Hypothese
   projizieren;
4. sonst ohne Hypothese enthalten.

Sie erhaelt identische Eingaben und Budgets, darf aber weder die spaetere
S2-KL-Funktion noch deren Zwischen- oder Endergebnis aufrufen. Vollstaendige
Gleichheit ist der erwartete Engineeringbefund und kein Nachweis besonderer
MCM-Physik.

## Fail-Closed-Regeln

Ohne Ausgabe abzubrechen ist bei:

- falschem Typ, Profil oder Dimension ungleich `48 + 288`;
- fehlender, doppelter oder falsch angeordneter Rollenquelle;
- fremdem Probe-, Masken-, Kontext-, Konfigurations- oder Zustandsdigest;
- ungleichen Vor-/Nachzustandsdigests;
- instabilem oder nicht mechanisch passendem B-Kandidaten;
- Kandidat bei `ABSENT_VALID` oder fehlendem Kandidaten bei `AVAILABLE`;
- fehlender Herkunft fuer eine behauptete sichtbare Gleichheit;
- Lesen einer maskierten Position waehrend der Anwendbarkeitspruefung;
- mehr als drei Kandidaten oder irgendeiner Ressourcenueberschreitung;
- Teilhypothese, Rollenfallback, Rangfolge, Verschmelzung oder Feldwirkung.

Gueltige Abwesenheit, sichtbarer Konflikt und Mehrdeutigkeit sind regulaere
Ergebnisse. Beschaedigte Evidenz ist dagegen niemals `NO_CONTEXT`,
`NO_APPLICABLE_CONTEXT` oder `AMBIGUOUS_CONTEXT`, sondern methodisch
ungueltig.

## Falsifikation und Aussagegrenze

Bei vollstaendig gueltiger Beweiskette ist S2-KL fachlich falsifiziert, wenn:

- genau ein anwendbarer Kandidat nicht als getrennte Hypothese zugelassen
  wird;
- null anwendbare Kandidaten irgendeine Hypothese erzeugen;
- mindestens zwei anwendbare Kandidaten eine Auswahl oder Ergaenzung
  erzeugen;
- ein nicht zugelassener Kandidat Werte oder Entscheidung beeinflusst;
- beobachtete Werte veraendert oder Hypothesenwerte als Beobachtung
  beziehungsweise Feldkontakt ausgegeben werden;
- Funktion und unabhaengige Baseline bei identischen gueltigen Eingaben
  abweichen;
- irgendein Read-only-Zustand veraendert wird.

`NOT_EVALUABLE` gilt ausschliesslich bei unvollstaendiger, fremder,
widerspruechlicher oder beschaedigter Quellen-, Rollen-, Owner-, Digest-,
Zustands-, Gleichheits- oder Ledgerbindung.

Ein spaeteres Bestehen bestaetigt nur kontrollierte visuelle
Kontextzulassung bei 336 Werten: Das System kann feststellen, ob genau eine
vorhandene Erfahrung mit den beobachteten Teilen der aktuellen Wahrnehmung
vereinbar ist. Nicht nachgewiesen sind automatische Maskenerkennung,
semantische Relevanz, Objektverstaendnis, eine beste Erinnerung,
Feldrueckwirkung oder neue MCM-Physik.

Nach statischer Abnahme kann unmittelbar eine kleine private reine
Zulassungsfunktion, eine unabhaengige Baseline und eine fokussierte neutrale
Qualifikation folgen. Neue Runner-, Recorder- oder Plattforminfrastruktur
ist dafuer nicht begruendet.
