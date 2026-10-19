# LZ1-Einmallauf: Ergebnisbericht vom 2026-10-04

**COMPLETE – genau ein freigegebener Forschungsdurchlauf.** Alle96 Geschichten
mit P,U,H64 ausgeführt:288 Arme,99.840 Quellenframes,299.520 armbezogene Frames,
49.824 bewertete Ziele je Arm und24.576 primäre G_Y-Ziele je Arm.
Keine Wiederholung, Seed-Auswahl, Fallkürzung oder Änderung der gebundenen Kriterien.
A1/K1 bleiben deaktiviert. Die Einmalbeauftragung ist verbraucht.

## Getrennte Urteile

| Frage | Urteil | Tragweite |
| --- | --- | --- |
| Technische Gültigkeit | AUSWERTBAR | Vollständigkeit, Referenzen, Kausalität, Budgets und Abschluss bestanden |
| Informationsnachweis durch H64 | BELEGT in S und W | Mittlerer G_Y-Fehler gegenüber Persistenz niedriger; beide primären Intervalle unter0 |
| Nutzung durch U | BELEGT in S und W | Unverändertes U nutzt die vorhandene Lerngelegenheit; beide primären Intervalle unter0 |
| Vergleich U/H64 | U insgesamt schlechter in S und W, sekundärer Befund |95%-Intervalle von U−H64 vollständig positiv; kein MCM-spezifischer Mehrwert belegt |

Belegt ist ein begrenzter Lernnutzen bei wiederkehrender Fortsetzungsverteilung
innerhalb vorhandener Kapazität. Die Fehler sind nicht verschwunden. Historische
negative T1/F-Befunde bleiben unverändert; sie werden nicht neu bewertet oder
aufgehoben. Kein Nachweis für Transfer, Verdrängungsrobustheit oder feldinterne Memory.

## Vier primäre Kontraste auf G_Y

Je Bedingung32 Wiederholungen mit jeweils256 Y-Fortsetzungen, also8.192 Ziele
je Arm. Kontrast ist linker Arm minus Persistenz; negative Werte bedeuten Vorteil.
Vorab festgelegte10.000 gepaarte Bootstrap-Ziehungen der32 Wiederholungstripel,
98,75%-Intervalle mit nominaler Bonferroni-Aufteilung für die vier Primärkontraste.
Die Intervalle sind die vorab bestimmte finite Bootstrap-Auswertung, keine
zusätzliche nachträgliche Testauswahl. Tabellenwerte sind gerundet; vollständige
Zahlen und sämtliche Wiederholungswerte bleiben im Archiv erhalten.

| Bedingung | Kontrast | mittlere MAE-Differenz |98,75%-Intervall | Urteil |
| --- | --- | ---: | --- | --- |
| S | H64-P | -0,147705078 | [-0,152237129; -0,143402100] | BELEGT |
| S | U-P | -0,089141846 | [-0,095947266; -0,082641602] | BELEGT |
| W | H64-P | -0,132537842 | [-0,137390137; -0,127639580] | BELEGT |
| W | U-P | -0,092376709 | [-0,099243164; -0,085037041] | BELEGT |

Absolute mittlere Fehler auf G_Y:

| Bedingung | P | U | H64 |
| --- | ---: | ---: | ---: |
| S | 0,250000000 | 0,160858154 | 0,102294922 |
| W | 0,250000000 | 0,157623291 | 0,117462158 |
| N | 0,250000000 | 0,252563477 | 0,247528076 |

[Alle81 primären/sekundären Kontraste](contrasts.csv),
[Maskenmittel aller96 Geschichten](case-mask-means.csv),
[gebundenes Gesamtergebnis mit32 Einzelwerten pro Kontrast](../lz1-comparison-20261004-01/assessment.json).
Keine Mittelwerte nur ausgewählter oder warmer Ziele ersetzen G_Y.

## Nullkontrolle und Gerüst strikt getrennt

N-G_Y, sekundäre95%-Intervalle:

| Kontrast | mittlere Differenz |95%-Intervall |
| --- | ---: | --- |
| H64-P | -0,002471924 | [-0,007659912; 0,002685547] |
| U-P | 0,002563477 | [-0,003906250; 0,009582520] |
| U-H64 | 0,005035400 | [-0,002410889; 0,012542725] |

