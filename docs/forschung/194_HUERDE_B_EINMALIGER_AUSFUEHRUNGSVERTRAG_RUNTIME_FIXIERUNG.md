# 194 - Huerde B: Einmaliger Ausfuehrungsvertrag fuer eine moegliche spaetere Runtime-Fixierung

## 1. Zweck und Status

Dieses Dokument bereitet ausschliesslich Huerde B aus Dokument 192 vor. Es beschreibt die Kardinalitaets-, Reihenfolge- und Abbruchbedingungen eines moeglichen spaeteren Einmallaufs.

Es ist keine Implementierungs-, Test- oder Ausfuehrungsfreigabe. Es wurde kein Projektmodul importiert oder ausgefuehrt, keine reale Bindung erzeugt, keine Handoff-Funktion aufgerufen, keine Fixierung ausgefuehrt und keine Runtime aktiviert.

Huerde A ist laut unabhaengiger statischer Review dokumentarisch abgenommen. Das erfuellt Huerde B nicht automatisch und gibt keinen Einmallauf frei.

## 2. Gebundene Vertragsgrundlage

| Datei | SHA-256 |
|---|---|
| `docs/forschung/192_SPERR_UND_FREIGABEBEDINGUNGEN_REALE_FIXIERUNGSAUSFUEHRUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md` | `d6b9fedd7310425bff7bbdd3b9f2a778e0ede32c6074d4b68f78c8c4cede7edb` |
| `docs/forschung/193_HUERDE_A_BYTE_UND_UMFANGSBINDUNG_EINMALLAUF_PFAD_RUNTIME_FIXIERUNG.md` | `d002bc7832a0ef6cd36c2cc5ef481e0bb403cfede503c6ed6b22cd955c70974f` |
| `mcm_field_organism/_runtime_fixation_binding.py` | `2fa92c99b9386c1d407128b22980d211a8f2ffbad574866524010fb5c0cc7444` |
| `mcm_field_organism/_runtime_fixation_handoff.py` | `73e3fd5559dbc9eced92e2b7e31adea247c9fe8be73f79b59fc359ca2bbab068` |

Die vollstaendige Byte- und Umfangsbindung der 37 beteiligten Vorgabedateien bleibt Dokument 193 vorbehalten und unveraendert wirksam. Dokument 194 erweitert weder den Produktions- noch den Testumfang.

## 3. Definition des moeglichen Einmallaufs

Ein spaeterer Einmallauf duerfte nur als genau ein neu gestarteter Betriebssystemprozess betrachtet werden. Der Prozess duerfte genau einen linearen privaten Ausfuehrungspfad enthalten:

1. genau eine Konstruktion einer `_PrivateFixationBinding` ueber `_build_private_fixation_binding()`;
2. genau einen unmittelbaren Aufruf `_execute_private_runtime_fixation(binding)` mit genau dieser Bindung;
3. den bereits im Handoff gekapselten genau einen Aufruf von `_coordinate_runtime_fixation_with_operations(...)`;
4. unmittelbar danach genau einen erfolgreichen oder fehlerhaften Prozessabschluss.

Diese Reihenfolge ist eine spaetere Vertragsbedingung und kein jetzt auszufuehrender Ablauf. Zwischen Bindungskonstruktion und Handoff duerfte kein anderer Produktions-, Runtime- oder Integrationsschritt liegen.

## 4. Harte Kardinalitaeten

Fuer den gesamten spaeteren Prozess muessten gleichzeitig gelten:

| Ereignis | Zulaessige Anzahl |
|---|---:|
| Betriebssystemprozess fuer den Einmallauf | genau 1 |
| `_build_private_fixation_binding()` | genau 1 |
| erfolgreich an den Handoff uebergebene Bindung | genau 1 |
| `_execute_private_runtime_fixation(...)` | genau 1 |
| `_coordinate_runtime_fixation_with_operations(...)` | genau 1 |
| zweiter oder weiterer Aufruf eines dieser Ausfuehrungsschritte | 0 |
| Prozessneustart, Wiederholung oder Fortsetzung | 0 |

Ein fehlender Aufruf ist kein erfolgreicher Einmallauf. Ein zweiter Aufruf ist ein Vertragsbruch und muesste vor seinem Eintritt technisch verhindert werden.

## 5. Wiederholungs- und Nebenlaeufigkeitssperre

Der moegliche spaetere Einmallauf duerfte nicht enthalten:

- Schleifen um Bindung, Handoff oder Ablaufkoordinator;
- Retry, Backoff, Wiederanlauf oder Fehlerwiederholung;
- Rekursion oder indirekte erneute Ausloesung;
- mehrere Prozesse, Subprozesse oder Prozesspools;
- Threads, Threadpools, Tasks, Futures oder asynchrone Nebenlaeufigkeit;
- parallele oder ueberlappende Bindungs- oder Fixierungsaufrufe;
- Scheduler, Watcher, Service, Daemon oder automatische Fortsetzung;
- signal-, callback-, hook- oder eventgetriebene Wiederholung;
- einen zweiten Lauf nach erfolgreichem oder fehlerhaftem Abschluss.

Auch eine manuelle Wiederholung waere ein neuer Lauf und benoetigte eine neue, ausdrueckliche Einzelfallentscheidung. Dieses Dokument erteilt sie nicht.

## 6. Abbruchgrenze vor jedem zweiten Aufruf

Ein spaeteres Ausfuehrungsprotokoll muesste technisch nachweisen, dass eine Aufrufzaehlung bereits vor jedem Bindungs-, Handoff- und Ablaufkoordinatoraufruf geprueft wird. Sobald ein zweiter Aufruf versucht wuerde, muesste der Prozess vor Eintritt in diesen Aufruf fehlerhaft enden.

