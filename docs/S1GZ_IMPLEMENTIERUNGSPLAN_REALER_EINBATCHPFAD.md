# S1-GZ: Implementierungsplan fuer den realen Einbatchpfad

Stand: 2026-08-15

Status: `IMPLEMENTIERUNGSREIHENFOLGE_GEBUNDEN_AUSFUEHRUNG_GESCHLOSSEN`

## Ziel

S1-GZ trennt die sichere Baufolge der fuenf in S1-GY fehlenden Komponenten
von ihrer spaeteren atomaren Laufreihenfolge. Es wird noch keine Komponente
implementiert und keine Realfreigabe angefragt.

## Implementierungsreihenfolge

1. reiner Real-Transition-Builder;
2. externe Besitzer-Autorisierungs-Origin-Bridge;
3. reale Einmaltoken-Factory;
4. atomare Real-Adapteraufruf-Receipt-Factory;
5. gegateter Real-Einbatch-Adapter.

Der reine Builder steht zuerst, weil er ohne externen Effekt gegen die bereits
gebundenen Transition- und Receipt-Schemata implementiert werden kann. Der
Adapter steht zuletzt und integriert erst dann die getrennt geprueften
Grenzen.

## Spaetere Laufreihenfolge

```text
externe Besitzerautorisierung annehmen und pruefen
-> exaktes S1-GY-Ziel binden
-> genau ein prozesslokales Einmaltoken erzeugen
-> Route und Budget erneut pruefen
-> Token unmittelbar vor dem Adapteraufruf verbrauchen
-> genau ein Adapteraufruf und ein Feldschritt
-> Receipt innerhalb derselben Adaptergrenze versiegeln
-> reine Real-Transition aus Receipt und neuem Feld bilden
-> gemeinsamen Real-Envelope pruefen
-> vollstaendige Transition oder kein Ergebnis zurueckgeben
-> Autorisierung und Token nach Erfolg oder Fehler beenden
```

## Besitzgrenzen

- Nur die Origin-Bridge prueft die externe Herkunft der Besitzerfreigabe.
- Nur die Token-Factory erzeugt nach gueltiger Autorisierung genau ein Token.
- Nur die Adaptergrenze verbraucht das Token, ruft den Kernel auf und
  versiegelt das Receipt.
- Der Transition-Builder besitzt weder Autorisierung noch Token oder
  Kernelzugriff.
- Jeder Fehler beendet den Versuch ohne Teilergebnis.

Entscheidung:

```text
FIVE_COMPONENT_IMPLEMENTATION_ORDER_BOUND_EXECUTION_CLOSED
```

Es wurde nichts autorisiert, implementiert, ausgefuehrt oder persistiert.
Dies ist kein Feld-, Substrat- oder Memory-Befund.

## Bester naechster Schritt

S1-HA implementiert als erste isolierte Komponente nur den reinen
Real-Transition-Builder gegen S1-GU und S1-GV. Er darf keinen Adapter, Token
oder Autorisierungspfad aufrufen und wird ausschliesslich synthetisch getestet.
