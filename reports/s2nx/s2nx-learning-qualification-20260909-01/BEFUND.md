# S2-NX: neutrale Zwei-Lerner-Anbindung qualifiziert

Lauf-ID: `s2nx-learning-qualification-20260909-01`.
Status: **S2NX_LEARNING_QUALIFIED**, **32/32**, Exit-Code `0`.
Genau ein vorab gebundener Testaufruf, kein Retry. Alle 32 Testkoerper
wurden laut [Testprotokoll](stderr.txt) erreicht. Inventar, Quellhashes,
Umgebung und Budgets stehen in [preregistration.json](preregistration.json).
Die [Vorversiegelung](../s2nx-source-preseal-20260909-01/BEFUND.md) ist unveraendert.

## Implementierter privater Anschluss

- Zwei eigene primaere und zwei direkte NW-Nullzustaende. Historienbindung
  aus den zugehoerigen sechs Quellenbelegen; getrennte Owner und Ketten.
- Unveraenderte NW-Updatearithmetik, vier Updates je Historie, danach Freeze.
  Kein primaerer Koeffizient wird in einen Direktlerner uebernommen.
- Funktional ausschliesslich Profil, verfuegbare Halbvektoren und bei den
  Lernarmen der eigene Koeffizient. Administrativ gebundene Historiennamen
  gehen nicht an die Praediktoren. FIXED_HALF bleibt literal 0.5;
  PERSIST und LINEAR verwenden unveraenderte historische Funktionen.
- Geschlossener Einmaleinstieg mit Quellen-/Qualifikationsbindung,
  atomarem Gesamtbeleg, phasengenauem Fehlerabschluss, einmaligen
  Verifikations-/Evaluationsanschluessen und finally-Gateschliessung.
  Keine historische Hauptfunktion umgewidmet und keine neue Laufplattform.

Einstieg: `tools/_s2nx_private_learning_run.py::run_main_once`.
Er ist ausschliesslich im temporaeren neutralen IO-Test ausgefuehrt worden.
Der reale NX-Hauptlauf ist weiterhin nicht freigegeben; MAIN_GATE=False.

## Tatsaechlich erreichte Kontrollen

| Bereich | Erreichte neutrale Kontrolle |
| --- | --- |
| Historien | Vier getrennte Nullobjekte; fremde Formationsketten, vertauschte Owner-/Historienbindungen und manipulierte Lernzustaende typisiert abgewiesen |
| Lernen | Eigene vier Updates je H1/H2, vorgebundene Binary64-Rechenfolge; Direktlerner aus eigenen Nullzustaenden |
| Zukunft | Zielzugriff vor Prognosebindung sowie fehlende/geaenderte Bindung abgewiesen; beide Gegenrechnungen vor Zielverarbeitung gebunden |
| Updategrenze | Vor Zielbeobachtung kein Update; primaere und direkte Fehlerbindung vor Update geprueft; Fehler im Scorer verhindert Update |
| Freeze | Beide Freeze-Bindungen vor erstem Testreaderzugriff erforderlich; fehlende und manipulierte Bindungen abgewiesen |
| Pruefteil | Zwoelf Stellen mit beiden unveraenderten Zustaenden, jeweils frisches Praefix; keine Testupdates; derselbe einmal gelesene Zielzustand fuer alle Arme |
| Kontrollen | Feste 0.5 unabhaengig von Fits, historische Persistenz-Bitkopie und LINEAR; Direktrechnung bei gesperrten Primaerfunktionen erfolgreich |
| Grenzwerte | Nullnenner, Unterlauf/Subnormale, Inf/NaN und falsche Eingabeformen; endliche Prognosen ausserhalb [0,1] bleiben ungeclippt |
| Negative Befunde | Numerisch initiale/nullinformative und gleiche informative Fits bleiben RECORDING_COMPLETE und verifizierbar; fachlich FALSIFIED statt Technikfehler |
| Bewertung | Alle 28 Kriterien einzeln; K und F getrennt; Training, Wechselverluste und Folgefenster separat; keine Verlustverrechnung |
| Gesamtbeleg | Fehlende Quellen, falsche Prognosen, Historien-/Freeze-/Update-Manipulationen, Fortschrittsfehler, Schreibkonflikt und Auswertungssperre geprueft |
| Lifecycle | Beide Lernpaare bei Erfolg geschlossen und bei Abbruch freigegeben; Fehlerfall in zweiter Lernhistorie veroeffentlicht keine fachlichen Teilbefunde |

