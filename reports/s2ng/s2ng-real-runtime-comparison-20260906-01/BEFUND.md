# S2-NG: einmaliger realer Runtimevergleich

## Abschluss

- Lauf-ID: `s2ng-real-runtime-comparison-20260906-01`.
- Technische Aufzeichnung: `RECORDING_COMPLETE`.
- Einmalige unabhaengige read-only Gesamtverifikation: bestanden,
  `RECORDING_COMPLETE`, `evidence_valid=true`, Datei unveraendert.
- Anschliessende getrennte Funktionsauswertung: zwei neue korrekte auditive
  Abrufe; keine Fehlzulassung. Visuelle Ergebnisse unveraendert.
- Beide Runtimeinstanzen sind `CLOSED`; Hauptgate danach `False`.
- Kein Retry, kein Zusatztest, keine Rezeptorvorpruefung und keine
  nachtraegliche Quellen-, Regel-, Schwellen- oder Budgetaenderung.

Dies ist ein begrenzter Transfergewinn der auditiven A-Abrufselektivitaet.
Auditives `D=0` bedeutet weiterhin `ERHALTUNG_NICHT_GEPRUEFT`.

## Einmalige Ausfuehrung und Bindungen

Aufruf aus dem Workspace-Root, genau einmal, Exit-Code `0`:

```text
C:/Python314/python.exe -B -m reports.s2ng.run_runtime_comparison_once
```

`preregistration.json` bindet vor dem Hauptaufruf Lauf-ID, Test-/Produkt-
Quellenstand der bestandenen Qualifikation, Aufrufer, Interpreter,
Ereignisspezifikationen und Ressourcenlimits. Die Quellhashes vor und nach
dem Hauptlauf stimmen ueberein. Die qualifizierten Produktmodule und Tests
wurden fuer diesen Lauf nicht geaendert.

Die Quellenwurzel stammt unveraendert aus
`reports/s2mt/s2mt-presealed-transfer-runtime-20260906-05/result.json`:

- Datei-SHA-256:
  `2de06dfc17728fd1c9aa7793e616e5a530cbf716306431117ce9dce4325d886f`.
- Plandigest:
  `3b749837273f9cfb1af4ac50659881c48a4a113384d65999dc90e922b46fd26c`.
- Gebundener Eingangs-Skalierungsfaktor: `0.989912331104279`, bestehende
  Float32-Bindung `e56a7d3f`; keine weitere Skalierung.
- Explizite Felduhr: `s2mt-transfer-field-clock`.

Nur der Quellenplan wurde uebernommen, kein historischer Memoryzustand.
Die bestehende Materialisierung wurde einmal gemeinsam aufgerufen und gab
28 unveraenderliche Ereignisse zurueck. Die bestehenden Quellenhelfer
prueften jeden regenerierten Payloadhash vor dessen Rezeptorverarbeitung.
Keine zusaetzliche Geometriepruefung oder separate Rezeptormessreihe.
Rohpayloads wurden nicht in Ergebnisdateien gespeichert.

Die beiden getrennten Runtime-, Feld-, Memory- und Ownerinstanzen erhielten
dieselben Materialisate. Die Referenz verwendet historisches `sum(...)/24`,
nicht `statistics.mean`. Die Alternative verwendet `ALL_BANDS_24` nur fuer
auditive B4-/Fast-Anwendbarkeit. Slow, Visualpfad, Feld und Formation bleiben
unveraendert. Keine Regelwahl am Hinweis, kein Fallback und kein B-Vorrang.

## Umfang und technische Pruefung

| Groesse | Aufgezeichnet |
| --- | ---: |
| Gemeinsame Materialisierungen | 1 |
| Ereignisse pro Arm | 28 |
| Formationen pro Arm | 20 |
| Teilhinweise pro Arm | 8 |
| Feldkontakte insgesamt | 16.128 |
| Vollstaendige Scanbelege einschliesslich Direktbaselines | 32 |
| Wertvergleiche / gebundene Obergrenze | 12.544 / 21.248 |
| Atomarer Gesamtbeleg, Byte / Obergrenze | 1.452.881 / 4.194.304 |
| Unabhaengige Gesamtverifikationen | 1 |

