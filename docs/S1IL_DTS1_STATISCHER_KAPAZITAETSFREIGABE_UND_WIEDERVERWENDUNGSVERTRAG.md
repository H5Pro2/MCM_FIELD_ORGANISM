# S1-IL: Statischer DTS-1 Kapazitaetsfreigabe- und Wiederverwendungsvertrag

## Status

S1-IL bindet ausschliesslich Funktion, Gegenprognosen, direkte Messrollen,
Kontrollen und Verwerfungsbedingungen fuer lokale Kapazitaetsfreigabe und
anschliessende Wiederverwendung. Es werden keine Fixturewerte gewaehlt, keine
Gleichung geaendert, kein Harness implementiert und kein Ressourcen- oder
Feldschritt ausgefuehrt.

Entscheidung:

```text
DTS1_LOCAL_CAPACITY_RELEASE_AND_ADJACENT_REUSE_CONTRACT_BOUND
```

Vertragsdigest:

```text
05582932f13789dab3ff612ea2035ffbfb3180154203ee1574e67b6a86e2c550
```

Gebundene Quellen sind der S1-HH-Vertrag
`5eae6462ed7019f3e2f09b0f1ba0ae3859781c7be852d7d4cdf011b4ae602388`
und der S1-IK-Audit-Receipt
`7d0a5bffd19cc7f212392b1d4a9c4d8ea8c79ffb1414d6a9fbc9a936ff9dedfe`.

## Funktionsprognose

Gebunden bleibt die offene Dreiknotenlinie mit den benachbarten vorhandenen
Kanten A und B. Beide Kanten teilen genau ein endliches Ledger am mittleren
Knoten. Zuerst wird fuer beide spaeteren Arme genau ein gemeinsamer positiver
A-Belastungszustand mit positiver refraktaerer Ressource gebildet.

Danach unterscheiden sich nur zwei zeitgleiche kontaktfreie Fenster:

```text
RECOVERY-ON   refraktaer -> frei ist aktiv
RECOVERY-OFF  refraktaer -> frei ist abgetragen
```

Dauer, Nullbeteiligung, leitender Umsatz, Ereignisgrenzen und komplette
Voranatomie bleiben identisch. Erst danach erhalten beide Arme dieselbe
positive B-Probe auf der benachbarten Konkurrenzkante.

Die gebundene Prognose verlangt gemeinsam:

1. strikt positive direkte Recovery im kontaktfreien RECOVERY-ON-Fenster;
2. bitgenau gleiche leitende Bindung nach beiden Fenstern;
3. weniger refraktaere und mehr freie Ressource mit RECOVERY-ON;
4. strikt mehr akzeptierte B-Bindung nach RECOVERY-ON.

Kein Feldwert darf einen fehlenden direkten Freigabe- oder
Wiederbindungsledger ersetzen.

## Direkte Messrollen

- komplette Vor- und Nachanatomie fuer Belastung, Freigabefenster und B-Probe;
- Engagement-, Turnover- und Recovery-Transfer je Kante und Intervall;
- freie Ressource an jedem Knoten, insbesondere direkt vor der B-Probe;
- akzeptierte B-Bindung und Knotenzulassung in beiden Armen;
- lokale und globale Erhaltungsreste an jedem Checkpoint;
- Recovery-Marge und zusaetzliche B-Bindung als getrennte Messgroessen;
- optionaler gemeinsamer S/H-Readout nur getrennt von der Ressourcenfolge.

Mit "derselben Ressource" ist keine markierte Einheit gemeint. Die
Wiederverwendung wird ausschliesslich durch das geschlossene lokale
Dreirollenledger, positive Freigabe und anschliessende zusaetzliche Bindung
am selben gemeinsamen Endpunkt bilanziert.

## Kontrollen

1. N01: wertidentische vollstaendige Wiederholung muss bitgenau sein;
2. N02: Recoveryrate null muss dem abgetragenen Recoverykanal bitgenau
   entsprechen;
3. N03: ohne refraktaere Ressource und ohne Turnoverquelle ist Recovery null;
4. N04: B-Beteiligung null erzeugt exakt null B-Bindung;
5. N05: A0 liefert den bitgenauen neutralen Feldpfad;
6. N06: ein vor der Freigabe fixierter Adapter erzeugt keinen armspezifischen
   Readout aus der Ledgerdifferenz;
7. N07: jede spaeter registrierte Feldtrennung muss bei angeglichenem oder
   abgetragenem H bestehen bleiben.

## Gegenbaselines

- Fixed Adapter/Frozen-E1 besitzt keinen direkten refraktaer-zu-frei-Transfer.
- Leaky/Integrator darf keine direkte lokale Freigabe und B-Zulassung durch
  getragenen Feldzustand ersetzen.
- Dynamisches zweistufiges E1 kann Freigabe und Wiederverwendung ebenfalls
  zeigen. S1-IL allein grenzt DTS-1 deshalb nicht davon ab; der direkte
  Frei/Refraktaer-Eingriff aus S1-IB bleibt gemeinsam erforderlich.
- F3/CONST-V besitzt ohne das lokale Dreirollenledger keinen entsprechenden
  direkten Transferrecord.
- Schneller Nachhall kann bei H-Angleichung weder Recovery noch zusaetzliche
  B-Bindung erzeugen.

Keine Baseline wird in S1-IL ausgefuehrt oder armweise angepasst.

## STOPP und Aussagegrenze

Jede ungleiche Voranatomie, Zeit, Turnoverrate, Ereignisgrenze oder B-Probe
ergibt STOPP. Das gilt ebenso, wenn Recovery nicht positiv ist, freie
Ressource nicht steigt, B-Bindung nicht zunimmt, eine Bilanz verletzt wird,
ein Ergebnis nachtraeglich Fixture oder Richtung veraendert oder ein Feldwert
als Ersatz fuer direkte Ledger verwendet wird.

S1-IL beweist weder Freigabe noch Wiederverwendung. Selbst ein spaeterer PASS
waere allein kein Abgrenzungsbefund gegen dynamisches E1 und kein Material-,
Runtime- oder weitergehender Faehigkeitsbefund. Memory bleibt eine offene
Forschungsrichtung; KI, Lernen, Vergessen, Semantik, innerer Kontext,
Organisation und Selbstregulation werden nicht behauptet.

## Technische Bindung

```text
mcm_field_organism/dynamic_substrate_s1il_release_reuse_contract.py
tests/test_dynamic_substrate_s1il_release_reuse_contract.py
```

Neun Tests pruefen Quellenbindung, Geometrie, Recoveryintervention, direkte
Ledgertrennung, sieben Kontrollen, alle Gegenbaselines, Fail-Closed-Verhalten,
Ausfuehrungssperren und Manipulationsschutz.

## Bester naechster Schritt

S1-IM darf ausschliesslich ein endliches synthetisches Fixture und den
Ausfuehrungsvertrag fuer S1-IL binden. Kapazitaeten, gemeinsame
Ausgangsanatomie, Belastungsbildung, kontaktfreie Dauer, Raten,
nichtsaturierende B-Probe, direkte analytische Ledgerwerte, Rundungsgrenze,
Fallmatrix und maximales technisches Aufrufbudget muessen vor jeder
Harnessimplementierung feststehen. Noch keine Runtime oder Ausfuehrung.
