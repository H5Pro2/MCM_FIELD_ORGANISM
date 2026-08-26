# S2-BJ: AVPC-1 Materialisierbarkeitsaudit

## Ergebnis

Sechs von sieben Materialisierungsrollen sind technisch darstellbar. AVPC-1
bleibt als Funktion bestehen. Ein enger Eingabeblocker verhindert jedoch
noch jede Implementierung.

## Inhaltsbildung

Die vorhandenen Profilgrenzen tragen mindestens acht auditive und vier
visuelle Prototypen. AVPC-1 benoetigt jeweils nur zwei. Zwei konstante
Rollenvektoren mit Komponenten `-0.5` und `0.5` liegen im zulaessigen Bereich
und sind mit Distanz `1.0` weiter getrennt als jede erlaubte Matchschwelle.

Beide Rollen koennen jeweils bis `stable_after` wiederholt werden, bevor die
kleinste vorhandene Ablaufgrenze erreicht wird. Deshalb koennen beide
Geschichten mit exakt denselben stabilisierten Bankzustaenden beginnen.
Diese Werte sind nur ein statischer Existenznachweis und noch keine
registrierte Fixture.

## Gekreuzte Fenster

Eine endliche Konstruktion mit vier nicht ueberlappenden Feldfenstern ist
moeglich:

```text
Audio:   A_KEY, B_CONTROL, A_KEY, B_CONTROL
H_LEFT:  V_LEFT, V_RIGHT, V_LEFT, V_RIGHT
H_RIGHT: V_RIGHT, V_LEFT, V_RIGHT, V_LEFT
```

Audio und Video teilen je Position dasselbe positive Fenster. Verschiedene
Positionen ueberlappen nicht. Jeder Snapshot besitzt damit genau einen
Partner; es gibt keine mehrdeutigen oder unverknuepften Snapshots. Jede
Relation wird zweimal exponiert und beide Geschichten besitzen gleiche
Randinventare und Anzahlen.

Die Inhaltsbanken bleiben waehrenddessen eingefroren und werden nur read-only
abgefragt. Daher kann die gekreuzte visuelle Reihenfolge ihre Zustaende nicht
veraendern.

## Kapazitaet und Baselines

Zwei Relationsplaetze reichen fuer die gekreuzte Kernfunktion. Eine
verkettete gemeinsame Prototypbank und eine heteroassoziative Tabelle koennen
mit derselben Kapazitaet und denselben vier Ueberlappungsbelegen aufgebaut
werden. Replay bleibt eine Kontrolle mit groesserem Informationsbudget.

Die konkrete Kapazitaet, Bestaetigungsregel und Vollbelegungsregel werden in
diesem Audit noch nicht registriert.

## Offener Blocker

Die spaetere AVPC-1-Probe muss exakt einen auditiven Frame und keinen
visuellen Frame enthalten. Die vorhandene aktive Batch-Huelle erzwingt jedoch
immer genau zwei nicht leere Sequenzen in der Reihenfolge Audio, Video. Ein
leerer, neutraler oder kuenstlicher visueller Frame waere methodisch keine
ehrliche Abwesenheit visueller Eingabe.

Ein ungebundener einzelner Audioframe reicht ebenfalls nicht, weil dann
Quellvertrag, Profil, Konfiguration und Feldzeit nicht vollstaendig gebunden
waeren.

Erforderlich ist deshalb eine neue rein private Audio-only-Probenhuele. Sie
muss genau einen quell-, profil-, konfigurations- und feldzeitgebundenen
auditiven Frame tragen und die visuelle Eingabeanzahl explizit auf null
binden. Sie darf die bestehende audiovisuelle Batch-Huelle nicht veraendern.

## Naechster Schritt

S2-BK definiert ausschliesslich den statischen Funktions-, Provenienz- und
Fail-Closed-Vertrag dieser privaten Audio-only-Probenhuele. Implementierung,
AVPC-1-Relationsmechanik, Fixture und Ausfuehrung bleiben gesperrt.
