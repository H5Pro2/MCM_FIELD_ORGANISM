# S2-HC: Einmaliger Kontextfunktionslauf

## Laufbindung

```text
Lauf-ID: s2hc-context-function-20260830-01
Owner: s2hc-run-owner
run_main_once-Aufrufe: 1
read-only Verifikatoraufrufe: 1
EvaluationPlanSeal:
1838da68fa3184a8be277b59b81bfa87332cc94f2be8f9282e91a9885ec0fb5c
```

Das Gate wurde nur im ausfuehrenden Prozess vor dem einzigen Aufruf geoeffnet
und im `finally`-Abschluss wieder auf `False` gesetzt. Die versionierte Quelle
blieb bei `MAIN_EXECUTION_ENABLED = False`.

Es gab keinen Retry, keine Teilfortsetzung, keine Parameteranpassung und keine
Codeaenderung.

## Terminaler Befund

```text
NOT_EVALUABLE
```

Der Lauf publizierte `op-0002`, die erste kompakte
`FORMATION_RECEPTOR_ANALYSIS`, erfolgreich. Das zugehoerige Receipt besitzt
2.748 Bytes und liegt damit innerhalb der durch S2-HA und S2-HB qualifizierten
Grenze.

Der unmittelbar folgende Schritt `op-0003` stoppte beim Versuch, das
tatsaechliche `COMPOSITE_FORMATION`-Ergebnis in die unveraenderte
4.096-Byte-`FormationReceipt`-Grenze zu schreiben:

```text
E008: registered resource limit was exceeded
```

Fuer `op-0003` wurde kein Erfolgsartefakt publiziert. Der registrierte
Fehlerpfad `fp-0003` schloss den Lauf mit:

```text
error_code: E008
failed_operation: op-0003
failed_operation_class: COMPOSITE_FORMATION
failed_phase: ACTIVE
terminal_status: NOT_EVALUABLE
```

Damit bestaetigt der reale Fehlabschluss zugleich die in S2-HA qualifizierte
unveraenderte Weitergabe des registrierten und phasenzulaessigen Codes
`E008`. Der Fehler wurde nicht mehr zu `E009` umklassifiziert.

## Aufzeichnungsumfang

Gespeichert wurden genau zwoelf verkettete Ereignisse:

- `op-0001` START/RESULT;
- `op-0002` START/RESULT;
- `op-0003` START/FAILED-RESULT;
- je START/RESULT fuer `err-0001` bis `err-0003`.

Die vier 13-Schritt-Geschichten, sieben GJ-Faelle, 139 Operationen und 278
Ereignisse wurden nicht erreicht. Es entstanden kein
`ExecutionEvidencePackage`, keine `EvaluationRunBinding`, keine reine
Funktionsauswertung und kein `COMPLETE`-Marker.

## Einmalige read-only Verifikation

Die genau einmal ausgefuehrte unabhaengige Verifikation ergab:

```text
status: NOT_EVALUABLE
operation_count: 0
event_count: 12
byte_count: 13.488
errors:
- artifact binding differs: op-0003
```

Der Fehler bezeichnet das aufgrund von `E008` nicht publizierte
`op-0003`-Erfolgsartefakt. Er aendert den terminalen Status nicht und erzeugt
keinen Funktionsbefund.

## Quellidentitaet

Alle zehn gebundenen Ausfuehrungsquellen waren vor und nach dem Lauf
byteidentisch:

| Rolle | SHA-256 |
| --- | --- |
| Fixture-Registry | `5d4ed450c2443f51839acfb9717661b8c54422be3fd87605c50b020e5a887849` |
| Runner | `321699d3864e4ff7e8872118fae6cae0aea701bc84de4554f496222110cca730` |
| Recorder | `371f371c3db7f441b675abb797143108737cc329bb238e9bbde3e5d4946ad2b1` |
| Verifikator | `4a62e1d97c9d0448614463981a86dc587ed64bc758cf19306688f4661b120154` |
| Koordinator | `95ee05ccc0eeb14abbcda036971da5c33ac79363dd546789f4878aace5677db0` |
| Kontextbundle | `0fba7b0323fe772c481eb5261b9640e4a5b00d7da3ceb1a7e0f81c6d9f54bf49` |
| A/B-Projektion | `21bc206dc37f8a9f477c02eac7d14ff22e6924bbdb54eb5153122ec296cdd587` |
| Kontextverbraucher | `29c16372184bec0092fadf777adc7b7e1c9a5ba0529711c46ca75c92c4769832` |
| direkte Baseline | `43ac94ca59a1157893cdc96cd4b980a0fb348130bc670596bbd3d65e112d7958` |
| Auswerter | `ac33ed97b670681250cb709b40332024ab107365836cd5641d27e34ee85e5cf5` |

## Belegdigests

| Beleg | SHA-256 |
| --- | --- |
| Manifest | `61bf21a4a25ae53a201fbfb6108a4f248b786fbb2b605367bdf7cf4cefe7baeb` |
| Journal | `c013f151a2b23c74e8b815bf0fe76f4347c8f18093aef29a4418335de44f5561` |
| kompaktes `op-0002`-Receipt | `dd4eeb90d2231c84c801fee8dc530e724f82b68d2761eb45e07e7d9241c269f1` |
| RunFailureReceipt | `2a3bb3851b0d5eedb7b16af3b378ddfb36c0fff5b1fb29556ca5fa3dd442080c` |
| Fehlerterminal | `a5b3187103cc2c041b383e1b88a7cfbc797040aeb26459ec537f56bdf08ccf92` |
| `NOT_EVALUABLE`-Marker | `f03b434b6381d67be1a4992c397285f6a66d65e9d269624880b973fa94a29d90` |
| Laufsteuerungs- und Verifikationsbeleg | `8fa12303e024405ff2631f3b445033c08cb33d0cc62ab79195667aa423697ead` |

## Fachliche Grenze

S2-HC liefert weder einen positiven noch einen negativen Befund zur
Kontextverwendung. Der erwartete Status
`S2GJ_FUNCTION_VALID_DIRECT_MASK_FILL_EXPLAINS` wurde nicht geprueft und darf
nicht aus Zwischenwerten abgeleitet werden.

S2-GW bleibt unveraendert `NOT_EVALUABLE`. S2-HC wird nicht wiederholt,
fortgesetzt oder nachtraeglich repariert.

## Naechster konkreter Schritt

Vor einem neuen Funktionslauf muss ausschliesslich die Aufzeichnungsanatomie
des tatsaechlichen `COMPOSITE_FORMATION`-Ergebnisses geklaert werden:

- Nutzresultat und erneut serialisierte Zustandsobjekte getrennt zaehlen;
- kleinste herkunftserhaltende kompakte FormationReceipt-Projektion pruefen;
- den vollstaendigen In-Memory-Nachzustand weiterhin unveraendert fuer den
  naechsten Schritt verwenden;
- die bestehende 4.096-Byte-Grenze und Gesamtbudgets nicht vorsorglich
  erhoehen.

Das ist ein enger Instrumentierungsblocker, keine neue Memory- oder
Infrastrukturarchitektur. Eine Korrektur oder ein weiterer Lauf benoetigt eine
neue ausdrueckliche Freigabe.
