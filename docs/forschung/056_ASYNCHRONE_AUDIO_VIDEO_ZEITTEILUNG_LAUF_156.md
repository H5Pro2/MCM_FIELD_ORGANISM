# Lauf 156 - Asynchrone Audio-Video-Zeitteilung

## Forschungsfrage und Auftrag

Bleibt die Feldwirkung derselben vollstaendig erfassten, prozeduralen
Audio-Video-Quelle erhalten, wenn ihre unveraenderten Rezeptorereignisse
entweder in einem groben Feldschritt oder entlang aller gemessenen
Completion-Zeitpunkte verarbeitet werden? Zusaetzlich werden die deklarative
Reihenfolge der Rezeptorsequenzen, eine exakte Wiederholung sowie die
technischen Gegenbaselines `w0`, `wv` und `wa` geprueft.

Der Lauf untersucht ausschliesslich die in Forschung 030 benannte
Asynchronitaetsluecke. Kamera, Mikrofon, Browseraufnahme, Memory,
Semantik, Zielverhalten und neue Feldmechanik sind nicht Bestandteil.

## Verwendete Quellen

- aktueller Benutzerfreigabe und Freigabe fuer Lauf 156
- `docs/forschung/030_KONZEPT_BESTANDSLUECKE_ASYNCHRONER_AUDIO_VIDEO_WELTKONTAKT.md`
- `mcm_field_organism/controlled_audio_video_test_world.py`
- `mcm_field_organism/asynchronous_receptor_events.py`
- `mcm_field_organism/field_time_partition.py`
- `mcm_field_organism/neutral_asynchronous_field_runtime.py`
- `mcm_field_organism/neutral_local_field_substrate.py`
- `mcm_field_organism/shared_mcm_field.py`

Externe Webquellen wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Neu hinzugefuegt wurden:

- `mcm_field_organism/asynchronous_audio_video_partition_probe.py`
- `tools/run_asynchronous_audio_video_partition_probe.py`
- `tests/test_asynchronous_audio_video_partition_probe.py`

Die Probe verwendet die vorhandene prozedurale Weltfamilie, deren Audio- und
Video-Rezeptorpfade, die bestehende Completion-Zeitpartition und die
unveraenderte neutrale asynchrone Feldruntime. Die Feldanatomie, Projektion,
lokale Antwort und der schnelle Nachhall wurden nicht veraendert.

## Durchgefuehrte Schritte

1. Eine Sekunde Weltzeit wurde fuer alle Arme mit derselben Anatomie, Uhr und
   Rezeptorkonfiguration erzeugt.
2. `w0`, `wv`, `wa` und `wav` wurden als rein technische Quellen verglichen.
3. `wav.coarse` verarbeitete alle Ereignisse in einem Feldschritt.
4. `wav.fine` verarbeitete dieselben Ereignisse in 91 verlustfreien Schritten
   entlang der Completion-Grenzen.
5. Der feine Arm wurde exakt wiederholt und mit vertauschter deklarativer
   Reihenfolge der Audio- und Video-Sequenzen erneut ausgefuehrt.
6. Verglichen wurden Ereignis- und Gruppenanzahl, Endtick, Feldticks,
   Aktivierung und Nachhall komponentenweise.

## Messergebnisse und Gegenbaselines

Alle sieben Arme enthielten 101 Rezeptorereignisse, 91 Completion-Gruppen,
10 gemischte Audio-Video-Gruppen und den Endtick 1.000.000. Der grobe Arm
hatte einen technischen Feldtick, die feinen Arme jeweils 91.

| Arm | Aktivierung L2 | Nachhall L2 |
| --- | ---: | ---: |
| `w0.coarse` | 0,3258928632563555 | 0,19381650487527308 |
| `wv.coarse` | 0,5321459860598585 | 0,3187892108422303 |
| `wa.coarse` | 0,3477797596706884 | 0,20799539736448644 |
| `wav.coarse` | 0,5541715200520211 | 0,3321177084288284 |
| `wav.fine` | 0,5541715200520135 | 0,3321177084288230 |

Komponentenweise Vergleiche:

- grob gegen fein, Aktivierung L-inf: `4,6351811278100286e-15`
- grob gegen fein, Nachhall L-inf: `4,614364446098307e-15`
- vertauschte Sequenzreihenfolge, Aktivierung und Nachhall L-inf: `0,0`
- exakte Wiederholung des feinen Arms: bitgenau gleich

Testreproduktion:

```text
23 passed in 6.20s
```

## Einordnung

**Beobachtet:** Bei identischem Ereignisbestand und identischem Zeithorizont
ist die grobe und feine Verarbeitung bis auf etwa `4,6e-15` komponentenweise
gleich. Die deklarative Sequenzreihenfolge hat keinen messbaren Einfluss. Die
Wiederholung ist exakt reproduzierbar.

**Technische Interpretation:** Die kleine grob-fein-Abweichung liegt in der
Groessenordnung akkumulierten Gleitkomma-Rundens bei unterschiedlich vielen
technischen Feldschritten. Fuer diesen kontrollierten Ein-Sekunden-Lauf ist
keine zusaetzliche Asynchronitaetswirkung erforderlich, um das Ergebnis zu
erklaeren.

**Hypothese:** Bei laengeren Horizonten oder nicht-kommensurablen Audio- und
Videoraten koennte sich Rundung staerker akkumulieren. Das ist keine
beobachtete Feldorganisation und wurde hier nicht geprueft.

## Grenzen und nicht gepruefte Annahmen

- Es handelt sich um eine synthetische prozedurale Welt, nicht um reale
  Kamera- oder Mikrofonwahrnehmung.
- Geprueft wurde ein Horizont von einer Sekunde mit den vorhandenen Raten.
- Die Quelle wurde nicht interpoliert, normalisiert oder sample-and-hold
  behandelt; unterschiedliche reale Sensorlatenzen wurden nicht simuliert.
- Die technischen Baselines sind keine Bedeutungsrollen.
- Memory, Organisation, Topologie, Semantik und Feld-Welt-Feld-Kausalitaet
  wurden nicht untersucht und werden aus dem Ergebnis nicht abgeleitet.

## Konkrete Schlussfolgerung

Die Asynchronitaetsfrage aus Forschung 030 ist fuer die vorhandene
prozedurale Audio-Video-Testwelt im geprueften Bereich geschlossen: Eine
verlustfreie feinere Completion-Zeitteilung und eine vertauschte
Sequenzdeklaration veraendern die spaetere Feldaufnahme nicht ueber numerische
Rundung hinaus. Lauf 156 liefert daher keinen Hinweis auf eine eigenstaendige
Feldorganisation oder Memoryfunktion und erfordert keine neue Mechanik.

Eine Zielabweichung ist nicht erkennbar.

## Naechster begrenzter Forschungslauf

Aus dem jetzigen Stand sollte als Lauf 157 die reale gemeinsame Kamera- und
Mikrofonaufnahme technisch stabilisiert werden. Begrenzter Auftrag: laengerer
reiner Schnittstellenlauf mit Zeitkontinuitaet, Aussetzern, Dock-Herkunft,
nativen Raten, Synchronisierung und unverfaelschter Uebergabe als Messgroessen.
Noch keine Memory-Auswertung und keine Feld-Welt-Feld-Behauptung. Der physisch
getrennte Effektor-Zielflaeche-Kamera-Aufbau bleibt danach der wichtigste
Grundlagenzweig.
