# Vorbereitung des begrenzten Terminal-Bedienversuchs

Stand 2026-09-11. Nur Vorbereitung; keine Gateöffnung und kein Lauf.
Vorgesehene Lauf-ID: `caller-terminal-basic-20260911-01`.
Ergebnisziel: `reports/s2od/caller-terminal-basic-20260911-01`.
Die bekannte OB-Folge wird unverändert wiederverwendet, nicht als neuer
Bestand oder unabhängiger Robustheitsnachweis ausgegeben.

## Eingangs- und Bedienbindung

Die sieben Ereignisobjekte einschließlich IDs, Reihenfolge, Modalitätsfenstern,
Quellenpfaden und Payloadhashes stammen unverändert aus
`reports/s2ob/caller-input-binding/manifest.json`. Nur Lauf-ID und aktuelle
Codebindung samt Manifestdigest werden neu gebunden. Drei vorhandene Rohdateien:
`window.pcm`, `full.rgb`, `partial.rgb` unter `sources/s2ob/caller-av-basic`.
Keine Regeneration, keine Voranalyse. Hashbestätigung erfolgt später beim
jeweiligen qualifizierten Payloadzugriff, nicht in dieser Vorbereitung.

Bedienfolge, exakt 16 Kommandos:
`open`, `next`, `status`, `next`, `status`, `next`, `status`, `next`, `status`,
`next`, `status`, `next`, `status`, `next`, `status`, `close`.
Jedes Kommando wird einzeln vom Benutzer angefordert. Keine selbsttätige
Schleife über die Ereignisse, kein Überspringen und kein Wiederanlauf.

Umfang: eine Sitzung, sieben Ereignisse, vier Formationen, ein auditiver und
zwei visuelle Hinweise; fünf Audioanalysen/NJ-Projektionen, sechs visuelle
Analysen, 1.968 Feldkontakte und sechs Scanbelege. Geplante Lesemenge
37.420.800 Byte, Eingangsbestand 12.460.800 Byte. Tatsächlich hier gelesen: null.

Die drei Erwartungen bleiben unverändert: `input-basic-01` enthält sich mit
`ABSTAIN_NO_CONTEXT`; `input-basic-03` liefert `ADMIT_SINGLE_CONTEXT` aus
`A_RECENT`; `input-basic-07` enthält sich mit `ABSTAIN_INTERNAL_AMBIGUITY`.
Auch die vier Formationsprognosen werden unverändert referenziert. Kein B-Vorrang.
Die historische Evaluationsdatei bleibt unverändert, ihre alte Manifestbindung
ist Herkunft, nicht die neue operative Manifestbindung.

## Einziger vorgeschlagener autorisierter Startweg

Eine dateigebundene, versuchsspezifische Startfunktion im selben Python-Prozess
ist noch erforderlich. Vorgesehener Ort:
`reports/s2od/start_terminal_basic_once.py`, höchstens 4.096 Byte Quelltext.
Diese Datei ist **noch nicht implementiert oder qualifiziert**. Ihr Auftrag:

1. Fest gebundene neue Lauf-ID, Ausgabeabwesenheit, gemeinsame SHA-256-Bindung,
   aktuelle Client-/Basiscodes und separate Einmallauffreigabe prüfen.
2. Genau einen `TerminalClient(common_path, pin, inventory_path, output)` laden.
   Der Konstruktor prüft weiterhin OC- und Clientzulassung; kein `neutral=True`.
3. Nur unmittelbar für das Benutzerkommando `open` einmal `entry.MAIN_GATE=True`
   setzen und `client.command("open")` aufrufen. Im `finally` sofort wieder
   `False`; kein erneutes Setzen bei Fehler oder zweitem `open`.
4. Die restlichen gebundenen Kommandos ausschließlich auf Benutzereingabe an
   `client.command` weiterreichen und Rückgaben anzeigen. Abbruch/EOF schließen
   die vorhandene Sitzung, starten sie nicht neu. Abschließendes `finally`
   setzt das Gate zuverlässig `False`; keine zweite Publikation.
5. Der Client allein ruft die unabhängige Verifikation einmal auf. Weder
   `run_bound_session_once.run` noch ein äußerer `verify_once` wird verwendet.

Es gibt keinen alternativen CLI-Gateschalter, keinen Inline-Ersatzstarter und
keine allgemeine Gatefreigabe. Die alte Einmallauffreigabe ist nicht übertragbar.
Die synthetischen 16/16 prüfen die Bedienhülle, nicht diese Startfunktion oder
das Zusammenspiel mit nativer Sitzung. Ein echter Start ist daher noch nicht
allein aufgrund der bestehenden Qualifikation ausführungsbereit.

## Anzeigeabgleich und Abschluss

Nach jeder Rückgabe bleibt nur ihr SHA-256 im begrenzten Aufruferzustand;
kein zweiter vollständiger Schrittbeleg. Verglichen wird nach Abschluss mit
den sieben gespeicherten `execution.rows[n].step`: die Felder
`perception_status`, `memory_status`, `context_status`, `hypothesis`, `error_codes`
und die Ordinal-/Gesamtzahl sind genau die Projektion von `render_step`.
Die gespeicherte Schrittprojektion und ihr Anzeigehash müssen mit der vom
Client zurückgegebenen Anzeige übereinstimmen. Das ist ein Anzeigevergleich,
keine neue Scanberechnung oder zweite technische Verifikation.

Die sieben Hashes/Abgleichresultate gehören in die reservierte Auswertung,
nicht in eine zusätzliche vollständige Belegablage. Auswertung ausschließlich
nach `RECORDING_COMPLETE` und gespeicherten `evaluation_allowed=True`;
sonst Primärfehler/Phase/Fortschritt erhalten, keine fachliche Teilauswertung.
Auch dieser äußere Anzeige-/Erwartungsabgleich ist bislang nicht implementiert;
er gehört zur selben kleinen Startfunktion, nicht zu einer neuen Laufplattform.

## Bilanz und Freigabegrenze

`terminal-basic-preparation/budget.json` enthält sämtliche acht Präfixpositionen
und beide Abschlussalternativen auf Grundlage des bestehenden Ledgers.
Clientdateien, aktive Qualifikationsbelege, historische Eingangs-/Erwartungsbindung,
Vorbereitung und notwendige Referenzinhalte werden mitgezählt. Quellenbytes sind
separater Eingangsbestand, kein Systemausgabe-Artefakt.
Zusätzlich reserviert: 4.096 Byte für den noch fehlenden Starter, 8.192 Byte
für die Budgetdatei; bestehende Abschluss-/Auswertungsreserven bleiben erhalten.
Diese Reserven ersetzen weder verfügbaren Quelltext noch dessen Hash/Prüfung.

`common.json` bindet den vorhandenen Anschluss vollständig, ist jedoch bis zur
konkreten Starter-/Abgleichbindung **kein endgültiger Hauptlaufbeleg**. Nach deren
expliziter Freigabe müssen tatsächlicher Codehash und Dateigröße innerhalb der
Reserve ergänzt und die finale gemeinsame Bindung vorgelegt werden.
Keine neue Quellen-, Memory- oder Rezeptorqualifikation wird dadurch behauptet.
