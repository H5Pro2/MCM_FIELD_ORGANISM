# S2-UC: Vorabbindung des kleinen Quellenvergleichs

## Aktueller Stand: M1–M5 implementiert und technisch geprüft, Reallauf gesperrt (2026-09-30)

Das Paket M1–M5 ist als **s2uc.productive.v1** durch den Projektleiter im geprüften
Implementierungs- und Testumfang abgenommen. **226/226 PASS** auf endgültigem Code: sämtliche bisherigen 207 Prüfpflichten
plus 19 neue Prüfungen Q1–Q7, keine Fehler, Fehlschläge oder Skips, Exit 0.
Code und Laufzeit blieben während der Vollprüfung unverändert. Die begrenzte
P2-Projektleiterabnahme bleibt bestehen. Die begrenzte Paketabnahme ist keine
unabhängige Gesamtabnahme und keine Freigabe realer Ausführung.
Belege: [Abschlussbericht](../reports/s2uc/p3-implementation-20260930-01/REPORT.txt),
[Einzelresultate](../reports/s2uc/p3-implementation-20260930-01/test-result.json) und [Prüfprotokoll](../reports/s2uc/p3-implementation-20260930-01/protocol.json).

Vier zusätzliche Dateien ergänzen produktive Zulassung, intern gebundenen
Originalsupplier, exklusiven persistenten Verbrauch vor Prozessstart und getrennte
Produkt-/Herkunftsleser. Die Autorität muss unabhängig vom Freigabedokument im
festen, administrativ geschützten Windows-Register bestätigt sein. Testzulassungen
werden vom öffentlichen Einstieg abgewiesen. **Keine operative Autorisierung wurde
erzeugt, kein Originalquellenlauf ausgeführt; die vier realen Ablagen sind unbenutzt.**
Der gespeicherte Originalhash-Negativfall endet vor Rezeptor und NJ als `NOT_EVALUABLE`;
ein erfolgreicher Originalquellenlauf wird aus Ersatzproduktion nicht behauptet.

Die endgültige Fassung umfasst **76 Dateien / 978.115 Byte**. Gemeinsame gemessene
Schlussbilanz einschließlich Bericht: **1.973.225 / 4.194.304 Byte**;
prospektive Abschlussreserve: **2.707.220 / 4.194.304 Byte**. Sämtliche P2-Teilgrenzen
bleiben unverändert. Dies ist eine Testpaketbilanz, keine Vorausmessung eines Reallaufs.
640 MiB begrenzen ausschließlich den Produktkindprozess.
Belege: [Code-/Laufzeitinventar](../reports/s2uc/p3-implementation-20260930-01/inventory.json),
[gemeinsame Bilanz](../reports/s2uc/p3-implementation-20260930-01/ledger.json) und [historische Integrität](../reports/s2uc/p3-implementation-20260930-01/preservation.json).

**Operative Fortsetzung: Benutzerzustimmung durch den Projektleiter übermittelt;
Einrichtung an fehlenden administrativen Rechten blockiert.** Die aktuelle Sitzung
hat keinen aktivierten Administratortoken. Bereits das Öffnen von HKLM64\SOFTWARE
mit dem Recht KEY_CREATE_SUB_KEY wird mit Windows-Fehler 5 (Zugriff verweigert)
abgewiesen. Kein Registry-Schreibzugriff wurde ausgeführt; alle drei Schlüssel fehlen.
Beleg: [Rechte- und Bindungsprüfung](S2UC_ADMINISTRATIVE_RECHTE_20260930.json).
Die 76 Code-/Laufzeitbindungen, 48 Qualifikationsdateien, Quellenbindungen und Bilanz
sind erneut lesend bestätigt; alle vier realen Ablagen bleiben unbenutzt. Keine
operative Autorisierung, kein Claim und keine Quellenproduktion wurden erzeugt.
Die Zustimmung wird nicht erneut angefordert. Nächster Schritt ist eine regulär
administrativ berechtigte Ausführungsumgebung für die bereits genehmigte Einrichtung;
danach Vorprüfung und genau ein Versuch gemäß dem übermittelten Auftrag.
Das [begrenzte Einrichtungsskript](Setup-S2UCRegistry.ps1) und sein
[dokumentierter Aufruf samt Prüfgrenzen](S2UC_REGISTRY_EINRICHTUNG_AUFRUF_20260930.txt)
liegen vor. Im vorhandenen PowerShell-7.6.5-Host unter unverändertem `RemoteSigned`
sind Selbstprüfung einschließlich nativer SDDL-Konvertierung und lesender Prüfung
praktisch bestanden. Der Installationsaufruf stoppt ausschließlich am fehlenden
Administratortoken. Der genaue reguläre UAC-Aufruf steht in der Aufrufdatei;
[Kompatibilitätsbeleg](S2UC_POWERSHELL7_KOMPATIBILITAET_20260930.json).
Keine Richtlinienänderung oder Umgehung, keine Registry-Anlage und kein Verbrauch.
Nach UAC-Einrichtung muss zusätzlich der unveränderte produktive ACL-Leser zustimmen.

