# U/A1-Einmallauf: vollständiger Ergebnisbericht vom 2026-10-04

Der separat beauftragte Lauf ist genau einmal gestartet und COMPLETE abgeschlossen.
24/24 Vertragsfälle,48/48 Arme,3.584 Aufnahmen und unabhängige
Referenzfortschreibungen,872 bewertete Ziele je Arm. Kein Abbruch, kein Neustart,
keine Regel- oder Kriterienänderung. A1 bleibt standardmäßig deaktiviert.
Die Einmalbeauftragung ist verbraucht; keine automatische Wiederholung.

## Vertragsurteile

| Urteil | Ergebnis | Begründung |
| --- | --- | --- |
| Technik | AUSWERTBAR | Vollständige Fall-/Zielmenge, Referenzgleichheit, Limits und Abschluss bestanden |
| Mechanismus | NICHT_NACHGEWIESEN | Modale warme T1-Möglichkeiten unverändert80/624 |
| Gesamtnutzen | NICHT_NACHGEWIESEN | T1-Mittel verschlechtert; geforderte strikte T1-Verbesserung fehlt |
| Schaden | GRENZE_EINGEHALTEN | Jede mittlere Falldifferenz unter1/32; T1-G_w unverändert |

Schadensgrenze bedeutet keine Schadensfreiheit. Der Vertrag begrenzt die
mittlere Falldifferenz, nicht den größten einzelnen Zielfehler.
Die324 Diagnoseziele bleiben bei0 modalen warmen Möglichkeiten beider Arme.
Anpassung bleibt0/52, jeweils0/13 pro Gruppe, mit20 Negativkontrollen.

## Vollständige Nutzenbilanz

Mittel sind wie vorab festgelegt gleich gewichtete Fallmittel.

| Fallmenge | U | A1 |
| --- | ---: | ---: |
| T1,16 Fälle | 0,05347585104979002 | 0,053612703314194314 |
| F,8 Fälle | 0,026776713709677418 | 0,02649319556451613 |
| Alle24 | 0,04457613860308582 | 0,04457286739763492 |
| T1-G_w | 0,03089406092961629 | 0,03089406092961629 |

15 Zielverbesserungen,7 Verschlechterungen,850 Gleichstände über alle872 Ziele.
15 Verbesserungen zu jeweils0,0078125 summieren sich auf15/128.
Sechs F-Schäden zu jeweils0,0078125 plus der T1-Schaden summieren sich auf
17337/131072. Die ungewichtete Zielschadenssumme ist damit größer als die
Zielgewinnsumme; das etwas bessere gleich gewichtete24-Fallmittel ist kein
Widerspruch, weil T1- und F-Fälle unterschiedlich viele Ziele enthalten.

Nur vier Fallmittel ändern sich:

| Fall | A1 minus U | Verbesserte Ziele | Verschlechterte Ziele |
| --- | ---: | --- | --- |
| T1-1-3 | +0,00218963623046875 | keine | 17 |
| F3 | +0,00025201612903225806 | 31,55 | 11,35,59 |
| F4 | -0,0005040322580645161 | 39,51,63 | 43 |
| F7 | -0,0020161290322580645 | 11,15,27,31,35,39,51,55,59,63 | 19,43 |

Die übrigen20 Fallmittel sind gleich. Alle Einzelwerte stehen in
[targets.csv](targets.csv), alle Fall-/Maskenmittel in
[case-metrics.csv](case-metrics.csv). Exakte Brüche bleiben im
[gebundenen Gesamtergebnis](../a1-comparison-20261004-01/assessment.json) erhalten.

## Zulassung, Bestätigung, Feedback und Wiederabruf

Zählung je Ereignis beziehungsweise berechtigter Hypothese; mehrere Hypothesen
können dasselbe Ziel betreffen. Vollständige Bestätigungen sind keine bloßen
Retained-Rollen und keine Teilzulassungen.

| Stufe über alle24 Fälle | U | A1 |
| --- | ---: | ---: |
| Teilzulassungen | 0 | 18 |
| Vollständige Bestätigungen | 76 | 82 |
| davon Kandidaten-/Retained-Bestätigungen | 17/59 | 7/75 |
| Verarbeitetes Hypothesenfeedback | 237 | 270 |
| Verworfenes Hypothesenfeedback | 12 | 12 |
| Warme Hypothesenabrufe | 193 | 231 |
| Spätere warme Abrufe nach Teilzulassung | 0 | 51 |
| Durch Teilzulassung verdrängte Spuren | 0 | 6 |

