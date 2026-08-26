# S1-YM: Statisches LPRH-1-Praeimplementierungs-Erratum

## Ergebnis

Beim Uebergang vom statischen Vertrag zur Implementierung wurde eine enge
Zaehlinkonsistenz festgestellt. Der Typ
`LPRH1TransientLocalPrototypeContext` enthaelt neun fremde Digestfelder und
einen eigenen Kontext-Digest. S1-YK band fuer diesen Typ irrtuemlich nur
acht fremde Digestrollen.

Die zusaetzliche Rolle ist `selected_prototype_digest_str`. Sie ist nicht
Teil der acht geordneten Quelldigests im Handoff-Receipt, muss im Kontext
aber dennoch eigenstaendig als SHA-256-Hexdigest validiert werden.

## Korrektur

Nur die Kontextinvariante
`ALL_EIGHT_DIGEST_ROLES_ARE_SHA256_HEX` wird durch
`ALL_NINE_FOREIGN_DIGEST_ROLES_ARE_SHA256_HEX` ersetzt. Der eigene
`context_digest_str` bleibt davon getrennt und wird weiterhin gegen das
kanonische Kontextpayload geprueft.

Alle anderen Bindungen aus S1-YG, S1-YI, S1-YK und S1-YL bleiben
unveraendert. Das Erratum aendert weder Architektur noch Forschungsrichtung.

## Grenze

S1-YM implementiert und fuehrt nichts aus. API, Snapshot, Produktion,
Feldkonsum und Feldschritt bleiben gesperrt. Die private reine
LPRH-1-Handoff-Implementierung ist erst im gesonderten Schritt S1-YN
zulaessig.

Maschinenlesbare Bindung:
[S1YM_LPRH1_STATISCHES_PRAEIMPLEMENTIERUNGSERRATUM_V1.json](S1YM_LPRH1_STATISCHES_PRAEIMPLEMENTIERUNGSERRATUM_V1.json).
