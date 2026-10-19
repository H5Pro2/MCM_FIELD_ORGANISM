# Hinweisabhängige Erfahrungsnutzung: kapazitätsbewusster Konzeptentwurf

2026-10-04. Status: FACHLICH_ANGENOMMEN; Kontrollaussage präzisiert.
Verbindliche Spezifikation: [HX1-Prüfvertrag](S2UC_HX1_PRUEFVERTRAG_20261004.md).
Auftrag: nächste eigenständige Forschungsfrage nach dem abgenommenen ULZ1-Abschluss.
Keine Implementierung, Quellenerzeugung, Qualifikation oder Versuchsausführung.
Keine Speichererweiterung; U bleibt unverändert, A1/K1 bleiben aus.

## 1. Frage und vorläufiges Urteil zur Machbarkeit

Kann der bestehende Gesamtpfad anhand verschiedener beobachtbarer
Zweiframehinweise unterschiedliche Fortsetzungen nutzen, obwohl deren globale
Häufigkeiten gleich sind? Untersucht werden reguläre Aufnahme, selektiver Abruf
und Fehlererfahrung gemeinsam; nicht ausschließlich der Zusatznutzen der EMA.

**Begrenzte Lerngelegenheiten sind architektonisch möglich. Vier dauerhaft
verfügbare Hinweis-Fortsetzungs-Spuren sind es nicht.** Zwei Retained-Spuren
und ein Kandidat sind abrufbar. Ein Vierframeblock im Aufbau ist keine weitere
abrufbare Spur. Zwei Hauptfortsetzungen können regulär bestätigt und bewertet
werden; Minderheitsvarianten können Kandidaten ersetzen und Retained-Spuren
verdrängen. Der Entwurf untersucht genau diese begrenzte Architektur, ohne
unverfügbare Alternativen einzuspeisen oder Verluste aus der Bewertung zu nehmen.

## 2. Beobachtbare Eingänge und entgegengesetzte Fortsetzungen

Wie in der bisherigen synthetischen Familie sei V(x)[j]=x+j/4096,
j=0,…,47. Alle folgenden Namen dienen ausschließlich der externen Beschreibung.

| Größe | Beobachtbarer Vektor bzw. Paar |
| --- | --- |
| Hinweis X | (V(1/8), V(1/2)) |
| Hinweis Y | (V(7/8), V(1/2)) |
| Fortsetzung A | V(1/4) |
| Fortsetzung B | V(3/4) |
| Schlussframe R | V(1/16) |

Ein regulärer Vierframeblock lautet [Hinweisframe 1, Hinweisframe 2, Fortsetzung, R].
Die beiden Hinweise unterscheiden sich im ersten Frame. Ihr zweiter Frame ist
identisch; Persistenz kann deshalb den Hinweis nicht bereits unterscheiden.
Die vier vollständigen Blocktypen sind XA, XB, YA und YB.

Die Komponentensteigung von V ist immer 1/4096. Ein Faktor 1/2 oder 2 verändert
diese Steigung und kann keinen anderen dieser Vektoren exakt treffen.
Damit gibt es keine unbeabsichtigte Gleichsetzung der Hinweise durch die
vorhandene Faktorsuche. U akzeptiert ohnehin nur Faktorenliste [1.0].

Bei den beiden primären Hinweisabfragen passen nur Offset-0-Fenster:
Offset 1 beginnt mit V(1/2), Offset 2 mit A oder B, niemals mit V(1/8)
oder V(7/8). Zwei Hinweis-Fortsetzungs-Beziehungen lassen sich hier also
nicht verdeckt in verschiedenen Offsets einer einzigen Spur unterbringen.

### Bedingung D: Hinweisabhängigkeit

| Hinweis | Häufigkeit | A gegeben Hinweis | B gegeben Hinweis |
| --- | ---: | ---: | ---: |
| X | 1/2 | 3/4 | 1/4 |
| Y | 1/2 | 1/4 | 3/4 |
| global | 1 | 1/2 | 1/2 |

