# S1-EC71: Statischer Quellintegritaetspreflight

## Ausgangspunkt

EC70 hat gezeigt, dass die stabilen Audit-Digests von EC64, EC65 und EC67
ihre aktuellen Python-Quellen nicht kryptografisch binden. Ein unveraenderter
Audit-Digest konnte deshalb eine Implementierungsaenderung am EC64-Konverter
nicht sichtbar machen.

## Umsetzung

EC71 registriert die normalisierten SHA-256-Digests der realpfadnahen
Quellen:

- EC64 Output-Konverter nach EC75:
  `6e72f30489be527a6da1cb06fa8d45c16bff518e6bedddc55a45c8101a70225d`
- EC65 Aufrufadapter:
  `4fc2159d573570f11df27e0437f4dead219abfa6ccae6f71f9bb1dc313c69220`
- EC67 Realmodus-Koordinator:
  `b56a922153959b97ed69b4936074f2bed6b0cdc2a787aaf80a07f88e4d25c230`
- EC75 Handoff-Digest-Schemata:
  `92265285bf4482faafa6cef3f1c64e3fad97e3ea686ad188debeb9dc6733a105`

Der Preflight liest ausschliesslich diese vier Dateien, normalisiert
Zeilenenden und vergleicht ihre Digests mit den vorregistrierten Werten.
Abweichende Quellen werden einzeln in `failed_sources` genannt. Eine fehlende
Quelldatei fuehrt fail-closed zu einer Exception, bevor ein Preflight-Ergebnis
ausgestellt werden kann.

## Synthetische Abnahme

- aktueller Quellsatz: alle drei Digests exakt;
- gezielte Mutation des EC64-Konverters: EC64 wird einzeln als abweichend
  benannt und die Entscheidung wechselt auf
  `KORREKTUR_SOURCE_INTEGRITY_MISMATCH`;
- fehlender Quellsatz: fail-closed;
- keine Wrapper-, Adapter-, Koordinator- oder Feldkernausfuehrung;
- keine Schreib- oder Persistenzoperation im Preflight.

Vier fokussierte EC71-Tests bestehen. Der kanonische Preflight-Digest lautet:

`15966ff850b5028cab9960c6fdd11914896c85e8edfa2da8c8e29092a33aa852`

Entscheidung:

`SOURCE_INTEGRITY_EXACT_REAL_EXECUTION_STILL_BLOCKED`

## Aussagegrenze

EC71 belegt nur, dass die drei aktuell registrierten Quellen byteinhaltlich
dem geprueften Stand entsprechen. Der Preflight belegt weder Fehlerfreiheit
noch die Ursache des EC69-Teilabbruchs. Er liefert keinen Memory-, Feldzeit-,
Organisations- oder KI-Nachweis.

**STOPP fuer reale Ausfuehrung bleibt bestehen.** EC71 akzeptiert keine
Einmallauffreigabe und erneuert die verbrauchte EC69-Freigabe nicht.

Am besten geht es mit S1-EC72 weiter: EC71 als verpflichtendes Gate in einen
neuen korrigierten Gesamtpreflight aufnehmen. Dieser muss weiterhin jede
Ausfuehrung sperren und eine neue ausdrueckliche Einmallauffreigabe getrennt
fordern.
