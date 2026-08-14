# 213I - Statische Hook-Inhalts- und Herkunftsabnahme

## Forschungsfrage und Auftrag

Zu pruefen war ausschliesslich statisch, ob der aktuelle Inhalt von
`mcm_field_organism/previous_state_contribution_hook.py` seiner dokumentierten
Rolle entspricht, durch vorhandene Aenderungsauftraege beziehungsweise
Projektaufzeichnungen gedeckt ist und als belegbar autorisiert gelten kann.

213I ist kein Forschungslauf. Es wurden keine Dateien ausser diesem Dokument
geaendert, keine Projektmodule importiert, keine Tests ausgefuehrt und keine
Prozesse gestartet. Eine Digestkorrektur oder Huerdenentscheidung ist nicht Teil
dieser Abnahme.

## Tatsaechlich verwendete Quellen

- `mcm_field_organism/previous_state_contribution_hook.py`;
- `mcm_field_organism/_controlled_av_previous_state_probe.py`;
- `mcm_field_organism/_runtime_fixation_structure.py`;
- `mcm_field_organism/__init__.py`;
- `tests/test_previous_state_contribution_hook.py`;
- `tests/test_previous_state_minimal_runner_structure.py`;
- `tools/run_controlled_av_previous_state_probe.py`;
- Forschungsdokumente 172 bis 179;
- `213_KONTROLLIERTER_AUDIOVISUELLER_VORZUSTANDSTEST_LAUF_187.md`;
- `213H_STATISCHE_HOOK_DIGESTABWEICHUNG_URSPRUNG_UND_KORREKTUREMPFEHLUNG.md`;
- lokale Dateigroessen, SHA-256-Werte, UTC-Schreibzeitstempel und Textsuche.

Keine Webquelle und keine externe MCM-Quelle wurde verwendet.

## Verwendete Schnittstellen und aktueller Inhalt

Der aktuelle Hook besitzt zwei private Funktionen:

| Funktion | beobachtete Rolle |
| --- | --- |
| `apply_previous_state_operator(field, previous_state_operator=...)` | setzt bei `zero` ausschliesslich `activation` und `afterimage` aller Neuronen vor einem nachfolgenden unveraenderten Runtimeschritt auf `0.0`; `None` und `identity` geben dasselbe Feldobjekt zurueck |
| `advance_with_previous_state_operator(...)` | fuehrt bei `None` und `identity` den bestehenden neutralen schnellen Feldpfad aus; bei `zero` verwendet es Nullvektoren nur als Integrator-Anfangsbedingung und behaelt Generator, Boundary, Zeitschritt, Konfiguration und Feldfortschreibung bei |

Beide Funktionen akzeptieren ausschliesslich `None`, `identity` und `zero`. Der
Hook exportiert keine Funktion ueber `mcm_field_organism/__init__.py`. Der private
AV-Adapter importiert nur `apply_previous_state_operator()` relativ und wendet ihn
unmittelbar vor dem Holdout an.

Aktuelle Bytebindung:

```text
path:   mcm_field_organism/previous_state_contribution_hook.py
bytes:  4568
sha256: 42f98fe9beab7f71900135524693fc7e3be898fdc16c1696057c95a0fad8a648
```

## Durchgefuehrte statische Schritte

1. Hook-Signaturen, Validierungen, Importe und beide Operatorpfade wurden als Text
   gelesen.
2. Die Rollen wurden gegen Vorregistrierung 172 und die Vertraege 173 bis 179
   abgeglichen.
3. Projektweit wurde nach beiden Funktionsnamen, dem Hook-Pfad und ausdruecklichen
   Aenderungs-, Implementierungs-, Freigabe- oder Abnahmeaussagen gesucht.
4. Der Lauf-187-Adapter und die zugehoerige Testdatei wurden nur statisch gelesen.
5. Zeitstempel und Digests von Hook, Test, CLI, AV-Adapter und Lauf-187-Dokument
   wurden erhoben.
6. Die private Exportgrenze wurde anhand von `__init__.py` und der statischen
   Strukturpruefung kontrolliert.

## Abgleich mit der dokumentierten Rolle

### Vertragslinie 172 bis 179

