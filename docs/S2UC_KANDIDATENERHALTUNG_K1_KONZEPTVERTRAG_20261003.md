# K1: genau ein zusätzlicher Viererblock Kandidatenerhaltung

Status: geschlossener Konzeptvorschlag zur Abnahme. Keine Implementierung,
Materialisierung, Qualifikation oder Ausführung freigegeben oder vorgenommen.
Grundlage ist die abgenommene T1-Ursachenanalyse, nicht ein positiver Transferbeleg.
Die bisherige U-Variante bleibt eingefrorene Vergleichsgrundlage; Defaults bleiben aus.

## Eine Änderung und ihre Begründung

K1 ersetzt ausschließlich die bisherige sofortige Ersetzung eines Kandidaten
am nächsten nicht passenden vollständigen Viererblock durch eine feste,
nicht verlängerbare Erhaltungsfrist bis zum zweiten Folgeblockabschluss.
Ein Kandidat kann dadurch genau einen zusätzlichen vollständigen Block überleben.
Die folgende Fristbehandlung bei einer Bestätigung einer bereits bestätigten Spur
gehört zu derselben Kandidatenregel; es gibt keine zweite Optimierungsvariante.

Die Dauer wird hier auf zwei Folgeabschlüsse festgelegt, weil dies die kleinste
positive Verlängerung der bisherigen Ersetzungsgranularität um einen Viererblock
ist. Sie ist keine aus T1 geschätzte Wiederkehrdauer und kein Optimierungsergebnis.
Keine Suche über Dauern, keine spätere Verlängerung bei günstigen Fehlern, Treffern
oder erwarteter Wiederkehr. Die 133 beobachteten Verluste begründen die Frage,
beweisen aber weder diese Dauer noch einen Nutzen von K1.

## Vollständige Zustandsregel

Eingaben am vorhandenen Segmentabschluss: der gerade gebildete Block F, die
höchstens zwei bestätigten Originalspuren R, der höchstens eine Kandidat C und
deren bereits vorhandene Frameordinalen. Kein Zugriff auf Quelle, Modus, Phase,
Modalwert, zukünftige Daten, Archivdiagnose, Vorhersagefehler oder Abrufhäufigkeit.
Die bestehende zeitliche Ordnung und die Vierersegmentierung bleiben unverändert.

Für einen vorhandenen Kandidaten sei c die Ordinale seines letzten Originalframes,
für einen vollständigen eingehenden Block f dessen letzte Ordinale. Die Frist ist
abgelaufen, sobald f−c >= 8. Es wird keine absolute Frist gespeichert. Im regulären
lückenlosen Pfad liegen die beiden Folgeabschlüsse bei c+4 und c+8. Bezug sind
Originalordinalen im selben Scope, nicht Uhrzeit, Prognoseziele oder Nutzungszahlen.
Bestätigungen anderer Spuren und Abrufe setzen c nicht zurück.

Die Reihenfolge ist verbindlich; genau der erste zutreffende Zweig wird ausgeführt:

| Priorität | Bedingung | Aktion |
| --- | --- | --- |
| 1 | F ist unvollständig | F nach bestehender Regel verwerfen. Keine neue Spur und keine Promotion. Beim regulären Storyende räumt der bestehende Abschluss anschließend alles auf. |
| 2 | F stimmt exakt mit einer bestätigten Spur überein | Bestehende Bestätigung und Aktualisierung ihrer Reihenfolge unverändert ausführen; keine neuen Originalframes behalten. Falls C existiert und f−c >= 8, C zusätzlich freigeben; andernfalls C unverändert lassen. |
| 3 | Keine bestätigte Übereinstimmung; F stimmt exakt mit C überein und Originalordinalen sind disjunkt | Bestehende Promotion unverändert ausführen, auch genau am Fristende: Originalframes von C übernehmen, neue bestätigte Generation vergeben, gegebenenfalls älteste bestätigte Spur nach bisheriger Regel verdrängen, C leeren. F liefert keinen zweiten Originalsatz. |
| 4 | Wie 3, aber die erforderliche Disjunktheit fehlt | Keine Promotion. Bestehende Überlappungsablehnung; bei abgelaufener Frist C freigeben, sonst C erhalten. Im regulären lückenlosen Aufnahmepfad tritt diese Überlappung nicht auf. |
| 5 | Keine passende bestätigte Spur; C fehlt | F als neuen Kandidaten mit neuer Kandidatengeneration übernehmen. |
| 6 | C vorhanden, F passt nicht, f−c < 8 | C einschließlich vorhandener Fehlerzellen erhalten; F vollständig verwerfen. Keine Kandidatengeneration vergeben, keine neue Spur vormerken. |
| 7 | C vorhanden, F passt nicht, f−c >= 8 | C freigeben und F als neuen Kandidaten mit neuer Kandidatengeneration übernehmen. Alte Kandidatenfehlerzellen nach bestehender Lebendigkeitsregel entfernen. |