Die Gesamtverifikation bestaetigt vollstaendige Ereignisfolge,
Baselinegleichheit, identische korrespondierende Feld-/Memoryzustaende und
read-only Hinweise. Die unveraenderten Teil- und Gesamtlimits sind in der
Vorbindung und im Gesamtbeleg enthalten. Keine Grenzerhoehung.

Beide geschlossenen Snapshots binden 28 verarbeitete Ereignisse,
20 Memoryformationsversuche, 28 Feldversuche und 16 Scanversuche.
Gemeinsamer finaler Felddigest:
`0082847646f83305b63ff8cb06a60e926d7ec4c9d6601fd53e578abaadd27d80`.
Gemeinsamer finaler Memorydigest:
`5ce6eea03e632dc649d507fd3f2343fc6a39450db28469f094945133f267cc35`.
Runtime-/Receiptbindungen bleiben armabhaengig und muessen nicht gleich sein.

## Alle acht Hinweise

A/B/C und unbekannt sind ausschliesslich Bezeichnungen des nachgelagerten
Auswerters. `ZULASSUNG` bezeichnet `ADMIT_SINGLE_CONTEXT`,
`MEHRDEUTIG` bezeichnet `ABSTAIN_INTERNAL_AMBIGUITY`,
`UNPASSEND` bezeichnet `ABSTAIN_NO_APPLICABLE_CONTEXT`.
Hypothesen werden nicht angewendet.

| Ereignis | Hinweis | Referenz | Alternative |
| --- | --- | --- | --- |
| e21 | A auditiv | MEHRDEUTIG | ZULASSUNG, korrekt, B_STABLE_AUDITORY |
| e22 | A visuell | ZULASSUNG, korrekt | ZULASSUNG, korrekt |
| e23 | B auditiv | MEHRDEUTIG | ZULASSUNG, korrekt, B_STABLE_AUDITORY |
| e24 | B visuell | ZULASSUNG, korrekt | ZULASSUNG, korrekt |
| e25 | C auditiv | MEHRDEUTIG | UNPASSEND |
| e26 | C visuell | UNPASSEND | UNPASSEND |
| e27 | unbekannt auditiv | MEHRDEUTIG | MEHRDEUTIG |
| e28 | unbekannt visuell | UNPASSEND | UNPASSEND |

Gespeicherte auditive Treffermengen, jeweils B4/Fast/stabiles Slow:

| Ereignis | Referenz | Alternative |
| --- | --- | --- |
| e21 | 9/3/1 | 0/0/1 |
| e23 | 9/3/1 | 0/0/1 |
| e25 | 9/3/0 | 0/0/0 |
| e27 | 9/3/0 | 7/3/0 |

Der B-Gewinn entsteht durch das Ausbleiben unpassender A-Treffer, nicht durch
automatische Bevorzugung von B. Die unbekannte auditive Probe bleibt wegen
A-Mehrdeutigkeit enthalten; dies ist kein Nachweis von Unbekanntheitserkennung.

## Erhaltung, Verlust und Fehlzulassung

N bezeichnet erwartete positive Kontextfaelle, D bereits richtige
Referenzzulassungen, R erhaltene und L verlorene richtige Zulassungen.
`D = R + L`; Gewinne werden nicht gegen Verluste verrechnet.

| Modalitaet | N | D | R | L | Neue richtige Abrufe | Erhaltung |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Audio | 2 | 0 | 0 | 0 | 2 | ERHALTUNG_NICHT_GEPRUEFT |
| Visual | 2 | 2 | 2 | 0 | 0 | 2/2 erhalten |

