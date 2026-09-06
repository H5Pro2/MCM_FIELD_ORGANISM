# S2-MT Lauf 05: Read-only Ursache der auditiven Mehrdeutigkeit

## Ergebnis

Die auditive Enthaltung ist durch die aktuellen A_RECENT-Abrufregeln
erklaerbar. Alle vier auditiven Hinweise passen auf den beobachteten
24 Baendern zu allen drei finalen Fast-Slots bei Schwelle 0.2. Bereits
diese digestgebundene Treffermenge erzwingt A_RECENT_INTERNAL_AMBIGUITY und
anschliessend ABSTAIN_INTERNAL_AMBIGUITY, unabhaengig vom Slow-Ergebnis.

Die Bindung der neun finalen B4-Eintraege an ihre Formation ergibt ebenfalls
neun auditive Treffer je Hinweis. Das Ziel muss dafuer nicht mehr in A_RECENT
gespeichert sein: Die verbliebenen Distraktoren reichen als Konkurrenten aus.

S2-MT Lauf 05 bleibt technisch RECORDING_COMPLETE und fachlich
S2MT_FUNCTION_FALSIFIED. Diese nachgelagerte Diagnose aendert keine Vorhersage.

## Vorhandene Evidenz

- Lauf: `s2mt-presealed-transfer-runtime-20260906-05/result.json`.
- Laufdatei-SHA-256:
  `2de06dfc17728fd1c9aa7793e616e5a530cbf716306431117ce9dce4325d886f`.
- Gespeicherte 48-Werte-Vektoren:
  `../s2mw/s2mw-audio-receptor-compatibility-20260906-02/result.json`,
  dort `scaled_outputs`.
- Auditdatei-SHA-256:
  `b1ca1ad9d11e29c6d5b547d166741f1afbf40fb3e8f240ea6eb07d3f4e7d87ef`.

Beide kanonischen Record-Digests wurden nachgerechnet. Alle 13 gespeicherten
Vektoren stimmen mit ihren Binary64-Byte-Digests ueberein. Ihre
PCM-Eingangsdigests stimmen mit den 13 Rezepten des im Lauf gespeicherten
skalierten Quellenplans ueberein. Die bekannte falsche interne S2-MW-Audit-ID
wird nicht korrigiert; die Zuordnung verwendet Dateipfad, Datei-/Recorddigest
und die konkreten Payloadbindungen.

Alle 14 im Lauf gebundenen Quellhashes entsprechen den gelesenen Dateien.
Die Untersuchung importierte keine Projektmodule und rief keine Rezeptor-,
Memory-, Scan-, Kontext-, Feld-, Runtime- oder Projektverifikatorfunktion auf.
Es wurden nur vorhandene JSON-Werte geparst, gehasht und arithmetisch verglichen.
Es gab keinen erneuten Versuchs- oder Qualifikationslauf.

## Slotbindung

Nach Formation 20 bleiben folgende Fast-Slots besetzt:

| Fast-Slot | Rezept | Letzte Formation | Support |
| --- | --- | ---: | ---: |
| 000 | n10 | 19 | 1 |
| 001 | n11 | 20 | 1 |
| 002 | n09 | 18 | 1 |

Die kanonischen JSON-Digests der gespeicherten Audio-Vektoren stimmen exakt
mit den `auditory_values_digest`-Feldern dieser drei Laufslots ueberein.
Dies ist eine Zuordnung vorhandener Werte, keine Rueckrechnung aus Digests.

B4 enthaelt Formationen 12 bis 20, also n03 bis n11. Fuer jeden Eintrag
stimmt der finale Eintragsbeleg mit dem direkt nach seiner Formation
aufgezeichneten Beleg ueberein. Der jeweils neue Fast-Geschwisterslot hat
Support 1 und den passenden auditiven Vektordigest. Die gelesene
Koordinatorregel uebernimmt fuer B4 denselben AV-Eingang unveraendert.
Damit sind die B4-Audiodistanzen ueber Formation und Geschwisterbindung
ableitbar; separate 48-Werte-B4-Payloads wurden im Lauf nicht gespeichert.

Alle acht Hinweise behalten den finalen Memory-Zustandsdigest bei.

## Nachgerechnete auditive Distanzen

