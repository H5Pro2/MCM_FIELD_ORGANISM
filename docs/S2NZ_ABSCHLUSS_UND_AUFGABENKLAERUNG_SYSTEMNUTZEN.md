# S2-NZ: Abschluss und Aufgabenklaerung zum Systemnutzen

Stand 2026-09-09. Ausschliesslich statische Dokumentation nach
Analystenentscheidung; keine neue Versuchslinie, Lauf-ID oder Freigabe.

## Geschlossener Befund NW bis NZ

| Stufe | Bestaetigt | Nicht daraus ableitbar |
| --- | --- | --- |
| [NW](../reports/s2nw/s2nw-learned-prediction-20260909-01/BEFUND.md) | Aus beobachteten Uebergaengen geschaetzter Parameter nuetzt nach Einfrieren auf anderem Ton-/Phasenbestand. | Allgemeine Fortsetzungsgarantie; Wechselverluste bleiben. |
| [NX](../reports/s2nx/s2nx-crossed-learning-20260909-01/BEFUND.md) | Getrennte Lernerfahrungen veraendern identische Pruefeingaben aufgabengerecht, auch gegen festes 0.5. | Automatische Auswahl der passenden Historie. Die unpassende Historie kann schaden. |
| [NY](../reports/s2ny/s2ny-prefix-recommendation-20260909-01/BEFUND.md) | Begrenzte Empfehlung anhand vergangener Fehler. | Ueberzeugender praktischer LOCAL-Zusatznutzen oder verlaessliche Anwendbarkeit. |
| [NZ](../reports/s2nz/s2nz-diagnostic-disturbance-20260909-01/BEFUND.md) | Technisch gueltiger Stoerungsvergleich, Schwerpunkt N=4/D=4: drei Empfehlungsgewinne gegen LOCAL, ein Verlust. | Durchgaengiger Vorteil, Robustheit oder Integrationsgrund. |

S2-NZ wird unveraendert als gemischter Diagnosebefund geschlossen.
An beiden ersten Wechselzielen empfiehlt NZ die schlechtere Historie;
an beiden Folgefenstern ist die Empfehlung NEXT_BEST, verliert aber gegen
PERSIST. Ein groesserer LOCAL-Fehler hebt diese Grenze nicht auf. Feste
Historienvorteile und tatsaechlich ausgegebene Empfehlungen bleiben getrennt.
Historische Belege, Erwartungen und Einzelwerte werden nicht geaendert.

## Bestehende Aufgabe und fehlender Verbraucher

Die vorhandene private Minimalruntime verarbeitet quellengebundene reale
AV-Ereignisse: unabhaengiger Feldkontakt, atomare Memorybildung bei
vollstaendiger Wahrnehmung und read-only Abruf bei Teilhinweisen. Ihre
Hypothesen bleiben getrennt und unangewandt. Diese Aufgabe besteht bereits
ohne eine Prognose des naechsten auditiven Rezeptorzustands.

Die Anschlussklaerung beruht auf folgenden gelesenen Grenzen, nicht auf
einer neuen Ausfuehrung oder einer Behauptung ueber alle denkbaren Verbraucher:

| Bestehender Anschluss | Gelesene Bindung | Warum daraus kein Prognosebedarf folgt |
| --- | --- | --- |
| Wahrnehmungseingang im Halbprofil | [NN: bind_event / validate_input](../tools/_s2nn_private_half_runtime_binding.py) bindet NJ-Projektion, Quellen, Zeit und dieselben Werte fuer Feld und Memory. | Eine Zukunftsschaetzung ist kein beobachteter Rezeptorendpunkt und ersetzt keine Quellenbindung. |
| Feld und Memoryfortschreibung | [MR: process_once](../tools/_s2mr_private_minimal_mcm_runtime.py) verarbeitet das aktuelle Ereignis; komplette Wahrnehmung bildet Memory, Teilhinweise lassen Memory unveraendert. | Weder Feldanregung aus Prognosen noch Bildung aus erwarteten statt beobachteten Werten ist bestehende Aufgabe. Beides waere eine neue Kopplung. |
| Aktueller Teilhinweisabruf | [NR: MaskRuntimeComparison / process_next](../tools/_s2nr_private_runtime_binding.py) verbindet MR mit Feld-, Memory- und aktuellen Scanadaptern, einschliesslich Direktbaselines. | Keine naechste Zustandsprognose wird fuer den Scan benoetigt. Ein kleiner Vorhersagefehler belegt weder passende Kandidatenherkunft noch richtigen Wahrnehmungsbezug. NR bleibt eine untersuchte, nicht bevorzugte Maskenkomposition. |
| Diagnoseausgang | [NZ: execute / evaluate_file_once](../tools/_s2nz_private_diagnostic_run.py) zeichnet NY-Prognosen auf und wertet sie nach Verifikation aus. | Der Auswerter ist ein Messverbraucher des Versuchs, keine operative Aufgabe des MCM-Grundsystems. |