Alle drei Intervalle enthalten0. Ein systematischer Y-Vorteil ist in N nicht
nachgewiesen; das ist kein Gleichwertigkeits- oder Unmöglichkeitsbeweis.
Im deterministischen Gerüst beträgt der Fehler für alle Arme in S/W/N jeweils0.
Die Gerüstkontraste sind deshalb0 mit Intervall[0;0]. Der primäre Vorteil stammt
hier nicht aus Gerüstleistung. Grundsätzlich wäre ein Gerüstvorteil auch in N
kein Informationslecknachweis.

G_post enthält gleich viele Y- und Gerüstziele und halbiert daher hier die
G_Y-Mittel. Gesamtverlauf einschließlich Präfix und sämtliche übrigen Masken
stehen vollständig in `case-mask-means.csv`; sie sind sekundär.

## Festgelegte Zeitfenster und Wechselanpassung

P-MAE ist in allen folgenden Y-Fenstern0,25. Der Wechsel in W liegt zwischen
Block128 und129. S/N verwenden dieselben Fenster ohne entsprechenden Wechsel.
Alle Intervalle dieser Tabelle sind sekundäre95%-Intervalle.

| Bedingung | Y-Blöcke | U-MAE | H64-MAE | U−P-Intervall | H64−P-Intervall |
| --- | --- | ---: | ---: | --- | --- |
| S | 1–32 | 0,156738281 | 0,109619141 | [-0,110351562; -0,077148438] | [-0,154541016; -0,126708984] |
| S | 33–128 | 0,157633464 | 0,098144531 | [-0,102620443; -0,082682292] | [-0,157552083; -0,146484375] |
| S | 129–160 | 0,168945312 | 0,106445312 | [-0,098632812; -0,063964844] | [-0,156250000; -0,130371094] |
| S | 161–256 | 0,162760417 | 0,102620443 | [-0,096354167; -0,077799479] | [-0,153401693; -0,141194661] |
| W | 1–32 | 0,156738281 | 0,109619141 | [-0,110351562; -0,077148438] | [-0,154541016; -0,126708984] |
| W | 33–128 | 0,157633464 | 0,098144531 | [-0,102620443; -0,082682292] | [-0,157552083; -0,146484375] |
| W | 129–160 | 0,168945312 | 0,252441406 | [-0,097180176; -0,063964844] | [-0,010742188; 0,014648438] |
| W | 161–256 | 0,154134115 | 0,094401042 | [-0,106445312; -0,084635417] | [-0,161783854; -0,149414062] |
| N | 1–32 | 0,242187500 | 0,241943359 | [-0,023925781; 0,008300781] | [-0,022216797; 0,005859375] |
| N | 33–128 | 0,250325521 | 0,249023438 | [-0,010416667; 0,011230469] | [-0,009114583; 0,007242839] |
| N | 129–160 | 0,264648438 | 0,246826172 | [-0,002441406; 0,031750488] | [-0,016601562; 0,010009766] |
| N | 161–256 | 0,254231771 | 0,248128255 | [-0,006347656; 0,014485677] | [-0,010253906; 0,006266276] |

Im frühen Wechselzeitfenster129–160 liegt U weiter unter P.
H64 liegt dort mit mittlerem Fehler0,252441406 nahe P; sein Intervall zu P
enthält0. U−H64 beträgt−0,083496094 mit95%-Intervall
[−0,097900391;−0,068603516]. Dies ist ein vorab benannter sekundärer Vorteil
von U im frühen Wechselzeitfenster, kein neuer Primärnachweis.

Im späten Fenster161–256 liegen beide Arme wieder unter P.
H64 erreicht0,094401042, U0,154134115. U−H64 ist dann
+0,059733073 [0,053222657;0,066569010]. Damit beruht die Aussage über
Leistung nach dem Wechsel auf den festgelegten Nachwechselwerten, nicht allein
auf dem günstigen W-Gesamtmittel. Eine genaue individuelle Anpassungslatenz
oder garantierte Erholung jeder Geschichte wird aus diesen Fenstermitteln nicht behauptet.

Die Befunde passen zu unterschiedlicher kurzfristiger Reaktion und längerfristiger
Häufigkeitsschätzung. Das ist eine technische Interpretation; Speicherumfang
und Bewertungsverfahren unterscheiden sich zugleich, ihre Ursachenanteile sind
hier nicht isoliert.

## Vollständiger Erfahrungszyklus

Das feste Präfix wurde als gewöhnliche Wahrnehmung verarbeitet. In allen96 Fällen
wurden die Originalspuren1–4 und9–12 durch vollständige Wiederkehr regulär erhalten.
Es gab keine direkte Speicherbefüllung, keine A1-Zulassung und kein Nachtraining
bis zu einem gewünschten Ergebnis.