Die Berechnung verwendet die Produktionsform
`sum(abs(candidate[i] - cue[i]) for i in range(24)) / 24`.
Der auditive B4-/Fast-Scan verwendet 0.2, der Slow-Scan 0.02.

| Hinweis | Rolle | B4-Minimum | B4-Maximum | B4-Treffer | Fast-Distanzbereich | Fast-Treffer |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| e21 / n00 | A | 0.0591329255 | 0.1024846237 | 9/9 | 0.0591329264 bis 0.0591329291 | 3/3 |
| e23 / n01 | B | 0.0489846348 | 0.0923362816 | 9/9 | 0.0489846414 bis 0.0489846450 | 3/3 |
| e25 / n02 | C | 0.0441341018 | 0.0874855860 | 9/9 | 0.0441341226 bis 0.0441341262 | 3/3 |
| e27 / n12 | unbekannt | 0.0000016468 | 0.0433533896 | 9/9 | 0.0000016468 bis 0.0000016470 | 3/3 |

Die kleinste Reserve unter 0.2 betraegt ueber diese Beziehungen
0.09751537628952471. Es handelt sich nicht um eine Gleitkomma-Grenzentscheidung.
Die zwoelf gespeicherten Cue-zu-Lerninhalt-Distanzen stimmen mit der
Nachrechnung bis maximal 4.17e-17 ueberein; der Unterschied stammt aus der
Summationsreihenfolge. Alle Selbstabstaende bleiben exakt null.

## Ursache der falschen Transferprognose

Im Runner prueft `_geometry` die Vollvektortrennung der Formationsrezepte
mit der AV-OR-Trennregel. Fuer auditive Teilhinweise prueft es dagegen nur
n00/n01/n02 und verwendet dabei die Slow-Schwelle 0.02. Die neun spaeteren
Distraktoren unter der auditiven A-Schwelle 0.2 werden in dieser Cue-Pruefung
nicht untersucht. Deshalb ist S2MT_GEOMETRY_MATERIALIZED mit einer spaeteren
auditiven A-Mehrdeutigkeit vereinbar.

Die Produktionsfunktion `_resolve_a` erzeugt bei mehreren Treffern in
einer internen Bank A_RECENT_INTERNAL_AMBIGUITY. `_decide` enthaelt sich
dann, bevor eine eindeutige oeffentliche Quelle zugelassen werden koennte.
Die unabhaengige Direktbaseline besitzt dieselbe fachliche Regel.

Die Formationsbedingung fuer AV-Trennung, die Slow-Stabilitaet und die
Eindeutigkeit eines auditiven Teilhinweisabrufs sind somit verschiedene
Bedingungen. Support 3 und Verlust des Originalinhalts aus A_RECENT
garantieren keine eindeutige auditive Hypothese unter Distraktorkonkurrenz.

## Aussagegrenzen und naechster Schritt

Der Lauf speichert Scan-Receiptdigests, aber keine vollstaendigen internen
Scantabellen. Die Fast-Treffermengen wurden aus digestgebundenen vorhandenen
Vektoren abgeleitet; sie werden nicht als nachtraeglich wiederhergestellte
Originalreceipts bezeichnet.

Die finalen Slow-Prototypwerte fehlen ebenfalls. Ihre Digests sind nicht
bitgleich zu den gespeicherten Originalrezeptorvektoren. Es wurde weder ein
Slow-Zustand nachgebildet noch ein genauer finaler Slow-Abstand behauptet.
Die nachgewiesene Fast-Mehrdeutigkeit erklaert die Enthaltung bereits allein.

Die passenden Enthaltungen fuer C und den unbekannten Hinweis belegen hier
keine spezifische Erkennung von Instabilitaet oder Unbekanntheit: Beide
laufen in dieselbe A-Mehrdeutigkeitsregel wie A und B.

Der aktuelle Transfervergleich ist mit falsifizierter Gesamtvorhersage
abgeschlossen. Ein weiterer identischer Hauptlauf hat keine neue Gegenprognose.
Die naechste fachliche Frage betrifft die Selektivitaet des auditiven
Teilhinweisvergleichs unter Konkurrenz. Ein prospektiver Vergleich muss
Lerninhalte, belegte A-Distraktoren, unbekannte Hinweise und fehlende
Spektralinformation gemeinsam beruecksichtigen. Dieser Befund waehlt keine
neue Schwelle, Maskierung oder Bevorzugung von B_STABLE.
