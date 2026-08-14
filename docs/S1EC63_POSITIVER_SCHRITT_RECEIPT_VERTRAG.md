# S1-EC63: Positiver-Schritt-Receipt-Vertrag

## Zweck

S1-EC63 schliesst die in EC62 gefundene Typgrenze, ohne die bewahrte
EC61-Nullschritt-Fixture umzudeuten. Dafuer existieren getrennte Receipt-
Typen, welche die exakt begrenzte positive Last eines spaeteren realen
n2/r2-Laufs abbilden koennen.

## Vertrag

### Bildungsreceipts

- genau vier Rollen: aktiv AB/BA und bildungsablatiert AB/BA
- genau `402` verbuchte Feldschritte je Receipt
- typisiertes E1-Zustandsobjekt und passender Zustandsdigest
- Quellen- und Receipt-Digest
- expliziter Modus `synthetic-contract` oder `real-wrapper`

### Probereceipts

- genau acht EC45-Rollen
- genau `200` verbuchte Feldschritte je Receipt
- P0 ohne Zustand
- aktive und rueckwirkungsablatierte Rollen mit aktivem AB/BA-Zustand
- bildungsablatierte Rollen mit bildungsablatiertem AB/BA-Zustand
- exakter Rueckwirkungsschalter
- Aktivierungs-/Nachhallvektor, Supportzahl und Quellen-Digest

### Gesamtergebnis

- vier Bildungsreceipts und acht Probereceipts
- 1.608 verbuchte Bildungsschritte
- 1.600 verbuchte Probeschritte
- 3.208 verbuchte Schritte insgesamt

Die synthetische Abnahme trennt diese verbuchte Vertragslast explizit von
der Ausfuehrung: `actual_field_steps_executed = 0`.

## Abnahme

- alle Rollen- und Rueckwirkungsrouten exakt
- falsche Schrittzahlen `401` und `199` werden fail-closed abgelehnt
- keine EC54-Wrapper- oder Feldkernreferenz im Fixture-Builder
- keine Persistenz, Forschungsentscheidung oder Claims
- 19 fokussierte Tests bestanden

Fixture-Digest:

`a1dce7d6ee522f5953556bc7ae4b090a21687bece3c23ac07bbc81f68fda400a`

## Bewertung

Die EC62-Luecke positiver Schrittwerte ist auf Vertragsebene geschlossen.
Dies ist weiterhin nur eine synthetische Typ- und Routenabnahme. Es wurden
keine 3.208 Feldschritte ausgefuehrt und keine reale Wrapperbindung
freigegeben.

Am besten geht es mit S1-EC64 weiter: getrennte Adapter fuer reale
EC54-Bildungs- und Probeausgaben definieren, welche deren vorhandene
Zustaende, Beobachtungen und Schrittzahlen verlustfrei in die EC63-Receipts
uebertragen. Zunaechst nur statische Signatur- und Konvertierungspruefung,
kein Wrapperaufruf.
