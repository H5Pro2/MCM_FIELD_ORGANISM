# ZW1: zeitliche Wiederkehr als Bedingung des Erhaltungsnutzens

2026-10-18 · Workflow 23158b34-8650-49c6-90e5-02b4b0196b70.
Status: Konzeptvorschlag, keine Implementierungs- oder Forschungsfreigabe.
Nur Dokumentation und statische Prüfung; keine Quellen erzeugt oder Kennungen ausprobiert.

## 1. Frage und ungeprüfte Gegenprognose

Die unabhängige ER1-v2-Zeugenprüfung ist abgenommen. ER1 ist abgeschlossen:
lokale Erhaltungsnutzen und Gegenkosten beider Arme sind bestätigt, das globale
Primärurteil bleibt INCONCLUSIVE. Historische Ergebnisse werden nicht neu ausgewertet.

**Ungeprüfte Hypothese H+:** Wiederbeobachtungsbasierte Auffrischung könnte E gegenüber
F helfen, wenn kürzlich wiederkehrende Hinweise auch künftig häufiger wiederkehren.
**Ungeprüfte Gegenrichtung H−:** Ohne diesen zeitlichen Zusammenhang könnten
die Verdrängungskosten von E überwiegen. Weder ein Vorteil noch ein Schaden wird garantiert.

Einzige primäre Frage: **Ist der E−F-Effekt bei positiv zeitabhängiger Hinweisfolge
kleiner als bei unabhängiger Hinweisfolge?** Erwartungsrichtung der Interaktion: negativ.
Ein negativer Interaktionseffekt allein belegt weder einen absoluten Vorteil von E in
der ersten Bedingung noch einen absoluten Schaden in der zweiten.

## 2. Unveränderte Systeme und kontrollierte Quellen

E bleibt FactorRecencyArm mit MultiErrorAdapter, F bleibt FifoObservationArm mit
FifoAdapter. Auswahl U, Fehlerfeedback, Originalidentitäten, Endmarken, Speichergrenzen
und Ressourcenmessung bleiben unverändert. Kein System erhält Bedingungs-, Hinweis-,
Phasen- oder Zukunftslabels. Jede Geschichte startet mit einem frischen Arm; keine
Zustandsübertragung zwischen Bedingungen. E und F erhalten innerhalb einer Bedingung
exakt dieselben Frames. Zwischen den Bedingungen sind die Frames bewusst verschieden.

**Vorgeschlagener Mindestumfang:** 16 unabhängige Quellenpaare r=1…16, je zwei
Bedingungen A/B mit 256 Viererblöcken = 1024 Frames. Orientierung o=(r−1) mod 2,
also acht Paare je Orientierung. Kein Startpräfix, kein Reset beim Phasenwechsel.

Gemeinsamer Blockaufbau aus ER1:
`(V((2i+1)/16), V(1/2), V(1/4+y/2), V(15/16))`,
`V(x)[j]=x+j/4096`, j=0…47; Hinweis i∈{0,1,2,3}, Fortsetzungsbit y∈{0,1}.

Für jedes Paar:

1. Ein gemeinsamer erster Hinweis K ist gleichverteilt auf vier Werten: A₁=B₁=K.
2. Für Block b=2…256 eine neue unabhängige Zufallszahl U_b, gleichverteilt auf
   {0,…,23}. In A gilt: U_b<12 behält den vorherigen Hinweis; andernfalls wählt
   floor((U_b−12)/4) einen der drei anderen Hinweise in aufsteigender Reihenfolge.
   Damit P(A_b=A_{b−1})=1/2, jede andere Transition hat Wahrscheinlichkeit 1/6.
3. In B gilt B_b=U_b mod 4. B ist über die Zeit unabhängig und gleichverteilt;
   P(B_b=i | gesamte bisherige B-Historie)=1/4. Das gemeinsame U koppelt die
   Verfahren verändert nicht die jeweiligen Gesetze. Tatsächliche Paarung entsteht
   insbesondere durch den gemeinsamen ersten Hinweis und den gemeinsamen Flipstrom;
   Rest und Quotient der gleichverteilten Zahl liefern hier unabhängige Komponenten.