Dokument 172 benennt `advance_with_previous_state_operator` ausdruecklich als
`research_control`, bindet die Operatoren `None`, `identity`, `zero` und verlangt:

- `identity` bleibt bitgleich zu `None`;
- `zero` neutralisiert nur den schnellen Vorzustand aus `activation` und
  `afterimage`;
- Generator, Boundary, Zeitschritt, Rezeptorverteilung und Fortschreibung bleiben
  identisch;
- kein Produktionsschalter und kein oeffentlicher AV-Pfad;
- kein Reset, keine veraenderte Projektion, Diffusion, Daempfung oder
  Nachhallkonfiguration.

Der aktuelle Text von `advance_with_previous_state_operator()` bildet diese
technische Rolle direkt ab. Die statische Abnahme findet keine zusaetzliche
Operatorart, keine fachliche Fallregel, kein Label, keinen Reward und keine
Memorymechanik.

Die Dokumente 178 und 179 binden allerdings den aelteren Hook-Digest
`2a3f2f355ba3c713296156abb08553dc4ce0cbe5a0701e12258ea286caf8371e`.
Sie autorisieren daher nicht automatisch die heutigen Rohbytes.

### Spaetere Lauf-187-Erweiterung

Das Dokument zu Lauf 187 nennt `apply_previous_state_operator()` ausdruecklich als
private Intervention unmittelbar vor dem Holdout. Es dokumentiert sechs
Kombinationen der Operatoren `None`, `identity`, `zero`, die Begrenzung auf einen
privaten Forschungsadapter und fuenf bestandene fokussierte Hook-Pruefungen.

Der zugehoerige Adapter ruft genau diese Funktion unmittelbar vor dem Holdout auf.
Die aktuelle Testdatei bildet fuenf statische Pruefrollen ab:

1. `zero` setzt nur den schnellen Zustand auf null;
2. `None` entspricht dem Legacy-Pfad;
3. `identity` entspricht `None`;
4. `zero` aendert nur die Integrator-Anfangsbedingung;
5. Determinismus und Ablehnung anderer Operatoren.

Diese Tests wurden in 213I nicht ausgefuehrt. Beobachtet wurde nur ihr aktueller
Text; dass sie bei Lauf 187 bestanden, ist eine historische Aussage des
Laufdokuments.

## Herkunftsbefund

| Datei | Bytes | UTC-Schreibzeit | SHA-256 |
| --- | ---: | --- | --- |
| Hook | 4.568 | `2026-07-31T21:24:20.1481336Z` | `42f98f...d8a648` |
| Hook-Test | 5.683 | `2026-07-31T21:24:23.6855575Z` | `24ec42...0fe8e` |
| Lauf-187-CLI | 655 | `2026-07-31T21:24:22.4461717Z` | `155b9f...e1d66` |
| privater AV-Adapter | 10.597 | `2026-07-31T21:27:03.9991437Z` | `7f0a5f...45a80` |
| Lauf-187-Dokument | 5.711 | `2026-07-31T21:27:07.9294497Z` | `de4b1a...125a0` |

Die enge zeitliche Folge und die exakten Schnittstellenverweise sind konsistent
mit einer gemeinsamen Lauf-187-Aenderung. Sie sind jedoch kein Ersatz fuer einen
versionierten Commit oder den wortgetreuen urspruenglichen Freigabeauftrag.

Projektweit wurde kein weiteres Dokument gefunden, das den aktuellen Hash
`42f98f...d8a648` vor 213A bindet. Der Lauf-187-Bericht nennt als Quelle einen
`aktuellen freigegebenen Uebergabeauftrag`, gibt dessen Wortlaut und Byteumfang aber
nicht wieder.

## Messergebnisse und Gegenbaselines

### Beobachtetes Ergebnis

- Rollenabgleich aktueller Hook gegen 172: fachlich-technisch passend.
- Private Begrenzung: statisch vorhanden; kein Export ueber `__init__.py`.
- Lauf-187-Nutzung von `apply_previous_state_operator`: direkt dokumentiert und im
  privaten Adapter sichtbar.
- Explizite aktuelle Hashbindung vor 213A: nicht gefunden.
- Wortgetreuer Aenderungsauftrag oder versionierter Alt-/Neustand: nicht gefunden.

### Gegenbaselines