Dabei duerften nicht erfolgen:

- erneute Bindungskonstruktion;
- teilweise oder vollstaendige zweite Fixierung;
- Rueckgabe eines zweiten Ergebnisses;
- Retry oder Fortsetzung nach dem Abbruch;
- nachfolgende Runtime- oder Integrationsaktivierung.

Die konkrete technische Realisierung dieser Zaehlsperre ist nicht Gegenstand von Dokument 194. Jede dafuer erforderliche Codeaenderung wuerde die Bytebindung aus Dokument 193 aufheben und vorab eine neue Umfangsbindung verlangen.

## 7. Erfolgs- und Fehlerabschluss

Ein spaeterer Prozess muesste nach dem einzigen Handoff-Aufruf eindeutig genau einen der folgenden Endzustaende erreichen:

- erfolgreicher Prozessabschluss nach genau einem vertraglich gueltigen Ergebnis; oder
- fehlerhafter Prozessabschluss ohne Retry, zweiten Aufruf, Teilfreigabe oder Runtime-Fortsetzung.

Die konkreten Exitcodes, Ressourcenlimits, Ausgabeformate und Seiteneffektpruefungen sind in Dokument 194 absichtlich nicht festgelegt. Sie gehoeren zu den spaeteren Huerden C, E und G und muessen vor jeder Ausfuehrung separat bytegebunden und unabhaengig geprueft werden.

Unabhaengig von der spaeteren Exitcodewahl muss gelten:

- Erfolg und Fehler duerfen nicht denselben Exitstatus verwenden;
- eine Exception darf keinen zweiten Versuch ausloesen;
- ein Fehler darf kein Teilergebnis als Erfolg ausgeben;
- jeder Abschluss muss den Prozess beenden;
- nach dem Abschluss darf keine Runtime weiterlaufen.

## 8. Nicht festgelegte Ausfuehrungsparameter

Dieses Dokument legt bewusst keinen ausfuehrbaren Befehl, keinen CLI-Einstieg, kein Skript, keinen Arbeitsordner, keine Umgebung und keine Ressourcenwerte fest. Ebenso wenig wird ein neuer Runner oder Executor zugelassen.

Diese Parameter duerften erst nach Erfuellung der vorhergehenden kumulativen Huerden in einem separaten, statisch geprueften Freigabedokument exakt benannt werden. Bis dahin existiert kein zulaessiger Ausfuehrungsbefehl.

## 9. Fortbestehende Sperren

Weiterhin gesperrt bleiben:

- reale Bindungskonstruktion;
- jeder reale Aufruf von `_execute_private_runtime_fixation(...)`;
- jeder reale Ablaufkoordinatoraufruf;
- Fixierung und Minimaltest;
- Runtime, Runner, Integrator, Hook und Executor;
- Public-AV und realer Weltkontakt;
- Produktionsschalter und automatische Ausfuehrung;
- persistente Zustandsaenderung und Ausdruckskanaele.

Die Beschreibung genau eines spaeter moeglichen Aufrufs ist keine Erlaubnis, diesen Aufruf jetzt vorzunehmen.

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
coordinator_handoff_release: false
minimal_test_release: false
```

`minimal_test_release_recommended: false`

## 11. Entscheidung zu Huerde B

Huerde B ist mit diesem Dokument rein vertraglich vorbereitet. Sie ist erst nach unabhaengiger statischer Review dokumentarisch abgenommen.

Aus einer positiven Review folgt keine Freigabe fuer eine Implementierung, einen Prozessstart, eine Bindung, einen Handoff, eine Fixierung, einen Minimaltest oder eine Runtime. Der einzige zulaessige naechste Schritt ist die unabhaengige statische Review von Dokument 194.

## 12. Aussagegrenze

Kein Inhalt dieses Dokuments ist ein Befund zu Feldwirkung, Kontaktgeschichte, Memory, Organisation, Bedeutung, Semantik, Bewusstsein, Eigenstaendigkeit oder KI.

## 13. Zielbezug

Es besteht keine erkennbare Zielabweichung. Der Vertrag begrenzt nur einen moeglichen technischen Einmallauf und programmiert weder Erinnerung noch Bedeutung, Zielverhalten oder Topologie vor.

## 14. Auftrag fuer die unabhaengige statische Review

Die Review muss mindestens bestaetigen:

- alle vier eingebetteten SHA-256-Digests stimmen;
- genau ein spaeterer Prozessstart ist beschrieben;
- genau eine Bindungskonstruktion, ein Handoff-Aufruf und ein darunterliegender Ablaufkoordinatoraufruf sind beschrieben;
- jeder zweite Aufruf, Retry, Neustart und jede automatische Fortsetzung sind gesperrt;
- Parallelitaet, Nebenlaeufigkeit, Subprozesse, Threads und asynchrone Tasks sind gesperrt;
- erfolgreicher und fehlerhafter Prozessabschluss sind getrennt, ohne konkrete Ausfuehrung freizugeben;
- kein ausfuehrbarer Befehl, Runner, Executor oder CLI-Einstieg ist freigegeben;
- der Freigabeblock enthaelt genau zwoelf `false`- und kein `true`-Feld;
- `minimal_test_release_recommended: false` ist gesetzt;
- `git diff --check` meldet keine neuen Whitespace-Fehler.

Die Review darf keine Implementierungs-, Test-, Runtime- oder Exportdatei aendern, keine Projektmodule importieren oder ausfuehren, keine reale Bindung erzeugen und keine Handoff-, Fixierungs- oder Runtime-Funktion aufrufen.