4. Ein vom Hinweisstrom unabhängiger gemeinsamer Flipstrom Z_b hat P(Z_b=1)=1/4.
   Für c∈{A,B} gilt y_c,b=(i_c,b mod 2) XOR o XOR p_b XOR Z_b,
   mit p_b=0 für b≤128 und p_b=1 für b≥129. Derselbe Flip wird zum selben Block
   in beiden Bedingungen verwendet. Keine Auswahl nach realisierten Häufigkeiten.

Statisch folgt: A startet stationär; beide Hinweise sind zu jedem Zeitpunkt marginal
gleichverteilt. A hat positive kurzfristige Wiederkehrabhängigkeit, B keine.
Die nichttrivialen Eigenwerte der A-Übergangsmatrix sind 1/3, daher nimmt der
Zusammenhang mit zeitlichem Abstand ab; das ist eine Quellenannahme, kein KI-Befund.
Für beide Bedingungen gilt dieselbe bedingte Fortsetzungsverteilung je Hinweis,
Orientierung und Phase: dominanter Ausgang 3/4, anderer 1/4. Auch die marginale
Fortsetzungsverteilung ist identisch. Beide Bedingungen sehen denselben festen
Wechsel nach 128 Blöcken; innerhalb der Systeme bleibt er unbekannt.

**Deterministisches späteres Rezept, heute nicht ausführen:** vorgeschlagener einziger
Namensraum `MCM-ZW1/source/v1`; unabhängige Streams `cue` und `outcome` je Paar.
SHA-256-Schlüssel `{namespace}/r={r}/stream={name}/draw={cursor}`, Cursor ab 0;
erste acht Bytes unsigned Big-Endian, rejection sampling wie ER1. Cue einmal below(4),
danach 255-mal below(24); Outcome 256-mal below(4), Flip genau bei 0. Höchstens
4096 Rohziehungen je Stream, sonst technischer Abbruch ohne Ersatzkennung.
Neutrale Qualifikation muss später einen getrennten Namensraum verwenden.
Alle 32 Quellen und ihre unabhängigen Rekonstruktionen wären vor dem ersten Arm
zu versiegeln. Keine alten ER1-Quellen, günstigen Teilgruppen oder Kennungssuche.

## 3. Tragfähigkeit und unvermeidbare Unterschiede

Die Isolation ist **auf Ebene der Quellengesetze tragfähig**, nicht als identische
realisierte Häufigkeitstabelle: gleicher stationärer Hinweisrand, gleiche bedingte
Fortsetzungsregel, identische Frameform, Länge, Informationszugänge und Budgets;
geändert wird die zeitliche Abhängigkeit der Hinweise.

Unvermeidlich ändern sich Lauf-/Wiederkehrlängen, Zahl unmittelbarer Wiederholungen,
lokale Häufigkeiten, Kandidatenbestätigungen, Promotionen, Verdrängungen und Chancen
auf Feedback. Diese Größen sind Folgen der manipulierten Sequenzabhängigkeit, keine
zusätzlichen unabhängig eingestellten Faktoren. Auch die zeitliche Abhängigkeit der
Fortsetzungen kann sich über die Hinweisabhängigkeit ändern, trotz gleicher
bedingter und marginaler Fortsetzungsverteilungen. Der Vergleich kann deshalb keinen
isolierten direkten Effekt einer einzelnen Auffrischungsoperation identifizieren.

Realisierte Hinweis- und Fortsetzungshäufigkeiten können zwischen A/B abweichen.
Exakte Gleichheit durch Permutation eines festen Beutels wäre kein gleichwertiger
Ersatz für B: Ziehen ohne Zurücklegen erzeugt Restmengenabhängigkeit; ein aus A
übernommener Beutel kann außerdem latente Häufigkeitsunterschiede übertragen.
Keine nachträgliche Frequenzangleichung, Nachgenerierung oder Gewichtung.

