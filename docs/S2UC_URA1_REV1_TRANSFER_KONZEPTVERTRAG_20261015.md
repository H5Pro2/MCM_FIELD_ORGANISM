# URA1-REV1: einmalige Kontingenzumkehr bei unverändertem U/R

Stand 2026-10-15. KONZEPT_ZUR_ABNAHME, keine Laufnummer und keine Ausführungsfreigabe. Fortsetzung des Transfer-Konzeptauftrags nach URA1-V4. Erstellt durch statische Code-/Vertragslektüre; keine Quellen erzeugt, keine Policies ausgeführt, keine neuen Messungen berechnet. Die V4-Einmalfreigabe bleibt verbraucht.

## 1 Frage und falsifizierbare Gegenprognose

Bleibt die fehlerbasierte Auswahl U gegenüber Originalrecency R im frühen Fenster nach einer einmaligen Umkehr der Hinweis-Fortsetzungs-Beziehung hilfreich? Genau ein gepaarter U/R-Vergleich; keine zusätzlichen Arme, stationären Kontrollgeschichten, Parameteroptimierungen oder nachträglichen Quellenvarianten.

Gegenprognose: Im vorab festen frühen Nachwechselfenster ist die mittlere MAE von U größer als die von R. Vor dem Wechsel erworbene Bewertungen können die erste Auswahl danach noch beeinflussen; ein inzwischen verfügbares neueres Original kann für R günstiger sein. Diese Möglichkeit ist keine garantierte Anpassungsverzögerung durch EMA. Insbesondere bedeutet Originalrecency nicht „zuletzt beobachtete Fortsetzung“ und garantiert keinen schnellen Wechsel. Der neue Verlauf muss erst als berechtigtes Original verfügbar sein. Der primäre Kontrast kann diese Gegenprognose unterstützen, ihr widersprechen oder unentschieden bleiben.

V4 belegt einen U-Vorteil in seiner stationären Quellenfamilie, zugleich Nachteile bei kalten und Ein-Kandidaten-Zielen. Das ist Motivation, kein vorweggenommener Transferbefund und keine historische Kontrollgruppe [B1].

## 2 Festes Quellenrezept

32 neue Geschichten r=1…32, je 1024 Frames = 256 Blöcke. Jede Geschichte beginnt mit frischen Armen; innerhalb einer Geschichte läuft der Zustand ohne Unterbrechung weiter. Kein zusätzliches Aufnahmepräfix. Katalog wie V4: V(x)[j]=x+j/4096 für j=0…47; X=V(1/8), Y=V(7/8), P=V(1/2), A=V(1/4), B=V(3/4), S=V(1/16). Jeder Block b enthält (X oder Y, P, A oder B, S). Q-Ziel ist Frame 4b−1, vorhergesagt nach Frame 4b−2. Alle übrigen regulären Vorhersagen und Rückmeldungen bleiben erhalten.

Zwei Phasen p=0,1 mit je 128 Blöcken. In jeder Phase zunächst eine Liste aus 64 A und 64 B mischen. Danach die aufsteigend gesammelten A-Positionen und B-Positionen jeweils unabhängig mischen. Die jeweils ersten nA bzw. nB Positionen bekommen X, alle übrigen Y:

| Geschichten | Phase 0: nA/nB | Phase 1: nA/nB |
| --- | --- | --- |
| ungerades r | 48/16 | 16/48 |
| gerades r | 16/48 | 48/16 |

Damit je Phase 64 X, 64 Y, 64 A, 64 B. Die empirische bedingte Häufigkeit von A bei X kehrt sich 3/4↔1/4 um, bei Y spiegelbildlich; die Randhäufigkeiten bleiben konstant. Das sind feste Gesamtzahlen mit Ziehen ohne Zurücklegen, keine unabhängigen Bernoulli-Versuche je Block. Die beiden Phasen werden unabhängig gemischt, nicht kopiert oder zeitlich gespiegelt. Das Halbieren der Bestandszahlen gegenüber V4 ist Bestandteil dieses neuen Rezeptes; V4 wird nicht als kausale Kontrollbedingung verwendet.

Deterministisches Mischen analog [B2]: drei getrennte Streams `continuation`, `dependent-A`, `dependent-B` je r,p. Schlüssel exakt `MCM-URA1-REV1/source/v1/r={r}/phase={p}/stream={name}/draw={cursor}`; Dezimalzahlen ohne führende Nullen, cursor beginnt je Stream bei 0. SHA-256 des UTF-8-Schlüssels; erste acht Digestbytes als unsigned Big-Endian-u64. Für Ziehung unter n nur u < 2^64−(2^64 mod n) akzeptieren, Ergebnis u mod n; auch verworfene Ziehungen erhöhen cursor. Absteigendes Fisher-Yates, i=L−1…1, Tausch mit Ziehung unter i+1. Höchstens 4096 Ziehungen je Stream, sonst technischer Abbruch ohne Ersatzseed. Phasenlisten in Reihenfolge 0,1 aneinanderhängen. Katalog-/Block-IDs nur im externen Quellenerzeuger; Arme bekommen die bisherigen numerischen Frames mit regulären Herkunftsdaten.

