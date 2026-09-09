# S2-NV: rezeptorfreie Vorversiegelung abgeschlossen

Einmaliger Lauf `s2nv-source-preseal-20260909-01`, Exit-Code `0`:
**S2NV_SOURCES_PRESEALED**, anschliessend genau eine unabhaengige
read-only Bindungspruefung: **S2NV_PRESEAL_VERIFIED**. Kein Retry.
Voraussetzung war die unveraenderte [16/16-Qualifikation](../s2nv-source-binding-qualification-20260909-01/BEFUND.md).

```text
C:/Python314/python.exe -m reports.s2nv.preseal_once
```

## Gebundener Umfang

20/20 PCM-Fenster in vier Fuenferfolgen wurden einmal erzeugt: insgesamt
96.000 Samples / 384.000 PCM-Byte. Maximal ein 19.200-Byte-Fenster wurde
gleichzeitig gehalten; keine Rohpayloadablage. Bytegleiche Fenster wurden
trotzdem jeweils erzeugt und mit eigenen Quellenidentitaeten und Zeiten gebunden.

Die [Ausfuehrungswurzel](execution-plan.json) enthaelt Rezepte, Reihenfolge,
native Zeiten, `start//480`-Indizes, Quellen-/Payloadhashes, die unveraenderten
Roh-/Halbprofilbindungen, Generator-/Interpreteridentitaet, zwoelf feste
Prognosestellen und die textuell gebundenen Vorschriften. Kategorien,
Bewertung und sechs strikte Prognosebedingungen liegen ausschliesslich in
der getrennten [Evaluationswurzel](evaluation-plan.json). Kein Kriterium wurde
ausgewertet. Der [Vorabbeleg](preregistration.json) entstand vor PCM-Erzeugung.

## Vollstaendige Bytegleichheiten

Im Folgenden steht `sSS/wKK` fuer die getrennte Quelle `nv-sSS-wKK`.
Alle Mitglieder einer Zeile besitzen denselben PCM-Hash; kein Eintrag wurde
entfernt oder ersetzt. Die vollstaendigen Hashes stehen im [Siegel](seal.json).

| Bytegleiche Quellen | Einordnung aus den festen Rezepten |
| --- | --- |
| s01/w00, s02/w00, s02/w04, s03/w00, s04/w00 | Gemeinsamer erster Praefix und Rueckkehr zum Anfangspegel |
| s01/w01, s02/w01, s02/w03, s03/w01, s04/w01 | Gemeinsamer zweiter Praefix und wiederholter Pegel |
| s01/w02, s02/w02, s03/w02, s03/w03, s03/w04, s04/w02 | Gemeinsamer dritter Praefix und Stillstand |
| s04/w03, s04/w04 | Wiederholtes neues Gruppenfenster |

Die Quellen s01/w03 und s01/w04 besitzen jeweils eigene Payloadhashes.
Damit sind alle Bytegleichheitsgruppen dokumentiert; keine weitere
Kollision ausserhalb dieser rezeptgleichen Gruppen wurde gefunden.
Dies ist keine Aussage ueber Rezeptorvektorgleichheit oder Vorhersagen.

## Wurzelbindungen und Pruefung

| Bindung | SHA-256 / kanonischer Digest |
| --- | --- |
| Unveraenderter NV-Planfilehash | `b2ac2c154fd81e7740e2bc16b96fff7d72d2739e90fd56675e16afd133366cee` |
| Ausfuehrungsdigest | `37a6a114860f868bda9d7bfbb437ad6f3e8e22820fedc60d49a1622ae209499e` |
| Evaluationsdigest | `85bd55b8c1e40e0ce8f99a285408756f20a152439c842cda48f01c21842c4155` |
| Siegeldigest | `c927527b71f016e5f359fc2e439c8b58a23672fcb22f8cb959760313ade8507a` |
| Verifikationsdigest | `5c2bcbd6c0ee9079a170f9c6e9b107453755e262338f3c859ec1152e88731eb7` |

Die [unabhaengige Pruefung](verification.json) las ausschliesslich Belege:
Quellenform, native Fenster, Literale, Vorschriften, Praefixe, Kriterien,
Kollisionstabellen, Profile, Generator-/Umgebungs- und Datei-/Objektdigests.
Alle Quellhashes und die gelesenen Plandateien blieben unveraendert.
Keine Payloadregeneration: PCM-Hashes werden gegen gespeicherte Bindungen
geprueft, nicht aus erneut erzeugten Bytes unabhaengig nachgerechnet.

Ausfuehrungswurzel 31.727 Byte, Evaluation 1.744 Byte, Siegel 4.415 Byte,
Vorabbeleg 28.536 Byte, Verifikation 2.162 Byte. Die jeweils gebundenen
Artefaktgrenzen wurden eingehalten. CPython 3.14.4 / AMD64 und Built-in-math
sind explizit gebunden; alle Detailhashes stehen in den Belegen.

## Nicht ausgefuehrt und weitere Grenze

Rezeptor-, NJ-, Prognose-, Fehler-, Memory-, Feld-, Kontext- und Runtimeaufrufe:
jeweils **0**. Keine separate Rezeptormaterialisierung freigegeben. Die
Zukunftsrezepte, Payloadhashes, Quellen- und Zeitkennungen bleiben ausserhalb
der funktionalen Vorhersagereingaben. Die spaetere Ausfuehrung muss Prognosen
vor Regeneration/Analyse des jeweiligen Zielzustands binden; ein finaler
Digest alleine kann die historische Aufrufreihenfolge nicht beweisen.

Dieser Abschluss bestaetigt nur Quellen- und Planbindung. Rezeptorgueltigkeit,
Vorhersagenutzen und die praktische Zukunftssperre sind noch nicht geprueft.
Das festgelegte Verfahren ist Extrapolation, kein Lernen. NU bleibt geschlossen,
ME/MI gesperrt, Gate `False`; historische Belege und Bootstrap unveraendert.