Eine Übereinstimmung mit einer bestätigten Spur hat weiterhin Vorrang vor einer
Kandidatenübereinstimmung. Der Fristtest ändert keine Gleichheits-, Disjunktheits-,
Bestätigungs-, Retained-Recency- oder Promotionsregel. Er beendet nur das Recht
des Kandidaten, den Kandidatenplatz weiter zu belegen. Keine Interpolation,
Ähnlichkeitssuche, Zusammenführung von Spuren oder Änderung der Spurwerte.

Für den späteren Abschlussrückgabewert gelten weiterhin die vorhandenen Felder
action, generation, candidate_generation und evicted. Beim reinen Erhalten heißt
action=TRACE_CANDIDATE_HELD, generation=None, candidate_generation=unveränderte
Generation, evicted=None. Anlage, Ersetzung und Promotion behalten ihre bisherigen
Ereignistypen und Bedeutungen. Bei Bestätigung mit Fristfreigabe bleibt der
Bestätigungs-/Recency-Ereignistyp erhalten, candidate_generation wird None;
evicted bezeichnet weiterhin ausschließlich eine verdrängte bestätigte Spur.
Kandidatenfreigabe ist aus Vor-/Nachbestand abzulesen und wird nicht als Retained-
Verdrängung gemeldet. Im Überlappungsablehnungsfall bleibt der Ablehnungstyp erhalten,
candidate_generation bezeichnet den verbleibenden Kandidaten oder None nach Ablauf.
Keine zusätzliche persistente Ereignisliste im System.

Jeder vollständige Folgeblock zählt zeitlich, auch eine Bestätigung einer anderen
Spur. Deshalb kann C bei fortlaufender Aufnahme spätestens am zweiten Folgeabschluss
nicht mehr als derselbe Kandidat verbleiben: Er wird promoviert, freigegeben oder
ersetzt. Eine Promotion kann ihn regulär in eine bestätigte Spur überführen;
das ist kein fortbestehender Kandidatenplatz. Ohne weitere Eingaben vergeht keine
Systemerfahrung; Storyende und Scopewechsel räumen wie bisher auf. Ungültige
Ordinale, Scopewechsel oder Ordnungsverletzung führen zum bestehenden Fehlerabschluss,
nicht zu einer Verlängerung oder einer Rekonstruktion gelöschter Spuren.

## Preis und Eindeutigkeit

Beim Zwischenabschluss c+4 wird eine neue, nicht passende Viererspur nicht als
Kandidat gespeichert. Sie steht danach weder für Abruf noch für eigene spätere
Promotion zur Verfügung, es sei denn, die gleiche Wahrnehmung entsteht später
erneut im normalen Eingang. Aus Archiv, Replayquelle oder Log wird sie nie restauriert.
Es gibt keinen Warteslot. Das ist der ausdrückliche Preis für die längere
Erhaltung des alten Kandidaten. Hinweise aus dem eingehenden Block wurden vor
seiner Aufnahme wie bisher verarbeitet; dies macht den ganzen Block nicht zum
gespeicherten Kandidaten. Die bekannte Schlechterstellung bei benötigter neuer
Erfahrung wird nicht aus der Auswertung entfernt.

Eine gleichzeitige Garantie, den alten Kandidaten länger zu behalten UND jeden
neuen abweichenden Block sofort als Kandidat verfügbar zu machen, wäre mit genau
einem Kandidatenplatz unvereinbar. K1 beansprucht diese Garantie ausdrücklich nicht.
Es wird keine zweite Spur unter einem anderen Namen gespeichert.

