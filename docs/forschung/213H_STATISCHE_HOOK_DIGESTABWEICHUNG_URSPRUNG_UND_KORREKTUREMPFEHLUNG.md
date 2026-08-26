# 213H - Statische Hook-Digestabweichung: Ursprung und Korrekturempfehlung

## Forschungsfrage und Auftrag

Dieses Dokument untersucht ausschliesslich read-only, warum der aktuelle SHA-256
von `mcm_field_organism/previous_state_contribution_hook.py` nicht mit dem in
`mcm_field_organism/_runtime_fixation_structure.py::_SOURCE_DIGESTS` gebundenen
Sollwert uebereinstimmt. Zu bestimmen sind aktueller Dateihash, eingebetteter
Soll-Digest, Ursprung der Sollbindung, betroffene Dokumente und eine eindeutige
Korrekturempfehlung.

213H ist kein Forschungslauf und keine technische Ausfuehrung. Es wurden weder
Projektmodule importiert noch Tests, Zielprozesse oder Runtimefunktionen gestartet.

## Verwendete Quellen, Dateien und Schnittstellen

Tatsaechlich verwendet wurden ausschliesslich lokale Dateien und read-only
Dateisystem- beziehungsweise Git-Metadaten:

- `mcm_field_organism/previous_state_contribution_hook.py`;
- `mcm_field_organism/_runtime_fixation_structure.py`;
- Forschungsdokumente `178`, `179`, `196`, `197`, `198`, `202`, `205`, `212`,
  `213A` und `213G` unter `docs/forschung/`;
- `Get-FileHash` beziehungsweise SHA-256 ueber lokale Rohbytes, Dateigroesse und
  UTC-Dateizeitstempel;
- `git log`, `git blame`, `git status` und Textsuche mit `rg`.

Keine Webquelle und keine externe MCM-Quelle wurde verwendet.

## Durchgefuehrte statische Schritte

1. Aktuelle Hook-Rohbytes, Dateigroesse und SHA-256 wurden gelesen.
2. `_SOURCE_DIGESTS` und alle lokalen Vorkommen von Soll- und Ist-Digest wurden
   enumeriert.
3. Die Dokumentfolge wurde vom ersten Sollwert in 178 bis zu den aktuellen
   Abweichungsbefunden in 213A und 213G verfolgt.
4. Git-Historie und Git-Trackingstatus der Hook-, Fixierungs- und Dokumentdateien
   wurden geprueft.
5. Als Gegenbaseline wurden die aktuellen Bytes unveraendert sowie mit LF- und
   CRLF-Zeilenenden gehasht.
6. Dateizeitstempel der Hook und der Dokumente 205 bis 213A wurden zeitlich
   verglichen. Zeitstempel sind dabei nur Indizien und kein Inhaltsnachweis.

## Messergebnisse

### Aktuelle und erwartete Bytebindung

| Messpunkt | Wert |
| --- | --- |
| Hook-Pfad | `mcm_field_organism/previous_state_contribution_hook.py` |
| aktuelle Groesse | 4.568 Bytes |
| aktueller Rohbyte-SHA-256 | `42f98fe9beab7f71900135524693fc7e3be898fdc16c1696057c95a0fad8a648` |
| eingebetteter Soll-SHA-256 | `2a3f2f355ba3c713296156abb08553dc4ce0cbe5a0701e12258ea286caf8371e` |
| Uebereinstimmung | nein |
| eingebettete Quelldigests insgesamt | 7/8 passend |

Der Sollwert steht direkt in `_runtime_fixation_structure.py::_SOURCE_DIGESTS`.
Der vorhandene Verifikationspfad liest die referenzierte Datei als Rohbytes. Damit
ist die Abweichung fuer diesen Vertrag materiell und nicht nur beschreibend.

### Ursprung der Sollbindung

Der frueheste gefundene lokale Beleg ist Dokument 178, Abschnitt 3. Dort wird
`2a3f...371e` ausdruecklich als SHA-256 der unveraenderten rohen Hook-Dateibytes im
damaligen Vertragsstand fixiert. Dokument 179 uebernimmt ihn als bereits statisch
fixierten Runner- und Hook-Dateidigest. `_runtime_fixation_structure.py` bettet
denselben Wert danach in `_SOURCE_DIGESTS` ein.

Die Dokumente 196, 197, 198, 202 und 205 fuehren denselben Sollwert fort. Dokument
205 behauptet fuer seinen damaligen Stand 8/8 Uebereinstimmungen. Dokument 213A
stellt erstmals den aktuellen Wert `42f9...a648` und nur noch 7/8 passende Werte
gegenueber; 213G bestaetigt diesen offenen Befund.

Die Hook wurde laut lokalem Dateisystem am `2026-07-31T21:24:20.1481336Z` zuletzt
geschrieben. Das liegt nach den lokalen Schreibzeitpunkten von Dokument 205
(`2026-07-31T19:27:29.4949047Z`) und Dokument 212
(`2026-07-31T20:10:52.2390243Z`) sowie vor Dokument 213A
(`2026-07-31T21:31:18.0591138Z`). Dies ist mit einer zwischen 212 und 213A
eingetretenen Byteaenderung vereinbar, beweist aber weder deren Inhalt noch Anlass.

### Gegenbaselines

| Bytevariante | SHA-256 | entspricht Sollwert |
| --- | --- | --- |
| aktuelle Rohbytes / LF | `42f98fe9beab7f71900135524693fc7e3be898fdc16c1696057c95a0fad8a648` | nein |
| aktuelle Zeichenfolge mit CRLF | `8e861e649e0c922d339e862dcee25d359cad3887270ea910ffa7da96e4be86eb` | nein |

