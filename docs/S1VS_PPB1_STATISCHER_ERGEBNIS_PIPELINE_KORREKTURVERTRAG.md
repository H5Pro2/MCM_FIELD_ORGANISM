# S1-VS: Statischer PPB-1-Ergebnis-Pipeline-Korrekturvertrag

> Abschlussstatus: S1-VT implementiert und prueft die nachstehend gebundene
> private Ergebnispipeline mit konstruierten Receipts. Die registrierte
> Matrix bleibt gesperrt. Siehe
> [S1-VT](S1VT_PPB1_PRIVATE_ERGEBNISHUELLE_COMPOSITOR_UND_V2_AUSWERTER_ABNAHME.md).

## Auftrag und Grenze

S1-VS bindet die in S1-VR erkannten Korrekturen vor jeder weiteren
Implementierung. Der Vertrag legt ausschliesslich fest:

- die atomare Versiegelung eines vollstaendigen korrigierten
  528-Fall-Ergebnisses;
- die einzige zulaessige Verdichtung der Fallreceipts in 48 technische
  Armrecords;
- die Herkunft jeder entscheidungsrelevanten Metrik;
- die vollstaendige Aufruf- und Identitaetsmetadatenbilanz;
- die korrigierte Baseline- und Einfachheitsentscheidung;
- eindeutige Fail-Closed- und Stoppregeln.

Nicht zulaessig sind Implementierung, Tests, Matrixausfuehrung,
Parameterwahl, Feld- oder Medienintegration, oeffentliche API,
Snapshotumbau oder eine Aussage ueber eine besondere Feldfunktion. PPB-1
bleibt eine private Engineeringkomponente fuer verdichtete technische
Wahrnehmungszustaende.

## Unveraenderte Eingangsgrundlage

S1-VS veraendert weder den S1-VN-Elternplan noch den korrigierten S1-VQ-
Plan. Verbindlich bleiben:

```text
Elternplan:       384 Pfade
Elternplandigest: 35c1e589f749f1c1f1f24900f611fd43f8329d803a4b82ca94584d1925067ba3

Korrekturplan:       528 Pfade
Korrekturplandigest: f307363400ba66e53a49ec9cd21bc17973f93f240f3946eade2c6a7dbdcd1210

PPB-Aufrufe:         9.476
Baselineaufrufe:    66.332
Gesamtaufrufe:      75.808
```

Die vorhandenen privaten Runnerkoerper bleiben unveraendert und gesperrt.

## Atomare Ergebnishuelle

Ein spaeteres korrigiertes Matrixresultat ist nur als ein vollstaendig
validiertes Objekt zulaessig. Seine kanonische Payload muss mindestens
enthalten:

- feste Schemafassung;
- Eltern- und Korrekturplandigest;
- genau 528 Fallreceipts in Korrekturplanreihenfolge;
- genau 144 R0/R1-Vergleichsrecords;
- PPB-, Baseline- und Gesamtaufrufzahl;
- Digest der geordneten Fallreceiptliste;
- Digest der geordneten Wiederholungsvergleichsliste;
- einen kanonischen Gesamtdigest.

Vor der Erzeugung des Gesamtdigests muessen folgende Identitaeten gelten:

1. Jede registrierte Pfad-ID kommt genau einmal vor.
2. Pfadrolle, Parent-ID, Familie, Parameter, Modalitaet, Fixture,
   Wiederholungsrolle, Config-Digest und Aufrufzahl stimmen mit dem Plan
   ueberein.
3. `base_receipt.path_id` entspricht der korrigierten Pfad-ID.
4. Ereignisse, Schrittbeobachtungen und Identitaetsbeobachtungen besitzen
   jeweils exakt die registrierte Schrittlange.
5. Schrittindizes der beiden Beobachtungsfolgen sind paarweise gleich und
   streng aufsteigend.
6. Die Summe aller akzeptierten Aufrufe ist exakt 75.808.
7. Jeder R1-Pfad besitzt genau den unmittelbar vorangehenden R0-Parent und
   einen bitgleichen normalisierten Wiederholungsdigest.