Kandidatengenerationen steigen ausschließlich bei tatsächlicher Kandidatenanlage
oder Ersetzung, nie beim Verwerfen eines neuen Blocks. Eine bereits vergebene
Generation wird nicht wiederverwendet. Promotion vergibt wie bisher eine neue
bestätigte Generation und übernimmt die ursprünglichen Frameidentitäten.
Freigabe durch Fristablauf erzeugt keine neue Generation. Bestehende Generationen-
und Ordinalgrenzen sowie deren Fehlerbehandlung bleiben unverändert.

Prognosen bleiben vor der Aufnahme ihrer Hinweisframes eingefroren. Offene Tickets
und die schon gewählte Ausgabe werden durch Erhaltung, Ersetzung, Freigabe oder
Promotion niemals rückwirkend umgeschrieben. Ein noch lebender Originalschlüssel
erhält Feedback nach der bisherigen Regel. Ein inzwischen gelöschter oder durch
Promotion abgelöster Ticketschlüssel erhält kein neues Zellupdate und wird nicht
wiederbelebt. Bereits vorhandene Kandidatenzellen werden bei echter Promotion
wie bisher auf den neuen Retained-Schlüssel übertragen. Das offene Ticket bleibt
am alten Schlüssel. Nach Fristfreigabe werden tote Zellen im selben vorhandenen
Prune-Schritt entfernt. Ende und Fehlerpfad lösen alle eingefrorenen Referenzen.

Die vorhandenen kurzfristig eingefrorenen Nachfolgerreferenzen dürfen eine
begonnene Prognose abschließen. Sie bilden keinen zweiten abrufbaren Kandidaten,
dürfen nicht in den Bestand zurückkopiert werden und bleiben in der unveränderten
Originalframe- und Ausgabebilanz enthalten.

## Ressourcenvertrag

| Ressource | Unveränderte Grenze / K1-Anforderung |
| --- | --- |
| Bestätigte Spuren | Höchstens 2 × 4 Originalframes |
| Kandidat | Höchstens 1 × 4 Originalframes |
| Bildender Block | Höchstens 4 Frames; nach Entscheidung vollständig übernommen oder freigegeben |
| Hinweis und transiente Originalreferenzen | Weiterhin höchstens 18 verschiedene Originalframes insgesamt, einschließlich eingefrorener und abgelöster Referenzen |
| Ausgabeslots / kombinierte Grenze | 2 / 20 |
| Gepackte Fehler-/Ticketbank | Unverändert 416 Byte; keine Umwidmung freier Bytes für Alter, Archiv oder Wartespur |
| Zusatz-Pythonheap | Unverändert 16.384 Byte einschließlich temporärer Objekte im bisherigen Messumfang |
| Receipt / transienter UTF8 | Unverändert 16.384 / 32.768 Byte |
| Neue persistente Kandidatenmetadaten | Keine: weder Alterszähler noch Verlängerungsbit, Zeitstempel oder zusätzliche Frame-ID-Liste |

Die Regel nutzt lediglich zwei vorhandene Ordinalwerte, eine lokale Differenz und
Vergleiche. Auch temporäre Python-Skalare, neue Ereignisrückgaben und noch offene
alte Framealiase müssen bei einer späteren Implementierung mitgezählt werden.
Die konzeptionelle Slotbilanz ist budgetneutral; eine gemessene Heap- oder
Laufzeitqualifikation liegt damit noch nicht vor. Überschreitung einer Grenze
wäre ein technischer Gegenbefund, keine Erlaubnis zur Grenzerhöhung.

Der einzige geänderte operative Teil ist die Entscheidung über den Kandidaten
am Segmentabschluss. Keine Änderungen an Segmentlänge, Hint-Zeitpunkt, exaktem
Abruf, Hypothesenberechtigung, EMA, Persistenzvergleich, Tie-Regel oder Default.
Neue administrative Ereignisbezeichnungen müssen von bestehenden Aufrufern als
nichtpromovierende Abschlüsse verarbeitet werden; TRACE_PROMOTED bleibt nur für
eine echte Promotion zulässig. Die Recency-Aktualisierung bestätigter Spuren darf
durch einen zusammengesetzten Bestätigungs-/Freigabefall nicht versehentlich
ausfallen. Dies ist eine spätere Abnahmebedingung, keine heutige Codeänderung.

## Geschlossener Entwicklungs-Gegenprüfvertrag

