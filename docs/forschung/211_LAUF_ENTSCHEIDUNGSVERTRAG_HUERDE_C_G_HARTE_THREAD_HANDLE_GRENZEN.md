# Lauf 211: Entscheidungsvertrag Huerde C/G - harte Thread- und Handlegrenzen

## Forschungsfrage und Auftrag

Rein dokumentarisch ist zu entscheiden, ob Thread- und Handlewerte fuer die private
Einmalverkettung harte Vorabgrenzen der Huerde C bleiben oder zu nachgelagerten
Beobachtungskriterien herabgestuft werden duerfen. Daraus ist der Status von Huerde G
abzuleiten. Dieser Lauf importiert keine Projektmodule, fuehrt keine Tests aus und ruft
keinen Lauf-, Prozesswaechter-, Bindungs-, Handoff-, Fixierungs- oder Runtimepfad auf.

## Gebundene Bytebasis

| Quelle | SHA-256 |
| --- | --- |
| `docs/forschung/192_SPERR_UND_FREIGABEBEDINGUNGEN_REALE_FIXIERUNGSAUSFUEHRUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md` | `d6b9fedd7310425bff7bbdd3b9f2a778e0ede32c6074d4b68f78c8c4cede7edb` |
| `docs/forschung/195_HUERDE_C_RESSOURCEN_UND_ZEITGRENZEN_EINMALLAUF_RUNTIME_FIXIERUNG.md` | `0154a6de7e80b5db8f373878af592855dfa6a0938bd7dedf5ebea927e5ae4ca3` |
| `docs/forschung/204_ERNEUTE_HUERDE_C_RESSOURCEN_UND_ZEITGRENZEN_PRIVATE_EINMALVERKETTUNG.md` | `ec0cead77a18d2b3ca0ba1caca43c0baf96d5af269ea8512fe72ff4823018671` |
| `docs/forschung/209_LAUF_KORREKTURPLAN_HUERDE_G_RESSOURCENWAECHTER_PROZESSVERTRAG_ARTEFAKTKONTROLLE.md` | `b3a0123cf1169f45895095e75fe1919c81da8e28e8efed2e6f52a01c5e6e6f5c` |
| `docs/forschung/210_LAUF_MACHBARKEITSANALYSE_WINDOWS_JOB_OBJECTS_HARTE_GRENZEN.md` | `e861ab6412df014c9775d0badb9981d4fed17135c44a50bb573ab3ab9a7b6456` |
| `mcm_field_organism/_runtime_fixation_single_use_path.py` | `44cc4dc42bea8b163531d5315e5bab5eda101b1a13f16323e2e34f0ba003787a` |
| `mcm_field_organism/__init__.py` | `c04e371daba2593d771e8ffa26e614746599f15541b303d5d5eaeaeaf332a9b0` |

Diese Bindung gilt nur fuer die statische Entscheidung dieses Dokuments. Eine
Aenderung einer gebundenen Datei macht die Entscheidung fuer eine spaetere
Ausfuehrungsbewertung neu pruefpflichtig.

## Verwendete Dateien und Schnittstellen

Verwendet wurden ausschliesslich die gebundenen Dokumente und Python-Quelldateien als
Text beziehungsweise Bytefolgen. Es wurde keine Python-, Prozesswaechter-, Job-Object-,
AppContainer-, Prozess-, Netzwerk-, Geraete-, Public-AV- oder Weltkontaktschnittstelle
aufgerufen.

## Durchgefuehrte Schritte

1. Die normative Huerde-C-Methodik aus Dokument 195 wurde gegen die erneute statische
   Huerde-C-Bewertung aus Dokument 204 abgegrenzt.
2. Die in Lauf 209 verlangten harten Thread- und Handlegrenzen wurden mit der in Lauf
   210 festgestellten Reichweite von Windows Job Objects verglichen.
3. Die Folgen einer Herabstufung auf Nachlaufkriterien wurden als Gegenbaseline
   bewertet.
4. Aus der unveraenderten Huerde-C-Methodik wurde der Status von Huerde G abgeleitet.

## Entscheidung zu Huerde C

| Kriterium | Entscheidung |
| --- | --- |
| Threadzahl | Bleibt eine harte, vor und waehrend der Fachoperation technisch zu erzwingende Grenze. |
| Offene Handles | Bleiben eine harte, vor und waehrend der Fachoperation technisch zu erzwingende Grenze. |
| Herabstufung zu Nachlaufkriterien | Abgelehnt. |
| Aenderung der Huerde-C-Methodik | Keine. Dokument 195 bleibt normativ bytegebunden. |
| Konsequenz fuer den Einmallauf | Technisch blockiert. |

Die Herabstufung wird abgelehnt, weil eine erst nachtraegliche Messung eine
Grenzverletzung bereits geschehen liesse. Sie koennte weder den geforderten Abbruch vor
weiterer Fachoperation noch eine lueckenlose Einhaltung nachweisen. Eine bessere
Ausfuehrbarkeit waere keine methodische Rechtfertigung fuer die Abschwaechung der
vorregistrierten Grenze.

