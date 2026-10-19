# ZW1: unabhängiger Audit der vorhandenen mechanistischen Zeugen

2026-10-18 · Workflow 0f057ea1-94b9-496c-a771-0987161a1186.
Status: PASS für sämtliche 32 Bedingungsarchive und beide Arme.
Keine Policy-Ausführung, keine neuen Forschungsquellen, keine Bootstrapziehung,
keine Regeländerung und keine weitere Forschungsserie.

## Ergebnis und Nenner

Die vollständige erwartete Zeugenmenge wurde unabhängig aus den archivierten
Zustands-, Vorhersage- und Feedbackdaten enumeriert und als Multimenge mit den
archivierten Zeugen verglichen. Alle 32 Vergleiche stimmen exakt überein:
keine fehlenden, unbelegten oder exakt duplizierten Zeugendatensätze.
Die unveränderten ursprünglichen Mechanismenzähler stimmen ebenfalls überein.

| Gruppe | Erhaltungsereignisse | warme Ereigniszuordnungen | eindeutige warme Ziele | lokale Gewinnziele | lokale Schadensziele | gleiche Fehler |
|---|---:|---:|---:|---:|---:|---:|
| A/E | 102 | 206 | 206 | 91 | 28 | 87 |
| A/F | 179 | 174 | 174 | 78 | 31 | 65 |
| B/E | 56 | 123 | 123 | 69 | 20 | 34 |
| B/F | 137 | 243 | 243 | 138 | 44 | 61 |

Je Gruppe: 16 Geschichten mit je 511 beobachtbaren Zielen, somit **8176 Ziele**;
4096 Viererblockenden als zeitlicher Bezugsumfang. Die Zahl tatsächlich geeigneter
Konkurrenzgelegenheiten ist damit nicht gleichgesetzt. Erhaltungsereignisse sind
Ereignisse, keine Zielpositionen; aus ihrem Quotienten wird keine Erfolgsrate abgeleitet.

Eindeutige warme Ziele werden als (Paar, Bedingung, Arm, Zielposition) gezählt.
Innerhalb jeder Gruppe gibt es null Mehrfachzuordnungen. Deshalb stimmen hier warme
Ereigniszuordnungen und eindeutige warme Ziele numerisch überein. Die Prüfung und
Zählung unterscheiden diese Größen dennoch ausdrücklich. E- und F-Mengen dürfen
nicht zu einer vermeintlich eindeutigen bedingungsweisen Zielmenge addiert werden;
eine mögliche armübergreifende Überlappung wird hier nicht als Vereinigungszahl ausgewertet.

Lokaler Gewinn bedeutet keeper_error < other_error am selben Ziel, lokaler Schaden
keeper_error > other_error. Es handelt sich um den realisierten Fehlervergleich der
zwei vorhandenen Arme, nicht um den kausal isolierten Schaden einer einzelnen
Erhaltungsoperation. F-Gewinne sind aus Sicht von F definiert; die Richtung darf
nicht stillschweigend als E-Gewinn gelesen werden. Gleichstände sind separat erfasst.

Fehlersummen nur über eindeutige warme Ziele, ohne Mehrfachzählung:
A/E Gewinn 22,75 / Schaden 7,00; A/F 19,50 / 7,75;
B/E 17,25 / 5,00; B/F 34,50 / 11,00.
Dies sind keine vollständigen A/B-Kostenbilanzen und keine Zerlegung des Primäreffekts.

## Unabhängigkeit und eng begrenzte Anpassung

Der semantische Kern audits/er1-v2-witness-20261018/checker_qualified.py wird
unverändert direkt verwendet, SHA256:
`4ea7148b1bcc581c00e039c05b229760753a5a35a19c2afe55f6c712dd41c518`.
Seine zwölf bereits bestandenen neutralen Prüfungen wurden per Liefer- und
Abhängigkeitsbindung übernommen und nicht erneut ausgeführt.

Neu: audits/zw1-witness-20261018/adapter.py, test_adapter.py und run.py.
Der Adapter prüft ausschließlich ZW1-Quellenformat, Archivrevision und Zuordnung;
zusätzlich enthält er die beauftragte deskriptive Gewinn-/Schadenszählung.
Die semantischen Erhaltungs- und Warmnutzungskriterien wurden nicht geändert.

