# 226 - Unabhaengige statische Pruefung des Korrekturvorschlags zum Bindungs-Preflight-Supervisor

## 1. Forschungsfrage und Auftrag

Ist Dokument 225 eine vollstaendige, widerspruchsfreie und statisch pruefbare
Korrekturgrundlage fuer die sechs Befunde aus Dokument 224, ohne
Implementierung oder Ausfuehrung freizugeben?

Freigegeben und durchgefuehrt wurde ausschliesslich die unabhaengige statische
Pruefung von Dokument 225. Sie ist kein Forschungs-, Test- oder Programmlauf.

## 2. Verwendete Quellen

- `AGENTS.md`
- `AKTUELLER_FORSCHUNGSWEG.md`
- `docs/forschung/217_VORREGISTRIERUNG_EINMAL_AUSFUEHRUNGSAUFTRAG_BINDUNGS_PREFLIGHT.md`
- `docs/forschung/218_STATISCHER_IMPLEMENTIERUNGSVORSCHLAG_BINDUNGS_PREFLIGHT_SUPERVISOR.md`
- `docs/forschung/224_UNABHAENGIGE_STATISCHE_IMPLEMENTIERUNGSPRUEFUNG_BINDUNGS_PREFLIGHT_SUPERVISOR.md`
- `docs/forschung/225_STATISCHER_KORREKTURVORSCHLAG_BINDUNGS_PREFLIGHT_SUPERVISOR.md`
- aktueller Freigabe-Eingang des Forschungshelfers

Keine externe Quelle wurde verwendet.

## 3. Verwendete Dateien und Schnittstellen

Die genannten Dokumente wurden ausschliesslich als Text gelesen und statisch
verglichen. Supervisor- und Testcode wurden weder geaendert noch importiert,
geparst oder ausgefuehrt. Es wurden keine Prozess-, stdin-, Runtime- oder
Preflight-Schnittstellen verwendet.

## 4. Durchgefuehrte Schritte

1. Aktuelle Projektregeln und Ausfuehrungsgrenzen gelesen.
2. Jeden Korrekturpunkt aus Dokument 225 auf den zugehoerigen Befund aus
   Dokument 224 zurueckgefuehrt.
3. Den Sonderabbruch vor Job-Zuweisung gegen den Abbruchvertrag aus Dokumenten
   217 und 218 geprueft.
4. Wandzeit, Terminierungsbestaetigung, Nachmanifest und Beobachtungsphasen auf
   vollstaendige Zustands- und Reihenfolgebindung geprueft.
5. Die vorgeschlagene statische Testabdeckung auf eindeutig pruefbare
   Sollmerkmale untersucht.

## 5. Statische Befunde

### 5.1 Hoch - Der feste TerminateProcess-Abbruchcode ist nicht festgelegt

Dokument 225 erlaubt im eng bewachten Vor-Job-Zustand genau einen
`TerminateProcess`-Aufruf mit einem "fest gebundenen Nichtnull-Abbruchcode",
nennt aber keinen konkreten Wert. Damit koennen Implementierung und statischer
Test unterschiedliche Nichtnull-Werte verwenden und dennoch jeweils eine
Vertragserfuellung behaupten.

Kleinste erforderliche Korrektur: Dokument 225 muss genau einen numerischen
Abbruchcode festlegen und dessen unveraenderte Verwendung sowie statische
Pruefung binden.

### 5.2 Hoch - Timeout, bestaetigter Abbruch und Nachmanifest sind am Fristende nicht widerspruchsfrei geordnet

Dokument 225 verlangt eine einzige absolute 60-Sekunden-Frist fuer Prozess-,
Abbruch- und EOF-Warten. Zugleich darf das Nachmanifest erst nach
bestaetigtem Prozessende oder bestaetigtem Abbruch aufgenommen werden. Wird
die Zeitueberschreitung erst mit Ablauf dieser Frist festgestellt, verbleibt
innerhalb derselben Frist keine Zeit mehr, um die erforderliche Terminierung
zu bestaetigen. Ohne Bestaetigung darf nach der vorgeschlagenen Ordnung aber
kein abschliessendes Nachmanifest als stabiler Nachzustand gelten.

