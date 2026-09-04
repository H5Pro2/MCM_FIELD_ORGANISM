# S2-LR Rezeptor- und Geometriematerialisierung 20260904-01

Materialisierungs-ID:
`s2lr-receptor-geometry-materialization-20260904-01`

Status: `S2LR_VARIATION_GEOMETRY_NOT_MATERIALIZABLE`

Die einmalige Materialisierung wurde im vorgeschalteten statischen
Konsistenzgate vor dem ersten Rezeptoraufruf fail-closed beendet. Ursache ist
eine fixtureunabhaengige Unvereinbarkeit zwischen drei gebundenen visuellen
Faellen und der qualifizierten S2-KQ-Scanregel.

S2-KQ verwendet fuer jeden visuellen Teilhinweis dieselben beobachteten
Positionen `0...31`. Ein Kandidat trifft nur, wenn alle 32 Werte exakt mit dem
Teilhinweis uebereinstimmen.

Damit gelten logisch:

1. q01 als eindeutiger F-Treffer verlangt, dass F auf den beobachteten
   Positionen mit q01 uebereinstimmt und G nicht.
2. q03 als eindeutiger G-Treffer verlangt die umgekehrte Beziehung.
3. q09 als gleichzeitiger F/G-Treffer verlangt auf denselben Positionen
   `F = q09 = G`.

Punkt 3 widerspricht den Eindeutigkeitsbedingungen aus Punkt 1 und 2. Keine
RGB-Fixture kann alle drei Beziehungen unter derselben festen Maske und der
exakten S2-KQ-Gleichheitsregel gleichzeitig erfuellen. Dieser Widerspruch ist
unabhaengig von Pixelwerten, Rezeptorausgabe oder Schwellenabstand.

Deshalb wurden keine RGB-/PCM-Fixtures erzeugt oder gesucht. Es gab exakt
null Rezeptor-, Memory-, Feld- und Kontextaufrufe sowie keine
Parameteranpassung. S2-LQ und alle bestehenden qualifizierten Komponenten
bleiben unveraendert.

Eine spaetere Korrektur muss entweder q09 als andere real erreichbare
Mehrdeutigkeit binden oder fuer den Konfliktfall eine getrennte, vorab
qualifizierte Maskenrolle einfuehren. Beides ist eine prospektive
Vertragsentscheidung und darf nicht in diesen abgeschlossenen Befund
eingearbeitet werden.