Der unveränderte Kern bestätigt Originalidentität und Quellwerte, lückenlose
Originalkontinuität, letzte Wiederbeobachtung, ungleiche Zwischenblöcke,
Konkurrenzpromotion beim verlierenden Gegenarm und dessen Gegenopfer.
Er prüft früheres gültiges Feedback desselben Originals und Offsets vor der
Konkurrenz und vor der späteren Auswahl, einschließlich lückenloser
Kandidat-zu-Retained-Promotion. Tatsächliche warme Auswahl, Fehlerzelle, ausgegebener
Originalwert und Fehler werden aus Bank, Receipt, Ausgabe und Quellziel bestätigt.
Alle Kandidaten werden enumeriert; erst danach erfolgt der Vergleich mit den
berichteten Zeugen. Die berichteten Zeugen steuern die Kandidatensuche nicht.

Produktive Zeugenfunktion, Observer und Policy-Engine wurden nicht importiert.
Die Modulprüfung bestätigt dies nach dem Lauf. Archivierte Observerdaten werden
nicht als Beweisgrundlage verwendet. Der bestehende begrenzte Delta-Decoder wird
als Formatkomponente übernommen; das ist keine zweite Implementierung des Codecs.

## Quellenbindung und Zuordnung

Ausgangspunkt ist die unveränderte ZW1-Forschungslieferung mit SHA256:
`bad2f49c9f46a5e743767c0ee37091ddde7e254d6b5063050ae1c941965c2731`.
Alle 155 Lieferdateien sowie Vorstart-/Berechtigungs-/Verbrauchsbelege wurden geprüft.
Quellennamensraum bleibt MCM-ZW1/source/v1. Die gespeicherten Quellen werden nur
gelesen und über Katalog/Indizes in Frames aufgelöst; keine Quelle wird nachgeneriert.

Für Fall n gilt Paar (n+1)//2, A bei ungeradem n, B bei geradem n.
Manifestpaar, Bedingung, Quellpfad, SHA, Fallzusammenfassung, Orientierung und
Paarquittung müssen übereinstimmen. Revision muss ZW1_V1 sein, neutral_only=false.
Die archivierten 1024 Quellframes müssen exakt zur gebundenen Quellendatei passen.
Zusätzlich stimmen die unabhängig aus Ausgaben bestimmten 511 Fehler pro Arm
mit der jeweiligen Bedingung der Paarquittung überein.

bindings.json enthält 358 Bindungen einschließlich neuer Prüferdateien,
unverändertem ER1-Prüfkern, dessen Qualifikation, Decoder, Laufzeitkomponenten,
Quellen und Forschungsbelegen. Alle Bindungen wurden nach dem Audit erneut geprüft.
verification.json bestätigt zusätzlich die weiterhin gültige ZW1-Vorstartbindung
mit 2995 Dateien und 98 Qualifikationsartefakten sowie die historischen Lieferungen.

## Neue neutrale Prüfungen

12/12 bestanden, IDs und Ergebnisse in tests.json/tests.log:
positiver Zuordnungsfall; vertauschte Bedingung im Manifest; überkreuztes Paar;
überkreuzte Fallzusammenfassung; vertauschte Bedingung in der Paarquittung;
überkreuzte Paarquittung; falscher Quellpfad; falscher Quellhash; falsche Quellframes;
falsche Archivrevision; Gewinn-/Schadenszählung mit absichtlicher Mehrfachzuordnung;
Ablehnung widersprüchlicher Fehlerwerte am selben Ziel.
Die Fixtures sind ausschließlich künstliche In-Memory-Daten, keine neuen
Forschungsquellen und keine Policyfälle. Kein Anlass zur Wiederholung der zwölf
unveränderten ER1-Semantiktests entstand.

## Konkrete belegte Wege und deskriptive Einordnung

Beispiele sind jeweils die erste enumerierte Instanz ihres Typs, keine Auswahlbasis
für die Zähler. Die Fallberichte enthalten Beispiele aller dort vorhandenen Typen,
die vollständigen Differenzlisten und einen Digest der gesamten erwarteten Multimenge.

Paar 1/A, E-Gewinn: Ursprung 621–624, letzte Beobachtung 664, ungleiche Blöcke
668/672, Konkurrenz 676, vorheriges Feedback 627/659/663, warme Auswahl Ziel 683,
Offset 0; E-Fehler 0, F-Fehler 0,25. E bewahrt das Original, F verliert es;
E verdrängt dabei das neuere Original 637–640.

