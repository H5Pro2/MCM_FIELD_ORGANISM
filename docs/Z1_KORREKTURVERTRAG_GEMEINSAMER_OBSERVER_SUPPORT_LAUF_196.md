# Z1: Korrekturvertrag gemeinsamer Observer-Support fuer Lauf 196

Stand: 2026-08-06

> **Aktueller Status:** Die Supportprojektion ist
> [implementiert und synthetisch geprueft](Z1_GEMEINSAMER_OBSERVER_SUPPORT_IMPLEMENTIERUNG.md).
> Der [Lauf-196-Einstieg](Z1_LAUF196_EINSTIEG_UND_AUSFUEHRUNGSSPERRE.md)
> wurde inzwischen genau einmal real ausgefuehrt. Das Ergebnis ist in
> [Lauf 196](forschung/LAUF_196_Z1_GEMEINSAMER_SUPPORT_FELDTRAJEKTORIEN.md)
> dokumentiert.

## Anlass

[Lauf 195](forschung/LAUF_195_Z1_FELDTRAJEKTORIEN_KOVARIANZAUDIT.md)
ist `TECHNICALLY_UNDECIDABLE`, weil `A.partitioned` nicht nur die technischen
Integrationsgrenzen, sondern zugleich die Stuetzpunktdichte der polygonalen
Sachpfadmetrik verdoppelte.

Der Vertrag korrigiert ausschliesslich diese Vermischung. Er veraendert
keinen Forschungsbefund, da Lauf 195 keine Sachentscheidung freigegeben hat.

## Unveraendert gebunden

- alle sieben Quellen- und Ausfuehrungsdigests;
- F3-Kandidat und lineare gekoppelte B3-Baseline;
- neutraler gemeinsamer Start-Layer;
- n, 2n, 4n und unabhaengige 4n-Reproduktion;
- vollstaendige technische Integration jedes Arms;
- alle Massen-, Werte-, Handoff- und Konvergenzkontrollen;
- normierte kumulative Pfadlaenge und 101-Punkte-Raster;
- numerische Huellen und 5-Prozent-Grenzen;
- Teilungsstopp, Zeit-, Ordnungs- und B3-Entscheidungslogik;
- Claim- und Testweltgrenzen.

## Einzige zulaessige Korrektur

Der Runtimeobserver erfasst weiterhin jeden technischen Integrationsabschluss.
Vor der Sachpfadmetrik wird daraus deterministisch eine Entscheidungstrajektorie
gebildet, die nur enthaelt:

1. den neutralen Startpunkt des Arms und
2. jeden Tick, an dem mindestens ein reales reduziertes Rezeptorereignis
   abgeschlossen wurde.

Leere Zwischenabschluesse aus `A.partitioned` bleiben in der technischen
Diagnose, gehen aber nicht als zusaetzliche Polygonstuetzpunkte in die
Sachmetrik ein. Es findet keine Interpolation auf Weltzeit und keine
Ergebnisanpassung statt.

## Pflichtkontrollen

- vollstaendige und Entscheidungstrajektorie werden getrennt gezaehlt;
- Referenz und `A.partitioned` besitzen je 91 Entscheidungsschritte plus den
  gemeinsamen Startpunkt;
- alle 101 reduzierten Ereignisse bleiben genau einmal zugeordnet;
- die vollstaendige 4n-Reproduktion bleibt bitgleich;
- Filterung liest nur die bereits fest gebundenen Abschlussgruppen;
- kein Sachwert beeinflusst die Auswahl eines Stuetzpunkts;
- alle anderen Arme behalten dieselbe Entscheidungstrajektorie wie ihre
  bisherige vollstaendige Abschlussfolge.

## Entscheidungsregel

Erst nach bestandenen Pflichtkontrollen wird die unveraenderte Z1-Auswertung
erneut angewendet. Scheitert `A.partitioned` dann weiterhin gegen die
numerische Huelle, lautet auch Lauf 196 `TECHNICALLY_UNDECIDABLE`; es gibt
keine weitere Beobachterkorrektur.

## Laufgrenze

Implementierung und synthetische beziehungsweise technische Tests erhalten
keine Laufnummer. Die einmalige reale Ausfuehrung des korrigierten, sonst
unveraenderten Vertrags erzeugt Lauf 196.

## Bester naechster Schritt

Den unveraenderten one-shot Lauf-196-Einstieg genau einmal ausfuehren und das
skalare Ergebnis ohne nachtraegliche Aenderung dokumentieren.
