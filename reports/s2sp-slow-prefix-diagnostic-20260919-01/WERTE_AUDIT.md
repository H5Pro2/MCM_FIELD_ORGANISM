# S2-SP-Slow: Werte- und Rechenwegaudit

Auftragskennung: `S2SP-SLOW-WERTE-AUDIT-20260919-01`  
Methode: ausschließlich read-only auf den Records
` s2sp-memory-compare-real-20260919-01` und
`s2sp-slow-prefix-diagnostic-20260919-01` sowie dem laufgebundenen Code.

## Befund

Die visuellen Formationswert-Digests von e03, e04 und e05 sind jeweils
identisch mit dem e06-Cue-Digest
`51e24706d4e4e19658d2d5dc76530782dcd3d05ebc5a04ffcd9c627df85d65fe`.
Für die 30 von S2-SP verglichenen visuellen Komponenten liegen beim e06-Cue
und beim gespeicherten Slow-Prototyp vollständige Werte vor. 14 Komponenten
weichen ab; die übrigen 16 sind bitgleich.

| Indizes | Cue (Binary64) | PPB nach e05 (Binary64) | Differenz |
| --- | --- | --- | --- |
| 0, 12, 15, 18, 21, 24, 27 | `0.09411764705882353` / `3FB8181818181818` | `0.0941176470588235` / `3FB8181818181816` | `-2.7755575615628914e-17` / `BC80000000000000` |
| 2, 14, 17, 20, 23, 26, 29 | `0.18823529411764706` / `3FC8181818181818` | `0.188235294117647` / `3FC8181818181816` | `-5.551115123125783e-17` / `BC90000000000000` |

Alle Abweichungen liegen innerhalb der gesamten, von S2-SP geprüften
30-Komponenten-Sicht. Daher scheitern sowohl die Exaktprüfung als auch die
Teilstrukturprüfung regelkonform.

## Rechenweg

Das Profil bindet für visuelle PPB `update_rate = 0.05` und `stable_after = 3`
in [tools/_s2jw_default_live_profile.py](../../tools/_s2jw_default_live_profile.py:129).
Bei einer PPB-Übereinstimmung schreibt
[advance_ppb1_bank](../../mcm_field_organism/_ppb1_reference.py:619) je
Komponente in genau dieser Reihenfolge

```text
neu = (1.0 - update_rate) * alt + update_rate * eingang
```

fort. Die PPB wird nur nach einer konsolidierbaren Fast-Transition aufgerufen
([_tspm1_private.py](../../mcm_field_organism/_tspm1_private.py:2538)).

e03 legt bei identischem Eingang den Prototyp an. e04 und e05 aktualisieren
ihn je einmal. Die unabhängige Binary64-Nachrechnung
`0.95 * alt + 0.05 * eingang` reproduziert für alle 14 genannten Komponenten
den gespeicherten e05-Wert exakt, einschließlich der Hexdarstellung. Die
Abweichung entsteht damit beim wiederholten Rechenausdruck mit identischen
Eingängen, nicht beim Anlegen und nicht durch eine Mischung verschiedener
gebundener Wahrnehmungen.

## Abgrenzung

Dies ist eine nachgewiesene numerische Drift der bestehenden Prototypformel,
keine beabsichtigte inhaltliche Prototypänderung und kein Anschlussfehler. Die
historischen Records enthalten die Zwischenprototypen und vollständigen
Formationswerte nur über Digests; über die 30 gespeicherten Vergleichswerte
hinaus ist keine komponentenweise Historienprüfung möglich. Eine solche
fehlende Detailbindung wird nicht rekonstruiert.

Die kleinste sachlich begründete spätere Anschlussänderung wäre ausschließlich
eine versionierte Receipt-Erweiterung: pro PPB-Schritt die bereits verwendeten
Eingangs- und Vor-/Nachprototypwerte mit Binary64-Bindung ausgeben. Sie würde
die Evidenzlücke schließen. Sie begründet weder eine Toleranzschwelle noch eine
Änderung der PPB-Formel oder der Abrufregel.