Der feste Fortsetzungswechsel ist in beiden Bedingungen gleich, kann aber mit
unterschiedlichen Wiederkehrmustern interagieren. Die Aussage gilt daher für diese
gesamte zweiphasige Quellenfamilie, nicht isoliert für stationäres Fortsetzungslernen.
Die gemeinsame Zufallskopplung ist festgelegt, garantiert aber keine Varianzreduktion.
Wenn exakte realisierte Häufigkeitsgleichheit UND echte zeitliche Unabhängigkeit
gefordert werden, ist dieser Vorschlag dafür ungeeignet; diese stärkere Isolation
wird ausdrücklich nicht behauptet.

## 4. Ein vorab definierter Interaktionsvergleich

Statistische Einheit ist das **Quellenpaar**, nicht Frame, Zeuge oder einzelner Arm.
Alle vier Ausführungen eines Paares bleiben bei jeder Auswertung zusammen.

Für c∈{A,B}: `D_r,c = Σ_t(MAE_E,r,c,t − MAE_F,r,c,t)/511`,
t=3,5,…,1023. Auch kalte, gleiche, erfolglose und nicht zugeordnete Ziele bleiben
enthalten; Ziel 1025 ist wie in ER1 zensiert. Dann
`I_r=D_r,A−D_r,B` und einziges Primärmaß `I=Σ_r I_r/16`.

Vollnenner: 8176 E/F-Zielpaare je Bedingung, 16352 über beide Bedingungen;
32704 einzelne Armfehlerwerte. Die unabhängige Stichprobe umfasst nur 16 Paare.
Keine historische Stichprobe wird ergänzt, keine Zielposition als unabhängige
Replikation behandelt, keine warmen Teilgruppen als neue Hauptauswertung.

Vorgeschlagenes vorab festzuschreibendes Verfahren: nominal zweiseitiges
95%-Perzentilintervall für I aus 10000 gepaarten Bootstrapziehungen, geschichtet nach
Orientierung (acht vollständige Paare mit Zurücklegen aus jeder der beiden Schichten).
Dieselben Paarindizes gelten gleichzeitig für A, B, E und F. Rationale Summen aus
den gespeicherten binary64-Fehlern; Quantile durch lineare Interpolation h=9999q.
Neue 16-spaltige Indexmatrix erst in einem gesonderten Vorbereitungspaket erzeugen
und vor Forschung binden. Die alte 32-Geschichten-Matrix darf nicht unverändert
übernommen werden. Separate unabhängige Statistikreferenz für I und seine Paardifferenzen.

| Vorab festes Kriterium | Primärurteil |
|---|---|
| obere Intervallgrenze <0 | Richtung der Gegenprognose für die Interaktion gestützt |
| untere Intervallgrenze >0 | entgegengesetzte Interaktion; Gegenprognose widersprochen |
| Intervall enthält oder berührt 0 | INCONCLUSIVE; keine Gleichwertigkeit |
| fehlendes Paar/Ziel, Herkunfts-, Referenz- oder Ressourcenfehler | technisch nicht auswertbar; kein Teilserienurteil |

D_A und D_B, Gewinn-/Schadenssummen, beidseitige Zeugen und Wiederkehrabstände
werden deskriptiv berichtet, ohne zusätzliche Signifikanzentscheidungen.
„In A signifikant, in B nicht“ ersetzt niemals den Test auf I. Selbst ein negatives
Intervall für I erlaubt keine Aussage „E hilft in A und schadet in B“, solange diese
absoluten Vorzeichen nicht gesondert belegt sind; das wäre eine andere Forschungsfrage.
Keine Power- oder Mindestnutzenzusage: 16 Paare können für kleine Interaktionen
unzureichend sein. Ein unentschiedener Ausgang löst keine automatische Erweiterung aus.

## 5. Neuigkeitsprüfung anhand vorhandener Verträge und Code

Statisch gelesen: ER1-Konzeptvertrag Abschnitte 4–7; `_s2uc_er1_v2_sources.py`
(`generate`, `reconstruct`); `_s2uc_er1.py`, `_s2uc_factor_recency.py`,
`_s2uc_perception_recency.py`; `_s2uc_er1_stats.py` und `_s2uc_er1_run_statistics.py`.
Die vorhandenen Dateien werden nicht geändert oder ausgeführt.