8. Gleiche Fixture-, Parameter- und Modalitaetsrollen besitzen ueber alle
   acht Familien denselben Eingangsfolgendigest.

Eine unvollstaendige Ergebnishuelle darf weder verdichtet noch ausgewertet
oder teilweise publiziert werden. Fehlerresultat und gueltiges
Gesamtresultat sind gegenseitig ausschliesslich.

Jeder der 144 Vergleichsrecords muss Familie, Parameter, Modalitaet,
Fixture, R0-Pfad-ID, R1-Pfad-ID, beide normalisierten Digests und das
Bitgleichheitsergebnis tragen. Die bisherige Kurzform aus nur R1-Pfad-ID und
einem Digest reicht fuer die atomare Abstammungsvalidierung nicht aus.

## Armkreuzprodukt und Receiptinventar

Der reine Compositor erzeugt exakt:

```text
8 Familien * 3 Parameterrecords * 2 Modalitaeten = 48 Armrecords
```

Jeder Arm wird ausschliesslich aus genau elf Receipts derselben Familie,
desselben Parameterrecords und derselben Modalitaet gebildet:

```text
R0: F01, F02, F03, F04, F05, F06, F07, F08
R1:                  F04, F05, F06
```

Es gibt keine falluebergreifende Zustandsuebernahme. R1 dient nur der
gebundenen Bitgleichheitskontrolle und darf keine zusaetzliche
Funktionsprobe bilden.

## Exakte Aufrufbilanz pro Arm

Der Armrecord muss Primaer-, Kontroll- und Gesamtaufrufe getrennt tragen:

| Parameter | Modalitaet | R0 | R1 | gesamt |
|---|---|---:|---:|---:|
| P0 | auditiv | 1.074 | 24 | 1.098 |
| P0 | visuell | 302 | 20 | 322 |
| P1 | auditiv | 2.106 | 32 | 2.138 |
| P1 | visuell | 562 | 24 | 586 |
| P2 | auditiv | 4.170 | 48 | 4.218 |
| P2 | visuell | 1.082 | 32 | 1.114 |

Diese sechs Budgets gelten fuer jede der acht Familien. Der bisherige
S1-VO-Wert `accepted_call_count` bildet nur R0 ab und muss in einer spaeteren
korrigierten Summaryfassung durch die drei expliziten Rollen ersetzt werden.

Der vorhandene S1-VO-v1-Auswerter darf deshalb kein korrigiertes
S1-VQ-Matrixresultat konsumieren. Er bleibt als gepruefter historischer
Elternstand unveraendert erhalten, bis eine private v2-Ergebnisrolle den
vollstaendigen R0/R1-Anschluss implementiert.

## Technische Zuordnungsidentitaet

Fuer die Verdichtung wird pro Schritt genau eine technische
`assignment_identity` abgeleitet:

1. Bei `MATCHED` ist sie die ausgewaehlte Identitaet.
2. Bei einer neuen Bildung, Speicherung, Aktualisierung oder Ersetzung ohne
   Match ist sie die Schreibidentitaet.
3. Ohne Auswahl und ohne Schreibvorgang ist sie `None`.

Bei einem Match hat die Auswahlidentitaet Vorrang vor einer gleichzeitig
fortgeschriebenen Schreibidentitaet. Dadurch wird insbesondere bei B01 die
zugeordnete Vorzustandsidentitaet nicht mit dem neu geschriebenen Ringinhalt
verwechselt.

Fuer PPB-1 wird die bereits vorhandene Slot-ID als Auswahl- beziehungsweise
Schreibidentitaet verwendet. Fuer B01 bis B06 gelten die in S1-VP und S1-VQ
gebundenen Identitaetsrollen. B07 bleibt identitaetsfrei.

## Feste Diagnosepositionen

Die sechs Diagnoseproben sind ausschliesslich folgende terminalen
Schrittpositionen der R0-Receipts:

