# S2-NV: vorab gebundene rezeptorfreie Quellenqualifikation

Genau ein Aufruf unter `s2nv-source-binding-qualification-20260909-01`,
16 neutrale Testkoerper, Failfast, kein Retry. Vor dem Aufruf werden
Testinventar, dieses Dokument, Quellhashes und Interpreter/Umgebung gebunden.
Keine neue Prognoseimplementierung: Vorschriften bleiben ausschliesslich Text.

1. Literale 20-Fenster-Folge und getrennte Quellenidentitaeten.
2. Native Zeitfenster und exakte Indexteilbarkeit, ungueltige Typen abweisen.
3. Drei gleiche Praefixrezepte in vier getrennten Quellen-/Zeitbindungen.
4. Phasenfolge einschliesslich Nullpartialposition mit neutralem Seed.
5. Gruppensumme, lokale Synthesezeit und Gainfolge gegen neutrale Direktform.
6. Genau eine Float32-Rundung erst nach Gruppenakkumulation und Gain.
7. Partialreihenfolge einschliesslich Nullamplitude unveraendert erhalten.
8. Vollstaendige synthetische Bindungspruefung ohne PCM-Erzeugung.
9. Quellen- und Zeitmanipulation getrennt abweisen.
10. Zwoelf Vorhersagestellen, Zukunft im Praefix und falsche Praefixgruppe.
11. Geschlossener funktionaler Eingabevertrag ohne Zukunftsmetadaten;
    separate Vorabmaterialisierung bleibt explizit nicht autorisiert.
12. Getrennte Evaluationswurzel und sechs strikte Prognosebedingungen.
13. Vollstaendige neutrale Metadatenhuellen und Payload-/Artefaktgrenzen.
14. Unveraenderliche Specs, Profilabweichung und Digestmanipulation.
15. Built-in-math nur bei doppeltem Herkunftsnachweis akzeptieren.
16. Ungueltige Quellenzahl, Gain, PCM-Normalform und Ausfuehrungsfreigaben;
    kein Rezeptor-/NJ-/NumPy-Import und geschlossenes Gate.

Alle Testkoerper sperren die NV- und historischen NU-PCM-Fenstereinstiege.
Nur sechs kleine neutrale Samples werden erzeugt (24 Byte), hoechstens ein
12-Byte-Generatorpayload lebend. Zusaetzliche Referenzbytes dienen nur der
neutralen Bytegleichheitsassertion. Eine ungueltige skalare Inf-Probe erreicht
keine Float32-Ablage; der interne Allokationsversuch umfasst vier Byte.
Hoechstens 64 sin-Aufrufe und 32.768 Metadaten-/Digestchecks. Keine NV-Gruppen
numerisch vorbereiten oder auswerten; Planmetadaten und synthetische Hashes
duerfen gebunden werden. Keine Rezeptor-, NJ-, Prognose-, Fehler-, Memory-,
Feld-, Kontext- oder Runtimeberechnung.

Die Quellenqualifikation prueft nur die deklarierte Praefixgrenze. Sie
qualifiziert keinen spaeteren funktionalen Vorhersager oder chronologischen
Aufrufpfad. Ein abschliessender Digest beweist diese Reihenfolge nicht.

Nur bei Bestehen genau eine Vorversiegelung unter
`s2nv-source-preseal-20260909-01`: 20 Fenster, insgesamt 96.000 Samples /
384.000 erzeugte PCM-Byte, hoechstens ein 19.200-Byte-Fenster gleichzeitig,
keine Rohablage. Beabsichtigte gleiche Praefixe und alle weiteren
Bytegleichheiten bleiben dokumentiert; keine Deduplizierung oder Ersatzquelle.
Je Plan-/Siegelwurzel maximal 65.536 Byte, Gesamtgrenze 2.097.152 Byte,
lesender Pruefbeleg 262.144 Byte. Alle spaeteren Rechenbudgets werden gebunden,
jetzt aber nicht verbraucht.

Danach genau eine unabhaengige read-only Bindungspruefung ohne
Payloadregeneration. Sie prueft Quellenmetadaten, Datei-/Objektdigests,
Praefix-/Kollisionsbindungen und Bewertungsregeln, nicht unabhaengig die
erzeugten PCM-Bytes. Zukunftsrezepte und Hashes gehoeren nur zur externen
Quellenbindung, niemals zum funktionalen Prognoseeingang. Keine anschliessende
separate Rezeptormaterialisierung: zukuenftige Endpunkte duerfen erst nach
Bindung ihrer Prognose analysiert werden, nach eigener Freigabe.
NU bleibt geschlossen, ME/MI gesperrt, Gates `False`.
