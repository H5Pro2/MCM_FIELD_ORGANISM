# Einmalige Offline-Diagnose e03 → e04

Vorbindung, 2026-09-12. Keine Medien-, Rezeptor-, NJ-, Feld-, Memory- oder
Abrufausführung. Ausschließlich der gespeicherte Übergang des abgeschlossenen
`media-memory-video-20260912-01` wird untersucht. e03 und e04 sind unmittelbar
benachbarte vollständige Formationen; die gespeicherten Vor-/Nachbindungen
werden vor der Rechnung erneut auf ihre Integrität geprüft.

Vier visuelle PPB-Slots werden vollständig berücksichtigt, davon zwei belegt
(Generationen e02/e03). Freie und gegebenenfalls abgelaufene Slots werden
ausdrücklich ausgewiesen. Keine Beschränkung auf einen Zielslot, keine
Fast-Distanz und keine nachträgliche Schwellenwahl.

Reihenfolge: Ablaufprüfung, vollständige Kandidatendistanzen mit bestehendem
`normalized_mean_l1_distance` (`math.fsum` / 288), Grenze einschließlich
Gleichheit, Distanz-/Slot-ID-Tie-Break; andernfalls kleinste freie Slot-ID,
sonst ältester Auswahlzeitpunkt und Slot-ID. Anschließend Vergleich mit dem
aufgezeichneten Übergang und Nachzustand, keine Zustandsfortschreibung.

Arbeit: 576 gespeicherte Einzelterme plus 576 Differenzen im unveränderten
Distanzhelfer, danach separat maximal 576 direkte Prüf-Differenzen. Insgesamt
höchstens 1.728. Die unabhängige read-only Prüfung verwendet weder den
Tabellenhelfer noch den produktiven Distanzhelfer; Herkunft wird erneut aus
den gebundenen Dateien aufgelöst. Vollständige Vektoren, Originalindizes,
Differenzen, Binary64-Hexwerte, Distanz und Abstand zur Schwelle bleiben erhalten.

Neue Logik wird einmal mit zwölf neutralen Prüfgruppen qualifiziert. Keine
historischen Passzahlen und keine realen Werte in dieser Qualifikation.
Danach genau ein Tabellenaufruf und eine unabhängige Belegprüfung.

Die dateigebundene Vorbereitung erfasst Code einschließlich statischer
Importabhängigkeiten, historische Eingangsdateien und die vollständigen
Ausgaberückstellungen. Code-Dateien und historische Dateien werden physisch
einmal mitgezählt, nicht nur ihre Digestlisten. Gesamtgrenze 4.194.304 Byte;
neue Metadaten höchstens 65.536 Byte; Tabelle höchstens 196.608 Byte innerhalb
der 262.144-Byte-Beleggrenze. Historische Eingangsdateien sind eine explizite
read-only Referenzklasse, keine neuen Metadaten. Deren Größe wird vollständig
in der Gesamtbilanz gezählt. Native Zustandsdecodierung bleibt bei 98.304 Byte.

Rückstellungen: Bindung 32.768, Qualifikationslog 16.384, Qualifikation 2.048,
Tabelle 196.608, Prüfung 4.096, Fehler 16.384, Bericht 8.192, Bilanz 4.096,
Claims 10 Byte. Erfolg und Fehler bleiben endlich; eine größere Fehlerausgabe
wird ungekürzt erhalten und als Überschreitung berichtet. Keine Wiederholung.
Gates False; Ergebnis ist Diagnose, keine Erhaltungslösung.
