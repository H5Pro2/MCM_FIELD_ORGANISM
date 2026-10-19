# PPB-Kette: feste Formatobergrenze v1

Diese Formatableitung belegt einen Teil der bestehenden 8.192-Byte-
Berichtreserve und zählt zugleich als verfügbare Referenz, nicht doppelt.
Die Vorregistrierung wird vor Veröffentlichung vollständig serialisiert und
gegen 8.192 Byte geprüft; ihre bisherige 16.384-Byte-Schätzung entfällt.
Ein größerer aktueller Quellenkatalog führt vor dem Test zum Stopp.

Gilt ausschließlich für drei Banken, je drei gebundene Übergänge mit 288
Komponenten, vier Slots, unveränderter Profilkonfiguration und sechs bereits
gebundenen Quellen. Kein allgemeiner PPB-Serialisierungsvertrag.

Die drei bisherigen 1-MiB-Reserven enthalten: den neutralen vollständigen
Record, den späteren vollständigen Record und das Fehlerpräfix derselben
Kette. Jeder wird separat mit 900.000 Byte reserviert; physisch doppelt
gespeicherte Ketten bleiben doppelt gezählt.

Konservative vollständige Zerlegung pro Kette:

| Bestandteil | Ableitung | Byte |
| --- | --- | ---: |
| Zustandsvektoren | 12 Zustände × 4 Slots × 288 × 25 | 345.600 |
| Kontakt- und Readoutvektoren | 9 × 2 × 288 × 25 | 129.600 |
| Numerische Tabellen einschließlich Hex/Originalindex | 3 × (0+1+2) × 288 × 100 | 259.200 |
| Kontakt-Carrierkennungen | 9 × 288 × 32 | 82.944 |
| Alle übrigen Felder, Schlüssel, Trenner und Wurzeln | feste Hülle | 65.536 |
| Summe | | 882.880 |
| Reserve je Record/Präfix | | 900.000 |

25 Byte umfassen einen endlichen Binary64-JSON-Zahlenwert plus Trenner
(auch Subnormale und Vorzeichen). Ein Term enthält drei feste Schlüssel,
Index 0..287, Differenz und Binary64-Hexstring; 100 Byte schließen dessen
Objektzeichen und Trenner ein. Vor Schritt drei können höchstens zwei Slots
belegt sein; daher höchstens neun aktive Kandidatenzeilen über alle Banken.
Die Tabelle enthält zusätzlich 36 Bankzeilen, auch freie, in der Resthülle.

Die Resthülle reserviert 16.384 Byte für Profil/Wurzel, 12 × 1.024 für
Zustands-/Slotmetadaten, 9 × 2.048 für Kontakt-/Readout-/Generationsbindungen,
36 × 400 für Tabellenzeilen ohne Terme und 2.048 für Ketten/Präfixabschluss:
63.552 Byte, innerhalb 65.536. Kennungen stammen ausschließlich aus dem
festen Profil oder dem Binder; Digeststrings haben 64 Hexzeichen. Keine
frei gewählten Herkunftstexte werden in die Schritte übernommen. Neutrale
Prüfung kontrolliert Carrier-/Termgrößen und vollständige Resthülle zusätzlich.
Dies ist keine Ableitung aus einer passenden Beispiel-Gesamtgröße.

Fehlertext: maximal 512 Codepunkte, höchstens 6.144 escaped Bytes;
verbleibende 2.048 Byte innerhalb failure.json=8.192 tragen feste Codes,
Phase, Zähler 0..9, Bindungsdigest und letzten Zustandsverweis. Kein
Traceback und keine frei expandierende Exceptionkette. UNKNOWN_ERROR
behauptet keine Ursache. Optionaler Nachrichtenausschnitt ist gekennzeichnet.

stdout/stderr: maximal 4.096 gespeicherte Bytes, ein Überlaufbyte zur
Erkennung, danach Prozessende und NOT_QUALIFIED. Vollständigkeit wird bei
Überlauf ausdrücklich verneint. Keine unbegrenzte Pufferung.

Erfolg und Fehler verwenden dieselbe Funktion alternatives(). Fehlerbudget
enthält konservativ auch bereits publizierte Auswertung und Verifikation.
Eine .tmp-Datei und ihr Endname ersetzen einander durch rename; exklusive
Neuanlage und kein Retry verhindern zwei Kopien desselben Ausgabeobjekts.
Übrig gebliebene .tmp-Dateien zählen in derselben Klasse. Fehler während
Fehlerpublikation oder Bilanzabschluss erhalten den Primärbeleg im Rückgabewert
mit CLOSURE_NOT_SECURED. Bei nicht beschreibbarem Datenträger wird ausdrücklich
kein vollständiger Dateibeleg garantiert. Kein Primärfehler wird neu geworfen
oder durch einen sekundären Schreibfehler ersetzt.
