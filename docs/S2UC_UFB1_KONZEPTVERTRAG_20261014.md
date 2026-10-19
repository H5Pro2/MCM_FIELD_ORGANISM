# UFB1 Konzeptvertrag für gemeinsamen Informationszugang und Speicherrahmen

Stand: 2026-10-14. Autor: MCM-KI-Entwickler. Empfänger: MCM KI Projektleiter.
Status: KONZEPT_ZUR_ABNAHME, keine Implementierungs- oder Forschungsfreigabe.
UFB1 ist eine Dokumentkennung, keine Laufnummer. Grundlage sind der aktuelle
Forschungsweg, der UF1-Prüfvertrag und der unabhängig abgeschlossene UF1-Befund.

**Fortschreibung nach fachlicher Auswertung am 2026-10-14:** Der Konzeptauftrag
ist abgeschlossen. Implementierung, neutrale Qualifikation und Forschungs-
wiederholung von UFB1 werden derzeit nicht beauftragt. Die Erkenntnisse bleiben
erhalten; die untenstehenden Anschlussvorschläge sind historische Vorschläge.
Aktuelle Konzeptentscheidung ist die
[URA1-Auswahlablation bei identischem Spurenbestand](S2UC_URA1_AUSWAHLABLATION_KONZEPT_20261014.md).

## 1 Forschungsfrage und Machbarkeitsentscheidung

Bleibt der Vorteil der Häufigkeitsregel gegenüber U bestehen, wenn beide
Verfahren denselben externen Informationszugang und dieselbe vollständig
definierte Speicherobergrenze erhalten?

**Entscheidung: als begrenzter Gesamtvergleich konzeptionell machbar, technisch
noch nicht qualifiziert.** Vorgeschlagen sind genau U_B und F_B: die bisherigen
Entscheidungs- und Lernregeln unter einer gemeinsamen kausalen Schnittstelle
und einer gemeinsamen Speicherrechnung mit 65.536 Byte je Arm. Die gemeinsame
Schnittstelle gewährt keine zusätzliche Vorhersagefähigkeit. Historische
U/F-Ergebnisse werden nicht umbenannt oder verändert. U_B/F_B bezeichnen eine
neue Ausführungs- und Ressourcenvariante, auch wenn die Kernregeln gleich bleiben.

Dabei ist „derselbe Informationszugang“ streng von „derselbe interne
Informationsbestand“ und „dieselbe Nutzung von Vorwissen“ zu unterscheiden.
Beide dürfen denselben bis zum aktuellen Zeitpunkt freigegebenen Eingang sehen;
welche Erfahrung sie behalten und wie sie sie auswerten, bleibt Teil ihres
Verfahrens. Eine Angleichung der gehaltenen Geschichte würde U oder F ersetzen
und damit die gestellte Frage wesentlich verändern.

**Wichtige Grenze:** Bereits UF1 gibt beiden den laufenden Frameindex; auch U
besitzt eine indexgebundene Vierframe-Segmentierung. Das Phasenprivileg von F
besteht wesentlich in seiner programmierten Verwendung der Phase für
Hinweisbildung, Prognose und Lernen. Ein gemeinsamer Index entfernt diese
Spezialisierung nicht. UFB1 darf deshalb nicht als isolierte Beseitigung eines
Phasenvorteils oder als Kausaltest der Verlaufsspeicherung bezeichnet werden.

Der zusätzliche prüfbare Gehalt liegt in der verifizierten gemeinsamen
Zugangsgrenze und einer für beide vollständigen Ressourcenrechnung. Falls beide
Kerne dabei unverändert bleiben und die Obergrenze nicht bindet, ist der
Leistungsvergleich eine Replikation unter gemeinsam geprüftem Ressourcenrahmen,
kein neuer Mechanismustest. Ein positiver Befund zeigt dann Fortbestehen des
Vorteils unter diesem Rahmen, nicht seine Ursache. Diese Einschränkung ist Teil
der Abnahmeentscheidung, nicht erst eine nachträgliche Ergebnisdeutung.

## 2 Tatsächlich nutzbare Informationen im vorhandenen Code

Die folgenden Aussagen stammen aus Codelektüre, nicht aus neuen Messungen.

