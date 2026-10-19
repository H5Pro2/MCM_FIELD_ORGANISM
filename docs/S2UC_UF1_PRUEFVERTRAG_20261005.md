# UF1 Prüfvertrag: U gegen die hinweisbezogene Häufigkeitsbaseline F

Stand 2026-10-05. Vertragskennung `MCM-UF1-v1-20261005`.
Status `KONZEPTIONELL_VORREGISTRIERT_KEINE_IMPLEMENTIERUNGS_ODER_LAUFFREIGABE`.
Empfänger: Projektleiter; erstellt durch den MCM-KI-Entwickler.

Abnahmegegenstand ist dieser vollständige Vertrag. Die Aufgabenfamilie bleibt
unverändert; der einfache Vergleichsarm wird von H auf F umgestellt. Genau U/F,
kein zusätzlicher H-Arm. Heute ausschließlich Dokumentation und statische
Dateibindung: keine Implementierung, Quellen- oder Matrixerzeugung, Qualifikation
oder Versuchsausführung. UF1 ist eine Vertragskennung, keine Laufnummer.
UH1/UHR1 und ihre verbrauchten Freigaben bleiben unverändert bestehen.

## 1 Frage, Verfahren und Umfang

Besteht der U-Vorteil gegenüber einer einfachen, aus eigener Erfahrung gelernten
hinweisbezogenen Häufigkeitsregel, die zur absoluten Fehlerbewertung besser passt
als ein Mittelwert? Analytisch begründete Gegenhypothese: F kann in D einen
kleineren mittleren Q-Fehler erreichen, also theta=U−F>0. Das ist kein Befund.
Alle drei vorregistrierten Intervallausgänge bleiben möglich.

U bleibt MultiErrorAdapter, multi_error_exact_v1, FactorRecencyArm, exact_v1,
legacy_v1, alpha=1/2, Faktorenliste [1.0], A1/K1 aus. Reguläre Aufnahme,
Bestätigung, Promotion, Kandidatenersetzung, Verdrängung, EC/EP-Updates,
Auswahl, Feedback und Cleanup unverändert. Zwei Retained-Vierframespuren und
ein Kandidat; forming wird kein weiterer abrufbarer Speicher. U wird frisch
ausgeführt, nicht durch frühere Fehlerreihen ersetzt.

F übernimmt Hs zwei Hinweisschlüssel, exakte Zweiframe-Schlüsselbildung,
Vierframe-Phasenwissen und Hinweisersatz nach letztem Feedback. Pro Hinweis
hält F höchstens zwei tatsächlich beobachtete Fortsetzungsvektoren und ihre
exakten Häufigkeiten seit Aufnahme dieses Hinweises. Keine vorgegebenen A/B-
Werte, Quoten, Labels, Anfangszähler oder externen Lernsignale. Nur nach dem
eingetroffenen Q-Ziel lernen. Vorhersage: strikt häufigerer beobachteter Wert;
bei bekanntem Gleichstand oder unbekanntem Hinweis Persistenz.

Vergleich zweier Gesamtverfahren mit verschiedenen Repräsentationen, Budgets
und Informationszugängen. F besitzt Hs Phasenprivileg und mehr numerischen
Speicher als H, weil es zwei Originalvektoren statt eines Mittelwerts je Hinweis
hält. Keine Ressourcen- oder Informationsgleichheit behaupten. F ist eine
gezielte Baseline, keine vorprogrammierte Organismusfunktion im MCM-Feldpfad.

r=1,…,32, D vor N; je Geschichte 1024 Frames in 256 Vierframeblöcken. Frische
getrennte U/F-Zustände und Referenzen je Geschichte. Je Frame U und U-Referenz,
dann F und F-Referenz, danach nächster Frame. 64 Geschichten, 128 Armläufe,
65.536 Quellframes, 131.072 Armverarbeitungen und zusätzlich 131.072 unabhängige
Referenzfortschritte. Kein Parallelworker, Tuning oder weiterer Arm.

## 2 Analytische Passung zur absoluten Fehlerbewertung

Für zwei Vektoren a,b und Häufigkeiten c_a,c_b mit positiver Summe sei
p=c_a/(c_a+c_b). Empirischer mittlerer absoluter Fehler:
L(x)=p·MAE48(x,a)+(1−p)·MAE48(x,b). Dieser Ausdruck zerfällt komponentenweise.
Bei p>1/2 ist a ein komponentenweiser gewichteter Median und minimiert L,
bei p<1/2 gilt dies für b. Das gilt auch bei gekreuzten Komponentenordnungen.
Ein Platz mit Zähler null ist keine gelernte Alternative. Bei nur einem
beobachteten Wert wird dieser vorhergesagt.

Bei p=1/2 minimiert jedes x mit x[j] zwischen a[j] und b[j] den empirischen
absoluten Fehler. Die angeordnete Persistenz ist nur dann ebenfalls ein
Minimierer, wenn sie komponentenweise in diesem Intervall liegt. In der
Forschungsfamilie liegt V(1/2) zwischen V(1/4) und V(3/4); F erhält dieses Wissen
nicht. Außerhalb kann Gleichstands-Persistenz schlechter sein. Die feste Regel
wird deshalb nicht nachträglich geändert. Bei unbekanntem Hinweis fehlen eigene
Fortsetzungshäufigkeiten vollständig.