Für die Hälfte der unabhängigen Geschichten wird die Zuordnung der dominanten
Fortsetzungen zu X/Y vertauscht. Diese Gegenorientierung ist Quellenkonstruktion,
kein Eingang oder Parameter von U. Es wird keine Ausgabewahl vorprogrammiert.

Konkreter Umfangsvorschlag für einen späteren Vertrag: 32 unabhängige
Geschichtenpaare mit je 256 Vierframeblöcken, ohne Vorwärmpräfix. Je Geschichte
liegen exakt 128 A und 128 B sowie 128 X und 128 Y vor. In Orientierung X→A
werden die vier Typen 96/32/32/96-mal beobachtet.

Die Quellen werden später vorab und unabhängig von Systemergebnissen bestimmt:
zunächst eine zufällige Reihenfolge von 128 A und 128 B; darauf gleichverteilte
Auswahl von 96 der A-Positionen und 32 der B-Positionen für X. Restpositionen
erhalten Y. In der Gegenorientierung werden die beiden Quoten vertauscht.
Es gibt keine bevorzugten Wiederholungsblöcke, geschützten Einführungsphasen
oder nachträgliche Auswahl günstiger Geschichten.

### Bedingung N: unabhängige Hinweise bei identischer Fortsetzungsfolge

N übernimmt **dieselbe vollständige A/B-Folge an denselben Blockpositionen**
wie die zugehörige D-Geschichte. Eine davon unabhängig gezogene, gleichverteilte
Permutation von 128 X und 128 Y liefert die Hinweise. Globale Fortsetzungs-
und Hinweishäufigkeiten sind damit exakt gleich, die Hinweisfolge ist unter
der Quellenverteilung unabhängig von der gesamten Fortsetzungsfolge.

Die erwartete Kreuztabelle ist 64/64/64/64, die realisierte darf zufällig davon
abweichen. Keine Nachauswahl auf exakt diese Tabelle: Eine solche Auswahl
würde Hinweise wieder an die beobachteten Fortsetzungen binden. Die realisierte
Kreuztabelle wird vollständig berichtet. Insbesondere wird ein zufälliger
Zusammenhang in einer endlichen Kontrollgeschichte nicht als Regel eingeführt.

Das Ziehen mit festen Gesamthäufigkeiten ist kein zeitlich unabhängiger
Bernoulli-Prozess: Restquoten erzeugen Abhängigkeiten innerhalb der A/B-Folge.
Diese Folge ist jedoch zwischen D/N identisch. In N liefern die unabhängigen
Hinweise auch nach gegebenen bisherigen A/B-Beobachtungen keine zusätzliche
Information über die nächste Fortsetzung. Quellenquoten oder Restzähler gehen
nicht an U oder den Vergleich. Spätere Seeds, Permutationsverfahren und
Gegenorientierungszuordnung sind vor jeder Materialisierung zu binden.

### Eingangsgrenze

U erhält ausschließlich die regulären 48-dimensionalen Frames und die bereits
erforderlichen, fortlaufenden technischen Scope-/Zeitangaben. Keine X/Y-, A/B-,
D/N-Labels, Wahrscheinlichkeiten, Kontingenztabellen, Blocktypcodes oder
aus dem Versuchsplan gebildeten Segmentnamen. Segmentnamen bleiben die normalen
fortlaufenden technischen IDs. Keine Domänenumschaltung oder Reset nach Hinweis.
Alle vier Frames jedes Blocks durchlaufen den bestehenden Aufnahmeweg.

## 3. Analytischer Speicherbedarf und regulärer Lebenszyklus

| Bestandteil | Originalframes | Abrufbar für eine neue Hinweisentscheidung? |
| --- | ---: | --- |
| zwei Retained-Spuren | höchstens 8 | ja |
| ein Kandidat | höchstens 4 | ja, auch vor Promotion |
| aktueller Vierframeblock im Aufbau | höchstens 4 | nein |
| aktuelles Hinweispaar | höchstens 2 | Eingang, keine zusätzliche Altspur |

