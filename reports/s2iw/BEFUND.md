# S2-IW Befund

Der statische Audit bindet die beiden S2-IV-Abweichungen an einen exakt
lokalisierten numerischen Effekt: Der stabile P1-B-Prototyp weicht auf den
sichtbaren Hochwertpositionen um `2` ULP vom Rezeptorwert ab. Das entspricht
nur `5.6621374255882984e-14` einer `1/255`-Rezeptorstufe.

Die Kontrollen `c07` und `c08` unterscheiden sich dagegen um genau eine volle
Rezeptorstufe. `c02` und `c03` bleiben wegen ihrer binaer exakt darstellbaren
sichtbaren Werte ohne Rundungsrest.

Eine uint8-gittergebundene Diagnose trennt diese konkreten Klassen. Die
vorhandenen L1-Schwellen tun dies nicht. S2-IW waehlt deshalb keine neue
Regel, aendert keinen Code und laesst die gueltige S2-IV-Falsifikation
unveraendert.

Status:

`PASS_S2IW_STATIC_POST_FALSIFICATION_NUMERIC_AUDIT_NO_RULE_SELECTED`