Verglichen werden genau zwei Varianten: eingefrorenes U und K1 mit derselben
Fehler-/Auswahlpolicy. Jede startet je Fall frisch und erhält dieselben Werte,
Zeitpunkte und Zielmasken. Die Speicherzustände dürfen gerade wegen der Änderung
auseinanderlaufen; Gleichheit zwischen U und K1 ist kein Prüfkriterium. Jede
Variante benötigt ihre eigene Referenzfortschreibung mit ihrer jeweiligen
Kandidatenregel. Ein alter U-Referenzbestand darf nicht als K1-Sollzustand dienen.

Die folgenden Datenmengen und Reihenfolgen sind vor einer späteren Implementierung
festgelegt, werden in diesem Auftrag aber weder erzeugt noch ausgeführt:

1. Die bestehenden 16 T1-Fälle in ihrer gebundenen Reihenfolge und unveränderter
   Länge80, aus den gespeicherten Dateien. Nur bekannte Entwicklungsgegenprobe.
   Alle39 Ziele3,5,...,79 pro Fall, insgesamt624, bleiben erhalten. Die324
   Diagnoseziele werden lediglich als zusätzliche Untergruppe berichtet.
2. Acht deterministische Gegenfälle F1–F8 mit jeweils16 Viererblöcken, also64
   Positionen und31 Zielen3,5,...,63. Insgesamt248 Ziele. Keine Auswahl nach
   Ergebnissen und keine weitere Seed-, Dauer- oder Variantenserie.

Damit umfasst der geplante Entwicklungsvergleich24 Fälle,1.792 Eingangspositionen,
48 Arm-Ausführungen,3.584 Arm-Aufnahmen und3.584 gesondert bilanzierte
Referenzfortschreibungen. Die letzte Prognose für81 beziehungsweise65 ist zensiert.
Die beiden Datenmengen werden getrennt ausgewertet; zusätzlich wird das gleich
über24 Fallmittel gewichtete Gesamtmittel angegeben. Keine positive Gesamtaussage
aus einer ausgewählten Maske oder nur aus den324 Diagnosezielen.

### Exakte symbolische Gegenfälle

Für i=0,...,15 und Koordinate j=0,...,47 wird ausschließlich für diese späteren
technischen Entwicklungsfixtures definiert:
q_i[j] = 1/2 + (i+1)/128 + j/8192.
Alle Werte sind feste dyadische Zahlen. Es gibt keine Zufallsziehung, Policy-
Rückkopplung oder Parameterwahl. Der Policy werden nur die48 Zahlen übergeben,
niemals Symbolnamen oder Fallrollen. Diese einfachen Fixtures sind keine neue
Transferpopulation und kein Audio-/Video-Nachweis.

A=(q0,q1,q2,q3), B=(q4,q5,q6,q7), C=(q8,q9,q10,q11),
D=(q0,q1,q2,q12), E=(q0,q1,q0,q14), F=(q0,q1,q2,q15).
Jeder folgende Buchstabe bezeichnet einen vollständigen unveränderten Viererblock.

| Fall | Genau 16 Blöcke | Zweck, kein vorweggenommenes Gesamtergebnis |
| --- | --- | --- |
| F1 | A B A C A B A C A B A C A B A C | Wiederkehr nach übersprungenem Zwischenblock; Preis der verworfenen B/C-Spuren sichtbar |
| F2 | A B B C A B B C A B B C A B B C | Neu eintreffendes B wird rasch erneut benötigt; U kann es früher nutzen oder bestätigen |
| F3 | A D E E C B A D E E C B A D E E | Alter Kandidat erhält zunächst günstiges Feedback, danach irreführende Fortsetzung |
| F4 | A B C D E F A B C D E F A B C D | Laufend neue Erfahrung und zwangsweiser Ablauf; kein unbegrenztes Festhalten |
| F5 | A A B A A C A A B A A C A A B A | Bestätigte Wiederkehr neben Kandidat; Bestätigungspriorität und Frist ohne Neustart |
| F6 | A B A B A B A B A B A B A B A B | Konflikt zwischen zusätzlicher Promotion und verpasster neuer Spur |
| F7 | A D F D E F A D F D E F A D F D | Gleicher Hinweis bei wechselnden Gesamtspuren und Nachfolgern; Feedback eindeutig je Originalkey |
| F8 | A A B B C C A A B B C C A A B B | Zwei bestätigte Plätze, weitere Promotion und reguläre Verdrängung |