T1: fünf Teilzulassungen, fünf spätere warme Abrufe nach Teilzulassung;
verarbeitetes Feedback174→179 und warme Abrufe168→173. Keine zusätzliche
modale warme Möglichkeit und keine bessere T1-Prognose.
F:13 Teilzulassungen,46 spätere warme Abrufe nach Teilzulassung;
verarbeitetes Feedback63→91 und warme Abrufe25→58.
Die51 Abrufe nach Teilzulassung sind nicht51 zusätzliche Abrufe gegenüber U.
Sie sind eine andere Ereignismenge als die38 zusätzlich verfügbaren warmen
Hypothesenvorkommen. [stages.csv](stages.csv) trennt alle Fälle und Arme.

## Zusätzliche Erfahrung und ihre Grenzen

38 zusätzliche Hypothesenvorkommen an36 Zielen entsprechen acht eindeutigen
Originalspur-Offset-Linien. Alle38 sind warm;25 liefern den tatsächlichen und24
den modalen Nachfolger. Fünf zusätzliche warme Vorkommen liegen in T1,
33 in F. Wärme allein belegt weder modale Eignung noch Vorhersagenutzen.

Konkreter nutzbarer Zyklus in F7: Originalspur1–4/Offset0 wird bei6 teilzugelassen,
Feedback bei7 verarbeitet und bei Ziel11 warm ausgewählt. A1 verbessert dieses
Ziel um0,0078125. Dieselbe Linie verursacht bei19 und43 aber Mehrfehler.
Beleg: [F7-Fallauswertung](../a1-comparison-20261004-01/F7-assessment.json),
`rows` mit `target=11,19,43`, sowie dort `stages.A1.partial_lineage_chains`.

T1-1-1 und T1-1-4 erhalten Originalspur45–48/Offset1 bei50, verarbeiten Feedback51
und rufen sie bei69 beziehungsweise73 warm ab. Die Prognosen verbessern sich
nicht. T1-1-2 und T1-2-3 verarbeiten Feedback nach Teilzulassung, haben danach
keinen warmen Wiederabruf dieser Linie. Alle fünf T1-Ketten sind vollständig in
[lineages-and-losses.json](lineages-and-losses.json) enthalten.

## Konkreter größter Schaden

T1-1-3, Ziel17: U-Fehler0; A1-Fehler0,08539581298828125.
Originalspur1–4/Offset0 wird bei6 zugelassen, Feedback7 wird übernommen.
Vor Ziel17 hat diese Linie Ec=0,08672873179117839 und Ep=0,08912928899129231.
Der bestehende Auswahlmechanismus bevorzugt damit den alten Originalnachfolger3.
Dieser ist am Ziel17 weder tatsächlich richtig noch modal; die U-Persistenz
ist hier richtig. Es handelt sich um schädliche Wiederverwendung einer warmen
Spur, nicht um einen Verdrängungsschaden.
Beleg: [T1-1-3-Fallauswertung](../a1-comparison-20261004-01/T1-1-3-assessment.json),
`rows[target=17].arms.A1.selected`, Feedbackhistorie und Teilzulassungskette;
Rohreceipts im [A1-Arm](../a1-comparison-20261004-01/T1-1-3-A1.json).

## Verlorene und verdrängte Erfahrungen

Fünf unter A1 verlorene, unter U vorhandene Vorkommen entsprechen fünf kalten
Original-Offset-Linien: F3 bei31/55, F4 bei43, F7 bei31/55. Vier hätten den
richtigen tatsächlichen und modalen Nachfolger geliefert; keine war bereits warm.
Diese verlorenen Möglichkeiten dürfen nicht mit den sechs folgenden warmen
Bestandsverdrängungen gleichgesetzt werden.