Kleinste erforderliche Korrektur: Dokument 225 muss getrennt und exakt binden,
welche Frist die zulaessige Child-Lebens- und EOF-Phase begrenzt und welche
rein technische, feste Nachlaufgrenze ausschliesslich fuer
Terminierungsbestaetigung, Reader-Abschluss, Handle-Schliessung und
Nachmanifest gilt. Die Nachlaufgrenze darf weder Child-Ausfuehrung,
Ergebnisannahme noch eine Verlaengerung der 60-Sekunden-Erfolgsfrist erlauben.
Bleibt das Prozessende unbestaetigt, muss auch festgelegt werden, ob und wann
ein Nachmanifest noch aussagefaehig aufgenommen werden kann; andernfalls endet
der Zustand ausdruecklich technisch unentscheidbar.

### 5.3 Hoch - Beobachtungsmechanismus und Dokumentationsort bleiben vor der Implementierung offen

Dokument 225 fordert Betriebssystem-Thread- und Handlewerte, verschiebt aber
die Auswahl und statische Fixierung der dafuer benoetigten Windows-APIs auf
eine weitere Phase vor der Implementierung. Gleichzeitig bezeichnet es die
unabhaengige Pruefung von Dokument 225 als letzten Schritt vor einer
Korrekturimplementierung. Diese Reihenfolge ist widerspruechlich.

Zudem sollen die Werte nur im Speicher gehalten werden und das Erfolgsschema
nicht erweitern. Es bleibt offen, in welcher unveraenderlichen internen
Struktur alle drei Phasen dokumentiert und einer spaeteren Pruefung
zugaenglich werden.

Kleinste erforderliche Korrektur: Vor einer Implementierungsentscheidung sind
die konkreten Beobachtungsschnittstellen, deren Handle-Eigentum sowie eine
interne, unveraenderliche Dreiphasen-Struktur statisch zu binden. Diese
Struktur darf das gebundene stdout-Erfolgsschema nicht veraendern und keine
neue wissenschaftliche Schwelle einfuehren.

### 5.4 Bestaetigt - Die uebrigen Befundflaechen sind sachlich begrenzt

Dokument 225 bindet das Workspace-Nachmanifest an eine gemeinsame
Finalisierung, die Ablehnung doppelter JSON-Schluessel vor Dictionary-Bildung
und die Korrektur des widerspruechlichen `__pycache__`-Tests. Es haelt
Supervisor- und Testdatei als einzigen spaeteren Aenderungsumfang fest und
erweitert weder Ergebnisinhalt noch wissenschaftliche Aussage.

Diese bestaetigten Teile heben die drei offenen Vertragsstellen nicht auf.

## 6. Messergebnisse und Gegenbaseline

Es wurde kein Test, Prozess oder Preflight ausgefuehrt. Es gibt keine
Laufmessung und keine experimentelle Gegenbaseline.

Beobachtetes statisches Ergebnis: Dokument 225 adressiert alle sechs Befunde
aus Dokument 224, laesst aber drei fuer Implementierung und statische Pruefung
entscheidende Vertragswerte beziehungsweise Reihenfolgen offen.

Technische Interpretation: Eine unmittelbare Korrekturimplementierung koennte
den Abbruchcode, die Nachlaufbehandlung oder die Beobachtungsschnittstellen
eigenstaendig festlegen. Das waere erneut eine nicht vorab gebundene
Vertragserweiterung.

## 7. Grenzen, Nichtnachweis und offene Annahmen

- Windows-ABI und Runtime wurden nicht fixiert oder geprueft.
- Die Wirksamkeit von Prozess- und Job-Terminierung ist nicht nachgewiesen.
- Reader-, EOF-, Handle- und Workspace-Verhalten wurden nicht ausgefuehrt.
- Die statischen Tests wurden weder geaendert noch ausgefuehrt.
- Es liegt kein technischer Erfolg, Preflight-Ergebnis oder wissenschaftlicher
  Befund vor.
- Memory, Organisation, Topologie, Bedeutung, Selbstregulation und KI sind
  nicht nachgewiesen.

## 8. Schlussfolgerung und naechster Schritt

Dokument 225 besteht die unabhaengige statische Pruefung noch nicht. Es bleibt
innerhalb des Projektziels und der Testwelt-Grenze, ist aber wegen des
fehlenden numerischen Abbruchcodes, der unvollstaendigen Frist-/Nachlaufordnung
und der offenen Beobachtungsschnittstelle noch nicht eindeutig
implementierbar.

Der kleinste naechste Entwicklungsschritt ist eine rein statische Korrektur
von Dokument 225, die ausschliesslich diese drei Punkte festlegt. Erst danach
ist eine erneute unabhaengige statische Pruefung sinnvoll. Implementierung,
Tests, Projektimporte, Prozessstart, stdin-Transport und Preflight bleiben
gesperrt.

Keine Zielabweichung vom aktuellen Projektziel wurde festgestellt.

