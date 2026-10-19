# Vorbereitung des einmaligen neutralen URA1-Größentests

Stand 2026-10-15. Vorbereitung bestanden; der eigentliche Marker war bei Erstellung dieses Berichts noch nicht reserviert.

S01–S07 bestehen mit höchstens acht Policy-Frames je Test. Bindung von Material, Code, Runtime, Grenzen und Aufruf, exklusiver verbrauchter Marker, unabhängige Erfassungsanker, absichtlich neu gehashte Manipulationen, Dictionaryabbruch, Fortschritt, Cleanup und Exportgrenzen sind geprüft. Die bestehende 128-Frame-Hülle blieb unverändert.

Zusätzliche Supervisorproben im harten gemeinsamen Windows-Job bestätigen Startfehler nach reserviertem Testmarker sowie Worker- und Gesamtfristüberschreitung mit bestätigtem Workerende. Jeder Testmarker liegt ausschließlich im Vorbereitungsverzeichnis. Die finalen Belege stehen unter qualification-final; der frühere vorbereitende Durchlauf bleibt erhalten.

Der unabhängige Ankernachweis wird aus kanonisch normalisierten Originalrecords vor Referenzencoderzugriff gebildet. Der Decoder prüft alle acht Folgen samt Anzahl, Byteumfang und Hash sowie die übrige Struktur. Der zusätzliche volle Envelopehash ist kein Ersatz für diese Anker.

Die folgende einmalige Ausführung ist separat durch prestart.json/.sha256, den festen Aufruf und den exklusiven START.json-Marker gebunden. Sie ist ausschließlich ein technischer Grenztest einer periodischen 1024-Frame-Handgeschichte. Bei technischem Abbruch kein Retry, Resume oder Ersatzfall. Kein Forschungsversuch oder Leistungsurteil.
