# S1-EC90: STOPP r4/r8-Receipt-Konverter-Schrittsperre

## Prueffrage

Kann die bestehende EC54-/EC65-/EC64-/EC63-Kette die neuen EC89-Handoffs
unveraendert fuer `r4` und `r8` verarbeiten?

## Befund

Teilweise:

- EC54 waehlt Bildungs- und Probeplaene ueber die Refinement-ID des Slots;
- EC54 reicht die gebundene Refinement-ID an den Bildungskern weiter;
- EC65 delegiert die aufgeloesten Objekte und enthaelt keine festen
  Schrittzahlen.

Die nachgelagerte Kette ist jedoch explizit `r2`-gebunden:

- EC64 verlangt beim Bildungsdiagnosegate exakt 402 Schritte;
- EC64 verlangt bei der Probe exakt 200 Schritte;
- EC63 akzeptiert in Bildungsquittungen nur 402 Schritte;
- EC63 akzeptiert in Probequittungen nur 200 Schritte;
- die synthetischen EC64-Hilfen verlangen den alten
  `E1CommonProbeN2R2ObjectHandoff` und setzen `r2` fest.

`r4` mit 804/400 und `r8` mit 1.608/800 Schritten wuerden daher korrekt
fail-closed abgelehnt. Eine synthetische Gesamtroute ist noch nicht
zulaessig.

Entscheidung:
`STOP_R4_R8_ROUTE_RECEIPT_CONVERTER_STEP_LOCK`

## Korrekturgrenze

Die bestehende und bereits real bestaetigte `r2`-Kette darf nicht
umgeschrieben werden. Erforderlich ist eine getrennte verallgemeinerte
Erweiterung, die:

- `r4/r8` und ihre EC88-Schrittbudgets typisiert bindet;
- Schrittzahlen aus dem jeweiligen Plan prueft;
- Rollen-, Zustands-, Support- und Digest-Gates beibehaelt;
- zuerst nur synthetische Outputs akzeptiert;
- keine Ausfuehrung, Persistenz, EC46-Entscheidung oder Claims erlaubt.

## Aussagegrenze

Dies ist ein technisches Integrations-STOPP, keine wissenschaftliche
Sackgasse und kein negativer Feldbefund. Es wurden keine Feldschritte
ausgefuehrt.

Am besten geht es mit S1-EC91 weiter: separate verfeinerungsgebundene
`r4/r8`-Receipt-Typen und reine Konverter implementieren und gegen die
EC89-/EC88-Budgets synthetisch testen. Die bestehenden EC63-/EC64-r2-Dateien
bleiben unveraendert.
