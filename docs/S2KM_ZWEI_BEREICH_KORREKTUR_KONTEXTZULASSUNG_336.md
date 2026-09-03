# S2-KM - Zwei-Bereich-Korrektur der Kontextzulassung 336

## Status und Korrekturumfang

`S2KM_STATIC_TWO_AREA_CONTEXT_ADMISSION_CORRECTION_COMPLETE`

S2-KM korrigiert ausschliesslich den Architekturfehler im
Kandidateninventar und in der Kardinalitaetsentscheidung von S2-KL. B4 und
Fast bleiben intern getrennte Evidenzrollen von `A_RECENT`; sie sind keine
zwei oeffentlichen Memorybereiche und keine eigenstaendigen oeffentlichen
Kandidatenautoritaeten.

Der oeffentliche Zulassungsraum besitzt exakt zwei Bereiche:

```text
A_RECENT
B_STABLE
```

Alle S2-KL-Regeln zu getrennter Hypothese, unveraenderter aktueller
Wahrnehmung, unabhaengiger Maske, Zielwerttrennung, Read-only-Nutzung,
fehlender Feldwirkung und unabhaengiger Direktbaseline bleiben unveraendert.

S2-KM ist rein statisch. Implementierung, Tests, Runner, Recorder,
Memoryaufrufe, Kontextverbrauch und Feldzugriff bleiben gesperrt.

## Gebundener Ausgangsstand

Technischer Ausgangsstand ist Commit
`027fc15085abf175e45f0a0aaa1485924f73f742`.

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| zu korrigierender S2-KL-Vertrag | `docs/S2KL_KONTROLLIERTE_KONTEXTZULASSUNG_336_VERTRAG.md` | `641ef52f58ae63e40e46362a55ae735b42940c19fcfcb99662475a7bcec798b6` |
| Zwei-Bereich-Kontext 336 | `tools/_s2kj_two_area_perceptual_context_336.py` | `5e2510eb6dd58ffef27901fc545ad700d1f8a5e4d5b3363d09811fe11c0a1d17` |
| 336-Werte-Findingbinder | `tools/_s2kj_validated_perceptual_finding_336.py` | `920762c4a29d2baf579829fdb896526c5a2901ffd3629d52ab1658b0436a0b6c` |

Der S2-KL-Quelldigest bezeichnet den unveraenderten Ausgangsvertrag vor der
hier dokumentierten Sperrnotiz. S2-KM ersetzt darin nur die Abschnitte
`Kandidateninventar`, `Verbindliche Entscheidungstabelle`, die davon
abhaengigen Ausgabe- und Ressourcenangaben sowie die entsprechenden
Falsifikationsregeln.

## Interne und oeffentliche Rollen

Die unveraenderte technische Eingangsstruktur lautet:

```text
TwoAreaPerceptualContext336
  A_RECENT
    B4_RECENT       interne AV-Evidenz
    TSPM_FAST       interne AV-Evidenz
  B_STABLE
    AUDITORY        modalitaetsgetrennte Evidenz, kein visueller Kandidat
    VISUAL          visueller Bereichskandidat
```

Die interne Pruefung darf weiterhin hoechstens drei visuelle Wertquellen
sehen:

```text
A_RECENT.B4_RECENT.visual
A_RECENT.TSPM_FAST.visual
B_STABLE.VISUAL
```

Nach der Einzelpruefung duerfen aber hoechstens zwei oeffentliche
Bereichskandidaten entstehen. Eine spaetere Hypothese nennt ausschliesslich
`A_RECENT` oder `B_STABLE`. B4 und Fast erscheinen nur in der
Herkunftsevidenz des A-Befunds.

## Interne A-Projektion

B4 und Fast werden zuerst separat nach den unveraenderten S2-KL-Regeln
validiert und gegen die sichtbaren Positionen geprueft. Jeder interne Befund
besitzt genau einen der regulaeren Zustaende:

```text
ABSENT_VALID
APPLICABLE
VISIBLE_CONFLICT
```

Beschaedigte, unvollstaendige oder fremde Evidenz besitzt keinen regulaeren
Zustand und stoppt den gesamten Aufruf fail-closed.

Erst nach beiden gueltigen internen Befunden wird ein
`ARecentApplicability336V1` projiziert:

| B4 | Fast | oeffentlicher A-Befund |
| --- | --- | --- |
| `ABSENT_VALID` | `ABSENT_VALID` | `A_RECENT_ABSENT_VALID`, kein Kandidat |
| `APPLICABLE` | `ABSENT_VALID` oder `VISIBLE_CONFLICT` | `A_RECENT_APPLICABLE`, B4-Werte, ein Herkunftsbeleg |
| `ABSENT_VALID` oder `VISIBLE_CONFLICT` | `APPLICABLE` | `A_RECENT_APPLICABLE`, Fast-Werte, ein Herkunftsbeleg |
| `APPLICABLE` | `APPLICABLE`, exakt wertgleich | `A_RECENT_APPLICABLE`, ein A-Kandidat, zwei Herkunftsbelege |
| `APPLICABLE` | `APPLICABLE`, nicht wertgleich | `A_RECENT_INTERNAL_CONFLICT`, kein oeffentlicher A-Kandidat |
| kein `APPLICABLE`, mindestens ein `VISIBLE_CONFLICT` | entsprechend | `A_RECENT_NOT_APPLICABLE`, kein Kandidat |

Exakte Wertgleichheit bindet denselben validierten 288-Werte-Tupelinhalt und
denselben Wertedigest. Es wird kein Mittelwert gebildet, keine Rolle
bevorzugt und kein Kandidat kopiert. Die beiden Finding- und
Kandidatendigests bleiben als getrennte Herkunftsbelege erhalten.

Sind beide internen Kandidaten anwendbar, aber verschieden, ist
`A_RECENT_INTERNAL_CONFLICT` ein gueltiger fachlicher Befund. Er ist weder
`ABSENT_VALID` noch beschaedigte Evidenz. Er darf keinen A-Kandidaten und
keine Teilhypothese erzeugen.

## B-Projektion

`B_STABLE_VISUAL` wird nach der unveraenderten S2-KL-Anwendbarkeitsregel
geprueft und genau einmal auf den oeffentlichen Bereich B abgebildet:

| interner Slow-Befund | oeffentlicher B-Befund |
| --- | --- |
| `ABSENT_VALID` | `B_STABLE_ABSENT_VALID`, kein Kandidat |
| `APPLICABLE` | `B_STABLE_APPLICABLE`, genau ein Kandidat |
| `VISIBLE_CONFLICT` | `B_STABLE_NOT_APPLICABLE`, kein Kandidat |

Instabiler, nicht mechanisch passender, falsch dimensionierter oder fremder
Slow-Befund bleibt ein Evidenzfehler und wird nicht in regulaere Abwesenheit
umgedeutet. Der auditive Slow-Befund bleibt transparent gebunden, erzeugt
aber in dieser visuellen Aufgabe keinen B-Kandidaten.

## Oeffentliche Kardinalitaetsentscheidung

Die Zulassung wird erst nach abgeschlossener A- und B-Projektion gebildet.
Sie zaehlt ausschliesslich oeffentliche Bereichskandidaten, niemals interne
B4-/Fast-Rollen.

Zuerst gilt die harte interne Konfliktgrenze:

```text
A_RECENT_INTERNAL_CONFLICT
-> ABSTAIN_A_RECENT_INTERNAL_CONFLICT
-> keine Hypothese
```

Diese Enthaltung gilt auch dann, wenn B fuer sich anwendbar waere. Ein
ungeloester interner A-Widerspruch darf nicht durch B umgangen oder als
SINGLE_SOURCE umetikettiert werden.

Ohne internen A-Konflikt gilt:

| A-Kandidat | B-Kandidat | Entscheidung | Hypothese |
| ---: | ---: | --- | --- |
| nein | nein, beide Bereiche abwesend | `ABSTAIN_NO_CONTEXT` | keine |
| nein | nein, mindestens ein Bereich unpassend | `ABSTAIN_NO_APPLICABLE_CONTEXT` | keine |
| ja | nein | `ADMIT_SINGLE_CONTEXT` | `A_RECENT` |
| nein | ja | `ADMIT_SINGLE_CONTEXT` | `B_STABLE` |
| ja | ja | `ABSTAIN_AMBIGUOUS_CONTEXT` | keine |

