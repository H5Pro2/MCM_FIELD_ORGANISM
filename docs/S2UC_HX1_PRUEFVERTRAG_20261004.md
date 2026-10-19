# HX1: verbindlicher Prüfvertrag zur hinweisabhängigen Erfahrungsnutzung

2026-10-04. Vertragskennung `MCM-HX1-v1-20261004`.
Status: VERTRAG_SPEZIFIZIERT_KEINE_IMPLEMENTIERUNGS_ODER_LAUFFREIGABE.
Der fachlich angenommene Konzeptentwurf wird durch diesen Vertrag konkretisiert.
Bei Abweichungen gilt dieser Vertrag. Keine Implementierung, Quellenmaterialisierung,
Qualifikation oder Forschungsausführung durch seine Erstellung. ULZ1 bleibt
abgeschlossen; keine Wiederverwendung seiner verbrauchten Freigabe.

## 1. Frage, Umfang und unveränderte Architektur

Genau zwei Bedingungen D/N und drei Prädiktoren U/G/P. Keine weiteren Varianten,
Parameterwahl, abgeleiteten Arme oder spätere Auswahl günstiger Quellen.
32 Geschichtenpaare r=1,…,32, jedes mit D und N; 256 Vierframeblöcke je Geschichte,
1024 Frames, keine Vorwärmung, kein ausgeschlossener Einlauf. Alle Arme beginnen
je Geschichte frisch. Ausführungsreihenfolge: r aufsteigend, D vor N; je Frame
U, G, P und jeweils ihre getrennten Referenzen. Kein Zustand zwischen Geschichten.

U ist die unveränderte `MultiErrorAdapter`-Policy `multi_error_exact_v1` mit
`FactorRecencyArm`, Abruf `exact_v1`, Fortsetzung `legacy_v1`, alpha=1/2.
A1/K1 deaktiviert. Reguläre vollständige Wiederbeobachtung, Kandidatenersetzung,
Bestätigungsaktualität, Promotion und Verdrängung bleiben unverändert.
Keine reservierten Hinweise, Spuren, Rückmeldungen oder Speicherplätze.

Maximal zwei Retained-Vierframespuren und ein Kandidat sind abrufbar. Vier
unterschiedliche Hinweis-Fortsetzungs-Kombinationen erfordern vier Originalspuren
und passen nicht gleichzeitig in diesen Bestand. Forming ist kein Abrufspeicher.
Die Studie prüft Nutzen unter genau dieser Knappheit, nicht bei garantierter
Verfügbarkeit sämtlicher Alternativen. Fehlerzellen folgen Originalgeneration
und Offset, werden bei Verlust gelöscht und bei Promotion bitgleich übernommen.

## 2. Quellen und vorab gebundene Zufallsströme

V(x)[j]=x+j/4096, j=0,…,47, jeweils exakt als binary64 darstellbar.
Hinweis X=(V(1/8),V(1/2)), Hinweis Y=(V(7/8),V(1/2));
A=V(1/4), B=V(3/4), Schlussframe R=V(1/16).
Block b besteht aus [erstem Hinweisframe,V(1/2),A oder B,R].
Alle Namen sind externe Analysebegriffe, keine Labels im Systemeingang.

Gegenorientierung o=(r−1) mod 2: o=0 für ungerade r, X bevorzugt A;
o=1 für gerade r, X bevorzugt B. Je 16 Paare pro Orientierung.

### 2.1 Deterministische Zufallszahlen und Permutation

Es gibt pro r vier getrennte Quellenströme s mit den exakten ASCII-Namen
`continuation`, `dependent-A`, `dependent-B`, `null-cue`.
Jeder Strom hat einen eigenen Ziehungszähler d, initial 0. Eine Rohziehung ist
die erste acht Bytes des SHA256-Digests des UTF-8-Strings

`MCM-HX1/source/v1/r={r}/stream={s}/draw={d}`

als vorzeichenlose Big-Endian-Ganzzahl u. Dezimalzahlen ohne führende Nullen,
kein abschließender Zeilenumbruch, keine zusätzlichen Leerzeichen. Danach d um 1
erhöhen, auch bei verworfener Ziehung. Keine eingebauten Zufallsgeneratoren,
keine Runtime-Hashwerte, Uhrzeit, maschinenspezifischen oder benutzergewählten Seeds.