ER1 verwendet ausschließlich die A-artige Bleibewahrscheinlichkeit 1/2 und bewertet
E−F über 32 Geschichten. Sein Bootstrap und Vollständigkeitsprüfer erwarten genau
diese 32 Geschichten, nicht 16 Vierfachpaare. Bestehende Quellen-/Statistikeinstiege
sind deshalb nicht unverändert für ZW1 zugelassen.

Lokale Erhaltung, warme Auswahl und Gegenkosten sind bereits bekannt und unabhängig
bestätigt. Ihr erneutes bloßes Auftreten wäre keine neue Erkenntnis. Neu wäre allein
die kontrollierte **Änderung des vollständigen E−F-Effekts** durch das Gesetz der
zeitlichen Wiederkehr. Historische warme Teilgruppen, günstigere Orientierungen oder
Zeugen liefern weder die B-Bedingung noch einen gültigen Interaktionskontrast.

## 6. Vollständiger Umfang und Entscheidungsgrenze

| Vorgeschlagenes Paket | Anzahl |
|---|---:|
| unabhängige Quellenpaare | 16 |
| Quellen/Geschichten (A+B) | 32 |
| Frames je Geschichte | 1024 |
| Policy-Arme (16 × 2 Bedingungen × E/F) | 64 |
| begleitende Live-Referenzen | 64 |
| unabhängige Archivrekonstruktionen | 64 |
| unabhängige Quellenrekonstruktionen | 32 |
| unabhängige Gesamtstatistikreferenz | 1 |
| zusätzliche Policy-Mess-/Capture-Arme | 0 |
| geplante Bootstrapziehungen, einmal für die Interaktion | 10000 |

Damit bleibt die Zahl der Forschungsarme im bisherigen 64er-Rahmen, während sich
Paarung und Forschungsfrage ändern. Das ist keine Übertragung der verbrauchten
ER1-Freigabe. Eine Alternative mit 32 Paaren hätte 64 Geschichten, **128 Policy-Arme,
128 Live-Referenzen, 128 Archivrekonstruktionen und 64 Quellenrekonstruktionen**;
sie ist nicht Teil dieses Vorschlags und benötigt eine gesonderte Umfangsentscheidung.

Keine zusätzliche neutrale Ausführung ist hier enthalten oder freigegeben.
Ein späteres Implementierungs-/Qualifikationspaket muss seinen neutralen Umfang
separat ausweisen. Die vorstehenden Referenzzahlen bezeichnen die Forschungsserie.

Bestehende Policybudgets bleiben: zwei Retained-Viererspuren, ein Viererkandidat,
höchstens vier Bildungsframes, 18 Originalframes plus zwei Ausgabeslots, 416-Byte-Bank,
Zusatzheap/Receipt je 16384 Byte, UTF8 transient 32768 Byte, höchstens zwei Endmarken.
Bestehende Gesamtobergrenzen bleiben: Worker 54000 s, gesamt 57600 s einschließlich
3600 s Reserve, gemeinsamer Job 512 MiB, höchstens zwei Prozesse; Vorbereitung 8 MiB,
Quellen gesamt 2 MiB/je 32 KiB, Archive gesamt 32 MiB/je gzip 512 KiB,
encoded/dictionary je 4 MiB, Record 256 KiB, nodes/indices je 65536, edges 262144,
Collections 16, Temporär/Export je 64 MiB, Administration 2 MiB, Closure 1 MiB.
Gleiche Fallzahl beweist weder Laufzeit- noch Speicherverträglichkeit des neuen
Quellenregimes; separate neutrale Qualifikation wäre erforderlich. Kein Anheben
dieser Grenzen aus diesem Konzept ableiten.

**Nächste Entscheidung beim Projektleiter:** Ist die Isolation auf Ebene der
Verteilungsgesetze mit den ausdrücklich genannten Folgeunterschieden und 16 Paaren
fachlich ausreichend? Bei Zustimmung erst ein begrenztes Implementierungs- und
Qualifikationspaket beauftragen; ein Forschungsstart bleibt separat zu entscheiden.
Heute wurden nur dieser Vertrag und die drei Projektübersichten geschrieben.
