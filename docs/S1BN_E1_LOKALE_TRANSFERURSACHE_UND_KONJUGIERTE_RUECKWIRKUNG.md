# S1-BN: E1 lokale Transferursache und konjugierte Rueckwirkung

## Status

Statischer Kausal- und Vorzeichenvertrag fuer E1. Noch keine Runtime, kein
Snapshot-Schema, kein Testlauf und kein Memory-, Lern-, Organismus- oder
KI-Befund.

## Entscheidung

E1 verwendet genau eine lokale Ursache: die bereits vorhandene schnelle
Feldspannung zwischen den Endpunkten einer bestehenden ungerichteten
MCM-Kante.

Fuer `e = {i,j}` und schnelle Feldwerte `S_i,S_j` im vorhandenen Bereich
`[-1,1]` wird die dimensionslose Teilnahme definiert als:

```text
p_e(S) = ((S_i - S_j) / 2)^2
0 <= p_e <= 1
```

`p_e` ist invariant gegen Vertauschung von `i` und `j` sowie gegen einen
gemeinsamen Vorzeichenwechsel. Es verwendet weder Modalitaet noch Label,
Objektklasse, Wiederholungszaehler oder gewuenschtes Ergebnis.

## Bindungsursache

Die in S1-BM definierte Kantenbindung `b_e` darf nur zunehmen, wenn an beiden
Endpunkten freie Ressource und auf der Kante Feldspannung vorhanden sind.
Der Bindungsanteil hat deshalb die Vorzeichenform:

```text
Bindung_e proportional zu
p_e(S) * (f_i / q_i) * (f_j / q_j)
```

Damit gilt ohne Sonderfall:

```text
p_e = 0       -> keine neue Bindung
f_i = 0       -> keine neue Bindung
f_j = 0       -> keine neue Bindung
b_e = 0       -> Bindung bleibt bei Feldspannung moeglich
```

Die Produktform erzeugt lokale Konkurrenz: Bereits an anderen inzidenten
Kanten gebundene Ressource senkt `f_i` oder `f_j` und damit die weitere
Bindungsbereitschaft derselben Feldorte.

## Kontinuierliche Freigabe

Jede vorhandene Bindung besitzt einen allgemeinen, inhaltsfreien Rueckfluss:

```text
Freigabe_e proportional zu b_e
```

Er wird weder durch ein Loeschsignal noch durch eine erkannte Phase
ausgeloest. Im vollstaendig spannungsfreien Feld bleibt nur die Freigabe. Sie
fuehrt gebundene Ressource kontinuierlich an beide Endpunkte zurueck.

## Vorzeichen der Gesamtaenderung

Die spaetere Minimalgleichung muss ausschliesslich die Differenz dieser beiden
Fluesse verwenden:

```text
d b_e / dt = Bindung_e - Freigabe_e
```

Zusammen mit der S1-BM-Identitaet folgt fuer jeden Endpunkt automatisch:

```text
d f_i / dt = -0.5 * Summe(d b_e / dt fuer e inzident an i)
```

Die konkrete Integrationsform muss den zulaessigen Bereich ohne
nachtraegliches Clipping und ohne globale Nachnormierung invariant halten.

## Konjugierte Rueckwirkung

Die Bindung wird nicht als separater Lesewert auf `S` addiert. Sie veraendert
ausschliesslich die Leitfaehigkeit derselben vorhandenen Kante:

```text
r_e(b_e) = r_0 * (1 + gamma * b_e / q_0)
gamma >= 0
```

Der dadurch vermittelte schnelle Feldfluss besitzt weiterhin die vorhandene
diffusive Vorzeichenform:

```text
J_e = r_e(b_e) * (S_j - S_i)
```

Die Kante bleibt symmetrisch und konservativ: Was auf einer Seite in den
internen Feldfluss eingeht, verlaesst die andere Seite mit entgegengesetztem
Vorzeichen. E1 erzeugt keinen externen Antrieb und keine neue Kante.

`gamma = 0` ist die Rueckwirkungsablation. E1 opt-in aus bedeutet dagegen,
dass weder E1-Zustand noch E1-Dynamik angelegt werden und die heutige neutrale
S/H-Runtime exakt erhalten bleibt.

## Warum diese Kopplung konjugiert ist

Dieselbe lokale Wechselwirkung besitzt beide Rollen:

```text
Feldspannung auf e
-> bindet lokale Ressource an e
-> veraendert die Leitfaehigkeit von e
-> veraendert spaeteren Feldfluss auf e
```

Es gibt keinen unabhaengigen Schreibpfad und keinen nachgelagerten
Speicherleser. Trotzdem ist die Form eine bewusst entworfene
Plastizitaetsregel und kein Beleg fuer ein neues Naturprinzip.

## Nullkontaktgrenze

Nullkontakt bedeutet weiterhin keine neuen Rezeptorwerte. Er bedeutet nicht
automatisch `S_i = 0`. Solange das schnelle Feld intern noch Spannung traegt,
kann Bindung und Freigabe gleichzeitig auftreten. Erst im spannungsfreien
Grenzfall `p_e = 0` gilt auf jeder Kante reine Freigabe.

Ein spaeterer Nullkontaktversuch muss deshalb S/H-Verlauf, `p_e`, Bindungs-
und Freigabefluss getrennt berichten. Andernfalls duerfte eine blosse
Feldrelaxation nicht als E1-Freigabe interpretiert werden.

## Gegenprognosen

Vor Implementierung gelten folgende unterscheidbare technische Erwartungen:

1. **Fester Gain:** Bei identischem festem `r_e` gibt es keine
   geschichtsabhaengige Aenderung der Kantenleitfaehigkeit.
2. **Eingefrorenes E1:** Ein fixiertes `b_e` wirkt wie ein fester raeumlicher
   Gain und darf nicht als Plastizitaet gelten.
3. **Leaky Knotenregister:** Es kann lokale Amplitude fortsetzen, besitzt aber
   keine knotenweise konkurrierende Kantenbilanz.
4. **F3:** Es transportiert dynamische Knotenmasse bei fester Kopplungsform;
   E1 veraendert Kantenleitfaehigkeit bei fester Knotenkapazitaet.
5. **Rueckwirkungsablation:** `gamma = 0` darf trotz veraendertem `b_e` keine
   spaetere Feldfortsetzung veraendern.
6. **E1 aus:** Der neutrale S/H-Pfad und sein Zustandsdigest bleiben exakt
   unveraendert.

## Noch nicht festgelegt

- die beiden positiven Raten fuer Bindung und Freigabe;
- eine erhaltende zeitdiskrete oder exakte Integrationsform;
- der zulaessige Wertebereich von `gamma`;
- der opt-in Zustandscontainer;
- die Einbindung in den gemeinsamen Feldgenerator;
- Testwelten, Lauflaengen und Erfolgsschwellen.

## Aussagegrenze

S1-BN legt eine plausible technische Ursache-Wirkungs-Kette fest. Die Form
liegt in der Klasse ressourcenbegrenzter adaptiver Diffusionskoeffizienten.
Sie ist daher kein Neuheitsbeleg und noch kein Nachweis von Praegung,
Vergessen, Rekonstruktion oder MCM-Memory.

## Bester naechster Schritt

S1-BO hat die dimensionskonsistente Minimalgleichung und eine
bereichserhaltende Integrationsstrategie gebunden. Als naechstes spezifiziert
S1-BP den kleinsten isolierten, opt-in E1-Zustandscontainer und seine reine
Zustandsentwicklung ohne Einbindung in S/H, Snapshot oder `current_api`.