`randbelow(n)` für 1≤n≤256: M=2^64, L=M−(M mod n). Ziehe aus dem betreffenden
Strom, bis u<L, dann Ergebnis u mod n. Auch n=1 verbraucht genau eine Ziehung.
Je Strom höchstens 4096 Rohziehungen; Überschreitung ist terminaler technischer
Fehler, kein Ersatzseed. Rejection-Sampling vermeidet Moduloverzerrung im Modell
gleichverteilter 64-Bit-Ziehungen. Die tatsächliche Quelle ist eine fest gebundene
SHA256-Pseudozufallsquelle; keine mathematisch bewiesene Zufälligkeit oder
Unabhängigkeit ihrer konkreten endlichen Ausgaben wird behauptet.

Permutation einer geordneten Liste mit m Elementen: Kopie; für i=m−1,…,1 in
absteigender Reihenfolge j=randbelow(i+1), vertausche Positionen i und j.
Positionen sind hier nullbasiert. Auch bei gleichen Listenelementen wird getauscht.
Kein Sortieren nach Hashwerten, kein Nachmischen und kein Wiederholen aufgrund
der entstandenen Kreuztabelle oder des Speicherverlaufs.

### 2.2 Gemeinsame Fortsetzungsfolge und D-Hinweise

1. Permutiere [A]×128 gefolgt von [B]×128 mit `continuation`. Ergebnis T_r
   ist die gemeinsame Fortsetzungsfolge für D und N, an denselben Blockpositionen.
2. Bilde die aufsteigend geordneten, einsbasierten Positionen der 128 A und
   separat der 128 B. Permutiere sie mit `dependent-A` bzw. `dependent-B`.
3. Für o=0 erhalten die ersten 96 A-Positionen und ersten 32 B-Positionen X;
   für o=1 die ersten 32 A-Positionen und ersten 96 B-Positionen. Alle übrigen Y.

Damit D exakt 128 X und 128 Y sowie 128 A und 128 B.
Bei o=0 Kreuztabelle XA/XB/YA/YB=96/32/32/96; bei o=1=32/96/96/32.
Keine nachträgliche Zuweisung einer Orientierung anhand von Ergebnissen.

### 2.3 N-Hinweise und Bedeutung der Kontrolle

Permutiere [X]×128 gefolgt von [Y]×128 mit `null-cue`, unabhängig von den
drei anderen Stromnamen. Kombiniere positionsweise mit unverändertem T_r.
N hat exakt dieselben globalen A/B- und X/Y-Häufigkeiten wie D. Seine
Kreuztabelle ist nicht auf 64/64/64/64 konditioniert; sie wird unverändert
berichtet. Keine Neuziehung, Filterung, Ausbalancierung oder Paarersetzung.

Im zugrunde liegenden unabhängigen Ziehungsmodell ist die ganze N-Hinweisfolge
unabhängig von T_r. Die Hinweise liefern auch nach vergangenen Beobachtungen
keine zusätzliche Fortsetzungsinformation. Feste Gesamtquoten machen T_r
jedoch zeitlich abhängig. **P hat exakt MAE=1/4 auf jeder Fortsetzung;
1/4 ist keine allgemeine optimale erwartete Fehlergrenze in N.**
Ein Prädiktor könnte aus vergangenen Fortsetzungen Informationen über die
verbleibenden Quoten gewinnen. Der globale Vergleich wird nicht als optimal
bezeichnet. Die geteilte T_r-Folge hält solche Ausgangsbedingungen gepaart.

### 2.4 Bindung und Eingangsgrenze

Vor späterer Materialisierung werden dieser Vertrag, vollständiger transitiver
Codebestand einschließlich Referenzen/Export/Statistik, Runtime und exakte
Aufrufparameter in einem SHA256-Manifest gebunden. Es bindet Python-Version,
Interpreter-/Runtime-Binärdateien und verwendete Kompressionsbibliothek.
Jede Vertragsänderung erfordert eine neue ausdrücklich geprüfte Version,
keinen stillen Nachtrag nach Quell- oder Ergebnisansicht.

Erst nach separater Forschungsfreigabe werden alle 64 Quellen vollständig
erzeugt, gegen eine unabhängig implementierte Rezeptreferenz geprüft und
mit Datei-SHA256, Länge, Katalog, Indexfolge und Stromverbrauch versiegelt.
Kein Prädiktor läuft, bevor die vollständige Quellversiegelung abgeschlossen ist.
Verdeckte technische Fehlerprüfung darf Quellen verwerfen und den gesamten
Versuch stoppen, aber keine Quelle ersetzen. Keine erwartungsabhängige Sichtung.

Alle Prädiktoren erhalten nur den jeweils aktuellen normalen Frame und technische
Zeit-/Scopeangaben. Fortlaufende Indizes 1,…,1024; Zeitfenster [4800(i−1),4800i).
Konstante armneutrale Scopewerte `owner=comparison`, `stream=stream`; ein aus
dem gebundenen gemeinsamen Codeprofil abgeleitetes Profil ohne r/D/N/o.
Segmentnamen bleiben die bestehende fortlaufende Vierframesegmentierung.
Kein Vollquellenmanifest, Hinweislabel, Fallname, Quellenparameter, Restquotenzähler
oder Beobachterzugriff in U/G/P. Der Supervisor verwaltet Fallzuordnungen extern.

