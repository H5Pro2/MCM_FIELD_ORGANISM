# Lauf 183: Reale Audio-Video-Markerantwort

## Forschungsfrage und Auftrag

Geprueft wurde, ob drei physisch gleichzeitig sicht- und hoerbare
Klatschereignisse in den bereits reduzierten Kamera- und Mikrofonrezeptoren
auf demselben `organism.monotonic_ns`-Takt als getrennte Transienten
erscheinen und einen begrenzten Audio-Video-Versatz messbar machen.

Die Benutzerin oder der Benutzer bestaetigte die physische Bereitstellung des
Markers. Feld-, Memory-, Bedeutungs- und Organisationsmechanik durften nicht
geaendert werden.

## Verwendete Quellen

Tatsaechlich verwendet wurden:

- die direkte Benutzerbestaetigung und der freigegebene Auftrag zu Lauf 183
- `AGENTS.md`
- `docs/forschung/079_REALE_AUDIO_VIDEO_REPLIKATION_LAUF_182.md`
- `mcm_field_organism/receptor_contract.py`
- `mcm_field_organism/receptor_time_alignment.py`
- `mcm_field_organism/live_audio_video_field.py`
- `tools/run_live_receptor_time_audit.py`

Externe Quellen, Browsermedien und projektfremde Datenbanken wurden nicht
verwendet.

## Verwendete Dateien und Schnittstellen

Verwendet wurden Kameraindex `0`, Audioindex `1`,
`capture_live_audio_video_time_audit`, `ReceptorTimeSequence`,
`ReceptorContactFrame.values` und `CommonFieldTime`.

Neu angelegt wurden:

- `mcm_field_organism/receptor_marker_audit.py`
- `tools/run_live_receptor_marker_audit.py`
- `tests/test_receptor_marker_audit.py`
- dieses Forschungsdokument

Die Erweiterung ist ausschliesslich Reporting auf reduzierten
Rezeptorzustaenden. Sie veraendert weder Sensoradapter noch Rezeptoren,
Verteilung oder Feld.

## Durchgefuehrte Schritte

1. Vorhandenen Zeit-Audit und die reduzierte Rezeptorschnittstelle geprueft.
2. Eine deterministische Transientenauswertung implementiert: mittlere
   absolute Wertdifferenz zweier aufeinanderfolgender reduzierter Zustaende.
3. Die Erkennungsschwelle je Modalitaet als Maximum einer vorangestellten
   ruhigen Kontrollphase festgelegt. Es wurde kein erwarteter Versatz
   einprogrammiert.
4. Drei Antworten mit mindestens 1,2 Sekunden Abstand vorregistriert. Eine
   Reihenfolgepaarung ist nur bei genau drei Antworten beider Modalitaeten
   zulaessig.
5. Implementierung und bestehende Zeit-/Runtime-Schnittstellen getestet.
6. Einen realen 10-Sekunden-Lauf ausgefuehrt: 3 Sekunden ruhige Kontrolle,
   1 Sekunde ausgeschlossene Uebergangsphase, danach Markerphase.
7. Keine Rohbilder und keine Audiosamples gespeichert.

Ein erster 24-Sekunden-Aufruf wurde vor Sensoraufnahme von der vorhandenen
maximalen 10-Sekunden-Grenze abgewiesen. Ein anschliessender Shell-Aufruf mit
einem 1-Sekunden-Prozesslimit wurde vom Werkzeug beendet. Beide enthalten
keine Forschungsdaten. Nur der danach regulaer abgeschlossene Lauf wird
ausgewertet.

## Messergebnisse und Gegenbaselines

```text
Organismustakt:                         organism.monotonic_ns
Aufnahmedauer:                          10,0 s
ruhige Kontrollphase:                    3,0 s
ausgeschlossene Uebergangsphase:         1,0 s
erwartete Marker:                           3
Mindestabstand:                          1,2 s

auditive Kontrollschwelle:       0,0108418739
auditive Antworten oberhalb:                1
staerkste ausgewaehlte Antwort:  0,0120354477

visuelle Kontrollschwelle:       0,0654687903
visuelle Antworten oberhalb:                0

vollstaendige Reihenfolgepaarung:         nein
berechnete Versatzwerte:                     0
Rohsensorpayload gespeichert:             nein
Feldmechanik geaendert:                    nein
```

Verifikation:

```text
23 passed, 9 subtests passed in 1.29s
```