Der Sollwert ist daher nicht durch eine einfache LF-/CRLF-Normalisierung der
aktuellen Datei erklaert.

## Betroffene Dokumente und Quellen

### Bindende beziehungsweise korrekturbeduerftige aktive Quellen

- `mcm_field_organism/_runtime_fixation_structure.py`: enthaelt den operativ
  verglichenen alten Sollwert;
- ein spaeterer kumulativer G0-Vertrag: muss nach einer freigegebenen Entscheidung
  den dann gueltigen Hookstand neu binden.

### Historische Herkunft und Fortschreibung

- Dokument 178: erste gefundene Sollbindung;
- Dokument 179: Uebernahme als geschlossener Wert;
- Dokumente 196, 197, 198, 202 und 205: Fortschreibung beziehungsweise damalige
  Byte- und Umfangsaussagen.

Diese historischen Dokumente sollen nicht rueckwirkend umgeschrieben werden. Ihre
Aussagen gelten fuer den jeweils dokumentierten Bytezustand und muessen durch eine
neue Korrekturakte abgegrenzt werden.

### Aktuelle Diagnose, nicht zu korrigieren

- Dokument 213A: erster gefundener aktueller 7/8-Abweichungsbefund;
- Dokument 213G: bestaetigte G0-Sperre wegen derselben Abweichung;
- Dokument 213H: vorliegende Ursachen- und Entscheidungseingrenzung.

## Grenzen und nicht gepruefte Annahmen

- Hook, Fixierungsstruktur und Forschungsdokumente sind lokal unversioniert. `HEAD`
  kennt diese Pfade nicht; `git log` und `git blame` koennen deshalb keinen
  Aenderungsautor, Commit oder Altinhalt liefern.
- Die alten Hook-Rohbytes mit SHA-256 `2a3f...371e` wurden nicht gefunden. Ein
  inhaltlicher Diff zwischen altem und aktuellem Hook ist daher nicht moeglich.
- Dateizeitstempel koennen kopiert oder veraendert werden und sind kein
  kryptografischer Herkunftsnachweis.
- Es wurde nicht bewertet, ob der aktuelle Hook-Inhalt fachlich beabsichtigt,
  geprueft oder freigegeben ist.
- Es wurde keine Aussage zu G1, G2, AppContainer-Lauffaehigkeit, Huerde G,
  Feldwirkung, Memory oder KI getroffen.

## Beobachtung, Interpretation und Schlussfolgerung

- **Beobachtet:** Der aktuelle Hook besitzt 4.568 Bytes und SHA-256
  `42f9...a648`; `_SOURCE_DIGESTS` erwartet `2a3f...371e`. Beide getesteten
  Zeilenendenvarianten verfehlen den Sollwert.
- **Technische Interpretation:** Die aktuelle Runtime-Fixierungsbindung wuerde den
  Hook korrekt als nicht eingefroren ablehnen. G0 bleibt damit nicht bestanden.
- **Hypothese:** Die Hook-Rohbytes wurden nach der letzten dokumentierten 8/8-Basis
  und vor 213A geaendert. Wegen fehlender Versionshistorie ist das nicht als
  Inhalts- oder Freigabenachweis belastbar.
- **Offene Frage:** Ob die aktuellen Hook-Bytes der gewollte neue Quellstand oder
  eine unbeabsichtigte Abweichung sind, ist durch die vorhandenen statischen Quellen
  nicht entscheidbar.
- **Nicht gepruefte Annahme:** Ein blosses Ersetzen des Sollwerts wuerde unterstellen,
  dass der aktuelle Hook fachlich autorisiert ist. Diese Annahme ist unzulaessig.

Konkrete Schlussfolgerung: Der alte Sollwert darf weder stillschweigend auf den
aktuellen Hash umgestellt noch durch Ruecksetzung der Hook-Datei erzwungen werden.
Ohne belegten Altinhalt ist eine Ruecksetzung nicht reproduzierbar; ohne
Inhaltsabnahme ist eine Neubindung nicht gerechtfertigt.

## Eindeutige Korrekturempfehlung und naechster begrenzter Schritt

Als naechster Schritt ist genau eine statische Hook-Inhalts- und Herkunftsabnahme
zulaessig. Sie muss den aktuellen Hooktext read-only gegen seine dokumentierte Rolle
in 172 bis 179 und gegen alle spaeteren ausdruecklichen Hook-Aenderungsauftraege
abgleichen und eindeutig eine von zwei Entscheidungen dokumentieren:

1. **Aktueller Stand autorisiert:** Danach ist in einem separaten, erneut
   freizugebenden Korrekturpaket der operative Sollwert in `_SOURCE_DIGESTS` auf
   `42f9...a648` zu setzen und der vollstaendige aktuelle G0-Umfang atomar neu zu
   hashen. Historische Dokumente bleiben unveraendert.
2. **Aktueller Stand nicht autorisiert oder Herkunft weiter unbelegt:** Keine
   Byteaenderung und keine Neubindung. G0 bleibt gesperrt, bis ein autorisierter,
   bytegenau bestimmter Hookstand vorliegt. Eine Rekonstruktion aus dem Digest allein
   ist ausgeschlossen.

213H selbst empfiehlt keine der beiden Inhaltsentscheidungen. Es empfiehlt
verbindlich deren Reihenfolge: zuerst statische Inhalts- und Herkunftsabnahme, erst
danach gegebenenfalls ein gesondertes Bytebindungs-Korrekturpaket. G1, G2 und jede
Huerde-G-Entscheidung bleiben bis dahin gesperrt.