## 3. Prädiktoren, Kausalität und G-Gleichheit

### U

Aufnahme aller 1024 Frames. Abruf nach jedem vollständigen nichtüberlappenden
Zweiframepaar, vor Aufnahme desselben Paares in den Spurbestand. Auswahl des
eindeutigen negativen Minimums EC−EP unter warmen berechtigten Hypothesen,
sonst Persistenz. Nur Faktorenliste [1.0] und Offsets mit Nachfolger berechtigt.
Erstes gültiges Feedback direkt, danach EC=.5*EC+.5*ec und EP=.5*EP+.5*ep
in der bestehenden binary64-Operationsreihenfolge. Eigenes EP je Hypothese.
Feedback für alle eingefrorenen, beim Feedback noch lebenden Generationen;
kein nachträgliches Füllen verlorener oder neu entstandener Zellen.

Zieloutput muss vor Eintreffen des Zielwertes feststehen. Am ungeraden Ziel
zuerst Fehlerbeobachtung und gültiges Feedback, danach reguläre Aufnahme.
Keine Gleichsetzung von D/N-Speicherbeständen: Unterschiede sind zulässiger
Teil der Quellenwirkung. Jeder U-Bestand wird gegen seine eigene Referenz geprüft.

### G: globaler lernender Mittelwert

Persistenter numerischer Zustand: Zähler n gültiger bisheriger Q-Ziele und
48-Komponenten-Mittelwert m. Initial n=0, m nicht gültig. G erkennt ausschließlich
die technische Phase durch Frameindex mod 4; der unterscheidende erste
Hinweisframe wird nicht in seinen Lernzustand übernommen.

Bei einem prognostizierten Q-Ziel: falls n=0 Ausgabe des aktuellen zweiten
Hinweisframes; sonst unveränderliche Kopie von m. Auf Gerüstzielen Ausgabe
des unmittelbar vorherigen Frames. Kein Lernen aus Gerüstwerten. Nach beobachtetem
Q-Ziel y: bei n=0 m=y komponentenweise kopieren, n=1; sonst k=n+1 und für
j=0,…,47 genau tmp1=y[j]−m[j], tmp2=tmp1/float(k), m[j]=m[j]+tmp2, danach n=k.
Jede Operation wird einzeln auf binary64 gerundet, round-to-nearest/ties-to-even;
kein FMA, keine Umordnung oder nachträgliche exakte Summenrekonstruktion in G.
NaN/Inf oder Phasen-/Zählerfehler sind terminal. Keine Rückrechnung aus Quotentabellen.

G besitzt ausdrücklich Phasenwissen, produziert synthetische Ausgaben und hat
einen eigenen kleinen Speicher. Es ist keine Variante des U-Spurbestands und
kein ressourcengleicher Architekturvergleich. Für jeden Arm separate Instanzen;
G in N darf weder Instanz noch gespeicherte Prognosen von G in D wiederverwenden.

Für jedes r und b vor Q-Ziel 4b−1 extern vergleichen: n=b−1, G-Mittelwertgültigkeit,
sämtliche 48 Mittelwertbits, Ausgabevektorbits und nach dem Ziel Fehlerbits.
Nach Feedback erneut n=b und Mittelwertbits vergleichen. **D/N-Gleichheit muss
positionsweise vollständig bestehen.** Jede Abweichung → NICHT_AUSWERTBAR
für den ganzen Versuch. Beobachterkopien dienen nur der Prüfung, nie als
Fortsetzungszustand oder zur Korrektur eines Arms. Auf Gerüstzielen sind
identische Fehler zwischen D/N nicht gefordert: ihre nächsten Hinweise können
verschieden sein. Innerhalb derselben Geschichte sind Gerüstausgaben U/G/P=P.

### P und Fehlerdefinition

P gibt an jedem regulären Prognosezeitpunkt den zuletzt beobachteten Frame aus,
ohne lernenden Zustand. Kein vorausgesetzter A/B-Katalog im Prädiktor.
MAE pro Ziel ist die vorhandene kanonische `mae48`-Berechnung über die 48 Komponenten,
mit unveränderter Summations-/Divisionsreihenfolge; die später gebundene Runtime
ist Teil der Numerik: total=0.0; für j=0,…,47 difference=abs(x[j]−y[j]),
danach total=total+difference; abschließend total/48.0. Alle Subtraktionen,
Additionen und die Division einzeln binary64-gerundet, kein FMA, kein `fsum`
oder vektorisierter Reduktionsbaum. Der unabhängige Fehlerprüfer rekonstruiert diese Semantik
aus Ausgabe-/Zielwerten, ohne Produktionsfehler zu übernehmen. Für P auf Q wird
zusätzlich die exakte Identität MAE=1/4 gefordert. Alle Ausgaben bleiben vor
dem Ziel eingefroren, insbesondere G vor seiner Mittelwertaktualisierung.

