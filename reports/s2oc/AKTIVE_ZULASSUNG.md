# S2-OC: Aktive Sitzungszulassung v1

Die Nachweispflicht wird prospektiv geändert, nicht das historische Ergebnis.
Der Anschluss heißt `s2oc.active-admission.v1`; die gezielte Qualifikation heißt
`s2oc-admission-qualification-20260910-01`. Historischer OC-Code, OB-`run_once`,
Feld, Memory, Profile, Regeln und die 29/29 bleiben unverändert.

## Zulassung statt Archivwiederholung

Einmal bei Ausstellung wird das vollständige bestehende OC-Paket unabhängig
auf Byteintegrität, Klassen und Rekonstruktion geprüft. Ergebnis, ursprüngliche
Prüfinventarbindung und unveränderter OC-/OB-Softwarestand werden abgeglichen.
Auch die OB-Qualifikationskette wird dabei gelesen. Keine Tests, Wahrnehmungen
oder Owner werden wiederholt oder geöffnet.

Der neue Zulassungsbeleg enthält das historische Ergebnis, alle 29 Prüfnamen,
Profil, Konfiguration, Schemata, vollständige aktuelle Inventarbindung und
Archivherkunft mit gespeicherter/entpackter Größe. Der neue Anschlussstand wird
separat im vollständigen Inventar geführt: Die historischen Prüfungen werden
nicht als Qualifikation dieses Deltas ausgegeben. Dafür ist der neue gezielte
Aufruf erforderlich; reale Sitzungen bleiben bis zur separaten Freigabe gesperrt.

Beim Öffnen bindet der Aufrufer ausdrücklich den SHA-256 der Zulassung. Geprüft
werden dieser Pin, interne Digests, das vollständige Inventar gegen installierte
Dateien und Umgebung, Profil und Prüfdeckung. Ein aus derselben untrusted Datei
übernommener Pin ist kein Vertrauensanker. Die Bindung schützt nicht gegen einen
Akteur, der sowohl Freigabe-Pin als auch Belege und installierten Code ersetzt.

Nur `admission.json` und `inventory.json` sind aktive Qualifikationsdateien.
Das Archiv bleibt vollständig verfügbar, wird beim Sitzungsstart aber nicht
erneut gelesen. Ein Archivdigest allein ist keine Zulassung. Die Abschlussprüfung
verwendet die bestehende unabhängige OB-Verifikation der Zustände und Transaktionen,
nicht deren historischen dateilesenden Haupteinstieg. Dessen interner konservativer
Budgetcheck bleibt unverändert; die zusätzliche vollständige Sitzungsbilanz ist
maßgeblich und zählt keine fiktive neue Qualifikationsdatei.

## Eine gemeinsame Obergrenze

Für E Ereignisse, F Formationen und a/v Hinweise gelten unverändert die nativen
Obergrenzen: Zustände `(F+1)*98304`, Eingänge/Schritte jeweils `E*16384`,
Scans `2*(a+v)*32767`, NJ `(F+a)*1024`, Formationen/Generationen jeweils `F*1536`.
Quelleninventar und Zulassung werden einmal mit tatsächlicher Größe gezählt.
Keine zusätzliche unbelegte 4-KiB-Qualifikationsreserve im Sitzungsledger.
Der Bericht behält 512 Byte, die gemeinsame Verifikation 262.144 Byte.

Die Vorbindung reserviert insgesamt die bestehende Metadatengrenze von 65.536
Byte, nicht einen weiteren Zuschlag auf schon gezählte Inhalte. Die Gesamthülle
ist die Summe manifestabhängiger nativer Maxima, vollständiger Quellenanhänge,
dieser Metadatenobergrenze und gemeinsamer Verifikation. Auch die gemeinsame
Zusatzhülle wird vor Initialisierung geprüft. Lokale Maxima setzen keine globale
Grenze außer Kraft.

Während der Sitzung werden die aktuellen vollständigen Erfolgsköpfe einschließlich
Anfang/Ende, Konfiguration, Herkunft und jüngster Rückgabereferenz kanonisch gezählt,
ohne `close()` aufzurufen. Der danach verbleibende Metadatenraum ist die maximale
gemeinsame Fehlerkapazität. Ein vollständiges Budgetdiagnostikum plus Phase,
manifestgebundener Quellen-ID, Fortschritt und Endsnapshot muss darin passen.
Es wird kein historischer 16-KiB-Pauschalwert übernommen.

Andere tatsächliche Fehlerfelder werden vor Veröffentlichung vollständig geprüft.
Für beliebig große fremde Exception-Codes ist keine universelle Passgarantie
behauptet: Überschreitungen bleiben technische Grenzen, nicht Anlass zum Kürzen.
Erfolgs- und Fehlerhülle teilen dieselbe Obergrenze. Präfixschritte stehen bei
Fehlabschluss anstelle einer vollständigen Erfolgskette. Archivgrößen zählen
separat, nicht nochmals als aktive Sitzungsdateien. Lauf-JSON bleibt unkomprimiert.

## Genau ein gezielter neutraler Aufruf

16 unabhängige Prüfgruppen stehen in der neuen Testdatei. Zwei CALLER-Sitzungen
mit neu erstellten neutralen PCM/RGB-Dateien: eine AV/A-Folge und ein Abbruch
vor dem zweiten Ereignis nach abgeschlossener AV-Formation. Insgesamt vorgesehen:
3 Audioanalysen, 3 NJ-Projektionen, 2 visuelle Analysen und 2 Abschlussprüfungen.
Keine historische Testwiederholung, kein Stapelreplay und keine realen Aufruferdaten.

Die erste Sitzung sperrt Zugriffe auf beide historischen Qualifikationsverzeichnisse
während Öffnen, Verarbeitung und Prüfung. Separate Kontrollen sichern fehlende,
veränderte, software-/profilfremde Zulassungen und unvollständige Prüfdeckung vor
Payload- und Runtimezugriff ab. Weitere Gruppen prüfen tatsächliche CALLER-Zähler,
unbelegte Reserven, einzelne und vollständige Verletzungsmengen, Manifestmaxima,
erhaltenen Fortschritt beim Fehler und gemeinsame Verifikationsgrenze.

Vor dem Aufruf: vier neue Dateien vollständig im Inventar, 16 Prüfnamen in der
Vorregistrierung, gesamte native Maximalhülle für zwei kurze Sitzungen plus
65.536 Byte gemeinsame Metadaten, Inventar und 262.144 Byte gemeinsame Verifikation.
Die Qualifikationsdateien teilen unverändert 4.096 Byte innerhalb der Metadaten;
512 Byte Bericht bleiben darin reserviert. Rohfixtures sind temporäre, separat
ausgewiesene Eingänge. Keine Pflichtdatei verschwindet durch eine Referenz.

Nach dem Aufruf werden alle tatsächlichen Dateien gemeinsam gezählt. Vollständige
Fehlerlogs bleiben auch bei Überschreitung erhalten. Kein Retry. Die endgültige
Bewertung verlangt alle 16 Gruppen, unveränderte Quellhashes und passende Istbilanz.
Gates anschließend False; ME/MI gesperrt, Prognosezweig ruhend.
