# S1-KB: B1/B2-Frischzustands-Privatdigestkorrektur

## Ergebnis

S1-KB korrigiert die in S1-KA gefundenen vier Digestabweichungen. Alle
zwoelf S1-JZ-Privatzustandsrecords bestehen danach den statischen Rundlauf
gegen `DTS1CommonIntervalPrivateState.canonical_payload()` bitidentisch.

## Begrenzte Korrektur

Nur zwei verschachtelte Payloadformen wurden geaendert:

- B1 bildet den Fixed Adapter und jede Kantenrate als benanntes Mapping ab;
- B2 bildet den L-Zustand und jeden Eintrag als Mapping mit `node_id` und
  `value` ab.

Daraus folgen genau vier neue Privatzustandsdigests, jeweils fuer die Zwei-
und Dreiknotengeometrie von B1 und B2. Die acht B3-bis-B6-Payloads und ihre
Digests bleiben unveraendert.

Der korrigierte S1-JZ-Vertragsdigest lautet:

`83a5c6248d0dca0e0ba2461bbc6c0f76470a5af1b21ac89049238f1256380079`

Der S1-KA-Audit bleibt als historischer Befund gegen den fehlerhaften
Vorvertrag gebunden und wird nicht rueckwirkend umgedeutet.

## Abnahme

- zwoelf registrierte Privatzustandsrecords geprueft;
- zwoelf kanonische Rundlaeufe bestanden;
- null fehlgeschlagene Rundlaeufe;
- genau vier korrigierte B1/B2-Digests;
- genau acht unveraenderte B3-bis-B6-Digests.

Factory und Runner wurden nicht implementiert. Es gab keinen Materializer-,
Adapter- oder Intervallaufruf, keine technische Replik, keinen Profilfall,
keine Runtimeintegration und keine Forschungsprobe.

Entscheidung:

`B1_B2_CANONICAL_PRIVATE_PAYLOADS_AND_FOUR_DIGESTS_CORRECTED_ALL_TWELVE_ROUNDTRIPS_PASS`

Kanonischer Auditdigest:

`b4099484095dbdb5b4d5fbdfd047c5f953e34d31d92e50381f36f8e874c0fd27`

## Naechster zulaessiger Schritt

S1-KC darf denselben zuvor gesperrten Implementierungsschritt erneut
freigeben: ausschliesslich Frischzustandsfactory und privater reiner Runner
fuer `B1:P_IE_CAUSAL_TWO_SUBSTEP:r2`, zweimal mit hoechstens acht
technischen Intervallaufrufen. Keine andere Replik, kein vollstaendiger
Matrixfall, keine Runtime und keine Forschungsprobe.
