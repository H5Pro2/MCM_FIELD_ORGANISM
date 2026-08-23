# S1-XX: Statischer numerischer Konsistenz- und Quellenkompatibilitaetsaudit

## Auftrag und Grenze

S1-XX prueft den S1-XW-Materialisierungsvertrag ausschliesslich anhand der
gebundenen JSON-Werte und der vorhandenen PPB-1-Quelltexte. Es wurde kein
Projektmodul importiert und keine Fixture-, Zustands-, Probe-, Test- oder
Runnerfunktion ausgefuehrt.

## Numerischer Befund

Alle gebundenen Werte sind endlich, binaer exakt und liegen in `[-1, 1]`.
Die auditive Schwelle `0.25` und die visuelle Schwelle `0.125` entsprechen
der bestehenden robusten S1-XO-Rolle. Die konstante Belegung aller Traeger
macht die normalisierte L1-Distanz jeweils gleich dem absoluten
Skalarabstand; die Traegerzahl veraendert den Abstand nicht.

Bei Aktualisierungsrate `0.5` ergeben sich statisch exakt:

| Rolle | Auditiv | Visuell |
|---|---:|---:|
| H1 Endprototyp | 0.09375 | 0.046875 |
| H2/H5 Endprototyp | 0.1328125 | 0.06640625 |
| H2/H5 Abstand zum Ziel | 0.0546875 | 0.02734375 |
| statischer Abstand zum Ziel | 0.1875 | 0.09375 |

Damit erkennen beide Systeme die graduelle Zielprobe, PPB-1 liegt aber in
beiden Modalitaeten strikt naeher. Die Konflikt- und Negativkontrollen
bleiben auf der korrekten Schwellenseite.

## Vollstaendige Verhaltenspruefung

### H1

Der bestehende Nullprototyp wird durch zwei graduell-2-Expositionen auf die
gebundenen H1-Endwerte fortgeschrieben. Die Zielabstaende betragen
`0.03125` auditiv und `0.015625` visuell; die statischen Abstaende sind
`0.125` und `0.0625`. Konflikt B bleibt negativ.

### H2 und H5

Die drei graduellen Expositionen treffen bei jedem Schritt denselben Slot.
Die terminalen Zielabstaende stimmen exakt mit S1-XW ueberein. Ursprung und
graduell 2 bleiben positiv, Konflikt B bleibt negativ. Die vier Tick lange
Trennung in H5 veraendert keinen Zustand, weil die read-only Probe keinen
PPB-1-Schritt ausfuehrt.

### H3

Konflikt B liegt ausserhalb der Distanzschwelle zum Ursprung. Der erste
Kontakt erzeugt daher Slot 001; zwei weitere Kontakte stabilisieren ihn.
Slot 000 behaelt den stabilen Ursprung. PPB-1 erkennt beide Rollen mit
Distanz null, die statische Bank nur den Ursprung. Gegenpol C bleibt in
beiden Systemen negativ.

### H4

Nach der Bildung sind Slot 000/Ursprung zuletzt in Schritt 3 und Slot 001/B
zuletzt in Schritt 6 ausgewaehlt. Gegenpol C passt zu keinem Slot. Die
vorhandene Quellregel waehlt deshalb eindeutig Slot 000 als aeltesten Slot;
ein Gleichstand tritt nicht auf. Zwei weitere C-Kontakte stabilisieren den
ersetzten Slot. B und C sind danach positiv, Ursprung und ferne Kontrolle
negativ. Die statische Bank behaelt Ursprung und B.

## Kapazitaet, Stabilisierung und Ablauf

- Kapazitaet `2` stimmt mit allen Geschichten ueberein.
- Jede spaeter read-only auswertbare Zielrolle erreicht Support `3`.
- Der groesste Abstand eines nicht ausgewaehlten belegten Slots von seiner
  letzten Auswahl bleibt kleiner als die Ablaufgrenze `8`.
- H4 verwendet `REPLACED`, nicht impliziten Ablauf.
- Die Summen `18` Bildung, `14` Aktualisierung und `16` Proben pro System
  und Modalitaet sind korrekt.
- Die globalen Grenzen `128` Expositionsuebergaben und `64` Proben folgen
  exakt aus zwei Systemen und zwei Modalitaeten.

## Nichtzirkularitaet und Quellenkompatibilitaet

Der Vorteilsoperator verwendet nur Erkennungsentscheidung und Distanz. Die
fuenf verpflichtenden Vorteilsarme sind vorab festgelegt und fuer beide
Modalitaeten erreichbar. Digests, Support, Slotzahl und Identitaetsmetadaten
gehen nicht in den Vorteil ein.

Die vorhandenen Quellen stellen alle benoetigten Kandidatenrollen bereit:

- begrenzte Slots und atomare Fortschreibung;
- normalisierte L1-Distanz und `<=`-Matchoperator;
- Update mit vorhandener Rate;
- Stabilisierung ueber Support;
- deterministische Auswahl nach letzter Nutzung und Slot-ID;
- read-only Probe nur ueber stabilisierte Slots.

Eine private statische Vergleichshuelle und die neue Fixture sind noch
nicht implementiert. Das ist kein Vertragsfehler, sondern die naechste
Engineeringgrenze.

## Entscheidung

Alle `30 von 30` statischen Rollen bestehen:

`PASS_NUMERIC_INTERNAL_CONSISTENCY_AND_SOURCE_COMPATIBILITY_NO_EXECUTION`

Der Audit belegt nur die interne Berechenbarkeit des Vertrags. Er belegt
keine ausgefuehrte Aktualisierungsfunktion, keine MCM-spezifische
Memory-Mechanik und keine Feldwirkung. Alle Ausfuehrungszaehler sind null.

Der kanonische Auditdigest lautet
`29273e19be649ba57040e48e9fe11115ad45de03a12e1d0ac2d480d43436592a`.

## Naechster Schritt

S1-XY darf ausschliesslich als statischer Implementierungspreflight die
private Fixture-, Baseline-, Receipt- und Runneranatomie sowie exakte
Aufrufbudgets binden. Noch keine Implementierung, Tests oder Ausfuehrung.
