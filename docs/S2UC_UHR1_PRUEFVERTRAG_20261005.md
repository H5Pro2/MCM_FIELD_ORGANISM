# UHR1 Prüfvertrag: unabhängige Wiederholung von U/H auf neuen Folgen

Stand 2026-10-05. Vertragskennung `MCM-UHR1-v1-20261005`.
Status `KONZEPTIONELL_VORREGISTRIERT_KEINE_IMPLEMENTIERUNGS_ODER_LAUFFREIGABE`.
Empfänger: Projektleiter; erstellt durch den MCM-KI-Entwickler.

Dieser zusammenhängende Vertrag ist der Abnahmegegenstand. Er übernimmt die
unveränderten U/H-Verfahren aus dem abgeschlossenen UH1-Vergleich und legt
32 neue D/N-Paare derselben Aufgabenfamilie fest. Heute werden ausschließlich
Dokumente und Bindungen bestehender Dateien erstellt. Es werden weder Quellen
noch Bootstrapziehungen erzeugt oder gesichtet, keine Policies ausgeführt und
keine neutrale Qualifikation gestartet. UHR1 ist eine Dokumentkennung, keine Laufnummer.

## 1 Forschungsfrage und unveränderte Verfahren

Bleibt der in UH1 beobachtete U-Vorteil gegenüber H auf bisher ungetesteten
Folgen derselben Aufgabenfamilie bestehen? Erwartung: mittleres U−H in D < 0.
Das ist eine vorab festgelegte Hypothese, kein neuer Befund. Die bekannten
UH1-Ergebnisse motivieren diese Wiederholung, werden aber weder als zusätzliche
Beobachtungen noch zur Anpassung von Schwellen, Varianten oder Stichprobengröße benutzt.

U bleibt MultiErrorAdapter, multi_error_exact_v1, FactorRecencyArm, exact_v1,
legacy_v1, alpha=1/2 und Faktorenliste [1.0]. A1/K1 bleiben aus. Aufnahme,
Bestätigung, Promotion, Kandidatenersetzung, Verdrängung, Feedback und
EC/EP-Auswahl bleiben bitgleich. Zwei Retained-Vierframespuren und ein Kandidat;
eine gerade entstehende Spur ist kein zusätzlicher abrufbarer Speicher.
H bleibt die implementierte Zweischlüssel-Mittelwertbank aus UH1, vollständig
in Abschnitt 4 festgehalten. Keine Parameteroptimierung oder zusätzliche Variante.

Die Verfahren besitzen unterschiedliche Speicherrepräsentationen und Grenzen.
H kennt die Vierframephase und hält die beiden wiederkehrenden Schlüssel samt
Mittelwerten dauerhaft; U kann nicht alle vier Hinweis-Fortsetzungs-Kombinationen
als Retained-Spuren zugleich halten. Das ist ein Vergleich zweier Gesamtverfahren,
keine Gleichheit der Information oder Ressourcen und keine isolierte Prüfung
von Mittelwertbildung, Speicherkapazität oder Phasenwissen.

Ausführungsreihenfolge: r=1 bis 32, jeweils D vor N; je Geschichte 1.024 Frames
in 256 Vierframeblöcken. Frische getrennte U/H-Instanzen und eigene Referenzen
für jede Geschichte, keine Übernahme aus UH1 oder zwischen Geschichten.
Je Frame U und U-Referenz, dann H und H-Referenz, danach nächster Frame.
64 Geschichten, 128 Armläufe, 65.536 Quellframes, 131.072 Armverarbeitungen
und zusätzlich 131.072 unabhängige Referenzfortschritte. Kein Parallelworker.

## 2 Vorab festgelegtes neues Quellenrezept

### Namensraum und Ziehungsprimitive

