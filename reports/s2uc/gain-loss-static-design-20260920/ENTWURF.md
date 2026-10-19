# S2-UC: Herkunftsgebundene Auswertung von Gewinn und Verlust

Status: **statischer Entwurf zur fachlichen Entscheidung**. Keine Implementierung, keine Tests, keine Quellenproduktion und keine Auswertung historischer Records. Der direkte Auftrag des Projektleiters ist die Grundlage. Code, sieben Zielbindungen, bestehende Erwartungen, Speicherregeln, Budgets und Realsperre bleiben unverändert. Die unabhängige technische Abnahme von V9 bleibt separat offen. Dies ist weder eine Laufnummer noch eine Versuchsvorregistrierung mit Ausführungsfreigabe.

## 1. Vergleichsgröße und Aussagegrenze

Die Vergleichsgröße ist der **eindeutige, herkunftsbelegte Abruf der für den jeweiligen Hint gebundenen gespeicherten Formation**. Ein Entscheidungstext, ein gleicher Vektor oder ein passender Quellenname allein genügt nicht. A, B und C sind ausschließlich Auswertungsnamen für die gebundenen Formationen; sie werden keinem Speicherarm als Labels übergeben.

Vier getrennte Aussagen sind vorgesehen:

1. **Entscheidung:** unveränderter Receipttext und vollständige Liste aller `(generation, offset)`-Treffer.
2. **Zielabruf:** eindeutig richtige gespeicherte Herkunft, anderer Abruf, Mehrdeutigkeit, Enthaltung oder nicht bestimmbar.
3. **Vergleich:** Zielabrufgewinn oder Zielabrufverlust von S2-UA gegenüber S2-TW am selben Hint. Diese Listen werden niemals saldiert.
4. **Mechanismus:** Erhaltung einer alten Retained-Spur, fehlende Übernahme, Kandidatenunterbrechung oder Ersetzung einer Retained-Spur durch bestätigte Konkurrenz. Ein Vergleichsunterschied allein beweist keinen dieser Mechanismen.

Das ist ein begrenzter Softwarevergleich. Weder Quellenidentität in einer offenen Umwelt noch allgemeine Erinnerungsfähigkeit wird daraus abgeleitet.

## 2. Unveränderte Bindungen und vollständige Sieben-Zeitpunkte-Tabelle

Verbindliche Quellen der Tabelle sind `TARGETS` in [Laufbinder](../../../tools/_s2uc_run_binding.py), `EXPECTED` in [Evaluator](../../../tools/_s2uc_evaluation.py) sowie Ereignisfolge und Segmentbildung in [Manifestcode](../../../tools/_s2uc_source_binding.py). **Die unten aufgeführten Entscheidungspaare werden wortgetreu übernommen, nicht korrigiert.**

Notation: `p1` usw. sind stets geschichtenbezogen. Ereignisnummern sind globale Manifestordinale, keine nativen Audiozeiten. Offsets sind nullbasiert: 0 adressiert Frames 1/2, 1 Frames 2/3 und 2 Frames 3/4 einer vollständigen Viererspur. Die angegebenen Framepaare sind die herkunftsrichtigen Hintpositionen; trotzdem müssen später alle drei Offsets aller tatsächlich vorhandenen Retained-Spuren berücksichtigt werden. Ein unerwünschter zusätzlicher Match darf nicht herausgefiltert werden.

