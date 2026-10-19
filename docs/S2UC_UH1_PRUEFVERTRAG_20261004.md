# UH1 Prüfvertrag für U und den begrenzten hinweisabhängigen Mittelwert H

Stand 2026-10-04. Vertragskennung `MCM-UH1-v1-20261004`.
Status `SPEZIFIZIERT_KEINE_IMPLEMENTIERUNGS_ODER_LAUFFREIGABE`.
Empfänger: Projektleiter; erstellt durch den MCM-KI-Entwickler.

Dieser Vertrag konkretisiert den angenommenen H-Entwurf. Genau U/H werden
verglichen, auf den bereits bekannten 32 HX1-D/N-Quellenpaaren. Keine neue
Quelle, kein zusätzlicher Arm und keine nachträgliche Fallauswahl. HX1 bleibt
abgenommen; seine verbrauchte Einmalfreigabe wird nicht erneuert. Der vorliegende
Auftrag erlaubt ausschließlich Spezifikation und lesende Quellenhashprüfung.

## 1 Frage und feste Umfangsgrenze

Die offene Erwartung lautet: H hat auf Q in D einen geringeren mittleren MAE
als U. Begründete Hypothese ist die getrennte dauerhafte Zusammenfassung der
zwei tatsächlich wiederkehrenden Hinweise. Dies ist kein vorweggenommener Befund.
Ein Vorteil von H betrifft zwei Gesamtverfahren und darf weder allein der
Speicherkapazität noch allein der Mittelwertbildung zugeschrieben werden.

U bleibt der in HX1 gebundene MultiErrorAdapter, multi_error_exact_v1,
FactorRecencyArm, exact_v1, legacy_v1, alpha=1/2, Faktorenliste [1.0].
A1/K1 bleiben deaktiviert. Reguläre Aufnahme, Bestätigung, Promotion,
Kandidatenersetzung und Verdrängung unverändert. U wird später frisch ausgeführt,
nicht durch gespeicherte HX1-Fehlerreihen ersetzt. Kein Quellgenerator wird aufgerufen.

32 Paare r=1 bis 32, D vor N, je 1.024 Frames, 256 Vierframeblöcke. Je Geschichte
frische getrennte U/H-Instanzen und eigene Referenzen. Ausführungsfolge je Frame:
U und eigene Referenz, H und eigene Referenz; erst danach nächster Frame.
64 Geschichten, 128 Armläufe, 65.536 Quellframes, 131.072 Armverarbeitungen und
zusätzlich 131.072 unabhängige Referenzfortschritte. Kein Parallelworker.

## 2 Ausschließlich archivierte Quellen

`S2UC_UH1_QUELLENBINDUNG_20261004.json` bindet alle 64 ursprünglichen
`reports/s2uc/hx1-comparison-20261004-01/HX1-rr-C-source.json` über exakten Pfad,
Bytezahl, SHA256, Paar und Bedingung. Es bindet außerdem den ursprünglichen
HX1-Abschluss und dessen Manifest. Seine Reihenfolge ist r aufsteigend, D vor N.
Jeder Quellhash muss zugleich mit HX1-Manifest und HX1-Abschluss übereinstimmen.
Fehlende Datei, Hashabweichung, Duplikat oder zusätzliche Fallzuordnung sperrt
den gesamten Start. Kein Ersatz, Reparieren, erneutes Serialisieren oder Generieren.

Vor dem ersten Policy-Aufruf werden sämtliche Quellen lesend geprüft. Danach
vor jeder Geschichte erneut Bytezahl/SHA256 prüfen, dieselben geprüften Bytes
dekodieren und daraus genau einmal streamen. Originaldateien bleiben unverändert.
Keine Fallselektion anhand von H-Ausgaben; keine erneute HX1-Auswertung als
Auswahlregel. Quellenformat, Katalogwerte, Indexfolge, Längen und Zuordnung
werden unabhängig strukturell validiert, ohne das Erzeugungsrezept auszuführen.
Die vollständige Datei und die Labels bleiben im externen Loader.