**Aktueller UAC-Startbefund:** Der genehmigte administrative Start wurde ausgeführt,
aber Windows meldete „Der Vorgang wurde durch den Benutzer abgebrochen“.
Der Installer wurde nicht gestartet; ein Installations-Exitcode liegt nicht vor.
Alle drei Registry-Schlüssel fehlen weiterhin. Die unabhängige Vorprüfung war gültig;
keine Autorisierung, kein Claim und kein Quellenversuch wurden erzeugt.
[Abbruchbeleg](S2UC_UAC_START_20260930.json). Kein automatischer erneuter Start.
Fortsetzung benötigt einen erfolgreichen regulären UAC-Start der Einrichtung;
die übermittelte fachliche Zustimmung wird nicht erneut angefordert.

## Abgenommene P2-Basis (2026-09-30)

Der Projektleiter hat den **P2-Testanschluss einschließlich Anschlusskorrektur
im genehmigten Testumfang abgenommen**. Dies ist eine begrenzte Projektleiterabnahme,
keine unabhängige Gesamtabnahme, keine formale Laufqualifikation und keine Freigabe
realer Ausführung. **207/207 PASS** (203 bestehende plus vier Anschlussprüfungen),
keine Fehler, Fehlschläge oder Skips, Exit 0, unveränderter Code während der Prüfung.
Belege: [Korrekturbericht](../reports/s2uc/p2-supplier-correction-20260930-01/REPORT.txt),
[Einzelresultate](../reports/s2uc/p2-supplier-correction-20260930-01/final/test-result.json) und
[gebundenes Protokoll](../reports/s2uc/p2-supplier-correction-20260930-01/final/protocol.json).

Nachgewiesen sind 58 tatsächliche Aufrufe des vorhandenen gebundenen NU-Suppliers
über 58 Aufrufe der ersetzten PCM-Produktionsschnittstelle, acht vorher abgewiesene
falsche Endpunkte und sieben Herkunftsauswertungen. **Null reale Produktionsaufrufe**;
NU-Identitäten mit Test-PCM bleiben Testbefunde. Produktabschluss und Herkunftsnachtrag
bleiben getrennt; die ursprünglichen Produktdateien bleiben bytegleich.
Belege: [Supplierbeobachtung](../reports/s2uc/p2-supplier-correction-20260930-01/final/retained-success/observer/facts.json) und
[Nachtragsabschluss](../reports/s2uc/p2-supplier-correction-20260930-01/final/retained-success/appendix/appendix-terminal.json).

Die abgenommene P2-Codefassung umfasst **72 Dateien / 926.690 Byte**.
Die geschlossene P2-Testbilanz beträgt 2.290.197 Byte insgesamt, davon 77.369 Byte
für Produktverifikation und Herkunftsnachtrag gemeinsam. Diese Bestandswerte sind
keine Vorausbilanz eines Reallaufs. Die 640-MiB-Jobgrenze gilt ausschließlich für
den Produktkindprozess, nicht für Elternprozess oder Herkunftsauswertung.
Belege: [Codeinventar](../reports/s2uc/p2-supplier-correction-20260930-01/final/inventory.json) und
[geschlossene Ressourcenbilanz](../reports/s2uc/p2-supplier-correction-20260930-01/final/ledger.json).

