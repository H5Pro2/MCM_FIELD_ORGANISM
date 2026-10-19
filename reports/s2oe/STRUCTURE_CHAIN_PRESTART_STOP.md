# Direkter PPB-Kettenanschluss: Vorabstopp

Der kleine Kontakt-/Kettenbinder ist implementiert, aber **nicht qualifiziert**.
Der vorbereitende Aufruf von `reports.qualify_structure_chain_once prepare`
endet mit `ChainError: PRESTART_LIMIT` vor Ablage der Vorregistrierung und
vor jedem Testaufruf. Kein Qualifikationsclaim, keine tatsächliche Laufnummer
verbraucht, keine reale Neun-Übergänge-Geschichte. Gates False.

## Implementierter, noch ungeprüfter Umfang

`tools/_structure_ppb_chain.py` bindet die unveränderten drei Folgen an
regulär leere visuelle PPB-Banken. Quellenzeit und neue technische Kontaktzeit
sind getrennt beschrieben. Produktive Übergänge, Diagnosetabelle und
unabhängige Übergangsprüfung werden wiederverwendet. Zustandsketten,
Generationsherkunft, dritter Eingang gegen ursprüngliche Paarbeziehung und
gegen aktualisierte erste Spur bleiben getrennt.

Acht vorbereitete neue Tests in `tests/test_structure_ppb_chain.py` betreffen
nativen neutralen Gesamtumfang, Kontaktzeit, Reihenfolge, Banktrennung,
Generation, Wertebindung, erhaltenen Fortschritt bei Diagnosefehler und
reguläre negative Auswertung ohne produktiven Replay. **Null Tests ausgeführt.**
Diese Beschreibung ist keine bestandene Prüfdeckung.

## Vollständige statische Bilanz

Nach dem Vorabstopp wurden ausschließlich Dateiinventar und Reserven lesend
aufgeschlüsselt. Kein zweiter prepare-Aufruf, keine Nachsimulation.

| Klasse | Erfolg | Fehler |
| --- | ---: | ---: |
| Software-/Testquellen | 1.404.438 | 1.404.438 |
| Metadaten einschließlich 8.192 Berichtreserve | 70.646 | 70.646 |
| Evidenz einschließlich Referenzen und neutraler Hülle | 2.525.777 | 3.574.353 |
| Verifikation | 35.446 | 35.446 |
| Gesamt | **4.036.307** | **5.084.883** |

Gesamtgrenze unverändert **4.194.304 Byte**: Fehleralternative überschreitet
um **890.579 Byte**. Metadaten bleiben unter 98.304 Byte. Vorhandene aktive
Referenzdateien allein: **1.816.772 Byte**, ihr Manifest 9.418 Byte.
Damit trägt schon die konkrete Referenzmenge die frühere statische
Planannahme von maximal 1.310.720 Nichtmetadaten-Referenzbytes nicht.

Die Fehlerform enthält vorsorglich Gesamt- und Teilbeleg von jeweils
1.048.576 Byte. Die neutrale Erfolgshülle ist ebenfalls mit 1.048.576 Byte
aktiv mitgezählt. Keine Referenzen aus der Bilanz entfernt, keine kleinere
Fixture oder gekürzte Fehlermeldung eingesetzt.

## Ursache und engste Richtung

Der Import von `_s2oe_visual_transition_diagnostic` zieht dessen historische
e03/e04-Extraktion samt Profil-, Runtime- und Belegabhängigkeiten in das
aktive Inventar, obwohl nur Tabelle und reine Übergangsprüfung benötigt
werden. Das ist ein administrativer Anschlusskonflikt, kein Memorybefund.

Kleinste mögliche Korrekturrichtung wäre die explizite Trennung dieser
reinen Diagnosefunktionen von der historischen Extraktion, mit unveränderten
Rechenregeln und nachgewiesener Funktionsgleichheit. Alternativ müsste eine
kleinere vollständige Ausgabeobergrenze für die tatsächlich erforderliche
Hülle unabhängig begründet werden. Keine dieser Änderungen wurde nach dem
Stopp vorgenommen; keine Grenzerhöhung vorgeschlagen.

Die ursprüngliche Fehlstelle bleibt dokumentiert:

```text
reports/qualify_structure_chain_once.py, prepare:
c.need(len(c.s.raw(value))<=16384 and
       all(not x['violations'] for x in budgets.values()), 'PRESTART_LIMIT')
tools._structure_ppb_chain.ChainError: PRESTART_LIMIT
```

Keine Rezeptormessung, keine Quellenregeneration, keine Form-, Fast-,
Feld- oder reale PPB-Fortschreibung. Historische Dateien unverändert.
Es liegt noch keine konkrete tragfähige Einmalbindung vor.
