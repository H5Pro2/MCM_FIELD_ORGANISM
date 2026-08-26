# W7-AN: Privater stufenweiser Aufloesungsexecutor

## Entscheidung

`W7AN_PRIVATE_SIX_PHASE_RESOLUTION_EXECUTOR_IMPLEMENTED_R1_PASSED`

Ein privater In-Memory-Executor verbindet die sechs vorhandenen W7-AN-
Phasengrenzen fuer genau eine Aufloesungsrolle. Pro `advance()`-Aufruf wird
hoechstens eine Phase ausgefuehrt.

## Abhaengigkeitsgerechte Reihenfolge

Die statische Reihenfolge wurde korrigiert, weil eine Messmaterialisierung
erst ein vollstaendig auditiertes CAP-Ergebnis konsumieren kann:

```text
1. 67 CAP-Materialisierungen
2. 67 CAP-Pfadreihenfolgekontrollen
3.  4 CAP-Branchreihenfolgekontrollen und CAP-Finalisierung
4. 35 Messmaterialisierungen
5. 35 Messreihenfolgekontrollen
6.  1 Observerpassivitaetskontrolle und Aufloesungsfinalisierung
```

Die Gesamtzahl 209 pro Aufloesung bleibt unveraendert.

## Zustands- und Fehlervertrag

Der Executor haelt Materialisierungen, Auditobjekte, Zeugen und Resultate nur
im Arbeitsspeicher. Bei einem Fehler wird kein Phasenbeleg erzeugt und der
Phasenzaehler nicht erhoeht. Ein erneuter Aufruf beginnt dieselbe Phase neu.

Jede abgeschlossene Phase liefert einen digestgebundenen In-Memory-Beleg mit
Rolle, Refinement, Phasenkennung und Integrationsinventar. Dieser Beleg ist
kein Forschungsreport und wird nicht persistiert.

Vor Phase sechs ist `resolution_result` leer. Erst nach 67 Produktions- und
35 Messzeugen sowie allen vier Auditbatches wird ein
`W7ANResolutionResult` erzeugt. Eine siebte Ausfuehrung wird verworfen.

## Gemeinsame Finalisierung

Der gestufte und der bestehende oeffentliche W7-AE-Pfad verwenden denselben
privaten CAP-Finalizer. Dadurch bleiben Eingangspassivitaet,
Anfangsfelddigest, P0-/Observerbindung und bisherige Digestkomposition an
einer Stelle gebunden.

## Technische Pruefung

Der schnelle W7-AN-Strukturverbund besteht:

```text
24 tests, OK
```

Die Tests pruefen sechs getrennte Fortschritte, exakte Inventare
67/67/4/35/35/1, fehlende vorzeitige Ergebnisfreigabe, Fehlerstabilitaet,
Zeugenpflicht, Rollenvalidierung und fehlende oeffentliche Exporte. Die
Phasenergebnisse wurden injiziert. Anschliessend wurde der Executor genau
einmal real fuer R1 ausgefuehrt und reproduzierte die kanonischen W7-AE-,
W7-AG- und W7-AK-Digests mit 67+35 Zeugen.

## Grenzen

- R2 und R4 wurden nicht vollstaendig ausgefuehrt.
- Es gibt noch keinen R1/R2/R4-Koordinator und keinen Gegenlauf in
  umgekehrter Rollenfolge.
- Kein Gesamtcontainerdigest und kein 306-Zeugen-Nachweis liegt vor.
- Kein Browser, Report oder Forschungslauf wurde gestartet.
- Daraus folgt kein Funktions-, Memory-, Feldzeit-, Organisations- oder
  KI-Befund.

## Bester naechster Schritt

Der private R1/R2/R4-Koordinator ist inzwischen statisch gebunden. Offen ist
sein reiner globaler Containerfinalizer aus drei vollstaendigen
Primaerresultaten; vor dessen Bindung wird R2 nicht ausgefuehrt.