Der [geprüfte, nicht ausführbare Freigabeentwurf](S2UC_FREIGABEENTWURF_NACH_P2_20260930.txt) trennt vorhandene
P2-Nachweise, noch notwendige Implementierung und spätere ausdrückliche Laufentscheidung.
Der damalige Folgeauftrag M1–M5 ist umgesetzt und technisch geprüft; die aktuelle
Prüffassung und die jetzt anstehende Projektleiterentscheidung stehen oben.

## Historischer Stand: V9 neutral abgeschlossen, Regressionslücke geschlossen (2026-09-30)

Die folgenden Angaben einschließlich damaliger offener Abnahmen und Bytegrenzen
sind historische Befunde. Für den aktuellen Auftrag gilt die P2-Einordnung oben.

Der vollständige neutrale Ablauf vom begrenzten V9-Produkteinstieg bis zum
getrennt gespeicherten Herkunftsbericht ist im beauftragten Entwicklungsumfang
**abgeschlossen**. Produktabschluss und Nachtragsstatus bleiben getrennt;
Record, Produktverifikation und Produktterminal bleiben bytegleich erhalten.
Beleg: [Abschlussbericht](../reports/s2uc/provenance-appendix-repeat-20260929-01/REPORT.md).

Der Anschlusscheck vom 29.09.2026 besteht mit **79/79**: 70 bestehende und
neun neue Prüfungen. Die damals darin nicht wiederholten **105 bestehenden
Prüfpflichten wurden am 30.09.2026 mit 105/105 PASS ergänzend ausgeführt**.
Beide Gruppen weisen keine Fehler, Fehlschläge oder Skips auf, jeweils Exit `0`.
Damit liegen **184 unterschiedliche PASS-Nachweise aus zwei getrennten
Ausführungen ohne Überschneidung** vor. Der Codebestand ist für beide Gruppen
identisch und unverändert; die bisherigen Ergebnisse bleiben erhalten.
Der Ergänzungsauftrag ist durch den Projektleiter abgenommen und die benannte
Regressionslücke geschlossen. Dies ersetzt weder die unabhängige Gesamtabnahme
noch eine formale Laufqualifikation oder eine Freigabe des Realstarters.
Belege: [79 Test-IDs und Resultate](../reports/s2uc/provenance-appendix-repeat-20260929-01/test-result.json),
[zugehöriges Testprotokoll](../reports/s2uc/provenance-appendix-repeat-20260929-01/unittest.log),
[Ergänzungsbericht vom 30.09.2026](../reports/s2uc/regression-105-20260930-01/REPORT.txt),
[105 Einzelresultate](../reports/s2uc/regression-105-20260930-01/test-result.json)
und [vollständige Zuordnung aller 184 Prüfpflichten](../reports/s2uc/regression-105-20260930-01/coverage-184.json).

Die frischen synthetischen Nichtnull-Fixtures zeigen **einen Erhaltungsgewinn
bei g1/24** sowie **drei getrennte Verluste bei g1/26, g2/38 und g3/67**.
Diese Befunde werden weder verrechnet noch auf reale Quellen oder eine allgemeine
Überlegenheit übertragen. Bei g3/69 rufen beide Arme B richtig ab; dies ist kein
kompensierender Gewinn. Die Herkunftsbelege stehen im
[gespeicherten Sieben-Hint-Bericht](../reports/s2uc/provenance-appendix-repeat-20260929-01/cases/1/appendix/provenance.json).

**g1/24 bleibt ein offener Erwartungswiderspruch:** Die unveränderte alte
TW-Erwartung lautet `ABSTAIN_AMBIGUOUS_RETAINED_TRACE`; tatsächlich ergibt die
synthetische Gegenprobe `ABSTAIN_NO_RETAINED_TRACE`. Die alte Erwartung bleibt
verletzt und wird separat von der Herkunftsauswertung berichtet. Die historische
Entscheidungsauswertung wird dadurch nicht nachträglich korrigiert; die belegten
Herkunftsgewinne und -verluste stehen im getrennten Nachtrag.