Der konservative bestehende Rahmen beträgt 16 Trace-Frames plus 2 Hinweisframes.
Aliase werden nicht als neue Originale gezählt. Für eine Fortsetzungsentscheidung
nach dem ersten Paar des Blocks gibt es bei voller Altbelegung 12 alte Frames
und 2 neue Hinweisframes; beim Eintreffen des Zieles kommt ein neuer Frame hinzu.
Die später vervollständigte Aufnahme kann 16 Trace-Frames belegen, bevor der
Segmentabschluss bestätigt, ersetzt oder promoviert. Ausgabereferenzen und
eingefrorene Feedbackreferenzen erzeugen keine zusätzlichen vollständigen Spuren.
Es bleiben höchstens zwei Ausgabeslots; die bestehende 416-Byte-Fehlerbank hat
sechs Zellen, hier höchstens drei passende Offset-0-Hypothesen je Fortsetzungsziel.
Dies ist eine analytische Belegungsbeschreibung, kein neu gemessener Heap-Peak.

**Vier Varianten:** XA, XB, YA und YB benötigen vier unterschiedliche
Vierframeoriginale, also 16 gleichzeitig abrufbare Frames. Tatsächlich sind
höchstens drei solche Originale bzw. 12 Frames abrufbar. Der Forming-Bereich
kann die vierte Spur nicht dauerhaft ergänzen. Zusätzliche Fehlerzellen allein
würden das fehlende Original ebenfalls nicht ersetzen.

**Minimaler Erfahrungszyklus für eine Beziehung:**

1. Erste vollständige Beobachtung erzeugt am Blockende einen kalten Kandidaten.
   Aus der eigenen erstmaligen Fortsetzung wird rückwirkend keine vorab
   existierende Prognose oder bewertete Zelle konstruiert.
2. Beim späteren gleichen Hinweis kann dieser Kandidat bereits abgerufen
   werden. Bis zum eigenen gültigen Erstfeedback bleibt U dort kalt und
   verwendet gegebenenfalls Persistenz. Das Feedback aktualisiert sämtliche
   berechtigten, noch lebenden Hypothesen, nicht nur die gewählte.
3. Wiederholt sich auch die vollständige Vierframesequenz, promoviert der
   Kandidat regulär. Das kurz zuvor erhaltene Fehlerpaar wird mitgenommen.
4. Bei einer weiteren Hinweisbeobachtung kann die nun warme Erfahrung vor
   dem Ziel ausgewählt werden. Auch ein warmer, noch nicht promovierter
   Kandidat wäre nutzbar, falls er bis dahin erhalten bleibt.

Drei passende Hinweisgelegenheiten genügen somit als **Existenzbeispiel** für
Aufnahme → Erstfeedback → Nutzung. Sie sind keine Garantie für die Quelle.
Eine vollständige Wiederholung ist für Promotion nötig, nicht für jedes Feedback.
Eine andere neue vollständige Sequenz kann den Kandidaten vorher ersetzen;
Wiederholung einer vorhandenen Retained-Spur ersetzt ihn dagegen nicht.

### Symbolischer Nachweis einer erreichbaren Lerngelegenheit

Die Folge XA, XA, XA, YB, YB, YB benötigt keine Sonderaufnahme:

| Block | Relevanter Vorgang |
| ---: | --- |
| 1 | XA entsteht kalt als Kandidat |
| 2 | XA erhält (ec,ep)=(0,1/4), promoviert am Ende |
| 3 | warmer XA-Abruf kann A wählen; erneute Bestätigung |
| 4 | YB entsteht als Kandidat, XA bleibt erhalten |
| 5 | YB erhält (0,1/4), promoviert in den zweiten Retained-Platz |
| 6 | warmer YB-Abruf kann B wählen; XA bleibt vorhanden |

Dies ist eine von Hand hergeleitete mögliche Zustandsfolge, keine ausgeführte
Quelle und kein vorgeschlagenes Vorwärmpräfix. In D und N können solche
Teilfolgen auftreten. Ihr Auftreten oder langfristiges Überleben wird nicht
erzwungen. Damit ist die Lerngelegenheit möglich, ihre ausreichende Häufigkeit
unter der geplanten Quelle aber nicht analytisch nachgewiesen.

