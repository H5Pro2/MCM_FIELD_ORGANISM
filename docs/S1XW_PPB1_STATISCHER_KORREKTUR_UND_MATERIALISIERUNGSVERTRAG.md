# S1-XW: Statischer PPB-1-Korrektur- und Materialisierungsvertrag

## Auftrag und Grenze

S1-XW schliesst ausschliesslich die sechs S1-XV-Blocker fuer die in S1-XU
gewaehlte zeitliche Aktualisierung unter begrenzter Kapazitaet. Der Vertrag
verwendet nur vorhandene PPB-1-Konfigurationsrollen, die vorhandene
normalisierte L1-Distanz und konstante synthetische Traegerwerte.

Es werden keine Gleichung, Implementierung, Tests, Fixturefunktion,
Zustandsfunktion, Probe oder Runner eingefuehrt oder ausgefuehrt.

## Gemeinsame Konfiguration

Beide Modalitaeten muessen alle fuenf Geschichten bestehen:

| Rolle | Auditiv | Visuell |
|---|---:|---:|
| Traegerzahl | 12 | 72 |
| Matchschwelle | 0.25 | 0.125 |
| graduell 1 | 0.0625 | 0.03125 |
| graduell 2 | 0.125 | 0.0625 |
| graduell 3 | 0.1875 | 0.09375 |
| Konflikt B | 0.625 | 0.5 |
| Gegenpol C | -0.625 | -0.5 |
| ferne Kontrolle | 1.0 | 1.0 |

Jeder Wert wird auf allen Traegern der jeweiligen Modalitaet wiederholt.
Alle Werte sind binaer exakt und liegen im vorhandenen Wertebereich.

Gemeinsam gebunden sind Kapazitaet `2`, Aktualisierungsrate `0.5`,
Stabilisierung nach `3` Treffern und Ablaufgrenze `8`. Keine Geschichte
erreicht die Ablaufgrenze eines nicht ausgewaehlten Slots.

## Baseline und Vorvergleichslage

PPB-1 und statische Prototypbank verwenden pro Geschichte getrennte frische
Zustaende. Ihre Bildungsphase wird mit derselben vorhandenen PPB-1-
Bildungsregel materialisiert. Erst danach wird die Baseline eingefroren.

Vor der Aktualisierungsphase muessen fuer alle gebundenen Vorproben
Prototypwerte, Erkennungsentscheidungen und Distanzen beider Systeme exakt
gleich sein. Bank-, Slot- und Digestidentitaeten duerfen verschieden sein
und gehoeren nicht zum Funktionsvergleich.

Nach Bildung erhalten beide Systeme weiterhin jedes Expositionsfenster.
Nur PPB-1 darf seinen Zustand gemaess der vorhandenen Aktualisierungsregel
fortschreiben. Die statische Bank bestaetigt den Empfang, veraendert aber
keinen Prototyp.

## Endliche gemeinsame Budgets

Alle Expositionsfenster sind einen Tick lang und streng geordnet. Zwischen
letzter Aktualisierung und erster Probe liegen genau vier Ticks. Die Proben
folgen in der unten gebundenen Reihenfolge in je einem eigenen spaeteren
Fenster. Proben sind read-only.

| Geschichte | Bildung | Aktualisierung | Proben je System und Modalitaet |
|---|---:|---:|---:|
| H1 | 3 | 2 | 2 |
| H2 | 3 | 3 | 4 |
| H3 | 3 | 3 | 3 |
| H4 | 6 | 3 | 4 |
| H5 | 3 | 3 | 3 |
| Summe | 18 | 14 | 16 |

Damit erhaelt jedes System pro Modalitaet `32` Expositionen und `16`
Proben. Ueber zwei Systeme und zwei Modalitaeten sind spaeter hoechstens
`128` Expositionsuebergaben und `64` read-only Proben zulaessig. Es gibt
keinen Retry.

## Vollstaendig materialisierte Geschichten

### H1: Wiederholte Bestaetigung

- Bildung: `0, 0, 0`.
- Aktualisierung: graduell 2 zweimal.
- Proben: graduell 2, Konflikt B.
- Sollrolle: bestehender Slot bleibt derselbe; kein zweiter Slot entsteht.
- Akzeptanz: Ziel bleibt erkannt und seine Distanz wird kleiner als bei der
  statischen Bank; Konflikt B bleibt in beiden Systemen negativ.

### H2: Graduelle Veraenderung

- Bildung: `0, 0, 0`.
- Aktualisierung: graduell 1, graduell 2, graduell 3.
- Proben: `0`, graduell 2, graduell 3, Konflikt B.
- Sollrolle: derselbe Slot wird dreimal fortgesetzt.
- Akzeptanz: graduell 3 bleibt erkannt und liegt in PPB-1 strikt naeher als
  in der statischen Bank; Konflikt B bleibt in beiden Systemen negativ.

Der erwartete terminale PPB-1-Prototyp ist auditiv `0.1328125` und visuell
`0.06640625`. Die Zielabstaende zu graduell 3 sind `0.0546875` und
`0.02734375`; die statischen Zielabstaende sind `0.1875` und `0.09375`.

### H3: Widerspruechliche Wahrnehmung

