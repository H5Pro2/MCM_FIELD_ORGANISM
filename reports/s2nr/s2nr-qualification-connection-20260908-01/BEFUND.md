# S2-NR: administrative Verbundqualifikation

## Ergebnis

Lauf-ID: `s2nr-qualification-connection-20260908-01`.
Status: `S2NR_QUALIFICATION_CONNECTION_QUALIFIED`.
Genau ein neutraler Testaufruf, **4/4 bestanden**, Exit-Code `0`:

```text
C:/Python314/python.exe -m unittest tests.test_s2nr_private_qualification_binding -v
```

Der einmalige Aufruf wurde durch `python -m reports.s2nr.qualify_connection_once`
aus dem Workspace gestartet. Keine historische Qualifikation wurde wiederholt.

## Zusammengefuehrte Deckung

Der neue Beleg `reports/s2nr/combined-qualification-v1/qualification.json`
referenziert drei unveraenderte historische Beleggruppen mit Dateihashes,
Ergebnisdigests, Testinventaren, Protokollbindungen und getrennten Pruefbereichen:

| Historischer Beleg | Uebernommene Deckung | Unveraenderter Gesamtstatus |
| --- | --- | --- |
| `s2nr-runtime-binding-qualification-20260908-01` | 16/16: Typen, Masken, Isolation, Read-only und Lifecycle | `S2NR_RUNTIME_BINDING_QUALIFIED` |
| `s2nr-main-binding-qualification-20260908-01` | Nur die elf protokolliert erfolgreichen Laufpruefungen | `NOT_QUALIFIED` |
| `s2nr-main-binding-focused-qualification-20260908-01` | Drei unabhaengige Kontrollen: Fehlerfortschritt, Auswertungssperre und falsche Planwurzel | `S2NR_FOCUSED_BINDING_QUALIFIED` |

Dies ist **kein neuer vollstaendiger Testlauf**. Insbesondere bleibt der alte
11/12-Lauf fehlgeschlagen. Sein Fehlerstatus wird nicht als Haupteintrittsfreigabe
akzeptiert. Auch der fokussierte Drei-Test-Beleg allein genuegt nicht.

## Quellen- und Anschlussbindung

Die dokumentierte fruehere Testkorrektur in `tests/test_s2nr_private_run.py`
ist explizit gebunden:

- vorher: `c35a5fafbb621e008df28245b896b4659b46d21355a6995dc1d18c315a30895e`
- nachher: `c589efdaa57fcfbfd9dcf456eab47d6964723aced38962a6fb31864dba3f5ff7`

Die damaligen Produktquellen sind zwischen der Laufqualifikation und der
fokussierten Ergaenzung gleich. Die zuvor erfolgten Laufanschluesse an
Runtimebindung und Runtimeverifikation sind im Verbund separat ausgewiesen;
sie werden nicht rueckwirkend der ersten 16/16-Pruefung zugeschrieben.

Die jetzt notwendige administrative Aenderung betrifft ausschliesslich die
Qualifikationspruefung vor `load_execution()` und die zugehoerige Quellenliste
in `tools/_s2nr_private_run.py` sowie den neuen privaten Bindungshelfer.
Der Rest des Runner-AST stimmt mit Commit `519e1db2` ueberein. Diese neue
Anschlussaenderung ist ausdruecklich **nicht historisch getestet**, sondern
Gegenstand der hier dokumentierten vier Kontrollen.

- Runner vorher: `ab771819cb6d93872b9c3317bd540bf461137636ff76859060d7ea6bd09261f7`
- Runner nachher: `5712de02414fdf886a7dd08ea090ed02f03dbaeb44659c9e416edb6a191941a5`
- Digest des unveraenderten Runner-AST-Anteils: `c9031af298b09e2a552c548adfef241ba1223d82d05528dd596aa0b8cfb373fd`

Alle vorab gebundenen Quellhashes sind nach dem Aufruf unveraendert.
Der Haupteinstieg verlangt den vollstaendigen Verbund **und** den erfolgreichen
neuen Anschlussqualifikationsbeleg mit passender Quellenbindung.

## Vier Anschlusskontrollen

1. Vollstaendiger gueltiger Verbund akzeptiert.
2. Fehlender Teilbeleg: `S2NRRunError`, `QUALIFICATION_PART_MISSING`.
3. Falscher Teilbelegdigest: `S2NRRunError`, `QUALIFICATION_PART_DIGEST_INVALID`.
4. Unzulaessige Quellenabweichung: `S2NRRunError`, `QUALIFICATION_SOURCE_MISMATCH`.

Die Kontrollen verwenden den Anschlusshelfer des Haupteinstiegs. Nur dessen
noch zu erzeugender eigener Qualifikationsreceipt wurde am Leseuebergang
durch neutrale synthetische Metadaten vertreten; die historischen Teilbelege
wurden unveraendert gelesen. Der tatsaechliche neue Vier-Test-Beleg wurde erst
nach dem Testaufruf geschrieben. Es wird kein synthetischer Qualifikationsstatus
als realer Befund ausgegeben.

Aufrufsperren schlossen Materialisierung, Ausfuehrung, Quellenplanladung,
Runtimekonstruktion und Quellengeneratorzugriffe aus. Keine NR-Payloads,
Rezeptoranalysen, Memoryformationen, Feldkontakte oder Hauptausfuehrung.
Die Gates blieben `False`.

## Integritaet und Grenzen

- Verbundgroesse: **12.591 Byte**, Grenze **65.536 Byte**.
- Verbunddigest: `f9250b46a82373ea74e187f05a833cc3b1931f87675e2e0acbb6cb974834b0d3`
- Verbunddatei-SHA-256: `7401f87407a38afd4323fa170017e53ee8421ffe02ffa616514279a95cd3cba4`
- Neuer Ergebnisdigest: `454cd46591bcc1c8f8f6cc48a0da5e2c8760303f7cb6f8fd655c69371de3d215`

Die Pruefung qualifiziert die administrative Zulassung des zusammengesetzten
Nachweises, keinen realen NR-Funktionslauf. Historische Belege, Versiegelung,
fremde Aenderungen und Bootstrap bleiben unberuehrt.

**WEITER:** Den Verbund und die separat qualifizierte Anschlussaenderung dem
Analysten zur gesonderten Entscheidung ueber genau einen NR-Hauptlauf vorlegen.
Eine Hauptausfuehrung ist durch diesen Befund nicht freigegeben.