Konkreter vorab erwarteter Gegenfall F3: A liefert nach D am Feedbackziel7 einen
günstigen Fehlerwert für den Nachfolger q2. U ersetzt A am Abschluss8 durch D;
K1 behält A. Beim Hinweis9–10 aus E kann K1 deshalb den warmen alten Nachfolger q2
wählen, während U unter dem neuen kalten Schlüssel auf Persistenz q1 zurückfällt.
Das Ziel11 ist q0. Wegen der definierten Koordinatendifferenzen ist q2 weiter von
q0 entfernt als q1. Dieser erwartete lokale Schaden ist eine logische Prüfvorhersage,
kein bereits ausgeführtes Messergebnis. Er darf weder entfernt noch durch eine
nachträgliche Erhaltungsdaueränderung vermieden werden.

### Getrennte Messgrößen und Nenner

Für jedes der872 bewerteten Ziele werden beide tatsächlich lebenden Bestände und
eingefrorenen Prognosen dokumentiert. Vergleichsidentität einer Originalhypothese:
Fall, Originalordinalen und Offset; Generation/Role bleiben zusätzliche Belege,
aber armübergreifend unterschiedliche Generationnummern sind allein kein Gewinn.

- Zusätzliche/verlorene berechtigte Nachfolger: Mengendifferenzen der realen
  Originalhypothesen K1\U und U\K1, sowohl Hypothesenzahl als auch Zahl betroffener
  Ziele. Zusätzlich nach Gleichheit zum realisierten Ziel und zum Beobachtermodalwert.
  Für T1 bleibt der gespeicherte Modellmodalwert maßgeblich; bei den deterministischen
  F-Fällen ist die festgelegte nächste Position der Beobachter-Sollnachfolger.
- Vorzielliche Feedbackverfügbarkeit: je lebendem Key ec/ep vorhanden oder kalt,
  frühere Feedbackpositionen, Promotionslinie und Lebendigkeit beim Feedback.
  Warm gewordene und verlorene warme Möglichkeiten getrennt. Historische Vorkommen
  bleiben diagnostisch; sie werden nie in diese Mengen aufgenommen.
- Erfahrungsabhängige Entscheidungen: SELECTED_BY_ERROR mit eindeutigem striktem
  Vorteil, gewählter Originalkey, Unterschied zu U, Modal-/Realisierungsbezug.
  Kaltheit, fehlender Vorteil und Gleichstand getrennt. Keine vermutete Wärme aus G_w.
- Prognosegewinn und Schaden: je Ziel MAE(K1)−MAE(U), positive/negative/gleiche
  Anzahl, Gewinn- und Schadenssummen, größter Zielschaden, Fallmittel und schlechtester
  Fallmittelabstand. Alle Ziele jedes Falls; Gleichfälle und Kontrollen bleiben enthalten.
  T1-G_w sowie T1-Anpassung über unveränderte52 Übergänge einschließlich20 Kontrollen
  werden ergänzend unverändert berichtet, nicht als Ersatz für den Vollvergleich.

Die bisherige Anerkennungsschwelle für T1-Anpassung wird nicht gesenkt. Der neue
Vergleich mit U ist ein Entwicklungsvergleich und überschreibt das alte T1-Urteil
gegen M/E/K/P nicht. Die beiden Varianten teilen ausschließlich Eingabedaten,
keinen Speicher, keine Fehlerzellen und keine nachträgliche Entscheidungsinformation.

### Vorab festgelegte Entscheidungen

Primäre mechanistische Hypothese: Im bekannten T1-Gesamtkorpus über alle624 Ziele
ist der Anteil von Zielen mit mindestens einem lebenden modalen Nachfolger UND
vorziellichem Feedback bei K1 strikt größer als bei U. Nenner fest624, keine
Auswahl nur historisch wiederkehrender Ziele. Die324 Diagnoseziele werden separat
ausgewiesen. Gleichheit oder Abnahme widerlegt diese erwartete Verbesserung in
diesem Entwicklungsvergleich. Eine Zunahme beweist noch keinen Prognosenutzen.

Zusätzlicher Prognosenutzen wird nur ausgewiesen, wenn das ungerundete gleich
gewichtete Fallmittel von K1 im T1-Korpus strikt besser ist als U UND im gesamten
F1–F8-Korpus nicht schlechter. Auch das Gesamtmittel über24 Fälle muss strikt
besser sein. Reale Gewinne und Verluste bleiben in jedem Fall vollständig sichtbar.