Mit D=MAE48(a,b) hat der arithmetische Mittelwert m=p·a+(1−p)·b unter derselben
Zweipunktverteilung Verlust 2p(1−p)D, der Mehrheitsvektor min(p,1−p)D.
Für p=3/4 und D=1/2 wären das analytisch 3/16 gegenüber 1/8. Das ist keine
Messung oder Vorhersage des vollständigen kausalen Laufes. Die Ableitung nutzt
ideale reelle Arithmetik; tatsächlicher binary64-MAE und Beobachtungen werden
separat exakt gebunden. F berechnet selbst weder p noch einen Mittelwert.

Endliche gelernte Häufigkeiten sind nicht die unbekannte nächste bedingte
Verteilung. Reihenfolge, feste Gesamtquoten, frühe Fehlmehrheiten, Gleichstände
und Verdrängung können zukünftigen Fehler verändern. F kennt keine wahren
Wahrscheinlichkeiten, Quoten oder verbleibenden Fortsetzungen. Ein empirischer
Minimierer bisheriger Daten ist keine allwissende oder allgemein optimale
Referenz. Bei mehr als zwei Werten ist die häufigste ganze Vektorausprägung
auch nicht allgemein ein komponentenweiser Median.

UF1 kann die offene Erklärung durch Verlustfunktionspassung stützen oder
begrenzen. F ändert auch Repräsentation und Speicher; neue Quellen unterscheiden
sich von UH1/UHR1. Der Vergleich zu alten H-Ergebnissen isoliert deshalb den
Effekt der Mittelwertbildung nicht kausal. Kein Pooling und kein nachträglicher
H-Vergleich auf den neuen Quellen.

## 3 Vorab festgelegtes neues Quellenrezept

### Namensraum und Ziehungsprimitive

Exakter neuer Forschungsnamensraum:
`MCM-UF1/source/v1/r={r}/stream={s}/draw={d}`.
Die statische Suche vor Erstellung dieses Vertrags nach MCM-UF1, S2UC_UF1
und uf1-comparison in docs, tools, tests, reports sowie README und Forschungsweg
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

Geplante Fallkennungen UF1-01-D bis UF1-32-N; IDs, r/C/o und Quoten bleiben
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
`MCM-UF1/neutral/v1/r={r}/stream={s}/draw={d}`, nie den Forschungsnamensraum.
Neue Quellen werden nicht aus alten Fehlerreihen rekonstruiert oder selektiert.

Keine UH1-/UHR1-Quelle wird kopiert, erneut abgespielt oder als Auswahlkriterium
verwendet. Zufällige Übereinstimmungen werden nicht durch Nachziehen entfernt:
neu bedeutet der vorab festgelegte neue Namensraum, keine ergebnisabhängige
Disjunktheitsauswahl. Manifest und Quellenhashes entstehen erst im späteren
separat autorisierten Versuch. Heute keine Quellen oder Bootstrapmatrix.


## 4 Eingangsvertrag und F-Schlüssel

Nur aktueller normaler Frame mit 48 endlichen binary64-Komponenten und technischer
Index i=1 bis 1.024. Zeit/Scope wie HX1: [4800(i−1),4800i), owner=comparison,
stream=stream, armneutrales Profil ohne r/C/Orientierung. Keine X/Y-Labels,
Fortsetzungsprototypen, Fallnamen, Quoten, Manifest-, Archiv- oder Beobachterzugriffe.

F kennt die technische Vierframephase i mod 4. Diese Privilegierung wird gegenüber
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

Fortsetzungswerte ebenso als vollständige little-endian-Bitmuster von 48
binary64-Komponenten vergleichen. +0/−0 bleiben bitverschieden, auch bei gleichem
numerischen Fehler. Kein Runden, Mitteln, Ähnlichkeitscluster, Hashvergleich oder
Normalisieren beim Zählen. X/Y/A/B bleiben ausschließlich Beobachterbezeichnungen.


## 5 Vollständige begrenzte F-Zustandsmaschine

### 5.1 Slots, Aufnahme und zusätzliche Werte

Genau zwei Hinweisslots 0/1. Je Slot: Schlüssel 768 Byte, Werteplätze v0/v1
je 384 Byte, uint64-Zähler c0/c1 und uint64 letzter gültiger Q-Feedbackstempel.
Je Slot 1560 Byte. Ein Werteplatz ist genau bei Zähler >0 belegt. v0 immer vor
v1; c0=0 impliziert c1=0 und leeren Hinweisslot. Unbelegte Nutzdaten/Stempel
null. Ein Nullvektor mit positivem Zähler ist dagegen ein gelernter Wert.
Werteplatznummern bedeuten Aufnahmereihenfolge, keine A/B-Labels.

c0,c1 jeweils 0,…,256, je Hinweis c0+c1<=256. Globaler Feedbackzähler t=0,…,256;
belegte Slotstempel 1,…,t, leere 0. Summe gehaltener Häufigkeiten <=t, wegen
Verdrängung nicht zwingend gleich t. Doppelte belegte Hinweisschlüssel und
bitgleiche belegte Werteplätze desselben Slots sind Invariantenfehler.
Keine Sättigung, Halbierung, Abzinsung, gleitenden Fenster oder Überläufe.

