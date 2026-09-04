# S2-LF - PPB-Prototypdigest und funktionale Inhaltsgleichheit

## Status und Grenze

`S2LF_STATIC_PPB_TRANSITION_EXPECTATION_CORRECTION_BOUND`

S2-LF korrigiert ausschliesslich die prospektive LC02-Erwartung fuer den
fortgeschriebenen auditiven PPB-1-Prototyp. Der technisch vollstaendige Lauf
S2-LE bleibt unveraendert und formal
`S2LD_FUNCTION_FALSIFIED`. Seine Ergebnisdatei wird weder repariert noch neu
bewertet.

Unveraendert bleiben:

- die vier Memorygeschichten und der Nullzustand;
- alle 30 Formationen und sechs auditiven Teilhinweise;
- die Rezeptorwerte, Memorykerne und Slotkapazitaeten;
- `update_rate = 0.05`, `stable_after = 3` und Slow-Schwelle `0.02`;
- der vollstaendige read-only `9/3/8`-Scan und die unabhaengige Direktbaseline;
- das Verbot von Vollprobe, Rundung, Schwellenanpassung, Kontextfuellung und
  Feldkopplung.

## Gebundene Quellen

Ausgangsstand ist Commit
`c5da9653cabdd70a12313233b96af3698d95db1e`.

| Rolle | Quelle | gebundener SHA-256 |
| --- | --- | --- |
| PPB-1-Uebergang | `mcm_field_organism/_ppb1_reference.py` | `15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0` |
| S2-KY-Rezeptorwerte | `reports/s2kx/s2ky-auditory-partial-cue-geometry-20260903-01/materialization.json` | `87ac9aed39e6f3cd63f4d3cee24873a7e67357ce5cd9e5ed1ccc353d407d1dc3` |
| S2-LC-Zustandsspur | `docs/S2LC_AUDITIVER_MEMORY_SECHS_FALL_ZUSTANDSSPUR.md` | `f74f4bb44399dab09d1c2ce01762183467277fe97a7abe682813a879c3144979` |
| S2-LE-Ergebnis | `reports/s2ld/s2ld-real-auditory-partial-cue-336-20260904-01/result.json` | `827597089a5b2e93c80d12ef50d326bfa79ebc47281770f1b2c6708e9218b06f` |

Die Ableitung verwendet ausschliesslich den bereits materialisierten
48-Werte-Rezeptorvektor `CANDIDATE_PLUS` und die literale PPB-1-Formel. Sie
ruft weder Rezeptoren noch PPB-1, TSPM-1, B4 oder den Koordinator auf.

## Exakte Uebergangskette

Der Eingangsvektor jeder P-Formation ist bitidentisch. Seine kanonischen
Digests sind:

```text
P, 48 Werte:          dc28fbb4ee22315131333a2c871ee82d958600d832a05c7d972db1e3acb4a023
P, Positionen 24..47: 1622004a498c487579e941a9b99193eded1a966420f916140251e21933ee1ba9
```

Die vier Formationen bewirken:

| Formation | Fast-Ereignis | PPB-Aufruf | PPB-Ereignis | Support danach |
| ---: | --- | ---: | --- | ---: |
| P1 | neuer Fast-Slot | 0 | keines | kein Slow-Slot |
| P2 | Fast-Treffer, erste Konsolidierung | 1 | `CREATED` | 1 |
| P3 | Fast-Treffer, zweite Konsolidierung | 2 | `MATCHED` | 2 |
| P4 | Fast-Treffer, dritte Konsolidierung | 3 | `MATCHED` | 3, stabil |

Bei `MATCHED` ist fuer jede der 48 Positionen exakt die vorhandene
Binary64-Auswertungsreihenfolge aus PPB-1 zu verwenden:

```python
updated = (1.0 - 0.05) * previous + 0.05 * current
```

Es gibt keine vorgelagerte algebraische Vereinfachung zu `current`, keinen
Float32-Rueckcast, keine Dezimalrundung und keine ULP-Toleranz. Daraus folgt
die prospektiv gebundene Kette:

| Slow-Zustand | 48-Werte-Digest | Digest Positionen 24..47 | gegen P geaenderte Positionen | maximale absolute Abweichung |
| --- | --- | --- | ---: | ---: |
| nach `CREATED`, Support 1 | `dc28fbb4ee22315131333a2c871ee82d958600d832a05c7d972db1e3acb4a023` | `1622004a498c487579e941a9b99193eded1a966420f916140251e21933ee1ba9` | 0 | `0.0` |
| nach Update 1, Support 2 | `74586d098394ad463b427f37a674073c5451edb085ba07c222f9384e60d42968` | `1b04e6b862463cc9a7d27725a5d3783bf3e58bd40f0f7bf24297f39fee2c2b11` | 10 | `5.551115123125783e-17` |
| nach Update 2, Support 3 | `24c77fb0e9c027798884e33f28b8b14f0d4fde9723142a6937ab3546b203bd3e` | `8408f2f4452b64cd8bf53847b91de8d8a34d29f64191c344cf8684726974191e` | 10 | `1.1102230246251565e-16` |

Der finale mittlere L1-Abstand des 48-Werte-Prototyps zum unveraenderten
P-Eingang betraegt `2.3130362374575168e-18`. Der auf den 24 beobachteten
Baendern gemessene Abstand zum Cue L betraegt
`7.036867813342526e-11` und bleibt damit ohne Grenzfall innerhalb der
unveraenderten Slow-Schwelle `0.02`.

