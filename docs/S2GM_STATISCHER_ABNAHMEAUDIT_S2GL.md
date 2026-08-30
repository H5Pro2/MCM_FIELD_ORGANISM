# S2-GM: Statischer Abnahmeaudit von S2-GL

## Auftrag und Ausfuehrungsgrenze

S2-GM prueft den S2-GL-Vertrag rein statisch auf Materialisierbarkeit,
Nichtzirkularitaet und vollstaendige Budgets. Es wurden keine Projektmodule
importiert, keine Tests ausgefuehrt und keine Rezeptor-, Speicher-, Kontext-
oder Zustandsfunktion aufgerufen.

Geprueft wurden ausschliesslich:

- vorhandene Quelltexte und Datenformen;
- die literal dokumentierten Bildbits und Rohbytedigests;
- unabhaengige Ganzzahl-, Distanz- und Budgetarithmetik;
- statische Kontroll- und Digestbeziehungen.

## Gepruefte Quellgrundlage

| Rolle | gebundener SHA-256 | Ergebnis |
| --- | --- | --- |
| visueller Rezeptor | `d09cb6ba35fd061e4a243b7ed2112597a194e75abd026d7cc3ab7aa89922c07a` | identisch |
| B4-/TSPM-Koordinator | `95ee05ccc0eeb14abbcda036971da5c33ac79363dd546789f4878aace5677db0` | identisch |
| S2-GC-Projektion | `0fba7b0323fe772c481eb5261b9640e4a5b00d7da3ceb1a7e0f81c6d9f54bf49` | identisch |
| S2-GI-Projektion | `21bc206dc37f8a9f477c02eac7d14ff22e6924bbdb54eb5153122ec296cdd587` | identisch |
| S2-GK-Verbraucher | `29c16372184bec0092fadf777adc7b7e1c9a5ba0529711c46ca75c92c4769832` | identisch |
| S2-GK-Direktbaseline | `43ac94ca59a1157893cdc96cd4b980a0fb348130bc670596bbd3d65e112d7958` | identisch |
| S2-GK-Auswerter | `ac33ed97b670681250cb709b40332024ab107365836cd5641d27e34ee85e5cf5` | identisch |
| TSPM-1 | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` | identisch |
| PPB-1 | `15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0` | identisch |

## Bestandene Teilpruefungen

### Bilder und Rezeptoranatomie

Alle 25 Tabellenzeilen besitzen genau 18 Bits. Die daraus statisch
rekonstruierten Bilder besitzen:

```text
dtype = uint8
shape = (80, 120, 3)
Zellgroesse = 40 x 40
Kanalwerte = 0 oder 255
```

Alle 25 SHA-256-Werte der jeweils `28.800` Rohbytes stimmen. Weil jeder
Zellkanal konstant ist, ergibt die im Rezeptor implementierte Mittelwert-
bildung exakt den dokumentierten Wert `0/255 = 0.0` oder `255/255 = 1.0`.
Eine nachtraegliche Werteinspektion hinter dem Rezeptor ist nicht notwendig.

### Distraktor- und Abwesenheitsabstaende

Die unabhaengige statische Distanzpruefung bestaetigt:

- `D1..D9` untereinander mindestens `6/18`;
- `A1..A13` untereinander mindestens `6/18`;
- alle 22 D-/A-Bilder untereinander mindestens `6/18`;
- jeder D-/A-Zustand gegen `J1-T`, `J1-F` und das derzeitige `J1-C`
  mindestens `5/18`;
- auditive 4-von-8-Masken untereinander mindestens `2/8`.

Damit kann kein D- oder A-Schritt einen Fast-Match bei `0.2` erzeugen. Die
Abstaende liegen zugleich ueber der visuellen PPB-Grenze `0.01`, der
auditiven PPB-Grenze `0.02` und der funktionalen visuellen Grenze `44/765`.

### Support-, Ablauf- und Verdraengungsfolge

Die Quelllogik ergibt fuer vier identische AV-Expositionen:

| Schritt | Fast | Fast-Support | PPB-Aufruf | Slow-Support |
| ---: | --- | ---: | --- | ---: |
| 1 | `FAST_CREATED` | `1` | nein | `0` |
| 2 | `FAST_UPDATED` | `2` | ja, `CREATED` | `1` |
| 3 | `FAST_UPDATED` | `2` | ja, `MATCHED` | `2` |
| 4 | `FAST_UPDATED` | `2` | ja, `MATCHED` | `3`, stabil |

Fast ist auf Support `2` begrenzt und loest ab dort bei jeder passenden
Exposition eine Slow-Konsolidierung aus. Vier Expositionen sind daher exakt
ausreichend fuer Slow-Support `3`.

Nach Schritt 4 liegt die letzte Fast-Auswahl bei `4`. Vor Schritt 12 gilt
`12 - 4 = 8`; der Ziel-Fast-Slot laeuft somit bereits vor `D8` ab. B4 besitzt
Kapazitaet `9` und haelt nach Schritt 13 exakt `D1..D9`; alle vier frueheren
J-Eintraege sind dann FIFO-verdraengt.

Weil jeder D- und A-Zustand zu allen vorherigen D-/A-Zustaenden oberhalb der
Fast-Grenzen liegt, entsteht kein `FAST_UPDATED` und damit kein PPB-Aufruf.
`D1..D9` erzeugen keinen weiteren Slow-Kandidaten. `K_ABSENT` erzeugt bei 13
einmaligen AV-Quellen gar keinen Slow-Kandidaten.

### Zeit- und Frischegrenze

Die vier Tabellen besitzen jeweils 13 eindeutige, streng aufsteigende Fenster
`[0,1]` bis `[12,13]` und eine spaetere Probe `[13,14]`. Der Vertrag fordert
vier getrennte frische Composite-Zustaende. Eine Vermischung der Zustaende
ist nicht erforderlich und waere fail-closed ungueltig.

### Verbraucher- und Baselinebudget

Fuer die beiden tatsaechlich paarweise verglichenen Faelle `CORRECT` und
`FOREIGN` sind die gebundenen S2-GK-Ledger gleich:

```text
18 Maskenvalidierungen
9 sichtbare Vergleiche
9 Maskenuebernahmen
1 Bereichszugriff
1 Kandidatenreferenz
18 Wertereferenzen
2 Digestoperationen
```

Die Direktbaseline ruft den Verbraucher nicht auf. Beide erhalten dieselbe
maskierte Probe und dasselbe A/B-Bundle. Dieser Teil ist nichtzirkulaer und
budgetgleich.

### Zielwerttrennung

Der S2-GK-Verbraucher und die Direktbaseline erhalten keine getrennte
Zielwertfixture. Sie sehen nur die maskierte aktuelle Probe und den explizit
benannten B-Kandidaten. Vollstaendige Sollwerte werden erst an den reinen
Auswerter uebergeben. Die bestehende Implementierungsgrenze erfuellt diese
Trennung.

## Blocker

### GM-B01: `K_FOREIGN` ist mit der gebundenen Probe nicht materialisierbar

S2-GL bindet fuer alle vier Kontexte dieselbe volle read-only Probe
`J1-T/Q0`. Der visuelle Abstand von `J1-T` zu `J1-F` ist:

```text
9/18 = 0.5
```

Die Slow-Auswertung erkennt einen stabilen visuellen Prototyp nur bis zur
funktionalen Grenze `44/765`, ungefaehr `0.0575`. `0.5` liegt deutlich
darueber. `K_FOREIGN` liefert daher mit dieser Probe keinen visuellen
`B_STABLE`-Kandidaten, sondern eine gueltige Abwesenheit. Die vorgesehenen
Faelle `GJ-04` und `GJ-05` koennen so nicht entstehen.

Dieser Blocker betrifft nur die spaetere Kontext-Probenbindung. S2-GK selbst
bleibt unveraendert gueltig.

### GM-B02: Ziel und Konflikt sind nicht ueber alle Schwellen getrennt

Der Abstand des derzeitigen `J1-T` zu `J1-C` ist:

```text
1/18 = 0.055555...
```

Damit gilt gleichzeitig:

```text
1/18 > 0.01       visuelle native PPB-Grenze
1/18 <= 44/765    funktionale visuelle Auswertungsgrenze
1/18 <= 0.2       visuelle Fast-Grenze
```

Die Beziehung ist eindeutig berechenbar, erfuellt aber nicht die in S2-GM
geforderte eindeutige Trennung aller Ziel- und Konfliktbilder unter den
Matchgrenzen. Sie ist im bisherigen S2-GL-Weg notwendig, damit die fremde
`J1-T`-Probe den `J1-C`-Slow-Prototyp ueberhaupt als funktionalen Kontext
auswaehlt. Das zeigt einen Vertragswiderspruch zwischen Kontextauswahl und
Schwellentrennung.

Eine Korrektur muss Kontextbildung und spaetere maskierte Verbraucherprobe
getrennt binden. Der Audit legt noch keine neuen Bilder oder Probeformen fest.

### GM-B03: Fallrollen stehen in der Speicherprovenienz

Die kanonische Quellen-ID `s2gl.<context>.formation.<nn>` enthaelt die Rollen
`K_CORRECT`, `K_FOREIGN`, `K_CONFLICT` oder `K_ABSENT`. Diese Rollen werden
zwar nicht fuer Distanz oder Slotwahl verwendet, gehen aber in Quellen-,
Input-, Receipt- und Zustandsdigests ein.

Damit ist die strikte Forderung, dass keine Fallkennung den Speicherpfad
beeinflusst, nicht vollstaendig erfuellt. Erforderlich sind neutrale,
technische History- und Quellen-IDs. Die Zuordnung zu GJ-Faellen darf erst in
der Auswertung erfolgen.

### GM-B04: `131/262` ist nur ein fachlicher Top-Level-Umfang

Die Summe der in S2-GL genannten Top-Level-Operationen ist arithmetisch
korrekt:

```text
56 + 52 + 4 + 4 + 4 + 1 + 4 + 2 + 4 = 131
131 * 2 = 262
```

Noch nicht eindeutig gebunden ist, ob folgende notwendige Arbeiten eigene
Operationen sind oder atomar in diese 131 Operationen eingehen:

- Konfigurations- und Frischzustandsbildung;
- Quellen-, Zeit- und Envelopebindung;
- Owner- und Autorisierungsbildung;
- S2-GC-Projektionsbindung und `NOT_REQUESTED`-Sequenzevidenz;
- S2-GK-Kontextbindung;
- Konstruktion der privaten Maskenprobe;
- Laufmanifest, Terminalbefund und Abschlussmarker.

Ohne eine explizite Zuordnung waeren Operations- und Ereignisbudget im
spaeteren Runner mehrdeutig. Die Ressourcenledger der bereits vorhandenen
Funktionen sind korrekt, ersetzen aber diese Aufruf- und Recorderanatomie
nicht.

### GM-B05: Der prospektive Digestgraph ist noch nicht vollstaendig typisiert

Der in S2-GL angegebene Digestpfad ist vorwaertsgerichtet und zeigt keinen
offensichtlichen Zyklus. Fuer die noch nicht vorhandene Fixture-, Runner- und
Aufzeichnungsschicht fehlen jedoch konkrete Datenformen fuer:

- History- und Laufplan;
- Operation-START und Operation-RESULT;
- Maskenprobenableitung;
- Arm- und Fallreceipt;
- Evidenzpaket, Terminalbefund und Abschlussmarker.

Deshalb kann der gesamte Quellen-, Bild-, Kontext-, Bundle-, Projektions-,
Resultat- und Receiptgraph noch nicht formal als vollstaendig und azyklisch
abgenommen werden. Bestehende S2-FS-, S2-GC-, S2-GI- und S2-GK-Digests sind
fuer sich azyklisch; die offene Luecke liegt nur in der prospektiven
Laufhuelle.

## Auditentscheidung

Die Rezeptorbilder, Distraktoren, Abwesenheitsgeschichte, Supportfolge,
Fast-/B4-Entfernung und vorhandenen Funktionsledger sind statisch belastbar.
Der Gesamtvertrag ist dennoch nicht implementierungsreif, weil
`K_FOREIGN` mit der gebundenen Probe nicht erzeugt werden kann und die
Schwellen-, Provenienz-, Operations- und Laufdigestgrenzen noch nicht
widerspruchsfrei geschlossen sind.

Status:

`BLOCKED_S2GM_S2GL_NOT_YET_IMPLEMENTATION_READY`

Keine private Fixture-, Runner- oder Aufzeichnungsimplementierung ist
freigegeben. Es wurden keine Funktionsbefunde erzeugt und S2-GK wurde nicht
veraendert.

## Naechster enger Schritt

Der naechste fachlich begruendete Schritt ist ein statischer
Korrekturvertrag, der ausschliesslich GM-B01 bis GM-B05 schliesst:

1. kontextspezifische volle Speicherproben getrennt von der gemeinsamen
   maskierten Verbraucherprobe;
2. widerspruchsfreie Ziel-/Fremd-/Konfliktdistanzen;
3. neutrale Quellen-IDs ohne GJ-Fallrolle im Speicherpfad;
4. vollstaendige Zuordnung aller Hilfsarbeiten zu einem exakten
   Operations- und Ereignisbudget;
5. konkrete, azyklische Daten- und Digestformen der spaeteren Laufhuelle.

Diese Korrektur darf S2-GK, Speicherkerne, Schwellen und Erfolgskriterien
nicht aendern.