Historische Kontextverbraucher werden dabei nicht geleugnet:
[S2-GK](S2GK_PRIVATE_KONTEXTVERBRAUCHER_BASELINE_AUSWERTER_QUALIFIKATION.md)
betrifft read-only maskierte visuelle Kontextnutzung, nicht die Vorhersage
des naechsten auditiven Zustands. Der
[MR-Vertrag](S2MR_MINIMALER_QUELLENNEUTRALER_MCM_LERNRUNTIME_VERTRAG.md)
schliesst Kontextverbraucher, Maskenfuellung und Ersatzwahrnehmung aus
dieser Minimalruntime aus. Daraus entsteht kein freigegebener Anschluss
fuer NW/NX-Erwartungen oder NY/NZ-Empfehlungen.

## Aufgabenfragen und Fehleranforderung

1. **Verbraucher:** Im hier bestehenden Grundpfad ist kein begruendeter
   Verbraucher der naechsten auditiven Zustandsprognose benannt. Das ist
   ein fehlender Aufgabenanschluss, kein Gegenbeweis gegen Prognosen allgemein.
2. **Messbare Verbesserung:** Die vorhandenen Aufgaben betreffen korrekte
   Wahrnehmungsbindung, Feld-/Memoryfortschreibung und richtige Hypothesen
   beziehungsweise Enthaltung. Es fehlt eine konkrete Verbraucherentscheidung,
   deren Erfuellung durch geringere Prognose-MAE besser wuerde. Ein weiterer
   MAE-Vergleich waere kein eigenstaendiger Systemnutzenbeleg.
3. **Fehler oder Enthaltung:** Ohne operative Verwendung veraendert eine
   falsche oder fehlende Prognose Feld, Memory und Abruf nicht. Eine spaetere
   Verwendung muesste ihre Fehlerfolgen erst begruenden. Jetzt weder Prognosen
   als Wahrnehmung einspeisen noch Enthaltung durch Ersatzwerte verdecken.
4. **Einfache Vergleichsbasis:** Fuer die bestehende Aufgabe ist dies der
   unveraenderte Pfad ohne Verlaufserwartung: reale Eingaben verarbeiten,
   gebundene Hinweise scannen, Hypothese oder Enthaltung unangewandt ausgeben.
   PERSIST/LOCAL sind diagnostische Prognosebaselines, aber kein Nachweis,
   dass das Grundsystem ueberhaupt eine Prognose benoetigt.
5. **Sachliche Fehleranforderung:** Ohne Verbraucherentscheidung, Folgen eines
   Fehlers oder einer Enthaltung und konkrete Nutzungsanforderung ist keine
   praktische MAE-Grenze begruendbar. Abrufgrenzen, Stoerstaerke und beobachtete
   Gewinndifferenzen werden dafuer nicht als Ersatzschwelle verwendet.

## Entscheidung

**STOPP: Der Prognosevergleichszweig ruht wegen fehlenden begruendeten
Aufgabenanschlusses.** Kein kuenstlicher Verbraucher, keine bevorzugte
Empfehlungsregel und keine weitere Stoerstaerke, Koeffizientenvariante,
Fehlerschwelle oder Auswahlheuristik. Keine neue Vertragsserie.

Der begrenzte Lern- und Transferbefund NW/NX bleibt gueltig; die
Anwendbarkeit dieser Erfahrung bleibt offen. Zeitliche Nachbarschaft oder
Vorhersageerfolg begruenden weiterhin keine Quellenidentitaet oder
Objektbindung. ME/MI und Systemintegration bleiben gesperrt, Gates False.

Diese Aufgabenklaerung erzeugt keine neue Messung, Verifikation oder
Qualifikation. Keine Implementierung, Quellenproduktion oder Systemausfuehrung.
Nur die Abschlussdokumentation wird versioniert; historische Belege,
fremde Aenderungen und Bootstrap bleiben unberuehrt.

WEITER: Am besten geht es jetzt mit der Analystenentscheidung ueber eine
konkrete bestehende Aufgabe des MCM-Grundsystems weiter, unabhaengig von
einer Verwendung der Prognoseergebnisse. Bis zu einer solchen Begruendung
bleibt der Prognosezweig ruhend.
