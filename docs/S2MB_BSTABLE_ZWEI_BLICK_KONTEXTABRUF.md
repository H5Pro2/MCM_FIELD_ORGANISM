# S2-MB: B_STABLE-Zwei-Blick-Kontextabruf

## Funktionsgrenze

S2-MB prueft die qualifizierte fluechtige S2-MA-Zwei-Blick-Evidenz gegen
tatsaechlich gebildete visuelle `B_STABLE`-Slots. Die beiden 96er-Blicke
bleiben eine interne, nach der Entscheidung geloeschte Funktion von
`A_RECENT`. Die Slow-Slots werden waehrend des Abrufs ausschliesslich gelesen.

Der Lauf verwendet unveraendert den versiegelten S2-LZ-Korpus, dessen zwei
Masken und dessen vor den Holdouts gebildete `UNION_FORM_192`-Huellen. Es
entsteht weder ein neuer Deskriptor noch eine neue Distanzgrenze. Das Zentrum
jeder Laufhuelle wird jedoch nicht aus einem Forschungszentroid uebernommen,
sondern aus dem tatsaechlichen PPB-Prototyp des gebundenen stabilen Slots
projiziert.

## Statische PPB-Erreichbarkeit

Die ersten drei S2-LZ-Basisreferenzen werden jeweils viermal bitidentisch
gebildet:

```text
source-001 x4, source-007 x4, source-013 x4
```

Die kleinsten Abstaende zwischen diesen drei Rezeptorzustaenden betragen
`0.026143791`, `0.027886710` und `0.036601307`; sie liegen damit jeweils ueber
der unveraenderten visuellen Slow-Grenze `0.01`. Innerhalb jeder Viererfolge
entsteht Support `3`. Fuer `source-001` beginnt PPB nach der Fast-Neuanlage
mit `CREATED -> MATCHED -> MATCHED`; `source-007` und `source-013` erhalten
ueber den bereits vorhandenen Fast-Zusammenhang jeweils zusaetzlich ein
supportgesaettigtes `MATCHED`. Diese Binary64-Uebergangsfolgen binden die
spaeteren Prototypdigests.

Danach folgen neun bitidentische Druckformationen aus der bereits gebundenen
S2-JX-D1-RGB-Fixture und dem vorhandenen D_FAR-PCM. D1 liegt zu den drei
Familienrezeptorzustaenden bei `0.463139978` bis `0.469094953`. Es belegt den
vierten visuellen Slow-Slot und veraendert die drei Familienslots nicht. Die
neun Druckformationen entfernen die Familien-AV-Zustaende vollstaendig aus
B4; der alte Fast-Zusammenhang ist spaetestens vor Druckschritt acht
abgelaufen. Die vier visuellen Slow-Slots bleiben mit Support `3` erhalten.

Der D1-Druckslot wird beim Abruf nicht verborgen. Seine aus vier
bitidentischen Bildungseingaengen nach der bestehenden S2-LZ-Regel abgeleitete
Kalibrationshuelle besitzt Radius `0.0` und wird wie jeder andere reale
stabile Slot vollstaendig geprueft.

## Lauf und Entscheidung

- `21` atomare AV-Memoryformationen;
- `40` spaetere visuelle Feldkontakte fuer `20` Zwei-Blick-Faelle;
- jede Fallentscheidung ausschliesslich aus den beiden beobachteten
  96er-Sichten und allen vier realen visuellen Slow-Slots;
- `CURRENT_ONLY` erzeugt keine Kontexthypothese;
- Kontextarm und unabhaengige Direktbaseline erhalten identische Slot-,
  Masken-, Quellen- und Zeitbindungen;
- Feldkontakte werden unabhaengig fortgeschrieben und durch Enthaltung oder
  Fehler der Kontextentscheidung nicht zurueckgenommen;
- Memory-Pre-/Postdigest bleibt ueber alle 40 Abrufblicke identisch.

Prospektiv zugelassen werden `case-001`, `case-002`, `case-004`, `case-005`
und `case-006`. `case-003` bleibt wie in S2-LZ ein konservativer bekannter
Informationsverlust. Die nicht stabilisierte vierte Familie, unbekannte und
mehrdeutige Formen sowie unvereinbare Blickpaare muessen enthalten werden.
Eine vollstaendige technische Ausfuehrung mit anderer Entscheidung ist eine
Funktionsfalsifikation, kein Anlass fuer Fixture- oder Schwellenanpassung.

## Aussagegrenze

Ein Erfolg belegt den Pfad

```text
Wahrnehmungsstrom -> fluechtige A_RECENT-Zwei-Blick-Evidenz
-> realer B_STABLE-Slotscan -> kontrollierte Kontexthypothese
```

fuer diesen kleinen versiegelten Korpus. Die Direktbaseline darf die Funktion
vollstaendig erklaeren. Nicht belegt werden allgemeine Open-Set-Erkennung,
Semantik, automatische Maskenbildung, Feldrueckwirkung oder eine neue
Memorymechanik.

## Ergebnis

Die neutrale Qualifikation bestand einmalig mit `10/10`, Exit-Code `0` und
`OK`. Der anschliessende Lauf
`s2mb-bstable-two-view-context-20260905-01` wurde genau einmal ausgefuehrt und
einmal read-only als `RECORDING_COMPLETE` verifiziert.

- `21` reale Formationen, `40` spaetere Blickkontakte und `20` Faelle;
- alle vier visuellen Slow-Slots waren real gebildet und stabil;
- `5/6` stabilisierte bekannte Holdouts wurden zugelassen;
- ein bekannter Holdout wurde konservativ abgewiesen;
- alle `14` unbekannten, mehrdeutigen oder inkompatiblen Faelle enthielten;
- keine falsche Kontextzulassung;
- Kontextarm und unabhaengige Direktbaseline waren in allen Faellen gleich;
- die `21` Formationen schrieben den Memoryzustand; ausschliesslich die `20`
  spaeteren Abruf- und Kontextfaelle waren read-only;
- der Memory-Pre-/Postdigest dieser Abrufphase war identisch, alle
  Feldkontakte blieben erhalten.

Damit ist fuer diesen versiegelten Korpus der begrenzte Pfad von fluechtiger
Zwei-Blick-Evidenz zu real gebildeten `B_STABLE`-Kandidaten bestaetigt. Der
einzige bekannte Fehler ist konservativer Informationsverlust, keine
Fehlzulassung. Das Ergebnis belegt keine allgemeine Open-Set-Erkennung.
