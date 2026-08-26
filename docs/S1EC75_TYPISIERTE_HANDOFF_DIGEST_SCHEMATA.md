# S1-EC75: Typisierte Handoff-Digest-Schemata

## Ausgangspunkt

EC74 bestimmte den fehlgeschlagenen Vergleich eindeutig als
Digest-Schemaabweichung. Der reale Bildungsrunner lieferte einen Digest nur
ueber Abschlusszuweisungen, waehrend der Plan einen umfassenderen
Envelope-Digest trug. Der bisherige EC70-Vergleich setzte beide Rollen
faelschlich gleich.

## Korrektur

`E1HandoffDigestPair` traegt jetzt zwei explizite Rollen:

- `assignment_digest`: Abschlusszeit und geordnete Frame-Identitaeten; exakt
  kompatibel mit dem bisherigen realen Runner-Audit;
- `envelope_digest`: Assignment-Inhalt plus Clock, Modalitaeten,
  Ereigniszaehler und Assigned-once-Status; exakt kompatibel mit dem
  bisherigen Plan-Digest.

Der Konverter prueft diese Rollen getrennt:

1. `formation-arm-identity-exact`
2. `formation-refinement-identity-exact`
3. `formation-runtime-assignment-digest-exact`
4. `formation-plan-envelope-digest-exact`
5. `formation-source-support-count-exact`
6. `formation-plan-step-count-exactly-402`

Kein Gate wurde entfernt. Der unzulaessige Kreuzvergleich wurde durch zwei
gleichartig serialisierte Vergleiche ersetzt.

## Synthetische Abnahme

- Der typisierte Paarvertrag reproduziert beide bisherigen privaten
  Digestfunktionen exakt.
- Die beiden Rollen sind fuer denselben Handoff erwartungsgemaess
  verschieden.
- Ein Runner-Audit mit falschem Assignment-Digest falsifiziert nur das
  Runtime-Assignment-Gate.
- Ein manipulierter Plan-Envelope-Digest falsifiziert nur das
  Plan-Envelope-Gate.
- Ein gueltiges synthetisches Output besteht alle sechs Gates.

Aktueller Referenz-Diagnose-Digest:

`502966897ff44402a72b113b3ab00b3180bf5deab7971fbfa29abd2706ee9afe`

## Neubindung

EC71 bindet jetzt vier statt drei Quellen, einschliesslich
`e1_handoff_digest_schemas.py`:

- aktueller EC71-Digest:
  `15966ff850b5028cab9960c6fdd11914896c85e8edfa2da8c8e29092a33aa852`
- erneuerter EC72-Referenzfixture-Digest:
  `d2a491e62f856cff30ccc8241dbb2b1b61e283818f1ddf297c012a22b418dc10`
- erneuerter geschlossener EC73-Referenzfixture-Digest:
  `727454d3d6519459c5333c9e304ee7426492839f44a8b08652c4a7d9aa24a4c6`

Die historische EC74-Autorisierung wird nicht erneuert. EC75 fuehrt keinen
Wrapper, Adapter, Koordinator oder Feldkern aus.

## Aussagegrenze

EC75 korrigiert eine technische Vertragsinkompatibilitaet. Die Korrektur
belegt nicht, dass ein vollstaendiger Lauf gelingt, und liefert keinen
Memory-, Feldzeit-, Organisations- oder KI-Nachweis.

**STOPP fuer reale Ausfuehrung bleibt bestehen.**

Am besten geht es mit S1-EC76 weiter: einen frischen nicht ausfuehrenden
EC72/EC73-Preflight gegen die EC75-Quellen bilden und die komplette
Koordinatorroute weiterhin nur synthetisch bis hinter den ersten
Bildungskonverter pruefen. Erst danach darf eine neue Einmallauffreigabe
angefragt werden.
