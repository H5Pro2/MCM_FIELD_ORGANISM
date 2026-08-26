# 213K - Umgesetzte Hook-Sollbindung und statische G0-Bytebindung

## Einordnung, Forschungsfrage und Auftrag

Dieses Paket dokumentiert einen eng begrenzten statischen Korrekturauftrag und ist
kein Forschungslauf. Deshalb wird keine Laufnummer vergeben.

Freigegeben war ausschliesslich, in
`mcm_field_organism/_runtime_fixation_structure.py::_SOURCE_DIGESTS` den Sollwert
fuer `mcm_field_organism/previous_state_contribution_hook.py` vom historischen
Digest auf den in 213I autorisierten aktuellen Rohbyte-Digest zu setzen und danach
eine neue statische Bytebindung zu dokumentieren.

Keine weitere Codeaenderung, kein Import, kein Test, kein Prozessstart und keine
Sicherheits- oder Systemaktion waren freigegeben oder wurden ausgefuehrt.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabe-Eingang mit der ausdruecklichen Einzeilenfreigabe;
- `213I_STATISCHE_HOOK_INHALTS_UND_HERKUNFTSABNAHME.md`;
- `213J_STATISCHER_BYTEBINDUNGS_KORREKTURVORSCHLAG_UND_G0_NEUAUFNAHME.md`;
- `mcm_field_organism/_runtime_fixation_structure.py`;
- die acht in `_SOURCE_DIGESTS` referenzierten lokalen Projektdateien;
- die 67 unten bezeichneten G0-Eingangsdateien.

Verwendete read-only Schnittstellen nach der Aenderung waren `Get-Content`,
`Test-Path`, `Get-Item`, `Get-FileHash -Algorithm SHA256`, regulaere Textsuche und
`git diff --check`. Keine Web- oder externe MCM-Quelle wurde verwendet.

## Ausgefuehrte Codeaenderung

Exakt eine Sollbindungszeile wurde geaendert:

```diff
-    ("mcm_field_organism/previous_state_contribution_hook.py", "2a3f2f355ba3c713296156abb08553dc4ce0cbe5a0701e12258ea286caf8371e"),
+    ("mcm_field_organism/previous_state_contribution_hook.py", "42f98fe9beab7f71900135524693fc7e3be898fdc16c1696057c95a0fad8a648"),
```

Dateipfad, Tupelstruktur, die sieben anderen Quelldigests und alle weiteren
Deklarationen der Fixierungsstruktur blieben unveraendert. Der Hook selbst wurde
nicht geaendert.

## Neue Quellbytebindung

| Datei | Bytes | SHA-256 nach Korrektur |
| --- | ---: | --- |
| `_runtime_fixation_structure.py` | 15.549 | `bb4acbc8a7dfd19a22dd1dd404248aff2eddeec72a7de110ef8d6c4a7d76aa3c` |
| `previous_state_contribution_hook.py` | 4.568 | `42f98fe9beab7f71900135524693fc7e3be898fdc16c1696057c95a0fad8a648` |

Gegenueber dem von 213J gebundenen Strukturhash
`399c0c86800f353d37b77f829666f89df3d6385550caeead3893a580244c746e`
hat sich nur die Fixierungsstruktur geaendert. Ihre Bytegroesse blieb gleich. Der
Hook-Hash ist bitgleich zur 213J-Eingangsbasis.

## Statische Pruefung der acht eingebetteten Quelldigests

Die acht Pfad-/Digesttupel wurden aus dem `_SOURCE_DIGESTS`-Text gelesen. Jeder
referenzierte Pfad wurde als regulaere lokale Datei gefunden und sein SHA-256 ueber
die aktuellen Rohbytes erhoben.

| referenzierte Quelle | Ergebnis |
| --- | --- |
| `receptor_contract.py` | passend |
| `receptor_distributor.py` | passend |
| `shared_mcm_field.py` | passend |
| `field_step_time.py` | passend |
| `neutral_local_field_substrate.py` | passend |
| `mcm_neuron_layer.py` | passend |
| `_previous_state_minimal_runner.py` | passend |
| `previous_state_contribution_hook.py` | passend |
| **Summe** | **8/8 passend, 0 abweichend** |

Dies ist eine statische Rohbytepruefung. Die Verifikationsfunktion wurde nicht
importiert oder ausgefuehrt.

## Kumulative G0-Eingangsbasis nach der Korrektur

Die 66 Dateien aus 213J bleiben im Umfang. Hinzu kommt 213J selbst mit 10.840 Bytes
und SHA-256
`ce42a8c8b9398415ff0c6a17cf1276ecce9ef22cf3d7265a51e0c5ad42a1927c`.
Innerhalb der 22 Projektquellen ersetzt der neue Strukturhash den alten, ohne die
Dateianzahl oder Bytesumme zu veraendern.

| Klasse | Dateien | vorhanden | fehlend | Bytes |
| --- | ---: | ---: | ---: | ---: |
| private Projektquellen und Importbaseline | 22 | 22 | 0 | 272.960 |
| venv-Konfiguration | 1 | 1 | 0 | 215 |
| Entscheidungsdokumente | 19 | 19 | 0 | 189.132 |
| native Seeds aus 213E | 25 | 25 | 0 | 35.478.952 |
| **Summe** | **67** | **67** | **0** | **35.941.259** |

Rechnung:

```text
213J-Eingangsbasis: 66 Dateien / 35.930.419 Bytes
+ 213J:              1 Datei  /     10.840 Bytes
= neue Basis:       67 Dateien / 35.941.259 Bytes
```

