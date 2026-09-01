# S2-IX Vertragsbefund

S2-IX bindet eine prospektive Gleichheitsregel fuer sichtbare visuelle
Kontextwerte. Entscheidend ist nicht die Naehe zweier Floats, sondern die
belegte Identitaet ihrer `uint8`-Rezeptorgittercodes.

Ein PPB-Prototyp ist nur zulaessig, wenn seine positionsweise Formationslinie
vollstaendig und homogen ist. Gemischte oder nicht belegte Linien stoppen
fail-closed. Maskierte Werte, Memory-Kerne und bestehende L1-Schwellen bleiben
unveraendert.

Die unabhaengige prospektive Domain umfasst alle 256 Gitterwerte, sieben
Wiederholungsgrenzen, 510 gerichtete Ein-Stufen-Vergleiche und 510 gemischte
Linien: insgesamt 2812 Primaerzellen. Noch wurde nichts implementiert oder
ausgefuehrt.

Status:

`STATIC_UINT8_RECEPTOR_GRID_EQUIVALENCE_CONTRACT_BOUND`