Alle sechs Teilzulassungsopfer liegen in F8: Spuren1–4,9–12,17–20,25–28,33–36
und41–44 gehen bei22,30,38,46,54 beziehungsweise62 verloren. Jede besitzt für
Offset0 bereits Feedback und die Fehlerzelle mit Ec=0 und Ep=0,0078125. Offset1 ist jeweils kalt.
F8 zeigt dennoch keinen Prognosemehrfehler gegenüber U und keine verlorene warme
Abrufmöglichkeit an einem verglichenen Ziel. Bestandsverlust ist hier belegt,
ein daraus entstandener zusätzlicher Zielfehler nicht.
Beleg: [F8-Fallauswertung](../a1-comparison-20261004-01/F8-assessment.json),
`stages.A1.losses` mit `cause=PARTIAL_VICTIM`, und
[F8-A1-Arm](../a1-comparison-20261004-01/F8-A1.json), `partial_admissions`.

Über sämtliche Lebenszyklen gehen unter U38 und unter A125 warme Offset-Linien
verloren; dies umfasst auch reguläre Abschlüsse und ist kein direkter
paarweiser Nutzenvergleich. Sämtliche Verluste und Originalidentitäten stehen
in [lineages-and-losses.json](lineages-and-losses.json).

## Ressourcen, Bindungen und Prüfung

Worker4,355s von3.540s; Supervisor bis vor terminalem Schreiben5,964s von3.600s.
60s Abschlussreserve blieb verfügbar. Zusatzheap maximal7.158Byte von16.384;
konservative Originalframe-Obergrenze16 von18, kombiniert18 von20;
zwei Ausgabeslots,416Byte Bank,Receipt1.038Byte,UTF-8-Obergrenze2.076Byte.
Die nicht eingeschalteten Frame-Tracing-Zähler sind keine Nullbelegungsmessung.
Die unveränderte neutrale Tracequalifikation ergänzt diese konservativen Grenzen.

Vorbereitung2.859.611Byte von8MiB; Laufexport inklusive Abschluss6.996.620Byte.
Zusammen9.856.231Byte von64MiB einschließlich der vorgesehenen1MiB-Abschlussreserve.
Die genaue Zeitmessung endet wie vorgebunden vor dem terminalen Schreibvorgang.

Vorstart-SHA256:
`c5478f0a7fce810bda23ee045a02b21317d5178d4ee595c1f064327d08199705`.
Operative Autorisierung aus der Vorlage, einzig Status auf AUTHORIZED_ONCE gesetzt:
`e56284685cf21020dcd1561ca0f617723e71e275bc638dc45491d8b32d7e4239`.
Die Statusdatei bleibt als historischer Startbeleg unverändert; der vorhandene
Zielordner und dieser Abschluss dokumentieren den Verbrauch der Einmalfreigabe.

Laufabschluss-SHA256:
`85ef6239c3e3fc8e161284c9ffbe19ddbdcb06bc1201e73850f04862c807a769`.
[Versiegelter Laufabschluss](../a1-comparison-20261004-01/closure.json).
Alle149 darin verzeichneten Dateien wurden nach Abschluss auf Länge und SHA256
geprüft. Auswertung dieses Berichts liest ausschließlich das gespeicherte Archiv;
kein zusätzlicher Replay. [verification.json](verification.json) enthält die Bilanz.

## Interpretation und nächster sinnvoller Schritt

Beobachtet ist ein häufiger nutzbarer Feedback-/Wiederabrufzyklus in einigen F-Fällen,
aber kein vertragsgemäßer Mechanismus- oder Gesamtnutzenbeleg. A1 löst das
Erhaltungsproblem teilweise und erhält dabei auch irreführende Erfahrung.
Die erlaubte Schadensgrenze wird eingehalten, obwohl ein deutlicher Einzelschaden
auftritt. Dies bleibt ein Vergleich bekannter synthetischer Entwicklungsfälle;
kein unabhängiger Transfernachweis und keine allgemeine Memory-Behauptung.

Empfehlung an den Projektleiter: A1 nicht in den Standard übernehmen und den
negativen Primärbefund abnehmen. Als kleinster weiterer Erkenntnisschritt bietet
sich ausschließlich eine Archivdiagnose der Auswahl bei T1-1-3/Ziel17 gegenüber
den nützlichen und schädlichen F7-Abrufen an: Welche bereits vorhandene
Feedbackinformation macht eine konservierte Linie nützlich oder irreführend?
Daraus zunächst eine prüfbare Gegenprognose ableiten. Keine neue Regel, Variante,
Schwelle oder Wiederholung dieses Laufs ist damit beauftragt oder implementiert.