| Gegenbaseline | Ergebnis |
| --- | --- |
| aktueller Hook ohne Lauf-187-Dokument betrachten | Rolle von `apply_previous_state_operator()` waere nicht historisch zuordenbar |
| nur Dokument 172 betrachten | `advance_with_previous_state_operator()` ist benannt; die spaetere vorgelagerte Funktion ist dort nicht benannt |
| Lauf 187 samt Adapter betrachten | spaetere Funktion und privater Einsatz sind eindeutig zugeordnet |
| historische Digestbindung 178/179 als aktuelle Autorisierung behandeln | unzulaessig; sie bindet andere Rohbytes |
| Zeitstempel als alleinigen Autorisierungsnachweis behandeln | unzureichend; Zeitstempel sind veraenderbar |
| dokumentierte Testaussage als aktuelle Testausfuehrung behandeln | unzulaessig; 213I hat keinen Test ausgefuehrt |

## Autorisierungsentscheidung dieser Abnahme

Die Evidenz muss zweistufig bewertet werden:

1. **Rollen- und Einsatzautorisierung: belegt.** Die aktuelle Erweiterung
   `apply_previous_state_operator()` ist durch das Lauf-187-Dokument und den dort
   bezeichneten privaten Adapter sachlich und zeitlich zugeordnet. Ihre Rolle bleibt
   innerhalb der bereits vorregistrierten Operatoren und der privaten
   Forschungsgrenze.
2. **Exakte Byteautorisierung fuer G0: nicht belegt.** Weder ein versionierter
   Aenderungssatz noch ein erhaltenes Freigabedokument bindet SHA-256
   `42f98f...d8a648`. Der Laufbericht dokumentiert Nutzung und historische Tests,
   aber keinen neuen Quellbytevertrag.

Damit ist der aktuelle Inhalt nicht als unbegruendete fachliche Fremdmechanik zu
bewerten. Er darf aber aufgrund dieser Abnahme allein noch nicht den alten
`_SOURCE_DIGESTS`-Sollwert ersetzen.

## Grenzen und nicht gepruefte Annahmen

- Alle untersuchten neuen Pfade sind unversioniert; Git liefert keine
  Herkunftskette und keinen Inhaltsdiff zum alten Digeststand.
- Der urspruengliche Lauf-187-Uebergabeauftrag liegt nicht als lokale Quelle vor.
- Die alten Hook-Rohbytes sind weiterhin unbekannt.
- Es wurde keine dynamische Aequivalenz der beiden Operatorpfade geprueft.
- Testquelltext und historische Testergebnisangabe beweisen nicht, dass die Tests
  im aktuellen Workspace bestehen.
- G1, G2, SID, Profil, ACL, SACL, AppContainer, Huerde G und reale Ausfuehrung
  wurden nicht bearbeitet.

## Konkrete Schlussfolgerung

Der aktuelle Hook ist inhaltlich mit der dokumentierten Forschungsrolle vereinbar,
und die nachtraegliche Funktion `apply_previous_state_operator()` ist dem
freigegeben berichteten Lauf 187 belastbar zuzuordnen. Die Autorisierung reicht
jedoch nur bis zur Rollen- und Einsatzebene, nicht bis zu einer exakten neuen
G0-Bytebindung.

G0 bleibt deshalb nicht bestanden. Es wird weder eine Codeaenderung noch eine
Digestkorrektur empfohlen, bevor der Forschungshelfer die Byteuebernahme
ausdruecklich entschieden hat.

## Naechster begrenzter Schritt

Als naechster Schritt ist ausschliesslich die unabhaengige statische Pruefung von
213I zulaessig. Der Forschungshelfer soll eindeutig entscheiden, ob die
dokumentierte Lauf-187-Rollen- und Einsatzautorisierung als ausreichende Grundlage
fuer einen spaeteren, separat freizugebenden Bytebindungs-Korrekturauftrag gilt.

Nur bei ausdruecklicher positiver Entscheidung darf danach ein eng begrenztes
Korrekturpaket vorgeschlagen werden, das den aktuellen Hook-Digest in
`_SOURCE_DIGESTS` ersetzt und G0 vollstaendig neu erhebt. Bis dahin bleiben G0,
G1, G2 und jede Huerde-G-Entscheidung gesperrt.