- 24.576 Y-Ziele mit jeweils beiden lebenden Originalhypothesen;
- 49.152 warme Hypothesenvorkommen und49.152 lebend übernommene
  Hypothesenfeedbacks an diesen Y-Zielen;
- 24.768 vollständige Bestätigungen einschließlich Aufnahmepräfix;
- 24.574 Kontextwahlen an Y-Zielen, zwei Enthaltungen wegen fehlender geschätzter
  Verbesserung: LZ1-21-S und LZ1-21-W, jeweils Ziel483;
- 99.840 unabhängige U-Zustandsfortschreibungen und49.824 H64-Feedbackabgleiche;
- U-Abschluss in allen96 Geschichten geleert; H64 je Geschichte ohne Reset
  am Wechsel, Rückmeldungszählung durchgehend0…518.

Jede Prognose entstand vor ihrem Ziel; die Fehlerzellen der konkurrierenden
Originalspuren wurden erst anschließend mit dem tatsächlichen Ziel aktualisiert.
An den Y-Zielen liegen beide Spuren innerhalb der zwei verfügbaren Retained-Plätze.
Damit scheitert dieser Versuch nicht an fehlender Aufnahme, Verdrängung oder
unterbrochenem Feedback. Ein Speicherknappheitstest war ausdrücklich nicht Gegenstand.

[Zyklusbelege aller Geschichten](cycles.json),
[alle49.824 Zielzeilen mit Entscheidungen und kumulierten Differenzen](targets.csv).
Die Fallakten im Laufarchiv enthalten zusätzlich alle Receipts, Zellen vor
Auswahl, Feedbackereignisse, Originalidentitäten und H64-Stimmen/Überschreibungen.
Sie sind verlustloses gzip-JSON; Quellen liegen als exakte Vektorkataloge mit
Indexfolgen vor. Für diese Berichtsauswertung erfolgte kein Replay.

## Gewinne, Schäden und Abstand zum lernenden Vergleich

Je Tabellenzeile vollständig8.192 G_Y-Ziele. Gewinn-/Schadenssummen summieren
die Beträge der einzelnen MAE-Differenzen; sie sind keine mittleren Fehler.
„Schlechteste Wiederholung“ ist die größte mittlere Differenz unter allen32.

| Bedingung | Vergleich | besser | schlechter | gleich | Gewinnsumme | Schadenssumme | größter Zielschaden | schlechteste Wiederholung |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| S | U-P | 5556 | 2635 | 1 | 1389,000000000 | 658,750000000 | 0,250000000 | -0,064453125 |
| S | U-H64 | 358 | 1317 | 6517 | 172,000000000 | 651,750000000 | 0,500000000 | 0,079101562 |
| W | U-P | 5609 | 2582 | 1 | 1402,250000000 | 645,500000000 | 0,250000000 | -0,050781250 |
| W | U-H64 | 637 | 1284 | 6271 | 301,750000000 | 630,750000000 | 0,500000000 | 0,067382812 |
| N | U-P | 4054 | 4138 | 0 | 1013,500000000 | 1034,500000000 | 0,250000000 | 0,054687500 |
| N | U-H64 | 1958 | 2055 | 4179 | 843,750000000 | 885,000000000 | 0,500000000 | 0,043945312 |

U verbessert damit gegenüber P in S5.556 Ziele und verschlechtert2.635;
in W5.609 Verbesserungen und2.582 Verschlechterungen. Auch ein in jeder
S/W-Wiederholung günstiger mittlerer Unterschied bedeutet keine Schadensfreiheit
an einzelnen Zielen. Größter Zielmehrfehler gegenüber P0,25, gegenüber H640,5.
Es wurde keine historische A1-Schadensschwelle auf LZ1 übertragen und kein neues
binäres Schadensurteil nachträglich eingeführt.

U−H64 über die gesamte primäre Y-Menge, sekundär:

| Bedingung | mittlere Differenz |95%-Intervall | Einordnung |
| --- | ---: | --- | --- |
| S | 0,058563232 | [0,055297852; 0,061889648] | U hat höheren Fehler |
| W | 0,040161133 | [0,036499023; 0,044036865] | U hat höheren Fehler |

H64 speichert einen Ring der letzten64 Hinweis-Ziel-Tripel mit73.728Byte
Nutzdaten; sein gemessener Heap beträgt maximal78.964Byte. U benötigt hier
maximal5.495Byte Zusatzheap plus die nach bestehender Konvention separat
gezählten Originalframes. H64 darf bis128KiB nutzen, U-Zusatzheap bis16KiB.
Das ist kein kapazitätsgleicher Vergleich. H64s geringerer mittlerer Fehler
belegt die Verfügbarkeit nutzbarer Information und den Rückstand dieses U-Pfads,
nicht, dass allein mehr Speicher die Ursache des Vorteils ist.

