# Privater UHD-Sitzungsanschluss qualifiziert

`media-uhd-admission-20260912-01`: genau einmal **6/6 bestanden**.
Keine Decoder-, Browser- oder Memoryprüfungen wiederholt. Decoder und
NativeRuntime waren in den Tests durch Aufrufsperren ersetzt.

## Änderung und Prüfdeckung

`s2oe.sampled-media.v6-file-bound-uhd` bindet den vorhandenen privaten
1024-MiB-Profilfactoryanschluss in `Session.start()`, `check_common()` und
den unabhängigen Verifikator ein. Quelle, Lauf-ID, Profilcode und tatsächliche
Prozess-/Joblimits müssen übereinstimmen. Falsche Grenzen und vermischte
Bindungen scheitern vor Medienöffnung; der Main-Gate wird zurückgesetzt.
Die alten Worker- und Playernachweise werden nicht als aktuelle Hashzulassung
ausgegeben. Sie bleiben historische Prüfdeckung.

Aktuelle Zulassung: neuer 6/6-Nachweis mit vollständigem `m.inventory()` sowie
die fest gehashten Bindungs- und Verifikationsbelege des bestandenen vollständigen
Decoderchecks. Der zugehörige Rohdiagnoserecord, die Diagnose-Aufrufskripte und
die alten Profilexperimente sind Archiv, keine durch den Sitzungsstart erneut
gelesenen Laufabhängigkeiten. Deren Angaben werden nicht erneut berechnet.
Diese aktive Abgrenzung ist prospektiv und keine Änderung ihrer historischen Bilanz.

Die Quellenbeleggrenze beträgt ausschließlich in diesem privaten v6-Pfad
327.680 Byte. Defaultdecoder weiterhin 512 MiB, historische OB-Grenzen unverändert.
Metadaten 131.072, Zusatzhülle 393.216, Gesamt 4.194.304 Byte unverändert.
Ein neutraler Grenztest bestätigt 327.680 Byte und weist +1 Byte ab.

Sechs Prüfgruppen: vollständige gültige Zulassung; falsche Limits vor
Initialisierung; vermischte Quelle/Lauf-ID; tatsächliche Workerlimitbindung;
fehlender verfügbarer Decodercheckbeleg; private Budgetgrenze und Defaults.
Keine neuen Betriebsergebnisse oder Memoryaussagen.

## Bilanz und Endbindung

Vorab wurden Test-/Aufrufdateien, aktuelle Quellen und sämtliche 50
Fortschritts-/Abschlussalternativen bilanziert. Die Qualifikation hat einen
eigenen vollständigen Dateivorrat von 49.152 Byte; keine Vermischung mit den
Sitzungsmetadaten. Die vollständige Qualifikation wird zusätzlich im gemeinsamen
Gesamtmaximum mitgezählt. Gemeinsame Referenzdateien zählen dort nur einmal.

Neue reale Bindung: `reports/s2oe/media-player-run-binding-20260912-01`.
Die ergänzende `budget-closure.json` zählt die physische Budgetdatei selbst
und ihre Abschlusshülle mit einer zusätzlichen Metadatenreserve von 16.384 Byte.
Keine Dateiinhalte ausgelagert oder gekürzt.

| Klasse | Obergrenze der gebundenen Folge | Limit |
| --- | ---: | ---: |
| Quellen | 283.802 | 327.680 |
| Sitzungsmetadaten einschließlich Budgetabschluss | 107.407 | 131.072 |
| gemeinsame Zusatzhülle | 367.770 | 393.216 |
| Verifikation | 262.144 | 262.144 |
| Laufgesamt | 3.849.686 | 4.194.304 |
| Lauf plus vollständige zusätzliche Qualifikation | 3.898.838 | 4.194.304 |

Qualifikationsmetadaten einschließlich Reserve: 87.744 Byte;
Qualifikationsgesamt einschließlich aktiver Quellen: 371.546 Byte.
Erfolgs- und Fehlerabschluss bleiben Alternativen. Die Zusatzreserve wird
auf jede der 50 Alternativen angewandt, nicht nur auf ein Erfolgsbeispiel.
Das sind Vorbindungen, keine Messung eines noch nicht erfolgten Lernlaufs.

`media-memory-video-20260911-02` bleibt unbenutzt. Keine gültige Autorisierung,
kein Serverstart, keine Medienöffnung oder Runtimeausführung. Der Starter
wurde nur über seinen lesenden Bindungslader geprüft. Die Anzeige-/Browser-
Bedienung und die neue reale Wirkung wurden nicht wiederholt oder vorweggenommen.

Ergebnis-SHA-256:
`0f1840b75f97b178f888983803225f94a70c30a57a45bccf648ad0417a422a34`.

**RÜCKMELDUNG ERFORDERLICH:** separate Freigabe des einen gebundenen Lernlaufs.
Historischer Fehlversuch bleibt `NOT_EVALUABLE`; kein Wiederanlauf.
