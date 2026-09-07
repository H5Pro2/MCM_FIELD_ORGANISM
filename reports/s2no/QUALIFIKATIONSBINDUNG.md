# S2-NO: einmalige neutrale Anschlussqualifikation

Vor dem Aufruf gebunden, 2026-09-07. Kein realer NH-Funktionslauf.

## Unveraenderte Grenzen

Genau ein unittest-Prozess, failfast, 20 vorab benannte Testkoerper, 180 Sekunden.
Keine NH-Payloads, keine 28-Ereignis-Geschichte, keine NH-Rezeptorvorpruefung.
Historische Quellenplaene werden nur gelesen. Alle Hauptgates bleiben False.
Der abgewiesene Aufruf des geschlossenen Haupteinstiegs ist nur eine Guardpruefung.

Neutrale Hauptfolge: AV, Audiohinweis, Visualhinweis, AV, Audiohinweis,
Visualhinweis. Ein eigener neutraler Sinus mit Amplitude float32(0.01),
zwei neutral gesaete Bilder und deren okkludierte Ansichten. Keine Auswahl
anhand gemessener Werte. Bestehende Generatorrechnung, 1920x1080 RGB8 und
4800 PCM-Samples; pro Payload Hashpruefung vor Verarbeitung.

Vier Audiofenster, 40 Hops, 31 rollende Abschluesse, vier NJ-Projektionen und
vier visuelle Analysen. Zwei Runtimearme: 12 Ereignisse, vier Formationen,
2688 Feldkontakte, 16 Scanbelege. Zusaetzlicher Scanfehler-Kontrollpfad:
dieselben ersten zwei reduzierten Eingaben, vier Runtimeereignisse, zwei
Formationen, 768 Kontakte, keine erfolgreichen Scanbelege.
Gesamt: maximal 16 Runtimeereignisse, sechs Formationsversuche, 3456 Kontakte,
16 Scanbelege. Scanobergrenze 10624 Wertvergleiche je technischer Pruefschicht;
Formation-L1-Grenze 21312. Keine neue Feldgleichheit zwischen Alt-/Halbprofil.

Quellgenerierung neutral: ein PCM- und drei RGB-Rezeptpayloads zur lokalen
Testbindung; vier PCM-/vier RGB-Payloads bei Materialisierung; hoechstens ein
weiterer PCM-Payload im negativen Hashfall ohne Rezeptoraufruf.
Zu keinem Zeitpunkt mehr als ein PCM-Fenster und ein RGB-Frame gleichzeitig.
Keine Rohpayloads im Ergebnis. Neutraler Rohrezeptorzustand bleibt nur im
Testprozess fuer die unmittelbare Kontrolle der einmaligen Halbierung.

Gesamtbeleg maximal 4194304 Byte; NO-Aussenbeleg einschliesslich NJ-Belegen
maximal 32768 Byte. NN-Eingangsbundle maximal 65536 Byte, NG-Grenzen fuer
States/Inputs/Paare/Scans unveraendert. Eine reine Serialisierungsfixture
prueft die maximale 24-Audio-/4-Visual-Receiptbelegung ohne Quellen-/Ereignisausfuehrung.
Sie ist kein Korpus und keine Hauptgeschichte. Keine Grenzerhoehung.

## Testinventar

1. Rezeptor -> NJ -> Kontakt, vier einmalige Projektionen.
2. Doppelhalbierung typisiert ablehnen.
3. Unterschiedliche versiegelte Modalitaetsfenster unveraendert erhalten.
4. Vier Zeit-/Uhrmanipulationen unabhaengig abweisen.
5. NN-Defaultgleichheit unveraendert; falsche explizite Bindung abweisen.
6. HearingPath ueber Videoereignis und Memory ueber fruehe Hinweise fortsetzen.
7. Gleiche Inputs/korrespondierende Zustaende, getrennte Runtimeidentitaeten.
8. Hinweise read-only, gueltige Feldkontakte, Lifecycle CLOSED.
9. Quellenprofil und neues Halbprofil strikt trennen.
10. Rohzustands-, Rohwerte-, NJ- und gerundete Wertebindung; Offline-Aussagegrenze.
11. Quellen-/NJ-Digestmanipulationen abweisen.
12. Fehlende/vertauschte Receipts und Zaehlerabweichung abweisen.
13. Vollstaendige Scans, Direktbaseline und konkrete Serialisierungsgrenzen.
14. Payloadfehler vor Rezeptor, typisierter Fortschrittsbeleg.
15. Scanfehler laesst unabhaengige Feldkontakte und Memory bestehen.
16. Gueltige Enthaltung technisch gueltig, verfehlte Vorhersage fachlich falsch.
17. Genau ein read-only Dateiverifikationsaufruf, Schreibkonflikt.
18. Geschlossener Hauptgate, Einmalgrenze, unveraenderliche Belege.
19. Historische Quellenbindung und vier explizite neue Profilhashes, ohne Payloads.
20. N/D/R/L, Gewinn/Verlust und Modalitaetsnenner getrennt.

## Offline-Grenze und Auswertung

Die Online-Materialisierung prueft Payloadbytes und NJ exakt einmal am rohen
Rezeptorendpunkt. Offline werden Quelle, Rezept/Fenster, Programm-/Profilbindung,
Rohzustands- und Rohwertedigest als Verknuepfungen, NJ-Digest, neue gerundete
Werte und alle technischen Runtime-/Scanbelege geprueft. Aus neuen Werten wird
ausschliesslich das neue NJ-Ausgabeobjekt aufgebaut, nie ein alter Rohvektor.

Ohne Rohenergien prueft Offline weder die FFT noch die Multiplikation oder
die Behauptung verlorener positiver Unterlaufwerte numerisch erneut.
Ein konsistent neu erfundener vollstaendiger Herkunftsbeleg waere durch
Digestkonsistenz allein nicht authentifiziert. Die vorab gebundene lokale
Online-Ausfuehrung bleibt dafuer notwendig. Keine universelle Binary64-Garantie.

Der Auswerter wird getrennt nach gueltigem Gesamtbeleg aufgerufen. Die
bestehende NH-Auswertung nutzt die neuen gespeicherten Werte und tatsaechlichen
Uebergaenge. NO ergaenzt einen konservativen Herkunftsnachweis: reine numerische
Kollision oder gemischte Herkunft ersetzt keine belegte Zielzuordnung.
Sollsupport und positive Hypothesen sind keine technischen Startbedingungen.

Quellhashes und vollstaendiges Inventar werden unmittelbar vor dem einen
Aufruf im preregistration.json festgeschrieben, danach unveraendert geprueft.
Bei Scheitern Befund sichern und stoppen. Kein Retry, keine Ersatzfixture.
