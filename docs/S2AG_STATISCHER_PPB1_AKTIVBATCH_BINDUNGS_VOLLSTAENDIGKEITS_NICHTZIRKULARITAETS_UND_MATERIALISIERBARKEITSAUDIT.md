# S2-AG: Statischer Vollstaendigkeits-, Nichtzirkularitaets- und Materialisierbarkeitsaudit

## Auftrag und Grenze

S2-AG prueft ausschliesslich statisch, ob der in S2-AF gebundene private
Anschluss vollstaendig, nichtzirkulaer und ohne neue Parameter umsetzbar ist.
Es wurden keine Typen, Funktionen oder Fixtures implementiert und keine
Zustands-, Probe-, Baseline- oder Feldfunktion ausgefuehrt.

## Materialisierbarer Anteil

Die eigentlichen Rezeptordaten sind anschliessbar. Mit den vorhandenen Audio-
und Videokonfigurationen des PPB-1-Browserprofils kann ein kompatibler
kontrollierter Browserpfad aufgebaut werden. Der allgemeine Browser-Bridge-
Typ erzwingt dieses Profil jedoch nicht. Deshalb muss der Binder Modalitaet,
Geometrie, Traegerreihenfolge und Wertedimension exakt vergleichen und jeden
abweichenden Batch ohne Transformation, Resampling oder Fusion verwerfen.

Jeder zeitgebundene Frame stellt ausserdem Snapshotidentitaet, Quellzeit und
gemeinsames Feldzeitintervall bereit. Batch-, Profil- und Bankdigests sind
deterministisch ableitbar. Der Anschluss braucht weder eine neue numerische
Regel noch eine Aenderung an API, Snapshot oder Feldkern.

Die Abnahme ist nicht zirkulaer: Sie darf nur Identitaet, Digest, Zeitordnung,
Unveraenderlichkeit und Vollstaendigkeit pruefen. Bildung, Stabilisierung,
Wiedererkennung oder spaetere Vergleichsergebnisse duerfen den Anschluss
weder erzeugen noch bestaetigen.

## Ein verbleibender Blocker

Der S2-AF-Funktionskopf enthaelt nur `binding_id`,
`BrowserReceptorSequenceBatch` und `PPB1ReceptorProfileBinding`. Der Batch
enthaelt zwar ID und Digest des `BrowserWorldContract`, aber nicht dessen
kanonischen Inhalt. Der Binder kann deshalb den Vertragsdigest aus seinen
aktuellen Eingaben nicht unabhaengig neu berechnen.

Damit ist die geforderte exakte Quellbindung noch nicht fail-closed
materialisierbar. Ein syntaktisch gueltiger Digest koennte lediglich
weitergereicht werden. Das reicht fuer die in S2-AF gebundene Rolle
`BATCH_OR_CONTRACT_DIGEST_MISMATCH` nicht aus.

## Erforderliche Korrektur

Vor jeder Implementierung muss der statische Vertrag genau um das validierte,
unveraenderliche `BrowserWorldContract`-Objekt als Eingabe ergaenzt werden.
Dann lassen sich Vertrags-ID und neu berechneter Vertragsdigest gegen den
Batch pruefen, bevor eine vollstaendige Huelle entsteht.

Nicht zulaessig sind ein ungeprueft vertrauter Digeststring, eine externe
Soll-ID ohne Quellobjekt, eine Rekonstruktion des Vertrags aus Rezeptorframes
oder eine Teilhuelle vor abgeschlossener Pruefung.

## Entscheidung und naechster Schritt

S2-AF ist in seiner aktuellen Eingabeform noch nicht implementierungsreif.
Der Stopp betrifft genau eine Provenienzrolle; Datenformat, Profilpassung und
PPB-1-Regeln sind davon nicht betroffen.

S2-AH soll ausschliesslich die statische Vertragskorrektur binden: Das
validierte `BrowserWorldContract` wird als vierte Eingabe aufgenommen und
seine ID sowie sein Digest muessen exakt mit dem Batch uebereinstimmen. Eine
Implementierung oder Ausfuehrung bleibt weiterhin gesperrt.

Maschinenlesbarer Audit:
[S2AG_STATISCHER_PPB1_AKTIVBATCH_BINDUNGS_VOLLSTAENDIGKEITS_NICHTZIRKULARITAETS_UND_MATERIALISIERBARKEITSAUDIT_V1.json](S2AG_STATISCHER_PPB1_AKTIVBATCH_BINDUNGS_VOLLSTAENDIGKEITS_NICHTZIRKULARITAETS_UND_MATERIALISIERBARKEITSAUDIT_V1.json).