Bekannte Quellen bedeuten Anschlussuntersuchung auf demselben Material, keine
unabhängige Replikation oder Prüfung auf ungesehenen Quellen. Ein Bootstrap
beseitigt diese Aussagegrenze nicht. Der zukünftige Bericht muss sie im Einstieg nennen.

## 3 Eingangsvertrag und H-Schlüssel

Nur aktueller normaler Frame mit 48 endlichen binary64-Komponenten und technischer
Index i=1 bis 1.024. Zeit/Scope wie HX1: [4800(i−1),4800i), owner=comparison,
stream=stream, armneutrales Profil ohne r/C/Orientierung. Keine X/Y-Labels,
Fortsetzungsprototypen, Fallnamen, Quoten, Manifest-, Archiv- oder Beobachterzugriffe.

H kennt die technische Vierframephase i mod 4. Diese Privilegierung wird gegenüber
U ausdrücklich offengelegt. Schlüssel ist die geordnete Konkatenation der ersten
zwei tatsächlich beobachteten Frames eines Blocks: 96 binary64-Werte, 768 Byte.
Vergleich vollständiger little-endian-Bitmuster; keine Hashschlüssel, Approximation,
Normalisierung oder Cluster. +0 und −0 sind unterschiedliche Schlüsselwerte.
NaN/Inf, falsche Dimension oder nicht aufeinanderfolgender Index sind terminal.
Die Quellenprüfung darf Namen kennen; sie darf sie nicht an die Prädiktoren reichen.
Das Profil bleibt bitgleich zum gebundenen HX1-Pfad:
`4309cfc91eb99fc2a999fdac99c5a7f1807ee654996e019ec0d94e3900bcbd4b`.
Es ist SHA256 der UTF-8-Bytes der kanonischen JSON-Zeichenfolge
`"HX1-schema-48-float64"` mit abschließendem LF, entsprechend der
unveränderten HX1-Funktion `source.digest('HX1-schema-48-float64')`.
Kein neuer fallabhängiger Profilwert und keine Änderung der U-Scope-Semantik.

## 4 Vollständige H-Zustandsmaschine

Genau zwei Slots, nummeriert 0 und 1. Je Slot: Schlüssel 768 Byte, Mittelwert
48×8=384 Byte, uint64 n, uint64 letzter gültiger Q-Feedbackstempel. n=0 bedeutet
leer; leere Nutzdaten und Stempel sind null. Keine Historie außerhalb dieser Slots.
Zählerbereich n=0 bis 256; Stempel/globaler Feedbackzähler t=0 bis 256. Technische
Indices höchstens 1.025. Jede Überschreitung stoppt vor Zustandsänderung.

Weitere persistente Zustände: Zweiframe-Puffer, eine Ausgabe, i, t,
pending_target sowie ein 8-Byte-Steuerwort für Phase, Pufferbelegung, closed,
pending_kind und pending_slot. Steuerdaten mit i/t/target insgesamt 32 Byte.
pending_kind ist NONE, KNOWN_Q, UNKNOWN_Q oder SKELETON;
pending_slot bei KNOWN_Q 0/1, sonst NONE als festes Sentinel. Ein leerer Slot
kann niemals KNOWN_Q sein. Externe Beobachter dürfen keine Steuerwerte ergänzen.

Initial: alles leer/null, i=t=0, pending_kind=NONE, closed=false. Jeder accept
prüft offenen Zustand, nächsten Index, Werte und erwartete Phase vor Mutation.

### Phase 1 eines Blocks, i=4b−3

Außer i=1 liegt die SKELETON-Prognose für genau diesen Index vor. Zuerst Ausgabe
gegen aktuellen Frame bewerten und Prognose konsumieren; kein Slotupdate.
Danach alten Puffer leeren und ersten beobachteten Hinweisframe hineinkopieren.
Keine neue Prognose. Bei i=1 ist pending_kind=NONE zwingend.

