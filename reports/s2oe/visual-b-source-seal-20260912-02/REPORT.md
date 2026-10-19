# VISUELLE-B-ANWENDBARKEIT-QUELLENBINDUNG

## Abgeschlossen

Qualifikation `visual-b-source-qualification-20260912-03`: genau ein Aufruf,
18/18 bestanden. Danach sieben RGB-Quellen genau einmal erzeugt, separat
gebunden und einmal unabhängig read-only geprüft: BINDING_VALID.
Der historische 17/18-Fehlbefund bleibt unverändert NOT_QUALIFIED.

Änderung: ausschließlich Schlüsselwortargumente im historischen Testaufruf;
Assertions und Produktregeln unverändert. Neue Ausgabe-/Qualifikationskennung
im Aufrufer. Vollständiger aktueller Code-/Interpreterstand und Prüfbestand
stehen in inventory.json und preregistration.json. Quellen nach dem Test
und vor der Bindungsprüfung unverändert bestätigt.

## Erreichte Prüfung

Inklusive Grenze 1/255 und Binary64-Nachbarwerte, aufsteigende numerische
Terme, vollständige vier B-Plätze, historische numerische Exaktgleichheit
einschließlich signierter Null und Subnormalfall, unveränderte A-/öffentliche
Auflösung, unabhängige Direktrechnung und unveränderliche Eingaben.
Quellenidentitäten, Fenster, Okklusion/Pegelreihenfolge, getrennte
Evaluationswurzel, Manipulationsabwehr und Verluste/Fehlanwendbarkeit geprüft.
Private Metadatengrenze 98.304 einschließlich Überschreitungsabweisung und
begrenzter Fehlerausgabe erreicht; keine globale Grenzänderung.

## Quellen und Aussagegrenze

Originalpayloadhash vor jeder der sieben Ableitungen gegen die historische
Versiegelung bestätigt. Jeweils nur ein RGB-Frame mit 6.220.800 Byte plus
kleiner Zeilenpuffer; kein Rohpayload gespeichert, keine Deduplizierung.
Pegeländerung beziehungsweise Rechteck vor Okklusion. Quellen, Zeiten,
eingefrorener Zustand nach Formation 4 und Evaluationsrollen getrennt gebunden.

Bytegleich nach Okklusion: vb-01/vb-02/vb-03/vb-06. Identitäten bleiben
getrennt; keine Quelle ersetzt. Dies beweist keine gemessene Rezeptorgleichheit
und keine Anwendbarkeit gegenüber dem gespeicherten Prototyp.

Seal-Digest:
`7d228bdf0d34ad0c39f5d3be1c1bafccdb3c6e1fc45169466fb6ef55f3eb0bff`
Alle sieben Payloadhashes stehen in seal.json. Die Offline-Prüfung kontrolliert
Bindungen, Formen, Vollständigkeit und Kollisionsliste, rekonstruiert aber
nicht numerisch die Bildgenerierung. Keine erneute Payloadgenerierung.

## Bilanz und offene Anschlüsse

Vorbindung: 1.278.376 Byte insgesamt, davon 73.984 Metadaten.
Abschluss einschließlich Restreserven: 1.223.137 Byte insgesamt,
59.708 Metadaten, 975.239 Quellen, 180.969 Evidenz und 7.221 Verifikation.
Keine Verletzung. balance.json trennt Dateigrößen und verbleibende Reserven;
dieser Bericht liegt innerhalb seiner 3.072-Byte-Reserve.

Keine realen Rezeptoranalysen oder B-Regelvergleiche, keine Formation,
Memory-, Feld- oder Runtimeausführung. Gates False.
Reale Slot-/Generationsanbindung und Gesamtverifikation des späteren
Vergleichs bleiben offen. Kein Funktionsgewinn behauptet, keine Folgeausführung.
