# q04/q05/q06: statische Fast-/Memory-Anschlussklärung

## Geschlossener Ausgangsbefund

Der direkte Neun-Übergänge-Versuch bleibt unverändert abgeschlossen:
q04/q05/q06 erreicht Support 1/2/3 und visuelle Stabilisierung;
q01/q02/q03 legt q02 getrennt ab; q01/q03/q04 legt q04 getrennt ab.
Keine der drei Entscheidungen zum dritten Eingang kippt gegenüber der
ursprünglichen Ankerbeziehung. Keine neue Schwelle oder Formprojektion.
Der reale Videobefund bleibt unverändert.

## Konkreter Unterschied im regulären Pfad

Gelesener Arbeitsstand zu HEAD 53710999, keine Projektimporte oder Ausführung.
`tools/_s2jw_default_live_profile.py:179–183` bindet im privaten Halbprofil
Fast mit Kapazität 3, Audio-/Visualgrenzen 0,1/0,2, Updatefaktor 0,5,
`consolidate_after=2`, Ablauf 8 und fester Halbprofil-Rangumrechnung.
Auch das historische Profil bindet `consolidate_after=2` (Zeile 134).

`mcm_field_organism/_tspm1_private.py::advance_tspm1_fast`:

- Zeile 1458 initialisiert `eligible=False`.
- Zeilen 1504–1531: Neubelegung speichert aktuelle Werte mit Support 1;
  sie ist kein konsolidierungsfähiger Match.
- Zeilen 1488–1503: Nur ein passender bestehender Slot erhöht Support,
  gesättigt auf 2, und wird ab dieser Grenze konsolidierungsfähig.
- Zeilen 2538–2548: Nur bei `candidate.consolidation_eligible` werden
  Audio- und Visual-PPB fortgeschrieben. Verwendet wird der aktuelle native
  Kontakt `exposure.visual.timed_frame.frame`, nicht der Fast-Prototyp.

Damit ergibt sich selbst im günstigsten, hier nicht als gemessen behaupteten
Fall vollständiger Fast-Matches:

| Formation | Fast | Visueller PPB-Eingang |
| --- | --- | --- |
| q04 | neue Belegung, Support 1 | keiner |
| q05 | Match, Support 2 | q05, erste PPB-Erfahrung |
| q06 | Match, Support 2 | q06, zweite PPB-Erfahrung |

Die direkte Folge q04/q05/q06 beginnt dagegen bereits mit q04 in PPB.
Aus regulär leerem Fast-/Memoryzustand können drei Formationen höchstens
zwei PPB-Schritte erzeugen. Bei stabil_after=3 kann kein neuer visueller
PPB-Slot dadurch Support 3 erreichen. Misslingende Fast-Matches verringern
die Zahl der Konsolidierungen weiter; Audiozuordnung kann diese obere Grenze
nicht erhöhen. Dies ist eine Regelfolge, kein negativer Integrationstest.

## Konsequenz für die verlangte Bindung

Die erfolgreiche direkte Dreierfolge ist als Drei-Formationen-Systemtest
nicht erreichbar. Eine Vorbelegung oder zusätzliche Formation wäre eine
andere Geschichte; sie wird weder stillschweigend eingefügt noch vorbereitet.
Ein künstlich konsolidierungsfähiger Fast-Slot wäre ebenfalls unzulässig.

Deshalb keine ausführbare Integrationsbindung, keine fingierte vollständige
Laufbilanz und kein passend gewählter Audioeingang. Quellen, Zeiten und
Kontrollhinweis werden nicht als freigegebene Eingangsfolge ausgegeben.
Die bedingte Vorbereitung eines Stabilitäts-/B-Abrufnachweises entfällt an
dieser vorgelagerten Erreichbarkeitsgrenze. Ein späterer stabiler B-Slot würde
ohnehin nicht automatisch eine eindeutige öffentliche Ausgabe bei A-Konkurrenz
begründen.

Bestehende Fast-/Memorymechanik bleibt unverändert. Keine Tests, Quellen-
oder Rezeptorverarbeitung, keine zusätzlichen direkten PPB-Aufrufe, keine
Feld-/Runtimeausführung. Gates unverändert False. Für eine andere fachliche
Systemaufgabe ist eine konkrete Entscheidung erforderlich, nicht eine weitere
isolierte Variante dieses abgeschlossenen Direktversuchs.