### Phase 2, i=4b−2

Zweiten Hinweisframe in Puffer kopieren; alle 96 Bitsätze linear gegen Slot 0,
dann Slot 1 vergleichen. Mehrere gleiche belegte Schlüssel wären ein technischer
Invariantenfehler. Bei Treffer Mittelwert in eigene Ausgabe kopieren;
pending_kind=KNOWN_Q, pending_slot=Trefferslot. Ohne Treffer zweiten Hinweisframe
in eigene Ausgabe kopieren; pending_kind=UNKNOWN_Q, pending_slot=NONE.
In beiden Fällen pending_target=i+1. Schlüssel bleibt im Puffer bis Q-Feedback.
Ausgabe ist eingefroren. Insbesondere keine Neuaufnahme, Ersetzung,
Zählererhöhung oder Aktualitätsänderung durch die Prognose.

### Phase 3, i=4b−1, beobachtetes Q-Ziel

Zuerst das zu diesem Index gehörige KNOWN_Q/UNKNOWN_Q-Ticket prüfen und MAE
aus der unveränderten eingefrorenen Ausgabe bestimmen. Ausgabe erst nach
Fehlerbeobachtung freigeben. Der Schlüssel stammt ausschließlich aus dem
vorherigen Zweiframe-Puffer; der aktuelle Zielwert darf ihn nicht verändern.

KNOWN_Q: Slot muss weiterhin denselben Schlüssel und n>=1 besitzen. Mit k=n+1
für j=0 bis 47 in dieser Reihenfolge: tmp1=y[j]−m[j], tmp2=tmp1/float(k),
m[j]=m[j]+tmp2. Jede einzelne Operation round-to-nearest/ties-to-even in
binary64; kein FMA, keine Umordnung, kein fsum, keine exakte Summenbank.
Dann n=k. Beobachtungen zählen auch bei Fehler null.

UNKNOWN_Q: erst jetzt kleinsten freien Slot wählen; bei voller Tabelle den
kleinsten Stempel, bei Gleichstand kleinere Slotnummer. Alten Slot vollständig
löschen, Schlüssel aus Puffer kopieren, Mittelwert aus aktuellem Ziel kopieren,
n=1. Keine Vorhersage mit diesem gerade eingetroffenen Ziel nachliefern.

Für beide Pfade anschließend t=t+1 und Stempel des betroffenen Slots=t.
Alle anderen Slots unverändert. Prognoseticket und Puffer leeren; pending_kind=NONE.
Ein Fehler während Kopieren/Rechnen/Export führt zum terminalen Ende ohne
weiteren accept-Aufruf; ein teilweise mutierter Zustand darf nicht fortgesetzt werden.

### Phase 4, i=4b

Aktuellen Frame in eigene Ausgabe kopieren: pending_kind=SKELETON,
pending_target=i+1, pending_slot=NONE. Kein Lernen. Nach Frame 1.024 liegt somit
die rechtszensierte Prognose für 1.025 vor; sie wird beim Ende ohne Fehlerwert
oder Feedback gelöscht. Genau 511 beobachtete Ausgaben und eine zensierte
Ausgabe pro Geschichte; davon 256 beobachtete Q-Ausgaben.

### Ausgabelebensdauer und Ende

Es existiert höchstens eine ausstehende Ausgabe. Ihre Werte dürfen zwischen
Freeze und Fehlerbeobachtung nicht geändert werden, auch nicht durch Slotupdate.
Kein Alias auf eine veränderliche Mittelwertbank. Externe Archivkopien erfolgen
vor Wiederverwendung des Ausgabeslots, sind unveränderlich und für H unerreichbar.
Eine frühere Ausgabe darf nicht als kostenloser armseitiger Rückgabeverlauf bleiben.