213K ist wegen echter Hash-Selbstreferenz nicht Bestandteil seiner eigenen
67-Dateien-Eingangsbasis. Es muss nach unabhaengiger Pruefung in einer spaeteren
kumulativen Bindung aufgenommen werden.

## Durchgefuehrte Schritte

1. Altwert, Strukturhash und Hookhash vor der Aenderung read-only bestaetigt.
2. Genau den freigegebenen 64-stelligen Sollwert ersetzt.
3. Struktur- und Hookgroesse sowie ihre SHA-256-Werte neu erhoben.
4. Alle acht `_SOURCE_DIGESTS`-Eintraege textuell extrahiert und gegen die
   aktuellen Rohbytes verglichen.
5. 213J in die kumulative Dokumentbasis aufgenommen.
6. Klassenzaehler und Bytesummen fuer 67 Eingangsdateien neu berechnet.
7. Keine andere Quellzeile, kein Systemobjekt und keine Sicherheitskonfiguration
   geaendert.

## Messergebnisse und Gegenbaselines

```text
ausgefuehrte Quellzeilenaenderungen:       1
Hook-Dateiaenderungen:                     0
_SOURCE_DIGESTS-Eintraege:                 8
passende Eintraege:                        8/8
abweichende Eintraege:                     0/8
G0-Eingangsdateien:                        67
vorhanden:                                 67/67
fehlend:                                   0/67
G0-Eingangsbytes:                          35.941.259
Klassen:                                   22/1/19/25
Imports, Tests und Prozesse:               jeweils 0
SID-/Profil-/ACL-/SACL-Aktionen:           jeweils 0
```

Gegenbaselines:

| Gegenbaseline | Befund |
| --- | --- |
| alter Strukturhash nach Korrektur erwarten | falsch; jede Rohbyteaenderung muss den Strukturhash aendern |
| veraenderten Hook erwarten | falsch; nur dessen Sollwert wurde angepasst |
| nur den Hook-Eintrag vergleichen | unzureichend; alle acht Eintraege wurden statisch geprueft |
| 8/8 als Laufzeitnachweis behandeln | unzulaessig; kein Import und keine Verifikationsfunktion wurden ausgefuehrt |
| 67-Dateien-Basis als vollstaendiges G0 ausgeben | falsch; G1, G2 und 213K-Eigenaufnahme bleiben offen |
| historische Dokumente umschreiben | unzulaessig; sie dokumentieren ihren damaligen Altstand |

## Grenzen und nicht gepruefte Annahmen

- Der Befund `8/8` gilt ausschliesslich fuer den statischen Rohbytevergleich.
- Es wurde nicht geprueft, ob importierter Code oder eine Runtime dieselben Pfade
  oeffnet.
- 213K ist nicht selbst in der 67-Dateien-Eingangsbasis enthalten.
- G1 und G2 sind weiterhin nicht bearbeitet; damit ist der endgueltige
  Huerde-G-Umfang unbekannt.
- Keine Tests bestaetigen in diesem Auftrag das Verhalten der geaenderten
  Deklaration.
- Es wurde nichts zu Feldwirkung, Memory, Organisation, Topologie, Semantik,
  Bewusstsein, Eigenstaendigkeit oder KI geprueft.

## Beobachtung, Interpretation und Schlussfolgerung

- **Beobachtet:** Der freigegebene Sollwert wurde in genau einer Zeile ersetzt.
  Hook und Struktur besitzen die oben gebundenen Rohbytehashes; alle acht
  eingebetteten Quelldigests passen statisch.
- **Technische Interpretation:** Die in 213G festgestellte Hook-Digestabweichung
  ist auf der aktuellen Bytebasis statisch geschlossen.
- **Hypothese:** Eine spaetere statische oder dynamische Verifikationsfunktion
  sollte fuer dieselben unveraenderten Pfade keinen Quelldigestfehler melden. Das
  wurde wegen Import- und Testsperre nicht geprueft.
- **Offene Frage:** Der vollstaendige G0-Umfang bleibt von G1 und G2 abhaengig.
- **Nicht gepruefte Annahme:** Dass keine weitere runtimebezogene Vertragsbindung
  auf den alten Strukturhash verweist, wurde nicht durch Ausfuehrung untersucht.

Konkrete Schlussfolgerung: Die einzelne Hook-Sollbindungsabweichung ist korrekt und
nachvollziehbar umgesetzt. Der reale statische Stand betraegt jetzt `8/8`. G0 als
Gesamtgate ist dennoch **nicht bestanden**, weil 213K noch nachfolgend gebunden
werden muss und G1/G2 weiterhin offen sind. Huerde G bleibt gesperrt.

## Naechster begrenzter Schritt

Als naechster Schritt ist ausschliesslich die unabhaengige statische Pruefung von
213K zulaessig. Zu reproduzieren sind der Einzeilen-Diff, die neuen Struktur- und
unveraenderten Hookbytes, der `8/8`-Rohbytebefund, die 67/67-Dateienbasis, die
Klassen `22/1/19/25`, 35.941.259 Bytes sowie alle fortbestehenden Sperren.

Erst eine nachfolgende Freigabe darf den naechsten statischen Gate-Auftrag
bestimmen. Aus 213K folgt keine Import-, Test-, Prozess-, G1-, G2- oder
Huerde-G-Freigabe.

## Zielabweichung

Keine erkennbare Zielabweichung. Geaendert wurde ausschliesslich eine technische
Rohbyte-Sollbindung; keine Dynamik oder Forschungsbedeutung wurde programmiert.