Die **unterschiedliche Speicheraufteilung** bleibt eine Grenze der
Ursacheninterpretation: TW besitzt zwei Erhaltungsslots, UA einen Kandidaten-
und einen Erhaltungsslot. Die Befunde isolieren daher nicht allein die Wirkung
der Bestätigung.

Der vollständige Codebestand umfasst **62 Dateien mit 851.840 / 851.968 Byte**;
es bleiben **nur 128 Byte frei**. Produktverifikation und Herkunftsbericht
belegen gemeinsam **77.760 / 131.072 Byte**. Das sind Artefakt-/Quellbytekonten,
keine Prozessspeichermessung. Belege:
[vollständiges Codeinventar](../reports/s2uc/provenance-appendix-repeat-20260929-01/dependency-inventory.json)
und [gemeinsame Budgetrechnung](../reports/s2uc/provenance-appendix-repeat-20260929-01/success-budget.json).

Die Windows-Job-Commitgrenze von **640 MiB gilt ausschließlich für den
Produktkindprozess**. Die nachgelagerte Herkunftsauswertung im Elternprozess
ist davon **nicht erfasst**. Eine Begrenzung des gesamten Ablaufs wird nicht
behauptet.

**Unabhängige Abnahme offen; reale Quellen und realer Starter weiterhin
gesperrt.** Die nächste fachliche Entscheidung betrifft die **Abnahme des
abgeschlossenen neutralen Gesamtstands**, keinen weiteren Ausbau seiner
technischen Hülle. Aus diesem Dokumentationsstand folgt weder ein neuer
Implementierungs-/Testauftrag noch eine Grenzerhöhung oder Lauföffnung.

## Historische Stände und Bindungen (unverändert überlieferte Befunde)

Alle nachfolgenden Abschnitte sind historische Zeitstände. Ihre Formulierungen
„aktuell“, „aktiv“ oder „nächster Schritt“, früheren Budgets, Qualifikations- und
Auswertungsangaben sind keine heutige Freigabe oder aktuelle Gesamtbilanz.
Der damalige Stopp der untersuchten Modultrennung bleibt als historischer
Einzelentscheid erhalten; die damalige offene Ressourcenarchitekturfrage ist
für den neutralen V9-Anschluss inzwischen bearbeitet. Maßgeblich sind oben der
abgeschlossene Entwicklungsumfang und die noch offene unabhängige Abnahme.
Der historische reale S2-UC-Lauf bleibt unverändert `NOT_EVALUABLE`.

Die darunter erhaltene Vorabbindung beschreibt unter anderem reale NU-IDs
und ältere Erwartungen; sie belegt keine heute ausgeführte reale Quelle.
Ihre frühere Aussage über ausgegebene Kandidatengewinne/-verluste ist kein
rückwirkender Herkunftsnachweis der alten Entscheidungsauswertung. Maßgeblich
für den aktuellen synthetischen Befund ist ausschließlich der oben verlinkte
separate Herkunftsnachtrag.

## Historischer Stand V6: S2-UC-Zulassung gesperrt, untersuchte Modultrennung beendet (2026-09-20)

Die Zulassungskorrektur ist mit **57/57 neutralen Entwicklungstests**, Exitcode
`0`, belegt. Die **unabhängige Abnahme bleibt offen**; dies ist keine formale
Gesamtqualifikation und keine Hauptlauffreigabe.
Belege: [Entwicklerbericht](../reports/s2uc/v6-admission-development-20260920-155753/REPORT.md)
und [Test-IDs, Ergebnisse und Hashbindungen](../reports/s2uc/v6-admission-development-20260920-155753/test-result.json).

