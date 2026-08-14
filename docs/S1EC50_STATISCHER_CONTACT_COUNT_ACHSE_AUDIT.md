# S1-EC50: Statischer Contact-Count-Achsen-Audit

## Anlass

Vor der statischen Bindung des EC49-Adapters an reale Kerne wurde die
vollstaendige EC44-Versuchsmatrix erneut mit dem neuen Common-Probe-Pfad
verglichen.

EC44 untersuchte zwei getrennte Kontaktzweige:

- `n1`: Ein-Kontakt-Kontrollzweig;
- `n2`: Zwei-Kontakt-Zweig mit beobachtetem P0-Reihenfolgekontrast.

EC45 bis EC49 fuehren acht Rollen ueber `r2`, `r4` und `r8`, tragen die
Kontaktzahl aber nicht als typisierte Achse.

## Befund

Der EC49-Adapter besitzt derzeit:

```text
3 Verfeinerungen * 8 Rollen = 24 Samples
```

Der vollstaendige, nicht vermischte Anschluss benoetigt:

```text
2 Kontaktzweige * 3 Verfeinerungen * 8 Rollen = 48 Samples
```

`n1` darf nicht stillschweigend verworfen werden. Es bleibt der notwendige
Kontrollzweig. Ein spaeterer n2-Befund darf nicht auf n1 generalisiert
werden.

## Entscheidung

`KORREKTUR_CONTACT_COUNT_AXIS_MISSING`

**STOPP fuer die reale Kernelbindung und jede Common-Probe-Ausfuehrung.**

Dies ist keine wissenschaftliche Sackgasse des Vorhabens. Die Luecke ist im
Adapter- und Ergebnisschema klar lokalisierbar. Erlaubt ist nur, die Achse
`contact_count in (1, 2)` in Handoffs, Reset-Slots, Rollenreceipts und
Auswertung wiederherzustellen und synthetisch abzunehmen.

Zwoelf fokussierte gemeinsame Tests bestehen. Es wurden keine Adapter- oder
Feldkerne ausgefuehrt.

Audit-Digest:
`e4e779ba04a955bea10f10d34a42727f9d89cd19c3ac50a96e54aa71ceb9ec14`

## Naechster Schritt

Am besten geht es mit S1-EC51 weiter: EC49 um die explizite Kontaktachse
erweitern und alle 48 synthetischen Slots getrennt durch EC47/EC46 fuehren.
Erst danach darf EC50 als Real-Binding-Schritt neu angesetzt werden.