| Hint / gebundene Eingabe | Zulässige gespeicherte Zielherkunft und zugehörige Frameordinale | Richtiger Offset / Ziel-Framepaar | Relevante Herkunfts- und Übergangsanker | Bestehende Erwartung S2-TW / S2-UA | Getrennte Vergleichsfrage, kein Ergebnis |
|---|---|---|---|---|---|
| **g1/12**, Hintframes 11/12, `H(b,c)` | A aus `g1-p1` (1–4) oder `g1-p2` (6–9) | **1**: p1 → 2/3; p2 → 7/8 | Closes 5 und 10. Gespeicherte Ursprungsframes und Bestätigung durch p2 auseinanderhalten. | `TRACE_MATCH` / `TRACE_MATCH` | Referenzpunkt nach wiederholtem A; richtige Herkunft in beiden Armen einzeln feststellen. |
| **g1/24**, Hintframes 23/24, `H(c,d)` | A aus `g1-p1` (1–4) oder `g1-p2` (6–9) | **2**: p1 → 3/4; p2 → 8/9 | Closes 5/10 sowie B: 17 und C: 22. Durchgängige A-Generation verfolgen; bei TW eventuelle Verdrängung derselben Generation belegen. | `ABSTAIN_AMBIGUOUS_RETAINED_TRACE` / `TRACE_MATCH` | Möglicher A-Erhaltungsgewinn; Erwartungskonflikt K1 beachten. |
| **g1/26**, Hintframes 25/26, `H(d,c)` | B ausschließlich aus `g1-p3` (13–16) | **0**: 13/14 | B-Close 17; C-Close 22. Bei UA B-Kandidat und gegebenenfalls dessen Ersetzung durch C zuordnen. | `TRACE_MATCH` / `ABSTAIN_NO_RETAINED_TRACE` | Verlust des einmaligen B-Zielabrufs gegenüber TW; getrennt vom A-Gewinn bei 24. |
| **g2/38**, Hintframes 37/38, `H(b,c)` | A ausschließlich aus `g2-p1` (27–30) | **1**: 28/29 | A-Close 31, B-Close 36. Die zweite A-Formation `g2-p3` (39–42, Close 43) liegt **nach** diesem Hint. | `TRACE_MATCH` / `ABSTAIN_NO_RETAINED_TRACE` | Unterbrechungsbedingtes Abrufdefizit bzw. Nichtübernahme des ersten A; keine rückwirkende Hilfe durch p3. |
| **g3/60**, Hintframes 59/60, `H(c,d)` | A ausschließlich aus `g3-p1` (44–47) | **2**: 46/47 | A-Closes 48/53; B-Close 58. `g3-p2` (49–52) ist möglicher Bestätiger, **nicht zusätzlich erlaubte gespeicherte Zielherkunft**. | `TRACE_MATCH` / `TRACE_MATCH` | A-Referenz vor der zweiten B-Formation; Ausgangspunkt für den zeitlichen Vergleich mit 67. |
| **g3/67**, Hintframes 66/67, `H(c,d)` | A ausschließlich aus `g3-p1` (44–47) | **2**: 46/47 | Vorzustand bei 60 und B-Close 65. Ersetzter Retained-A-Identifier muss mit dem früher belegten A übereinstimmen. | `TRACE_MATCH` / `ABSTAIN_NO_RETAINED_TRACE` | Möglicher A-Verlust nach bestätigter B-Konkurrenz; Vergleichsverlust, Bestandsersetzung und früherer Abruf getrennt ausweisen. |
| **g3/69**, Hintframes 68/69, `H(d,c)` | B aus `g3-p3` (54–57) oder `g3-p4` (61–64) | **0**: p3 → 54/55; p4 → 61/62 | B-Closes 58/65. Kandidatenursprung p3 und Bestätigung p4 getrennt nachweisen. | `TRACE_MATCH` / `TRACE_MATCH` | Richtiger B-Abruf nach Konkurrenz; kein Ausgleich eines A-Verlusts bei 67. |

Diese Herkunftsmengen werden **nicht** durch alle wertgleichen Formationen erweitert. Insbesondere gehören g2-p3 nicht zum Ziel g2/38 und g3-p2 nicht zum Ziel g3/60 oder g3/67. Die Mengen mit zwei Formationen erlauben keine frei erfundene Mischspur aus beiden.

Numerische Generationen werden nicht vorab eingesetzt: Sie entstehen durch die tatsächlichen, wertabhängigen Übergänge. Eine konkrete Generation ist erst durch den späteren Receipt und seine vollständige Ursprungskette belegt. Die Tabelle behauptet daher weder einen bestimmten Speicherinhalt noch ein Ergebnis an einem der sieben Zeitpunkte.

## 3. Erforderliche Belegkette

### 3.1 Technische Eingangsvoraussetzung

Eine spätere fachliche Auswertung setzt den unveränderten gültigen Produktabschluss mit bestandener technischer Verifikation und stimmigen Record-/Verifikations-/Terminalreferenzen voraus. Ein externer Prozessbeleg oder `VERIFIED_FAILURE` ersetzt diesen Abschluss nicht. Ein nicht auswertbarer Gesamtabschluss wird nicht durch die Herausnahme früher erfolgreicher Hintzeilen nachträglich fachlich auswertbar gemacht.

Für einen noch nicht ausgeführten oder technisch unzureichend belegten Vergleich lauten Gewinne und Verluste **nicht bestimmbar**. Der vorliegende Entwurf trägt deshalb überhaupt keine beobachteten Gewinne oder Verluste ein.

### 3.2 Vom Match zur gespeicherten Formation