Dritter verschiedener Hinweis: Erst bei seinem Q-Feedback kleinsten freien
Slot wählen, sonst ältesten Feedbackstempel, bei Gleichstand kleinere Slotnummer.
Alten Schlüssel, beide Werte, Zähler und Stempel vollständig löschen. Neuen
Schlüssel aus dem Zweiframepuffer und Ziel in v0 kopieren, c0=1,c1=0.
Zurückkehrende verdrängte Hinweise sind unbekannt; keine alten Zähler restaurieren.

Dritter bitverschiedener Fortsetzungswert für denselben gehaltenen Hinweis:
terminaler Fehler F_VALUE_CAPACITY vor Lernmutation. Kein Ignorieren, Zusammenlegen,
Werteersatz, Überlaufbehälter oder Weiterlaufen als Persistenzarm. Der gesamte
Versuch wird NICHT_AUSWERTBAR, ohne Leistungsurteil aus früheren Teilzeilen.
Das ist die explizite Domänengrenze eines Zweiwerte-Zählers, kein Vorwissen über
die Werte selbst. Die Forschungsfamilie besitzt zwei Werte; den dritten Wert
nur neutral als Fehlerpfad prüfen. Nach Hinweisverdrängung beginnt die Kapazität neu.

### 5.2 Gepackter Zustand und Tickets

Nullbasierte Offsets, little-endian:

| Bereich | Offset | Länge |
| --- | ---: | ---: |
| Hinweisslot 0 | 0 | 1560 |
| Hinweisslot 1 | 1560 | 1560 |
| Steuerblock | 3120 | 32 |
| Zweiframepuffer | 3152 | 768 |
| Eingefrorene Ausgabe | 3920 | 384 |
| Bank gesamt | 0 | 4304 |

Je Slot relative Offsets: Schlüssel 0, v0 768, v1 1152, c0 1536, c1 1544,
Stempel 1552. Steuerblock: uint64 i bei 0, t bei 8, pending_target bei 16;
Byte pending_kind bei 24, pending_slot bei 25, pending_value bei 26, flags bei 27;
vier reservierte Nullbytes bei 28. flags: Bit 0 closed, Bit 1 erster Pufferframe,
Bit 2 zweiter Pufferframe, übrige Bits null. Phase wird aus i abgeleitet.

pending_kind: NONE=0, UNKNOWN_Q=1, TIE_Q=2, MAJORITY_Q=3, SKELETON=4.
pending_slot bei TIE_Q/MAJORITY_Q 0/1, sonst Sentinel 255.
pending_value nur bei MAJORITY_Q 0/1, sonst 255. NONE hat pending_target=0.
Initial Nutzdaten/Zähler/Indices null, NONE, Slot-/Wertsentinel 255, flags=0.
Höchstens eine ausstehende Ausgabe, keine erreichbare Ausgabegeschichte.

accept prüft offenen Zustand, nächsten Index 1,…,1024, Dimension, endliche
Werte, erwartete Phase und Ticket-/Slotinvarianten vor Nutzung. Prognoseziel
maximal 1025. Keine fehlenden, doppelten oder vertauschten Frames.
Der gespeicherte Index bezeichnet den zuletzt erfolgreich abgeschlossenen
accept-Aufruf. Jeder erfolgreiche Aufruf aller vier Phasen schreibt ihn auf
den aktuellen Eingangsindex fort; ein fehlgeschlagener Aufruf bleibt terminal.

### 5.3 Phase 1, i=4b−3

Bei i=1 muss NONE gelten. Sonst zuerst eingefrorene SKELETON-Ausgabe gegen genau
diesen Index bewerten und konsumieren, ohne Lernen. Puffer/Ausgabe danach leeren,
ersten Hinweisframe hineinkopieren, erstes Pufferflag setzen. Keine neue Prognose
oder Hintaufnahme.
Konsumiertes Ticket auf NONE, pending_target=0 und beide Sentinels zurücksetzen.

### 5.4 Phase 2, i=4b−2: Prognose vor Ziel

Zweiten Hinweisframe in Puffer kopieren. Vollständigen Schlüssel linear gegen
Slot 0, dann 1 vergleichen; Mehrfachtreffer terminal. Unbekannt: zweiten
Hinweisframe in eigene Ausgabe kopieren, UNKNOWN_Q, Slot-/Wertsentinel 255.
Bekannt mit c0=c1>0: dieselbe Persistenz, TIE_Q, Trefferslot, Wertsentinel 255.
Bekannt mit c0!=c1: belegten Platz mit größerem Zähler in eigene Ausgabe
kopieren, MAJORITY_Q, Trefferslot/gewählten Werteplatz speichern. c0>=1,c1=0
führt somit zur Ausgabe v0; keine Mindesthäufigkeit.

Immer pending_target=i+1; Puffer bis Feedback erhalten. Ausgabe bitgleich
einfrieren, kein Alias auf den Werteplatz. Prognosen ändern weder Schlüssel,
Werte, Häufigkeiten noch Stempel. Keine Nutzung des noch unbekannten Zieles.

