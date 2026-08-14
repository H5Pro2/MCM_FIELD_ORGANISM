# 195 - Huerde C: Ressourcen- und Zeitgrenzen fuer einen moeglichen spaeteren Einmallauf

## 1. Zweck und Status

Dieses Dokument bereitet ausschliesslich Huerde C aus Dokument 192 vor. Es legt fest, welche Ressourcen- und Zeitobergrenzen vor einem moeglichen spaeteren Einmallauf konkret, endlich, technisch erzwingbar und unabhaengig pruefbar gebunden werden muessten.

Es ist keine Implementierungs-, Test- oder Ausfuehrungsfreigabe. Kein Projektmodul wurde importiert oder ausgefuehrt, keine reale Bindung erzeugt, keine Handoff-Funktion aufgerufen, keine Fixierung ausgefuehrt und keine Runtime aktiviert.

## 2. Gebundene Vertragsgrundlage

| Datei | SHA-256 |
|---|---|
| `docs/forschung/192_SPERR_UND_FREIGABEBEDINGUNGEN_REALE_FIXIERUNGSAUSFUEHRUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md` | `d6b9fedd7310425bff7bbdd3b9f2a778e0ede32c6074d4b68f78c8c4cede7edb` |
| `docs/forschung/193_HUERDE_A_BYTE_UND_UMFANGSBINDUNG_EINMALLAUF_PFAD_RUNTIME_FIXIERUNG.md` | `d002bc7832a0ef6cd36c2cc5ef481e0bb403cfede503c6ed6b22cd955c70974f` |
| `docs/forschung/194_HUERDE_B_EINMALIGER_AUSFUEHRUNGSVERTRAG_RUNTIME_FIXIERUNG.md` | `f4e2139aee4cc9f7cf95deb4cefc20881efe57aef1e17f8a9cad70b741e7274e` |

Die 37-Dateien-Bindung aus Dokument 193 und die Einmaligkeitsbedingungen aus Dokument 194 bleiben unveraendert wirksam. Dokument 195 erweitert keinen Produktions-, Test-, Runtime- oder Exportumfang.

## 3. Verbindliches Grenzwertmodell

Vor jeder spaeteren Einzelfreigabe muesste fuer jede in Abschnitt 4 genannte Ressource genau ein numerischer Grenzwert in einem separaten, bytegebundenen Ausfuehrungsprotokoll festgelegt werden.

Jeder solche Grenzwert muesste:

- endlich und groesser oder gleich null sein;
- in einer eindeutig benannten Einheit angegeben sein;
- den gesamten Prozess einschliesslich Initialisierung und Abschluss umfassen;
- vor Prozessstart unveraenderlich feststehen;
- waehrend des Prozesses nicht erhoeht, zurueckgesetzt oder neu interpretiert werden koennen;
- vor und waehrend der Ausfuehrung technisch ueberwacht werden;
- bei Erreichen oder Ueberschreiten vor jeder weiteren Fachoperation zum Abbruch fuehren;
- im Nachlauf mit Messwert, Grenzwert und Abbruchstatus dokumentiert werden.

`unbegrenzt`, `automatisch`, `nach Bedarf`, ein fehlender Wert oder ein nur beobachteter Wert ohne technische Erzwingung waeren unzulaessig.

## 4. Zwingend zu bindende Obergrenzen