- Richtige bekannte Audiozulassungen: Referenz `0/2`, Alternative `2/2`.
- Richtige bekannte Visualzulassungen: beide `2/2`.
- Fehlzulassungen: auditiv beide `0/4`, visuell beide `0/4`.
- Enthaltungen: auditiv Referenz `4/4`, Alternative `2/4`; visuell beide `2/4`.
- Erwartete Enthaltungen bei C und unbekannt: je Modalitaet beide `2/2`.
- Verworfene Zielkandidaten: keine in den gespeicherten Auswertungszeilen;
  insbesondere keine bei den zwei positiven Audio- und zwei Visualfaellen.
- Kein beobachteter Verlust einer richtigen Zulassung. Fuer Audio ist dies
  bei D=0 ausdruecklich kein Erhaltungsnachweis; visuelle Treffer fuellen den
  auditiven Nenner nicht auf.

Die Gruppierungen nach Quellenverwendung und realer Druckkonkurrenz sowie
alle Einzelzeilen stehen unverkuerzt in `evaluation.json`. Wiederverwendete
Quellen pruefen technischen Transfer, keine unabhaengige Generalisierung.

## Tatsaechliche Memorybildung

Die 20 Formationen folgen unveraendert der literalen Rezeptfolge:

```text
n00 n01 n02 n00 n01 n02 n00 n01 n02 n00 n01
n03 n04 n05 n06 n07 n08 n09 n10 n11
```

Beide Slow-Banken enthalten abschliessend n00 und n01 mit Support 3 sowie
n02 mit Support 2. Die aufgezeichneten PPB-Zuordnungen ergeben fuer n00/n01
je drei eigene Konsolidierungseingaenge, fuer n02 zwei. Kein Druckrezept ist
in diesen Slotgenerationen enthalten. Volle Prototypdigests und die
Transitions-/Zustandsbindungen sind im Gesamtbeleg und der Auswertung
erhalten; Kandidaten wurden nicht mit urspruenglichen Rezeptorvektoren
bitgleich vorausgesetzt.

B4 enthaelt ausschliesslich Formationen 12 bis 20, also n03 bis n11.
Fast enthaelt die letzten Formationen 18 bis 20, jeweils Support 1 und
Consolidation Count 0. A/B/C sind damit aus B4 und Fast verdraengt.

## Belegintegritaet und Aussagegrenze

- Gesamtbeleg-Datei-SHA-256:
  `927013f5fd313d3e319d376561be18ba5aa04cadef66af17c7bf1000f0c1acb1`.
- Gesamtbeleg-Ergebnisdigest:
  `346f9be348e3597fc003e45ece69ecd362f817073f461b22223de9c6e1ad3dc4`.
- NG-Kompositionsdigest:
  `1ada3ab322ea7a514c426300c3ca43db87f3caccbbde05ddde0ab253ebd50740`.
- Unabhaengiger Verifikationsdigest:
  `ed2ac167cf540c02904134dc7c673a4d3ca7e8332e80241e5efe038309f231cf`.
- Nachgelagerter Auswertungsdigest:
  `0cf55669e26acbc2b575e3c0260a1d2552be1ece080010ba38f794627e7e7f50`.

Die Direktbaselines erklaeren alle Entscheidungen. Bestaetigt ist ein
begrenzter Runtime-Transfer der strengeren auditiven A-Regel, keine neue
Lernmechanik, Speicherkapazitaet, allgemeine Verlustfreiheit oder Robustheit.
Keine Produktumstellung, Hypothesenanwendung oder Feld-/Memoryrueckwirkung.
Historische Laeufe bleiben unveraendert. Fuer die Berichtserstellung wurden
nur gespeicherte Belege gelesen; keine erneute Verifikation oder Auswertung.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieses begrenzten
Runtime-Transfergewinns und einer separaten Entscheidung ueber die weitere
private Regelanbindung weiter.