Exakter neuer Forschungsnamensraum:
`MCM-UHR1/source/v1/r={r}/stream={s}/draw={d}`.
Die statische Suche vor Erstellung dieses Vertrags nach MCM-UHR1, S2UC_UHR1
und uhr1-comparison in docs, tools, tests, reports sowie README und Forschungsweg
des aktuellen Projekts ergab keinen Treffer. Das belegt die bisherige Nichtnutzung
im geprüften Projektbestand; eine weitergehende historische Garantie wird nicht behauptet.
Der Namensraum wird nicht anhand erzeugter Folgen ausgewählt oder gewechselt.

r=1,…,32. Je r vier getrennte Streams mit exakt diesen s-Werten:
`continuation`, `dependent-A`, `dependent-B`, `null-cue`.
Jeder Stream beginnt unabhängig bei d=0. SHA256 der exakten UTF-8-Zeichenfolge,
Dezimalzahlen ohne führende Nullen, kein abschließender Zeilenumbruch; die ersten
acht Digestbytes als unsigned Big-endian-64-Bit-Zahl u. Für randbelow(n),
1<=n<=256, M=2^64 und L=M−(M mod n): u<L akzeptieren und u mod n liefern,
sonst nächste Ziehung desselben Streams. d wird auch bei Ablehnung erhöht;
auch n=1 verbraucht eine Ziehung. Höchstens 4.096 Rohziehungen je Stream,
Überschreitung terminal, kein Ersatzstream.

Shuffle ist Fisher-Yates: bei Länge m nacheinander i=m−1,…,1,
j=randbelow(i+1), Elemente i/j tauschen. Auch gleiche Werte tauschen;
kein Zufallssortieren. Getrennte SHA-Namensräume liefern deterministisch getrennte
pseudorandomisierte Folgen; dies ist keine mathematische Unabhängigkeitsgarantie
für SHA256. Keine Deduplikations-, Schönheits- oder Leistungsfilter.

### Katalog, Quoten und Orientierung

V(x)[j]=x+j/4096 für j=0,…,47, exakt in binary64 darstellbar.
Katalogreihenfolge: V(1/8), V(7/8), V(1/2), V(1/4), V(3/4), V(1/16).
Hinweis X=(V(1/8),V(1/2)), Y=(V(7/8),V(1/2));
Fortsetzungen A=V(1/4), B=V(3/4); Schlussframe R=V(1/16).
Jeder Block ist [erster Hinweisframe, V(1/2), Fortsetzung, R].

T_r = Shuffle([A]×128 gefolgt von [B]×128) mit continuation.
D und N desselben Paars verwenden exakt dieses T_r. Aufsteigend geordnete
nullbasierte A-Positionen in T_r mit dependent-A mischen, B-Positionen analog
mit dependent-B. Für ungerades r erhalten die ersten 96 A-Positionen und
32 B-Positionen X; für gerades r die ersten 32 A- und 96 B-Positionen X.
Alle übrigen Positionen erhalten Y. Orientierung o=(r−1) mod 2,
16 Paare je Orientierung. D-Kontingenz (XA,XB,YA,YB): ungerade
(96,32,32,96), gerade (32,96,96,32). Je Geschichte 128 X,128 Y,128 A,128 B.

N-Hinweise = Shuffle([X]×128 gefolgt von [Y]×128) mit null-cue,
gepaart mit demselben T_r. Die N-Kontingenz wird unverändert berichtet;
keine künstliche 64/64/64/64-Balance. Die festen Gesamtquoten erzeugen zeitliche
Abhängigkeiten. Unabhängige N-Hinweiszuteilung bedeutet nicht, dass eine konstante
Vorhersage unter Kenntnis des bisherigen Verlaufs optimal sein muss.

### Materialisierung erst nach separater Forschungsfreigabe