Einziger Wechsel: nach Block 128 / Frame 512. Frame 513 beginnt die neue Kontingenz; erstes betroffenes Q-Ziel ist Frame 515 (b=129). Kein zusätzlicher Trenner, Reset, Phasenbit, Zeitplan, Wahrscheinlichkeitswert oder Wechselhinweis an U/R. Die feste Position ist ausschließlich Versuchsmetadatum. Kein Arm darf daraus einen neuen Entscheidungszweig erhalten.

## 3 Unveränderte Verfahren und Informationszugang

U bleibt `MultiErrorAdapter`: eindeutiges negatives Minimum EC−EP unter warmen berechtigten Hypothesen; sonst Persistenz, auch bei Gleichstand. R bleibt `OriginalRecencyAdapter`: größte Originalordinalzahl unter berechtigten Nachfolgern; Gleichstand über (role,generation,offset), Persistenz nur ohne berechtigten Kontext [B3,B4]. Beide behalten dieselben Fehlerzellen und dieselbe Rückmeldung auch für nicht gewählte berechtigte Hypothesen. R verwendet deren Werte nicht zur Auswahl.

Aufnahme, Bestätigung, Promotion, Verdrängung, Abruf, Ticketprüfung und Originalnachfolger sind unverändert. Promotion erhält vorhandene Fehlerpaare, reguläres Verdrängen darf Zellen entfernen; „fortlaufend“ verlangt keinen künstlichen Erhalt bereits verdrängter Zellen. Kein Löschen, Aufwärmen oder Nachbewerten am Wechsel [B4].

Pro Geschichte identische Eingaben und identischer zugänglicher Spurenbestand beider Arme, keine zwischen Geschichten geteilte Memory. Der spätere technische Nachweis muss vor jeder Auswahl Bestands-/Herkunfts-/Hypothesengleichheit und anschließend Ticket-/Zellgleichheit nach bestehendem Referenzverfahren prüfen. Vorhersagewahl darf nicht auf die Quellen oder den Bestand zurückwirken. Eine Verletzung ist ein technischer Abbruch, kein auszuschließendes ungünstiges Ziel. Diese Invarianten sind Vertragsbedingungen; ihre Erfüllung für die neue Quelle ist noch nicht gemessen.

## 4 Statische Unterscheidbarkeit und Grenze der EMA-Erklärung

Für Q gilt bei A/B-Originalen: ep=1/4, ec entweder 0 oder 1/2. Eine bereits warme, fortlaufend gültige Zelle hat EP=1/4. Nach A-Feedback gilt EC_A'=EC_A/2 ≤1/4 und EC_B'=EC_B/2+1/4 ≥1/4; nach B spiegelbildlich. Daher kann eine rückgemeldete alte Gegenhypothese nicht allein wegen EMA noch mehrere passende Rückmeldungen lang negativ besser bleiben. Initialisierung, fehlende Berechtigung und Gleichstände müssen getrennt betrachtet werden. Auch binary64 rechtfertigt hier keine pauschale lange Trägheit [B5].

Der frühere gestoppte binäre U/L-Vergleich änderte ausschließlich EMA gegen letztes Fehlerpaar bei gleicher fehlerbasierter Auswahl. Sein festes Präfix und sein beständiger Zweihypothesenbestand führten zu regulärer Vorhersageäquivalenz. Der spätere ULZ1-Vergleich ergänzte eine dritte Fortsetzung; auch er verglich U mit einer fehlerbasierten Letztfehlerregel. R dagegen ordnet verfügbare Originale nach Originalzeit und ignoriert Fehlerwerte vollständig [B6]. Der U/L-Äquivalenzbeweis ist deshalb kein U/R-Äquivalenzbeweis.

Ein statisches Entscheidungsbeispiel: einzige berechtigte warme A-Spur, EC=1/2 und EP=1/4 nach B-Feedback. U gibt P aus, R A. Am nächsten A-Ziel hat R den kleineren Fehler (0 statt 1/4), am nächsten B-Ziel U (1/4 statt 1/2). Ebenso unterscheiden sich U=P und R=A bei einer einzigen kalten A-Spur. Das folgt direkt aus den Auswahlregeln und benötigt weder Rundungsartefakte noch einen zweiten Armparameter. Es ist ein zulässiges lokales Zustandsbeispiel, kein Nachweis, dass gerade diese Konstellation im festgelegten Nachwechselfenster auftreten wird.