### 5.5 Phase 3, i=4b−1: Feedback und Lernen

Passendes Q-Ticket und unveränderte Ausgabe prüfen, deren MAE48 gegen aktuellen
Zielvektor bestimmen. Hinweis bleibt der vorherige Zweiframepuffer. Bei
TIE_Q/MAJORITY_Q muss der gleiche Slot noch denselben Schlüssel besitzen;
Ticketgrund und Wertwahl müssen aus dem unveränderten Vorzustand folgen.
UNKNOWN_Q darf keinen inzwischen belegten gleichen Schlüssel besitzen.

Bekannter Hinweis: Zielbits gegen belegtes v0, dann v1 vergleichen. Treffer:
nur dessen Zähler +1. Kein Treffer und v1 frei: Ziel nach v1 kopieren, c1=1.
Kein Treffer und beide Plätze belegt: F_VALUE_CAPACITY vor Lernmutation.
Unbekannter Hinweis: Aufnahme/Hintverdrängung nach 5.1, Ziel nach v0, c0=1.

Vor Mutation Zulässigkeit von t+1, Zielzähler+1 und Hinweissumme prüfen.
Dann Aufnahme/Zählupdate, t=t+1, betroffenen Slotstempel auf t setzen; andere
Slots unverändert. Auch Fehler null und Gleichstandsprognosen lernen regulär.
Ausgabe/Puffer/Ticket danach löschen, NONE/Sentinels, i fortschreiben. Keine
nachgelieferte Vorhersage mit dem gerade eingetroffenen Ziel.

Fehler während Kopieren, Zählen, Export oder Cleanup terminal; kein Fortsetzen
teilweise mutierter Zustände. Bereits beobachteter Fehler darf als technischer
Teilbeleg bleiben, nicht als Leistungsentscheidung aus einem unvollständigen Lauf.

### 5.6 Phase 4 und Ende

Schlussframe in eigene Ausgabe kopieren: SKELETON, Ziel i+1, Slot-/Wertsentinel
255, kein Lernen. Nach Frame 1024 steht Ziel 1025 aus. finish nur bei vollständigen
1024 Frames, t=256 und diesem Ticket. Ziel 1025 rechtszensiert löschen, ohne
Fehler oder Feedback. Je Geschichte 511 beobachtete Ausgaben, 256 Q/255 S,
eine zensierte Ausgabe. Keine stille Teilgeschichte oder verkürzter Teilblock.

finish nullt Slots, Puffer, Ausgabe, Scratch, Zähler/Indices; NONE, Sentinels 255
und closed=true bilden den geschlossenen Zustand. Danach accept und zweites
finish technische Fehler. Idempotenter abort darf erneut bereinigen; kein
erfundener Cleanup-Erfolg nach Prozessabbruch. Externe Zustandskopien und
Diagnosen sind für F unerreichbar und im Prozess-/Exportbudget enthalten.

## 6 Bewertung und vorab fixierte Statistik

MAE48 exakt wie HX1: total=0.0, j=0 bis 47 jeweils difference=abs(pred[j]−y[j]),
total=total+difference, abschließend total/48.0, einzeln binary64-gerundet.
Keine Umordnung oder FMA. Ein Mittelwert ist unter MAE nicht allgemein optimal.

Q={3,7,…,1023}, je Geschichte 256; G_all={3,5,…,1023}, 511;
S=G_all ohne Q, 255. Externe Q_X/Q_Y jeweils 128 werden aus dem archivierten
Quellkatalog gebildet und ausschließlich zur ergänzenden Auswertung benutzt.
Alle Q-Ziele zählen, kein Warm-up, Ausschluss unbekannter/kalter/verdrängter
Hinweise oder günstiges Zeitfenster. Je Bedingung 8.192 Q-Ziele je Arm.

m[r,C,a] ist der Mittelwert aller 256 Q-MAE. d[r,C]=m[r,C,U]−m[r,C,F].
Einziger Primärkontrast: theta=(1/32) sum_r d[r,D]. Gegenhypothese theta>0.
Positive Werte bedeuten F-Vorteil. Primärurteil aus ungerundeten rationalen Werten:
untere 95%-Grenze>0: F_VORTEIL_BELEGT; obere<0: U_VORTEIL_GEGEN_F_BELEGT;
sonst KEIN_EINDEUTIGER_UNTERSCHIED_NACHGEWIESEN, einschließlich Grenze genau null.
Technischer Fehler überschreibt alles mit NICHT_AUSWERTBAR.

### Exakte Bootstrapregel

10.000 Ziehungen z=0,…,9999. Orientierung o=0: r=1,3,…,31;
o=1: r=2,4,…,32. Je o und k=0,…,15 die ersten acht SHA256-Bytes von
`MCM-UF1/bootstrap/v1/z={z}/orientation={o}/k={k}` als Big-endian uint64 u.
ASCII/UTF-8, Dezimalzahlen ohne führende Nullen, kein Zeilenumbruch.
Gewähltes r=2*(u mod 16)+1+o. Dieselbe 32er-Indexzeile für alle Bedingungen,
Arme und ergänzenden Masken; keine getrennte Ziehung einzelner Ziele oder D/N.
Die Regel ist hier vor jeder UF1-Ausführung fixiert. Matrix später vor Replay
erzeugen, unabhängig prüfen und ihre 320.000 Bytes (r−1 je Eintrag) per SHA256
in die neue Vorstartbindung aufnehmen. Dieser Spezifikationsauftrag erzeugt sie nicht.

