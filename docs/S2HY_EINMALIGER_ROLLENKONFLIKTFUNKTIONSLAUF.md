# S2-HY - Einmaliger Rollenkonfliktfunktionslauf

## Status

`S2HY_ROLE_CONFLICT_FUNCTION_CONFIRMED_DIRECT_ROLE_FILL_EXPLAINS`

Lauf-ID: `s2hy-role-conflict-20260831-01`

Der einmalig freigegebene S2-HY-Hauptlauf wurde vollstaendig aufgezeichnet,
unabhaengig read-only verifiziert und anschliessend ausschliesslich aus den
gespeicherten Belegen ausgewertet.

## Technischer Abschluss

- genau ein Aufruf von `run_main_once`;
- keine Wiederholung und keine Parameteraenderung;
- zwei frische Fuenf-Schritt-Geschichten;
- vier gerichtete Rollenfaelle mit den gebundenen Q0/Q1-Spiegelproben;
- `60` Operationen und `120` START-/RESULT-Ereignisse;
- terminaler Laufstatus: `COMPLETE`;
- unabhaengiger Verifikatorstatus: `RECORDING_COMPLETE`;
- Verifikationsfehler: keine;
- aufgezeichnete Bytezahl: `149868`;
- zehn Quellhashes vor und nach dem Lauf identisch;
- Gate nach dem Lauf: `False`;
- S2-HW unveraendert als `NOT_EVALUABLE` erhalten.

## Funktionsbefund

In beiden Geschichten waren `A_RECENT` und `B_STABLE` zum Probezeitpunkt
gleichzeitig als `AVAILABLE_COMPLETE` vorhanden. Der nach der Stabilisierung
gebildete A-Zustand veraenderte die Slow-Bank nicht.

Die vier vorab gebundenen Faelle wurden bestaetigt:

| Fall | Geschichte | Gewaehlte Rolle | Ausgabe |
| --- | --- | --- | --- |
| `c01` | `h0` | `A_RECENT` | Q0 |
| `c02` | `h0` | `B_STABLE` | Q1 |
| `c03` | `h1` | `A_RECENT` | Q1 |
| `c04` | `h1` | `B_STABLE` | Q0 |

Damit bestimmte ausschliesslich die explizit gebundene Rolle die neun
maskierten Ergaenzungen. Die jeweils nicht gewaehlte, gleichzeitig vorhandene
Rolle hatte keinen erkennbaren Einfluss. Alle sichtbaren Werte blieben
unveraendert.

Verbraucher und unabhaengige direkte rollenadressierte Maskenfuellbaseline
lieferten in allen vier Faellen dieselbe Ausgabe. Der gespeicherte
Terminalbefund lautet deshalb
`S2HS_ROLE_CONFLICT_FUNCTION_CONFIRMED_BASELINE_EXPLAINS`.

## Read-only-Grenze

Saemtliche Verbraucher- und Baselinebefunde weisen identische Vor- und
Nachzustandsdigests aus. Auch die gemeinsamen Memory- und Bundlezustaende
blieben waehrend Projektion, Rollenbindung und Auswertung unveraendert.

## Belege

- Lauf: `reports/s2hy-role-conflict/s2hy-role-conflict-20260831-01/`
- Kontrolle: `reports/s2hy-role-conflict/s2hy-control-20260831-01/`
- Abschlussbefund:
  `reports/s2hy-role-conflict/s2hy-control-20260831-01/S2HY_BEFUND.json`
- Journal-SHA-256:
  `f58a5b9334a73aeda6c23df965bcdce66cb6112d863ab28b38eb6e410369f2c5`
- Completion-SHA-256:
  `97fb0d3c4ecebae808552188271db721b119fde2a9c6c1479e42729c7221eb73`

## Aussagegrenze

S2-HY bestaetigt fuer diese begrenzte Fixture, dass zwei gleichzeitig
vorhandene Memory-Bereiche kontrolliert und getrennt adressiert werden koennen.
Die direkte Rollenfuellung erklaert die konkrete Verbrauchsfunktion vollstaendig.

Nicht geprueft oder nachgewiesen wurden automatische Kontextwahl, Rangfolge,
Verschmelzung, Semantik, Feldrueckwirkung oder ein MCM-spezifischer
Memory-Mechanismus.
