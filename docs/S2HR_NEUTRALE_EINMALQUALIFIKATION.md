# S2-HR: Neutrale Einmalqualifikation

Status: `PRIVATE_ROLE_ADDRESSED_CONSUMER_QUALIFICATION_VALID`

## Ausfuehrungsgrenze

Die Qualifikation wurde unter der ID
`s2hr-role-consumer-qualification-20260831-01` genau einmal ausgefuehrt.

Ausgefuehrt wurde ausschliesslich:

```text
python -m unittest -v tests.test_s2hr_role_addressed_consumer_qualification
```

Es gab keinen Retry und keine Korrektur waehrend oder nach dem Lauf. Es
wurden keine Bildungsgeschichte, kein B4-, TSPM-1- oder PPB-1-Uebergang, kein
Koordinator und kein Feldpfad aufgerufen.

## Ergebnis

```text
Ran 16 tests in 0.057s
OK
Exit-Code: 0
```

Alle 16 vorregistrierten Tests sind bestanden.

Geprueft wurden:

- Q0/Q1-Materialisierung und exakte Distanzen;
- zwei spiegelbildliche Richtungen und vier Rollenfaelle;
- getrennte Auswahl von `A_RECENT` und `B_STABLE`;
- funktionale Unabhaengigkeit vom nicht gewaehlten Kandidaten;
- unveraenderte sichtbare Werte;
- ausschliessliche Fuellung der neun maskierten Positionen;
- Gleichheit von Verbraucher und unabhaengiger Direktbaseline;
- Fail-Closed-Verhalten bei fehlenden, beschaedigten, fremden und
  widerspruechlich gebundenen Rollen;
- keine Teilfuellung bei sichtbarem Konflikt;
- identische Vor-/Nachzustandsdigests;
- Ausschluss der Evaluationsfixture aus beiden Funktionsmodulen.

## Quellidentitaet

Die SHA-256-Digests vor und nach dem Lauf sind bytegleich:

| Quelle | SHA-256 |
|---|---|
| Byte-Block-Fixture | `6b5adce16f7b3523f4a521636d4687b07b7728c2986ff070f1692524e23a3898` |
| Rollenverbraucher | `cb9b3ecea1bfd0090d379bdbd46c317565ea58d664d2b3f66a64f33008960e57` |
| Direktbaseline | `e42ed48b7c06baf5939654be0e470e8d39e8e98e837680c6128c92ac46c12254` |
| Qualifikationstest | `f5a209b2682e46b6177c84accf17f9d16c4233b2e04803b9eedee3f74a02fe69` |

Die gespeicherten Hashlisten vor und nach dem Lauf besitzen beide den Digest:

```text
c736657a5b818aefb9fb34491265ad2d5bfedfc71ac501e40443ac06e61ab466
```

Der vollstaendige Testoutput besitzt den Digest:

```text
afacb7445c8451fcd9754987a9bb38e6da3ebff249d033e6e465ec0036a7638d
```

## Einordnung

S2-HR qualifiziert die private Fixture-, Rollenverbraucher- und
Baselinegrenze. Der Befund bestaetigt, dass ein bereits bereitgestelltes
synthetisches A/B-Bundle strikt nach einer expliziten Rollenbindung verwendet
werden kann.

Er bestaetigt noch nicht, dass `A_RECENT` und `B_STABLE` in der korrigierten
Konfliktgeschichte tatsaechlich gemeinsam gebildet werden. Er ist kein neuer
Memory-Befund und keine automatische Kontextwahl.

Der naechste zulaessige Schritt ist die getrennte statische Vorbereitung
eines einmaligen realen Konfliktfunktionslaufs mit tatsaechlich erzeugtem
`A_RECENT` und `B_STABLE`. Runner, Bildungsgeschichten und Funktionslauf
bleiben bis zu einer ausdruecklichen Freigabe gesperrt.
