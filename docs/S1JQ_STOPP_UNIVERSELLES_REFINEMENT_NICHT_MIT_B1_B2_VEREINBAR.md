# S1-JQ: STOPP universelles Refinement nicht mit B1/B2 vereinbar

## Ergebnis

S1-JQ stoppt die in S1-JP freigegebene Adapterimplementierung vor dem ersten
Adaptercode. Die fuer alle sechs Rollen gebundene Zerlegung eines physischen
Intervalls in 2, 4 oder 8 positive Unterfenster ist mit den bestehenden B1-
und B2-Kernoberflaechen und dem S1-JK-Takt nicht vereinbar.

## Gebundene Zeitgrenze

Jedes S1-JK-Intervall umfasst genau einen ganzzahligen Tick. Ein
`MCMFieldStepTime` akzeptiert nur ganzzahlige Start- und Endticks und verlangt
`Ende > Start`. Zwei, vier oder acht zusammenhaengende positive
Ganzzahlfenster benoetigen mindestens ebenso viele Ticks.

Eine feinere private Uhr, eine veraenderte Tickrate oder nachtraeglich
umgeschriebene Abschlussmetadaten wuerden die gemeinsame Exposition und die
korrigierte Carry-Zeitprovenienz veraendern. Bruchteilsticks sind ungueltig.

## Kernklassifikation

- B1 integriert das feste Spektrum exakt ueber eine Dauer und schliesst danach
  genau einen atomaren `field.advance` mit dem vollstaendigen Zeitfenster ab.
  Die Funktion besitzt keinen Refinementparameter.
- B2 `model-b2` verwendet eine analytische Matrixexponentialfunktion ueber
  genau eine positive Dauer. Die Funktion besitzt ebenfalls keinen
  Refinementparameter und liefert keinen vollstaendigen Feldabschluss.
- B3 bis B6 verwenden die bestehende F3-Runtime, deren eigener positiver
  ganzzahliger Refinementparameter die Werte 2, 4 und 8 direkt aufnehmen kann.

Ein Wiederholen von B1 mit demselben Vollfenster waere nicht monoton und
wuerde den Kontakt erneut anwenden. Ein stilles Ignorieren der Stufe bei B1
oder B2 widerspraeche dem S1-JP-Unterfenstervertrag. Eine Neuimplementierung
der Kerne oder Gleichungen ist nicht zulaessig.

## Umfang des STOPPs

B1 und B2 sind in je vier Profilbloecken betroffen, also acht der 24
Baseline-Rollen-Block-Faelle. Da der spaetere Vergleich atomar alle sechs
Baselines verlangt, bleiben alle 24 Faelle blockiert.

Erhalten bleiben:

- alle 23 S1-JK-Envelopefixtures, Zeiten, Identitaeten und Digests,
- der reine S1-JO-Materializer,
- alle sieben S1-JA-Konfigurationen und 24 Fallidentitaeten,
- die nicht zeitabhaengigen Informations-, Zustandsrueckgabe-, Neutral- und
  Fail-Closed-Regeln aus S1-JP,
- alle bestehenden Baselinekerne unveraendert.

## Entscheidung

`STOPP_S1JP_UNIVERSAL_REFINEMENT_PARTITION_INCOMPATIBLE_WITH_ONE_TICK_B1_B2_KERNELS`

Kanonischer Auditdigest:

`9111d1f5814f96f72d995df1eccc7e5163629f515c9c18566e9dceaf904735f5`

Es wurden keine Adapter konstruiert, keine Baselinekerne aufgerufen und null
technische oder forschungsbezogene Feldschritte ausgefuehrt. Ein
Baselineergebnis oder weitergehender Claim folgt daraus nicht.

## Naechster zulaessiger Schritt

S1-JR darf ausschliesslich einen korrigierten rollenspezifischen
Refinementvertrag binden. Fuer die analytisch exakten B1-/B2-Kerne ist zu
pruefen, ob ein unveraendertes Vollintervall mit vorregistrierter bitgleicher
r2/r4/r8-Kontrollerwartung methodisch zulaessig ist; andernfalls bleiben sie
gestoppt. B3 bis B6 behalten natives Refinement. Noch keine Implementierung,
kein Modellaufruf, keine Runtime oder Forschungsprobe.