Auch exakt gleiche anwendbare A- und B-Kandidaten bleiben zwei oeffentliche
Bereichskandidaten und fuehren zur Enthaltung. S2-KM fuehrt keine
`CONSISTENT`-Sonderzulassung, Rangfolge oder Bereichspraeferenz ein.

## Korrigierte Ausgabeform

Das spaetere `ControlledContextAdmission336V1` bindet:

- genau einen `ARecentApplicability336V1`;
- genau einen `BStableApplicability336V1`;
- hoechstens zwei oeffentliche Bereichskandidaten;
- interne B4- und Fast-Befunddigests ausschliesslich innerhalb der
  A-Herkunft;
- oeffentliche Kandidatenanzahl und Zulassungsentscheidung;
- bei `ADMIT_SINGLE_CONTEXT` genau einen Bereich aus
  `A_RECENT | B_STABLE`;
- Probe-, Maske-, Kontext-, Konfigurations-, Zustands-, Ledger- und
  Ergebnisdigest;
- identische Read-only-Vor-/Nachzustandsdigests.

Die optionale `ContextHypothesis336V1` nennt nur den zugelassenen Bereich.
Bei `A_RECENT` bindet sie zusaetzlich einen oder zwei interne
Herkunftsbelege, ohne B4 oder Fast nach aussen zu einem Bereich zu erheben.
Bei `B_STABLE` bindet sie den visuellen Slow-Kandidatendigest.

Sie enthaelt weiterhin nur die maskierten Positionen und deren
vorgeschlagene Werte. Beobachtete Werte, Rezeptoroutput, Feldkontakte und ein
vollstaendig zusammengesetzter Wahrnehmungsvektor bleiben ausgeschlossen.

## Korrigierte minimale Fallmatrix

Eine spaetere neutrale Qualifikation muss mindestens abdecken:

1. beide internen A-Rollen abwesend;
2. nur B4 anwendbar ergibt genau einen `A_RECENT`-Kandidaten;
3. nur Fast anwendbar ergibt genau einen `A_RECENT`-Kandidaten;
4. B4 und Fast anwendbar und wertgleich ergeben genau einen A-Kandidaten mit
   zwei Herkunftsbelegen;
5. B4 und Fast anwendbar, aber verschieden ergeben
   `A_RECENT_INTERNAL_CONFLICT` und Enthaltung;
6. nur `B_STABLE_VISUAL` anwendbar ergibt genau einen B-Kandidaten;
7. A und B gleichzeitig anwendbar ergeben `ABSTAIN_AMBIGUOUS_CONTEXT`;
8. vorhandene, aber nur sichtbar widerspruechliche Rollen ergeben
   `ABSTAIN_NO_APPLICABLE_CONTEXT`;
9. vollstaendige gueltige Abwesenheit ergibt `ABSTAIN_NO_CONTEXT`;
10. jede beschaedigte interne oder oeffentliche Evidenz stoppt ohne Ausgabe.

Die Faelle 2 und 3 sowie vertauschte A-/B-Inhalte muessen dieselben
funktionalen Budgets besitzen. Interne B4-/Fast-Reihenfolge darf weder
A-Werte noch Endentscheidung beeinflussen.

## Korrigierte Ressourcenbindung

Pro Aufruf gelten hoechstens:

| Ressource | Maximum |
| --- | ---: |
| validierte maskierte Proben | 1 |
| validierte `TwoAreaPerceptualContext336` | 1 |
| interne visuelle Rollenpruefungen | 3 |
| oeffentliche Bereichsbefunde | 2 |
| oeffentliche Bereichskandidaten | 2 |
| referenzierte Kontextwerte im Eingang | 1.008 |
| sichtbare Anwendbarkeitsvergleiche | `3 x 32 = 96` |
| interne B4-/Fast-Wertgleichheitsvergleiche | hoechstens 288 |
| gesamte Wertvergleiche | hoechstens 384 |
| maskierte Hypothesenwerte | 256 oder 0 |
| logische Funktionsoperationen | 10 |
| Memory-, Rezeptor-, Verbraucher- oder Feldaufrufe | 0 |
| serialisierte Ausgabe | hoechstens 32.768 Byte |