finish löscht Slots, Zähler, Stempel, Puffer, Ausgabe, Scratch und Ticket und setzt
closed=true. Danach sind accept und zweites finish technische Fehler; ein eigener
idempotenter abort-Cleanup darf beim Fehlerabschluss erneut versuchen zu löschen.
Ein abgebrochener Prozess begründet keinen erfundenen Cleanup-Erfolg. Weder
fehlendes noch doppeltes/vertauschtes Feedback wird toleriert.

## 5 Bewertung und vorab fixierte Statistik

MAE48 exakt wie HX1: total=0.0, j=0 bis 47 jeweils difference=abs(pred[j]−y[j]),
total=total+difference, abschließend total/48.0, einzeln binary64-gerundet.
Keine Umordnung oder FMA. Ein Mittelwert ist unter MAE nicht allgemein optimal.

Q={3,7,…,1023}, je Geschichte 256; G_all={3,5,…,1023}, 511;
S=G_all ohne Q, 255. Externe Q_X/Q_Y jeweils 128 werden aus dem archivierten
Quellkatalog gebildet und ausschließlich zur ergänzenden Auswertung benutzt.
Alle Q-Ziele zählen, kein Warm-up, Ausschluss unbekannter/kalter/verdrängter
Hinweise oder günstiges Zeitfenster. Je Bedingung 8.192 Q-Ziele je Arm.

m[r,C,a] ist der Mittelwert aller 256 Q-MAE. d[r,C]=m[r,C,U]−m[r,C,H].
Einziger Primärkontrast: theta=(1/32) sum_r d[r,D]. Erwartung theta>0.
Positive Werte bedeuten H-Vorteil. Primärurteil aus ungerundeten rationalen Werten:
untere 95%-Grenze>0: H_VORTEIL_BELEGT; obere<0: H_ERWARTUNG_WIDERLEGT_U_VORTEIL;
sonst LEISTUNGSRICHTUNG_NICHT_NACHGEWIESEN, einschließlich Grenze genau null.
Technischer Fehler überschreibt alles mit NICHT_AUSWERTBAR.

### Exakte Bootstrapregel

10.000 Ziehungen z=0,…,9999. Orientierung o=0: r=1,3,…,31;
o=1: r=2,4,…,32. Je o und k=0,…,15 die ersten acht SHA256-Bytes von
`MCM-UH1/bootstrap/v1/z={z}/orientation={o}/k={k}` als Big-endian uint64 u.
ASCII/UTF-8, Dezimalzahlen ohne führende Nullen, kein Zeilenumbruch.
Gewähltes r=2*(u mod 16)+1+o. Dieselbe 32er-Indexzeile für alle Bedingungen,
Arme und ergänzenden Masken; keine getrennte Ziehung einzelner Ziele oder D/N.
Die Regel ist hier vor jeder H-Ausführung fixiert. Matrix später vor Replay
erzeugen, unabhängig prüfen und ihre 320.000 Bytes (r−1 je Eintrag) per SHA256
in die neue Vorstartbindung aufnehmen. Dieser Spezifikationsauftrag erzeugt sie nicht.

Pro Ziehung ungewichteter Mittelwert der 32 Paarwerte. Sortieren, Quantile
q=1/40 und 39/40, h=9999q, lineare Interpolation zwischen floor/ceil(h).
Alle gespeicherten binary64-MAE als exakte rationale Zahlen aggregieren;
auch Kontraste, Mittel und Quantile rational. Nur Anzeige runden.
Ein Primärkontrast, keine Bonferroni-Aufteilung auf HX1-Kontraste.
Nominale approximative Intervalle, keine exakte Abdeckungs- oder Powerbehauptung.

### Vollständige ergänzende Bilanz

Je D/N und Q/G_all/S/Q_X/Q_Y: U/H-MAE, U−H, Zielzahl, alle 32 Geschichtenwerte;
zusätzlich getrennt je Orientierung mit 16 Geschichtenwerten. Explorative 95%-
Intervalle aus derselben Matrix, für Orientierung ausschließlich deren 16 Spalten.
Auch Q-Interaktion d[r,D]−d[r,N] mit 32 Paarwerten und explorativem 95%-Intervall.
Keine ergänzende Auswertung wird nachträglich zur Erfolgsregel erklärt.