Für jeden Arm und Hint ist die folgende Kette erforderlich:

1. In der `stories`-Liste wird die Zeile mit dem gebundenen `story`-Wert ausgewählt. Deren `hints` enthält genau den Receipt mit gebundenem `ordinal` und Hintsegment. Die zwei Hintereignisse in `events` stimmen mit den entsprechenden Manifestereignissen überein. Erste Hintaufnahme liefert noch keine abschließende Entscheidung.
2. `immediate_before`/`candidate_before` und `immediate_after`/`candidate_after` belegen dieselben vollständigen Speicherinhalte und Generationen. Owner und Profil stimmen. Die Snapshots umfassen den Zustand vor dem ersten und nach dem zweiten Hintframe; kein Hint fördert Kandidaten, ersetzt Spuren oder erneuert deren Alter.
3. Jeder `(generation, offset)`-Eintrag verweist auf eine tatsächlich in diesem **Vorzustand** vorhandene Retained-Spur desselben Arms, Owners und derselben Geschichte. Ein Kandidat oder eine spätere Formation ist nicht abrufberechtigt. `offset` liegt in 0..2. Die vollständige Matchliste muss der unveränderten positionsbezogenen Wertevergleichsregel entsprechen.
4. Alle vier gespeicherten `Frame`-Objekte dieser Spur werden über `ordinal`, `segment`, `owner` und `profile` auf ihre vier Formationsereignisse zurückgeführt. Sie bilden genau eine abgeschlossene, geordnete Formation. Gleiche Werte allein begründen weder diese Zuordnung noch ein Zusammenführen verschiedener Ursprünge.
5. Die zugehörigen Ereigniszeilen binden `source_id`, `values_hex` und Materialisierungsreceipt an die Manifestendpunkte: PCM-Hash/-Bytezahl, Profil, natives Samplefenster, NJ-Snapshotindex sowie die vorhandenen Projektions-/Wert-/Rohzustandsquerbindungen. Die bestehenden Verifikationsbelege bleiben Voraussetzung; es wird kein PCM neu erzeugt und keine Rohrezeptornachrechnung aus unvollständigen Daten behauptet.
6. Die aus diesen vier Ereignissen bestimmte gespeicherte Formation muss Mitglied der **expliziten Zielmenge der Tabellenzeile** sein. Die beiden adressierten Frames müssen außerdem zum dort gebundenen Offset und zur geordneten Quellenherkunft des Hints passen. Eine Spur aus einer anderen Formation bleibt eine andere Herkunft, selbst bei vollständig gleichen Vektoren.

Die Quellenreferenz eines Endpunkts umfasst die vorhandenen Bindungsfelder gemeinsam. Derselbe PCM-Hash oder dieselbe native Fensterzeit kann mehrfach verwendet werden; erst Geschichte, Arm/Owner und Manifestordinal identifizieren die konkrete Ereignisverwendung. Umgekehrt beweisen gleiche projizierte Werte keine gleichen PCM-Quellen. Ein eindeutig belegter Match auf eine bekannte andere Quelle ist ein fremder/wertkollidierender Treffer, nicht eine unbekannte Herkunft.

Im TW-Snapshot ist `retained` eine Folge von `(generation, frames)`-Paaren; im UA-Snapshot ist es `None` oder ein einzelnes solches Paar. Die Matchliste darf keine künstlich duplizierte Adresse enthalten. Ein nach `close_owner()` geleerter Endzustand ist regulärer Lebenszyklusabschluss, kein Erinnerungsverlust am früheren Hint; maßgeblich sind dessen eigene Vor-/Nachzustände.

### 3.3 Generation und Bestätigung sind verschiedene Herkunftsrollen

Die eindeutige Identität einer Spur wird als `(Lauf-/Manifestbezug, Geschichte, Arm, Owner, Speicherrolle, Generation)` gelesen. Die Zahl `1` allein ist keine Identität. Kandidaten- und Retained-Generationen haben getrennte Zähler; Geschichten und Arme ebenfalls.

Die vorhandenen `transitions` werden mit den CLOSE-Ereignissen des Manifests verknüpft. Aus `events` sind die vorangehenden vier Formationsframes zuordenbar. Für eine spätere Auswertung ist die lückenlose Kette bis zum Hint erforderlich:

- **S2-TW `TRACE_RETAINED`:** Die neu gespeicherten Frames stammen aus der gerade geschlossenen Formation. `generation` bezeichnet die neue Retained-Spur; `evicted` gegebenenfalls die entfernte Retained-Generation.
- **S2-TW `TRACE_CONFIRMED`:** Die vorhandenen Frames und die Generation bleiben erhalten. Die bestätigende neue Formation wird als Bestätigungsereignis geführt, nicht als neuer gespeicherter Ursprung. Das FIFO-Alter wird nicht erneuert.
- **S2-UA `TRACE_CANDIDATE_CREATED` / `TRACE_CANDIDATE_REPLACED`:** `candidate_generation` bindet die neue Kandidatenformation. `evicted` bezeichnet hier eine **Kandidaten**generation. Das ist keine Retained-Verdrängung und keine erfolgreiche Übernahme.
- **S2-UA `TRACE_PROMOTED`:** Die neue Retained-Generation speichert die Frames des bisherigen Kandidaten. Die gerade geschlossene Formation ist der Bestätiger; ihre Ereignisordinale müssen zur Kandidatenformation disjunkt sein. `candidate_generation` bezeichnet den übernommenen Kandidaten, `evicted` gegebenenfalls die ersetzte **Retained**-Generation.
- **S2-UA `TRACE_CONFIRMED`:** Der gespeicherte Retained-Ursprung bleibt unverändert. Eine andere, lediglich wertgleiche Quelle darf dadurch weder als gespeicherter Ursprung noch als herkunftsgleiche Wiederholung umetikettiert werden.
- Incomplete-, Overlap- oder sonstige abweichende Receipts werden als tatsächliche Aktionen geführt. Sie dürfen nicht in eine erwartete Promotion umgedeutet werden.

Ein technischer Bestätigungsreceipt beweist zunächst nur die vorhandene Wertegleichheitsregel. Die stärkere Formulierung „Bestätigung derselben gebundenen Quellenfolge“ verlangt zusätzlich die Ereignis-/Quellenkette beider Formationen. Wo diese fehlt, bleibt genau diese stärkere Aussage nicht bestimmbar. Es ist keine zusätzliche Speicherregel und kein neuer Speicherinhalt vorgesehen; diese Zuordnung entsteht ausschließlich in der späteren Auswertung vorhandener Belege.

## 4. Eindeutige Klassifikation pro Arm und Hint

Die unveränderte Entscheidung und alle Matches bleiben immer als eigene Felder erhalten. Zusätzlich erhält jeder Match genau einen Herkunftsbefund: `ZIEL_PASSEND`, `ANDERE_FORMATION`, `FALSCHER_OFFSET_ODER_QUELLENPAAR` oder `HERKUNFT_NICHT_BESTIMMBAR`. Bekannte andere Treffer werden auch bei Mehrdeutigkeit aufgelistet; daraus wird kein tatsächlich gewählter falscher Abruf gemacht.

| Primärer Auswertungsbefund | Erforderlicher Nachweis | Zielabruf C |
|---|---|---|
| **RICHTIGER_ZIELABRUF** | `TRACE_MATCH`, genau ein Match in der vollständigen Liste, vorhandene Retained-Generation und vollständige Herkunftskette; Match ist `ZIEL_PASSEND`. | wahr |
| **ANDERER_ABRUF** | `TRACE_MATCH`, genau ein vollständig belegter Match; gespeicherte Formation außerhalb der Zielmenge oder falscher Offset/Quellenpaar. Untergrund separat nennen. | falsch |
| **MEHRDEUTIG** | `ABSTAIN_AMBIGUOUS_RETAINED_TRACE` mit mindestens zwei technisch passenden Matches; alle erforderlichen Herkunftsbelege vollständig. Zielbeteiligung, andere Formationen und mehrere Offsets derselben Spur getrennt auflisten. | falsch |
| **ENTHALTUNG_OHNE_MATCH** | `ABSTAIN_NO_RETAINED_TRACE`, leere vollständige Matchliste und vollständig belegter Vorzustand. | falsch |
| **NICHT_BESTIMMBAR** | Erforderliche Belege fehlen/widersprechen sich, Matchgeneration ist nicht zuordenbar, Herkunft ist unzureichend oder technische Eingangsvoraussetzung fehlt. Ein technisch ungültiger Receipt wird als Grund genannt. | unbekannt |

`ABSTAIN_NO_RETAINED_TRACE` bedeutet im bestehenden Code **keinen passenden Retained-Offset**, nicht zwingend einen leeren Speicher. Deshalb sind zusätzlich unabhängig vom Entscheidungstext auszuweisen:

- `ziel_retained_vorhanden`: wahr/falsch/unbekannt, aus dem vollständigen Vorzustand und den gespeicherten Ursprüngen;
- `ziel_nur_kandidat`: wahr/falsch/unbekannt, nur bei belegter Abwesenheit im Retained-Bestand und Anwesenheit als Kandidat;
- bei Enthaltung: Speicher leer / andere Spuren vorhanden / Zielspur vorhanden, aber kein passender Offset;
- bei Mehrdeutigkeit: Ziel beteiligt / nur andere Treffer / Herkunft unzureichend. Auch mehrere Offsets derselben Generation bleiben nach der unveränderten Armregel mehrdeutig;
- falls relevant: technische Wertebestätigung mit abweichender gebundener Quellenherkunft.

Eine fehlende Herkunft wird nie aus `TRACE_MATCH` rekonstruiert. Bei `NICHT_BESTIMMBAR` darf der beobachtete Entscheidungstext weiterhin dokumentiert werden; er ersetzt den unbekannten Zielabrufwert nicht.

## 5. Vergleich, Erhaltung und getrennte Summen

Für einen Hint h bezeichnet `C_TW(h)` bzw. `C_UA(h)` den eben definierten Zielabrufwert. Der Vergleich verwendet denselben Hint und dieselbe vorab gebundene Zielmenge:

| C_TW | C_UA | Vergleichsbefund |
|---|---|---|
| falsch | wahr | **Zielabrufgewinn S2-UA**; Ursache zusätzlich nachweisen. |
| wahr | falsch | **Zielabrufverlust S2-UA gegenüber S2-TW**; Ursache zusätzlich nachweisen. |
| wahr | wahr | Beide rufen das gebundene Ziel richtig ab; weder relativer Gewinn noch relativer Verlust. |
| falsch | falsch | Beide ohne richtigen Zielabruf. Ihre Fehlabrufe, Mehrdeutigkeiten und Enthaltungen bleiben getrennt; keine Gleichwertigkeit der Fehlerarten behaupten. |
| mindestens einmal unbekannt | beliebig | **Vergleich nicht bestimmbar**; weder Gewinn noch Verlust als null eintragen. |

**Erhaltungsgewinn** ist ein engerer Unterfall eines Zielabrufgewinns: Zusätzlich muss derselbe gebundene Zielursprung vor der Konkurrenz in beiden Armen als Retained belegt sein, bei UA bis zum aktuellen Hint erhalten geblieben sein und bei TW durch einen zugeordneten Übergang aus dem Retained-Bestand entfernt worden sein. Eine erneute Aufnahme nach dem Verlust ist keine Erhaltung derselben alten Spur. Der Fall g1/24 adressiert diese Frage; seine Beantwortung ist offen.

Bleibt das Ziel bei TW gespeichert, ist aber mehrdeutig, kann UA einen **eindeutigen Zielabrufgewinn bei erhaltener TW-Zielspur** zeigen. Dieser wird nicht als Nachweis besserer Speichererhaltung ausgegeben. Ebenso ist ein relativer Zielabrufverlust bei UA, das das Ziel nie in Retained übernommen hat, keine Löschung einer zuvor abrufbaren UA-Erinnerung.

Ein **Verlust bereits nachgewiesener Abrufbarkeit innerhalb UA** verlangt zusätzlich einen früheren gebundenen Hint mit `C_UA=wahr`, dasselbe Ziel und eine lückenlos zugeordnete Bestandsänderung. Für g3 ist hierfür das Paar 60 → 67 vorgesehen. Fehlt der frühere richtige Abruf, kann die Bestandsersetzung dennoch belegt sein; die stärkere Aussage früherer eindeutiger Abrufbarkeit folgt nicht daraus.

Die spätere Rückgabe enthält sieben Einzelergebnisse, eine Liste belegter Gewinne, eine getrennte Liste belegter Verluste, eine Liste nicht bestimmbarer Vergleiche und die Abdeckung bestimmbarer Hinweise. Bei vollständiger Beleglage ist eine leere Gewinn- oder Verlustliste ein bestimmbares Nullergebnis dieser **neuen** Auswertungsregel. Bei fehlender/teilweiser Beleglage bleibt die jeweilige vollständige Gesamtzahl unbekannt; allenfalls die Anzahl bereits belegter Fälle wird ausdrücklich als Teilbefund angegeben. Der heutige leere Inhalt von `candidate_gains`/`candidate_losses` ist weiterhin **keine Messung** und wird nicht umgedeutet.

