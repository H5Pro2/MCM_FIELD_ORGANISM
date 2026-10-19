# S2-SP: Korrigierte Lebenszyklus-Aufgabenbindung

## Anlass

Der technisch gültige Lauf `s2sp-identity-lifecycle-20260919-01` prüft den
vollständigen beabsichtigten Lebenszyklus nicht. Bei e13 bestehen weiterhin
zwei exakte B4-Treffer, während e06 bis e12 jeweils `FAST_UPDATED` auf
`tspm1.fast.slot.000` melden. Ein `FAST_REPLACED`-Ereignis ist nicht
belegt. Somit sind weder A-Verdrängung noch eine daran anschließende
B-Erhaltung geprüft.

## Soll und belegter Zustand

| Abschnitt | Gebundene Absicht | Tatsächlich im Record |
|---|---|---|
| e01-e04 | Ziel wiederholen und visuellen Slow-Aufbau bilden | Eine Fast-Spur wird erzeugt und danach aktualisiert; e05 hat im privaten Arm einen exakten visuellen Slow-Treffer. |
| e06-e12 | A durch konkurrierende Formationen verdrängen und Ziel in B erhalten | Jede Formation meldet `FAST_UPDATED` auf denselben Fast-Slot; keine Fast-Ersetzung. Bei e13 gibt es noch zwei exakte B4-Kandidaten. |
| e13 | Ziel nach A-Verdrängung read-only aus B abrufen | Kein exakter visueller Slow-Kandidat in beiden Armen. Die Voraussetzung A-Verdrängung ist nicht erfüllt. |
| e14-e15 | B-Zielgeneration ersetzen und alten Zielabruf verlieren | e14 ist eine weitere `FAST_UPDATED`- und PPB-Fortschreibung. Der Record besitzt keinen lesbaren visuellen PPB-Slot-/Ereignisbeleg, der eine Zielersetzung zuordnet. |
| e07 | Abweichende Komponente nach historischer Formel fortschreiben | Belegt: ausgewählter visueller PPB-Slot `.001`, nur Index 1 verändert und historischer Formelwert gespeichert. |

## Kandidatenkennungen

Die Vergleichslogik bildet Kennungen wie folgt:

- B4: `B4:<slot_id>:<Digest des vollständigen B4-Eintrags>`.
- Fast: `FAST:<slot_id>:<Digest des vollständigen Fast-Slots>`.
- visueller Slow: `VISUAL_SLOW:<slot_id>:<Digest des kanonischen PPB-Slot-Payloads>`.

Die Slot-ID ist die feste Speicherposition. Der Digestanteil ist kein
eigenständiger Generationsbezeichner: Bei PPB enthält er mindestens
`prototype_values`, `support_count` und `last_selected_step`. Eine Änderung
dieses Digests kann daher regulär durch ein Match-Update entstehen. Der
globale PPB-Schrittzähler ist ebenfalls keine Slotgeneration.

## e07 und die Zielspitze

Die e07-Variationsquittung nennt `ppb1.visual.default-live.v1.slot.001`.
Der bei e05 im privaten Arm exakte Zielkandidat liegt in `.000`. e07 hat
damit den e05-Zielslot nicht unmittelbar aktualisiert. Für e06 sowie e08 bis
e12 enthält der gespeicherte Lauf jedoch nur Readout-Digests, nicht den
ausgewählten visuellen PPB-Slot. Eine direkte Aktualisierung von `.000` in
e06 oder einem späteren Ereignis kann deshalb nicht rückwirkend
ausgeschlossen werden.

Die bestätigte Formelkontrolle e07 bleibt gültig, ist aber eine eigene
Frage. Sie darf nicht länger als Kontrolle einer unveränderten Zielspur
verwendet werden.

## Bereits vorhandene native Nachweisfelder

`PPB1Readout` führt bereits `event` (`MATCHED`, `CREATED`, `REPLACED`),
`slot_id`, Distanz, Support, Prototyp, Eingangs- sowie Vor- und
Nachzustandsdigest. Das Fast-Übergangsreceipt führt zusätzlich
`primary_event`, `selected_slot_id`, abgelaufene Slotdigests und bei
`FAST_REPLACED` den verworfenen Slotdigest. Der S2-SP-Record bewahrt für PPB
derzeit nur den Readout-Digest und globale Schrittstände. Künftige
Lebenszyklusbelege müssen die bereits native PPB-Readout-Form verlustfrei
referenzierbar machen, insbesondere Ereignis, Slot-ID, Vor-/Nachzustands-
und Eingangsbindung. Das ist eine Beleganforderung, keine Rekonstruktion aus
den vorliegenden Kandidatenkennungen.

## Korrigierte Aufgabenbindung

Die nächste mögliche Prüfung wird in getrennte kurze Geschichten zerlegt:

1. **Unveränderte Zielerhaltung:** Nur bitgleiche Zielbildungen bis zum
   read-only Cue. Keine veränderte Formation und kein konkurrierender
   PPB-Eingang vor dieser Aussage.
2. **Veränderter Eingang:** Separater Aufbau eines Nichtzielslots, danach
   eine vorgebundene veränderte Formation. Der Nachweis beschränkt sich auf
   gewählten Slot, geänderte Indizes und historische Formelwerte.
3. **A-Verdrängung und B-Erhaltung:** Eine eigene Geschichte, deren
   tatsächliche Fast-Transitionen und visuelle PPB-Readouts vollständig
   aufgezeichnet werden. Ein B-Cue wird nur als B-Erhaltungsfall bewertet,
   wenn der Record zuvor die beabsichtigte Fast-Ersetzung und die erhaltene
   Zielslotbindung belegt.
4. **Zielersetzung:** Nach einem vorherigen erfolgreichen B-Cue wird eine
   gesonderte, gebundene Formation verarbeitet. Erst ein natives
   `REPLACED`-Readout auf der zuvor gebundenen Zielslot-ID und die neue
   Vor-/Nachzustandskette begründen die Aussage über das Ende dieser
   Generation.

Diese Zustände sind spätere Bewertungskriterien, keine Startgates. Bleibt
eine Transition aus, ist das ein fachlicher Gegenbefund. Neue Quellen,
Schwellen, Memoryregeln oder eine nachträgliche Auswahl passender Fälle sind
nicht Teil dieser Bindung.