Je Bedingung/Maske/Orientierung: Zahl U besser/schlechter/gleich,
Gewinn_U=sum max(eH−eU,0), Schaden_U=sum max(eU−eH,0), Netto=Gewinn−Schaden,
maximaler Einzelschaden und sämtliche zugehörigen (r,C,Ziel)-Positionen,
schlechtester Geschichtenmittelwert von U−H. Jede Summe exakt gegen alle
Zielreihen prüfen; überlappende Masken nicht addieren. Kumulierte Differenzen
für alle G_all-Ziele und separat Q vollständig archivieren.

H bekannte/unbekannte Hinweise und Slotersetzungen, U-V0–V3 nach HX1 sowie
ihre jeweiligen Gewinn-/Schadensbeiträge vollständig deskriptiv partitionieren.
U-Zellenalter, fehlende Spuren oder H-Verfügbarkeit erklären mögliche Gelegenheiten,
beweisen aber keinen isolierten kausalen Mechanismus. Kein N-Gleichwertigkeitsurteil
aus einem nicht signifikanten Unterschied.

## 6 Unabhängige Referenzen und neutrale Prüfungen

Eigene U-Referenz wie im HX1-Vertrag: unabhängiger Bestand, Aufnahme,
Lebenszyklus, Abruf, EC/EP, Berechtigungen, Auswahl, Feedback und Cleanup.
Neue H-Referenz: eigener Zweislotspeicher und eigene Zustandsmaschine aus den
aktuellen Frames, keine Produktionsschlüssel, Slotwahl, Mittelwerte oder Tickets
als erwartete Daten übernehmen. Jede Operation eigene binary64-Rundung;
gemeinsame unveränderliche Eingaben und Standard-Hashprimitive zulässig.
Vor/nach jedem Schritt Schlüsselbits, n, Stempel, Ticket, Ausgabe und Bank
vergleichen. Eigener Fehlerprüfer rekonstruiert MAE aus Output/Ziel.
Statistikreferenz: unabhängige Reduktion aus Zielarchiven, unabhängige Ziehungs-
indexberechnung und Quantilinterpolation; nicht bloß Produktionskontraste kopieren.

Neutrale Prüfungen erst nach gesondertem Entwicklungsauftrag. Keine HX1-Quelle
zum Entwickeln von H ausführen; synthetische Handvektoren getrennt halten.

| Prüfung | Pflichtinhalt und Abnahme |
| --- | --- |
| N1 Eingang und Bitgleichheit | Dimension, Index, NaN/Inf terminal; ein Bit verschieden, vertauschte Framefolge und +0/−0 unterscheiden Schlüssel; keine Labels oder Zukunft im Input |
| N2 Erstaufnahme und Freeze | Hinweis a unbekannt: Persistenz vor erstem Ziel; davor beide Slots leer; erst Feedback belegt Slot 0 mit n=1. Zweites Auftreten gibt alten Mittelwert aus, Zieländerung ändert diese Ausgabe nicht |
| N3 Zwei Slots und Verdrängung | Getrennte Hinweise a,b,c aus Handwerten. Feedbackfolge a,b,a,c ergibt Stempel a=3,b=2; c verdrängt b und bekommt 4. Erneutes b zunächst unbekannt/Persistenz, erst sein Ziel verdrängt a und erhält 5. Kein Altmittelwert kehrt zurück |
| N4 Rundung und Tickets | Komponentenweise Handbeispiele einschließlich rundungsempfindlicher Werte; Ziel vor Update; bekannte/unbekannte Tickets mit falschem Ziel/Slot, doppeltes Feedback, veränderte Ausgabe und Zustandsalias terminal; einheitliche Quellenphase |
| N5 Grenzen und Cleanup | n/t=256 zulässig, nächstes Feedback terminal vor Mutation; Slotstempelgleichstand über neutralen Referenzzustand: kleiner Slot. Leere Geschichte/Teilblock unzulässig. Letzte Prognose zensiert, Nullung und closed; Abbruch an jedem Mutationsabschnitt; keine Fortsetzung |
| N6 U und Statistik | Bestehende relevante U-Regressionen; injizierte Referenzabweichung erkannt. Handtabellen für positiven/negativen/Nullrand, Paarzuordnung, 16+16-Schichtung, Zielvollständigkeit und exakte Gewinn-/Schadenspartition. Falsche Matrix/Quantile terminal |
| N7 Ressourcen und Export | Volltabelle plus dritter Hinweis; Treffer/Miss/Ersetzung/Fehlerpfade transient messen; Outputcopy und temporäre Schlüsselbytes zählen. Datei-/Gesamtgrenzen, Code-/Quellenmanipulation, fehlende Freigabe, existierender Zielordner, Timeout, Speicherablehnung, Workercrash und terminaler Abschluss prüfen |