Die zehn Operationen sind Eingangsvalidierung, Inventarbildung, drei
interne Rollenpruefungen, A-Projektion, oeffentliche Kardinalitaet und
Konfliktentscheidung, optionale Hypothesenprojektion, Read-only-Abgleich
sowie Ledger-/Digestabschluss.

Die Ausgabe serialisiert weder das vollstaendige Kontextbundle noch doppelte
A-Werte. Bei zwei wertgleichen internen A-Rollen werden die Werte einmal und
die beiden Herkunftsdigests getrennt gebunden. Die konkrete kanonische
Ausgabegroesse muss vor Implementierung gegen die 32.768-Byte-Grenze
materialisiert werden.

## Korrigierte Direktbaseline

Die unabhaengige Pflichtbaseline muss dieselbe Zwei-Stufen-Struktur separat
implementieren:

1. B4 und Fast einzeln pruefen;
2. daraus genau einen A-Bereichsbefund oder internen A-Konflikt bilden;
3. B-Stable separat pruefen;
4. erst danach zwischen maximal zwei oeffentlichen Bereichen entscheiden;
5. nur bei exakt einem oeffentlichen Kandidaten eine getrennte Hypothese
   projizieren.

Die Baseline darf weder die spaetere S2-KM-Funktion noch deren A-Projektion,
Entscheidung oder Ergebnis aufrufen. Identische gueltige Eingaben und
identische Ressourcenobergrenzen sind verbindlich.

## Fail-Closed- und Falsifikationskorrektur

Zusaetzlich zu S2-KL stoppt die Funktion ohne Ausgabe bei:

- Verlust eines internen B4- oder Fast-Befunds waehrend der A-Projektion;
- Ausgabe von B4 oder Fast als oeffentlicher Bereich;
- mehr als einem oeffentlichen A-Kandidaten;
- behaupteter Wertgleichheit ohne identischen validierten Tupelinhalt und
  Wertedigest;
- A-Hypothese ohne vollstaendige interne Herkunftsbelege;
- Umdeutung eines internen Konflikts in Abwesenheit, Single-Source oder
  einen B-Fallback;
- mehr als zwei oeffentlichen Kandidaten.

Bei vollstaendig gueltiger Evidenz ist S2-KM fachlich falsifiziert, wenn:

- wertgleiche anwendbare B4-/Fast-Befunde mehr als einen A-Kandidaten
  erzeugen;
- verschiedene anwendbare B4-/Fast-Befunde keinen internen Konflikt und
  keine Enthaltung erzeugen;
- die Kardinalitaet interne Rollen statt A/B-Bereiche zaehlt;
- eine Hypothese B4 oder Fast statt `A_RECENT` nennt;
- A und B gleichzeitig anwendbar sind und trotzdem eine Rolle zugelassen
  wird;
- Funktion und unabhaengige Zwei-Bereich-Baseline voneinander abweichen;
- beobachtete Wahrnehmung oder irgendein Read-only-Zustand veraendert wird.

Gueltiger `A_RECENT_INTERNAL_CONFLICT` ist eine fachliche Enthaltung.
Beschaedigte, fehlende oder widerspruechlich gebundene Evidenz bleibt dagegen
`NOT_EVALUABLE` und darf niemals als regulaerer Konflikt erscheinen.

## Aussagegrenze und naechster Schritt

S2-KM stellt das Zwei-Bereich-Modell wieder her. Intern bleiben B4 und Fast
vollstaendig pruefbar; oeffentlich entstehen dennoch nur `A_RECENT` und
`B_STABLE`. Eine spaetere Zulassung kann deshalb hoechstens genau einen
Memorybereich autorisieren und niemals eine interne Implementierungsrolle
als dritte Memorysicht veroeffentlichen.

Ein spaeteres Bestehen waere weiterhin nur eine kontrollierte visuelle
Kontextzulassung bei 336 Werten. Automatische Maskenerkennung, Semantik,
Objektverstaendnis, Feldrueckwirkung und besondere MCM-Physik bleiben
unbelegt.

Nach statischer Abnahme darf unmittelbar eine kleine private
A-Bereichsprojektion mit Zulassungsfunktion, unabhaengiger Baseline und
fokussierten neutralen Tests implementiert werden. Neue Runner-, Recorder-
oder Plattforminfrastruktur ist nicht erforderlich.