## 4. Bewertungsmengen und drei notwendige Primärkontraste

Q={4b−1 | b=1,…,256}, 256 Fortsetzungsziele je Geschichte und Arm.
G_all={3,5,…,1023}, 511 beobachtete reguläre Ziele; S=G_all ohne Q, 255 Gerüstziele.
Q_X und Q_Y je 128 Ziele, disjunkt und vollständig. Keine Vorwärm-/Kalt-/Verlust-
ausschlüsse. Prognose auf Ziel 1025 wird als rechtszensiert dokumentiert und
bei Abschluss freigegeben, nicht mit einem erfundenen Wert aktualisiert.
Keine weitere Quelle zur Vervollständigung dieses Zieles.

Für r, C∈{D,N}, a∈{U,G,P}: m[r,C,a] ist der arithmetische Mittelwert aller
256 Ziel-MAE auf Q. Genau drei Primärwerte je Geschichtenpaar:

- c1[r]=m[r,D,U]−m[r,D,G].
- c2[r]=m[r,D,U]−m[r,D,P].
- c3[r]=(m[r,D,U]−m[r,D,G])−(m[r,N,U]−m[r,N,G]).

Alle drei Erwartungen sind negativ. Hauptpunktwerte sind die ungewichteten
Mittelwerte der 32 Paarwerte; damit beide Orientierungen gleich gewichtet.
Die G-Gleichheit impliziert c3[r]=m[r,D,U]−m[r,N,U]; beide Berechnungswege
müssen exakt übereinstimmen. Keine Mittelung über scheinbar unabhängige Frames.

### Gepaarter, nach Orientierung geschichteter Clusterbootstrap

10.000 Ziehungen z=0,…,9999. R0=[1,3,…,31], R1=[2,4,…,32], jeweils aufsteigend.
Für jedes o∈{0,1} und k=0,…,15: erste acht SHA256-Bytes des UTF-8-Strings

`MCM-HX1/bootstrap/v1/z={z}/orientation={o}/k={k}`

als Big-Endian u, wähle R_o[u mod 16]. Modulo 16 ist hier ohne Restverzerrung.
Keine Zeilenumbrüche/führenden Nullen. Diese separaten Strings teilen keinen
Zähler oder Zustand mit den vier Quellenströmen. Je Ziehung somit 16 Paare pro
Orientierung mit Zurücklegen. Dieselbe Indexmatrix für alle Bedingungen,
Arme, Primärkontraste und sekundären Gesamtmasken. Paar und Orientierung bleiben
erhalten; niemals D/N, Prädiktoren oder Einzelziele getrennt resamplen.

Jeder Bootstrapwert ist der ungewichtete Mittelwert der ausgewählten 32 c-Werte.
Sortiere die 10.000 Werte aufsteigend. Quantil q durch lineare Interpolation
bei h=(9999)q: x[floor(h)]+(h−floor(h))*(x[ceil(h)]−x[floor(h)]).
Primär q=1/120 und 119/120: zweiseitige nominale 98⅓%-Intervalle.
Bonferroni-Aufteilung alpha=0,05 auf genau drei Primärkontraste.

Ziel-MAE werden für die externe Aggregation als exakte rationale Werte ihrer
gespeicherten binary64-Zahlen behandelt; Summen, Mittel, Kontraste und
Quantilinterpolation rational auswerten. Nur die Anzeige darf gerundet werden.
Ein zweiter, separat implementierter Auswerter kontrolliert die Paarwerte,
Indexmatrix und Quantile. Kein Grenzurteil aus gerundeten Dezimalanzeigen.

Der Bootstrap liefert nominale, approximative Intervalle; Bonferroni macht
deren Einzelabdeckung nicht zu einer exakten endlichen Abdeckungsgarantie.
Die Familie wird mit dieser vorab festgelegten gemeinsamen Fehlerkontrolle
beurteilt, ohne nachträglichen Wechsel zu günstigeren Tests. Keine Powerbehauptung.

### Urteile