Dokument 204 bereitet Ressourcen- und Zeitgrenzen statisch vor, ersetzt aber nicht die
in Dokument 195 geforderte technische Erzwingbarkeit. Daher entsteht keine geaenderte
Huerde-C-Methodik, die neu als Ersatzmethodik bytezubinden waere. Die bestehende
Methodik und ihre Bytebindung bleiben erhalten.

## Messergebnisse und Gegenbaselines

Dieser Lauf erzeugt keine Laufmesswerte. Seine statisch pruefbaren Ergebnisse sind:

- harte Threadgrenze beibehalten: `true`
- harte Handlegrenze beibehalten: `true`
- methodische Herabstufung: `false`
- Huerde-C-Methodik geaendert: `false`
- Huerde G freigegeben: `false`
- reale Ausfuehrung freigegeben: `false`

Bewertete Gegenbaselines:

| Gegenbaseline | Ergebnis |
| --- | --- |
| Polling oder reine Nachlaufmessung | Erkennt eine Verletzung nur mit Luecke oder nach ihrem Eintritt; unzureichend. |
| Windows Job Object allein | Erzwingt geeignete Prozess-, CPU- und Speichergrenzen, aber keine allgemeine harte Thread- oder Handleobergrenze; unzureichend. |
| Herabstufung der Kriterien | Erhoeht die Ausfuehrbarkeit, schwaecht aber Huerde C methodisch; abgelehnt. |
| AppContainer | Moeglicher spaeterer Isolationspfad fuer andere Ressourcenklassen, aber kein nachgewiesener Ersatz fuer harte Thread- und Handlezaehlung. |

## Huerde-G- und Freigabevertrag

Mangels eines nachgewiesenen Mechanismus fuer die harten Thread- und Handlegrenzen ist
Huerde G nicht erfuellt. Der private Einmallauf darf weder vorbereitet noch ausgefuehrt
werden.

| Freigabefeld | Wert |
| --- | --- |
| `real_operations_binding_release` | `false` |
| `real_fixation_execution_release` | `false` |
| `runtime_release` | `false` |
| `runner_release` | `false` |
| `integrator_release` | `false` |
| `hook_release` | `false` |
| `executor_release` | `false` |
| `public_av_release` | `false` |
| `production_switch_release` | `false` |
| `automatic_execution_release` | `false` |
| `coordinator_handoff_release` | `false` |
| `minimal_test_release` | `false` |

`minimal_test_release_recommended: false`

## AppContainer-Abgrenzung

Eine AppContainer-Kompatibilitaetsanalyse darf nur als spaeterer, separat freizugebender
statischer Pruefpfad betrachtet werden. Sie darf zunaechst ausschliesslich klaeren, ob
Datei-, Registry-, Netzwerk- und Geraetezugriffe des gebundenen Python-Korridors ohne
fachliche Ausfuehrung einschraenkbar waeren. Sie ist keine Thread- oder
Handlefreigabe und aendert den Sperrstatus von Huerde C/G nicht.

## Grenzen und nicht gepruefte Annahmen

- Keine Schutzfunktion wurde implementiert oder dynamisch validiert.
- Die praktische AppContainer-Kompatibilitaet des Python-Korridors ist nicht geprueft.
- Es ist kein lueckenloser Mechanismus fuer harte Thread- oder Handleobergrenzen
  nachgewiesen.
- Cache-, `__pycache__`-, Ausgabe- und Artefaktkontrollen wurden nicht ausgefuehrt.
- Es gibt keinen Befund zu Feldwirkung, Kontaktgeschichte, Memory, Organisation,
  Bedeutung, Semantik, Bewusstsein, Eigenstaendigkeit oder KI.

## Konkrete Schlussfolgerung

Thread- und Handlewerte bleiben harte Huerde-C-Vorbedingungen. Eine Herabstufung zu
Nachlaufkriterien waere eine unbegruendete methodische Abschwaechung und wird nicht
vorgenommen. Weil die erforderliche lueckenlose technische Erzwingung nicht
nachgewiesen ist, bleiben Huerde G und jede reale Ausfuehrung gesperrt.

## Naechster begrenzter Forschungslauf

Als naechster Schritt ist ausschliesslich eine unabhaengige statische Gegenpruefung
dieses Entscheidungsvertrags freizugeben. Sie muss die sieben Bytebindungen, die
unveraenderte Huerde-C-Methodik, die Ablehnung der Herabstufung, alle zwoelf falschen
Freigabefelder und die fortbestehende Ausfuehrungssperre reproduzieren. Erst danach
kann eine separate rein statische AppContainer-Kompatibilitaetsanalyse erwogen werden;
auch sie darf Huerde G nicht wieder oeffnen.

## Zielabweichung

Keine erkennbare Zielabweichung. Die Entscheidung behandelt ausschliesslich technische
Vorbedingungen eines gesperrten Forschungspfads und behauptet keine Organismusfunktion.
