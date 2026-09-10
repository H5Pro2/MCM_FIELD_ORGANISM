# S2-OA: administrative Bindungsqualifikation

Status **S2OA_ADMIN_QUALIFIED**, 20/20, Exit-Code 0. Genau ein neutraler
unittest-Aufruf unter `s2oa-admin-binding-qualification-20260910-01`.
Keine Wiederholung der historischen 18 Tests. Keine Quellenproduktion.

Die [Budgetklassen](../ADMINISTRATIVE_BUDGETBINDUNG.md) wurden vor dem Aufruf
festgeschrieben. [Vorregistrierung](preregistration.json) bindet alle 20
Testnamen, Einzel-/Gesamtgrenzen, Reserven, CPython-/Interpreteridentitaet
und sieben Dokument-/Codehashes. [Ergebnis](result.json) bestaetigt identische
Hashes vor/nach dem Test; [Protokoll](stderr.txt) weist alle Testkoerper aus.

Ergebnisdigest:
`1993a1bb91485ba41a31918f635638a8a218d7462fe6eff4eae4ac8b3cf1fbd1`.

## Tatsaechliche Deckung

- Synthetische 48 Quellen- und 28 Ereignisreferenzen akzeptiert.
- Fehlende Referenzen, falsche Digests, vertauschte Quellen-/Ereignisreferenzen
  sowie Profil-, Zeit- und Evaluationsmanipulationen typisiert abgewiesen.
- Fehlender Archivbestand und nicht passende Archivhashes abgewiesen.
- Metadaten-/Quellen-Einzelgrenzen und jeweilige Gesamtsummen geprueft;
  Gleichheit am Deckel akzeptiert, ein Byte darueber abgewiesen.
- NJ-/Formations-/Generationsreservierung einschliesslich Einzel- und
  Anzahlgrenzen geprueft. Der gemeinsame Zusatzhuellendeckel und die
  vollstaendige Gesamtgrenze sind separat abgesichert. Die strengeren
  Teildeckel verhindern bereits, dass regulaere Teilbelegungen den gemeinsamen
  Deckel erreichen; die direkte Aggregatgrenze wurde deshalb zusaetzlich
  mit synthetischen Bytezahlen am Deckel und darueber geprueft.
- Unabhaengige Bytebilanz stimmt mit der primaeren Bilanz ueberein;
  Referenzpruefung uebernimmt nicht den primaeren Kompaktierungshelfer.
- Eingaben bleiben unveraendert, Gate False, exklusive Belegpublikation
  verweigert Ueberschreiben. Historische Datenlesezugriffe und Quellen-/
  Systemimporte waren im Testprozess gesperrt; keine Payload-/Rezeptorwerte.

## Bindungen und Grenze

Budgetdokument SHA-256:
`ccdf06b57fa6f1657daf22040449a029c0f278749bf1ae00a5701a54907b8073`.
Administrative Anbindung:
`585ecc76d2734c39c555c62122e6425216c85a58774275876ce40f4a6d5902cc`.
Unabhaengige Verifikation:
`7ef5c9013eb15edecedbf584965a2b9e48d8a057d95cb6753d3412a340349273`.
Testdatei:
`1e0a178b2546511f998e99404638be77bf5c9a4c5131e033d7f39c93c3978457`.

Qualifiziert ist die administrative Referenz-/Budgetbindung, nicht der
kuenftige Eininstanz-/Generationsanschluss oder ein Funktionslauf. Reserven
sind verbindliche spaetere Obergrenzen, noch keine erzeugten NJ-/Transaktions-
oder Generationsbelege. Keine Quellen-, Rezeptor-, Memory-, Feld- oder
Runtimeausfuehrung. Historische 18/18 und v1-Vorversiegelung bleiben samt
dokumentierter Budgetabweichung unveraendert.

WEITER: Am besten geht es jetzt mit dem separat dokumentierten einmaligen
administrativen Bindungsbeleg aus vorhandenen Quellenbelegen weiter.