Geplante Fallkennungen UHR1-01-D bis UHR1-32-N; IDs, r/C/o und Quoten bleiben
im externen Beobachter. Quellenrecord wie HX1: catalog, ids (1.024 Katalogindices),
neutral_only=false, draws (alle vier Rohziehungszähler). Kanonische JSON-Bytes:
json.dumps mit sort_keys=True, separators=(',', ':'), allow_nan=False,
abschließend LF, UTF-8; Runtime vorab binden. Keine zusätzliche Zufallsquelle.

Später alle 64 Quellen vollständig erzeugen, durch eine eigene Implementierung
des Rezepts prüfen und Manifest mit Fall, Paar, Bedingung, Orientierung, Pfad,
Länge, SHA256 und Ziehungszählern versiegeln, bevor irgendein Policy-Aufruf erfolgt.
Vor jeder Geschichte dieselben Bytes erneut auf Länge/Hash prüfen und daraus streamen.
Die unabhängige Rezeptprüfung erfolgt im selben autorisierten Versuch und Budget;
sie ist keine zweite Materialauswahl. Keine Handkorrektur oder Ersatzquelle.
Entwicklungsprüfungen verwenden ausschließlich Handvektoren beziehungsweise
`MCM-UHR1/neutral/v1/r={r}/stream={s}/draw={d}`, nie den Forschungsnamensraum.
Neue Quellen werden nicht aus alten Fehlerreihen rekonstruiert oder selektiert.

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
Einziger Primärkontrast: theta=(1/32) sum_r d[r,D]. Erwartung theta<0.
Positive Werte bedeuten H-Vorteil. Primärurteil aus ungerundeten rationalen Werten:
untere 95%-Grenze>0: H_VORTEIL_BELEGT; obere<0: U_VORTEIL_REPLIZIERT;
sonst KEIN_EINDEUTIGER_UNTERSCHIED_NACHGEWIESEN, einschließlich Grenze genau null.
Technischer Fehler überschreibt alles mit NICHT_AUSWERTBAR.

### Exakte Bootstrapregel

10.000 Ziehungen z=0,…,9999. Orientierung o=0: r=1,3,…,31;
o=1: r=2,4,…,32. Je o und k=0,…,15 die ersten acht SHA256-Bytes von
`MCM-UHR1/bootstrap/v1/z={z}/orientation={o}/k={k}` als Big-endian uint64 u.
ASCII/UTF-8, Dezimalzahlen ohne führende Nullen, kein Zeilenumbruch.
Gewähltes r=2*(u mod 16)+1+o. Dieselbe 32er-Indexzeile für alle Bedingungen,
Arme und ergänzenden Masken; keine getrennte Ziehung einzelner Ziele oder D/N.
Die Regel ist hier vor jeder UHR1-Ausführung fixiert. Matrix später vor Replay
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
Unveränderte unabhängige H-Referenz aus UH1: eigener Zweislotspeicher und eigene Zustandsmaschine aus den
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
Die 3928 Byte sind das übernommene konservative Maximum. Die gepackte
H-Bank umfasst 3520 Byte. Frühere UH1-Messungen ersetzen keinen UHR1-Nachweis.

Ein Supervisor und höchstens ein Worker. Gesamtzeit 3600 s einschließlich
Startprüfung, vollständiger Quellenerzeugung und Rezeptprüfung, Archivlesen,
Referenzen, Statistik, Export und Abschluss;
Workerfrist spätestens Supervisorstart+3540 s, 60 s Abschlussreserve.
Gemeinsamer privater Commit höchstens 536870912 Byte, harter Windows-Job für
Supervisor und Worker; konkrete Mitgliedschaft und konfigurierte Grenze prüfen.
HX1-Speicherklarstellung bleibt gültig: Roh-Peak kann abgewiesene Anträge
enthalten; konservativ jeder Roh-Peak über Limit terminal NICHT_AUSWERTBAR.
Kein Abschwächen dieser Regel für UHR1. Windows-Job-Limitflag 0x200;
Supervisor und genau ein Worker müssen demselben Job angehören.