Keine Differenz „Gewinne minus Verluste“, kein gemeinsamer Nutzenscore, keine Verrechnung zwischen Geschichten oder Zielherkünften. Mechanismuskennzeichnungen sind Zusatzmerkmale eines Vergleichsereignisses und keine weiteren, doppelt gezählten Gewinne/Verluste.

## 6. Unterbrechung und bestätigte Konkurrenz einzeln berichten

### U1: Unterbrechung der ersten A-Aufnahme, g2/38

Gesuchte Belegkette: A aus g2-p1 wird bei Close 31 zum UA-Kandidaten `c_A`; bei Close 36 wird genau `c_A` durch den B-Kandidaten `c_B` ersetzt. Vor Hint 38 ist die ursprüngliche A-Herkunft nicht Retained und nicht mehr Kandidat; TW muss für einen relativen Verlust einen richtigen Zielabruf aus g2-p1 belegen.

Wenn diese Belege vorliegen, lautet der Mechanismus **Kandidatenverlust durch Unterbrechung vor Übernahme**. Es ist kein Verlust einer zuvor übernommenen UA-Retained-Spur. Die erst danach folgenden A-Frames 39–42 und Close 43 dürfen weder die Bewertung bei 38 verbessern noch als damalige Quelle verwendet werden. Die nachfolgende A-Aufnahme kann höchstens in einer getrennten Übergangsbeschreibung erscheinen, nicht als zusätzlicher achter Hint oder nachträglicher Abruf.

Die Zuordnung beschreibt den konkreten Softwareübergang. Sie beweist keine allgemeine statistische Kausalwirkung beliebiger Unterbrechungen und keinen nicht ausgeführten Gegenlauf ohne B.

### U2: Verlust einer einmaligen B-Erfahrung, g1/26

B aus g1-p3 wird gegebenenfalls bei Close 17 als UA-Kandidat gespeichert und bei Close 22 durch C aus g1-p4 ersetzt. Wenn TW B herkunftsrichtig abruft und UA nicht, wird der relative Verlust bei Hint 26 mit dem Untergrund **einmalige Formation vor Bestätigung ersetzt** berichtet. Das ist ein eigenes Zielereignis; es wird weder dem A-Erhaltungsgewinn bei 24 gegengerechnet noch zusätzlich als zweiter Verlust gezählt, nur weil auch hier eine Kandidatenersetzung vorliegt.

### K: Ersetzung von A durch bestätigte B-Konkurrenz, g3/67 und g3/69

Gesuchte Belegkette: Vor dem zweiten B ist die Retained-A-Herkunft g3-p1 samt `r_A` belegt; B aus g3-p3 ist der Kandidat `c_B`. Bei Close 65 bestätigt die disjunkte Formation g3-p4 diesen Kandidaten. `TRACE_PROMOTED` muss `candidate_generation=c_B`, eine neue Retained-Generation `r_B` und `evicted=r_A` ausweisen. Die gespeicherten B-Frames stammen aus dem Kandidaten p3; p4 ist dessen Bestätiger. Beide B-Formationen werden über ihre eigenen Ereignisse an die gebundene Quellenfolge zurückgeführt.

Getrennte Befunde sind:

1. **Bestandsersetzung:** A-Retained wird durch B-Retained ersetzt, mit altem und neuem Identifier, Ursprung, Bestätiger und Close 65.
2. **A-Vergleich bei 67:** relativer Zielabrufverlust nur nach Abschnitt 5; früherer richtiger UA-Abruf bei 60 als zusätzliche eigene Aussage.
3. **B-Vergleich bei 69:** beide Arme werden erneut auf den richtigen B-Ursprung geprüft. Ein richtiger B-Abruf ersetzt keinen fehlenden A-Abruf und ist bei ebenfalls richtigem TW-B-Abruf kein relativer UA-Gewinn.

Fehlt der Beleg des bestätigten B oder des entfernten A, darf der Mechanismus nicht aus den nachfolgenden Entscheidungstexten geraten werden. Belegte aktuelle Abrufbefunde und ihre eventuell unzureichend belegte Ursache sind begrifflich getrennt; fehlende technisch obligatorische Übergangsbelege machen hingegen bereits die technische Eingangsvoraussetzung ungültig.

## 7. Bestehende Widersprüche und Grenzen