Schadensgate: Kein G-Fallmittelabstand K1−U darf größer als1/32 sein; T1-G_w darf
im gleich gewichteten Mittel der vier S0-Fälle nicht schlechter werden. Diese
Grenze übernimmt das vorhandene Schadensniveau, erklärt lokale Schäden aber
nicht für bedeutungslos. Technische Vollständigkeit, Ressourcenlimits und beide
unabhängigen Referenzfortschreibungen müssen bestehen. Kein Unterschied allein
rechtfertigt eine Architekturfreigabe.

Vier Urteile getrennt: technische Auswertbarkeit; mechanistische Verbesserung;
vollständiger Prognosenutzen; Schadensgate. Fehlende Belege/Ressourcenverletzung
führen zu NOT_EVALUABLE für abhängige Urteile. Ein vollständiger fachlich negativer
Vergleich bleibt ein gültiger Gegenbefund. Kein Nachoptimieren, Reparieren oder
Wiederholen eines später freigegebenen Einmallaufs unter derselben Freigabe.

## Spätere technische Abnahme und Ausführungsvoraussetzungen

Vor irgendeinem Entwicklungsreplay ist eine separate Implementierungsfreigabe
und neutrale technische Qualifikation erforderlich. Mindestens abzudecken:

| ID | Vorab verlangte technische Prüfung |
| --- | --- |
| K01 | c+4: alte Identität bleibt; neuer Block vollständig verworfen; keine neue Generation |
| K02 | c+8: abweichender Block ersetzt; keine Erhaltungsverlängerung |
| K03 | Exakte Kandidatenwiederkehr bei c+4 und c+8: ursprüngliche Frames promovieren |
| K04 | Retained-Bestätigung hat Vorrang; Recency korrekt; Kandidat läuft bei c+8 trotzdem ab |
| K05 | Offenes Ticket bei Ersetzung/Freigabe: eingefrorene Ausgabe unverändert, kein Update eines toten Keys |
| K06 | Promotion: vorhandene Zellen wechseln Schlüssel; offene Tickets nicht rückwirkend geändert |
| K07 | Kein Kandidat, inkompletter Abschluss, Storyende, Scope-/Ordinalfehler und Generationgrenzen |
| K08 | Volle zwei bestätigte Spuren, Kandidat, bildender Block, offene Referenzen:18 Frames/416 Byte und alle Heap-/Receiptgrenzen |
| K09 | Strikte Ersetzungskonflikte und F3-Schadensvorhersage werden sichtbar statt ausgefiltert |
| K10 | Prognosezeitpunkt, Segmentierung, Abruf und Auswahl unverändert; jede Variante gegen ihren eigenen Referenzzustand |

Dies sind geplante Abnahmekriterien, keine bestandenen Tests. Keine hier erzeugten
Fixturedateien, keine Simulation der Varianten und kein heutiger Laufzeitwert.
Für eine spätere Ausführung gelten höchstens3.600s gesamt,3.540s Worker,60s
Abschluss und64MiB einschließlich1MiB Abschlussreserve; Vorbereitungsrahmen8MiB.
Eine neue gebundene Ressourcen-/Zeitplanung und ein geprüftes Startformat müssen
das konkrete24-Fälle-Paket vorher abdecken. Bei fehlender Machbarkeit bleibt der
Start geschlossen; die Fallmenge oder Grenzen werden nicht stillschweigend geändert.

Alle Quellen, Masken, Varianten, Prüfer und Einmalautorisierung wären vor Start
neu zu binden. Historische Einmalfreigaben sind verbraucht. T1 bleibt bekanntes
Entwicklungsmaterial; nach einer Änderung ist ein gesondert vorab festgelegter
unberührter Transfervertrag mit neuem Material erforderlich. Dieser Konzeptvertrag
enthält dafür weder neue Leistungsbehauptung noch Ausführungsfreigabe.

## Anschlussentscheidung

Empfehlung: zuerst diesen einen Konzeptvertrag einschließlich seines Preises
und des ausdrücklich erwarteten F3-Gegenfalls abnehmen. Erst anschließend kommt
ein begrenzter Implementierungs- und neutraler Qualifikationsauftrag für genau K1
in Betracht. Keine Fehlergewichtungsänderung, keine alternative Erhaltungsdauer
und keine zusätzliche Speicherstelle innerhalb dieses Pakets.
