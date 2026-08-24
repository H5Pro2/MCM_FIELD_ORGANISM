# S2-BO: Begrenzter AVPC-1-Relationszustand

## Ergebnis

Der Relationszustand ist statisch festgelegt: zwei Schluesselplaetze, zwei
unabhaengige Belege pro stabiler Relation und hoechstens vier akzeptierte
zustandsaendernde Expositionsbelege. Implementiert wurde nichts.

## Zustand und Kapazitaet

Ein Slot ist `FREE`, `PENDING`, `STABLE` oder `CONFLICTED`. Ein neuer
Schluessel wird im ersten freien Slot vorgemerkt. Der zweite unabhaengige
Beleg desselben Paars stabilisiert ihn. Weitere gleiche Belege werden ohne
Zustandsaenderung abgewiesen.

Sind beide Slots belegt, wird ein neuer Schluessel atomar verworfen. Es gibt
keine Ersetzung oder Verdraengung.

## Konflikt

Wird derselbe auditive Schluessel mit einem anderen visuellen Ziel belegt,
wird sein vorhandener Slot konfliktbehaftet. Er besitzt danach kein
ausgabefaehiges Ziel. Dieser Zustand ist dauerhaft; Mehrheitswahl, Reparatur
oder spaetere Bestaetigung sind ausgeschlossen.

## Provenienz und Probe

Ein Beleg benoetigt zwei erfolgreiche read-only Prototypbefunde und eine
positive, eindeutige Eins-zu-eins-Ueberlappung auf derselben Felduhr.
Rohwerte und externe Paar-IDs werden nicht gespeichert.

Die spaetere Probe verwendet genau die private Audio-only-Huelle. Ein
stabiler Schluessel liefert eine visuelle Prototypidentitaet. Unbekannte oder
vorgemerkte Schluessel liefern `NO_MATCH`, Konflikte `NO_MATCH_CONFLICT`.
Relation und Inhaltsbanken bleiben unveraendert.

## Baselinegrenze

Die staerkste Gegenbaseline ist eine kapazitaetsgleiche heteroassoziative
Tabelle mit denselben Support-, Konflikt- und Vollbelegungsregeln. Erklaert
sie AVPC-1, bleibt die Funktion eine generische MCM-kompatible
Engineeringkomponente und keine eigene Feldursache.

## Naechster Schritt

S2-BP prueft statisch Typwiederverwendung, Uebergangsvollstaendigkeit,
Baselinegleichheit und die synthetische Testgrenze. Implementierung und
Ausfuehrung bleiben bis dahin gesperrt.