Nach bestandenen N1–N7 höchstens ein vollständig beauftragter neutraler Größenablauf
mit 64×1.024 Frames und U/H samt Referenzen. Neutrale Blockliste aus dem HX1-
Vertrag Abschnitt 7 (acht feste Blöcke, Rotation (b+r−2) mod 8, in N nur
Hinweise tauschen); keine Forschungsquellen und keine Nutzeninterpretation.
Der dritte Hinweis wird in N3/N7 geprüft, nicht als dritte Forschungsvariante.
Größenablauf und Entwicklung bleiben bis zu gesondertem Auftrag geschlossen.

## 7 Vollständige Ressourcenrechnung

H erhält keine unbegrenzte Tabelle und keine kostenlos erreichbare Beobachterhistorie.

| H eigener numerischer Zustand | Byte |
| --- | ---: |
| Zwei Schlüssel mit je 96 binary64 | 1536 |
| Zwei Mittelwerte mit je 48 binary64 | 768 |
| Zwei uint64-Zähler und zwei Stempel | 32 |
| i, t, pending_target, Steuerwort | 32 |
| Ein Zweiframe-Puffer | 768 |
| Eine eigene eingefrorene Ausgabe | 384 |
| Temporärer Vektor und drei Rechenskalare, auch beim Ersetzen | höchstens 408 |
| Eigene numerische Gesamtbelegung einschließlich Transienten | höchstens 3928 |

H: harte numerische Grenze 4096 Byte; gesamter eigener Python-Heap einschließlich
Container, Schlüsselrepräsentation, Steuerobjekte, Ausgaben und temporärer
Kopien 32768 Byte. Kein zusätzlicher 768-Byte-Schlüsselabzug außerhalb dieser
Grenzen. Vergleiche und Kopien müssen mit diesem Scratch auskommen.
Geliehen höchstens ein aktueller Eingangsframe, 384 Rohbytes; sein vollständiger
Python-Objektgraph wird separat gemessen. Nach accept keine Referenz darauf:
benötigte Daten befinden sich in eigenen Puffern. Keine armseitigen Receipts;
0 Receiptbytes, kein armseitiger Serializer oder interner Fehlertextaufbau.

Fehlermeldung durch festen externen Fehlercode; Fehlerpfad darf keine Bank-
oder Quellenkopie im Arm aufbauen. Exceptions/Tracebacks und externe Diagnose-
kopien zählen zum gemeinsamen Prozesslimit und zu den Exportbudgets. Kein
unbegrenztes Tracebackarchiv. Abbruchspeicher und Nullung müssen neutral gemessen
werden, einschließlich Allokationsfehlern. Eine externe Kopie zählt nur dann
extern, wenn H keine Referenz hält oder Zugriffsmöglichkeit besitzt.

