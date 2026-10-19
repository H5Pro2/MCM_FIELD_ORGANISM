# ER1-v2: unabhängige Prüfung der mechanistischen Zeugen

Workflow 37ca6eac-5bd2-4e67-9cd2-49c6c9c916d0, 2026-10-18.

## Ergebnis

PASS für alle 32 gespeicherten Forschungsarchive. Sämtliche gemeldeten Erhaltungs- und warmen Nutzungszeugen beider Arme sind durch einen separaten Prüfer aus Zustands-, Vorhersage- und Feedbackbelegen bestätigt. Kein fehlender, unbelegter oder exakt duplizierter Zeugendatensatz. Die vollständige erwartete Zeugenmenge wurde unabhängig enumeriert und als Multimenge mit der archivierten Meldung verglichen; es wurden nicht nur ausgewählte positive Beispiele geprüft.

| Getrennte Zählung | E | F |
|---|---:|---:|
| Erhaltungsereignisse | 171 | 343 |
| Ereignisbezogene warme Nutzungen | 327 | 320 |
| Ereignisbezogene lokale Gewinne | 141 | 166 |
| Eindeutige warme Zielpositionen (Geschichte, Ziel), je Arm | 327 | 320 |
| Eindeutige lokale Gewinnziele, je Arm | 141 | 166 |
| Innerhalb eines Arms mehrfach zugeordnete Zielpositionen | 0 | 0 |

Alle drei ursprünglichen Ereigniszähler stimmen exakt mit statistics.json überein. Ereignisse und Zielpositionen bleiben trotz hier gleicher Warmnutzungszahlen unterschiedliche Größen. E- und F-Zielmengen werden nicht zu einer vermeintlich eindeutigen Gesamtzielmenge addiert; ein armübergreifender Vereinigungszähler ist nicht Gegenstand dieser Tabelle. Der Primärnenner bleibt unverändert 16352.

## Unabhängiger Prüfweg

Implementierung: audits/er1-v2-witness-20261018/checker_qualified.py; Einstieg run_qualified.py; neutrale Qualifikation test_qualified.py. Die Dateien liegen außerhalb historisch gebundener Modulverzeichnisse. Vorhandene Forschung, Vertrag, Archive und Berichte bleiben unverändert.

Der Prüfer importiert weder _s2uc_er1_run_mechanisms noch _s2uc_er1_run_observer oder einen Policy-Engine-Pfad. Das wird zusätzlich anhand der geladenen Module kontrolliert. Er verwendet nicht den archivierten Observer als Wahrheit, sondern rekonstruiert:

1. Originalidentität und Werte anhand der Quellframes und sämtlicher gespeicherter Perception-Nachzustände, einschließlich Kandidaten-/Retained-Rollen und Generationen.
2. Retained-Verluste, neue Originale, Gegenopfer und Zwischenblöcke aus den Zustandsübergängen; eine Konkurrenzpromotion muss beim verlierenden Gegenarm belegt sein. Der bewahrende Arm kann bei bereits abweichendem Bestand nur bestätigen. Diese asymmetrischen Folgeeffekte sind in Abschnitt 4 des gebundenen Vertrags zugelassen.
3. Durchgehende Retained-Originallinie von der letzten Beobachtung über die Konkurrenz bis zur späteren Auswahl. Für früheres Feedback wird die vollständige Kandidaten-/Retained-Linie geprüft. Ein Generationenwechsel wird nur bei einer lückenlosen Kandidat-zu-Retained-Promotion an einer Blockgrenze akzeptiert; eine spätere Neuaufnahme oder ein Generationensprung im Retained-Bestand ersetzt diese Linie nicht.
4. Vorheriges tatsächlich als live protokolliertes Feedback desselben Origins und Offsets: vollständige Update-Schlüssel, eingefrorene Originalposition, vorhandene Feedbackzelle und gültiger Ursprung. Zeitpunkte müssen vor Konkurrenzpromotion und vor dem späteren Hinweis liegen. Feedback des aktuellen Ziels wird ausgeschlossen.
5. Tatsächlich ausgewählte Hypothese und warme Fehlerzelle aus Receipt und Bank, ausgegebenen Originalwert aus der Quelle und realisierte Fehler beider Arme aus den gespeicherten Ausgaben und Zielwerten.
6. Vollständigkeit, Multimengen-Gleichheit, exakte Duplikate und Mehrfachzuordnungen zu Zielen.

Der bestehende begrenzte Delta-Decoder wird als Formatkomponente wiederverwendet. Seine Mengen-, Größen- und Recordgrenzen bleiben aktiv. Die Authentizität der Archive beruht zusätzlich auf dem vorher geprüften und hier erneut SHA-geprüften Liefermanifest. Dies ist eine unabhängige semantische Zeugenprüfung, keine neue unabhängige Implementierung des Archivformats und keine erneute Policy-/Bootstrapausführung.

## Konkrete Bestätigungen

Geschichte 1, E: Ursprung [13,14,15,16], letzte Beobachtung 40, ungleicher Zwischenblock 44, Konkurrenz 48 und warme Auswahl an Ziel 51 mit Offset 0. Vorheriges gültiges Feedback [19,35,39] wird einschließlich des Kandidaten-Promotionsübergangs bestätigt; E-Fehler 0, F-Fehler 0,25.

