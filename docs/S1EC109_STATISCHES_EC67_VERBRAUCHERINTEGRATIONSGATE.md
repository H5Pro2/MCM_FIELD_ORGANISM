# S1-EC109: Statisches EC67-Verbraucherintegrationsgate

## Befund

Die EC108-Rueckgabehuelle kann EC67 nicht isoliert ersetzen. Drei direkte
Laufzeitverbraucher erwarten weiterhin das nackte
`E1CommonProbeN2R2RealModeCoordinatorResult`:

- EC82 reduziert dessen Proben zu EC80-Skalaren;
- EC84 bindet Resultat und Skalarquittung;
- EC102 extrahiert die r2-Proben fuer den Gesamtvektorpfad.

Daneben erwarten EC101, die Provenienz-Audits und mehrere synthetische Fixtures
noch die bisherige Rueckgabeform.

## Migrationsgrenze

Zuerst muss ein Besitzer-Scope-Token ohne Ausfuehrungsfreigabe implementiert
werden. Danach folgt die atomare EC67-Rueckgabe. Erst anschließend duerfen
EC82, EC84 und EC102 in dieser Reihenfolge auf die Huelle migriert werden.
Statische Audits und Fixtures werden zuletzt angepasst und gemeinsam
regressionsgeprueft.

Kein Verbraucher darf die Huelle ungeprueft zu `.result` entpacken. Er muss
zuerst Tokenverbrauch, Quittungsbindung, Huellendigest und Scope validieren.

## Status

`EC108_EC67_CONSUMER_MIGRATION_MAPPED_INTEGRATION_CLOSED`

EC109 veraendert weder Produzent noch Verbraucher. Es fuehrt nichts aus,
persistiert nichts und oeffnet den Realresultat-Einlass nicht.

## Bester naechster Schritt

Am besten geht es mit S1-EC110 weiter: einen Besitzer-Scope-Tokenvertrag und
eine sichere Factory implementieren, die ohne neue ausdrueckliche Besitzer-
Lauffreigabe keinen Token erzeugen kann. Noch keine EC67-Integration oder
Ausfuehrung.
