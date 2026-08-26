# S1-EC70: Benannte Bildungskonverter-Diagnosegates

## Ausgangspunkt

Der einmalige EC69-Lauf brach nach 402 realen Bildungsschritten an einer
Sammelpruefung des EC64-Bildungskonverters ab. Die Sammelfehlermeldung liess
nach Nichtpersistenz des Outputs keine eindeutige Zuordnung der Abweichung
mehr zu.

## Korrektur

Die bisherige Sammelpruefung ist in fuenf geordnete, benannte Gates zerlegt:

1. `formation-arm-identity-exact`
2. `formation-refinement-identity-exact`
3. `formation-handoff-digest-exact`
4. `formation-source-support-count-exact`
5. `formation-plan-step-count-exactly-402`

Der Konverter erzeugt vor jeder Receipt-Bildung ein typisiertes
Diagnoseobjekt mit:

- allen fuenf booleschen Gates;
- `all_passed`;
- der geordneten Liste `failed_gates`;
- einem Diagnose-Digest.

Bei einer Abweichung nennt die Exception jetzt die exakten fehlgeschlagenen
Gate-Namen. Es werden keine Zustandsvektoren, Messwerte oder Outputs
persistiert.

## Synthetische Abnahme

Vier outputabhaengige Gates wurden jeweils mit einem weiterhin intern
gueltigen, neu digestierten EC54-Ausgabetyp einzeln falsifiziert. Das
Planlaengengate wurde direkt auf Ebene des typisierten Diagnosevertrags
fail-closed geprueft, weil die Planlaenge nicht Bestandteil des Outputs,
sondern des bereits validierten aufgeloesten Plans ist.

Ein gueltiger synthetischer Bildungsoutput besteht alle Gates.

Referenz-Diagnose-Digest:

`1958d0aaa46a6a47d9884c8da617203e999f2ce75214b7e100a4889511882d76`

- 25 fokussierte Tests einschliesslich nachgelagerter statischer Pfade
  bestanden
- keine Wrapper-, Adapter-, Koordinator- oder Feldkernausfuehrung
- kein Retry des EC69-Laufs
- keine Persistenz und keine Claims

## Integritaetsbefund

Die bestehenden EC64-, EC65- und EC67-Audit-Digests bleiben trotz der
Quellcodeaenderung unveraendert. Das zeigt, dass diese Audits ihre
Implementierungsquellen bisher nicht kryptografisch binden. Vor einem
spaeteren Realversuch reicht deshalb ein erneuter Ressourcenpreflight allein
nicht aus.

**STOPP fuer reale Ausfuehrung bleibt bestehen.** Die Diagnose ist
korrigiert, aber die verbrauchte EC69-Freigabe wird dadurch nicht erneuert.

Am besten geht es mit S1-EC71 weiter: Quelltextdigests fuer EC64-Konverter,
EC65-Aufrufadapter und EC67-Realmodus-Koordinator vorregistrieren und in
einen neuen statischen Integritaetspreflight binden. Keine reale Ausfuehrung.
