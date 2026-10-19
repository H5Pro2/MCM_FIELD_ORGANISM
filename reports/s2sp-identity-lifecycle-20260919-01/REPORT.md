# S2-SP: identitätserhaltender Lebenszyklusvergleich

## Auftrag und technischer Abschluss

Auftragskennung: `s2sp-identity-lifecycle-20260919-01`.

Der private Zweiarmvergleich wurde genau einmal ausgeführt. Beide Arme
verarbeiteten dieselben zwölf gemeinsam materialisierten Formationsquellen und
16 visuellen Wertefolgen, jedoch mit getrennten Memoryzuständen. Der
historische Arm nutzt `historical.v1`; der private Arm nutzt
`identity-preserving.v1`. Die unabhängige read-only Verifikation bestätigt
`RECORDING_COMPLETE` mit Record-Digest
`928f38bc28bafc7f298b6a2af7d7a3ba40a45ff74647f2e59ce4b3acbf812b17`.

Gebundener Umfang: je Arm 16 Ereignisse, zwölf Formationen und vier
read-only Hinweise; gemeinsam zwölf Audioanalysen und 16 visuelle Analysen.
Es wurden keine Feldkontakte erzeugt. Die drei gespeicherten JSON-Belege
belegen zusammen 68.570 Byte und liegen damit unter dem privaten
262.144-Byte-Limit.

## Beobachtungen

| Kontrolle | Historisch | Identitätserhaltend | Einordnung |
|---|---:|---:|---|
| e05, wiederholtes Ziel: exakte visuelle Slow-Kandidaten | 0 | 1 | Bestätigter unmittelbarer Erhaltungseffekt des privaten Modus. |
| e13, nach Konkurrenzdruck: exakte visuelle Slow-Kandidaten | 0 | 0 | Der gewünschte B-Abruf ist nicht bestätigt. |
| e13, exakte Fast-Kandidaten | 0 | 0 | Die frühere Fast-Spur ist nicht mehr anwendbar. |
| e13, exakte B4-Kandidaten | 2 | 2 | Beide Arme enthalten weiterhin zwei passende B4-Kandidaten. |
| e15, nach zweiter C4-Formation: exakte visuelle Slow-Kandidaten | 0 | 0 | Kein nachträglicher exakter Zielabruf. |
| e16, Variantenkontrolle: exakte visuelle Slow-Kandidaten | 0 | 0 | Keine zusätzliche exakte Slow-Zulassung im privaten Arm. |

Die Änderungskontrolle e07 ist in beiden Armen gleich: Nur Komponente 1
weicht ab; der gespeicherte Wert ist jeweils exakt
`0.95 * vorheriger_wert + 0.05 * eingangswert = 0.8470588235294118`.
Damit ist die private Ausnahme auf bitgleiche Komponenten begrenzt; geänderte
Komponenten verwenden die historische Fortschreibung.

## Grenze

Der bei e05 im privaten Arm sichtbare Slow-Kandidat in `slot.000` hat bei
e13 einen anderen Digestanteil. Das beweist für sich keine Ersetzung: Die
Slow-Kennung besteht aus Bank, fester Slot-ID und dem Digest des gesamten
veränderlichen Slot-Payloads, einschließlich Prototyp, Support und
`last_selected_step`. Die Transaktionsbelege zeigen bis e12 reguläre
`ADVANCED`-Fortschreibungen und aufeinanderfolgende globale
PPB-Schrittstände, speichern aber die ausgewählte visuelle PPB-Slotbindung
nur als Digest. Aus dem vorliegenden Record lässt sich daher nicht
begründen, bei welchem Ereignis oder aus welchem Grund die Zielgeneration
ihre Exaktheit verlor.

Der Lauf bestätigt daher weder die verlangte Erhaltung eines exakten
visuellen B-Abrufs nach A-Verdrängung noch die beabsichtigte Ersetzung genau
dieser Zielgeneration erst bei e14. Das ist ein fachlicher Gegenbefund,
kein technischer Fehler und keine Rechtfertigung für eine Regel-, Schwellen-
oder Kernänderung. Ein weiterer Lauf wurde nicht gestartet.

## Aussagegrenze

`identity-preserving.v1` behebt die nachgewiesene Rundungsdrift für unmittelbar
wiederholte, bitgleiche Komponenten. Seine Wirkung über Konkurrenz,
Fast-Verdrängung und den vollständigen PPB-Lebenszyklus ist auf dieser Folge
nicht nachgewiesen. Historische Defaults und öffentliche Abrufregeln bleiben
unverändert.