- Bildung: `0, 0, 0`.
- Aktualisierung: Konflikt B dreimal.
- Proben: `0`, Konflikt B, Gegenpol C.
- Einzige Sollpolitik: **Trennung**.
- Sollrolle: Slot 000 behaelt `0`; Slot 001 bildet und stabilisiert B.
- Akzeptanz: PPB-1 erkennt `0` und B jeweils mit Distanz null. Die statische
  Bank erkennt nur `0`. C bleibt in beiden Systemen negativ.

Aktualisierung oder Verdraengung des alten Slots gelten in H3 als Fehler.

### H4: Kapazitaetsdruck und Verdraengung

- Bildung: `0, 0, 0, B, B, B`; beide Slots sind danach stabil.
- Aktualisierung: Gegenpol C dreimal.
- Proben: B, `0`, C, ferne Kontrolle.
- Einzige Sollpolitik: **deterministische LRU-Verdraengung**.
- Opfer: Slot 000 mit Rolle `0`, zuletzt in Schritt 3 ausgewaehlt.
- Erhalten: Slot 001 mit Rolle B, zuletzt in Schritt 6 ausgewaehlt.
- Neu: C belegt Slot 000 und ist nach Schritt 9 stabil.
- Gleichstand: durch die verschiedenen letzten Auswahlschritte ausgeschlossen.

PPB-1 muss B und C erkennen und `0` sowie die ferne Kontrolle ablehnen. Die
statische Bank behaelt `0` und B, erkennt beide und lehnt C sowie die ferne
Kontrolle ab. Der kontrollierte Rollenwechsel bei gleicher Kapazitaet ist
hier die vorab gebundene funktionale Differenz.

### H5: Spaeterer Abruf nach Aktualisierung

- Bildung: `0, 0, 0`.
- Aktualisierung: graduell 1, graduell 2, graduell 3.
- Trennung: genau vier Ticks ohne weitere Exposition und ohne Rohhistorie.
- Proben: graduell 3, `0`, Konflikt B.
- Sollrolle: Zustand und Slotidentitaet bleiben waehrend aller Proben
  unveraendert.
- Akzeptanz: graduell 3 liegt in PPB-1 strikt naeher als in der statischen
  Bank; beide erkennen `0` und lehnen B ab.

## Nichtzirkulaerer Verhaltenskomparator

Der Funktionsvergleich verwendet ausschliesslich Erkennungsentscheidung und
normalisierte L1-Distanz derselben Probe.

Fuer eine erwartete positive Zielprobe ist PPB-1 strikt besser, wenn:

1. PPB-1 erkennt und die Baseline nicht erkennt; oder
2. beide erkennen und die PPB-1-Distanz strikt kleiner ist.

Fuer eine erwartete negative Zielprobe ist PPB-1 strikt besser, wenn PPB-1
ablehnt und die Baseline faelschlich erkennt. Wenn beide korrekt ablehnen,
ist der Fall verhaltensgleich; die groessere Distanz zaehlt nicht als
zusaetzlicher Vorteil.

Ein Nachteil liegt bei der jeweils umgekehrten Erkennungsrelation oder bei
gleicher korrekter positiver Entscheidung und groesserer PPB-1-Distanz vor.
Private Digests, Supportzaehler, Slotzahl und Identitaetsrollen werden nur
auditiert und duerfen Vorteil oder Gleichstand nicht bestimmen.

## Aggregation

Der technische Gesamterfolg verlangt gleichzeitig:

- beide Modalitaeten vollstaendig;
- alle fuenf Geschichten vollstaendig;
- alle Probe- und Receiptrollen vorhanden und read-only;
- keine Sicherheitsregression in H1;
- strikten Vorteil fuer H2/graduell 3 und H5/graduell 3;
- die gebundene H3-Trennung;
- die gebundene H4-Verdraengung mit Vorteil fuer C und fuer die erwartete
  Ablehnung des verdraengten `0`;
- keine schlechtere Entscheidung fuer irgendeine negative Kontrolle;
- keine Methodenungueltigkeit.

Ein fehlender Arm, Gleichstand in einem verpflichtenden Vorteilsarm oder
eine nachtraeglich geaenderte Sollrolle ergibt keinen Gesamterfolg.

## Entscheidung und Grenze

Die sechs S1-XV-Blocker sind auf Vertragsebene geschlossen:

`PASS_SIX_MATERIALIZATION_BINDINGS_COMPLETE_NO_IMPLEMENTATION_TEST_OR_EXECUTION`

S1-XW ist weiterhin nur ein statischer Engineeringvertrag. Er belegt keine
ausgefuehrte Aktualisierungsfunktion, keine MCM-spezifische Memory-Mechanik
und keine Feldwirkung.

Der kanonische Vertragsdigest lautet
`4a39cae0f79b75921b6508f434d4d88390e76e51920cf8d7dcf706f75f30e8ef`.

## Naechster Schritt

S1-XX darf ausschliesslich statisch pruefen, ob alle numerischen Werte,
erwarteten Prototyp- und Distanzrollen, Budgets, Konflikt-, Verdraengungs-
und Aggregationsregeln intern widerspruchsfrei und mit den vorhandenen
PPB-1-Quellen kompatibel sind. Keine Implementierung, Tests oder
Ausfuehrung.