**K1 – g1/24:** `EXPECTED` verlangt für TW ausdrücklich `ABSTAIN_AMBIGUOUS_RETAINED_TRACE`. Die gebundene Folge lautet jedoch A → A → B → C → H(c,d); der Text der Quellenvergleichsbindung beschreibt TW mit B/C und Enthaltung bei c,d. Bei unterscheidbaren Symbolwerten enthält B=dcba die geordneten Paare dc/cb/ba und C=abce die Paare ab/bc/ce, somit kein cd. Die unveränderte Offsetregel würde in diesem ausdrücklich bedingten Beispiel `ABSTAIN_NO_RETAINED_TRACE` liefern. Das ist ein statischer Spezifikationskonflikt, **kein Befund zu realen NU-Werten**. Wertkollisionen könnten andere Matchlisten erzeugen; sie belegen keine Quellenidentität und lösen den Spezifikationskonflikt nicht als allgemeine Vorhersage auf.

Der Entwurf bewahrt den bestehenden Erwartungstext in der Tabelle. Die spätere Erwartungserfüllung wird in einem separaten Feld gegen diesen unveränderten Text ausgewiesen. Der herkunftsgebundene Zielabruf wird unabhängig davon nach den obigen Regeln bestimmt: Ein erwarteter Text kann einen falschen Ursprung nicht richtig machen; ein unerwarteter Text kann eine belegte Herkunft nicht ändern. Eine Abweichung wird nicht durch stilles Umschreiben der Erwartung beseitigt. Vor einer späteren Implementierungsfreigabe sollte der Projektleiter diese konkrete Erwartungsbindung fachlich entscheiden.

**K2 – bereits behauptete Gain-/Loss-Ausgabe:** Die Quellenvergleichsdokumentation beschreibt teilweise schon ausgewiesene Kandidatengewinne/-verluste. Der aktuelle Evaluator liefert hierfür tatsächlich nur leere Listen und prüft Entscheidungstexte. Diese Dokumentationsaussage ist kein Nachweis einer vorhandenen Herkunftsauswertung. Der vorliegende Entwurf schließt die fachliche Definition, nicht ihre Implementierung.

**K3 – „kein Retained“ im Entscheidungstext:** Der tatsächliche Code kann `ABSTAIN_NO_RETAINED_TRACE` auch bei nichtleerem Retained-Bestand liefern. Aus diesem Text darf weder Speicherleere noch Verlust einer bestimmten Zielspur geschlossen werden.

**K4 – Wiederholung und gespeicherter Ursprung:** Wertgleiche Bestätigung ist nicht gleichbedeutend mit einer neuen gespeicherten Formation. Die gespeicherten Frames bleiben bei TW-Bestätigung bestehen; UA-Promotion übernimmt die älteren Kandidatenframes. Die Zielmengen aus `TARGETS` werden deshalb nicht aus Bestätigungstexten erweitert. Gerade die G3-A-Zielbindung bleibt nur g3-p1.

## 8. Gezielte neutrale Gegenbeispiele für eine spätere Prüfung

Die folgenden Fälle sind **nur beschriebene Prüfvorschläge**, nicht implementiert oder ausgeführt. Sie verwenden synthetische Herkunftsbelege; kein NU-Payload ist erforderlich. Bei Gegenbeispielen mit absichtlich fehlenden/gefälschten Pflichtbelegen ist deren Verwerfung das Prüfzielsoll, kein zulässiger Produktrecord.

