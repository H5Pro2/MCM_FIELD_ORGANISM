# S2-MF: Materialisierungsaudit der slotgebundenen Anwendbarkeitsevidenz

## Status

`S2MF_STATIC_MATERIALIZATION_AUDIT_NOT_PASSED`

S2-MF prueft den statischen S2-ME-Vertrag vor jeder Implementierung. Der
Audit verwendet ausschliesslich bestehenden Quelltext und bereits
abgeschlossene read-only Ergebnisbelege. Es wurden keine Rezeptor-, PPB-,
Memory-, Kontext- oder Feldfunktionen aufgerufen und keine neuen Fixtures
erzeugt.

Der Audit bestaetigt, dass die neue Lernregel technisch atomar angebunden
werden kann. Er kann jedoch den entscheidenden prospektiven Starttest noch
nicht ableiten. Ein konkreter neuer, vor Rezeptor- und PPB-Auswertung
versiegelter Korpus samt literalem Ereignisplan fehlt. Zusaetzlich sind die
administrativen und kanonischen Artefaktgrenzen noch nicht vollstaendig
materialisiert. Eine Implementierung bleibt gesperrt.

S2-MC und S2-ME werden dadurch nicht widerlegt oder umgedeutet. MD-B02 und
MD-B03 bleiben ausserhalb dieses Audits.

## Auditbasis

Unveraenderter Default-Live-Zustand:

- visuelle Rezeptordimension: `288`;
- visuelle Slow-Kapazitaet: `4`;
- visuelle PPB-Matchgrenze: `0.01`;
- visuelle PPB-Aktualisierungsrate: `0.05`;
- stabil ab Support `3`;
- bestehender maskenkonditionierter Formdeskriptor: `144` Werte;
- Anwendbarkeit spaeterer zwei Blicke: `192` tatsaechlich beobachtete
  Raster-/Kanalpositionen.

Der bestehende PPB-Slot enthaelt nur Slot-ID, Belegungsstatus,
Prototypwerte, Support und letzten Auswahlschritt. Er enthaelt keine
Kalibrations-ID, keinen Radius und keine Formdeskriptorkette.

## Pruefmatrix

| ID | Pruefung | Ergebnis |
| --- | --- | --- |
| MF-P01 | S2-ME-Evidenz bleibt direkt an genau eine visuelle PPB-Slotgeneration gebunden | statisch darstellbar |
| MF-P02 | 192er-Deskriptor und PPB-Uebergang stammen aus derselben Formation | statisch darstellbar |
| MF-P03 | `CREATED`, `MATCHED`, fuenfter FIFO-Eintrag und `REPLACED` besitzen bestehende PPB-Anknuepfungspunkte | statisch darstellbar |
| MF-P04 | Evidenzfehler kann Memorypublikation verhindern, ohne Feldkontakt zurueckzunehmen | statisch darstellbar |
| MF-B01 | neuer Korpus und neutrale Ereignisreihenfolge sind vor jeder Auswertung konkret versiegelt | nicht materialisiert |
| MF-B02 | mindestens eine variable Trainingsfolge bleibt unter unveraenderter PPB-Regel in derselben Slotgeneration | nicht ableitbar |
| MF-B03 | alte Evidenz ist nach `REPLACED` durch eine exakt gebundene Generationsidentitaet unerreichbar | Digestform unvollstaendig |
| MF-B04 | administrative Daten und vollstaendige kanonische Artefaktgroessen besitzen endliche Maxima | nicht vollstaendig gebunden |

Jeder offene `MF-B*`-Punkt sperrt Adapter, Baseline, neutrale Tests und einen
Funktionslauf.

## MF-P01: Direkte Slotbindung

Die S2-ME-Evidenz kann als privater Bestandteil desselben aeusseren
visuellen Slow-Zustands gefuehrt werden. Pro PPB-Slot existiert dabei genau
eine Evidenzrolle mit derselben Slot-ID und einer eigenen Generation.

Die Projektion darf nie eine Kandidatenliste unabhaengig von den vier realen
PPB-Slots bilden. Ein Evidenzeintrag ist nur gueltig, wenn der zugehoerige
PPB-Uebergangsbeleg genau diesen Slot als ausgewaehlt bindet. Damit entsteht
keine dritte Memory-Ebene.

## MF-P02: Identischer Formationseingang

Der notwendige Datenfluss ist ohne Rueckrechnung materialisierbar:

```text
validierter RGB8-Frame
-> unveraenderter visueller Rezeptor
-> ein gebundener 288-Werte-Zustand
   -> bestehender PPB-Formationseingang
   -> Auswahl der festen UNION_192-Positionen
      -> bestehender maskenkonditionierter 144-Werte-Formdeskriptor
```

Der Formdeskriptor kann vor dem PPB-Aufruf vollstaendig berechnet und
validiert werden. Nach dem PPB-Aufruf darf er nur an die vom realen
Uebergangsbeleg ausgegebene Slot-ID gebunden werden. Beide Zweige muessen
denselben Rezeptorwertedigest, denselben Quellpayloaddigest und dasselbe
Quellzeitfenster tragen.

Unzulaessig waeren:

- erneute Rezeptoranalyse fuer die Evidenz;
- Ableitung des Deskriptors aus dem aktualisierten PPB-Prototyp;
- Verwendung eines anderen Frames oder Zeitfensters;
- Wahl der Slot-ID durch den Deskriptor oder durch Familienwissen.

## MF-P03: Uebergangsabdeckung

Der unveraenderte PPB-Kern stellt die notwendigen Ereignisse bereit:

- erster nicht passender Inhalt in freiem Slot: `CREATED`;
- Abstand `<= 0.01` zu mindestens einem Slot: deterministische Auswahl und
  `MATCHED`;
- weitere Treffer nach Supportsaettigung: weiterhin `MATCHED`;
- kein Treffer bei voller Vier-Slot-Bank: deterministische LRU-Auswahl und
  `REPLACED`.

Damit ist ein fuenfter Evidenzeintrag prinzipiell erreichbar: Nach vier
Zuordnungen derselben Generation fuehrt ein weiterer realer `MATCHED`-
Uebergang zur FIFO-Ersetzung des aeltesten Deskriptors. Die bestehende
PPB-Supportsaettigung verhindert diesen fuenften Treffer nicht.

Bei `REPLACED` muss die Evidenzfortschreibung die alte Generation verwerfen
und genau einen neuen Eintrag aus derselben Ersatzformation bilden. Diese
Operation ist technisch darstellbar, ihre kanonische Generationsbindung ist
unter MF-B03 jedoch noch nicht vollstaendig festgelegt.

## MF-P04: Atomaritaet und Feldunabhaengigkeit

Der PPB- und der bestehende B4-/TSPM-Fortschritt arbeiten mit unveraenderlichem
Prestate und liefern einen vorgeschlagenen Poststate. Ein privater aeusserer
Koordinator kann deshalb:

1. Rezeptor- und Formdeskriptorbeleg vorvalidieren.
2. Den bestehenden atomaren B4-/TSPM-Schritt berechnen.
3. Die Evidenz aus dessen realem visuellen PPB-Uebergang berechnen.
4. Erst nach vollstaendiger Validierung den gemeinsamen Memorypoststate
   zurueckgeben.

Bei einem Evidenzfehler darf kein Teil dieses vorgeschlagenen
Memorypoststates an den Stromzustand uebergeben werden. Der Ereignisowner
kann fehlerhaft terminal enden; der Memory-Prestate bleibt der sichtbare
Zustand.

Der Feldzweig bleibt wie in S2-LM ein unabhaengiger Geschwisterzweig. Ein
bereits gueltiger Feldkontakt bleibt daher auch dann bestehen, wenn die
Memory-/Evidenzfortschreibung fehlschlaegt.

## MF-B01: Kein konkreter prospektiver Korpus

S2-ME bindet Mindestklassen und eine Planform, aber noch nicht:

- die konkreten neutralen Quellenrezepte und Seeds;
- deren kanonische Byte-Digests;
- eine literale Formationseventfolge;
- die genaue Reihenfolge der vier Trainingsvarianten pro Slotkandidat;
- eine separate Ersetzungs- und FIFO-Kontrollfolge;
- die Quellen- und Zeitfenster aller Ereignisse;
- einen konkreten Planfiledigest.

Ohne diese Angaben kann nicht statisch entschieden werden, welche reale
Formation der unveraenderte PPB-Kern welchem Slot zuordnet. Eine spaetere
Auswahl von Varianten nach Rezeptordistanz waere zirkulaer und ist verboten.

## Historischer S2-LZ-Korpus ist kein Ersatz

Der vorhandene S2-LZ-Plan wurde zwar vor seiner damaligen Rezeptoranalyse
versiegelt. Er ist fuer S2-MF dennoch kein zulaessiger neuer Korpus:

- seine Referenzgruppen tragen bereits die externen Rollen `model-01` bis
  `model-04`;
- seine Rezeptor- und Open-Set-Ergebnisse sind bereits bekannt;
- eine jetzige Auswahl daraus waere ergebnisinformierte Wiederverwendung;
- seine vier Referenzvarianten pro Gruppe bilden unter der unveraenderten
  visuellen PPB-Grenze keine gemeinsame Startgeneration.

Der letzte Punkt ist bereits aus dem abgeschlossenen S2-LV-Beleg eindeutig.
Nach der ersten Formation ist der erste PPB-Prototyp exakt deren
288-Werte-Vektor. Der Abstand zur jeweils zweiten Referenz betraegt:

| historische Gruppe | erster Uebergang | 288-Werte-Mean-L1 | PPB-Folge |
| --- | --- | ---: | --- |
| `model-01` | `source-001 -> source-002` | `0.027450980392156862` | `CREATED -> CREATED` |
| `model-02` | `source-007 -> source-008` | `0.014040183974824498` | `CREATED -> CREATED` |
| `model-03` | `source-013 -> source-014` | `0.021496005809731300` | `CREATED -> CREATED` |
| `model-04` | `source-019 -> source-020` | `0.023485838779956428` | `CREATED -> CREATED` |

Alle vier Abstaende liegen strikt ueber `0.01`. Der entscheidende
S2-MF-Starttest scheitert fuer diesen historischen Korpus bereits am zweiten
Referenzeintrag. Die deutlich kleineren 144-Werte-Formdeskriptorabstaende
duerfen diese PPB-Zuordnung nicht beeinflussen.

## MF-B02: Starttest nicht ableitbar

Der verbindliche Starttest lautet:

```text
Mindestens eine Folge aus real unterschiedlichen, vorab versiegelten
vollstaendigen Formationen erzeugt unter der unveraenderten visuellen
PPB-Regel eine lueckenlose Slotgeneration mit Support >= 3.
```

Erforderlich sind mindestens:

- ein `CREATED`-Uebergang;
- zwei anschliessende `MATCHED`-Uebergaenge auf dieselbe Slotgeneration;
- mindestens zwei unterschiedliche Rezeptorwertedigests;
- mindestens zwei unterschiedliche 144-Werte-Deskriptordigests;
- keine Familien- oder Evaluationsinformation im Zuordnungspfad.

Da MF-B01 keinen konkreten neuen Plan liefert, ist dieser Test derzeit weder
bestaetigt noch falsifiziert. Eine bitidentische Vierfachwiederholung wuerde
Support erzeugen, aber nicht die geforderte erfahrungsbasierte
Variationshuelle materialisieren.

Wenn ein spaeter vorab versiegelter Korpus die Varianten auf mehrere Slots
verteilt, endet diese konkrete S2-ME-Materialisierung als
`S2ME_SLOT_APPLICABILITY_HISTORY_NOT_MATERIALIZABLE`. Korpus, Reihenfolge und
PPB-Grenze duerfen danach unter derselben Materialisierungs-ID nicht geaendert
werden.

## MF-B03: Generationsidentitaet unvollstaendig

S2-ME fordert einen `slot_generation_digest`, legt dessen kanonischen Payload
aber noch nicht feldgenau fest. Ohne diese Form kann der Offline-Verifikator
nicht eindeutig unterscheiden zwischen:

- fortgesetztem `MATCHED` derselben Generation;
- freiem und danach neu belegtem Slot;
- tatsaechlichem `REPLACED`;
- erneutem Inhalt mit derselben Slot-ID;
- manipuliert wiederangehaengter Evidenz einer alten Generation.

Fuer eine spaetere Materialisierung muss die Generation mindestens aus
Schema, Bank- und Konfigurationsdigest, Slot-ID, erzeugendem
`CREATED`-/`REPLACED`-Resultdigest, Formationseingangsdigest und
PPB-Schrittordinalzahl gebildet werden. Der aktuelle Zustand darf nach
Ersetzung keine Eintrags- oder Huelledigests der alten Generation referenzieren.

Historische Auditbelege duerfen den frueheren Zustandsdigest erhalten, aber
keine alte Generation als aktuellen Kandidaten oder aktuelle
Anwendbarkeitsevidenz projizieren.

## MF-B04: Administrative und kanonische Groessen

Das numerische S2-ME-Budget ist korrekt, aber nicht hinreichend:

- maximal `2.304` gespeicherte Deskriptorwerte;
- maximal `18.432` Byte logischer Float64-Wertebestand;
- maximal `5.184` Deskriptor-Rechenpositionen pro Funktionsarm und
  Teilblickpaar.

Noch ungebunden sind:

- exakte kanonische Payloads aller drei S2-ME-Datentypen;
- maximale Laengen von Quellenclock, Slot-ID und administrativen IDs;
- obere Grenzen fuer PPB-Schritt und Quellticks;
- maximale kanonische Floatdarstellung;
- Entry-, Slot-Evidenz-, Huelle-, Ergebnis- und Fehlerbeleggroesse;
- maximale Gesamtgroesse des privaten erweiterten Memoryzustands;
- Operations- und Receiptanzahl fuer FIFO- und Ersatzkontrollen.

Da Schritt- und Tickwerte derzeit keine fuer diesen Vertrag gebundene
kanonische Zifferngrenze besitzen, existiert noch keine endliche beweisbare
Artefaktobergrenze. Eine Schaetzung nur aus `8` Byte pro Float deckt JSON-
Serialisierung, Feldnamen, IDs und Digests nicht ab.

## Erforderliche enge Materialisierung

Vor einer Implementierung sind ausschliesslich folgende Luecken zu
schliessen:

1. Einen neuen neutralen Korpus mit unveraenderlichen Quellenrezepten,
   Seeds, Byte-Digests und literalem Ereignisplan versiegeln, ohne Rezeptor-,
   PPB- oder Schwellenimport.
2. Eine einmalige getrennte Rezeptor- und bestehende PPB-Materialisierung
   dieses exakten Plandigests freigeben. Es gibt keine Distanzsuche, keine
   Quellenauswahl und keinen Retry.
3. Die exakte `slot_generation_digest`-Form und die kanonischen
   S2-ME-Payloads binden.
4. Endliche ID-, Zeit-, Zaehler-, Einzelartefakt- und Gesamtzustandsgrenzen
   festlegen und gegen alle geplanten Pfade berechnen.

Nur wenn die einmalige PPB-Materialisierung mindestens eine reale variable
`CREATED -> MATCHED -> MATCHED`-Generation bestaetigt, kann S2-MF bestanden
werden. Erst danach sind Slot-Evidenzadapter, Direktbaseline und neutrale
Tests gerechtfertigt.

## Aussagegrenze

S2-MF stellt keinen negativen Befund ueber PPB, S2-MC oder die geplante
Lernregel dar. Der Audit verhindert ausschliesslich, dass ein bereits
ausgewerteter Rollen-Korpus oder eine ungebundene Artefakthuelle als
rollenfreies Lernen ausgegeben wird.

Die README wird nicht erweitert.

## Gebundene Belege

Auditbasis ist Commit:

```text
8fcbd5059552f665848f296adefceab043106cd5
```

Quell- und Belegdigests:

```text
15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0  mcm_field_organism/_ppb1_reference.py
ad5c8f607bc375daa8a6ed70134f6ed716780658a2a5e88bddb77a980da1af6f  tools/_s2jw_default_live_profile.py
64125b0ff0e469b792c1969f35b9972ca60723fd2503b1194fc703042eba34e4  tools/_s2lv_private_pose_form_projection.py
012bd97f2f5f036b09f4b21fb0934133893711d5cc87cbc48680595ee1f1c31e  tools/_s2ly_private_two_view_projection.py
ab1a3b93929ec483e03e2b5a1a303a3a6d0ba3930463d1bce3998cbdb582356d  tools/_s2mb_private_bstable_two_view.py
14427ffb7be9cee389782fd141406d289255fade2d2de3bb137c07503b53e13a  tools/_s2lz_private_open_set_comparison.py
69fec956b6e68bcde41367308fd9a4d785969fdbf1b62ef3eed5641de20b6fe7  reports/s2lz/s2lz-open-set-corpus-20260905-01/presealed-plan.json
3e5bdc0f0a88b92818048a464d9ca31cc137421c2b95e37879158adf9c610aa1  reports/s2lv/s2lv-pose-form-comparison-20260905-01/comparison.json
4dc6d755ed77ad6247319a91ec96f77d0d44f282ef9d945d58fb33e6ecb05745  docs/S2ME_ROLLENFREIE_SLOTGEBUNDENE_ANWENDBARKEITSEVIDENZ_VERTRAG.md
```
