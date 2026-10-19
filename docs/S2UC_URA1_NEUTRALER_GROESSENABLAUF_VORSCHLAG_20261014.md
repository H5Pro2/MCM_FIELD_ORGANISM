# Vorschlag: genau ein späterer neutraler URA1-Größenablauf

Status: VORSCHLAG, NICHT AUSGEFÜHRT, KEINE FREIGABE.
Keine Forschungsquelle, kein statistischer Versuch und keine Bootstrapmatrix.

Ein Durchlauf mit genau einer festen 1024-Frame-Handgeschichte und zwei
Armen U/R, nacheinander in höchstens einem Worker. Material: die vorhandene
Liste D_ITEMS (16 Blöcke) exakt 16-mal wiederholen; jedes Paar wird mit der
unveränderten blocks-Funktion in vier Frames umgewandelt. Keine Zufallswahl,
Suche, Variation oder Anpassung anhand eines Leistungsabstands. Vollständige
interne und äußere Ereigniserfassung, eigene Referenzen, Aufnahme-/Ticket-/
Zellgleichheit und separate Auswahlunterschiede bleiben obligatorisch.

Ziel ist eine erste technische Größenprobe mit einer vollen Geschichtenlänge,
nicht die Abnahme der geplanten 32 Forschungsgeschichten. Kein Nutzenurteil
aus diesem periodischen neutralen Material.

Vor Ausführung müsste der Projektleiter ausdrücklich einen gesonderten
Größen-Prüfeinstieg beauftragen: Die vorhandene Kleinfallhülle akzeptiert
höchstens 128 Frames und bleibt unverändert. Dieser Vorschlag ist keine
Erlaubnis, ihre Schranke still zu entfernen. Der separate Einstieg muss die
eine feste Geschichte vorab binden und genau einen Start erlauben.

Unveränderte Grenzen: gemeinsamer harter Windows-Job für Supervisor und
höchstens einen Worker, 536.870.912 Byte Commit, Gesamtfrist 3600 Sekunden,
Workerfrist 3540 Sekunden; pro Fall höchstens 524.288 Byte gzip und
4.194.304 Byte dekomprimiertes referenziertes Archiv. Im vorliegenden
Spoolverfahren zusätzlich höchstens 262.144 Byte je Record und 67.108.864
Byte temporäre Spooldaten je Fall, ohne Erhöhung. Temporäre Daten werden
separat bilanziert; sie sind kein kostenloser Export- oder Speicherbereich.

Die Spoolgrenze könnte bei 1024 Frames zuerst greifen. Das wäre ein
technischer Abbruchbefund, kein Anlass zum Kürzen der Ereignisse oder zum
Anheben der Grenze während des Laufs. Vor Freigabe ist anhand der kleinen
Fälle zu entscheiden, ob dieses Verfahren den einen Start rechtfertigt oder
zunächst eine direkt referenzierende fortlaufende Erfassung benötigt wird.

Erwartete Belege: festes Material-/Code-/Runtime-Binding, genau 1024 Frames
je Arm, vollständige Ziel- und Ereigniszählung, unabhängige Referenzprüfung,
verlustfreie fortlaufende Decoderrekonstruktion, Prozessgrundbelegung,
Phasenmessungen und kernelgemessener gemeinsamer Job-Peak, Laufzeit,
Spool-/Exportbilanz sowie bestätigtes Cleanup.

Terminaler Abbruch bei Bindungs-, Referenz-, Bestands-, Ticket-, Zell-,
Rekonstruktions-, Vollständigkeits-, Speicher-, Zeit-, Record-, Spool- oder
Exportabweichung. Keine Teilmengenwertung, kein Retry, Resume oder Ersatzfall.
Nur ein vollständiger technischer Erfolg wäre ein Beleg für diesen einen
neutralen Fall; Forschungsbereitschaft folgt auch daraus nicht automatisch.