Vier vollstaendige synthetische Ausfuehrungen deckten regulaeren Verlauf,
Nullzustandskoeffizienten, gleiche informative Fits und den neutralen
Einmaleinstieg ab; hinzu kamen ein Fehlerabschluss und fokussierte
Praefixkontrollen. Die synthetischen Beispielkoeffizienten sind **keine
NX-Ergebnisse und keine Lernvorgabe** fuer einen spaeteren Lauf.

Sechs echte direkte Audioanalysen und sechs NJ-Projektionen wurden nur auf
neutralen konstanten Adapterfenstern ausgefuehrt. Deren Hashpruefung und
native Zeitgrenze sowie Prognosebindung vor Zielerzeugung wurden geprueft.
Keine versiegelten NX-Payloads, keine separate NX-Materialisierung und
kein realer NX-Lern-/Transferlauf. Memory-, Feld- und Runtimeaufrufe `0`.

## Arbeit und Beleggroesse

Je synthetischem Komplettlauf: 32 gebundene reduzierte Fenster, acht Updates,
20 Prognosestellen, je Implementierung 92 Prognosevektoren, 4.416 Fehlerterme
und 108 Gewinndifferenzen. Nur beim realen neutralen Adapterteil wurden
tatsaechliche Rezeptoren ausgefuehrt; synthetische Analysezaehler behaupten
keine FFT-Ausfuehrung.

Offline separat gebunden und neutral geprueft: 1.536 Halbierungen,
je 6.912 Prognosesubtraktionen/-additionen, 4.992 Multiplikationen,
1.920 Persistenzkopien, je 1.536 Updateoperationen, 16 Updates/hoechstens
16 Divisionen, 8.832 Fehlerterme, 184 MAE-Summen und 216 Gewinnpruefungen.
Bei Nullnennern bleiben Divisionen aus; das ist kein technischer Fehler.

Die vollstaendige [neutrale Gesamtbelegdatei](neutral-envelope.json) mit
Roh-/Halbwerten, Zeit-/Quellenbelegen, zwei Historienketten, Prognosen,
Fehlereinzeltermen, Code- und Siegelbindung umfasst **767.427 Byte** bei
unveraendertem Limit **2.097.152 Byte**. Prognosebindung hoechstens 65.536,
Lernzustand 4.096, Verifikation und Auswertung jeweils 262.144 Byte.
Keine Grenzerhoehung oder nachtraegliche Korrektur.

## Digests und unveraenderliche Herkunft

[result.json](result.json) bindet identische Vorher-/Nachher-Quellhashes,
einschliesslich historischer Komponenten und aller vier NX-Siegeldateien.

| Bindung | SHA-256 / Digest |
| --- | --- |
| Qualifikationsergebnis | `95bef00924f51d9cb5924aa9f6ffc3a2cb9e4fb7b8eeb514e06ba30739892d26` |
| Neutrale Gesamtdatei | `581cf4eb0ea9e8fc1df872143414ac88f4c4ebebffa47466afb0b1c91641275c` |
| Prognosekomposition | `2b060dc8d0afcfde50cf466ab4721614e33feda871649ce54e84768381ca0c1a` |
| Laufanschluss | `c8b3c7b903370daf6dbbd7227768a7c7ec717f0cf85680da34f7b38d93539643` |
| Unabhaengige Verifikation | `db8ef74dd9c1dca75e68f0b5a6d173828daff3f430c7d1af78f0dccc78471906` |
| Getrennte Auswertung | `8b0ac64abf30808a4f11ddf8a8d7375510521e48a9de4a523fa0c2e685839b43` |
| Testdatei | `30dca2139f414c7e7a3c1a18118266c076a36112fe6d5da4337aa4719e7c4374` |

## Grenzen und Freigabestatus

Die Qualifikation belegt die geprueften privaten Anschlussgrenzen,
keinen NX-Funktionsnutzen. Der Offline-Pruefer rechnet aus gespeicherten
Roh-/Halbwerten, prognostischen Eingaben und eigenen Lernketten nach;
er beweist allein keine historische CPU-Aufrufreihenfolge. Diese beruht
auf dem qualifizierten kontrollierten Aufrufpfad, nicht auf einer Sandbox
gegen beliebige interne Python-Manipulation.

Gates nach Abschluss `False`, einschliesslich Quellen-, NW- und NV-Gate.
ME/MI bleiben gesperrt. Keine automatische Auswahl der passenden Historie,
keine Memorymechanik, Feldintegration oder Behauptung von Quellenidentitaet.
Historische Befunde, Versiegelung, fremde Aenderungen und Bootstrap sind
unveraendert. Ein realer Hauptlauf bedarf separater Freigabe.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieses
Qualifikationsbefunds und der separaten NX-Hauptlaufentscheidung weiter.
