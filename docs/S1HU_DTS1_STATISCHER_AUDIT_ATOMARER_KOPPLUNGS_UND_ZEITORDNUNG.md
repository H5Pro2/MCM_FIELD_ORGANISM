# S1-HU: DTS-1 atomare Kopplungs- und Zeitordnung

## Status

Genau eine kausale Ordnung zwischen abgeschlossenem S/H-Feldzustand,
DTS-1-Ressourcenschritt und Kantenratenleser wurde statisch auditiert. Kein
Feldintegrator wurde ausgewaehlt oder implementiert. Keine Materialratenwerte,
keine Runtime und kein Feldlauf.

Entscheidung:

```text
ZULASSEN_DTS1_CLOSED_PRESTATE_PARALLEL_READ_ATOMIC_COMMIT
```

Die Zulassung betrifft nur eine nichtzirkulaere technische Reihenfolge. Sie
ist kein Feld- oder Funktionsbefund.

## Ein gemeinsamer abgeschlossener Vorzustand

Ein spaeterer Subschritt beginnt mit genau einem vollstaendigen Paar:

```text
L_n = unveraenderlicher MCM-Layer mit abgeschlossenem S_n und H_n
A_n = unveraenderliche gueltige DTS-1-Anatomie
W_n = explizites geschlossenes physisches Kontaktintervall
C   = feste technische Konfigurationen, Raten und Ablationskontrolle
```

Layer und Anatomie muessen dasselbe Knoten- und Kanteninventar besitzen.

## Zugelassene Ordnung

```text
CLOSED_PRESTATE_PARALLEL_READ_ATOMIC_COMMIT
```

Die sieben logischen Stufen lauten:

1. Geometrie, Zeit, Kontakte und Konfigurationen vollstaendig validieren.
2. `p_n` fuer alle Kanten ausschliesslich aus `S_n` bilden.
3. aktiven oder ablatierten `G_n` ausschliesslich aus `A_n` bilden.
4. `A_next` mit S1-HP nur aus `A_n`, `p_n` und `Delta_t` vorschlagen.
5. `L_next` nur aus `L_n`, `W_n`, `G_n` und den unveraenderten schnellen
   Feldgrenzen vorschlagen.
6. beide vollstaendigen Vorschlaege pruefen, ohne Vorzustaende zu mutieren.
7. das Paar `(L_next,A_next)` atomar uebernehmen oder gar keine Ausgabe
   liefern.

Die Berechnungsreihenfolge der beiden Vorschlaege ist technisch austauschbar,
weil keiner den anderen Endzustand lesen darf. Verbindlich ist ihre gemeinsame
Vorzustandsquelle und der atomare Abschluss.

## Explizite kausale Latenz

Neu gebundene Ressource in `A_next` darf das Feld nicht rueckwirkend ueber
das Intervall beeinflussen, das diese Bindung erst erzeugt hat. Ebenso darf
`S_next` nicht die Ressourcenaenderung ueber sein vorhergehendes Intervall
bestimmen.

Daher gilt:

```text
neues b in Subschritt n     -> frueheste Feldwirkung in n+1
neues S in Subschritt n     -> frueheste Beteiligungswirkung in n+1
```

Diese Ein-Subschritt-Latenz ist Bestandteil der ersten expliziten Ordnung.
Sie muss bei S1-HQ-Verfeinerung `n,2n,4n` zeitlich schrumpfen. Sinkt der
vollstaendige Feld-/Anatomierest nicht oder bleibt ein endlicher Latenzrest,
wird die gekoppelte Runtimearbeit gestoppt.

## Null- und Ablationsidentitaeten

- P0 delegiert bitgenau an den bestehenden neutralen Feldpfad und fuehrt
  keine DTS-1-Rechnung aus.
- A0 entwickelt DTS-1, delegiert den Feldvorschlag aber ebenfalls bitgenau an
  P0.
- A0 und A1 erzeugen aus identischem Vorzustand im selben Subschritt
  identisches `A_next`, weil beide dasselbe `S_n` lesen.
- Bei `b_e=0` im Vorzustand erzeugen A0 und A1 denselben ersten Feldvorschlag.
- Erst eine fruehere Feldabweichung darf in spaeteren Subschritten ueber
  anderes `S_n`, `p_n` und damit anderes `A_next` zurueckwirken.
- F0 haelt sein vor der Probe eingefrorenes Ratenledger unveraendert.

## Nicht zugelassene Ordnungen

| Ordnung | Grund |
|---|---|
| Ressource zuerst, danach `G(A_next)` fuer das ganze Intervall | Endzustand wuerde ueber sein Entstehungsintervall wirken |
| Feld zuerst, danach `p(S_next)` fuer das ganze Intervall | Feldendzustand wuerde den vorhergehenden Ressourcentransfer treiben |
| halbe Ressource, volles Feld, halbe Ressource | fuer den ersten Korridor reserviert; fuehrt einen zweiten Ressourcenquellzustand ein |
| implizite gekoppelte Iteration | zusaetzliche Solver- und Toleranzfreiheiten |
| teilweiser Commit in Aufrufreihenfolge | kann gemischten Feld-/Anatomiezustand hinterlassen |

Die symmetrische historische E1-Halbschrittordnung wird damit nicht auf DTS-1
uebernommen. Sie bleibt hoechstens spaetere numerische Vergleichsoption nach
bestandener erster Ordnung.

## Fail-Closed-Grenze

Vor einer Paaruebernahme wird abgebrochen bei:

- Geometrie-, Zeit-, Kontakt- oder Konfigurationsabweichung;
- ungueltiger Beteiligung, Rate, Anatomie oder Feldproposal;
- Ressourcen-, Positivitaets- oder Feldbereichsverletzung;
- Lesen eines Endzustands innerhalb desselben Subschritts;
- Mutation oder Teilcommit;
- Abweichung von P0/A0 vom bestehenden exakten neutralen Feldpfad;
- fehlender Konvergenz des vollstaendigen Paars unter `n,2n,4n`.

## Aussagegrenze

S1-HU zeigt nur, dass eine eindeutige kausale erste Kopplungsordnung ohne
algebraischen Kreis formulierbar ist. Nicht gezeigt sind ein geeigneter
Feldintegrator, gekoppelte Stabilitaet, Konvergenz, Feldwirkung oder
Baseline-Trennung.

## Bester naechster Schritt

S1-HV darf nach dem naechsten `ok weiter` ausschliesslich den privaten
gekoppelten Einzelschrittvertrag und seine technische Testmatrix spezifizieren.
Dabei muss der bestehende exakte P0/A0-Feldpfad erhalten bleiben. Noch keine
Implementierung, Materialratenwerte, Runtimeintegration oder Feldlauf.
