# S1-ZQ: W1-F statischer Drei-Asset-EOL-Korrekturvertrag

## Auftrag und Grenze

S1-ZQ bindet die kleinstmoegliche Korrektur fuer die in S1-ZP nachgewiesene
LF/CRLF-Arbeitsbaumabweichung. Dieser Schritt erstellt noch keine
`.gitattributes`, schreibt keine Assetdatei um und fuehrt keine Projekt-,
Smoke-, Browser-, Capture-, Rezeptor- oder Feldfunktion aus.

## Gebundene Korrektur

Die spaetere Korrektur darf eine neue `.gitattributes` mit genau diesen drei
wirksamen Regeln anlegen:

```gitattributes
tools/controlled_browser_payload_world/index.html text eol=lf
tools/controlled_browser_payload_world/styles.css text eol=lf
tools/controlled_browser_payload_world/world.js text eol=lf
```

Es ist keine globale EOL-Regel und keine Regel fuer Python-, Dokumentations-,
JSON-, Report- oder andere Assetdateien freigegeben.

## Unveraenderliche Byteerwartung

Nach der kontrollierten LF-Materialisierung muessen die rohen
Arbeitsbaumdigests genau den bereits gebundenen W1-F- und Git-Blob-Digests
entsprechen:

| Asset | unveraenderter Sollwert |
|---|---|
| `index.html` | `74fc372a3eff08ac38e803689e562ce5acbb39d56d3351db475c768457e32af8` |
| `styles.css` | `f026fce8f826fb7364a11b1b05ad4acb3dd37aed7dede5453c6f82cbf497b594` |
| `world.js` | `fda8c774708af883eb97625b7064ec288c06e2819619fb2eb93e281212d32158` |

Inhalt, Reihenfolge, Dateinamen und W1-F-Konstanten duerfen nicht angepasst
werden. Die Korrektur gilt als ungueltig, falls ausser dem Zeilenende ein Byte
abweicht oder Git einen neuen Assetinhalt registriert.

## Atomare Durchfuehrungsfolge fuer S1-ZR

1. Vorzustand und sauberen Git-Status pruefen.
2. Die drei exakten Attributregeln anlegen.
3. Nur die drei gebundenen Arbeitsbaumdateien als LF materialisieren.
4. Rohdigest, Git-Blobdigest und W1-F-Erwartung fuer jedes Asset vergleichen.
5. Mit `git check-attr text eol` genau `text: set` und `eol: lf` nachweisen.
6. Zuerst statische S1-ZP/S1-ZQ-Guards, danach nur fokussierte synthetische
   Source- und Fake-Smoke-Tests ausfuehren.

Bei Teilkorrektur, Zusatzdatei, Digestabweichung oder unerwartetem Git-Diff
wird fail-closed abgebrochen. Ein Retry darf keinen teilweise akzeptierten
Zustand fortsetzen.

## Test- und Ausfuehrungsgrenze

Nach erfolgreicher Korrektur sind nur synthetische Tests mit injizierter
Fake-Playwright-Factory zulaessig. Ein installiertes Browserbinary darf nicht
gestartet werden. Reale Browser-, Audio-/Video-, Rezeptor- oder Feldlaeufe
bleiben gesperrt.

Ein bestandener Test belegt ausschliesslich portable Assetbindung und den
bereits vorhandenen technischen Fake-Lifecycle. Er erzeugt keinen neuen
Feld-, Wahrnehmungs- oder Memory-Befund.

## Entscheidung

```text
Korrekturumfang eindeutig: ja
W1-F-Erwartungswerte zu aendern: nein
globale EOL-Aenderung zulaessig: nein
Korrektur in S1-ZQ ausgefuehrt: nein
S1-ZR eng freigabefaehig: ja
```

## Naechster Schritt

S1-ZR darf genau die drei Regeln implementieren, die drei Assetdarstellungen
kontrolliert auf LF materialisieren und die gebundenen statischen sowie
synthetischen Tests ausfuehren. Ein realer Browserstart bleibt ausgeschlossen.

Maschinenlesbarer Vertrag:
[S1ZQ_W1F_STATISCHER_DREI_ASSET_EOL_KORREKTURVERTRAG_V1.json](S1ZQ_W1F_STATISCHER_DREI_ASSET_EOL_KORREKTURVERTRAG_V1.json).