Je Primärkontrast: obere Grenze<0 → erwarteter Vorteil BELEGT;
untere Grenze>0 → gerichtete Erwartung WIDERLEGT;
sonst NICHT_NACHGEWIESEN, einschließlich einer Grenze exakt 0.
Gesamturteil HINWEISNUTZEN_BELEGT nur, wenn alle drei oberen Grenzen<0.
Wenn mindestens eine Erwartung widerlegt ist: GEMEINSAME_ERWARTUNG_WIDERLEGT;
andernfalls bei fehlendem Teilnachweis HINWEISNUTZEN_NICHT_NACHGEWIESEN.
Technischer Fehler hat Vorrang: NICHT_AUSWERTBAR, keine Nutzenentscheidung.
Ein nicht signifikanter N-Vorteil ist weder Null- noch Gleichwertigkeitsnachweis.

### Vollständige sekundäre Auswertung

Je D/N auf Q, G_all, S, Q_X, Q_Y: U/G/P-MAE und U−G, U−P, G−P,
jeweils insgesamt sowie nach o=0/o=1. Für jeden nichtleeren Datensatz alle
Paar-/Geschichtenwerte, Zielzahlen und explorative 95%-Intervalle
(q=.025/.975); Orientierungsanalysen verwenden ausschließlich die entsprechenden
16 Ziehungen derselben Matrix. Keine zusätzlichen bestätigenden Erfolgsregeln.
Keine nachträglichen Zeitfenster. Vollständige kumulierte Zielverläufe bleiben sichtbar.

Je Vergleich U/G, U/P, G/P und Maske/Bedingung/Orientierung: Zahl besser,
schlechter, gleich; Gewinnsumme=max(Fehler Vergleich−Fehler erstgenannter Arm,0)
summiert, Schadenssumme umgekehrt, Netto, maximaler Einzelschaden, sämtliche
Maximalschadensziele und schlechtester Geschichtenmittelwert. Summen müssen
mit den vollständigen Zielreihen exakt übereinstimmen; überlappende Masken nicht addieren.

## 5. Verfügbarkeit, Erfahrung und unabhängige Referenzen

Für jedes Q-Ziel aus dem Vorzustand genau eine Klasse:
V0 keine passende berechtigte Originalspur;
V1 mindestens eine passende Spur, aber keine warme Fehlerzelle;
V2 mindestens eine warme Zelle, U gibt Persistenz aus;
V3 mindestens eine warme Zelle, U gibt eine Kontextfortsetzung aus.
V0–V3 partitionieren Q vollständig. Je Klasse Anzahl und sämtliche Gewinn-/
Schadensbeiträge gegenüber G/P getrennt nach D/N; Summe=Gesamtbilanz.
Keine nachträgliche bestätigende Untergruppenbewertung.

Extern festhalten: vorhandene/warme A/B-Nachfolger, Originalordinale,
Rolle/Generation/Offset, alle Treffer und Ausschlüsse, EC/EP und Wahlgrund
vor Entscheidung, eingefrorene Tickets, Ausgabe, Feedbackzeitpunkte,
gültige/ungültige Updates samt Grund, Zellalter als Zahl gültiger Feedbacks,
erstes/letztes Feedbackziel, Promotion, Kandidatenersetzung, Verdrängung.
In D zusätzlich dominant gemäß Quellenplan: fehlt/kalt/warm. In N keine
willkürliche dominante Fortsetzung. Alterszählung ausschließlich im Beobachter.

Fehlende oder kalte Spuren erklären eingeschränkte Gelegenheit, sind kein Grund
für Ausschluss. Warme Zellen ohne Vorteil sind ebenfalls nicht automatisch
ein Bewertungsfehler. Volle Fehlerbeiträge und Unsicherheit bleiben maßgeblich.
Zeitliche Nähe zu Verdrängung ist kein isolierter Kausalnachweis.

Unabhängige Referenzen, später separat zu implementieren und zu binden:

1. Quellenreferenz: unabhängige Schleifen/Permutation und Kontingenzprüfung;
   keine Übernahme fertiger Produktionsindexfolgen als erwartetes Ergebnis.
2. U-Referenz: eigener Bestand aus regulär aufgenommenen Frames, eigene
   Kandidaten-/Retained-Entscheidungen, Aktualitätsordnung, Abruf, Zellrekursion,
   Wahl und Feedbackberechtigung. Keine Produktionsmethoden/Bank als Oracle.
   Ereignisweise Originalwerte/-ordinale, Rollen, Generationen, Forming,
   Berechtigungen, Zellen, Auswahl und Verluste exakt vergleichen.
3. G-Referenz: eigener n/m-Zustand mit expliziten binary64-Rundungsschritten,
   unabhängig vom Produktionsmittelwert; P-Referenz aus dem vorherigen Input.
   Ausgabe-/Fehlergleichheit prüfen; D/N-G-Invariante zusätzlich separat prüfen.