Pro Ziehung ungewichteter Mittelwert der 32 Paarwerte. Sortieren, Quantile
q=1/40 und 39/40, h=9999q, lineare Interpolation zwischen floor/ceil(h).
Alle gespeicherten binary64-MAE als exakte rationale Zahlen aggregieren;
auch Kontraste, Mittel und Quantile rational. Nur Anzeige runden.
Ein Primärkontrast, keine Bonferroni-Aufteilung auf HX1-Kontraste.
Nominale approximative Intervalle, keine exakte Abdeckungs- oder Powerbehauptung.

### Vollständige ergänzende Bilanz

Je D/N und Q/G_all/S/Q_X/Q_Y: U/F-MAE, U−F, Zielzahl, alle 32 Geschichtenwerte;
zusätzlich getrennt je Orientierung mit 16 Geschichtenwerten. Explorative 95%-
Intervalle aus derselben Matrix, für Orientierung ausschließlich deren 16 Spalten.
Auch Q-Interaktion d[r,D]−d[r,N] mit 32 Paarwerten und explorativem 95%-Intervall.
Keine ergänzende Auswertung wird nachträglich zur Erfolgsregel erklärt.

Je Bedingung/Maske/Orientierung: Zahl U besser/schlechter/gleich,
Gewinn_U=sum max(eF−eU,0), Schaden_U=sum max(eU−eF,0), Netto=Gewinn−Schaden,
maximaler Einzelschaden und sämtliche zugehörigen (r,C,Ziel)-Positionen,
schlechtester Geschichtenmittelwert von U−F. Jede Summe exakt gegen alle
Zielreihen prüfen; überlappende Masken nicht addieren. Kumulierte Differenzen
für alle G_all-Ziele und separat Q vollständig archivieren.

F bekannte/unbekannte Hinweise und Slotersetzungen, U-V0–V3 nach HX1 sowie
ihre jeweiligen Gewinn-/Schadensbeiträge vollständig deskriptiv partitionieren.
U-Zellenalter, fehlende Spuren oder F-Verfügbarkeit erklären mögliche Gelegenheiten,
beweisen aber keinen isolierten kausalen Mechanismus. Kein N-Gleichwertigkeitsurteil
aus einem nicht signifikanten Unterschied.



F-Prognoseklassen auf Q: F0=UNKNOWN_Q, F1=TIE_Q, F2=MAJORITY_Q, vollständige
Partition je Geschichte mit Zielzahl und Gewinn-/Schadensbilanz. Bekannt/unbekannt
und Hinweisersatz ja/nein als weitere separate Partitionen. Vorzielzähler,
gewählter Werteplatz, Zahl belegter Werteplätze, erster/letzter Feedbackindex
und Hintstempel extern vollständig archivieren. Unbekannt hat keine gespeicherten
Zähler, nicht zwei erfundene Beobachtungen. Leere Gruppen: Anzahl 0, Mittelwert
undefiniert, nicht künstlich null.

U-V0 keine passende Spur, V1 nur kalte Zellen, V2 warm/Persistenz, V3 warm/Kontext.
Je Arm D/N zusammen 32.704 beobachtete Ziele, davon 16.384 Q. Alle 640 armweisen
Geschichtenmittelwerte über 32×2×5×2 exportieren. Nur neue UF1-Daten, kein Pooling
oder gemeinsames Intervall mit UH1/UHR1. Deskriptiver Studienvergleich muss die
anderen Quellen und Vergleichsarme ausdrücklich auseinanderhalten.

## 7 Unabhängige Referenzen und neutrale Prüffälle

U-Referenz und Replaypfad unverändert aus UHR1: eigener Bestand, Aufnahme,
Lebenszyklus, Abruf, EC/EP, Auswahl, Feedback, Cleanup. F-Referenz getrennt
implementieren, z.B. eigene Zwei-Slot-Objekte und eigene auf zwei Einträge
begrenzte Häufigkeitslisten. Produktionsschlüssel, Zähler, Slotwahl, Gewinner,
Tickets und Ausgaben niemals als erwartete Daten übernehmen. Nur aktuelle
Frames/Indices und Standardprimitive teilen, keine Zukunft/Quoten/Labels.

Jeden Vor-/Nachzustand bitweise vergleichen: Schlüssel, Werteplätze, Zähler,
Stempel, Ticket, Puffer, Ausgabe und Cleanup. Referenz wählt aus eigenem Zustand.
Unabhängiger Fehlerprüfer rekonstruiert MAE48 aus Ausgabe/Ziel in fester Reihenfolge.
Archivdecoder unabhängig vom Encoder; initiale 4304-Byte-Bank einschließlich
Sentinels spezifizieren, nicht fälschlich komplett null. Nur verlustfreie Kodierung.

