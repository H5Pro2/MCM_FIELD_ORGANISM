# S1-HJ: DTS-1 lokale Rollenwechsel und Kausalquellenvertrag

## Status

Statischer Zulassungsvertrag hinter S1-HI. Keine Transferfunktion, kein
Transferbetrag, keine Rate, kein Zeitgesetz, kein Integrator, keine
Feldrueckwirkung, keine Runtime und kein Lauf.

Entscheidung:

```text
DTS1_LOCAL_ROLE_CYCLE_AND_CAUSAL_ELIGIBILITY_BOUND_NO_DYNAMICS
```

S1-HJ sagt nur, welche Rollenwechsel eine spaetere Dynamik grundsaetzlich
verwenden duerfte und welche lokale Ursache dafuer notwendig waere.
Zulaessigkeit beweist weder, dass ein Wechsel stattfindet, noch wie gross oder
wie schnell er waere.

## Einziger Rollenzyklus

```text
frei -> leitend gebunden -> refraktaer -> frei
```

Es gibt genau drei zulaessige Rollenwechsel. Jeder bleibt auf derselben
vorhandenen ungerichteten Kante und verwendet dieselbe inhaltsfreie Regelklasse
an allen Kanten.

## Lokale Bindungszulassung

`frei -> leitend gebunden` ist nur zulaessig, wenn ein abgeschlossener
gueltiger DTS-1-Vorzustand an beiden Kantenendpunkten freie Ressource besitzt
und auf dieser bestehenden Kante aktuelle symmetrische schnelle
Feldbeteiligung vorliegt.

Die genaue lokale Feldobservable ist noch nicht ausgewaehlt. Insbesondere ist
keine Formel aus S-Werten, keine Schwelle und kein Transferbetrag gebunden.
Nachhall H, Adapterwert und Gain sind keine Bindungsursachen.

Die reine Buchungswirkung eines spaeter bestimmten Betrags waere:

```text
derselbe Betrag zu b_e
je die Haelfte dieses Betrags aus f_i und f_j
```

Dies beschreibt nur, wie S1-HI erhalten bliebe. Es ist keine
Dynamikgleichung.

## Lokale Umsatz- und Erholungszulassung

`leitend gebunden -> refraktaer` ist nur auf derselben Kante zulaessig, wenn
dort leitend gebundene Ressource waehrend eines positiven physischen Intervalls
vorliegt. Derselbe gebuchte Betrag wechselt von `b_e` nach `u_e`; freie
Endpunktressource bleibt dabei unveraendert.

`refraktaer -> frei` ist nur zulaessig, wenn auf derselben Kante refraktaere
Ressource waehrend eines positiven physischen Intervalls vorliegt. Derselbe
gebuchte Betrag verlaesst `u_e`; je eine Haelfte kehrt in die abgeleiteten
freien Endpunktanteile zurueck.

Weder Umsatz noch Erholung darf durch erkannte Kontaktart, Pause, Phase,
Wiederholungszahl, Alter eines Eintrags oder Resetkommando ausgeloest werden.
S1-HJ waehlt noch kein Zeitgesetz.

## Verbotene Abkuerzungen

Nicht zulaessig sind:

- `frei -> refraktaer`;
- `leitend gebunden -> frei`;
- `refraktaer -> leitend gebunden`;
- direkter Ressourcentransfer zwischen verschiedenen Kanten;
- Erzeugung oder Vernichtung einer Ressourcenrolle;
- H, Fixed Adapter, Gain oder Replayinhalt als Kausalquelle;
- globale Rangfolge, Gewinnerauswahl oder Nachnormierung;
- Observermessung, Sollausgang, Label, Reward, Loss, Objekt- oder Episoden-ID;
- Wiederholungs-, History-, Phasen- oder Alterszaehler;
- verschiedene Regeln nach Kante, Modalitaet oder Versuchsarm.

## Gleichzeitige lokale Konkurrenz

Spaetere Bindungsabsichten inzidenter Kanten muessen denselben abgeschlossenen
Vorzustand verwenden. Ihre gemeinsame Buchung darf an keinem Endpunkt mehr
freie Ressource beanspruchen als vorhanden ist. Eine Aufrufreihenfolge darf
keine Gewinnerkante bestimmen.

S1-HJ waehlt noch keine Konfliktloesung. Kann eine spaetere Regel die
gleichzeitige Belegung nicht eindeutig und bilanzerhaltend bestimmen, muss sie
vor jeder Teilzustandsausgabe abbrechen.

## Aussagegrenze

S1-HJ prueft nur den gerichteten Rollenzyklus, lokale notwendige Ursachen,
Buchungskompatibilitaet mit S1-HI und Fail-Closed-Konkurrenz. Nicht gezeigt
sind Rollenwechsel, Abschwaechung, Interferenz, Kapazitaetsfreigabe,
Wiederbeanspruchung oder eine Wirkung auf das MCM-Wahrnehmungsfeld.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1hj_local_role_transition_contract.py
tests/test_dynamic_substrate_s1hj_local_role_transition_contract.py
```

## Bester naechster Schritt

S1-HK darf nach dem naechsten `ok weiter` genau eine symmetrische lokale
Feldbeteiligungsobservable fuer die Bindungszulassung und ihre Nullfaelle
statisch waehlen. Noch kein Transferbetrag, keine Rate, keine
Dynamikgleichung, keine Feldrueckwirkung und kein Lauf.