| Maskenposition | Fixture | Schrittrolle |
|---:|---|---|
| D0 | F02 | letzte `v_low`-Probe |
| D1 | F03 | vorletzte `v_low`-Probe |
| D2 | F03 | letzte `v_high`-Probe |
| D3 | F04 | letzte `v_mid`-Probe |
| D4 | F05 | vorletzte `v_low`-Randprobe |
| D5 | F05 | letzte `v_high`-Randprobe |

Der Armrecord traegt eine geordnete Sechs-Bit-Matchmaske. Ein Bit ist genau
dann gesetzt, wenn das zugehoerige Ereignis `MATCHED` lautet und eine
Auswahlidentitaet vorhanden ist. `diagnostic_match_count` wird nur als Summe
dieser Maske abgeleitet und darf die Maske nicht ersetzen.

Null gesetzte Bits bleiben der gebundene Nie-Match-Stopp. Sechs gesetzte
Bits bleiben der gebundene Immer-Match-Stopp.

## Zuordnungs- und Lebenszyklusrollen

Aus den R0-Receipts werden vier feste Lebenszyklusrollen gebildet:

- `F01_EXACT_REPEAT`: Die erste Zuordnungsidentitaet existiert; die letzte
  Probe ist ein Match auf genau diese Identitaet.
- `F06_CAPACITY_BOUNDED`: Beobachtete Belegung und aktives
  Identitaetsinventar ueberschreiten die gebundene Kapazitaet nie; alle
  registrierten F06-Schritte sind akzeptiert.
- `F07_RELEASE_RESPONSE`: Die letzte Probe besitzt keine ausgewaehlte
  Vorzustandsidentitaet.
- `F08_RETENTION_RESPONSE`: Die letzte Probe ist ein Match auf die erste
  Zuordnungsidentitaet.

`lifecycle_valid` ist nur dann wahr, wenn alle vier Rollen wahr sind.

Die Nahzuordnung aus F02 ist nur konsistent, wenn alle sechs
Zuordnungsidentitaeten vorhanden und identisch sind.

Die getrennte Ankerzuordnung aus F03 ist nur gueltig, wenn:

- die ersten `v_low`- und `v_high`-Zuordnungen vorhanden und verschieden
  sind;
- die terminale `v_low`-Probe wieder dem ersten Low-Anker zugeordnet ist;
- die terminale `v_high`-Probe wieder dem ersten High-Anker zugeordnet ist.

## Wiederholungsrolle

Der Armrecord traegt eine geordnete Drei-Bit-Wiederholungsmaske fuer F04,
F05 und F06. Jedes Bit muss aus dem bereits normalisierten R0/R1-
Vergleichsdigest entstehen. `repeatability_confirmed` ist nur wahr, wenn
alle drei Bits wahr sind.

Ein R1-Receipt darf keine Lebenszyklus-, Diagnose- oder Zuordnungsmetrik
doppelt erhoehen. Es traegt ausschliesslich Wiederholungsnachweis und
Kontrollaufrufe bei.

## Kanonischer Armrecord

Jeder der 48 geordneten Armrecords muss mindestens folgende Rollen tragen:

- Schemafassung, Familie, Parameter und Modalitaet;
- Korrekturplandigest und Digest der elf Quellreceipts;
- Vier-Bit-Lebenszyklusmaske und abgeleitetes `lifecycle_valid`;
- Sechs-Bit-Diagnose-Matchmaske und abgeleitete Matchanzahl;
- F02-Nahzuordnungs- und F03-Ankertrennungsrolle;
- Drei-Bit-Wiederholungsmaske und abgeleitete Wiederholungsbestaetigung;
- maximales logisches Werte- und Identitaetsmetadatenbudget;
- R0-, R1- und Gesamtaufrufzahl;
- Digest des zugehoerigen Evidenzledgers;
- kanonischen Armrecorddigest.

Die 48 Records werden in der bereits gebundenen Reihenfolge Familie,
Parameter, Modalitaet sortiert. Der Compositor darf weder Ergebnisse
auswaehlen noch Baselines vergleichen.

## Zustands- und Identitaetsbudget

Jeder Armrecord traegt getrennt:

- `peak_logical_value_count`: Maximum aller logischen Vektorwerte ueber die
  elf Armreceipts;
- `peak_identity_metadata_value_count`: Maximum der gleichzeitig aktiven
  technischen Identitaetsrecords ueber dieselben Receipts;
- R0-, R1- und Gesamtaufrufe.

Fuer PPB-1 entspricht die aktive Identitaetszahl der belegten Slotzahl. Fuer
B01 bis B06 wird `active_identity_count` aus dem atomaren Identitaetsreadout
verwendet. Fuer B07 ist der Wert null.

Der Identitaetsdigest ist ein Integritaetsbeleg und keine zusaetzliche
Mengeneinheit. Vektorinhalte der B02-Fensterhistorie bleiben dagegen wie
bisher vollstaendig im logischen Wertebudget enthalten.

## Evidenzledger ohne nachtraegliche Schwelle

Der Compositor muss neben den Entscheidungsrollen ein kanonisches
Evidenzledger erhalten. Dieses bindet mindestens:

- die elf geordneten Falldigests;
- Ereignisfolgen und Zuordnungsidentitaeten der festen Probepositionen;
- die sechs diagnostischen Distanzen, einschliesslich `None`;
- F05-Zustandsverschiebungen, soweit die Familie diese Rolle technisch
  bereitstellt;
- maximale Belegung, Stabilisierung, logische Werte und Identitaetszahl je
  Fixture;
- die drei R0/R1-Vergleichsdigests.

Fuer Distanz oder Verschiebung ist in S1-VS keine neue Toleranz gebunden.
Diese Werte bleiben deshalb reproduzierbare technische Messwerte, duerfen
aber weder nach dem Lauf geschwellt noch allein fuer Auswahl oder
Baseline-Reduktion verwendet werden.

## Korrigierte Zulassungsregel

Ein Arm ist nur zulaessig, wenn:

1. Ergebnishuelle, Armreceiptinventar und Aufrufbilanz gueltig sind;
2. alle vier Lebenszyklusrollen bestehen;
3. die Diagnosemaske weder Immer-Match noch Nie-Match ergibt;
4. F02 dieselbe Nahzuordnung behaelt;
5. F03 beide Anker getrennt und terminal wieder zuordnet;
6. alle drei R0/R1-Kontrollen bitgleich sind;
7. alle Zustands- und Identitaetsbudgets endlich und innerhalb des Vertrags
   bleiben.

Diese Reihenfolge wird vor jedem Familienvergleich angewendet.

## Korrigierte Baseline-Reduktion

B01 bis B06 duerfen einen zulaessigen PPB-Arm nur dann erklaeren, wenn die
Baseline fuer denselben Parameterrecord und dieselbe Modalitaet:

- selbst zulaessig ist;
- dieselbe geordnete Diagnose-Matchmaske besitzt;
- dieselben vier Lebenszykluswahrheitswerte besitzt;
- dieselbe bestandene Nah- und Ankertrennungsrolle besitzt;
- dieselbe bestandene Drei-Bit-Wiederholungsmaske besitzt;
- kein groesseres logisches Wertebudget besitzt;
- kein groesseres Identitaetsmetadatenbudget besitzt;
- keine groessere Gesamtaufrufzahl besitzt.

Die bisherige Regel, nach der bereits irgendeine zulaessige Baseline mit
kleinerem Werte- und Aufrufbudget reduziert, ist fuer die korrigierte
Pipeline nicht ausreichend. Unterschiedliche Diagnosemasken duerfen nicht
als gleiche technische Wirkung behandelt werden.

B07 kann weiterhin keinen zustandsbehafteten Arm reduzieren.

## Auswahl unter nicht reduzierten PPB-Records

Unter mehreren zulaessigen und nicht reduzierten PPB-Records gilt pro
Modalitaet genau diese lexikographische Ordnung:

1. geringeres `peak_logical_value_count`;
2. geringeres `peak_identity_metadata_value_count`;
3. geringere Gesamtaufrufzahl;
4. feste Parameterreihenfolge P0, P1, P2.