Quellenreferenz mit eigener SHA-Zeichenfolge, Zählern, Rejection und Permutation,
kein Produktionsgenerator als Oracle. Statistikreferenz berechnet Geschichtenwerte,
Paaraggregation, Ziehungsindices und Quantile unabhängig aus Zielarchiven.
Nachgelagerte Archivprüfung ohne Policy-Aufruf und ohne Quellenerzeugung.

Folgende Prüfungen sind spezifiziert, heute nicht ausgeführt:

| ID | Neutraler Fall und erwartetes Verhalten |
| --- | --- |
| N1 | Dimension, Index, NaN/Inf terminal; Framevertauschung/ein Bit/+0 gegen −0 unterscheiden Schlüssel UND Zielwerte. Keine Labels/Zukunft im Input |
| N2 | Unbekanntes x: Persistenz vor a; erst Feedback erzeugt v0=a,c0=1. Zweites x sagt a vor b voraus; danach v1=b,c1=1. Drittes x bei 1:1 Persistenz; nach a 2:1, nächste Prognose a. Prognose ändert keine Zähler/Stempel |
| N3 | Feedbackfolge a,b,a,b,b zu x: Vorhersagen Persistenz,a,Persistenz,a,Persistenz; danach nächste Prognose b bei 2:3. Beide Gewinnerwechsel und Fehler-null-Feedback. Aufnahmereihenfolge b vor a vertauscht Plätze, nicht Mehrheit |
| N4 | Hinweise x,y getrennte Häufigkeiten; x,y,x,z-Feedback verdrängt y erst bei z-Feedback. Rückkehr y unbekannt ohne Altzähler. Stempelgleichstand im neutralen Zustand: kleiner Slot |
| N5 | Dritter Wert a,b,c für x: aktuelle eingefrorene Prognose bewerten, dann F_VALUE_CAPACITY vor Lernen, terminaler Cleanup. Kein Werteersatz/Unterdrücken. Ein Bit und +0/−0 ebenfalls kapazitätsrelevant; neue Hinweise dürfen eigene Werte haben |
| N6 | Falsches Ticketziel/Slot/Wert/Grund, doppelte Wertplätze, Ausgabealias/Korruption terminal. t=256/c=256 zulässig, nächste Erhöhung abgewiesen; Summen/Belegung. Leere/Teilgeschichte, doppeltes finish, zensiertes Ende, Fehler an jedem Mutationsabschnitt |
| N7 | Zwei Hinweise/vier Werteplätze voll; Treffer, Gleichstand, Erstaufnahme, Hintverdrängung, dritter Wert, Abort/Kopierfehler transient messen. Bank 4304, Numerik<=4712, harte Heapgrenze, keine freie externe Historie |
| G1 | Forschungszugriff vor Freigabe gesperrt, auch Referenzgenerator. Unabhängige neutrale Generatoren identisch; L−1/L, n=1,4096-Grenze, Permutation/Zähler |
| G2 | Alle 64 Quellen vor erstem Arm versiegelt; D-Quoten/Orientierung, geteiltes T, unveränderte N-Kontingenz; Quellen-/Manifest-/Code-/Runtimeabweichung terminal |
| G3 | Positive/negative/nullhaltige/nullberührende Intervalle; vollständige Paare/Masken,16+16-Schichtung,rationale Gewinn-/Schadenspartition; falsche Matrix/Quantile/fehlende Ziele terminal |
| G4 | Relevante elf U-Untertests; injizierte U-/F-Referenzabweichung erkannt. U-Profil,A1/K1,EC/EP,Numerik unverändert |
| G5 | Datei-/Kategorie-/Gesamtbudget, gzip/LZMA-Roundtrip,Korruption,fehlende/falsche Freigabe,existierender Ordner,Startfehler,Crash,Timeout,Cancel,harte gemeinsame Speicherablehnung |
| G6 | Zwei ungeordnete Handvektoren mit 3:1/1:3: Mehrheitsvektor minimiert empirischen MAE. 1:1 mit Persistenz innerhalb/außerhalb des Komponentenintervalls; außerhalb keine Optimalitätsbehauptung |

Nach separat beauftragter Implementierung und bestandenen Einzelprüfungen
höchstens ein ausdrücklich beauftragter neutraler Größenablauf 64×1024 mit U/F
und Referenzen. Festes Muster: (X,A),(X,A),(X,B),(Y,B),(Y,B),(Y,A),(X,A),(Y,B).
Für b=1,…,256 und r Index (b+r−2) mod 8, in N nur X/Y tauschen. Jeder Block
enthält die vier Frames aus Abschnitt 3. Dritter Hinweis/Wert nur Einzelprüfungen.
Ein gescheiterter Größenablauf hat keine automatische Wiederholungsfreigabe.
Neutrale Ergebnisse rein technisch, keine Nutzeninterpretation.

## 8 Vollständige Ressourcenrechnung

| Eigener numerischer Zustand F | Byte |
| --- | ---: |
| Zwei Hinweisschlüssel | 1536 |
| Vier Fortsetzungsvektoren | 1536 |
| Vier uint64-Häufigkeiten und zwei Stempel | 48 |
| Steuerblock einschließlich Ticket | 32 |
| Zweiframepuffer | 768 |
| Eingefrorene Ausgabe | 384 |
| Persistente Bank | 4304 |
| Maximal ein temporärer Vektor und drei 8-Byte-Skalare | 408 |
| Konservative numerische Gesamtbelegung | 4712 |