Der bestehende reale Einstieg bleibt wegen der vollständigen Quellbytebilanz
**gesperrt**: 29 Projektdateien mit 477.802 Byte überschreiten die unveränderte
Reserve für aktive Bindungen (131.072 Byte) und bereits allein die Shared-Grenze
(262.144 Byte). Das ist eine Quellbytebilanz, keine Prozessspeichermessung.
Beleg: [vollständiges Abhängigkeitsinventar](../reports/s2uc/v6-admission-development-20260920-155753/dependency-inventory.json).

**STOPP für die untersuchte S2-UC-Modultrennung.** Die statische
Machbarkeitsprüfung ist mit negativem Befund abgeschlossen; es erfolgt keine
Umsetzung, kein Teilumbau und keine weitere Optimierungsrunde auf diesem Weg.
Das vollständigere, ausdrücklich modellierte aktive Budget liegt bei 140.838
Byte und damit 9.766 Byte über der Reserve, selbst bei kostenlos angenommener
Rezeptorentkopplung. Beleg: [abschließender Machbarkeitsentscheid](../reports/s2uc/final-split-feasibility-20260920-163154/DECISION.md).
Diese Entscheidung betrifft diesen technischen Umbau, nicht die MCM-KI oder
die fachliche Frage nach dem Nutzen wiederholter Wahrnehmungsbestätigung.

Der historische S2-UC-Lauf bleibt unverändert **NOT_EVALUABLE**. Historische
Abschnitte, Bindungen und Ergebnisse bleiben erhalten; ihre damaligen
Aufträge oder Freigaben begründen keinen heutigen Ausführungsauftrag.

Die nächste offene Architekturfrage lautet: **Wie lässt sich der fachliche
Vergleich unter einer tragfähigen, ausdrücklich begründeten Ressourcenarchitektur
durchführen?** Dazu besteht noch kein Umsetzungs- oder Laufauftrag. Die nächste
Architekturentscheidung liegt beim Projektanalysten. Die nachfolgenden älteren
Standseinordnungen sind im Licht dieses aktuellen Abschlussstands zu lesen.

Stand: 2026-09-20. Dieses Dokument bindet nur einen künftigen Vergleich. Es
erzeugt keine PCM-Daten, führt keine Rezeptor-/NJ-Verarbeitung aus und startet
keine Memorygeschichte.

## Vergleichsarme und Quellenherkunft

Beide Arme erhalten pro Ereignis denselben genau einmal materialisierten
Halbprofilendpunkt. Der unmittelbare Arm ist unverändertes S2-TW mit zwei
Retained-Slots; der private Arm ist S2-UA mit einem Bildungs-, Kandidaten- und
Retained-Platz. Es gibt keine weitere Regel, keine Schwelle und keine
Quellenauswahl im Arm.

Die Quellen werden ausdrücklich wiederverwendet:

| Symbol | unveränderte Quellen-ID | Verwendung |
| --- | --- | --- |
| `a` | `nu-s02-w00` | erster Wert der Folge A |
| `b` | `nu-s02-w01` | zweiter Wert der Folge A |
| `c` | `nu-s02-w02` | dritter Wert der Folge A |
| `d` | `nu-s02-w03` | vierter Wert der Folge A |
| `e` | `nu-s02-w04` | abweichender vierter Wert der Folge C |

Die Planwurzel ist unverändert
`6e64fbd5b7e86f16156b6d68bd5f7dbda3fefa8f223b2a31114bf3293eaa5f10`,
der gebundene Execution-Digest
`1d2787da42fe01e6bb960ad545bcfbf96a3e4abd036ce91033b325c450d7f2c7`.
Vor einer späteren Ausführung müssen die vorhandenen Quellreihen samt
Payloadhash, Profil, nativem Fenster und NJ-Snapshotindex erneut als eigene
S2-UC-Manifestbindung referenziert werden. Die Wiederverwendung ist keine
erneute Vorversiegelung und keine Deduplizierung: Jede Ereignisverwendung wird
einzeln materialisiert, aber ihr Ergebnis wird innerhalb dieses Ereignisses an
beide Arme weitergereicht.

Die Auswertungsnamen sind ausschließlich:

```text
A = a b c d
B = d c b a
C = a b c e
```

Sie sind nicht Teil des Quellen-, Rezeptor- oder Speicherpfads.

## Drei frische Geschichten

Jede Geschichte startet beide Arme mit neuen Ownern und leerem Zustand. Die
technischen Segmentkennungen `p1`, `p2` und so weiter ordnen nur Formation und
Close; sie gehen nicht in Gleichheit oder Hintentscheidung ein.

| Geschichte | gebundene Folge | read-only Hintzeitpunkte und Erwartungen, getrennt je Arm |
| --- | --- | --- |
| G1: Erhaltung und Verlust | `A -> A -> H(b,c) -> B -> C -> H(c,d) -> H(d,c)` | Nach zweitem A: beide Arme finden A über `b,c`. Nach C: S2-TW enthält B/C und enthält sich bei `c,d`; S2-UA erhält A und trifft `c,d`. Bei `d,c` trifft S2-TW B, S2-UA enthält sich, weil B nur Kandidat war und C ihn ersetzt hat. |
| G2: Unterbrechung | `A -> B -> H(b,c) -> A` | Vor der zweiten A-Aufnahme trifft S2-TW A über `b,c`; S2-UA enthält sich, weil A durch B als Kandidat ersetzt wurde. Die nachfolgende A-Aufnahme ist nur neuer Kandidat, kein nachträglicher Abruf. |
| G3: zweite bestätigte Konkurrenz | `A -> A -> B -> H(c,d) -> B -> H(c,d) -> H(d,c)` | Vor dem zweiten B trifft A in beiden Armen über `c,d`. Nach bestätigtem B behält S2-TW A und B; S2-UA ersetzt A durch B. Danach enthält sich S2-UA bei `c,d`, während beide Arme B über `d,c` finden. |

Die Hintpaare sind absichtlich nicht aus gemeinsamen Einzelwerten als
eindeutig abgeleitet. Sie werden nach der bestehenden positionsbezogenen
Zweiframe-Regel gegen alle retained Spuren und alle drei Offsets geprüft.
Mehrdeutigkeit und Enthaltung sind reguläre Auswertungsergebnisse.

Vor jeder Hintaufnahme gilt zwingend:

```text
Inventar und Generationen sichern
-> Hint read-only ausführen
-> vollständige Speicherinhalte unverändert bestätigen
-> erst danach eine mögliche nächste Formation aufnehmen
```

Kandidaten sind für Hints nicht zugänglich. Kein Hint kann Kandidaten fördern,
retained Spuren verjüngen oder eine noch nicht abgeschlossene Formation
mitlesen.

## Vorab gebundene Ereignisform

| Geschichte | Ereignisse | Formationen | Hintframes / Entscheidungen | Segmentcloses | Audio-/NJ-Endpunkte |
| --- | ---: | ---: | ---: | ---: | ---: |
| G1 | 26 | 16 | 6 / 3 | 4 | 22 |
| G2 | 17 | 12 | 2 / 1 | 3 | 14 |
| G3 | 26 | 16 | 6 / 3 | 4 | 22 |
| Gesamt, drei frische Zustände | 69 | 44 | 14 / 7 | 11 | 58 |

Jede einzelne Geschichte bleibt unter den bekannten Einzelgrenzen der
S2-TW-Form (`<= 28` Ereignisse, `<= 20` Formationen und `<= 22`
Audio-/NJ-Endpunkte). Die Summe von 69 Ereignissen ist **keine** zulässige
Einzelruntime: sie beschreibt drei getrennte, frisch gebundene Geschichten.
Eine spätere Ausführungsbindung muss ihre gemeinsame Artefakt- und
Verifikationsbilanz zusätzlich ausweisen und darf die feste S2-TY-Laufhülle
nicht wiederverwenden.

## Arbeits- und Artefaktgrenzen

Pro Arm bleiben höchstens zwölf produktive Traceframes erlaubt:

| Anteil | S2-TW | S2-UA |
| --- | ---: | ---: |
| retained | 8 Frames | 4 Frames |
| Kandidat | 0 Frames | 4 Frames |
| bildende Formation | 4 Frames | 4 Frames |
| Traceframes gesamt | 12 Frames | 12 Frames |
| Hintbuffer, getrennt | 2 Frames | 2 Frames |

Ein Halbprofilframe hat 48 Binary64-Werte, also 384 native Wertebytes. Damit
liegen die produktiven Tracewerte pro Arm bei höchstens 4.608 Byte. Die
Hintwerte, der aktuell eine materialisierte NJ-Endpunkt, der PCM-Puffer, die
Rezeptor-/FFT-Arbeitsräume, Receipts, Übergangs- und Verifikationsbelege sind
getrennte Beiträge. Die aktive Manifestbindung hat den Digest
`a357979bf70dd6b90b0db9c7f3098e8b28fbb612e10792dcb588c6fe29062fca` und
`24.440` Byte. Die gemeinsame, nicht dreifach vervielfachte Vorbilanz rechnet
Erfolgs- und Fehlerabschluss alternativ mit jeweils `245.760` Byte Record,
`131.072` Byte Verifikation, `131.072` Byte aktiven Bindungen und `16.384`
Byte terminaler Hülle. Die Reserve ist damit größer als die gemessene neutrale
Erfolgsform (`221.622` Byte), bleibt aber innerhalb der unveränderten
Recordgrenze (`262.144` Byte). Keiner der alternativen Zweige verletzt
Metadaten (`65.536`), Shared (`262.144`), Record (`262.144`), Verifikation
(`262.144`) oder Gesamt (`4.194.304`) Bytes.

Die Bilanz ist eine Anschlussreserve, keine Garantie für eine spätere reale
Ausgabe. Der fest auf 26 S2-TY-Ereignisse geformte Ledger bleibt ungeeignet.

## Unabhängige Nachrechnung und Auswertung

Für jede Geschichte sind vorab getrennt auszuweisen:

- sämtliche Übergangsreceipts mit Aktion, Kandidaten-/Retained-Generation,
  Ersetzung und Inventar;
- vollständige Speicherinhalte vor und nach jedem Hint;
- alle Hintentscheidungen und alle passenden Retained-Offsets;
- Erhaltungsgewinn für A, Verlust der einmaligen B-Erfahrung,
  Unterbrechungsverlust und Ersetzung von A durch bestätigtes B.

Die vorhandene S2-UA-Direktnachrechnung kann die Kandidatenregel erneut
unabhängig prüfen. Der S2-UC-spezifische Manifestbinder, der dreigeschichtige
Orchestrator, die unabhängige Verifikation, der gemeinsame Ledger und der
dateigebundene, standardmäßig geschlossene Einstieg sind implementiert. Der
Einstieg akzeptiert erst eine zukünftig separat gebundene
Materialisierungsfunktion; er öffnet sein Gate nicht selbst. Reale
Quellenanbindung und Hauptlauf bleiben gesperrt.

Der Einstieg ist eine gesperrte Python-Aufruffunktion, keine veröffentlichte
Datei oder Bedienoberfläche.

## Neutrale Materialisierungs- und Recordbindung

Der private Anschluss akzeptiert neben dem bisherigen neutralen 48-Werte-Tupel
den vorhandenen S2-TY-Materialisierungsreceipt. Pro Endpunkt bindet er
Payloadhash, Payloadgröße, Rohzustands-, Projektions- und Wertedigest,
Profilbindung sowie Unterlaufmarkierungen. Beide Arme erhalten aus demselben
Receipt exakt dieselben Halbwerte. Der Anschluss speichert kein PCM.

S2-UC-Records werden über eine verlustfreie, indexgebundene Frametabelle
serialisiert. Native Frames, Binary64-Werte, Profile, Owner, Segmente und
Ordinale werden beim Wiedereinlesen vollständig rekonstruiert. Die neutrale
Erfolgsform mit 58 tatsächlichen Adapterendpunkten belegt `221.622` Byte und
bleibt damit innerhalb der bestehenden Recordgrenze von `262.144` Byte.
Erfolgs- und Fehlerhüllen bleiben alternative Ledgerzweige.