Gesamtexport einschließlich Vorbereitung, Quellen und Fehlerbelegen 64 MiB;
Vorbereitung 8 MiB; alle Quellen 2 MiB, je Datei 32 KiB;
64 Fallarchive zusammen 32 MiB, je Fall 512 KiB gzip/4 MiB expandiert;
Verwaltung und vollständige Auswertung 2 MiB; Abschlussreserve 1 MiB.
Quellen werden als gebundene externe Eingangsdaten mit voller Bytezahl belastet,
auch ohne neue Kopie. Doppelte physische Pakete zählen mehrfach, referenzierte
identische Dateien einmal je kanonischem Paket. Quellenbindung zählt Vorbereitung.
Kein Einlesen des gesamten HX1-Ergebnisarchivs oder UH1-Ergebnisarchivs als versteckter UHR1-Eingang.

Kompression gzip Level 9, mtime=0, kein Dateiname; Python, Interpreter/DLL und
Kompressionsruntime vorab binden. Vollständige U-Lebenszyklen und H-Pre-/Post-
zustände, Tickets, Schlüsselbits, Ausgaben, Fehler, Updates und Ersetzungen
verlustfrei exportieren; Delta-/ID-Kodierung nur mit unabhängiger Rekonstruktion.
Keine Kürzung zur Budgeteinhaltung. Alle Budgets vor Start neutral nachweisen.

### Ergänzende Bindungen für die Wiederholung

Die Bootstrapmethode einschließlich Paaraggregation, 16+16-Schichtung und
Quantilinterpolation bleibt identisch zu UH1. Ausschließlich ihr deterministischer
Namensraum wird auf UHR1 festgelegt; keine Suche unter Ziehungsmatrizen.
Die Matrix wird erst im separat beauftragten Vorbereitungspaket erzeugt und
unabhängig gebunden, vor jeder Forschungsquellenerzeugung. Heute nur Rezeptbindung.
Alle Primär- und Sekundärwerte stammen ausschließlich aus den neuen 32 Paaren.
Kein Pooling mit UH1, kein kombiniertes Intervall, keine kombinierte Erfolgsregel.
Ein späteres deskriptives Nebeneinander muss die beiden Studien getrennt ausweisen.

Die 30 ergänzenden Bedingungs-/Masken-/Orientierungsbilanzen sind vollständig
zu liefern. U-V0=kein Kontext, V1=kalt, V2=warm/Persistenz, V3=warm/Kontext;
H-Treffer/Miss und Ersetzungen werden einschließlich Nullbelegungen berichtet.
Leere Untergruppen: Anzahl 0, Mittelwert nicht definiert, nicht künstlich 0.
Es gibt keinen zusätzlichen konfirmatorischen Test auf N oder Untergruppen.
Je Arm sind über D/N 32.704 beobachtete Ziele einschließlich 16.384 Q-Ziele
vollständig enthalten; je Bedingung und Arm 8.192 Q-Ziele.

Zusätzlich zu den übernommenen N1–N7 sind später neutral zu qualifizieren:
Forschungsnamensraum ohne Freigabe unerreichbar; Produktions- und unabhängiger
Referenzgenerator stimmen auf neutralen Streams überein; Ablehnungsgrenze L−1/L,
n=1 und 4.096-Grenze; D-Quoten/orientierte Zuteilung, geteilte T-Folge,
unveränderte zufällige N-Kontingenz; vollständiges Manifest vor erstem Arm;
manipulierte Quelle/Bindung terminal; neue Urteile einschließlich exakter Nullgrenze.
Keine alten Forschungsquellen als Entwicklungstest. Ein neutraler Größenablauf
bedarf des gesonderten Auftrags; heutige Dokumentprüfung ist keine Qualifikation.

