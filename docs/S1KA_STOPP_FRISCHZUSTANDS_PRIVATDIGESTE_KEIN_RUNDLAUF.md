# S1-KA: STOPP Frischzustands-Privatdigests ohne Rundlauf

## Ergebnis

S1-KA stoppt vor der Frischzustandsfactory und dem privaten Runner. Der
statische Vorabaudit der zwoelf in S1-JZ gebundenen Privatzustandsrecords
findet vier Digestabweichungen gegen die kanonische Runtimeform.

## Befund

Betroffen sind:

- B1 fuer `TWO_NODE_OPEN_LINE` und `THREE_NODE_OPEN_LINE`;
- B2 fuer `TWO_NODE_OPEN_LINE` und `THREE_NODE_OPEN_LINE`.

S1-JZ hat die verschachtelten B1-Fixed-Adapterdaten als Tupelfolgen und die
B2-L-Eintraege ohne die kanonische Objektform digestiert. Der reale private
Zustand serialisiert diese Teile dagegen als benannte Objekte. Deshalb kann
keiner der vier gespeicherten Digests den vollstaendigen Rundlauf aus
gebundenem Payload, Runtimezustand und kanonischem Payload bestehen.

Die acht B3-bis-B6-Records fuer beide Geometrien stimmen bitidentisch. Ihre
Payloads und Digests bleiben erhalten.

## Ausfuehrungsgrenze

Das einzige S1-JZ-Exemplar `B1:P_IE_CAUSAL_TWO_SUBSTEP:r2` gehoert zu den
fehlerhaften Records. Der Fehler wurde deshalb vor dem ersten
Materializeraufruf geschlossen. Ein begonnener Runnerentwurf wurde
vollstaendig verworfen.

Es wurden keine Frischzustandsfactory und kein Runner implementiert. Es gab
keinen Materializer-, Adapter- oder Intervallaufruf, keine technische Replik,
keinen Profilfall, keine Runtimeintegration und keine Forschungsprobe.

Entscheidung:

`STOPP_S1JZ_B1_B2_FRESH_PRIVATE_STATE_DIGESTS_DO_NOT_ROUNDTRIP`

Kanonischer Auditdigest:

`8e7a7ed21b6d5528ca152257e8ee550fdf8af12d42fd542893859a7735134a09`

## Erhaltener Stand

Alle S1-JZ-Bindungen ausser den vier abhaengigen Privatzustandsdigests und
dem davon abhaengigen Vertragsdigest bleiben erhalten. Insbesondere bleiben
Frischfeldpayloads, Checkpoints, Komponentenindizes, Outputschema,
Fehlergrenze und technisches Exemplar unveraendert. Ebenso bleiben alle
S1-JX-Carryregeln und die S1-JW-Adapterimplementierung erhalten.

## Naechster zulaessiger Schritt

S1-KB darf ausschliesslich die verschachtelten B1-Fixed-Adapter- und
B2-L-Payloads an die kanonische Runtimeobjektform angleichen, die vier
abhaengigen Privatzustandsdigests und den S1-JZ-Vertragsdigest neu berechnen
und alle zwoelf statischen Rundlaeufe pruefen. Die acht B3-bis-B6-Records
bleiben unveraendert. Noch keine Factory- oder Runnerimplementierung, kein
Materializer- oder Adapteraufruf, kein Matrixfall, keine Runtime und keine
Forschungsprobe.
