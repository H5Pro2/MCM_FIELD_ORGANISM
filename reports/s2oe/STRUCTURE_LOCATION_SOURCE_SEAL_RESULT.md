# Struktur-/Lage-Gegenprobe: rezeptorfreie Vorversiegelung

## Abschluss

`structure-location-source-qualification-20260912-01`: genau ein neutraler
Testaufruf, **6/6 bestanden**. Vorher Code, Prüfbestand, Interpreterdatei,
Planwurzeln und vollständige Reserven gebunden. Keine historischen Tests
wiederholt. Kleine neutrale 4×3-Pixel-Fixture, keine der 14 Quellen während
der Qualifikation erzeugt.

Erreicht: deterministische Pixelerzeugung gegen eine getrennte pixelweise
Referenz, Eingabeunveränderlichkeit, Exaktrezepte bei getrennten IDs/Zeiten,
22 Paarbindungen, 24 Kriterien, getrennte Bewertungswurzel, lokale und
globale Budgetabweisung sowie fehlende/manipulierte Quellenbindungen.

Danach `structure-location-source-seal-20260912-01`: genau **14 RGB-Frames**
einzeln erzeugt, gehasht und freigegeben; anschließend genau eine unabhängige
read-only Bindungsprüfung: **BINDING_VALID**. Kein erneutes Rendern in der
Prüfung. Vorgesehene Hashgleichheiten ausschließlich q01/q13 und q07/q14;
keine weiteren Kollisionen. Quellenidentitäten und native Zeitbindungen
bleiben getrennt. Keine Rohpayloadablage, keine Deduplizierung.

## Bindungen

Alle Dateien unter
`reports/s2oe/structure-location-source-seal-20260912-01/`:

- `execution.json`: SHA-256
  `60a0d7a7a20c31261b7e74e84c2b80a9f5a606ecf5fa7e8f8e94a8dd040baa36`
- `evaluation.json`: SHA-256
  `34734cae086afeb4317788bf224c46eb889e0f2c19432a69c9c890782c8d045a`
- `seal.json`: SHA-256
  `0b60545581687bfb04e5430835f98ee3b79884b195bf2e68ef5cf871fe63076f`

`preregistration.json` enthält das vollständige Quelleninventar einschließlich
Test und Dateieinstieg. Kein Rezeptor- oder Formmodul wird vom Sealer importiert.
Die zukünftigen 19.008 Differenzen, 19.008 separat zu prüfenden Terme,
88 Prüfsummen, 24 Ordnungskriterien und 1.728 Exaktgleichheiten bleiben
gebunden, aber unausgeführt. Projektionsrollen sind im Auswerterplan getrennt;
die funktionale Abschottung eines späteren Projektionsaufrufs ist noch nicht
qualifiziert, da dieser Anschluss hier nicht implementiert wurde.

## Ressourcen und Grenze

Vorbilanz: Quellen 21.476, Metadaten 55.311, Beleg 16.384,
Verifikation 8.192 Byte; insgesamt **101.363 Byte**.
Abschlussbilanz einschließlich noch voller Bilanz-/Berichtreserve:
**37.448 / 4.194.304 Byte**, Metadaten **12.763 / 65.536 Byte**,
Quellen 21.476, Quellenbeleg 3.027, Verifikation 182 Byte.
Reserve enthält 1.024 Byte Bilanz und 4.096 Byte für diesen Bericht;
physische Istdateien sind in `balance.json` einzeln aufgeführt.

Pro Erzeugung höchstens ein vollständiger 6.220.800-Byte-Frame plus eine
begrenzte Schreibzeile; insgesamt 87.091.200 erzeugte Payloadbytes, nicht
gespeichert. Das ist eine statische Containergrenze, kein gemessener
Prozess-Heap-Höchstwert.

Die Offline-Prüfung bestätigt Quellen-/Wurzelbindungen, Vollständigkeit und
aufgezeichnete Hashgleichheiten. Sie berechnet Pixelhashes nicht nochmals
aus Rohdaten und rekonstruiert die Erzeugung nicht numerisch.

Keine Rezeptor-/Formprojektion, Distanz- oder Ordnungsauswertung; kein
Tracker, Memory- oder Feldaufruf. Gates False. Historische Dateien
unverändert, kein Retry. Reale Vergleichsausführung bleibt gesperrt.