U unverändert: Bank 416 Byte, Zusatzheap höchstens 16384 Byte nach bestehender
Zählgrenze; höchstens zwei Retained-Spuren und ein Kandidat. Konservative
Originalframegrenze 18 und kombinierte Original-/Ausgabeslotgrenze 20 gemäß
HX1-Vertrag; zwei Ausgabeslots. Receipt 16384 Byte, transiente UTF-8-Obergrenze
32768 Byte, keine zusätzlichen Freibeträge. Basis-/Originalobjekte, erreichbarer
Gesamtgraph und neue Ausgabeanteile separat ausweisen.

Je Arm Grenzstelleninventar UND transiente Heapspitzen messen. Für H ist
gesamter Eigenheap, für U Zusatzheap begrenzt; nicht als gleiche Messgröße
ausgeben. Eingangs-, Beobachter-, Referenz- und Berichtsspeicher vollständig
als externe Prozesskosten erfassen; deren Historie ist keine Arm-Memory.
Auch fehlgeschlagene Pfade zählen, keine Auslagerung zur Umgehung einer Grenze.
Die 3928 Byte sind ein Entwurfsmaximum, kein bereits erbrachter Laufnachweis.

Ein Supervisor und höchstens ein Worker. Gesamtzeit 3600 s einschließlich
Startprüfung, Archivlesen, Referenzen, Statistik, Export und Abschluss;
Workerfrist spätestens Supervisorstart+3540 s, 60 s Abschlussreserve.
Gemeinsamer privater Commit höchstens 536870912 Byte, harter Windows-Job für
Supervisor und Worker; konkrete Mitgliedschaft und konfigurierte Grenze prüfen.
HX1-Speicherklarstellung bleibt gültig: Roh-Peak kann abgewiesene Anträge
enthalten; konservativ jeder Roh-Peak über Limit terminal NICHT_AUSWERTBAR.
Kein Abschwächen dieser Regel für UH1.

Gesamtexport einschließlich Vorbereitung, Quellen und Fehlerbelegen 64 MiB;
Vorbereitung 8 MiB; alle Quellen 2 MiB, je Datei 32 KiB;
64 Fallarchive zusammen 32 MiB, je Fall 512 KiB gzip/4 MiB expandiert;
Verwaltung und vollständige Auswertung 2 MiB; Abschlussreserve 1 MiB.
Quellen werden als gebundene externe Eingangsdaten mit voller Bytezahl belastet,
auch ohne neue Kopie. Doppelte physische Pakete zählen mehrfach, referenzierte
identische Dateien einmal je kanonischem Paket. Quellenbindung zählt Vorbereitung.
Kein Einlesen des gesamten HX1-Ergebnisarchivs als versteckter UH1-Eingang.

Kompression gzip Level 9, mtime=0, kein Dateiname; Python, Interpreter/DLL und
Kompressionsruntime vorab binden. Vollständige U-Lebenszyklen und H-Pre-/Post-
zustände, Tickets, Schlüsselbits, Ausgaben, Fehler, Updates und Ersetzungen
verlustfrei exportieren; Delta-/ID-Kodierung nur mit unabhängiger Rekonstruktion.
Keine Kürzung zur Budgeteinhaltung. Alle Budgets vor Start neutral nachweisen.

## 8 Startbedingungen und terminale Regeln

Dieser Vertrag, Quellenbindung und Paketbindung erlauben noch keinen Start.
Erforderliche Abfolge:

1. Fachliche Vertragsabnahme und gesonderter begrenzter Entwicklungsauftrag.
2. Implementierung einschließlich unabhängiger Referenzen; N1–N7 und höchstens
   ein beauftragter neutraler Größenablauf bestanden, vollständige Ressourcenrechnung.
3. Neue UH1-Code-/Runtimebindung einschließlich unverändertem U-Abhängigkeitsbestand,
   H, Loader, Referenzen, Statistik, Export, Vertrag, Quellenbindung, Bootstrapmatrix,
   neutralen Belegen und exakten Aufrufparametern. Vorstart-SHA256 vor Forschungsstart.