### Konkrete Verfügbarkeitsgrenze

Sind XA und YB Retained, kann XB als dritter Typ Kandidat sein. Eine neue
YA-Beobachtung ersetzt diesen Kandidaten, sofern YA nicht schon Retained ist.
Eine vollständige XB-Wiederholung kann ihn stattdessen promovieren und die
nach regulärer Bestätigungsaktualität älteste Retained-Spur verdrängen –
gegebenenfalls gerade XA oder YB. Weder Hauptfortsetzungen noch Hinweise
erhalten einen reservierten Platz. Mit dem verlorenen Original verschwinden
seine Fehlerzellen; ein später neu aufgenommenes Original beginnt kalt.

Die Architektur reicht somit **nicht** für den Anspruch, jederzeit beide
Alternativen beider Hinweise vollständig gelernt vorzuhalten. Dafür wäre
ein anderer Auftrag erforderlich. Die hier vorgeschlagene Frage bleibt
enger: erzielbarer Hinweisnutzen unter den tatsächlichen Verlusten.

## 4. Hinweisunabhängiger lernender Vergleich

Vergleich G ist ein globaler, fortlaufender Mittelwert der bereits gesehenen
Fortsetzungsvektoren: vor der k-ten Fortsetzung gibt er den Mittelwert der
ersten k−1 Fortsetzungen aus; nach dem Ziel aktualisiert er ihn komponentenweise
mit m←m+(y−m)/k. Ohne Vorgeschichte verwendet er V(1/2), also den gemeinsamen
aktuellen zweiten Hinweisframe. Es gibt keine eingeführten A/B-Prototypen,
Hinweisklassen, bedingten Tabellen oder Kenntnis der Quellenquoten.

Die Schnittstelle legt für alle Bewertungen dieselben vorab bestimmten
Zielpositionen fest. G nutzt nur diese technische Vierframephase, bisherige
Fortsetzungswerte und einen Zähler; den unterscheidenden ersten Hinweisframe
sieht sein Lernzustand nicht. Auf den übrigen regulären Vorhersagepositionen
verwendet G Persistenz und verändert seinen Mittelwert nicht. Diese Phase ist
ein ausdrücklich offengelegter Vorteil des einfachen Vergleichs, kein
zusätzlicher Eingang in U. Beide starten pro Geschichte frisch.

G benötigt einen 48-Komponenten-Mittelwert und einen Zähler, keine archivierten
Originalspuren. Seine Ausgabe ist ein synthetischer Vektor, bei U eine
Originalreferenz oder Persistenz. Es wird daher kein identischer Ressourcen-
oder Architekturnachweis behauptet. Ein späterer Vertrag muss G separat
begrenzen und seine kausale Aktualisierung prüfen.

Da D/N dieselbe Zielwertfolge besitzen, hat G an jeder Fortsetzungsposition
beider Bedingungen exakt denselben Vorzustand, dieselbe Ausgabe und denselben
Fehler. Ein rein globaler Häufigkeitsvorteil kann den gepaarten D/N-Unterschied
dieses Vergleichs deshalb nicht erklären.

Zusätzlich wird die feste Persistenz P ausgewertet. Das verhindert, dass
ein Vorteil allein aus einem schwachen globalen Mittelwertvergleich stammt:
P liegt exakt zwischen A/B und hat auf jeder Fortsetzung MAE=1/4.
Ein hypothetischer Prädiktor mit Kenntnis der dominanten Fortsetzung hätte
in D marginal MAE=(1/4)*(1/2)=1/8. Diese Zahl ist nur analytische Orientierung,
kein erreichter U-Wert und keine vierte, dem System zugeführte Vergleichspolicy.
In N beträgt der Persistenzfehler weiterhin exakt 1/4. Dies ist keine allgemeine
optimale erwartete Fehlergrenze: Bei festen Gesamtquoten können vergangene
Beobachtungen Informationen über verbleibende Fortsetzungen liefern.
Die unabhängig gezogenen Hinweise enthalten keine zusätzliche Information.
Deshalb bleibt der gepaarte Kontrollkontrast erforderlich.

