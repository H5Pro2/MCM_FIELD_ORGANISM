# Starter: Vorabstopp vor Anschlussqualifikation

Stand 2026-09-11, Bezugscommit
`537109994cf777f8d36cda617aafe12226806c25` mit vorhandenem Arbeitsbaum.
Status **PRECONDITION_BLOCKED**, Testaufrufe **0**. Kein Qualifikationslauf
und keine neue Laufnummer; insbesondere kein `NOT_QUALIFIED`-Testbefund.

| Gebundene Klasse | Grenze | Tatsächlicher Entwurf | Überschreitung |
| --- | ---: | ---: | ---: |
| Versuchsspezifischer Starterquelltext | 4.096 Byte | 6.720 Byte | 2.624 Byte |

Datei: [start_terminal_basic_once.py](start_terminal_basic_once.py).
SHA-256: `e8b18cb55a7cce4787c4bf59cfc00e62902307a9e38bf88a2b33a625ea8deb85`.
Die Größe wurde als Dateigröße gelesen, nicht durch eine Ausführung ermittelt.
Kein Import oder Aufruf des neuen Starters erfolgte.

## Umfang des unqualifizierten Entwurfs

- Feste Lauf-ID und abschließend noch zu erstellende Freigabebindung; keine
  allgemeine CLI-Gateoption. Ohne finale Bindung scheitert der Einstieg vor Öffnung.
- Gateöffnung nur beim ersten passenden Benutzerkommando `open`, Rücksetzung
  in `finally`; einzelne Benutzereingaben statt automatischer Ereignisfolge.
- EOF/Abbruch und Fehlerabschluss delegieren an den vorhandenen Client.
  Der Starter enthält keinen eigenen Verifikatoraufruf.
- Unabhängige Anzeigeprojektion aus gespeicherten Schrittfeldern ohne Aufruf
  von `render_step`; nur Anzeigehashes werden zusätzlich gehalten.
- Fachliche Bewertung erst nach gespeichertem gültigem technischem Abschluss;
  Wiederverwendung der bestehenden OB-Auswertungsfunktion, nicht ihres Haupteinstiegs.

Dies sind implementierte, **noch nicht qualifizierte** Kontrollabsichten.
Der Entwurf ist keine endgültige Ausführungsbindung. Insbesondere sind die
zusätzliche Auswerterabhängigkeit, Test-/Aufrufdateien, neutralen Eingangsbelege,
Qualifikations- und tatsächlichen Abschlussformen noch gemeinsam zu binden.
Die frühere Vorbilanz darf deshalb nicht als neue Gesamtbilanz ausgegeben werden.

## Offene Prüfdeckung

Noch nicht erreicht: kurze native Sitzung mit neu gebundenen neutralen Payloads,
Anzeigevergleich gegen gespeicherte echte Schritte, falsche Kommandoreihenfolge,
EOF/vorzeitiges Schließen, Fehlerabschluss ohne zweite Publikation/Verifikation,
vollständige tatsächliche Abschlussbilanz. Die vorhandenen synthetischen 16/16
bleiben auf die Client-Bedienhülle begrenzt und ersetzen keine dieser Prüfungen.

Gemäß Auftrag wird vor dem einzigen Testaufruf gestoppt, sobald der verständliche
Starter die lokale Reserve überschreitet. Keine Kürzung, Auslagerung ungezählter
Pflichtlogik, Grenzerhöhung oder neue Verpackung wurde vorgenommen.
Eine Entscheidung über die lokale Starterreserve ist erforderlich; selbst danach
muss die gesamte Hülle einschließlich aller zusätzlichen Nachweise zuerst passen.
Es wird keine automatische Folgeausführung vorbereitet oder gestartet.

Keine Payloads erzeugt oder verarbeitet, keine Sitzung, Rezeptor-, NJ-, Memory-
oder Feldaufrufe. Das reale Ergebnisverzeichnis und die finale Bindungsablage
existieren weiterhin nicht. Gates bleiben `False`. Historische Qualifikationen,
OB-Dateien und abgeschlossene Läufe bleiben unverändert.
