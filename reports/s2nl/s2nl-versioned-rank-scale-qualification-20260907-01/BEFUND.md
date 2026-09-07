# S2-NL: versionierter Rangskalenanschluss neutral qualifiziert

2026-09-07; ID `s2nl-versioned-rank-scale-qualification-20260907-01`.
Status: `S2NL_RANK_SCALE_COMPOSITION_QUALIFIED`.
**Genau ein Qualifikationsaufruf, 29/29 Tests, Exit-Code 0.** Kein Retry.
Unittest meldet 4,908 Sekunden. Testinventar und Budgets waren vorab in
[QUALIFIKATIONSBINDUNG.md](../QUALIFIKATIONSBINDUNG.md) festgelegt; der
[Vorbeleg](preregistration.json) bindet Kommando, Interpreter und Quellhashes
vor dem einzigen Testprozess. Keine vorgeschaltete Testausfuehrung.

Aufruf aus dem Workspace: `C:/Python314/python.exe -B reports/s2nl/qualify_once.py`.
[Testprotokoll](stderr.txt), [Ergebnis](result.json), [Beobachtungen](observations.json).
Ergebnisdigest:
`112bb589c74eb7bb9219f127b8f3362dbdfac836abbafd13f6c66c20e3a08baf`.
Die 26 gebundenen Dateihashes stimmen vor/nach der Qualifikation ueberein.

## Implementierter Umfang

- Genau zwei feste Rangbindungen im gemeinsamen privaten TSPM-Kern:
  historischer Schluessel unveraendert; neues Halbprofil mit
  `r_audio=2.0*d_audio_neu` ausschliesslich fuer die gemischte Rangfolge.
- Neue Semantik nur unter `tspm1.private.audio-half.v2`. Die historische
  Fast-Payload bekommt kein neues kanonisches Feld. Historische Default-
  Profil-, Parameter-, Bank- und Configdigests bleiben erhalten.
- Fast-Fortschreibung, interne Kandidatenrelationspruefung, native Vollprobe
  und deren Relationspruefung verwenden die profilgebundene Rangskala.
  Der S2-JW-Vollprobenbeobachter bindet auch ausgewaehlte Slot-ID und -Digest.
- Eigene Halbprofil-, Quellen-/AV-Paarungs- und Koordinatorversion. Die feste
  NJ-Ausgangsprojektion wird vor der Kontaktbindung uebernommen, nicht erneut
  multipliziert. Gespeicherte Audiowerte und Updateeingaenge bleiben halbiert.
- Audio-Fast/A-Grenze `0.1`, Audio-PPB/Slow-Grenze `0.01`. Visuelle Grenzen,
  Kapazitaeten, Support und Zeitparameter bleiben unveraendert. Die neue
  PPB-Profilbindung erweitert nicht den historischen Parameterbereich.
- Die bestehende atomare B4-/TSPM-Formation wird wiederverwendet. Die neue
  Configbindung gelangt transitiv ueber Digests in State, Owner und Receipt;
  bestehende Recordformen werden nicht pauschal umgeschrieben.
- Unabhaengige direkte Rangnachrechnung mit kompletten belegten Slotzeilen,
  Matchdistanzen, Rangtupeln, Slotbindung und bestehenden Tie-Breaks. Keine
  Delegation an den produktiven Ranghelfer. Verifikation fuehrt keinen
  neuen Memoryschritt oder Vollprobenabruf aus.

Private Aufrufbindung:
`tools/_s2nl_private_half_profile_binding.py` (`build_config`, `bind_pair`,
`bind_cue`); direkte Nachrechnung:
`tools/_s2nl_private_rank_verification.py`.
Es wurde kein Runner fuer einen Forschungs-Hauptlauf und keine neue
Recorderplattform angelegt. Historische R0- und S2-KZ-/S2-NE-Algorithmen,
PPB-Updatealgorithmus, Rezeptoren und Defaultfabriken bleiben in ihrer
historischen Semantik erhalten; die Kernanschlussaenderungen sind versioniert.

## Beobachtete Qualifikation

24 neue Testkoerper plus fuenf gezielte, unveraenderte S2-DH-Regressionen:

- Alle 30 festgelegten Matchpaare: gleiche Alt-/Neu-Matchentscheidung und
  bitgleiche neue Distanz gegen die Halbierung der alten Distanz. Das gilt
  nur fuer diese Faelle und die jeweils gebundene Arithmetik, nicht universell.
- Das S2-NK-Gegenbeispiel zeigt den naiven Slotwechsel und dessen Vermeidung
  durch die feste Rangumrechnung. Native Fast-Auswahl, Relationspruefung,
  Vollprobe und direkte Nachrechnung stimmen bei den neutralen Belegen ueberein.