## 5. Vollständige Bewertungsmengen und Verfügbarkeit

Für N_B=256 Blöcke und 1024 Frames gelten, ohne Vorwärmausschluss:

- Q={4b−1 | b=1,…,256}: sämtliche 256 Fortsetzungsziele, einschließlich
  erster, kalter, fehlender, mehrdeutiger und verlustnaher Gelegenheiten.
- G_all={3,5,…,1023}: sämtliche 511 tatsächlich beobachteten regulären
  Vorhersageziele. Q umfasst davon 256; die restlichen 255 bilden das Gerüst.
- Q_X und Q_Y: disjunkte, vollständige Hinweisaufteilung, je 128 Ziele.
  Sie werden zusätzlich nach Gegenorientierung berichtet.
- Ziel 1025 nach dem letzten vollständigen Paar ist mangels Beobachtung
  rechtszensiert; keine erfundene Rückmeldung. Alle tatsächlich beobachteten
  Ziele verbleiben in den Nennern. Kein abgebrochener Fall wird ersetzt.

Gerüstabfragen [A,R] bzw. [B,R] passen nur an Offset 2 und haben dort keinen
Nachfolger. Im entworfenen Quellenalphabet nutzt U deshalb auf dem Gerüst
Persistenz wie G/P. Gerüstfehler können wegen der verschiedenen nächsten
Hinweise zwischen D/N unterschiedlich sein; sie dürfen den Hinweisnutzen
nicht verwässern oder vortäuschen. Primär ist Q, G_all bleibt vollständig sichtbar.

Pro Bedingung und Vergleich: MAE, gepaarte Fehlerdifferenz, Zahl besser/
schlechter/gleich, Gewinn-/Schadenssumme, maximaler Einzelschaden und kumulierter
Verlauf. Keine Mittelung nur erfolgreicher oder warmer Entscheidungen.

### Vor der Entscheidung bestimmte Diagnoseklassen

Jedes Q-Ziel wird genau einer Klasse zugeordnet:

| Klasse | Vorzustand | Einordnung |
| --- | --- | --- |
| V0 | keine passende berechtigte Originalspur | keine abrufbare Lerngelegenheit |
| V1 | passende Originale, aber alle Fehlerzellen kalt | noch kein nutzbares gültiges Feedback |
| V2 | mindestens eine warme Hypothese, U gibt P aus | Bewertung ohne eindeutigen negativen Vorteil |
| V3 | mindestens eine warme Hypothese, U wählt Kontext | vorhandene Erfahrung wird ausgewählt |

Zusätzlich: welche A/B-Fortsetzungen vorhanden bzw. warm sind; Zahl und Alter
gültiger Feedbacks; Kandidat/Retained; Wahlgrund; Promotions-/Verlustereignisse;
eingefrorene gegenüber tatsächlich gültigen Feedbacktickets. In D wird extern
gezählt, ob die gemäß Quellenplan dominante Fortsetzung vor dem Ziel fehlt,
kalt oder warm ist. N hat keine ausgezeichnete dominante Fortsetzung.

Die vollständigen Fehlerbeiträge dieser Klassen müssen sich zur Gesamtbilanz
addieren. Ein warmer Bestand ohne Vorteil kann auf unzureichende Bewertung
hinweisen, ist aber nicht allein ein Beweis dafür: berechtigte Unsicherheit,
wenige Rückmeldungen oder eine überraschende Fortsetzung bleiben möglich.
Ebenso begründet Nähe zur Verdrängung keinen isolierten Verdrängungseffekt.
Verfügbarkeitsklassen sind durch den Quellenverlauf beeinflusst und dienen
der Diagnose, nicht nachträglich ausgewählten bestätigenden Untergruppentests.

## 6. Falsifizierbare Erwartung und Urteil

Erwartet wird auf dem **vollständigen Q** ein U-Vorteil in D gegenüber sowohl
G als auch P sowie ein stärkerer U/G-Vorteil in D als in N. Mit
d_D=MAE(U,D)−MAE(G,D), d_N entsprechend und p_D=MAE(U,D)−MAE(P,D):