V4 dokumentiert zudem tatsächlich verschiedene Ausgaben an 3524 Q-Zielen, darunter 1335 Wahlen verschiedener Kontexte [B1]. Allgemeine strukturelle U/R-Äquivalenz liegt somit nicht vor. Häufigkeit und Richtung der Unterschiede nach dieser konkreten Umkehr bleiben offen. Eine These „R reagiert sicher schneller, weil U glättet“ wird verworfen. Tragfähig bleibt die engere Gegenprognose zur vollständigen Auswahlregel unter fortlaufendem Bestand. Würde eine spätere statische Prüfung für genau diese Quellenklasse dennoch vollständige Vorhersageäquivalenz beweisen, STOPP dieses Vergleichs vor Materialisierung; keine Ersatzquelle ohne neuen Konzeptentscheid.

## 5 Ein Primärkontrast und Entscheidung

Primärfenster ausschließlich Q der Blöcke 129…160 (32 Ziele je Geschichte, 1024 insgesamt). Für jedes Ziel e=MAE48(U,target)−MAE48(R,target); D_r ist dessen Mittel über die 32 Ziele. Einziger primärer Schätzer D=(1/32)ΣD_r. Positiv bedeutet R-Vorteil. Einheit der Unsicherheit ist die vollständige Geschichte, niemals einzelne Frames oder Ziele.

Nominales zweiseitiges 95%-Perzentilintervall durch 10000 Bootstrapziehungen von je 16 Geschichten mit Zurücklegen innerhalb jeder der beiden Orientierungen; dann gleichgewichtetes Mittel aller 32 gezogenen D_r. Unveränderte URA1-Bootstrapindexmatrix und Quantilregel h=(10000−1)q, lineare Interpolation für q=0,025 und 0,975 [B7]. Matrix-SHA-256: `0b9fbf483e870adac01ded7d2d0d0a651a11474a4ac2e4fbae1c14e793d7d965`. Keine neue Seedwahl. Exakte Auswertung gespeicherter binary64-Werte wie bisher; neue Fenstermaske bedarf später einer unabhängigen Prüfung.

- Untere Intervallgrenze >0: früher R-Vorteil unterstützt; U bleibt in diesem Fenster nicht überlegen.
- Obere Intervallgrenze <0: U bleibt im definierten frühen Fenster hilfreich; die Gegenprognose eines mittleren R-Vorteils wird nicht gestützt.
- Intervall enthält oder berührt 0: unentschieden, kein Gleichwertigkeitsnachweis.
- Fehlende Geschichte, fehlendes Ziel oder Integritätsfehler: kein konfirmatorisches Urteil aus einer Teilserie; kein automatischer Ersatz/Retry.

Alle Ziele des Primärfensters zählen einschließlich erster Wechselprognose, kalter Zustände, keinem/einem Kandidaten, Persistenz und schädlicher Ausgaben. Keine Mindestzahl warmer Zellen, kein Ausschluss aufgrund der beobachteten Wirkung. Keine zusätzliche primäre Vorher-Nachher-Differenz und kein primärer X/Y-Teiltest.

Nur deskriptiv: Q97…128 (späte Vorphase, 32 Ziele), Q161…256 (späte Nachphase, 96), Q129…256 (gesamte Nachphase, 128), Q1…256 und bisherige G_all/S/Q_X/Q_Y. Zusätzlich im Primärfenster bisherige Bestands-/Warm-/Auswahlpartitionen, Zahl besser/schlechter/gleich, Gewinn- und Schadenssumme sowie maximaler Einzelzielschaden. Keine separaten Signifikanzurteile oder nachträglich verschobenen Fenster. Die letzte unbeobachtete Vorhersage auf Frame 1025 bleibt wie bisher zensiert; sie ist kein Q-Ziel.

## 6 Aussagegrenzen, Ressourcen und nächster Schritt

Ein positives Primärergebnis belegt nur einen mittleren frühen R-Vorteil dieser Quellenfamilie. „Vorübergehend“ im Sinn späterer Erholung ist durch den frühen Kontrast allein nicht bewiesen; die späte Phase liefert lediglich deskriptiven Kontext. Ohne stationäre zeitgleiche Kontrollbedingung ist auch kein isolierter kausaler Wechselkosteneffekt identifiziert. Keine Aussage über alle Umkehrstärken, mehrere Wechsel, allgemeine Intelligenz, feldinterne Memory oder reale Audio-/Video-Übertragung. U/R isoliert die Nutzung von Fehlererfahrung einschließlich Kontext/Persistenz-Wahl, nicht den Glättungsfaktor allein.