Gzip-Fallarchive bleiben Level 9, mtime=0 und ohne Dateiname. Ein vorbereitendes
LZMA-Paket darf nur mit vorab gebundenem Format und unabhängiger vollständiger
Rekonstruktion benutzt werden; seine Bytezahl zählt zur Vorbereitung. Freier Rest
des 64-MiB-Gesamtbudgets erweitert keine Teilgrenze. Ein deaktivierter Rohtrace
ist keine Messung von null Speicherbelegung. Auch die Quellenerzeugung und ihre
Referenz laufen innerhalb desselben Prozess-, Zeit- und Exportbudgets.

## 8 Verfahrensbindung, Startbedingungen und Abbruch

Die begleitende [Vorregistrierungsbindung](S2UC_UHR1_VORREGISTRIERUNGSBINDUNG_20261005.json)
bindet diesen Vertrag und bestehende Ausgangsartefakte per SHA256/Bytezahl.
Sie dokumentiert die statische Übereinstimmung des vollständigen 150-Dateien-
Bestands mit der UH1-Codebindung. Sie ist keine operative Vorstartbindung.
Die historischen Dateien, ihre Hashes und ihre verbrauchten Freigaben bleiben
unverändert. U/H und deren laufwirksame Abhängigkeiten bleiben bitgleich.

Neue Dateien sind später ausschließlich für UHR1-Quellenzugang, Einmalstart,
Manifest, Bootstrap-Namensraum und Ergebniskennzeichnung zulässig. Der bisherige
UH1-Loader für bekannte Quellen ist kein Loader für UHR1. Neue Hüllen dürfen
Policy, Feedback, Reihenfolge, Numerik oder Speichergrenzen nicht ändern.
Eine Abweichung des Verfahrens erfordert vorab einen neuen fachlichen Auftrag;
keine stillschweigende Reparatur durch Tuning.

Verbindliche Reihenfolge nach diesem konzeptionellen Abschluss:

1. Projektleiter prüft diesen Vertrag und beauftragt gesondert das begrenzte
   Implementierungs- und neutrale Qualifikationspaket.
2. Neue Hülle und unabhängige Rezept-/Statistikprüfung implementieren; neutrale
   Nachweise einschließlich Ressourcen und terminalen Fehlerpfaden erbringen.
   Keine Forschungsquelle dabei erzeugen oder sichten.
3. Vollständige transitive Code-/Runtimebindung, Vertrag, Rezept, geprüfte
   Bootstrapmatrix, neutrale Belege und exakten Aufruf in neue Vorstartbindung
   aufnehmen. Runtime umfasst Interpreter, DLL, Byteorder und Kompressionsruntime.
4. Separate einmalige Forschungsfreigabe referenziert genau diese Vorstartbindung.
   Erst danach operative Autorisierung und genau ein Versuch einschließlich
   Quellenmaterialisierung. Ein allgemeines WEITER oder eine alte UH1-/HX1-
   Autorisierung genügt nicht. Keine Quellenhashes vor Materialisierung erfinden.

Geplanter exklusiver Zielordner `reports/s2uc/uhr1-comparison-20261005-01`;
er wird heute nicht angelegt. Exklusiver unveränderlicher Versuchsmarker muss
vor Forschungsquellenerzeugung entstehen. Vorhandener Ordner/Marker sperrt
Neustart. Keine Überschreibung oder Änderung des Namensraums bei Kollision.
Die späteren Autorisierungsfelder sind action=UHR1_32_NEW_PAIRS_UH_ONCE,
status=AUTHORIZED_ONCE, exakter Vorstart-SHA256 und Rezept-/Vertrags-SHA256,
source_namespace=MCM-UHR1/source/v1, dieser Zielordner, arms=[U,H], cases=64,
frames_per_case=1024, Q_targets_per_case=256, primary_pairs=32,
total_seconds=3600, process_bytes=536870912, export_bytes=67108864.
Das Quellmanifest entsteht erst innerhalb dieses Versuchs; es wird vor Replay
versiegelt und im Abschluss gebunden. Heute existiert kein UHR1-Starter.

