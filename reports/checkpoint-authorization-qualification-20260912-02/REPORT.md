# Neustartanschluss v2: vollständige Vorbilanz weiterhin außerhalb der Grenzen

**PRECONDITION_STOP; null neue Testaufrufe, kein Hauptlauf.**
Die 17 ergänzenden Prüfgruppen sind vorbereitet, nicht bestanden.
Der historische 24/24-Teilnachweis bleibt unverändert und wird nicht wiederholt.

## Private Änderung

`checkpoint.transfer-budget.v2` bindet prospektiv 131.072 Byte Metadaten.
Die historischen Ledger und Defaults bleiben bei 65.536 Byte. Die private
Publikation und `suspend_transfer()` benutzen die neue Grenze, ohne globale
Variablen historischer Module umzuschalten. Feldcheckpoint: weiterhin
524.288 Byte Schutzdeckel, bestehende Formatobergrenze 426.580 Byte.
Gesamt: weiterhin 4.194.304 Byte.

Workerautorisierung bleibt vor Gateöffnung und Sitzungserzeugung: feste
Autorisierung in kanonischer JSON-Form, Lauf-/Manifest-/Profil-/Codebindung,
Rollenabschnitt und verbrauchte Hauptzulassung; exklusive Rollenmarke.
Referenz 1–7, Save 1–4, Restore 5–7. Keine Zulassung wurde erzeugt.
Diese Änderungen sind noch nicht qualifiziert.

## Vollständige Schutzrechnung

Die neuen Angaben für Autorisierung, Verbrauch, gemeinsame Runtimebindung,
Dispatch, Qualifikation, Settings, Erfolgsabschluss, Ledgerpublikation und
Fehlerabschluss sind einbezogen. Erfolgs- und Fehleralternativen werden nicht
addiert. Die Gesamtwerte verwenden die zugehörige Prozessphase, nicht die
höchste Metadatenzahl einer anderen Phase.

| Grenze | Hergeleitete Spitze | Grenze | Überschreitung |
|---|---:|---:|---:|
| Metadaten | 140.276 | 131.072 | **9.204** |
| Quellenbelege | 175.480 | 174.080 | **1.400** |
| Gemeinsame Zusatzhülle | 256.376 | 262.144 | keine |
| Gesamt | 4.295.031 | 4.194.304 | **100.727** |

Metadatenspitze: `final-ledger-write-failure`.

| Beitrag | Byte |
|---|---:|
| Gemeinsame administrative Angaben | 68.390 |
| Arm- und Checkpointmetadaten | 18.574 |
| Drei begrenzte Prozesslogs | 24.576 |
| Beide Namen der endgültigen Ledgerdatei | 27.102 |
| Beide Namen des nachfolgenden kleinen Fehlerbelegs | 802 |
| Rollenmarken | 768 |
| Checkpointverbrauch | 64 |
| Summe | **140.276** |

Die administrative Basis enthält: bestehende aktive Nachweise 24.483 Byte,
gemeinsame Runtimebindung 8.349, Autorisierung 585, Verbrauch 64, Dispatch 132,
Runtime-Vorregistrierung 3.339, neues erfolgreiches Qualifikationslog 2.166,
Qualifikationsergebnis 219, neue Qualifikationsvorregistrierung 14.569 und
neue Settings 14.484 Byte. Keine dieser Angaben wurde aus der Rechnung entfernt.

Gesamtspitze: `restore-prefix-7`, einschließlich der dortigen Fehleralternative:
3.473.396 Byte native Belege, 426.580 Feld, 22.528 NJ, je 29.184 Formation und
Generation, 175.480 Quellen sowie **138.679** zu dieser Phase gehörende
Metadaten. Summe **4.295.031 Byte**. Die 140.276 Byte einer anderen Phase
wurden hier ausdrücklich nicht eingesetzt.

Die Qualifikationsmetadaten selbst liegen mit **100.589 Byte** unter 131.072.
Die Laufhülle bleibt dennoch unzulässig; deshalb wurde die bedingte einmalige
Testfreigabe nicht verbraucht. Die vorherige Vorregistrierung `...-01` bleibt
erhalten; sie startete ebenfalls keine Tests. `...-02` enthält die ergänzte
Eigenbelegung und phasengerechte Gesamtzuordnung.

## Aussagegrenze

Das sind hergeleitete Schutzobergrenzen und gebundene Quelldateigrößen,
**keine gemessenen Größen eines realen Neustartlaufs**. Insbesondere die
Summe aus nativen Einzeldeckeln ist kein Beweis einer notwendigen Mindestgröße.
Ein engerer Nachweis müsste aus dem vorhandenen Format begründet werden;
eine passende Beispielgröße oder eine Rückkehr zur eingesetzten Budgetgrenze
wäre kein Ersatz. Nur die Quellenüberschreitung um 1.400 Byte zu beseitigen
würde die beiden anderen Konflikte nicht schließen.

`preregistration.json` enthält alle Quellenhashes, das Prüfinventar, die
Metadatenbeiträge und Prozessalternativen. `settings-proposal.json` bleibt
`ready: false`; es ist keine endgültige Einmalbindung.
Historische Belege und Kernmechanik unverändert. Kein Payloadzugriff, keine
Rezeptoranalyse, kein Memory-/Feldlauf und kein geöffnetes Gate.
`memory-restart-transfer-20260912-01` bleibt unbenutzt.