Ressourcenrahmen unverändert aus [B8]: höchstens 32 Geschichten/64 Arme, 1024 Frames je Geschichte; global 57600 s, Worker 54000 s, Abschlussreserve 3600 s; Job 512 MiB, höchstens zwei Prozesse. Vorbereitung 8 MiB, Quellen gesamt 2 MiB/je 32 KiB, Archive gesamt 32 MiB/je gzip 512 KiB, encoded und dictionary je 4 MiB, record 256 KiB, nodes 65536, edges 262144, indices 65536, collections 16; temporär und Gesamtexport einschließlich Vorbereitung je 64 MiB, Administration 2 MiB, Closure 1 MiB. Alle bisherigen Grenzprüfungen und terminalen Abbruch-/Cleanup-Regeln bleiben verbindlich. V4-Istdauer und Speicherverbrauch sind historische Orientierung, keine neue Laufzeitgarantie.

Unveränderte technische Nachweise zu U/R, Feedback, Promotion, Archivcodec, Bestandsreferenz, Dateibilanzierung und Terminalabschluss werden wiederverwendet und später über ihre bestehenden Bindungen referenziert. Keine erneute große Qualifikationsserie zur bloßen Bestätigung. Neu zu prüfen wären ausschließlich phasenbezogenes Quellenrezept samt unabhängiger Referenz, Fenstergrenzen/Denominatoren, Signalfreiheit und Integration der unveränderten Schutzmechanismen. Der bestehende V4-Erzeuger und dessen Zulassung dürfen dafür nicht umgedeutet oder überschrieben werden.

Empfohlener nächster Schritt: Projektleiter bewertet diesen Vertrag insbesondere unter der eingeschränkten mechanistischen Gegenprognose. Bei Abnahme ein getrennt begrenztes Implementierungs-/Neutralprüfpaket für Quelle und Fenster festlegen. Erst nach dessen Nachweis eigener gebundener Vorstart und gesonderte Einmalfreigabe. Dieser Auftrag endet mit dem Konzept; keine Implementierung oder Versuchsausführung daraus ableiten.

## Belegstellen

- B1: [URA1-V4-Abschluss, Quellen-/Vergleichsdefinition und Diagnosen](../reports/s2uc/ura1-comparison-v4-consistent16h/REPORT.md), insbesondere Zeilen 13–15 und 67–85.
- B2: [V4-Quellenrezept](../tools/_s2uc_ura1_v4_sources.py), `Stream.below`, `Stream.shuffle`, `generate`, Zeilen 27–62. REV1 ist eine hier spezifizierte Änderung des Quellenrezeptes, keine Änderung dieser Datei.
- B3: [R-Auswahl](../tools/_s2uc_ura1.py), `OriginalRecencyAdapter._receipt`, insbesondere Originalordinalvergleich und `selection_key`.
- B4: [U-Auswahl, Feedback und Lebenszyklus](../tools/_s2uc_multi_error.py), `_receipt` Zeilen 105–172, `consume_feedback` ab 179 und Promotion ab 268.
- B5: [Analytischer U/L-Stopp](../reports/s2uc/ul-analytic-precheck-20261004-01/REPORT.md), Abschnitte Herleitung, Initialisierung und binary64; [historischer Konzeptstatus](S2UC_BEWERTUNGSVERGLEICH_GLEICHES_BUDGET_KONZEPT_20261004.md), Zeilen 3–8.
- B6: [L-Code](../tools/_s2uc_ulz1_last.py), `LastErrorAdapter.consume_feedback`; [URA1-Ablationsvertrag](S2UC_URA1_AUSWAHLABLATION_KONZEPT_20261014.md), Abschnitte 1–2 mit ULZ1-Abgrenzung.
- B7: [Statistikbasis](../tools/_s2uc_ura1_v2_stats.py), `matrix_bytes`, `quantile`, `interval`, Zeilen 11–29. Bestehendes `aggregate` hat noch keine REV1-Fenster; seine unveränderte Verwendung wäre nicht hinreichend.
- B8: [Ressourcenvertrag im Code](../tools/_s2uc_ura1_v2_series.py), `LIMITS`, Zeilen 7–11; [V4-Integration](../tools/s2uc_ura1_prepare_v4.py), [Dateibilanzierung](../tools/_s2uc_ura1_fs_accounting_v4.py), [Terminalabschluss](../tools/_s2uc_ura1_terminal_v3.py).