Zulaessige Ausgaben bleiben `P0`, `P1`, `P2` oder
`NO_ADMISSIBLE_CONFIGURATION`. Audio und Video werden weiterhin getrennt
entschieden.

## Fail-Closed- und Stoppregeln

Die Ergebnispipeline muss vor jeder Entscheidung stoppen bei:

- fehlendem, doppeltem, fremdem oder umsortiertem Pfadreceipt;
- Abweichung von Plan-, Config-, Eingangsfolgen- oder Fallrollen;
- nicht atomar ausgerichteten Schritt- und Identitaetsbeobachtungen;
- falscher R0/R1-Abstammung oder nicht bitgleicher Wiederholung;
- Abweichung von 528 Faellen oder 75.808 Gesamtaufrufen;
- fehlender Diagnoseposition oder mehrdeutiger Zuordnungsidentitaet;
- unvollstaendigem 48-Arm-Kreuzprodukt;
- fehlender R0-, R1-, Zustands- oder Identitaetsbilanz;
- einem Baselinevergleich ohne gleiche technische Ergebnisprofile;
- jeder nachtraeglichen Schwelle, Fixtureaenderung oder manuellen
  Uminterpretation.

Ein Teilresultat darf nicht als negatives oder positives PPB-Ergebnis
ausgegeben werden.

## Vertragsentscheidung

```text
S1_VS_ATOMIC_528_CASE_RESULT_ENVELOPE_BOUND
S1_VS_EXACT_48_ARM_COMPOSITOR_BOUND
S1_VS_ELEVEN_RECEIPTS_PER_ARM_BOUND
S1_VS_EXACT_DIAGNOSTIC_MATCH_MASK_BOUND
S1_VS_LIFECYCLE_ASSIGNMENT_AND_REPEAT_MASKS_BOUND
S1_VS_R0_R1_AND_TOTAL_CALL_BUDGETS_BOUND
S1_VS_IDENTITY_METADATA_BUDGET_BOUND
S1_VS_BASELINE_EQUIVALENCE_RULE_CORRECTED
S1_VS_FAIL_CLOSED_RESULT_PIPELINE_BOUND
S1_VS_NO_IMPLEMENTATION
S1_VS_NO_MATRIX_EXECUTION
S1_VS_ZERO_REGISTERED_CALLS_EXECUTED
```

S1-VS schliesst die drei S1-VR-Luecken auf Vertragsniveau. Es bestaetigt
weder die Implementierung der Ergebnispipeline noch die Eignung eines
Parameterrecords oder eine besondere technische Faehigkeit.

## Genau ein naechster Schritt

Der einzige Anschluss ist:

```text
S1-VT - private Implementierung und synthetische Vertragsabnahme der
        atomaren Ergebnishuelle, des 528-zu-48-Compositors und des
        korrigierten reinen Auswerters
```

S1-VT darf nur konstruierte synthetische Receipts verwenden. Der
registrierte 528-Pfad-Runner, das Vollmatrixgate, Feldkern, Medienpfade,
Snapshot und oeffentliche API bleiben unveraendert. Eine Matrixausfuehrung
ist auch nach einer erfolgreichen S1-VT-Abnahme nicht automatisch
freigegeben.

## Grundlagen

- [S1-VR abschliessender korrigierter Preflight](S1VR_PPB1_ABSCHLIESSENDER_STATISCHER_KORRIGIERTER_VOLLMATRIX_PREFLIGHT.md)
- [S1-VQ Identitaetsrollen und korrigierter Plan](S1VQ_PPB1_PRIVATE_IDENTITAETSROLLEN_UND_KORRIGIERTER_MATRIXPLANER.md)
- [S1-VO reiner Auswerter und erster Preflight](S1VO_PPB1_REINER_AUSWERTER_UND_STATISCHER_VOLLMATRIX_PREFLIGHT.md)
- [S1-VM Auswahl- und Matrixvertrag](S1VM_PPB1_STATISCHER_PARAMETERWAHL_BASELINE_UND_AUSFUEHRUNGSMATRIXVERTRAG.md)