Paar 1/A, E-Schaden: Ursprung 813–816, Wiederbeobachtung 832, Zwischenblock 836,
Konkurrenz 840, früheres Feedback 819/831, warme Auswahl Ziel 847;
E-Fehler 0,5 gegenüber F 0,25. Die belegte Erhaltung garantiert also keinen Gewinn.
Paar 1/A, F-Gewinn: Ursprung 257–260, Konkurrenz 324, Ziel 339;
F-Fehler 0 gegenüber E 0,25. Nützliche Erhaltung ist beidseitig belegt.

Paar 1/B, E-Gewinn: Ursprung 37–40, Wiederbeobachtung 164, Zwischenblöcke 168/172,
Konkurrenz 176, warme Auswahl Ziel 211; E-Fehler 0 gegenüber F 0,25.
Paar 1/B, F: dasselbe bewahrte Original 349–352 mit Wiederbeobachtung 360,
Zwischenblöcken 364/368, Konkurrenz 372 und früherem Feedback 359 liefert
an Ziel 375 einen Gewinn (0 gegenüber 0,25), an Ziel 391 einen Schaden
(0,5 gegenüber 0,25). Auch hier kann dieselbe bestätigte Erhaltung nützen oder schaden.

In A hat F mehr Erhaltungsereignisse als E (179 gegenüber 102), E aber mehr
warme Nutzungsziele (206 gegenüber 174). In B hat F mehr warme Nutzungsziele
(243 gegenüber 123) und mehr lokale Gewinnziele (138 gegenüber 69).
Diese Muster sind mit unterschiedlichen Erhaltungs-/Verdrängungswegen vereinbar,
erklären die gerichtete Interaktion aber nicht allein. Ereignishäufigkeit,
spätere tatsächliche Auswahl und realisierte Fehlerwirkung sind verschiedene Größen.
In allen vier Gruppen sind sowohl Gewinne als auch Schäden und Gleichstände belegt.

Offen bleibt, welcher Anteil des Primäreffekts kausal auf Auffrischung, Promotion,
Verdrängung oder andere durch das Quellengesetz veränderte Verlaufseigenschaften
zurückgeht. Die Zeugen sind keine randomisierte mechanistische Intervention und
keine disjunkte vollständige Zerlegung aller Fehlerziele. Keine neuen Signifikanztests,
keine neue Bootstrapziehung und keine Behauptung eines isolierten Ursachennachweises.

## Ressourcen und Erhaltung

32 Archive einzeln in einem Prüfprozess, danach jeweils Referenzen freigegeben.
Laufzeit 148.667562 s, Job-/Prozesspeak 48709632 Bytes
(46.45 MiB), harte Grenze 512 MiB.
Die generische Job-Snapshot-Beschriftung nennt einen Supervisor/Worker; tatsächlich
startet dieser Prüfeinstieg keinen Unterprozess. Exitcode 0, kein aktiver Teilfall,
keine Partialdateien. 54000 s Arbeitsgrenze, 57600 s Gesamtgrenze,
2 MiB Berichtsgesamtbudget, 1 MiB je Abschlussdatei und 64 MiB Exportgrenze bleiben
unverändert; der Decoder erzwingt seine bisherigen Größen- und Strukturgrenzen.

ZW1-Forschungslieferung (155 Dateien), ER1-v2-Forschung (139), historischer
ER1-v1-Abbruch (43) und qualifizierter ER1-Zeugenaudit (41) unverändert bestätigt.
ZW1 bleibt NEGATIVE_INTERACTION: -67/32704 mit 95%-Intervall
[-123/32704, -11/32704]. ER1 bleibt INCONCLUSIVE. Keine historischen Dateien geändert.
Die drei Projektübersichten erhalten ausschließlich eine neue Standseinordnung.

## Lieferung und Anschluss

case-01.json bis case-32.json enthalten Zuordnung, Quellen-/Archivhash,
erwartete und berichtete Zähler, Differenzen, Mehrfachzuordnungen, Beispiele und
Decoderressourcen. totals.json hält die vier getrennten Gruppen fest;
result.json/terminal.json den Prozessabschluss; verification.json den abschließenden
Erhaltungs- und Mengenabgleich. delivery-manifest.json bindet diese Lieferung und
die drei neuen Prüferdateien.

Der abgegrenzte Audit ist abgeschlossen. Nächster Schritt beim Projektleiter:
die bestätigten beidseitigen Erhaltungs-, Nutzungs- und Schadenswege deskriptiv
bewerten und entscheiden, ob daraus eine neue falsifizierbare mechanistische
Gegenprognose folgt. Höhere Zeugenzahlen allein rechtfertigen keine Regeländerung
oder Wiederholung. Eine weitere Forschungsserie ist nicht beauftragt.
