# S1-HK: DTS-1 symmetrische lokale Feldbeteiligungsobservable

## Status

Statischer Observablevertrag hinter S1-HJ. Genau eine lokale schnelle
Feldgroesse und ihre Nullfaelle sind gebunden. Kein Transferbetrag, keine
Schwelle, keine Rate, kein Zeitgesetz, kein Integrator, keine
Feldrueckwirkung, keine Runtime und kein Lauf.

Entscheidung:

```text
DTS1_SYMMETRIC_LOCAL_FAST_FIELD_PARTICIPATION_BOUND_NO_TRANSFER_LAW
```

## Observable

Fuer eine vorhandene ungerichtete Kante `e = {i,j}` und normierte schnelle
Feldwerte `S_i,S_j` gilt ausschliesslich:

```text
p_e(S) = ((S_i - S_j) / 2)^2
S_i,S_j in [-1,1]
p_e in [0,1]
```

Die Observable liest nur den abgeschlossenen schnellen S-Vorzustand an den
beiden Endpunkten derselben Kante. Sie liest weder H noch DTS-1-Ressourcen,
Adapter, Gain oder globale Feldwerte.

## Eigenschaften

`p_e` ist invariant gegen:

- Vertauschung der beiden Kantenendpunkte;
- gemeinsamen Vorzeichenwechsel von `S_i` und `S_j`;
- Kantenkennung und Modalitaet bei gleichen Endwerten.

Der Maximalwert `1` tritt bei antipodischen Grenzwerten `1` und `-1` auf.
Nichtendliche oder ausserhalb `[-1,1]` liegende Eingaben werden verworfen und
nicht geclippt.

## Nullfaelle

```text
S_i = S_j -> p_e = 0
uniformes S-Feld -> p_e = 0 auf jeder Kante
S_i = S_j = 0 -> p_e = 0
```

`p_e = 0` sperrt nur die Bindungszulassung `frei -> leitend gebunden` auf
dieser Kante. Lokaler Umsatz `leitend gebunden -> refraktaer` und Erholung
`refraktaer -> frei` lesen die Observable nicht.

## Keine versteckte Transferregel

Ein positiver Wert bedeutet nur, dass lokale schnelle Feldbeteiligung
vorliegt. Er ist weder Transferbetrag noch Rate oder Wahrscheinlichkeit. Auch
bei `p_e > 0` bleibt Bindung ohne freie Ressource an beiden Endpunkten
unzulaessig.

Nicht gebunden sind:

- Schwelle, Clipping oder Fallunterscheidung;
- Multiplikation mit freier Ressource;
- Transferbetrag pro Zeitintervall;
- Bindungs-, Umsatz- oder Erholungsrate;
- diskrete oder kontinuierliche Dynamik;
- Wirkung einer Ressourcenrolle auf das Feld.

## Bewusste Baselinegleichheit

S1-HK verwendet dieselbe Kantenbeteiligungsobservable wie die historische
zweistufige E1-Baseline. Damit wird keine neue Ursache fuer DTS-1 erfunden.
Eine spaetere eigene Gegenprognose muss aus der endlichen
frei/gebunden/refraktaer-Aufteilung und nicht aus einer speziell angepassten
Feldobservable entstehen.

Kann der spaetere DTS-1-Verlauf trotz dieser dritten Rolle vollstaendig durch
E1 oder eine andere registrierte Baseline erklaert werden, bleibt die
Verwerfungsregel aus S1-HH aktiv.

## Aussagegrenze

S1-HK zeigt nur Wertebereich, Symmetrie, Nullfaelle und Eingabevalidierung der
Observable. Es zeigt keinen Ressourcenwechsel, keine Abschwaechung,
Interferenz, Freigabe, Wiederbeanspruchung oder Feldwirkung.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1hk_edge_participation_contract.py
tests/test_dynamic_substrate_s1hk_edge_participation_contract.py
```

## Bester naechster Schritt

S1-HL darf nach dem naechsten `ok weiter` nur die dimensions- und
bilanzbedingten Faktoren binden, die ein spaeterer Transferbetrag mindestens
besitzen muesste. Noch keine Rate, keine vollstaendige Dynamikgleichung, keine
Feldrueckwirkung und kein Lauf.
