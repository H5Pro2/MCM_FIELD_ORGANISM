# Statische Vorregistrierung des stdin-Transports fuer den Bindungs-Preflight

## 1. Forschungsfrage und Auftrag

Kann der in Lauf 191 vor jeder Projektfunktion gescheiterte Transport des
Bindungs-Preflight-Codes so korrigiert werden, dass ein spaeterer, separat
freizugebender Versuch den unveraenderten Code ueber die Standardeingabe von
Python erhaelt, ohne erneut die fehleranfaellige `python -c`-Argumentgrenze zu
verwenden?

Dieses Dokument korrigiert und registriert ausschliesslich den
Prozesstransport. Es fuehrt weder den Transport noch den Bindungs-Preflight aus.

## 2. Verwendete Quellen und Dateien

- `AGENTS.md`
- `AKTUELLER_FORSCHUNGSWEG.md`
- aktueller Freigabe-Eingang des Forschungshelfers
- `mcm_field_organism/_previous_state_integration_contract.py`
- `mcm_field_organism/_runtime_fixation_handoff.py`
- `mcm_field_organism/_runtime_fixation_structure.py`

Die drei Python-Dateien wurden nur als lokale Schnittstellenquelle gelesen.
Keine externe Quelle wurde verwendet.

## 3. Festgeschriebener Prozessaufruf

Ein spaeterer, separat freizugebender Versuch darf genau einen Unterprozess mit
folgender Argumentfolge starten:

```text
.venv\Scripts\python.exe -B -I -
```

Der letzte Bindestrich ist verpflichtend und weist Python an, den Quelltext
vollstaendig von `stdin` zu lesen. `-c`, eine temporaere Python-Datei und jede
andere Quelltextuebergabe sind verboten.

Der aufrufende Prozess muss die vollstaendige, vorab fixierte UTF-8-Nutzlast
ohne BOM genau einmal in `stdin` schreiben und die Pipe danach schliessen. Es
darf keine interaktive Eingabe, keine zweite Schreiboperation, keinen Retry und
keine automatische Fortsetzung geben.

## 4. Unveraenderte Preflight-Nutzlast

Die Transportkorrektur darf den fachlichen Python-Quelltext des bereits
vorregistrierten Bindungs-Preflights nicht veraendern. Insbesondere bleiben die
vorgesehene Reihenfolge und Aufrufanzahl unveraendert:

```python
binding = _build_private_fixation_binding()
bundle = _execute_private_runtime_fixation(binding)
manifest = build_locked_previous_state_minimal_manifest()
contract = _build_private_integration_contract(bundle, manifest)
```

Jeder dieser vier Aufrufe ist fuer einen spaeteren Versuch hoechstens einmal
zulaessig und nur in der gezeigten Reihenfolge. Dieses Dokument importiert oder
ruft keine dieser Funktionen auf.

## 5. Statische Transportgrenzen

Vor einer spaeteren Ausfuehrungsfreigabe muessen mindestens folgende Punkte
statisch gebunden sein:

1. exakt der Interpreter `.venv\Scripts\python.exe`;
2. exakt die Optionen `-B`, `-I` und `-` in dieser Reihenfolge;
3. Quelltextuebergabe ausschliesslich ueber eine einmalig geschlossene
   Standard-Eingabe;
4. keine Shell-Auswertung oder Ersetzung innerhalb der Python-Nutzlast;
5. keine temporaere Datei, kein Download, kein Netzwerk und kein Bytecode;
6. ein Unterprozess, keine Kindprozesse und kein Retry;
7. die bereits vorregistrierte Laufzeit- und Ausgabegrenze bleibt unveraendert;
8. jeder Transport-, Parser-, Vertrags-, Digest-, Datei-, Ausgabe- oder
   Laufzeitfehler fuehrt zum Gesamtabbruch ohne Teilresultat.

Die Nutzlast muss vor Prozessstart als vollstaendige Bytefolge feststehen. Ein
spaeterer Ausfuehrungsvertrag muss ihren SHA-256-Digest vor dem Schreiben und
die vollstaendig geschriebene Byteanzahl pruefen. Digest und Byteumfang werden
erst mit der finalen, unveraenderten Nutzlast festgelegt und duerfen nicht aus
einer nachtraeglich rekonstruierten Shell-Darstellung abgeleitet werden.

## 6. Ausgabe- und Seiteneffektgrenze

Ein spaeterer erfolgreicher Bindungs-Preflight darf weiterhin nur das bereits
freigegebene kompakte JSON-Objekt mit `contract_digest` und den vier
Sperrmerkmalen ausgeben. Kontakt-, Effekt-, Feld- oder Zwischenwerte bleiben
verboten. Die maximale Ausgabegroesse bleibt 4096 Byte.

Vor und nach dem spaeteren Unterprozess ist derselbe vorregistrierte
Workspace-Manifestbereich zu vergleichen. Jede unerwartete Datei- oder
Metadatenaenderung sperrt das Gesamtergebnis. Dieses Dokument erzeugt ausser
sich selbst kein Artefakt und fuehrt diese Pruefung nicht aus.

## 7. Durchgefuehrte Schritte und statisches Ergebnis

- Die verbindlichen Projektleitdokumente wurden gelesen.
- Die lokalen privaten Schnittstellen wurden statisch lokalisiert.
- `python -c` wurde als Transportweg ausgeschlossen.
- Der korrigierte stdin-Aufruf wurde mit seinen Byte-, Reihenfolge-, Ausgabe-
  und Abbruchgrenzen vorregistriert.
- Es wurden keine Projektmodule importiert und keine Python-Ausfuehrung
  gestartet.

Beobachtete Messung: keine, da diese Arbeit ausschliesslich statisch ist.
Gegenbaselines: keine ausgefuehrt. Als technische Gegenabgrenzung ist nur der
in Lauf 191 gescheiterte `python -c`-Transport dokumentiert.

## 8. Grenzen, Nichtnachweis und offene Annahmen

Nicht geprueft sind die tatsaechliche stdin-Byteuebergabe, Parserfaehigkeit,
Runtime-Fixierung, Vertragskonstruktion, Bindbarkeit des `_FixedDigestBundle`,
Laufzeit, Ausgabe und Seiteneffektfreiheit. Die Annahme, dass stdin die in Lauf
191 beobachtete Argumentverformung vermeidet, ist technisch plausibel, aber
noch nicht ausgefuehrt.

Es gibt keinen Befund zu Vorzustandswirkung, Feldwirkung, Memory, Organisation,
Topologie, Bedeutung, Semantik, Selbstregulation oder KI.

## 9. Schlussfolgerung und naechster Schritt

Der Prozess-Transport ist statisch auf `.venv\Scripts\python.exe -B -I -`
korrigiert und vorregistriert. Der eigentliche Bindungs-Preflight bleibt
gesperrt.

Kleinster naechster Schritt ist eine unabhaengige statische Pruefung dieses
Transportvertrags. Erst nach positiver Pruefung darf ein neuer, genau einmaliger
Bindungs-Preflight mit final gebundener Nutzlast, festem SHA-256-Digest und
festem Byteumfang zur separaten Freigabe vorgeschlagen werden. Eine
Zielabweichung ist nicht erkennbar.