4. Statistikreferenz: eigener rationaler Aggregations-/Quantilpfad aus dem
   versiegelten Zielarchiv, nicht aus fertig berechneten Produktionskontrasten.

Gemeinsame unveränderliche Inputwerte und Standard-Hashprimitive sind zulässig,
gemeinsame veränderliche Zustände oder Wiederverwendung der zu prüfenden
Auswahl-/Update-/Permutations-/Statistikfunktionen nicht. Referenzen und Beobachter
sind externe Prüfkosten; niemals abrufbarer Armzustand oder Rückfüllquelle.

## 6. Ressourcenlimits und vollständige Bilanz

### Produktionsprädiktoren

| Grenze | U | G | P |
| --- | --- | --- | --- |
| abrufbare Originalspuren | 2 Retained + 1 Kandidat | 0 | 0 |
| Originalframes inkl. gehaltener Referenzen | 18 | höchstens 2 geliehene aktuelle Frames | höchstens 2 geliehene aktuelle Frames |
| Ausgabeslots | 2, bestehende Aliase | 1, eingefroren | 1, Alias |
| numerischer Lernzustand | genau 416 Byte Bank, höchstens 6 Zellen | höchstens 400 Byte gepackt: 48×8 Mittelwert + 8 Zähler + höchstens 8 Steuerbytes | keiner |
| Zusatz-Python-Heap U / gesamter eigener Heap G/P | 16.384 Byte | 8.192 Byte | 4.096 Byte |
| Receipt UTF-8 | 16.384 Byte | 2.048 Byte | 1.024 Byte |
| transiente UTF-8-Obergrenze | 32.768 Byte | 4.096 Byte | 2.048 Byte |

U: 16 Trace-Frames plus 2 Hinweisframes, höchstens 20 Original-/Ausgabeslots
konservativ kombiniert; Aliase physisch einmal. Zusatzheap nach bestehender
Zählkonvention ohne unveränderte Basisframes, Basis und gesamter erreichbarer
Graph aber separat vollständig ausweisen. Keine zusätzliche Historie/Zähler in U.

G/P: eigener Heap umfasst Bank, Container, Objekte, Steuerung, eigene Ausgabe-
payloads und Operationstransienten. Unveränderte externe Inputobjekte werden
separat als geliehene Originale mitgezählt; keine Auslagerung eigener Daten in
diesen Bereich. G höchstens ein Mittelwertpayload und ein Ausgabepayload;
mit zwei geliehenen Frames höchstens vier 48-Komponenten-Payloads (1536 Rohbytes).
P erzeugt keinen eigenen Vektorpayload. Der externe Eingangsframe zählt als
Input, jede über die Operation hinaus gehaltene Referenz in der Armbelegung.
Receipts/UTF-8 sind Teil der jeweiligen Heapzählung, keine Zusatzfreibeträge.

Alle erreichbaren eigenen Zustände inventarisieren. Messung an Operationsgrenzen
und transienter Zusatz-/Eigenheap-Peak erforderlich; eine Grenzstellenmessung
ist kein voller Prozesspeak. Ganze Basis-/Input-/Output-/Beobachter-/Referenzkosten
separat berichten. Kein Padding für scheinbar gleiche Nutzung. Grenzverletzung
führt zum Fehlerabschluss, nicht zu einer Speichererweiterung oder Spurverkürzung.

### Umfang, Zeit und Export

64 Quellen ×1024 =65.536 Quellenframes. Je U/G/P 65.536 Aufnahmen/Verarbeitungen,
zusammen 196.608; unabhängige U/G/P-Referenzfortschritte zusätzlich 196.608.
32.704 beobachtete G_all-Ziele je Prädiktor über D/N, davon 16.384 Q-Ziele.
Je Bedingung 8192 Q-Ziele je Prädiktor; 32 unabhängige Paarwerte pro Primärkontrast.
Zensierte letzte Prognosen und Bereinigung separat ausweisen.

Ein Supervisor, höchstens ein Worker, keine parallelen Forschungsworker.
Gesamtwallclock 3600 s einschließlich Materialisierung, Referenzen, Export,
Auswertung und Abschluss. Worker höchstens 3540 s; 60 s Abschlussreserve.
Monotone Uhr; der Supervisor beendet einen überfälligen Worker vor terminalem
Abschluss und bestätigt dessen Ende. Externer gesamter Prozessspeicher
(Supervisor und Worker zusammen, private committed bytes) höchstens 512 MiB;
neutrale Qualifikation muss die Messung und Durchsetzung nachweisen.

Exportbudget insgesamt 64 MiB einschließlich Vorbereitung und Fehlerbelegen.
Feste Unterbudgets/Reservierungen als Maxima:

- Vorbereitung einschließlich neutraler Qualifikation und Bindungsdateien: 8 MiB.
- Je Quellendatei höchstens 32 KiB, alle 64 höchstens 2 MiB.
- Je Bedingungsgeschichte U/G/P gemeinsam höchstens 512 KiB komprimiert,
  höchstens 4 MiB expandiert; 64 Exporte zusammen höchstens 32 MiB.
- Verwaltung, vollständige Auswertung und globale Prüfbelege: höchstens 2 MiB.
- Terminaler Abschluss einschließlich Fehlerindex: reserviert 1 MiB.

Geplante Summe höchstens 45 MiB; verbleibender Raum ist kein automatisch
verfügbares Erweiterungsbudget für Unterbudgets. Binäre Einheiten 1024-basiert.
Vollständige Reihen, G-Vorzustände/Outputs und U-Lebenszyklen dürfen kompakt über
eindeutige IDs oder Deltafolgen verlustfrei kodiert werden, nicht weggelassen.
Kompression gzip Level 9, mtime=0, ohne Dateiname; konkrete Bibliotheksversion
vorab binden. Rekonstruktion gegen vollständig expandierte Referenz prüfen.
Externes Archiv und Referenzspeicher sind keine zusätzliche Produktionsmemory.

## 7. Neutrale Qualifikation – nur nach separatem Entwicklungsauftrag

Ein begrenztes Paket Q1–Q7 und höchstens ein vollständiger neutraler Größenablauf.
Keine HX1-Forschungsströme im Vorbereitungsschritt aufrufen oder vorab sichten.
Miniaturprüfungen verwenden feste Handtabellen, nie die 32×256 Forschungsquellen.
Kleine Korrekturen mit betroffenen Prüfungen dokumentieren; keine verdeckte
wiederholte Vollqualifikation oder Parameteränderung.

- Q1 Quellenmechanik: Handpermutationen, getrennte Stromzähler, Rejection-Grenzen
  u=L−1/L, n=1 und Höchstverbrauch; feste Teststrings im Namespace
  `MCM-HX1/neutral/v1/`. Unabhängiger Rezeptvergleich mit kleinen Listen,
  Orientierung, exakte Marginalen und ungefilterte N-Kreuztabellen.
- Q2 U-Lebenszyklus: kalte Aufnahme, erstes Feedback, Wiederabruf, Kandidaten-
  ersetzung, vollständige Bestätigung, beide Retained-Plätze, Promotionsmitnahme,
  Verdrängung, verlorene Tickets, eigene EP-Historien, Gleichstände, Bereinigung;
  technisch alle sechs Zellen einschließlich Offset 1, obwohl die Forschungs-
  familie nur Offset 0 als Fortsetzungshypothese benötigt.
- Q3 G/P: Erstziel, Update nach Freeze, festgelegte Rundung, kein Gerüstlernen,
  separate Instanzen, kein Zugriff auf ersten Hinweis oder Quoten; veränderte
  Hinweise bei identischer Zielfolge müssen G auf Q bitgleich lassen. Getrennte
  kleine Gegenproben mit veränderter Zielfolge müssen G ordnungsgemäß ändern.
- Q4 Kausalität/Referenzen: unabhängige Bestände und Numerik, ungewählte Hypothesen,
  zukünftige Werte unzugänglich, keine Rückfüllung; absichtlich falsche Auswahl,
  Zellübernahme, G-Phase und G-D/N-Abweichung müssen jeweils terminal erkannt werden.
- Q5 Statistik: vollständig vorgegebene Handtabellen, drei Kontraste einschließlich
  Interaktion, Orientierungsschichtung, gleiche Paarindices, rationale Quantile,
  Grenzen exakt 0, gemischte Richtungen, fehlende Ziele/Paare; kein Gesamterfolg
  aus nur zwei erfolgreichen Kontrasten oder bloß nicht signifikantem N-Ergebnis.
- Q6 Diagnose/Export: V0–V3 partitionieren Q; alle Gewinn-/Schadenssummen stimmen;
  kalte/verlorene Ziele werden nicht entfernt; vollständige Dekodierung und
  Hashprüfung; Quellen-/Referenz-/Beobachterdaten strikt außerhalb der Armzustände.
- Q7 Grenzen/Fehler: exklusive Zielordner, versiegelte Startbindung, fehlende
  Autorisierung, manipulierter Code/Quelle, Zeit-/Heap-/Prozess-/Exportüberlauf,
  Crash/Workerende, Teilarchive, Bereinigung und keine Wiederaufnahme.