| Ressource | Spaetere bindende Einheit | Vertragsbedingung |
|---|---|---|
| Wandzeit | Millisekunden | Endliche Gesamtdauer vom Prozessstart bis zum Prozessende. |
| CPU-Zeit | Millisekunden | Endliche kumulierte CPU-Zeit des einzigen Prozesses. |
| Arbeitsspeicher | Bytes | Endlicher maximaler residenter Speicher des gesamten Prozesses. |
| Kontakte | Anzahl | Endliche Gesamtzahl aller im Fixierungskorridor verarbeiteten Kontakte. |
| Paesse | Anzahl | Endliche Gesamtzahl aller ausgefuehrten Verarbeitungspaesse. |
| Kontexte | Anzahl | Endliche Gesamtzahl aller erzeugten oder verarbeiteten Kontexte. |
| Operationsaufrufe | Anzahl | Endliche Gesamtzahl aller Aufrufe ueber die gebundene `_FixationOperations`-Grenze. |
| Ausgabegroesse | Bytes | Endliche Summe aller Standard-, Fehler- und vorgesehenen Ergebnisbytes. |
| Offene Dateien | Anzahl gleichzeitig offener Deskriptoren/Handles | Endliche Obergrenze einschliesslich geerbter und intern geoeffneter Dateien. |
| Prozesse | Anzahl zusaetzlicher Prozesse | Exakt `0`; nur der eine in Dokument 194 beschriebene Hauptprozess ist zulaessig. |
| Threads | Anzahl zusaetzlicher Threads | Exakt `0`; nur der bestehende Hauptthread ist zulaessig. |
| Externe Verbindungen | Anzahl | Exakt `0`; Netzwerk-, IPC-, Mikrofon-, Kamera- und Public-AV-Verbindungen bleiben verboten. |

Die konkreten positiven Grenzwerte fuer Wandzeit, CPU-Zeit, Arbeitsspeicher, Kontakte, Paesse, Kontexte, Operationsaufrufe, Ausgabegroesse und offene Dateien werden in Dokument 195 nicht erfunden. Sie duerfen erst nach statischer Ermittlung aus dem bytegebundenen Korridor in einem separaten Vorabprotokoll festgelegt und unabhaengig geprueft werden.

## 5. Mess- und Durchsetzungsanforderungen

Eine spaetere Freigabe duerfte nur erwogen werden, wenn fuer jede Ressource vorab statisch beschrieben und technisch nachweisbar waere:

- welche unabhaengige Messquelle den Verbrauch erfasst;
- an welcher Stelle vor der ersten Fachoperation die Ueberwachung aktiv ist;
- in welchen Intervallen oder vor welchen Operationen geprueft wird;
- welcher unveraenderliche Grenzwert verglichen wird;
- wie der Prozess bei Grenzverletzung beendet wird;
- wie verhindert wird, dass der Abbruch selbst einen Retry oder zweiten Aufruf ausloest;
- wie der Nachlauf die Einhaltung ohne Interpretation reproduziert.

Eine reine Protokollierung nach Prozessende, ein Durchschnittswert oder eine Warnung ohne Abbruchwirkung genuegt nicht.

## 6. Einheitliche Abbruchsemantik

Das Erreichen oder Ueberschreiten auch nur einer Ressourcengrenze muesste den gesamten Einmallauf fehlerhaft beenden. Danach duerften nicht stattfinden:

- weitere Kontakte, Paesse, Kontexte oder Operationsaufrufe;
- Handoff-, Orchestrator- oder Fixierungsfortsetzung;
- Retry, Wiederholung, Backoff oder Prozessneustart;
- Ausgabe eines Teilwerts als erfolgreiches Ergebnis;
- Teilfreigabe eines bereits berechneten Ergebnisses;
- Runtime-, Runner-, Integrator-, Hook- oder Executorfortsetzung;
- persistente Zustandsaenderung;
- ein zweiter Lauf.

Eine Grenzverletzung darf niemals durch Erhoehung des Grenzwerts im laufenden Prozess geheilt werden.

## 7. Zusammenspiel der Grenzen

Alle Ressourcengrenzen sind kumulativ. Das Unterschreiten einer Grenze kompensiert keine Verletzung einer anderen Grenze. Der frueheste eintretende Abbruchgrund beendet den gesamten Prozess.

Die Ein-Prozess- und Ein-Aufruf-Grenzen aus Dokument 194 gelten unabhaengig von den Ressourcenwerten. Insbesondere duerfen ein Zeitabbruch, Speicherdruck oder ein Messfehler keinen zweiten Bindungs-, Handoff- oder Orchestratoraufruf ausloesen.

Ein Ausfall oder eine Unverfuegbarkeit der Messung ist selbst ein Fehlergrund und darf nicht zu einem unueberwachten Weiterlauf fuehren.

