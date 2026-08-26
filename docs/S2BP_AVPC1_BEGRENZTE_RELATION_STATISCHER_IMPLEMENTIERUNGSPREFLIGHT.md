# S2-BP: AVPC-1-Relationspreflight

## Ergebnis

Der begrenzte Relationskern ist ohne offenen Implementierungsblocker
materialisierbar. Neun von neun Rollen sind eindeutig. Es wurde kein Code
implementiert und keine Funktion ausgefuehrt.

## Prototypidentitaet

Der Vertrag verwendet ausschliesslich Prototypdigests als Schluessel und
Ziele. Deshalb muessen stabilisierte Prototypdigests innerhalb jeder
eingefrorenen Modalitaetsbank eindeutig sein. Doppelte stabilisierte Digests
verwerfen die Relationsinitialisierung fail-closed. Die gekreuzte Fixture
erfuellt diese Bedingung durch ihre getrennten Rollenvektoren.

## Generischer Kern und Baseline

AVPC-1 und die staerkste heteroassoziative Baseline sollen denselben
generischen Uebergangskern verwenden. Ihre Zustandsinstanzen und Tabellen-IDs
sind getrennt, ihre Kapazitaet, Supportgrenze, Expositionsbudgets sowie
Konflikt- und Vollbelegungsregeln bleiben identisch.

Damit kann kein scheinbarer Vorteil durch unterschiedlich programmierten
Kandidaten- und Baselinecode entstehen. Stimmen beide funktional ueberein,
bleibt AVPC-1 eine generische MCM-kompatible Engineeringkomponente.

## Vollstaendigkeit

Die neun priorisierten Uebergangsfaelle sind disjunkt und vollstaendig:
ungueltig, doppelt, Budget erschoepft, Konflikt gesperrt, Bestaetigung,
Support gesaettigt, neuer Konflikt, Kapazitaet voll und neuer freier Slot.

Die spaetere read-only Abfrage prueft unbekannte, vorgemerkte, stabile und
konfliktbehaftete Schluessel. Ein stabiles visuelles Ziel muss weiterhin
eindeutig in der eingefrorenen visuellen Bank existieren.

## Testgrenze

Spaetere synthetische Tests duerfen die bestehende reine Zeitausrichtung und
read-only PPB-Probe zur Erzeugung echter typisierter Belege verwenden. Eine
PPB-Bankfortschreibung, Feld-, Produktions- oder Liveausfuehrung bleibt
ausgeschlossen.

## Naechster Schritt

S2-BQ darf nach gesonderter Fortsetzung nur den privaten generischen
Relationskern, seine Receipts, Uebergaenge, read-only Abfrage und die
budgetgleiche synthetische Baselinepruefung implementieren.