Gebundener Code-/Teststand:

| Datei | SHA-256 |
| --- | --- |
| `_s2uc_neutral_connection.py` | `25138be284998b37a59661690c9d291881708b47c7eccc7101799b045ee611da` |
| `_s2uc_record_codec.py` | `f8029b43ff55a766ba26ab7e7240e83e17037e6adecb37a9b4bd97d025270290` |
| `_s2uc_verification.py` | `061b6a90ffa64b2ecd68c375fa522a9b76f99aa8c77a2146071199d0e5f07c91` |
| `_s2uc_run_entry.py` | `5018446dc42aae68b3a48838504c590dcd0069724467e765f3d0141180508bba` |
| `_s2uc_resource_ledger.py` | `0066517f028121c2548cdbb8422b7f0c481378b17d6688583c37e8e850ab8040` |
| `_s2uc_evaluation.py` | `c714addc76020f64bb6a0383a24efa4438754c89272af47a795d704c01370a85` |
| `test_s2uc_materialization_connection.py` | `1c09c54d8ff1a024610dbd929055e9b55b462d3bedd9cad85dba19e2ca731b23` |

Diese Bindung ist ausschließlich neutral qualifiziert. Reale NU-Quellen,
Materialisierungsbindung für einen Hauptlauf und fachliche Auswertung bleiben
separat gesperrt.

Der dateigebundene Einstieg publiziert `record.json` und `terminal.json`
atomar in einer zuvor fehlenden Ergebnisablage. Die technische Verifikation
liest die publizierten Recordbytes erneut ein. Bei Codec-, Budget- oder
Verifikationsfehlern entsteht nur ein terminaler Fehlerbeleg; die Auswertung
bleibt gesperrt. Der Ledger weist absolute Grenzverletzungen und getrennt
davon Reserveverletzungen aus. Die vorgebundene Auswertung zählt die sieben
Hintentscheidungen gegen die UC-Erwartungen und weist Kandidatengewinne und
-verluste getrennt aus.

Das aktive Inventar umfasst zusätzlich die tatsächlich verwendeten
S2-UA/S2-TW/S2-TU- und S2-TY/S2-NJ-Materialisierungsbausteine. Seine
gemessene Codebelegung beträgt `72.245` Byte innerhalb der gebundenen
`131.072`-Byte-Reserve. Die Dateipublikation schreibt ausschließlich in eine
vom aktuellen Aufruf neu angelegte Ergebnisablage; eine vorhandene Ablage
bleibt bytegleich unangetastet.

## Abbruchkriterium

Der Vergleich wird nicht ausgeführt, falls eine vollständige Bindung die drei
getrennten Zustände, die Einmalmaterialisierung je Ereignis, beide alternativen
Abschlussformen und alle Pflichtbelege nicht innerhalb der bestehenden Grenzen
bilanzieren kann. Es gibt keine Kürzung, Grenzerhöhung oder Übernahme der
S2-TY-Hülle. Ein späterer fachlicher Gewinn darf den Verlust von B, den
Unterbrechungsverlust oder die Ersetzung von A nicht verrechnen.

## Bestehende Anschlüsse

- [S2-TW-Quellen- und Ereignisform](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2tw_source_schedule.py:7)
- [S2-TY-Quelle-/Zeitbindung, nur als Referenz](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2ty_source_time_binding.py:31)
- [Einzelendpunkt-Materialisierung](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2ty_audio_materialization.py:46)
- [S2-UA-Kandidatenarm](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2ub_candidate_confirmation.py:83)
- [S2-UA-Direktnachrechnung](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2ub_candidate_verification.py:6)
- [S2-UC-Manifest](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2uc_source_binding.py:1)
- [S2-UC-Verbindung](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2uc_neutral_connection.py:1)
- [S2-UC-Verifikation](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2uc_verification.py:1)
- [S2-UC-Dateieinstieg](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2uc_run_entry.py:1)