1. E[d_D]<0;
2. E[p_D]<0;
3. E[d_D−d_N]<0.

Alle drei Bedingungen gehören zum geplanten Nachweis; ein bloß nicht
signifikanter Vorteil in N ist kein Null- oder Gleichwertigkeitsnachweis.
Der gesamte Hinweisnutzen darf nicht durch einen nachträglich ausgewählten
Hinweis, eine Gegenorientierung oder nur warme Ziele begründet werden.
Die Aufteilungen zeigen mögliche Einseitigkeit; ihre eigenständige Bestätigung
wird ohne gesonderte Vorabbindung nicht behauptet.

Die unabhängige Einheit ist das Geschichtenpaar; D/N und U/G/P innerhalb
desselben Paares sind abhängig. Ein späterer Prüfvertrag muss Unsicherheits-
verfahren, gemeinsame Fehlerkontrolle für die drei Kontraste, technische
Grenzen, Seeds und Abbruchregeln vorab festlegen. Dieser Konzeptentwurf
enthält keine Leistungs- oder Powerbehauptung für die vorgeschlagenen 32 Paare.

Bleibt eine notwendige Bedingung unbestätigt, ist der angestrebte Nachweis
nicht erbracht. V0/V1-Anteile benennen dann fehlende Verfügbarkeit bzw.
fehlendes Feedback; V2/V3 mit ihren vollständigen Fehlerbeiträgen zeigen,
was aus tatsächlich vorhandener Erfahrung erreicht wurde. Ein klarer Nachteil
und bloß unzureichende statistische Präzision sind getrennt zu berichten.

Erfolg würde begrenzte hinweisabhängige Nutzung aufgenommener Erfahrung unter
dem regulären Lebenszyklus belegen. Kein Nachweis für Semantik, Clusterbildung,
Generalisierung auf neue Hinweise, Feld-Memory, biologisches Lernen oder einen
Vorteil gegenüber allen einfachen hinweisabhängigen Lernverfahren. Ein globaler
Vergleich isoliert außerdem nicht den Beitrag der EMA gegenüber dem bereits
vorhandenen selektiven Abruf; dafür wäre eine andere Forschungsfrage erforderlich.

## 7. Belegstellen und nächster Schritt

Statische Grundlage, ausschließlich gelesen:

- `tools/_s2uc_four_arm.py:27`: vollständige Bestätigung, Kandidatenersetzung,
  Promotion und höchstens zwei Retained-Spuren; `:86`/`:93`: 16-Frame-Tracebudget.
- `tools/_s2uc_perception_recency.py:10`: Aktualisierung der Retained-Reihenfolge
  nur durch spätere vollständige Wiederbeobachtung.
- `tools/_s2uc_factor_hint.py:20`: Suche in Retained und Kandidat, drei Offsets.
- `tools/_s2uc_pair_context_adapter.py:41`: Hinweissuche vor regulärer Aufnahme
  desselben Paares; Vierframe-Segmentierung bleibt erhalten.
- `tools/_s2uc_multi_error.py:103`: kalte/warme Bewertung, Faktorenberechtigung,
  eindeutiger negativer Vorteil, sonst Persistenz.
- `tools/_s2uc_multi_error.py:179`: gültiges Feedback aller berechtigten
  Hypothesen; `:97` und `:267`: Zellverlust bzw. Promotionsmitnahme.

Empfehlung: Diesen Entwurf als eng begrenzte **Kapazitäts- und Hinweisfrage**
fachlich prüfen. Der nächste Auftrag sollte einen vorab gebundenen Prüfvertrag
für genau D/N und U/G/P ausarbeiten, sofern der Projektleiter den engeren
Anspruch akzeptiert. Die nicht erfüllbare Alternative „vier jederzeit gelernte
Spuren“ wird ausdrücklich nicht vorausgesetzt. Bis dahin keine Umsetzung,
Quellenmaterialisierung oder Ausführung. ULZ1 bleibt abgeschlossen.