Die ruhige Anfangsphase ist die modalitaetsspezifische Gegenbaseline. Da
nicht beide Modalitaeten die vorregistrierte Zahl unabhaengiger Antworten
lieferten, wurde keine Ersatzpaarung, Interpolation oder Versatzschaetzung
vorgenommen.

Ein zweiter technisch regulaer abgeschlossener 10-Sekunden-Durchgang wurde
nach Abschalten zusaetzlicher Raumventilatoren gestartet. Der unvermeidbare
Laptopluefter blieb als Bestandteil der ruhigen Eigenkontrolle bestehen. Eine
lange Unterbrechung der Benutzerkommunikation verhinderte jedoch das
verlaessliche Klatschsignal im vorgesehenen Zeitfenster. Dieser Durchgang
lieferte bei auditiver Schwelle `0,0119352804` und visueller Schwelle
`0,0160747505` in beiden Modalitaeten null ausgewaehlte Antworten und null
Versatzwerte. Er wird als koordinativ unbrauchbarer Kontrollbefund
dokumentiert, nicht als Markerreplikation.

## Einordnung

**Beobachtet:** Eine auditive Transiente, aber keine visuelle Transiente lag
oberhalb des jeweiligen Maximums der ruhigen Kontrollphase. Drei paarbare
multimodale Markerantworten wurden nicht beobachtet.

**Technische Interpretation:** Der Lauf reicht nicht fuer eine Aussage zum
Audio-Video-Versatz. Die visuelle Klatschbewegung kann unter der
Kontrollschwelle geblieben sein; ausserdem war der reale Beginn der
Messphase wegen des vorgelagerten Kamera-Startups fuer die physisch handelnde
Person nicht exakt sichtbar.

**Offene Frage:** Ob ein nach dem Kamera-Startup ausgegebenes technisches
Bereitschaftssignal eine reproduzierbare Markerplatzierung innerhalb der
Messphase erlaubt.

**Nicht gepruefte Annahme:** Es ist nicht belegt, dass die einzelne auditive
Antwort einem bestimmten Klatscher entspricht. Ebenso ist nicht belegt, dass
alle drei Handlungen im auswertbaren Zeitfenster lagen.

## Grenzen und nicht gepruefte Annahmen

- Die physische Markerzeit wurde nicht separat hardwareseitig protokolliert.
- Die Reihenfolge der Handlungen relativ zum internen Kamera-Startup war
  nicht kontrolliert.
- Die Kontrollschwelle stammt nur aus drei Sekunden derselben Aufnahme.
- Kameraautomatik, Hintergrundbewegung, Raumakustik und Betriebssystemlast
  blieben unkontrolliert.
- Die Auswertung arbeitet nur auf bereits reduzierten Rezeptorwerten und kann
  keine Rohsensorursache rekonstruieren.
- Memory, Bedeutung, Feldorganisation und Feld-Welt-Feld-Rueckkopplung wurden
  nicht untersucht oder nachgewiesen.
- Bestehende fremde Workspace-Aenderungen blieben unangetastet.

Eine Zielabweichung ist nicht erkennbar.

## Konkrete Schlussfolgerung

Lauf 183 liefert keinen messbaren Audio-Video-Versatz. Die vorregistrierte
Paarungsbedingung wurde mit einer auditiven und keiner visuellen Antwort nicht
erfuellt. Das Ergebnis ist ein begrenzter Null-/Unentscheidbarkeitsbefund,
nicht der Nachweis fehlender physischer Synchronitaet.

## Vorschlag fuer den naechsten begrenzten Forschungslauf

Lauf 184 sollte dieselbe unveraenderte Rezeptor- und Zeitmechanik replizieren,
aber der Reporting-Runner muss erst nach abgeschlossenem Kamera-Startup ein
sichtbares Bereitschaftssignal ausgeben und eine feste Vorlaufzeit beginnen.
Danach werden erneut drei Klatscher und dieselbe ruhige Gegenbaseline erhoben.

Nur wenn beide Modalitaeten genau drei getrennte Antworten liefern, darf die
Reihenfolgepaarung und deren Versatzstreuung berichtet werden. Andernfalls ist
die Markerform beziehungsweise die reduzierte visuelle Empfindlichkeit als
technische Messgrenze zu untersuchen, ohne eine neue Feld- oder Memoryregel
einzufuehren.
