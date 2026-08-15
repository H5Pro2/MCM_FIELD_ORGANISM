# S1-GW: Externes Besitzer-Autorisierungsschema

Stand: 2026-08-15

Status: `SCHEMA_OHNE_ZIELINSTANZ_TOKEN_ODER_AUSFUEHRUNG`

## Umsetzung

S1-GW definiert das unveraenderliche Schema fuer eine spaetere externe
Besitzerfreigabe. Eine gueltige Freigabe muss gemeinsam binden:

- extern attestierten Nachrichtenursprung und Nachrichtendigest;
- Projekt `MCM_FIELD_ORGANISM` und einen namentlich genannten Lauf;
- S1-GS-Gate, exaktes Binding, Batchindex und Carrier;
- maximal einen Adapteraufruf und einen Feldschritt;
- Einmaligkeit und nicht persistente Ausfuehrung;
- kein Retry, keine Nachparametrierung und kein Teilergebnis;
- keine Memory-, Feldzeit-, Organisations- oder KI-Claims;
- Ablauf nach Erfolg oder Fehler.

## Aktuelle Nachricht

`ok weiter` ist ein Fortsetzungsbefehl fuer die nicht reale Projektarbeit. Er
ist keine ausdrueckliche Realfreigabe und wird von S1-GW nicht als solche
interpretiert.

## Geschlossene Grenze

Schema-Integritaet ist keine externe Authentizitaet. Es gibt keine
Autorisierungsfactory, keine Autorisierungsinstanz, noch kein ausgewaehltes
Ziel, keinen Realtoken und keine Ausfuehrung.

Entscheidung:

```text
EXTERNAL_OWNER_AUTHORIZATION_SCHEMA_BOUND_TARGET_AND_ORIGIN_REQUIRED
```

Dies ist eine technische Freigabegrenze, kein Feld-, Substrat- oder
Memory-Befund.

## Bester naechster Schritt

S1-GX waehlt statisch und deterministisch genau ein kleinstes Pilotziel aus
den bestehenden sechs S1-GO-Armen aus und bindet dessen Binding, ersten Batch
und Anfangscarrier. Es erfolgt kein Feldschritt und noch keine Freigabeanfrage.
