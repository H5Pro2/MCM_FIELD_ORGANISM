# S1-EC72: Quellgebundener korrigierter Gesamtpreflight

## Zweck

S1-EC72 verbindet den technischen EC68-Preflight mit dem neuen
EC71-Quellintegritaetspreflight. Damit reicht ein stabiler historischer
Audit-Digest nicht mehr aus: EC64-Konverter, EC65-Aufrufadapter und
EC67-Realmodus-Koordinator muessen zusaetzlich exakt den vorregistrierten
Quellstaenden entsprechen.

## Pflichtgates

- EC68 technisch bereit;
- EC68 enthaelt keine Besitzerfreigabe und haelt den Realpfad gesperrt;
- EC71-Preflight-Digest exakt;
- alle drei registrierten Implementierungsquellen exakt;
- Last exakt 1.608 Bildungs-, 1.600 Probe- und 3.208 Gesamtschritte;
- Ressourcen- und Schutzartefakt-Digests gebunden;
- Laufzeitgrenze 900 Sekunden;
- in-memory, kein Retry, keine Persistenz, Entscheidung oder Claims;
- keine neue Besitzerfreigabe im Preflight.

EC72 besitzt keinen Freigabeparameter und ruft weder Koordinator, Adapter,
Wrapper noch Feldkern auf.

## Abnahme

Vier eigene fokussierte Tests bestehen:

1. EC68 und EC71 exakt: technisch bereit, Realpfad weiterhin gesperrt.
2. Einzelmutation der EC65-Quelle: Gesamtbereitschaft fail-closed gesperrt.
3. Zu wenig Arbeitsspeicher in EC68: Gesamtbereitschaft gesperrt.
4. Keine Freigabeschnittstelle, Realpfadaufrufe oder Schreiboperationen.

Die kontrollierte Referenzfixture liefert den EC72-Digest:

`e55fcd85cc52627c2df02dd31adaed518f6a7f97a4fc680d34fa9749d694bac7`

## Aktueller statischer Snapshot

Zum aktuellen Pruefzeitpunkt wurden ohne Feld- oder Realpfadausfuehrung
gemessen:

- freier Arbeitsspeicher: `6.859.038.720` Byte;
- freier Datentraeger: `234.970.382.336` Byte;
- aktueller EC68-Digest:
  `e2f9585d48b1ddd0ca9c9084a49e9568178729fb0adad32b7ed97bcc73098537`;
- aktueller EC72-Digest:
  `b2d9c1e3c6559babc1e01a67c74ccd4afdc0838df3a6635bf01fbfabdaf83e9c`.

Entscheidung:

`TECHNISCH_BEREIT_QUELLGEBUNDEN_NEUE_EINMALLAUFFREIGABE_FEHLT`

Der aktuelle Digest ist wegen des Ressourcen-Snapshots zeitabhaengig. Er ist
keine dauerhafte Freigabe und muss vor einer spaeter autorisierten Ausfuehrung
erneut gebildet werden.

## Aussagegrenze

EC72 belegt die technische und kryptografische Vorbereitung der korrigierten
Kette. Es belegt weder die Ursache des EC69-Teilabbruchs noch Fehlerfreiheit,
Memory, Feldzeit, Organisation oder KI.

**STOPP fuer reale Ausfuehrung bleibt bestehen.** Die EC69-Freigabe ist
verbraucht. Ein allgemeines `ok weiter` ist keine neue Einmallauffreigabe.

Am besten geht es mit S1-EC73 weiter: einen statischen Einmallaufvertrag fuer
einen diagnostischen n2/r2-Retry formulieren. Er muss EC72, exakt 3.208
Maximalschritte, Abbruch am ersten benannten EC70-Gate, keine Wiederholung und
eine danach getrennt einzuholende ausdrueckliche Besitzerfreigabe binden.