| Aspekt | U in UF1 | F in UF1 | Konsequenz |
| --- | --- | --- | --- |
| Eingang | PerceptionSample mit 48 Werten, Index, Profil, Owner, Stream und Zeitintervall | accept(index, values) mit denselben 48 aktuellen Werten | Die Signaturen sind verschieden; Metadaten müssen auf einen gemeinsamen, fallneutralen Vertrag begrenzt werden. |
| Index und Zeit | next_index, first_ordinal=1, hop=window=4800; Frameordinal und Segmentname p1, p2 usw. | laufender Index und index % 4 | Beide besitzen die Information zur Vierframeausrichtung; die Verwendungsregeln sind verschieden. |
| Vierframephase | PairContextAdapter erzeugt p{(i−1)//4+1}; _admit schließt bei (ordinal−first_ordinal+1)%4=0 | Phase 1/2 bilden Hinweis, Phase 3 zählt dessen Ziel, Phase 0 sagt Persistenz voraus | U ist nicht phasenblind. F nutzt die Aufgabenphase gezielter. |
| Wahrnehmungshistorie | zwei Retained-Vierframespuren, ein Kandidat, forming, aktuelles Paar, Hinweis- und eingefrorene Ausgabereferenzen; kein beliebiger Zugriff auf die ganze Quelle | zwei Zweiframe-Schlüssel, je höchstens zwei beobachtete Fortsetzungen und ihre Häufigkeiten, Feedbackstempel, Puffer und eine Ausgabe | Diese Bestände sind endogen; die Hülle darf keinem Arm zusätzliche Historie liefern. |
| Prognose | nach jedem vollständigen Zweiframe-Paar, vor Aufnahme dieses Paares in die Spurorganisation; Ziel i+1 | bei i%4=2 Q-Prognose, bei i%4=0 Persistenz; jeweils Ziel i+1 | Beide haben dieselben äußeren Prognosetermine, nicht dieselben internen Abläufe. |
| Feedback | am folgenden ungeraden Index zuerst consume_feedback, danach accept_perception; EC/EP für alle gültigen eingefrorenen Hypothesen, EMA alpha=1/2 | accept bewertet vorherige Ausgabe; bei Phase 3 zählt es anschließend das tatsächliche Ziel, bei Phase 1 kein Zählerlernen | Beide bekommen nur das aktuelle tatsächlich eingetroffene Ziel, keine Erfolgslabels oder Zukunft. |
| Abruf/Entscheidung | Faktorhinweise, für Auswahl nur factors=[1.0] mit vorhandenem Nachfolger; eindeutiger strikt negativer EC−EP-Sieger, sonst Persistenz | exakte Schlüsselbits; strikte Häufigkeitsmehrheit, sonst Persistenz | Unterschiedliche Regeln bleiben Forschungsgegenstand. |
| Ende | finish_story verwirft letzte Prognose und räumt auf | finish erwartet 1024 Frames, 256 Q-Feedbacks, zensiertes Ziel 1025 | Gleiche äußere Geschichte; unterschiedliche interne Endinvarianten bleiben prüfbar. |

Konkrete Lesebelege:

- [PairContextAdapter](../tools/_s2uc_pair_context_adapter.py):
  PerceptionSample, accept_perception, _admit, finish_story.
- [MultiErrorAdapter](../tools/_s2uc_multi_error.py): _receipt,
  consume_feedback, _promote, _admit, selected_values.
- [FactorHintArm](../tools/_s2uc_factor_hint.py): hint und factor_matches;
  [PerceptionRecencyArm](../tools/_s2uc_perception_recency.py): close_segment.
- [UF1-F](../tools/_s2uc_uf1_f.py): _accept, invariants, finish.
- [UF1-Beobachter](../tools/_s2uc_uf1_engine.py) und
  [U-Replaypfad](../tools/_s2uc_hx1_replay.py): Aufrufreihenfolge,
  Referenzen und vom Arm getrennte Quell-/Beobachterbestände.

Keine Fallkennung r/D/N, Orientierung, X/Y/A/B-Labels, Quoten oder
Katalogtabellen gelangen in den Arm. Dass der externe Beobachter eine komplette
Quelle hält, gewährt dem Arm keinen Zugriff darauf. Diese Trennung muss im
späteren Zugangsprüfer belegt werden, nicht bloß durch identische Frames.

## 3 Gemeinsame kausale Schnittstelle

Der folgende Vertrag ist eine Spezifikation, heute nicht implementiert.

### 3.1 Gemeinsamer Eingang und vorab bekannte Struktur

Jeder Arm erhält je Frame genau einen unveränderlichen Eingangsrecord:

- values: Tupel aus 48 endlichen binary64-Werten;
- index: fortlaufend 1 bis 1024, erster Index 1;
- profile: unverändertes HX1-Profil
  4309cfc91eb99fc2a999fdac99c5a7f1807ee654996e019ec0d94e3900bcbd4b;
- owner=comparison, stream=stream;
- start_sample=4800(index−1), end_sample=4800·index.

Die gemeinsame Schnittstellenspezifikation nennt zusätzlich als festes
Vorwissen: Vierframeausrichtung ab Index 1, Prognose nach jedem geraden Index,
Feedback am nächsten Index, Q-Ziele 3 mod 4 und Endzensierung bei 1025.
Dies sind deterministische Funktionen des ohnehin verfügbaren Index und der
festen Versuchsanordnung. Sie werden keinem Arm als fallabhängige Steuerlabels
oder als vorverarbeiteter Hinweis geliefert. Es gibt kein neues phase-, cue-,
predict_now- oder learn_now-Feld und keine zusätzlichen callbacks nur für F.

Die Einführung dieses gemeinsamen Vertrages macht das erlaubte Vorwissen
explizit. U erhält dadurch keinen neuen Auswahlzweig, keinen Q-Filter und keine
Häufigkeitsbank. Es bleibt offen, dass F das gemeinsame Strukturwissen durch
seinen Algorithmus wirksamer ausnutzt. „Zugang gleich“ behauptet nicht
„Verarbeitung gleich“.

### 3.2 Aufrufreihenfolge und eingefrorene Prognose

Ein äußerer Schritt step(record) pro Arm und Index, in festem Ablauf U_B, danach
F_B, danach erst der nächste Quellframe. Der externe Sequencer darf nur diesen
Record und ein bereits ausstehendes eigenes Ticket bereitstellen, keine
zusätzlichen vergangenen oder künftigen Frames.

Bei ungeradem Index >1 bewertet der unabhängige Beobachter zuerst die vorher
eingefrorene Ausgabe. Danach erhält der Arm das aktuelle Ziel in seinem Schritt.
Die U_B-Hülle ruft wie bisher consume_feedback vor accept_perception auf;
F_B ruft wie bisher accept auf, das Bewertung und Phasenupdate intern ausführt.
Kein nachträgliches Austauschen einer Ausgabe anhand des aktuellen Zieles.

Nach geradem Index liefert die Hülle eine unveränderliche Kopie der tatsächlich
gewählten 48 Werte und target=index+1. U_B verwendet selected_values, F_B den
vorhandenen Ausgabebereich. Es wird weder eine zweite Wahl berechnet noch eine
Ausgabe von außen ergänzt. Diese gemeinsame Ausgabekopie wird in beiden Armen
als eigenes Speicherobjekt belastet; Beobachterkopien sind für die Arme
unerreichbar. Ausgaben und Receipts sind kein erneuter Eingang.

Am Ende werden beide Arme geschlossen, das Ticket für 1025 ohne Feedback
zensiert und alle armseitigen Nutzdaten freigegeben. Kein Wiederverwenden eines
Arms zwischen Geschichten. Ein unerwartetes Ticket oder Ausbleiben einer
vorgeschriebenen Ausgabe ist ein technischer Fehler, keine Enthaltung, die aus
der Primärmenge entfernt werden darf.

### 3.3 Zulässige historische Daten und Zugangsprüfung

Nach einem Schritt darf ein Arm ausschließlich seine gezählten eigenen
Strukturen sowie gemeinsame unveränderliche Programmlogik erreichen. Eine
gespeicherte Eingangsreferenz zählt vollständig zum Arm. Verboten sind
Quelleniteratoren mit Rückgriff, Manifest-/Katalogreferenzen, globale
Ergebnislisten, Closures mit Quellhistorie, Cache-/Datei-/Netzwerkzugriffe und
Beobachterreferenzen. Auch IDs, Profil, Reihenfolge der Aufrufe oder Objektfelder
dürfen keine Bedingung oder Fortsetzung kodieren.

Ein späterer neutraler Prüfer muss Inputfelder und Bitwerte, Zeitpunkte,
erreichbare Objektgraphen und alle Arm-Eintrittspunkte vergleichen. Kontrollfälle
mit identischem Präfix und verschiedenen späteren Fortsetzungen müssen bis zur
Abweichung dieselben jeweiligen armseitigen Zustände und Ausgaben haben. Dazu
kommen gesperrte Fremdattribute und injizierte Zugriffe auf Beobachter/Quelle.
Dies belegt Kausalität und die Grenze zum externen Bestand; es verlangt keine
Gleichheit zwischen den Zuständen von U_B und F_B.

## 4 Gemeinsame Speicherzählung

### 4.1 Gemeinsame Obergrenze und Zählbereich

Für jeden Arm gilt **65.536 Byte konservativ belasteter Daten- und
Objektspeicher**, einschließlich Hülle, aller Originaldaten und Transienten.
Das ist ein vorab gewählter technischer Rahmen, kein gemessener Bedarf und kein
Nachweis seiner Einhaltbarkeit. Er liegt über den vorhandenen
Grenzstellenbelegen von U und F und lässt eine gemeinsame Hülle samt
konservativer Transientenrechnung plausibel erscheinen. Die UF1-Maxima
20.871 Byte erreichbarer U-Graph, 5.359 Byte U-Zusatzheap und 5.847 Byte
F-Eigenheap sind unterschiedlich abgegrenzt und dürfen weder gleichgesetzt
noch als Zertifikat dieser neuen Grenze addiert werden.

Es gibt keine Pflicht, ungenutzten Speicher zu belegen. Kein zusätzlicher
Retained-Platz für U, kein künstliches F-Padding und keine Entfernung eines
F-Schlüssels, um die aktuelle Belegung gleich aussehen zu lassen. Zwei
Verfahren können dieselbe Obergrenze haben und verschieden viel nutzen.

| Zu belastende Kategorie | U_B | F_B |
| --- | --- | --- |
| Original-/Verlaufsdaten | alle erreichbaren Frameobjekte einschließlich 48 Werte, Tupel, Metadaten; Retained, Kandidat, forming und eingefrorene Referenzen | Schlüssel und Fortsetzungswerte in der Bank; jede zusätzliche tatsächlich existierende Kopie |
| Lernzustand | 416-Byte-Bank mit Fehlerzellen, Tickets, Updatepuffern und Steuerung; Beobachtungsendstände und Armmetadaten | 4304-Byte-Bank mit vier Häufigkeiten, zwei Stempeln und Steuerung; keine zusätzliche kostenlose Zählertabelle |
| Eingangs-/Hinweispuffer | pair, intervals, _hints, _pframe und gehaltene Eingangsrecords | Zweiframepuffer und aktueller geliehener Record |
| Ausgaben | vorhandene Persistenz-/Kontextreferenzen, PredictionReceipt, neue gemeinsame Ausgabekopie | eigene eingefrorene Ausgabe plus neue gemeinsame Ausgabekopie |
| Transienten | Matchlisten, Serialisierung, JSON/UTF-8-Receipts, Tupel-/Vektorkopien, lokale Container und temporäre Skalare | Kopier-/Vergleichsbytes, struct-Zwischenobjekte, temporäre Skalare und Container |
| Hülle | Recordprüfung, Ticket und alle gehaltenen Daten | dieselbe Zählregel, einschließlich sonst ungenutzter Metadaten |

Objekte im selben Arm werden nach Identität einmal gezählt; echte Kopien zählen
mehrfach. Zwei unterschiedliche Werte mit gleichem Inhalt sind keine
Speicherersparnis. Innerhalb der gepackten Bank werden überlagerungsfreie Bytes
einmal gezählt. Eine vermeintlich geliehene Referenz auf einen Originalframe ist
kein kostenloser Speicher: sobald erreichbar, gehört dessen ganzer relevanter
Objektgraph zur Rechnung. Ein zwischen Armen geteilter unveränderlicher Record
wird pro Arm voll belastet, damit gemeinsame Prozessobjekte keinen Arm subventionieren.

### 4.2 Verbindliche konservative Messregel

Ein gemeinsamer, separat qualifizierter Prüfer verwendet für beide Arme dieselbe
Definition. Zu Beginn jedes vollständigen step-/finish-/abort-Aufrufs:

1. G_before: tiefer Objektgraph aller Instanzen der Armhülle und des Arms sowie
   des aktuellen Eingangsrecords; union nach Identität. dict/slots/Container,
   String-/Bytesnutzdaten, Skalare, gepackte Banken und Originalwerte einschließen.
2. P_alloc: Spitzenzuwachs der während genau dieses Aufrufs lebenden,
   vom gebundenen Python-Allokationstracer erfassten Allokationen gegenüber
   dem Messbeginn. Der aktuelle Record muss vor diesem Messbeginn vorliegen.
   Vorbestehender Speicher, der während des Aufrufs freigegeben wird, reduziert
   G_before nicht; das ist absichtlich konservativ.
3. N_untracked: nachgewiesene obere Schranke für zusätzliche nicht vom Tracer
   erfasste armseitige native Datenpuffer. Keine Annahme null ohne Code-/Runtime-
   Beleg. Die Entwicklung muss eine konkrete Zahl je erlaubtem Pfad binden;
   unbekannter nativer Zusatzbedarf verhindert Qualifikation.
4. G_after: derselbe vollständige Objektgraph am Rückkehrpunkt, einschließlich
   noch lebender Ausgabe/Receipts und der Hülle. Der gemeinsame Prüfer entfernt
   seine eigenen Hilfsobjekte aus der Zählung, niemals Objekte des Arms.

Belastung des Aufrufs = max(G_before + max(0,P_alloc) + N_untracked,
G_after + N_untracked). Jede Belastung muss <=65.536 Byte bleiben. Initialisierung
zählt als Aufruf mit leerem Vorzustand; jede zusätzliche Export-/Kopieroperation
der Armhülle liegt innerhalb einer solchen Messgrenze. Keine unbeobachtete
Zwischenoperation zwischen Schritt, Ausgabeübernahme und Cleanup.

Ein tiefer Graphscan allein ist kein Transientennachweis. Die vorhandene
U-Funktion owned() lässt unter anderem Frameobjekte und Basisarm aus und darf
nicht als gemeinsame Messfunktion weiterverwendet werden. Auch die vorhandenen
F-/U-Meter ergeben zusammen noch keinen qualifizierten gemeinsamen Prüfer.
Die neue Zählung benötigt neutral geprüfte Identitätsbehandlung,
Kopierfälle, vollständige Wrapperwurzeln und Fehlerpfade. Der spätere Prüfer
darf den Arm weder mit einer Vollhistorie versorgen noch dessen Zählung beeinflussen.

Unveränderlicher Programmcode, Interpretergrundbestand und feste Ausführungs-
Stackinfrastruktur gehören nicht zum armseitigen Datenspeicher; ein Objekt darf
nicht durch Verlagerung in Modulglobals oder Funktionsdefaults ausgenommen
werden. Dynamische native Nutzdaten und temporäre Vektoren zählen weiterhin.
Der gesamte Prozess einschließlich Interpreter, Stacks, Referenzen, Quellen,
Beobachter und Zählprüfer bleibt zusätzlich im gemeinsamen harten Joblimit.
Dies ist eine implementierungsabhängige Speicherdefinition, keine abstrakte
Informationskapazität in Bits.

### 4.3 Abgrenzung zu bisherigen Grenzen

Die historischen unterschiedlichen Zusatzheap-/Eigenheap-/Numerikgrenzen
werden in UFB1 nicht als gleichwertige Armobergrenzen ausgegeben. Ihre alten
Messwerte dürfen ergänzend berichtet werden. Die zukünftige UFB1-Messhülle
ersetzt deren Budgetentscheidung durch die gemeinsame vollständige Rechnung;
sie darf nicht den alten asymmetrischen Meter und zusätzlich lediglich einen
gleich benannten Grenzwert verwenden.

Strukturelle Invarianten bleiben unverändert: U zwei Retained-Spuren plus ein
Kandidat, gültige Original-/Ticketreferenzen, sechs Fehlerzellen und unveränderte
Aufnahmeregeln; F zwei Schlüssel mit je zwei Werten und Zählgrenzen. Diese
begrenzen Fähigkeiten der Verfahren, nicht eine angeblich gleiche tatsächliche
Belegung. Die gemeinsame Obergrenze erlaubt keine Kapazitätserweiterung.

Quellen für die bisherige Abgrenzung:
[U owned/Meter](../tools/_s2uc_multi_observer.py),
[Grenzstellenerfassung](../tools/_s2uc_ulz1_resources.py),
[F-Meter](../tools/_s2uc_uf1_engine.py).

## 5 Ausdrückliches Änderungsregister

| Bestandteil | Vorgesehene Änderung | Was daraus nicht folgt |
| --- | --- | --- |
| Gemeinsame Hülle | ein Recordvertrag, feste step-Reihenfolge, identische Metadatenprüfung und identische Ausgabekopie | keine zusätzliche Wahrnehmungshistorie oder neue Auswahlregel |
| U-Einbindung | bisherige Feedback-vor-Perception-Reihenfolge erhalten; bestehenden Kern über die neue Hülle aufrufen | kein Q-only-Lernen, kein Phasengate für Abruf, keine Häufigkeitszellen, A1/K1 bleiben aus |
| F-Einbindung | gleichen Record prüfen, index/values an unveränderten Kern reichen, vorhandene Ausgabe exportieren | keine zusätzliche Schlüsselart, keine Beschneidung der Häufigkeiten, keine Entscheidungshilfe durch Labels |
| Speicheraufsicht | gemeinsamer vollständiger Zählprüfer und 65.536-Byte-Entscheidung statt unterschiedlich abgegrenzter Meter | kein Gleichbelegungs- oder Gleichkapazitätsbeweis |
| Referenzen | unabhängige Referenzen an dieselbe äußere Schnittstelle anbinden; Ressourcenprüfer separat referenzieren | Produktionsausgaben werden nicht zu erwarteten Referenzwerten |
| Quellen, Bootstrap, Hülle | neue getrennte Bindung und Namensräume | keine Wiederverwendung alter Freigaben, keine Vermischung alter Resultate |

Kerncode und bisherige Bindungen bleiben erhalten. Falls zur Einhaltung dieser
Spezifikation doch Aufnahme, Abruf, Auswahl, Updates, Phasennutzung oder
Kapazität geändert werden müssten, endet UFB1 als unverändert-regelbasierter
Vergleich vor Forschung. Eine solche Änderung verlangt einen neuen ausdrücklich
benannten Variantenvertrag. Keine stille Reparatur von U oder Beschränkung von F.

## 6 Geplanter Vergleich und neue Quellen

Genau zwei Arme U_B/F_B, 32 gepaarte Replikate r=1,…,32 mit D und N,
je 1024 Frames, 256 Vierframeblöcke. Reihenfolge r aufsteigend, D vor N;
frische Zustände je Geschichte. Insgesamt 64 Geschichten, 128 Armläufe,
65.536 Quellframes, 131.072 Armverarbeitungen und ebenso viele Referenzschritte.

Aufgabenfamilie und Rezept entsprechen Abschnitt 3 des
[UF1-Prüfvertrags](S2UC_UF1_PRUEFVERTRAG_20261005.md), mit ausschließlich
folgenden Identitätsänderungen: Fallnamen UFB1-01-D bis UFB1-32-N,
Forschungsnamensraum MCM-UFB1/source/v1 statt MCM-UF1/source/v1.
Die Suche im aktuellen Projekt vor diesem Dokument fand keine UFB1-Verwendung.
Heute werden die Namen nur reserviert, keine Ziehungen berechnet.

Zur eindeutigen Rezeptfestlegung: V(x)[j]=x+j/4096, j=0,…,47;
Katalog V(1/8), V(7/8), V(1/2), V(1/4), V(3/4), V(1/16).
X/Y sind die beiden Zweiframehinweise mit erstem Frame V(1/8)/V(7/8)
und zweitem Frame V(1/2); A/B sind V(1/4)/V(3/4), Schlussframe V(1/16).
Blöcke bestehen aus Hinweisframe, V(1/2), A/B und Schlussframe.

Je r vier Streams continuation, dependent-A, dependent-B, null-cue,
jeweils d=0 beginnend. SHA256 der exakten UTF-8-Zeichenfolge
MCM-UFB1/source/v1/r={r}/stream={s}/draw={d}, Dezimalzahlen ohne führende
Nullen, kein LF. Erste acht Bytes big-endian uint64 u. randbelow(n):
L=2^64−(2^64 mod n), u<L akzeptieren und u mod n; sonst nächste Ziehung.
d auch bei Ablehnung erhöhen, maximal 4096 Rohziehungen je Stream;
n=1 verbraucht ebenfalls eine Ziehung. Fisher-Yates i=m−1,…,1.

T_r ist die Shufflefolge von 128 A und 128 B, in D/N identisch. Die aufsteigenden
A- und B-Positionen getrennt mischen. Ungerades r: erste 96 A- und 32
B-Positionen erhalten X, gerades r: 32 A- und 96 B-Positionen; Rest Y.
N mischt separat 128 X/128 Y ohne erzwungene Kontingenz. Orientierung
o=(r−1)%2, je 16 Paare. Keine Deduplikation, Leistungsauswahl oder Ersatzfolge.

Nach separater Forschungsfreigabe alle 64 Quellen im einen reservierten Versuch
materialisieren, mit unabhängigem Rezeptprüfer prüfen und per Manifest
versiegeln, bevor irgendein Arm beginnt. JSON kanonisch sort_keys=True,
separators=(',', ':'), allow_nan=False, UTF-8 plus LF; Records wie UF1.
Danach je Geschichte Länge und SHA erneut gegen dasselbe Manifest prüfen.
Neue Quellen werden weder aus UF1-Archiven kopiert noch aus alten Fehlerreihen
abgeleitet. Neutrale Entwicklung ausschließlich Handfolgen oder separater
Namensraum MCM-UFB1/neutral/v1, erst nach Entwicklungsauftrag.

## 7 Einziger Primärkontrast und vorab feste Erfolgsregel

Q={3,7,…,1023}, alle 256 Ziele je Geschichte ohne Warm-up oder Ausschluss.
MAE48 wie UF1: binary64, abs(pred[j]−target[j]) in fester Reihenfolge j=0,…,47
aufsummieren, abschließend durch 48 teilen. Keine Umordnung oder FMA.

m[r,C,a] = mittlerer Q-MAE. d[r]=m[r,D,U_B]−m[r,D,F_B].
Einziger Primärschätzer theta = Mittelwert der 32 D-Paarwerte.

Nominales 95%-Intervall aus 10.000 nach Orientierung geschichteten Bootstrap-
Ziehungen. Für z=0,…,9999, o=0/1 und k=0,…,15 erste acht SHA256-Bytes von
MCM-UFB1/bootstrap/v1/z={z}/orientation={o}/k={k}, big-endian uint64 u,
gewähltes r=2·(u mod 16)+1+o. Exakte UTF-8-Bytes ohne LF. Je Zeile erst o=0,
dann o=1; dieselben Paarindices für beide Bedingungen und alle Nebenanalysen.
Matrix später 320.000 Bytes mit r−1, unabhängig prüfen und vor erster
Forschungsquelle binden. Heute keine Matrixerzeugung.

Jede Ziehung mittelt 32 Paarwerte. Quantile q=1/40 und 39/40, h=9999q,
lineare Interpolation zwischen benachbarten sortierten Werten. Gespeicherte
binary64-MAE, Geschichtenmittel, Kontraste und Quantile als exakte rationale
Zahlen behandeln; erst die Anzeige runden.

- Untere Grenze >0: F_VORTEIL_UNTER_GEMEINSAMEM_RAHMEN_BELEGT.
- Obere Grenze <0: U_VORTEIL_UNTER_GEMEINSAMEM_RAHMEN_BELEGT.
- Sonst, einschließlich Nullberührung: KEIN_EINDEUTIGER_UNTERSCHIED_NACHGEWIESEN;
  keine Gleichwertigkeit und kein Nachweis verschwundenen Vorteils.
- Jede technische Vertragsabweichung: NICHT_AUSWERTBAR; kein Leistungsurteil
  aus Teilmengen und keine Verrechnung mit dem alten UF1-Ergebnis.

Ein positives Intervall entscheidet das Fortbestehen des Vorteils nur im neuen
Rahmen; ein Unterschied zwischen alten und neuen Punktschätzern ist kein
Interaktionstest und kein Beleg einer kausalen Änderung.

Ergänzend vollständig wie UF1: D/N × Q/G_all/S/Q_X/Q_Y × alle/Orientierung 0/1;
640 Armmittelwerte, 30 Bilanzen mit Paarlisten, Mittelwerten, nominalen
Intervallen, Gewinn/Schaden/Netto, besser/schlechter/gleich, maximalem Schaden
mit allen Positionen und schlechtestem Paarmittel. G_all=3,5,…,1023, S=5,9,…,1021;
Q_X/Q_Y je 128. Explorative D−N-Interaktion, kumulative Differenzen,
U-Verfügbarkeitsklassen und F-Klassen/Zählerdiagnosen. Keine zweite Primärregel,
keine Gleichwertigkeit aus N, keine Änderung der Interpretation anhand
günstiger Untergruppen. Zusätzlich beide vollständigen Speicherprofile
berichten; tatsächliche Speichernutzung nicht als nachträglichen Kovariatenfilter nutzen.

## 8 Unabhängige Qualifikation vor einer Ausführung

Späterer Entwicklungsauftrag muss vor Forschungsfreigabe mindestens liefern:

| Prüfung | Abnahmekriterium |
| --- | --- |
| I1 Gemeinsamer Zugang | identische Recordfelder/Bitwerte und äußere Zeitpunkte; keine fallabhängigen Metadaten, Quelle/Beobachter unerreichbar |
| I2 Kausalität | neutrale Präfix-/Zukunftsgegenfälle, eingefrorene Ausgaben und Zielbindung; keine Mutation einer Prognose nach Zielzugang |
| I3 Hüllenidentität | auf neutralen Fällen gleiche Kernzustände/Ausgaben wie die unveränderten U/F-Kerne; Änderungen ausschließlich laut Register |
| M1 Vollständige Zählung | Originalframes, beide Banken, Metadaten, Wrapper, geliehene Records und Ausgabekopien einbezogen; Aliase einmal, Kopien mehrfach |
| M2 Transienten/Native | Zählergrenzen 65.536 zulässig, darüber terminal; vor/nach/innerhalb-Aufrufen, Initialisierung, Ausgabe, Serialisierung, Abort; konkrete gebundene N_untracked-Schranken |
| M3 Ressourcenqualifikation | getrennte Phasenspitzen, vollständige und transiente Belegung, Leck-/Fehlerfälle; beide Arme unter identischem Rahmen ohne stille Verfahrensänderung |
| R1 U-Referenz | unabhängiger Bestand, Aufnahme/Promotion/Ersetzung, Fehlerzellen, Auswahl und Cleanup; kein Übernehmen der Produktionsentscheidungen |
| R2 F-Referenz | unabhängige Schlüssel-/Werte-/Zählerobjekte, vollständiger Vor-/Nachzustand; unbekannt, Gleichstand, Mehrheit, Ersetzung und dritter Wert |
| R3 Zugang/Meter-Referenz | separat konstruierte erwartete Objektgraphen mit Sharing/Kopien; Vergleiche des Zählers nicht nur gegen sich selbst |
| S1 Quellen/Statistik | unabhängiges Rezept nur neutral; Rejectiongrenzen, D/N-Paarung, Matrixindices, Positiv/Negativ/Nullfälle und exakte vollständige Bilanzen |
| T1 Terminalfälle | Bindungsfehler, fehlendes Ziel, dritter F-Wert, überschrittenes Budget, Workerfehler/Timeout und vorhandener Zielordner führen zum vollständigen Fehlerabschluss |

Ein später ausdrücklich beauftragter neutraler Größenablauf darf die technische
Machbarkeit zeigen, keine Nutzenbehauptung. Solange die gemeinsame Messgrenze,
native Transienten oder Hüllenidentität offen sind, ist das Paket nicht
forschungsbereit. Die Grenze wird nicht nach gemessener Forschungsleistung
angehoben. Ein Scheitern der neutralen Machbarkeit führt zum Bericht an den
Projektleiter, nicht zu einer eigenständigen Kapazitätsänderung.

## 9 Ressourcen, Bindungen und Abbruch

Vor jeder Forschung neue transitive Code-/Runtimebindung, Vertrag, Rezept,
Bootstrapmatrix und neutrale Belege bytegenau versiegeln. Python, Bibliotheken,
DLLs, Byteorder, Zählerdefinition und native Schranken gehören zur Bindung.
Historische UF1-Dateien bleiben unverändert; ihre Freigabe ist verbraucht.

Geplanter exklusiver Forschungsordner: reports/s2uc/ufb1-comparison-v1.
Heute nicht anlegen. Nach abgenommener Vorbereitung separate einmalige
Forschungsbeauftragung auf den neuen Vorstart-SHA; genaue Autorisierung und
Aufruf erst mit diesem Paket. Nach Reservierung des Versuchsmarkers verbraucht
auch ein früher Fehler den Versuch. Kein Retry, Resume, Ersatzmaterial,
Falltausch, Zwischenstopp nach Leistung oder zweiter Worker.

| Grenze | Festlegung |
| --- | --- |
| Armseitiger vollständiger Speicher | je 65.536 Byte nach Abschnitt 4, alle Aufrufe |
| Gesamtzeit Forschung | 3600 s ab Supervisorstart einschließlich Prüfung, Quellen, Arme/Referenzen, Statistik, Export und Abschluss |
| Workerfrist | spätestens Start+3540 s, 60 s Abschlussreserve |
| Gesamter privater Windows-Job-Commit | 536.870.912 Byte, Supervisor plus ein Worker, harte Jobgrenze und Mitgliedschaft geprüft |
| Gesamtexport einschließlich Vorbereitung/Postprüfung | 67.108.864 Byte |
| Vorbereitung | 8 MiB |
| Quellen | 2 MiB gesamt, 32 KiB je Quelle |
| Fallarchive | 32 MiB gesamt, 512 KiB gzip und 4 MiB expandiert je Fall |
| Verwaltung/Auswertung einschließlich Postprüfung | 2 MiB |
| Versuchsabschluss | 1 MiB |

Freier Rest im Gesamtbudget erweitert keine Teilgrenze. Archivformat verlustfrei,
gzip Level 9, mtime=0, ohne Dateiname; alle vollständigen U-Lebenszyklen,
F-Zustände, Ausgaben, Lernupdates und Zähler bleiben prüfbar. Zusätzliche
Zugangs-/Speicherevidenz muss neutral in dieses Budget passen. Passt sie nicht,
ist die Vorbereitung nicht abnahmefähig; keine Kürzung entscheidender Belege.

Terminal sind ungültiger Input oder Quellen-/Code-/Runtimehash, unvollständige
Paarung, ein fremder Zugriff, fehlende/vorzeitig geänderte Prognose,
Referenzabweichung, dritter F-Fortsetzungswert, unvollständige Speicherzählung,
Arm-/Prozess-/Zeit-/Exportüberschreitung oder fehlender Cleanup-/Workerabschluss.
Auch ein roher Jobpeak oberhalb der Grenze bei abgewiesener Allokation zählt
konservativ als Überschreitung. Ganze Untersuchung NICHT_AUSWERTBAR, ohne
Leistungsurteil; Fehlerartefakt, Phase, Fall/Arm/Ziel und verbleibende Belege nennen.

Postlaufprüfung ausschließlich aus Archiven, unabhängig von Policies und
Quellengeneratoren: Bindungen, Zugangsprotokolle, vollständige Speicherrechnung,
U-Ausgaben/Updates, F-Banken/Häufigkeiten, Primärintervall und Nebenbilanzen.
COMPLETE verlangt alle 64 Quellen, 128 Armläufe, vollständige Referenzen,
Zeit-/Ressourcennachweise und beendeten Worker. Erst dann Ergebnisurteil.

## 10 Welche Erklärung wird geprüft, welche bleibt offen?

Prüfbar ist: Der F-Vorteil kann auch unter einem gemeinsamen externen
Informationsvertrag und einer vollständig gezählten gleichen Speicherobergrenze
bestehen. Das schließt im abgenommenen Rahmen eine Erklärung allein durch
zusätzlichen externen Datenzugang oder durch Überschreitung dieser gemeinsamen
Obergrenze aus. Es schließt keine Erklärung durch effizientere Repräsentation
oder die Verwendung eines größeren Anteils des erlaubten Budgets aus.

Es bleiben verschieden: tatsächliche Belegung, erhaltene Informationen,
vierframebasierte Spuren gegenüber Schlüssel-/Wertezählung, Aufnahme/Verdrängung,
Bestätigung und Recency, EMA gegenüber kumulierten Häufigkeiten, interne
Q-Spezialisierung, Entscheidungsregel und CPU-Aufwand. Ein gleicher Grenzwert
macht daraus weder gleiche Informationskapazität noch gleiche Verarbeitung.
Auch Verluste durch das Verwerfen früherer Beobachtungen gehören zum jeweiligen
Verfahren; das Auffüllen von U mit Fs Häufigkeitswissen würde die Frage ersetzen.

Für die MCM-Entwicklung kann das Ergebnis den Nutzen des vorhandenen
Erfahrungsverfahrens gegenüber einer einfachen Baseline enger einordnen.
Es isoliert nicht den kausalen Beitrag der Verlaufsspeicherung, beweist keine
Cluster, Semantik, allgemeine Kognition, Audio-/Video-Leistung oder feldinterne
Memory. UF1/UH1/UHR1 bleiben getrennte historische Befunde, ohne Pooling.

Falls der Projektleiter unter „gleicher Informationszugang“ stattdessen
identische interne Historie oder identische Verwendung der Vierframephase
verlangt, ist die ursprüngliche Frage mit unveränderten U/F **nicht sinnvoll
machbar**. Die einzelne Alternative wäre dann ein separat vorregistrierter
Ablationsvergleich innerhalb eines einzigen Verfahrens mit genau einer
veränderten Gedächtnisfunktion, um deren Beitrag gezielt zu prüfen. Das wäre
eine andere Forschungsfrage und ist hier weder spezifiziert noch freigegeben;
kein künstlich gleichgemachtes U/F wird als Ersatz ausgeführt.

## 11 Lieferstand und kleinster nächster Schritt

Heute ausschließlich Codelektüre und Konzeptdokumentation; kein Code verändert,
kein Zähler implementiert, keine Quelle oder Matrix erzeugt, keine Simulation,
kein Test- oder Versuchslauf. Die Projektübersichten führen diesen Vertrag als
aktuellen Konzeptstand; der UF1-Abschluss bleibt erhalten.

Empfehlung: Zunächst diesen eingeschränkten Gesamtvergleich fachlich abnehmen.
Danach als kleinstes Entwicklungspaket nur gemeinsame Hülle und vollständigen
Speicherprüfer samt neutraler Zugangs-, Identitäts- und Ressourcenqualifikation
beauftragen. Abnahme: gleiche Schnittstelle, unveränderte Kernentscheidungen,
nachgewiesene gemeinsame Zählung und Einhaltung von 65.536 Byte ohne
Verfahrensanpassung. Noch keine Forschungsquellen und keine Bootstrapmatrix in
diesem ersten Paket. Erst auf diesem technischen Nachweis entscheiden, ob die
begrenzte Replikationsaussage einen neuen Forschungsversuch rechtfertigt.

Referenzen: [UF1-Abschluss](../reports/s2uc/uf1-assessment-20261005-01/REPORT.md),
[UF1-Vertrag](S2UC_UF1_PRUEFVERTRAG_20261005.md),
[Erfahrungsorientierung](KONZEPTNOTIZ_WAHRNEHMUNGSVERLAEUFE_PRAEGUNG_UND_INNERKONTEXT.md).