## 8. Nicht freigegebene technische Mittel

Dokument 195 erlaubt keine Implementierung eines Ressourcenwaechters, Wrappers, Runners, Executors, CLI-Einstiegs oder Betriebssystem-Limiters. Es legt auch keinen ausfuehrbaren Befehl und keine konkrete Umgebung fest.

Falls eine spaetere technische Durchsetzung eine Code- oder Umfangsaenderung erfordern sollte, waere die Bytebindung aus Dokument 193 aufgehoben. Vor jeder solchen Aenderung waeren eine neue Umfangsbindung, eine separate Implementierungsvorabnahme und eine unabhaengige Review erforderlich.

## 9. Fortbestehende Sperren

Weiterhin gesperrt bleiben:

- reale Bindungskonstruktion;
- Handoff- und Orchestratoraufrufe;
- Fixierung und Minimaltest;
- Runtime, Runner, Integrator, Hook und Executor;
- Public-AV, Sensorzugriff und realer Weltkontakt;
- Produktionsschalter und automatische Ausfuehrung;
- persistente Zustandsaenderung und Ausdruckskanaele.

Die Beschreibung spaeterer Ressourcenobergrenzen ist keine Ausfuehrungsfreigabe.

## 10. Freigabefelder

```text
real_operations_binding_release: false
real_fixation_execution_release: false
runtime_release: false
runner_release: false
integrator_release: false
hook_release: false
executor_release: false
public_av_release: false
production_switch_release: false
automatic_execution_release: false
orchestrator_handoff_release: false
minimal_test_release: false
```

`minimal_test_release_recommended: false`

## 11. Entscheidung zu Huerde C

Huerde C ist mit diesem Dokument rein vertraglich vorbereitet. Sie ist erst nach unabhaengiger statischer Review dokumentarisch abgenommen.

Aus einer positiven Review folgt keine Freigabe fuer eine Implementierung, einen Test, einen Prozessstart, eine Bindung, einen Handoff, eine Fixierung oder eine Runtime. Der einzige zulaessige naechste Schritt ist die unabhaengige statische Review von Dokument 195.

## 12. Aussagegrenze

Kein Inhalt dieses Dokuments ist ein Befund zu Feldwirkung, Kontaktgeschichte, Memory, Organisation, Bedeutung, Semantik, Bewusstsein, Eigenstaendigkeit oder KI.

## 13. Zielbezug

Es besteht keine erkennbare Zielabweichung. Die Ressourcenbedingungen begrenzen nur einen moeglichen technischen Einmallauf und programmieren weder Erinnerung noch Bedeutung, Zielverhalten oder Topologie vor.

## 14. Auftrag fuer die unabhaengige statische Review

Die Review muss mindestens bestaetigen:

- alle drei eingebetteten SHA-256-Digests stimmen;
- alle zwoelf Ressourcenkategorien aus Abschnitt 4 sind enthalten;
- jede spaetere variable Obergrenze muss endlich, numerisch, unveraenderlich und technisch erzwingbar sein;
- zusaetzliche Prozesse, zusaetzliche Threads und externe Verbindungen sind jeweils auf exakt null begrenzt;
- jede einzelne Grenzverletzung fuehrt ohne Retry, Weiterlauf oder Teilfreigabe zum Fehlerabschluss;
- Messausfall fuehrt zum Abbruch und nicht zum unueberwachten Weiterlauf;
- kein Ressourcenwaechter, Runner, Executor, CLI-Einstieg oder Ausfuehrungsbefehl ist freigegeben;
- der Freigabeblock enthaelt genau zwoelf `false`- und kein `true`-Feld;
- `minimal_test_release_recommended: false` ist gesetzt;
- `git diff --check` meldet keine neuen Whitespace-Fehler.

Die Review darf keine Implementierungs-, Test-, Runtime- oder Exportdatei aendern, keine Projektmodule importieren oder ausfuehren, keine reale Bindung erzeugen und keine Handoff-, Fixierungs- oder Runtime-Funktion aufrufen.