Alle54 Schadensauswertungen einschließlich Präfix, Gerüst und Zeitfenstern
stehen in [harms.csv](harms.csv). Die vollständigen Zielzeilen enthalten auch
die kumulierten U−P-/U−H64-Differenzen; Wechselkosten sind nicht ausgeblendet.

## Ressourcen, Integrität und Einmalgrenze

Worker180,083s von3.540s; Supervisor bis vor terminalem Abschluss181,694s
von3.600s mit60s Abschlussreserve. Alle Limits eingehalten.

U: Zusatzheap5.495Byte, konservativ12 Originalframes/14 kombiniert,
zwei Ausgabeslots,416Byte Bank, Receipt772Byte, UTF-8-Obergrenze1.544Byte.
Die nicht eingeschalteten Frame-Tracing-Zähler sind keine gemessene Nullbelegung.
H64: maximal78.964Byte Heap,73.728Byte Ring. P:384Byte Vektornutzdaten;
Python-Repräsentation und Rechenaufwand wurden in der neutralen Qualifikation
separat dokumentiert, hier nicht neu als Laufmessung ausgegeben.

Vorbereitung4.446.703Byte; vollständiger Laufexport einschließlich Abschluss
5.551.555Byte. Zusammen9.998.258Byte unter64MiB einschließlich der vorgesehenen
Abschlussreserve; Vorbereitung unter8MiB. Die separate Archivauswertung fügt
Bericht und Tabellen hinzu, ohne das versiegelte Laufarchiv zu verändern.
Die Supervisorzeitmessung endet wie vorgebunden vor dem terminalen Schreibvorgang.

197 im Laufabschluss aufgeführte Dateien auf Länge und SHA256 geprüft.
[Prüf- und Ressourcenbilanz](verification.json).

Vorstart-SHA256:
`e4c57655eae1b954ea22807beb42d26bb28ce8df468c8c64f8048702046c9da3`.
Operative Autorisierung aus der Vorlage, nur Status AUTHORIZED_ONCE gesetzt:
`146a3d170edad2b4447e0146be7e6791c04b03cdb41b6541ef6da1c5a4b35b65`.
Laufabschluss-SHA256:
`4c04de12a48828669425e72e2b0b9881b739b8b7bb2f3eef7675a1deded9721d`.
[Versiegelter Laufabschluss](../lz1-comparison-20261004-01/closure.json).

Die operative Datei bleibt als historischer Startbeleg unverändert. Der
vorhandene Zielordner, `resume_permitted=false` und dieser Abschluss dokumentieren
den Verbrauch der Einmalfreigabe. Kein Neustart, keine automatische Wiederholung.

## Fachliche Schlussfolgerung und nächster sinnvoller Schritt

LZ1 belegt die beiden zunächst getrennten Fragen: Die Vergangenheit enthält
nutzbare Information für die wiederkehrende Fortsetzungsverteilung, und der
unveränderte begrenzte U-Mechanismus nutzt sie im Mittel gegenüber Persistenz.
Einzelne Schäden bleiben trotz dieses Vorteils erwartbar. Die Nullkontrolle
zeigt keinen nachgewiesenen systematischen Vorteil auf der richtigen Y-Maske.

H64 nutzt die Gelegenheit über den gesamten S/W-Verlauf besser, während U im
frühen Wechselzeitfenster günstiger reagiert. Daraus folgt kein MCM-spezifischer
Mehrwert und keine Rechtfertigung einer sofortigen Speicher-/Auswahländerung.
Die beiden gesicherten Originalspuren und das gezielt einfache Quellenformat
begrenzen die Aussage auf vorhandene Kapazität. T1/F-Negativbefunde bleiben gültig.

Empfehlung an den Projektleiter: diesen begrenzten Lernnachweis und den Abstand
zu H64 abnehmen. Vor Änderungen am MCM-Pfad als nächsten konzeptionellen Schritt
einen kapazitätsgleichen einfachen Vergleich festlegen, damit Speicherumfang
und Bewertungsstrategie nicht weiter miteinander vermischt werden. Erst dessen
begründeter Prüfvertrag sollte einen neuen Entwickler- oder Versuchsauftrag tragen.
Dieser Bericht startet weder eine neue Variante noch einen weiteren Durchlauf.