| Vorschlag | Konstellation | Geforderte spätere Reaktion |
|---|---|---|
| **N1: Wertgleich, andere Herkunft** | Synthetische, verschiedene Quellen a/d erhalten denselben Wertvektor x, b/c denselben Wertvektor y; e erhält z, mit x, y, z verschieden. Damit sind A und B wertgleich `(x,y,y,x)`, haben aber verschiedene Quellenreihen. Bei g1/26 kann UA auf den gespeicherten A-Ursprung p1 an Offset 0 mit `TRACE_MATCH` antworten; Ziel ist ausschließlich B/p3. B wurde im Wertepfad nur als Bestätigung von A behandelt. | `ANDERER_ABRUF`, nicht richtiger B-Abruf. Den gespeicherten Ursprung p1 nicht zu p3 umetikettieren. B nicht ohne entsprechenden Receipt als erstellten/verdrängten Kandidaten ausweisen. Dies ist ein bedingtes synthetisches Beispiel, keine Aussage über NU-Werte. |
| **N2: Ziel vorhanden, aber mehrdeutig** | Beispielsweise synthetisch bei g3/60: b und d sind wertgleich, a/b/c sonst verschieden. A besitzt den richtigen cd-Match an Offset 2; B kann zusätzlich cb an Offset 1 wertgleich treffen. TW kann dadurch Ziel und andere Spur matchen, UA nur die Retained-A-Spur. Zusätzliche Variante: zwei Offsets derselben Generation. | `MEHRDEUTIG` bei mehreren Matches, Zielbeteiligung und zusätzliche Matches sichtbar. Kein Herausfiltern zum Erfolg. Hat UA allein einen korrekten eindeutigen Abruf, ist ein relativer Zielabrufgewinn möglich, aber kein Speicher-Erhaltungsgewinn bei weiterhin gespeicherter TW-Zielspur. |
| **N3: Herkunft fehlt trotz Erfolgstext** | `TRACE_MATCH` und Werte bleiben erhalten, aber die gespeicherten Frameordinale sind nicht auf vollständige Formations-/Quellenereignisse rückführbar. | Zielabruf und Vergleich `NICHT_BESTIMMBAR`; keine Nullgewinne/-verluste. Ist die technische Integrität verletzt, zusätzlich technische Nichtauswertbarkeit. |
| **N4: Generation aus falschem Namensraum** | Ein Match oder `evicted=1` wird mit Generation 1 einer anderen Geschichte, eines anderen Owners oder mit Kandidat 1 statt Retained 1 verknüpft. | Zuordnung zurückweisen; keine Bestätigung eines richtigen Abrufs oder einer Retained-Ersetzung allein anhand der Zahl. |
| **N5: Spätes A repariert den früheren Hint nicht** | Bei g2 ist p1 vor Hint 38 als Kandidat durch B ersetzt; p3 liefert erst danach dieselben A-Werte. | Keine Rückprojektion von p3 auf Hint 38. Ein gegebenenfalls belegter Vergleichsverlust bleibt der Herkunft p1 und dem Mechanismus vor Übernahme zugeordnet; keine Behauptung zuvor erfolgreicher UA-Retention. |
| **N6: A-Verlust und B-Treffer bleiben getrennt** | Vollständig belegte Konkurrenzpromotion bei g3/65; anschließend korrekter TW-Abruf ohne korrekten UA-Abruf bei 67, bei 69 korrekter B-Abruf in beiden Armen. | Ein eigener bedingter A-Verlustfall und ein eigener B-Befund; kein Saldo, kein kompensierender UA-Gewinn für B und keine doppelte Zählung durch das Mechanismusmerkmal. |

## 9. Vorgeschlagene Rückgabe einer späteren Auswertung

Pro Hint: Schlüssel und Targetbindung; technische Zulässigkeit; beide unveränderten Entscheidungstexte; alle Matchadressen; für jede Adresse gespeicherte Formation mit vier Ordinalen, Quellenbezüge, Generation/Owner und Offset; getrennte Ursprung-/Bestätigungsbezüge; Zielbestand Retained/Kandidat; primäre Armklassifikation samt Belegstellen; getrennte Gewinn-/Verlustbestimmung; Mechanismusbelege; unverändertes Erwartungspaar und dessen Erfüllung; ausdrücklich benannte unbestimmbare Felder mit Grund.

Jede Aussage referenziert konkrete Recordpfade (Geschichte, Hintordinal, Snapshotrolle, Matchadresse, Ereignis- und Übergangsordinal) sowie den übergeordneten Record-/Manifestbezug. Ein freier A/B/C-Name oder eine Wertedigest-Gleichheit ist kein Herkunftsbeleg. Fehlende Pflichtfelder werden nicht aus dem erwarteten Ergebnis ergänzt.

Über alle sieben Hints: getrennte Gewinn-, Verlust-, Fehlabruf-, Mehrdeutigkeits-, Enthaltungs- und Unbestimmbarkeitslisten mit Abdeckung. U1, U2 und Konkurrenzersetzung K sind jeweils gesondert auffindbar. Keine historische Liste wird nachträglich befüllt.

## 10. Nächster fachlicher Schritt

Der Entwurf ist vollständig zur fachlichen Prüfung vorbereitet. Empfohlen ist die Entscheidung über diese Herkunfts- und Vergleichsregeln einschließlich des expliziten Konflikts g1/24. Erst ein anschließender eigener Auftrag sollte die eng begrenzte Auswertungsimplementierung und die beschriebenen neutralen Gegenproben freigeben. Die unabhängige technische V9-Abnahme bleibt ein separater Vorgang; aus diesem Dokument folgt weder eine Quellenproduktion noch eine Öffnung des Realeinstiegs.

Gelesene Dateistände und Hashes: [readset.json](readset.json). Es wurden ausschließlich dieser Entwurf und seine statischen Dateinachweise neu angelegt.
