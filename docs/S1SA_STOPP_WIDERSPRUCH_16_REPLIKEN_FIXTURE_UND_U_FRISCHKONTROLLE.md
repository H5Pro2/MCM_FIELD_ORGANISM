# S1-SA: Stopp wegen widerspruechlicher Zeitbindung der U-Frischkontrolle

## Status und Umfang

S1-SA sollte ausschliesslich den statischen gemeinsamen synchronen
Vier-Knoten-Expositionssegment-, Ereignisplan- und 16-Repliken-
Fixturevertrag binden. Vor der Wahl konkreter Werte und Dauern wurde die in
S1-PZ und S1-RA geforderte Praefix- und Zeitordnung geprueft.

Dabei wurde ein Widerspruch innerhalb der U-Familie festgestellt. Deshalb
wurden keine Kontaktwerte, Dauern, Ticks, Digests oder Fixtures gebunden.
Es gab keine Implementierung, keinen Test, keinen Modellaufruf, keine
Matrixzelle und keinen Forschungslauf.

Verbindlicher Status:

```text
S1SA_FIXTURE_BINDING_STOPPED
SINGLE_FRESH_B_CONTROL_CANNOT_MATCH_TWO_DISTINCT_PRELUDES
NO_VALUES_NO_FIXTURE_NO_EXECUTION
```

## Unveraendert gueltige Bindungen

Folgende Anforderungen bleiben gemeinsam gueltig:

- jede Replik startet aus derselben oeffentlichen Frischprojektion;
- alle modellwirksamen Segmente muessen fuer alle 14 Rollen als synchrone
  Intervalle materialisiert werden;
- `GAP_EARLY` ist ein echter Praefix von `GAP_LATE` und deshalb zeitlich
  kuerzer;
- `U_EARLY` und `U_RELEASED` verwenden dieselbe A-Geschichte;
- beide verwenden dieselbe B-Geschichte und dieselbe B-Probe;
- `U_FRESH_B` soll vor derselben B-Geschichte einen zeitangepassten
  kontaktfreien Frischvorlauf erhalten;
- `ALIGN_READOUT_SH` und alle Beobachtungen bleiben zeitlos und passiv.

## Formaler Widerspruch

Seien:

- `t0` die identische Feldzeit aller Frischstarts;
- `a` die Dauer der gemeinsamen A-Geschichte;
- `e` die Dauer von `GAP_EARLY`;
- `l` die Dauer von `GAP_LATE`;
- `f` die Dauer des einzigen Frisch-Nullvorlaufs von `U_FRESH_B`.

Wegen des echten Gap-Praefixes gilt zwingend:

```text
l > e
```

Die B-Geschichte beginnt damit in den beiden vorbelegten U-Repliken zu
verschiedenen Feldzeiten:

```text
U_EARLY:    t0 + a + e
U_RELEASED: t0 + a + l
```

Soll ein einzelnes `U_FRESH_B` an beide Vorlaeufe zeitangepasst sein, muesste
gleichzeitig gelten:

```text
t0 + f = t0 + a + e
t0 + f = t0 + a + l
```

Das verlangt `e = l` und widerspricht `l > e`. Ein einzelner linearer
Frischarm kann deshalb beide Zeitlagen nicht kontrollieren.

## Unzulaessige Scheinloesungen

S1-SA verwirft folgende Umgehungen:

- ein verstecktes Fuellintervall in `U_EARLY`, weil es den gebundenen
  fruehen Gap verlaengert;
- ein Nullzeitintervall in `GAP_LATE`, weil dadurch kein echter zeitlicher
  Praefix entsteht;
- ein zweiter B-Kontakt im selben Frischarm, weil der zweite Kontakt nicht
  mehr aus einem Frischzustand folgt;
- unterschiedliche Frischfeldzeiten, weil dann die gemeinsame
  Frischprojektion und Zeitinterpretation verletzt werden;
- nur eine der beiden Zeitlagen still als Vergleich zu verwenden, weil der
  andere U-Kontrast dann keine zeitangepasste Frischkontrolle besitzt;
- zwei interne Frischpfade unter einer Replikkennung, weil dies die reale
  Anzahl unabhaengiger Repliken und Matrixzellen verschleiert.

## Kleinste methodisch saubere Korrektur

Die kleinste vollstaendige Korrektur waere, `U_FRESH_B` in zwei unabhaengige
Frischkontrollen aufzuteilen:

```text
U_FRESH_B_EARLY:
zeitangepasster Frisch-Nullpfad bis t0 + a + e
-> HISTORY_B_LOCAL -> ALIGN_READOUT_SH -> PROBE_B -> OBSERVE

U_FRESH_B_LATE:
zeitangepasster Frisch-Nullpfad bis t0 + a + l
-> HISTORY_B_LOCAL -> ALIGN_READOUT_SH -> PROBE_B -> OBSERVE
```

Damit wuerde die Expositionsachse von 16 auf 17 unabhaengige Repliken und
die Baselinekreuzung von 224 auf 238 Zellen wachsen. Die B-Geschichte und
Probe blieben in allen vier U-Repliken wertidentisch. Nur der kontaktfreie
Frischvorlauf waere an die jeweilige Vergleichszeit angepasst.

Diese Aenderung ist noch nicht freigegeben und wird in S1-SA nicht
vorgenommen.

## Alternative mit geringerem Umfang

Eine 16-Repliken-Achse koennte nur erhalten bleiben, wenn fachlich auf einen
der beiden zeitangepassten Frischvergleiche verzichtet oder eine andere
U-Replik entfernt wird. Das wuerde den bisherigen Umfang und die
Comparatorabdeckung aendern und darf deshalb nicht still entschieden
werden.

## Projektgrenze

S1-SA erzeugt keinen negativen Kandidatenbefund. Der Stopp betrifft nur die
logische Konsistenz des vorgesehenen gemeinsamen Expositionsfixtures. Die
Vier-Knoten-Geometrie, die 14 technisch abgenommenen Modellrollen und ihre
Aufrufoberflaeche bleiben unveraendert.

Vor einem neuen Fixturevertrag ist eine ausdrueckliche fachliche
Richtungsentscheidung erforderlich:

1. 17 Repliken mit zwei getrennten zeitangepassten U-Frischkontrollen; oder
2. ein ausdruecklich reduzierter U-Vergleich unter Beibehaltung von 16
   Repliken.

Bis zu dieser Entscheidung bleiben konkrete Segmentwerte, Implementierung,
Tests, Matrixaufbau, Comparator und Forschungslauf gesperrt.