4. Neue separate einmalige Forschungsbeauftragung, die exakt diesen UH1-Vorstart
   referenziert. Eine operative Autorisierung darf erst dann entstehen. HX1-Autorisierung
   und ein allgemeines WEITER erfüllen diese Bedingung nicht.

Exklusiver geplanter Zielordner `reports/s2uc/uh1-comparison-20261004-01`;
er wird jetzt nicht angelegt. Der spätere Start reserviert vor Policyzugriff einen
unveränderlichen Versuchsmarker. Bestehender Ordner/Marker sperrt Neustart.
Erforderliche Autorisierungsfelder: action=UH1_32_KNOWN_PAIRS_UH_ONCE,
status=AUTHORIZED_ONCE, exakter Vorstart- und Quellenbindungs-SHA256,
genannter Zielordner, arms=[U,H], cases=64, frames_per_case=1024,
Q_targets_per_case=256, primary_pairs=32, total_seconds=3600,
process_bytes=536870912, export_bytes=67108864. Keine alternative Parameterform.
Die spätere Implementierung muss ihren konkreten Aufruf vor neutraler Qualifikation
fixieren; dieser Vertrag behauptet keinen heute existierenden Starter.

Alle Bindungen vor Ausführung prüfen, alle Quellen vor erstem Replay vollständig
validieren. Bindungsabweichung: kein Replay. Jeder technische Fehler verbraucht
einen bereits gestarteten autorisierten Versuch; kein Resume, Retry oder Ersatzfall.
Worker bei Frist/Fehler beenden und Ende belegen; Fehlercode, Phase, r/C/Arm/Ziel
soweit bekannt, erstes abweichendes Artefakt, vollständige/teilweise Einheiten,
Dateilängen/-hashes, Ressourcen und Cleanupstatus terminal protokollieren.
Fehlender terminaler Beleg bedeutet unvollständig, niemals implizit COMPLETE.

COMPLETE nur bei allen 64 Quellen/128 Armläufen, Referenzen, Zielreihen,
Statistikprüfungen und Grenzen sowie beendetem Worker. Keine Nutzenentscheidung
aus einem unvollständigen Teilbestand. Abschluss enthält Primärintervall/Urteil,
sämtliche sekundären Werte, Verfügbarkeit, Gewinne/Schäden, Ressourcen, Bindungen
und die Kennzeichnung UNTERSUCHUNG_AUF_BEKANNTEN_QUELLEN.

## 9 Abnahme und nächste Entscheidung

Eine bessere Leistung von H hebt HX1 nicht auf. Sie begrenzt den Nutzen von U
gegenüber genau diesem einfachen hinweisabhängigen Verfahren. Umgekehrt belegt
ein U-Vorteil weder allgemeine Überlegenheit noch Semantik, Cluster oder Feld-Memory.
Weder Tabellenkapazität, Phasenwissen, dauerhafte Schlüsselverfügbarkeit noch
Mittelwertbildung wird durch U/H isoliert kausal geprüft.

Nächster vorgeschlagener Schritt: Projektleiter nimmt diesen vollständigen Vertrag
ab und entscheidet anschließend über genau ein begrenztes Implementierungs- und
neutrales Qualifikationspaket. Forschungsfreigabe bleibt danach separat erforderlich.

Referenzen: [HX1-Vertrag](S2UC_HX1_PRUEFVERTRAG_20261004.md),
[HX1-Ergebnis](../reports/s2uc/hx1-assessment-20261004-01/REPORT.md),
[Speicherklarstellung](../reports/s2uc/hx1-memory-clarification-20261004-02/REPORT.md),
[Quellenbindung](S2UC_UH1_QUELLENBINDUNG_20261004.json),
[Spezifikationspaket](S2UC_UH1_SPEZIFIKATIONSBINDUNG_20261004.json).