Jede Bindungsabweichung vor Start sperrt die Ausführung. Nach Reservierung des
Versuchsmarkers verbraucht jeder technische Fehler den Versuch, auch bei
Quellenerzeugung vor dem ersten Arm. Kein Resume, Retry, Ersatzfall, Teilpooling,
Zwischenentscheid anhand von Leistung oder vorzeitiger Erfolgsstopp.
Terminale Fehler: Generatorlimit, ungültige Quoten/Länge/Dimension/Indices,
Manifest-/Hashabweichung, Referenz-/Numerik-/Ticketabweichung, fehlende Ziele,
Ausgabealias, Ressourcenüberschreitung, Workerfehler oder fehlender Abschluss.
Bei Frist/Fehler Worker beenden und Ende belegen. Roh-Peak über Grenze ist
NICHT_AUSWERTBAR, auch wenn eine Allokation abgewiesen wurde.

Fehlerabschluss: Fehlercode, Phase, r/C/Arm/Ziel soweit bekannt, erstes
abweichendes Artefakt, vollständige/teilweise Einheiten, Dateilängen/-hashes,
Ressourcen, Workerexit und tatsächlich belegter Cleanupstatus. Kein erfundener
Cleanup nach Prozessabbruch. Fehlender Abschluss bedeutet unvollständig.
COMPLETE nur mit 64 validierten Quellen, 128 vollständigen Armläufen,
allen Referenzfortschritten und Zielreihen, unabhängiger Statistikprüfung,
eingehaltenen Grenzen und beendetem Worker. Sonst NICHT_AUSWERTBAR ohne
Leistungsurteil. Vollständiger Abschluss enthält alle drei möglichen Primärurteile
als Regel, das tatsächlich zutreffende Urteil, Sekundärbilanzen, Bindungen,
Ressourcen sowie Kennzeichnung NEUE_FOLGEN_DERSELBEN_AUFGABENFAMILIE.

## 9 Aussagegrenze und nächster Umsetzungsschritt

Ein vollständig negatives nominales 95%-Intervall bestätigt den U-Vorteil in
 dieser vorregistrierten Wiederholung auf neuen Folgen derselben Aufgabenfamilie.
Ein vollständig positives Intervall belegt hier H-Vorteil; Null enthaltend oder
berührend bedeutet keinen eindeutigen Unterschied, nicht Gleichwertigkeit.
Die Aussage betrifft exakt diese Verfahren, Quellenregeln, Länge und Quoten.
Kein Transfer auf andere Aufgaben, neue Hinweisalphabete, Audio/Video,
allgemeine Kognition, Semantik, Cluster oder feldinterne Memory. Der bekannte
UH1-Befund bleibt separat bestehen, unabhängig vom Ausgang der Wiederholung.

Der nächste sinnvolle Umsetzungsschritt ist nach Vertragsabnahme ein begrenztes
Entwicklerpaket für die neue UHR1-Hülle samt unabhängigem Quellengenerator,
Rezeptprüfung, Autorisierungssperren und unverändertem U/H-Anschluss. Abnahme:
bitgleiche U/H-Verfahren, bestandene relevante neutrale Prüfungen, vollständige
Ressourcenrechnung und versiegelte neue Vorstartbindung. Erst anschließend ist
eine gesonderte Entscheidung über den einmaligen Forschungsversuch möglich.
Heute wurden ausschließlich Konzept und Standseinordnungen bearbeitet.

Referenzen: [UH1-Vertrag](S2UC_UH1_PRUEFVERTRAG_20261004.md),
[UH1-Codebindung](S2UC_UH1_V1_20261005_CODEBINDUNG.json),
[UH1-Abschluss](../reports/s2uc/uh1-assessment-20261005-01/REPORT.md),
[HX1-Quellenrezept](S2UC_HX1_PRUEFVERTRAG_20261004.md).
