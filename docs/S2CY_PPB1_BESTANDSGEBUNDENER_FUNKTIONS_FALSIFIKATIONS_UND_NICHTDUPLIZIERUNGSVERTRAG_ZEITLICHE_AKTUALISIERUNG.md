# S2-CY: Bestandsgebundener Vertrag zur zeitlichen Aktualisierung

## Gegenstand und statische Grenze

S2-CY bindet die technische Funktion **zeitliche Aktualisierung unter
begrenzter Kapazitaet** an den nachweisbaren Projektbestand. Es wurden keine
Projektmodule importiert, keine Zustands-, Probe-, Baseline- oder
Runnerfunktion ausgefuehrt und kein Code geaendert.

Der Audit vor der Vertragsbindung zeigt, dass diese Funktion keine neue
Forschungsfrage ist. Sie wurde bereits in S1-XU vertraglich definiert, ueber
S1-XV bis S1-XZ eindeutig materialisiert, in S1-YB synthetisch ausgefuehrt,
in S1-YC statisch abgeschlossen und in S1-YE gegen die staerkste
gleichartige Engineeringbaseline eingeordnet.

S2-CY ersetzt oder wiederholt diese Artefakte nicht. Es bindet ihre
Fortgeltung und verhindert, dass derselbe Mechanismus unter einer neuen
Bezeichnung erneut implementiert oder als neuer Befund interpretiert wird.

## Fortgeltender Funktionsumfang

Der gueltige technische Funktionsumfang bleibt:

1. wiederholte Bestaetigung eines vorhandenen Wahrnehmungszustands;
2. graduelle Veraenderung ueber eine geordnete Eingabefolge;
3. vorab gebundene Behandlung widerspruechlicher Eingaben;
4. Kapazitaetsdruck mit deterministischer Verdraengung;
5. spaeterer read-only Abruf nach der Aktualisierung.

Alle Geschichten beginnen mit getrennten Frischzustaenden. Eingabefolge,
Kapazitaet, Probezahl und Reihenfolge muessen je Vergleichsarm gleich sein.
Beim Abruf sind Rohhistorie, nachtraegliche Zustandsaenderung und Carry aus
anderen Geschichten verboten.

Ein neuer Digest, Supportzaehler, Slot oder Zustandswechsel ist allein kein
Funktionsbefund. Bewertet werden ausschliesslich vorab gebundene
Erkennungsentscheidungen, Distanzen, Konfliktrollen, Opferrollen,
Kapazitaetseinhaltung und unveraenderliche read-only Proben.

## Baselineordnung

Die geforderten Vergleichsarme bleiben als Diagnose gebunden:

| Baseline | Rolle |
|---|---|
| No-Memory | Nullgrenze ohne fortgesetzten Zustand |
| Replay | diagnostische Obergrenze mit offengelegtem groesserem Historienbudget |
| statische Prototypbank | Minimalvergleich ohne Aktualisierung nach Bildung |
| Nachhall | kurzfristige fortlaufende Restzustandsbaseline |
| gleitende Statistik | einfache laufende Verdichtungsbaseline |

Diese Arme koennen technische Mindestleistungen und Informationsasymmetrien
zeigen. Sie sind jedoch nicht die staerkste Gegenbaseline fuer eine Funktion,
deren Definition bereits Online-Aktualisierung, Konfliktbehandlung und
Verdraengung enthaelt.

Zwingende staerkste Baseline bleibt deshalb `AOPB-1`, eine
kapazitaetsgleiche adaptive Online-Prototypbank mit derselben Eingabe-,
Zustands-, Update-, Verdraengungs- und Probeoberflaeche.

## Bereits gebundener Ergebnisstand

S1-YB bestaetigte die technische Funktion synthetisch gegen die statische
Prototypbank:

- zehn getrennte Geschichten fuer zwei Modalitaeten;
- 32 gepaarte Probevergleiche;
- 14 strikte Vorteile, 14 Gleichstaende und vier vorab erwartete
  diagnostische Verluste;
- zehn erfuellte Pflichtvorteile und zehn sichere Negativkontrollen;
- Entscheidung
  `TEMPORAL_UPDATE_SYNTHETIC_FUNCTION_VALID_AGAINST_STATIC_PROTOTYPE`.

S1-YE stellte danach statisch fest, dass PPB-1 im beobachtbaren Umfang selbst
eine adaptive Online-Prototypbank mit zusaetzlichen Audit- und
Fail-Closed-Huellen ist. Bei gleichen Regeln waeren PPB-1 und AOPB-1
konstruktiv verhaltensgleich. Andere Regeln wuerden lediglich eine andere
Engineeringregel vergleichen, keine eigenstaendige Ursache.

## Falsifikation und Stoppbedingungen

Eine neue Ausfuehrung waere methodisch nur zulaessig, wenn vorab eine
Gegenprognose benannt wird, die:

1. nicht bereits durch den S1-XU-H1-bis-H5-Umfang erfasst ist;
2. bei identischem Informations-, Kapazitaets- und Probebudget gilt;
3. von einer adaptiven Online-Prototypbank nicht reproduziert wird;
4. nicht allein aus einer geaenderten Update-, Ablauf-, Match- oder
   Verdraengungsregel entsteht;
5. einen vorab entscheidbaren Verhaltensunterschied besitzt.

Keine solche Gegenprognose liegt fuer den hier gebundenen Funktionsumfang
vor. Deshalb greift die Stoppbedingung unmittelbar:

`STOP_DUPLICATE_TEMPORAL_UPDATE_FUNCTION_ALREADY_VALIDATED_AND_AOPB_REDUCIBLE`

Der im Auftrag vorgesehene anschliessende Implementierungs- und
Ausfuehrungsschritt wird nicht freigegeben. Eine Wiederholung gegen nur die
schwaecheren Baselines wuerde den bestehenden Engineeringbefund bestaetigen,
aber keine neue Information erzeugen.

## Claim- und Integrationsgrenze

PPB-1 bleibt als private, begrenzte und MCM-kompatible
Wahrnehmungszustandskomponente erhalten. S2-CY belegt keine
MCM-spezifische Memory-Mechanik, keine Feldwirkung und keine semantische
Funktion. Oeffentliche API, Snapshot, Produktion, Live-Sensorik und
Feldintegration bleiben ausgeschlossen.

## Naechste Richtungsentscheidung

Eine weitere technische Entwicklung benoetigt genau eine neue Funktion mit
einer nicht durch die adaptive Online-Prototypfamilie erklaerten
Gegenprognose. Diese Auswahl ist nicht Bestandteil von S2-CY und erfordert
eine neue ausdrueckliche fachliche Richtungsentscheidung.