Harte numerische F-Grenze 5120 Byte, Eigenheap einschließlich Container,
Steuerobjekte, Ausgaben und transienter Kopien höchstens 32768 Byte. 4712 ist
ein Entwurfsmaximum, kein Messbefund. Keine zusätzliche 768-Byte-Schlüsselkopie
außerhalb der Rechnung. Vergleiche direkt gegen Slots, Kopier-/Fehlerpfade mit
gebundenem Scratch messen. H hatte 3520 Byte Bank/4096 numerisches Limit:
F besitzt ausdrücklich mehr numerischen Speicher, keine Gleichbudgetbehauptung.

Höchstens ein geliehener aktueller Frame, 384 Rohbytes; vollständigen Objektgraph
separat messen. Nach accept keine Referenz darauf. Eigene Ausgabeslots 1,
Receipts 0; keine Armreferenz auf Beobachter-/Refhistorie. Fehlertexte extern,
mit Prozess-/Exportbelastung; kein versteckter armseitiger Serializer.

U unverändert: Bank 416, Zusatzheap<=16384 Byte; zwei Retained/ein Kandidat,
konservative Originalframegrenze 18, kombinierte Original-/Ausgabeslotgrenze 20,
Ausgabeslots<=2. Receipt<=16384, transiente UTF-8-Obergrenze 32768 Byte.
Basis-/Originalobjekte und erreichbaren Gesamtgraph separat ausweisen.
Kein U-Budgetzuschlag wegen größerem F-Speicher.

Je Arm Grenzstelleninventar und transiente Spitzen inklusive Fehlerpfaden.
U-Zusatzheap und F-Eigenheap sind unterschiedliche Messgrößen. Eingangs-,
Beobachter-, Referenz-, Archiv- und Berichtsspeicher vollständig im gemeinsamen
Prozesslimit; externe Historie ist keine Arm-Memory. Keine Grenzumgehung durch
Auslagern. Deaktivierte Rohtraces mit Wert 0 beweisen keine Nullbelegung.

Supervisor und höchstens ein Worker im selben harten Windows-Job: gemeinsamer
privater Commit<=536870912 Byte, Limitflag 0x200 und Mitgliedschaft prüfen.
Jeder rohe Job-Peak über Limit konservativ NICHT_AUSWERTBAR, auch bei abgewiesener
Allokation. Abgenommene Speicherklarstellung unverändert.

Gesamtfrist 3600 s ab Supervisorstart einschließlich Bindungsprüfung,
Quellenerzeugung/Rezeptprüfung, Replay/Referenzen, Statistik, Export und Abschluss.
Workerfrist spätestens Start+3540 s, Abschlussreserve 60 s. Bei Fehler/Frist
Worker beenden und Ende belegen; kein weiterer paralleler Worker.

Gesamtexport<=67108864 Byte (64 MiB) inklusive Vorbereitung/Quellen/Fehlerbelegen.
Teilgrenzen: Vorbereitung 8 MiB; Quellen 2 MiB gesamt/32 KiB je Datei; Fallarchive
32 MiB gesamt/512 KiB gzip/4 MiB expandiert je Fall; Verwaltung und vollständige
Auswertung 2 MiB; Abschlussreserve 1 MiB. Freier Rest erweitert keine Teilgrenze.
Postlaufbericht/Archivprüfung zusätzlich im Gesamt-/Verwaltungsbudget rechnen.
Identische referenzierte Dateien einmal je kanonischem Paket, doppelte operative
Pakete mehrfach zählen. Keine alten vollständigen Ergebnisarchive als Eingang.

Gzip Level 9, mtime=0, ohne Dateiname; Runtime mit Python/DLL, Byteorder und
Kompressionsbibliotheken binden. LZMA-Vorbereitungspaket nur mit vorab gebundenem
Format und unabhängiger bytegenauer Rekonstruktion. Vollständige U-Lebenszyklen,
F-Zustände, Zähler, Wertebits, Schlüssel, Tickets, Ausgaben, Fehler, Aufnahmen und
Ersetzungen verlustfrei exportieren. Keine Kürzung für Budgets. Ressourcen erst
nach Entwicklungsauftrag neutral nachweisen; alte H-Messungen sind kein F-Nachweis.

## 9 Bindungen, spätere Startbedingungen und Abbruch

Die [Vorregistrierungsbindung](S2UC_UF1_VORREGISTRIERUNGSBINDUNG_20261005.json)
bindet diesen Vertrag und vorhandene Artefakte per Bytezahl/SHA256. Sie bestätigt
statisch alle 159 Dateien der UHR1-Codebindung als unveränderte Ausgangsreferenz,
nicht als Auftrag zum Ausführen des alten U/H-Starters. U und seine laufwirksamen
Abhängigkeiten bleiben bitgleich. F/Referenz und neue Hüllen erst nach gesondertem
Entwicklungsauftrag. Alte Bindungen, Quellen, Resultate und Freigaben unverändert.