Geschichte 1, F: Ursprung [21,22,23,24], Konkurrenz 48, Ziel 103, Offset 0, vorheriges Feedback [27,31]; F-Fehler 0, E-Fehler 0,25. Damit sind Nutzen und Gegenkosten verlorener Erfahrung beidseitig bestätigt.

Die jeweiligen case-01.json bis case-32.json enthalten Quellenhash, rekonstruierte und gemeldete Zähler, vollständige Differenzlisten (alle leer), Mehrfachzuordnungen, Decodergrößen und Laufzeit. verification.json bestätigt zudem die Übereinstimmung mit den ursprünglichen Statistikzählern.

## Neutrale Qualifikation und Entwicklungskorrekturen

12/12 Tests bestanden; vollständige Test-IDs stehen in tests.json und tests.log. Die Gegenbeispiele erfassen falsche Feedbackzeit, falschen Offset, unterbrochene Originallinie, fehlendes Gegenopfer, ausgelassenen Zeugen, Duplikate, Mehrfachzuordnung, legitime asymmetrische Promotion, legitimen Kandidaten-Generationswechsel und unzulässigen Retained-Generationssprung. Der positive Fall wird akzeptiert.

Zwei Entwicklungsstände bleiben als Belege erhalten; sie sind nicht das Abnahmeergebnis:

- er1-v2-witness-audit-20261018-01 verlangte fälschlich gleichzeitige Promotionen beider Arme. 32 Archive gelesen; 148,074 s, Jobpeak 49319936 Bytes. Die dadurch gemeldeten Abweichungen waren überstrenge Prüferbedingungen.
- er1-v2-witness-audit-20261018-02 verlangte noch eine unveränderte Generation über Kandidatenpromotionen. 27 Fallberichte gespeichert; beim Bericht zu Archiv 28 stoppte REPORT_BUDGET. Auch der normale Abschlussbericht passte nicht mehr ins Budget. Endzeit und finaler Peak dieses Entwicklungsstands sind deshalb nicht belegt; der harte 512-MiB-Job war aktiv. Die 2084618 gespeicherten Bytes blieben unter 2097152 Bytes. Dieser Stand ist unvollständig und nicht abgenommen.

Die erneute reine Archivprüfung war durch diese konkret nachgewiesenen Prüferfehler erforderlich. Die finale Fassung korrigiert beide Bedingungen, ergänzt Regressionen, speichert kompakte Differenzen und reserviert 16 KiB für den Terminalstatus. Kein Forschungsversuch wurde wiederholt. development-notes.json hält diese Grenzen ausdrücklich fest.

## Ressourcen und Herkunft

Finale Prüfung: 147,347 s, Jobpeak 48762880 Bytes (rund 46,50 MiB), harte Grenze 536870912 Bytes. Ein Prüfprozess; Archive nacheinander freigegeben, niemals als ganze Serie im Speicher gehalten. Die generische Windows-Snapshot-Beschriftung „supervisor and inherited worker“ beschreibt hier keinen zusätzlich gestarteten Worker: der Prüfeinstieg startet keinen Unterprozess.

Workergrenze 54000 s, Gesamtobergrenze 57600 s, Administration 2097152 Bytes, einzelne Abschlussdatei 1048576 Bytes und Exportgrenze 67108864 Bytes. Der Decoder erzwingt die bestehenden Archiv-/Datenstrukturgrenzen. Keine temporären Partialdateien. Der finale Terminalstatus und Exitcode bestätigen den abgeschlossenen Prozess.

bindings.json bindet 153 Dateien einschließlich Forschungs-Liefermanifest, Forschungsbelegen, Prüferfassungen, Decoder, Vertrag und Laufzeitumgebung. Sämtliche Bindungen wurden nach Auswertung nochmals geprüft. Die verbrauchte v2-Vorstartbindung bleibt unverändert; alle 2979 Dateien und 72 Qualifikationsbelege bestehen den tatsächlichen Validator. Zusätzlich bleiben 2967 historische v1-Dateibindungen, 43 Qualifikationsbelege und 43 Abbruchbelege unverändert.

Keine Policy-Ausführung, keine neuen Quellen, keine Bootstrapziehung, keine Regeländerung. Alle historischen Berichte und Primärdaten bleiben unverändert. Die drei Projektübersichten erhalten lediglich eine neue Standseinordnung.

## Aussagegrenze und Anschluss

Die beidseitigen mechanistischen Zeugen sind jetzt unabhängig bestätigt. Daraus folgt weiterhin kein globaler Vorteil von E: Der unveränderte Primärvergleich bleibt INCONCLUSIVE, mit Mittelwert −45/65408 und 95%-Intervall [−89/65408; 1/16352]. Lokale Erhaltung und nützliche Wiederverwendung sind belegt; die stärkere globale Behauptung ist nicht belegt.

Keine offenen technischen Hindernisse. Anschlussvorschlag: Projektleiter nimmt die unabhängige Zeugenprüfung ab und bewertet die bereits vorhandene beidseitige Kostenbilanz auf eine neue falsifizierbare Gegenprognose. Keine erneute Serie oder Parameteranpassung ohne einen gesonderten Auftrag.
