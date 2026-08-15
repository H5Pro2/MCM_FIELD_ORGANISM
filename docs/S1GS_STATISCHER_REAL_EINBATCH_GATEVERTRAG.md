# S1-GS: Statischer Real-Einbatch-Gatevertrag

Stand: 2026-08-15

Status: `GESCHLOSSENER_GATEVERTRAG_KEINE_AUTORISIERUNG_KEINE_AUSFUEHRUNG`

## Gebundener Umfang

S1-GS begrenzt einen spaeteren realen Piloten auf:

```text
ein exaktes Fresh Binding
+ ein exakter naechster Batch
+ ein exakter aktueller LiveFieldCarrier
-> maximal ein Adapteraufruf
-> maximal ein realer Feldschritt
-> genau ein real-field-advance-Envelope oder Fail-Closed
```

## Autorisierungsgrenze

Vor einer spaeteren Ausfuehrung muessen in dieser Reihenfolge bestehen:

1. neue ausdrueckliche externe Besitzerfreigabe fuer den konkreten Lauf;
2. Bindung an genau einen Adapteraufruf und einen Feldschritt;
3. prozesslokales, nicht kopierbares Einmaltoken;
4. erneute Routen- und Budgetpruefung;
5. Tokenverbrauch unmittelbar vor dem einzigen Adapteraufruf.

Erfolg und Fehler verbrauchen die Freigabe. Retry, Nachparametrierung,
Teilergebnis, Persistenz und Claims bleiben verboten.

## Aktueller Zustand

S1-GS definiert nur den statischen Vertrag. Es liegt keine neue
Besitzerfreigabe vor, es existiert kein Token und es gibt weder
Real-Transition-Builder noch Realadapter. Entscheidung:

```text
REAL_SINGLE_BATCH_GATE_BOUND_AUTHORIZATION_AND_TOKEN_ABSENT
```

Es wurde kein Feldkernel ausgefuehrt. Dies ist kein Feld-, Substrat- oder
Memory-Befund.

## Bester naechster Schritt

S1-GT implementiert ausschliesslich einen synthetischen Lebenszyklus fuer das
prozesslokale Einmaltoken und prueft Erzeugung, Verbrauch, Ablauf und
Fail-Closed-Verhalten mit einer nicht realen Fixture. Eine Besitzerfreigabe
oder reale Ausfuehrung wird dadurch nicht erzeugt.