Bootstrapmethode identisch, UF1-Namensraum neu. Matrix erst im gesonderten
Vorbereitungspaket erzeugen, unabhängig prüfen und vor jeder Forschungsquelle
binden. Quellenbytes/-hashes erst innerhalb des späteren autorisierten Versuches.

1. Fachliche Vertragsabnahme und gesonderter Auftrag für F, Referenz, UF1-Hülle,
   Rezept-/Archiv-/Statistikprüfung.
2. N1–N7/G1–G6 bestanden, Ressourcenrechnung und ggf. der ausdrücklich beauftragte
   eine neutrale Größenablauf. Keine Forschungsquelle dabei erzeugen.
3. Vollständige neue transitive Code-/Runtimebindung, Vertrag/Rezept, geprüfte
   Matrix, neutrale Belege und exakter späterer Aufruf in neue Vorstartbindung.
4. Separate einmalige Forschungsbeauftragung auf genau diesen SHA256. Erst dann
   operative Autorisierung/Versuch; alte Freigaben/allgemeines WEITER genügen nicht.

Geplantes exklusives Ziel `reports/s2uc/uf1-comparison-20261005-01`, heute nicht
angelegt. Marker vor Forschungsquellenerzeugung reservieren. Vorhandener Marker/
Ordner sperrt Start; kein anderer Namensraum bei Kollision.
Spätere Autorisierungsfelder: action=UF1_32_NEW_PAIRS_UF_ONCE,
status=AUTHORIZED_ONCE, exakter Vorstart- und Vertrags-/Rezept-SHA256,
source_namespace=MCM-UF1/source/v1, genannter Zielordner, arms=[U,F],cases=64,
frames_per_case=1024,Q_targets_per_case=256,primary_pairs=32,
total_seconds=3600,process_bytes=536870912,export_bytes=67108864.
Starter/Aufruf vor neutraler Qualifikation fixieren; heute nicht implementiert.

Bindungsabweichung sperrt Ausführung. Nach Markerreservierung verbraucht jeder
technische Fehler den Versuch, auch vor erstem Arm. Kein Retry, Resume,
Ersatzmaterial, Leistungszwischenstopp, Falltausch oder Teilpooling.
Terminal: Generatorlimit, ungültige Quelle/Phase/Quote, dritte F-Fortsetzung,
Invarianten-/Referenz-/Numerik-/Ticketabweichung, Hashabweichung, fehlende Ziele,
Ressourcenüberschreitung, Workerfehler oder fehlender Abschluss.

Fehlerabschluss mit Code, Phase,r/C/Arm/Ziel soweit bekannt, erstem abweichendem
Artefakt, vollständigen/teilweisen Einheiten, Dateilängen/-hashes, Ressourcen,
tatsächlichem Workerexit/Cleanup. Fehlender Abschluss bedeutet unvollständig.
COMPLETE nur mit allen 64 Quellen/128 Armläufen/Referenzfortschritten/Zielreihen,
unabhängiger Statistikprüfung, eingehaltenen Grenzen und beendetem Worker.
Sonst NICHT_AUSWERTBAR ohne Leistungsurteil. Abschluss enthält Primärurteil,
vollständige Nebenbilanzen, Manifest/Bindungen/Ressourcen und Kennzeichnung
NEUE_FOLGEN_DERSELBEN_AUFGABENFAMILIE.

## 10 Aussagegrenze und nächster Schritt

Vollständig positives Intervall: F_VORTEIL_BELEGT. Vollständig negatives:
U_VORTEIL_GEGEN_F_BELEGT. Null enthaltend/berührend: kein eindeutiger Unterschied,
keine Gleichwertigkeit. Ein F-Vorteil widerlegt UHR1 gegenüber H nicht, begrenzt
aber dessen Interpretation gegenüber einer anderen einfachen Erfahrungsregel.
Ein U-Vorteil gegenüber F wäre ein neuer enger Befund, kein allgemeiner Nachweis.

Keine Veränderung der Aufgabenstruktur, kein Transfer auf andere Alphabete,
Audio/Video, allgemeine Kognition, Semantik, Cluster oder feldinterne Memory.
Zähler sind programmierte Grundmechanik; Inhalte und Gewinner entstehen erst
aus tatsächlich eingetroffenen Zielen.

Nächster Vorschlag: Projektleiter prüft diesen Vertrag, insbesondere die
explizite Zweiwerte-Domänengrenze und das größere F-Budget, und beauftragt danach
ein begrenztes Implementierungs-/Qualifikationspaket. Dessen Abnahme: U bitgleich,
F kausal/begrenzt, unabhängige Referenz, neutrale Prüfungen, Ressourcenrechnung
und neue Vorstartbindung. Forschungsfreigabe danach separat; kein paralleler
Aufgabenstrukturwechsel. Heute nur Konzept und Standseinordnungen.

Referenzen: [UHR1-Vertrag](S2UC_UHR1_PRUEFVERTRAG_20261005.md),
[UHR1-Codebindung](S2UC_UHR1_V1_20261005_CODEBINDUNG.json),
[UHR1-Ergebnis](../reports/s2uc/uhr1-assessment-20261005-01/REPORT.md),
[UH1-Vertrag mit H](S2UC_UH1_PRUEFVERTRAG_20261004.md).