## Zwei getrennte Pruefaussagen

### 1. Integritaet der konkreten Fortschreibung

Integritaet ist exakt und digestgebunden. Fuer LC02 muss gelten:

```text
support_count = 3
finaler 48-Werte-Prototypdigest = 24c77f...bd3e
Hypothesendigest der Positionen 24..47 = 8408f2...191e
```

Der bisher erwartete Digest `162200...ba9` bleibt als Digest des
unveraenderten P-Ausgangsvektors dokumentiert. Er ist kein gueltiger
Integritaetsdigest des zweimal fortgeschriebenen finalen Prototyps.

Jede Abweichung vom vollstaendig abgeleiteten finalen Digest ist ein
Integritaetsfehler, auch wenn der resultierende Vektor noch innerhalb einer
Matchschwelle laege.

### 2. Funktionale Inhaltsgleichheit

Funktionale Anwendbarkeit wird ausschliesslich durch die bereits vorhandene
S2-KZ-Regel bestimmt:

```text
mean_L1(beobachtete 24 Baender) <= 0.02
```

Ein unterschiedlicher Float- oder Digestwert ist deshalb nicht automatisch
ein funktionaler Inhaltsunterschied. Umgekehrt ersetzt ein bestandener
L1-Treffer niemals die exakte Integritaetspruefung des gespeicherten
Prototyps. Beide Aussagen muessen separat aufgezeichnet werden:

```text
prototype_transition_integrity
functional_observed_band_match
```

Es wird keine neue Gleichheitsregel eingefuehrt. Insbesondere gibt es keine
Rundung, keine Digestgleichheit als Matchregel und keine veraenderte
Wahrnehmungsschwelle.

## Prospektive Evaluatorbindung

Eine kuenftige S2-LD-Auswertung muss LC02 wie folgt binden:

```text
Entscheidung:       ADMIT_SINGLE_CONTEXT
A_RECENT:           A_RECENT_NOT_APPLICABLE
B_STABLE_AUDITORY:  B_STABLE_AUDITORY_APPLICABLE
Hypothesenbereich:  B_STABLE_AUDITORY
Support:            3
Integritaetsdigest: 8408f2f4452b64cd8bf53847b91de8d8a34d29f64191c344cf8684726974191e
Funktionsregel:     beobachteter mean L1 <= 0.02
```

Die fuenf anderen Fallbindungen bleiben unveraendert. Signalgeber und
Direktbaseline muessen weiterhin dieselben fachlichen Befunde liefern, aber
ihre rollenabhaengigen Gesamtdigests werden nicht gleichgesetzt.

## Kleine Qualifikation

Vor einem neuen Hauptlauf ist nur eine fokussierte neutrale Qualifikation
zulaessig. Sie darf keine der vier S2-LD-Hauptgeschichten bilden und muss
mindestens pruefen:

1. exakte Ableitung der drei Slow-Zustaende aus einem gebundenen
   48-Werte-Tupel mit der originalen Operationsreihenfolge;
2. die drei vollstaendigen und drei maskierten Digests der Tabelle;
3. `CREATED -> MATCHED -> MATCHED` sowie Support `1 -> 2 -> 3`;
4. Ablehnung veraenderter Update-Rate, Operationsreihenfolge,
   Eingangsreihenfolge oder Supportfolge;
5. getrennte Bewertung eines exakten Integritaetsfehlers und eines
   funktionalen L1-Nichttreffers;
6. synthetische LC02-Auswertung mit `8408f2...191e` als einzigem gueltigen
   finalen Hypothesendigest.

Die Qualifikation darf eine reine Rechenfixture verwenden. Sie darf keine
Memory-, Rezeptor-, Kontext- oder Feldfunktion aufrufen und erzeugt keinen
neuen Memorybefund.

## Spaetere Bestaetigungsgrenze

Erst nach bestandener Qualifikation darf hoechstens ein unabhaengiger
Sechs-Faelle-Lauf unter neuer Lauf-ID gesondert freigegeben werden. Dieser
verwendet unveraendert `30/6`, neue frische Memoryzustaende, genau einen
Hauptaufruf und genau eine read-only Verifikation. S2-LE bleibt unabhaengig
vom Ausgang dieses spaeteren Laufs historisch falsifiziert.

Ein vollstaendiger Bestaetigungslauf waere fachlich falsifiziert, wenn eine
der sechs Zustandsentscheidungen, die Read-only-Grenze, die Baselinegleichheit
oder die prospektiv abgeleitete finale LC02-Prototypbindung abweicht. Ein
Quellen-, Digest-, Zeit-, Zaehler- oder Abschlussfehler waere dagegen
`NOT_EVALUABLE`.

## Abschluss

S2-LF bindet die kleinste belegte Korrektur: Erwartet wird nicht mehr der
unveraenderte P-Ausgangsvektor, sondern der exakt aus zwei PPB-1-Updates
fortgeschriebene stabile Prototyp. Digestintegritaet und funktionale
Inhaltsanwendbarkeit bleiben strikt getrennte Aussagen. Es entsteht weder
eine neue Memoryebene noch eine neue Wahrnehmungs- oder Gleichheitsschwelle.