Vollständiger neutraler Größenablauf mit denselben 32×2×1024 Positionen:
periodische Blockliste [(X,A),(X,A),(X,B),(Y,B),(Y,B),(Y,A),(X,A),(Y,B)],
Index (b+r−2) mod 8 für b=1,…,256. In neutral-N ausschließlich X/Y vertauschen,
Fortsetzungen identisch lassen. Gleiche Wiederholungs-/Speicher-/Exportarbeit,
aber keine Forschungsziehung, keine D/N-Nutzeninterpretation oder Poweranalyse.
Alle Artefakte als neutral_only=true markieren. Forschungsquellen bleiben
nicht materialisiert. Vollständige Ressourcenbelege müssen vor Freigabe passen;
ein technischer Erfolg wird nicht vorweggenommen.

## 8. Startbedingungen, Fehlerabschluss und Ergebnisumfang

Nach gesondert beauftragter Implementierung/Qualifikation: signiertes bzw.
SHA256-gebundenes Vorstartpaket mit allen PASS-Belegen, genauen Dateipfaden,
Runtime, Aufruf, exklusivem Zielordner, Ressourcenbilanz und diesem Vertragsstand.
Die operative Autorisierung muss das Paket eindeutig referenzieren und separat
genau einen Forschungsdurchlauf erlauben. Vertrag und Konzept allein erlauben
weder Vorbereitungsausführung noch Materialisierung. Historische Freigaben
anderer Untersuchungen gelten nicht für HX1.

Vor Quellenerzeugung einen exklusiven unveränderlichen Versuchsmarker anlegen;
vorhandener Marker/Zielordner verhindert Neustart. Ein Fehler verbraucht den
autorisierten Versuch; kein Resume, Retry mit anderem Seed, Fallersatz oder
automatischer zweiter Forschungsdurchlauf. Eine rein archivgestützte spätere
Prüfung darf keine neue Quell- oder Policy-Ausführung auslösen.

Jeder technische Verstoß stoppt den gesamten Versuch: Status FAILED bzw.
NICHT_AUSWERTBAR, Fehlercode, Phase, r/C/Arm/Ziel soweit bekannt, erste abweichende
Belegstelle, bereits geschriebene Dateien mit Länge/SHA256, gezählte vollständige
und unvollständige Einheiten, Zeit-/Speicher-/Exportstände, Workerstatus und
resume_permitted=false. Keine Auswertung verbleibender scheinbar guter Fälle.
Bei Prozessabbruch keine erfolgreiche Bereinigung erfinden. Falls kein
vollständiger Abschluss geschrieben werden kann, bleiben Marker/Teilarchive
als unvollständig erkennbar; niemals implizit COMPLETE.

COMPLETE nur bei vollständigen 64 Quellen/192 Prädiktorgeschichten, allen
Referenzen und Invarianten, allen Bewertungsmengen, eingehaltenen Grenzen,
beendetem Worker und geprüftem Abschlussindex. Bericht enthält drei Primär-
intervalle/Urteile, alle 32 Paarwerte, Quellenkreuztabellen, vollständige
sekundäre Bilanz, V0–V3, Schäden, Verluste, G-Gleichheitsbeleg und Ressourcen.

## 9. Aussagegrenze und Anschluss

Ein gemeinsamer Erfolg belegt begrenzte hinweisabhängige Nutzung aufgenommener
Erfahrung durch diesen Gesamtpfad unter tatsächlicher Speicherknappheit.
Kein isolierter EMA-Nachweis, keine Semantik, Clusterbildung, Feld-Memory,
Generalisierung auf neue Hinweise oder Überlegenheit gegenüber allen einfachen
hinweisabhängigen Verfahren. D/N-Unterschiede im regulären Bestand sind Teil
des geprüften Effekts, kein separat identifizierter Speicherkausaleffekt.

Verfügbarkeitsdiagnosen dürfen einen fehlenden Primärnachweis erklären helfen,
ihn aber nicht ersetzen. Alle bisherigen ULZ1-/LZ1-/T1-/F-Aussagegrenzen bleiben.
Nächster sinnvoller Schritt: fachliche Prüfung dieses Vertrags, danach gegebenenfalls
ein ausdrücklich begrenzter Implementierungs- und neutraler Qualifikationsauftrag.
Der Forschungsdurchlauf bleibt anschließend separat freizugeben.

Statische Codebelegstellen: `tools/_s2uc_four_arm.py:27` und `:86`,
`tools/_s2uc_perception_recency.py:10`, `tools/_s2uc_factor_hint.py:20`,
`tools/_s2uc_pair_context_adapter.py:41`, `tools/_s2uc_multi_error.py:97`,
`:103`, `:179`, `:267`. Die dort beschriebene U-Semantik wird nicht verändert.
