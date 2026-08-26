# S1-HN: DTS-1 diskreter Integrationsvertrag

## Status

S1-HN bindet genau einen positivitaets- und bilanzwahrenden diskreten
Integrationsvertrag fuer die in S1-HM zugelassene technische Transferfamilie.
Es werden keine Parameterwerte gewaehlt und kein ausfuehrbarer Schritt
implementiert. Feldrueckwirkung, Runtime, Forschungslaeufe und Funktionsclaims
bleiben geschlossen.

Entscheidung:

```text
DTS1_POSITIVITY_CONSERVATION_DISCRETE_CONTRACT_BOUND
```

## Abgeschlossener Vorzustand

Jeder diskrete Schritt liest `f_i`, `b_e`, `u_e` und `p_e` genau einmal aus
demselben gueltigen S1-HI-Vorzustand. Innerhalb des Schritts erzeugte Ressource
darf nicht erneut als Quelle verwendet werden. Dadurch bleiben Rollenfolge und
Kausalordnung aus S1-HJ erhalten.

Fuer `Delta_t >= 0` und die weiterhin wertoffenen S1-HM-Ratensymbole gelten:

```text
alpha_bind = 1 - exp(-k_bind * Delta_t)
alpha_turn = 1 - exp(-k_turn * Delta_t)
alpha_rec  = 1 - exp(-k_rec  * Delta_t)
```

Bei nichtnegativen Raten liegen alle Anteile in `[0,1]`. Fuer
`Delta_t = 0` sind sie null und der gesamte Schritt ist die Identitaet. Die
Form bindet keine Rate und keine Zeitkonstante numerisch.

## Gleichzeitige Bindungszuteilung

Aus dem abgeschlossenen Vorzustand wird fuer jede Kante `e={i,j}` zuerst ein
Angebot berechnet:

```text
d_e = alpha_bind * p_e * 2 * min(f_i, f_j)
D_i = 0.5 * Summe_e~i(d_e)

a_i = 1                         falls D_i = 0
a_i = min(1, f_i / D_i)         sonst

x_e = d_e * min(a_i, a_j)
```

Alle `d_e`, danach alle `D_i` und erst danach alle `x_e` werden logisch
gemeinsam bestimmt. Eine Kantenreihenfolge darf das Ergebnis nicht
beeinflussen. Aus `x_e <= d_e*a_i` folgt:

```text
0.5 * Summe_e~i(x_e) <= a_i * D_i <= f_i
```

`a_i` ist eine lokale Vorabzulassung aus dem Quellbudget. Sie ist weder
Clipping eines bereits gebuchten Zustands noch nachtraegliche Normierung.

## Umsatz, Erholung und atomare Buchung

Ebenfalls nur aus dem abgeschlossenen Vorzustand:

```text
y_e = alpha_turn * b_e
z_e = alpha_rec  * u_e
```

Danach werden alle Rollen atomar gebucht:

```text
b_e' = b_e + x_e - y_e
u_e' = u_e + y_e - z_e
f_i' = f_i
       - 0.5 * Summe_e~i(x_e)
       + 0.5 * Summe_e~i(z_e)
```

Neu gebundenes `x_e` kann im selben Schritt nicht umgesetzt werden. Neu
umgesetztes `y_e` kann im selben Schritt nicht erholen. Damit gibt es keinen
verdeckten Rollen-Shortcut.

## Positivitaet und Bilanz

- `y_e <= b_e`, daher ist `b_e' >= x_e >= 0`.
- `z_e <= u_e`, daher ist `u_e' >= y_e >= 0`.
- die gemeinsame Bindungszulassung garantiert `f_i' >= 0`; Erholung kann
  freie Ressource nur vergroessern.
- `x_e` wird je zur Haelfte an beiden Endpunkten entnommen und vollstaendig
  in `b_e` gebucht.
- `y_e` wechselt nur von `b_e` nach `u_e`.
- `z_e` wird aus `u_e` entnommen und je zur Haelfte an beide Endpunkte
  zurueckgegeben.

Damit bleiben lokale und globale S1-HI-Erhaltungsidentitaet algebraisch
erhalten. Clipping, Nachnormierung oder Zustandsreparatur sind weder Teil des
Verfahrens noch als Fehlerbehandlung zulaessig.

Fuer kleine Intervalle gilt `alpha_x = k_x*Delta_t + O(Delta_t^2)`. Solange
die gemeinsame Ressourcenzulassung nicht aktiv begrenzt, ist die Abbildung
damit erster Ordnung konsistent zur S1-HM-Flussfamilie. Die Zulassung selbst
ist die notwendige diskrete Durchsetzung des endlichen gemeinsamen Budgets.

## Fail-Closed-Grenze

Ein spaeterer ausfuehrbarer Schritt muss vor Zustandsuebernahme abbrechen bei:

- negativem, nichtendlichem oder booleschem Intervall- oder Ratenwert;
- ungueltigem S1-HI-Vorzustand oder verletzter Ressourcenbilanz;
- fehlender, doppelter oder nichtkanonischer Kante;
- nichtendlichem `p_e` oder `p_e` ausserhalb `[0,1]`;
- Verletzung einer Quellobergrenze oder eines gemeinsamen Knotenbudgets;
- fehlendem Positivitaets- oder Erhaltungsnachweis;
- erforderlichem Clipping, Nachnormieren oder Reparieren;
- aufrufreihenfolgeabhaengiger Teilzulassung.

Eine Abbruchdiagnose ist kein Forschungsbefund.

## Aussagegrenze

Der Vertrag zeigt nur, dass eine diskrete Abbildung fuer DTS-1 konstruktiv
formulierbar ist, ohne die Ressourcenanatomie zu verletzen. Nicht gezeigt
sind numerische Konvergenz in einer Implementierung, Abschwaechung,
Interferenz, Kapazitaetsfreigabe im Feld, Wiederbeanspruchung oder irgendeine
Funktion des MCM-Wahrnehmungsfeldes.

## Bester naechster Schritt

S1-HO darf nach dem naechsten `ok weiter` ausschliesslich einen reinen,
zustandsfreien Einzelschritt-Implementierungsvertrag und dessen technische
Testmatrix festlegen. Noch keine Parameterwerte, keine Feldrueckwirkung,
keine Runtimeintegration und kein Forschungs- oder Feldlauf.