- Maximum, Summe, Slot-ID und bei B4 Formationsalter wurden getrennt geprueft.
  Gueltige Abwesenheit ist technisch verifizierbar; falsche Slot-/Rangbindungen
  sowie gemischte Profile, Zustaende, Quellen und Owner werden abgewiesen.
- Zwei Vier-Schritt-PPB-Ketten je Skala: 16 direkte PPB-Schritte. Alle
  Prototypkomponenten entsprechen der gebundenen Binary64-Updatefolge.
  Supportfolge je Kette `1,2,3,3`; Prototyp-/Zustandsdigests sind gespeichert.
- Neue Testkoerper: 13 neutrale atomare Formationen, davon je vier pro Skala
  im direkten Sequenzvergleich. Die geprueften visuellen Slotwerte bleiben
  gleich; auditive Endwerte entsprechen in diesen Ketten der Halbskala.
- Beide S2-NE-Teilscanregeln und Direktbaselines bleiben rangfrei, scannen
  `9/3/8` und verwenden die neuen A-/Slow-Grenzen. Read-only-Digests stimmen.
- Genau ein direkter neutraler Null-Rezeptoraufruf; keine NH-Quellen,
  keine RGB-Rezeptoranalyse. Die uebrigen Vektoren/Slotbelegungen sind
  ausdruecklich synthetische neutrale Testfixtures, kein neuer Lernkorpus.
- Gepruefte Grenzen: 44.544 numerische Zustandsbytes, 1.008 Fast-L1-Terme,
  Rangbeleg bis 16.384 Byte, AV-Paar bis 65.536 Byte und bestehende
  Teilscan-Ausgabe unter 32.768 Byte. Keine Grenzerhoehung.

## Numerische Grenze, separat vom technischen Bestehen

**Alle drei Subnormalpaare verlieren die volle Kandidatenunterscheidbarkeit.**
Bei `s` als kleinster positiver Subnormalzahl und `m` als kleinstem normalem
Binary64-Wert waren die jeweils nur an Position 47 unterschiedlichen Vektoren
vorher ungleich, nach der Projektion aber gleich:

| Originalpaar an Position 47 | Nach Halbierung |
| --- | --- |
| `(s,0)` | `(0,0)` |
| `(3*s,4*s)` | `(2*s,2*s)` |
| `(m,nextafter(m,0))` | `(m/2,m/2)` |

Die mittleren Distanzen und Rangpraefixe dieser neutralen Paare sind bereits
auf der alten Skala auf Null gerundet. Deren Match-/Ranggleichheit ersetzt
deshalb keinen Nachweis erhaltener Vollvektorgleichheit. Der Beleg weist
die drei Abweichungen gesondert aus. Eine daraus folgende A-Konfliktentscheidung
wurde fuer diese Subnormalpaare nicht als eigener Abruffall ausgefuehrt.
Keine Toleranz, kein Clipping, keine geaenderte Rundung und kein Ersatzfaktor.

Analytische Homogenitaet in exakter Arithmetik, beobachtete neutrale
Binary64-Ergebnisse und **fehlender universeller Gleitkommanachweis** bleiben
getrennte Aussagen. Die Qualifikation ist kein Beweis allgemeiner identischer
Memorygeschichten oder allgemein verlustfreier Kandidatengleichheit.

## Bindungen und Grenze

- Neues privates Profil: `23b600cb4de2a61c5a4db620ec61347bf21462efa1a802e84bed84e816fe0a03`
- Neuer Koordinator: `55f1de8602c945749728ce17c74cdff8320d1b5fc72c800f239bc86737db1a1e`
- Neue TSPM-Config: `f886dfba4521a397e764728f4bf0f1c12a59678c86ae5c7d56bf813e31bb680a`
- Neue Fast-Config: `b96f478d00986805c75910f9696ed7b853f80d3263f2a32d8bc74dfb0c801fc8`
- Neue Quellenprofilbindung: `4e2435ad1a9134ac5985236fefb0df0c83974327a5c5e179cf66d235aca94ab5`

NH-, NG- und NL-Hauptgate wurden vor/nach als `False` gebunden. Keine Feld-
oder Runtimeintegration, keine Hypothesenanwendung, keine Feld-Rueckverstaerkung.
Die erwartbar andere Feldanregung bleibt ungeprueft und getrennt von dieser
Memoryvergleichsqualifikation. S2-NH bleibt `NOT_EVALUABLE`; kein Wiederaufrollen.
Historische Belege und fremde Dateien einschliesslich Bootstrap unberuehrt.

WEITER: Am besten geht es jetzt mit der Analystenbewertung des qualifizierten
Profilanschlusses und der expliziten Subnormalgrenze weiter, bevor eine
separat freigegebene Systemintegration geplant wird.
