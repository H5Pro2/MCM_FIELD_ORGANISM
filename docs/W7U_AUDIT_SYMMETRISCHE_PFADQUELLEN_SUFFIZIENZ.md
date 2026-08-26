# W7-U: Audit der symmetrischen Pfadquellen-Suffizienz

## Entscheidung

`REGISTERED_SOURCE_INVENTORY_PARTIALLY_SUFFICIENT_SYMMETRIC_ADDITION_REQUIRED`

W7-U prueft statisch, ob das in W7-M eingefrorene Quelleninventar alle sieben
vorregistrierten Pfade segmentweise belegen kann. Es wurden keine Quellen
erzeugt, keine Sequenzen ausgefuehrt und keine Pfadmatrix gestartet.

## 1. Geprueftes Inventar

`MCMF3K2BSource` registriert derzeit:

- einen kombinierten viersekundigen A-Praefix `contact_a` auf 0 bis 4;
- vier einzelne B-Schritte `contact_b_steps` auf 4 bis 8;
- vier einzelne Unterbrechungsschritte `interruption_steps` auf 4 bis 8;
- fuenf einzelne Proben `probes` fuer Checkpoint 0 bis 4;
- genau einen A-Praefixdigest, vier B-Schrittdigests, vier
  Unterbrechungsdigests und fuenf Probendigests.

Die interne Erzeugung baut vor der Kombination zwar vier `contact_a_steps`
auf, gibt sie aber nicht aus und registriert keine Einzeldigests. Ein
viersekundiger B-Praefix auf 0 bis 4 wird derzeit nicht erzeugt oder
registriert.

## 2. Pfadweise Deckung

| Pfad | Praefix | Fortsetzung | Probe | Registrierter Stand |
| --- | --- | --- | --- | --- |
| `AB` | A 0-4 | B-Schritte 4-8 | P0-P4 | vollstaendig |
| `AG` | A 0-4 | G-Schritte 4-8 | P0-P4 | vollstaendig |
| `UB` | uniform bei 4 | B-Schritte 4-8 | P0-P4 | vollstaendig |
| `UG` | uniform bei 4 | G-Schritte 4-8 | P0-P4 | vollstaendig |
| `BA` | B 0-4 | A-Schritte 4-8 | P0-P4 | beide Kontaktrollen fehlen |
| `BG` | B 0-4 | G-Schritte 4-8 | P0-P4 | B-Praefix fehlt |
| `UA` | uniform bei 4 | A-Schritte 4-8 | P0-P4 | A-Schritte fehlen |

Damit sind vier von sieben Pfaden mit dem registrierten Inventar technisch
belegbar. Drei Pfade sind nicht belegbar. Das kanonische Pfadinventar in W7-M
ist daher umfangreicher als sein aktuelles segmentweises Quelleninventar.

## 3. Warum eine reine Rollenumbenennung nicht reicht

Die gespiegelte B-A-Linie darf nicht erzeugt werden, indem vorhandene
A-B-Sequenzen nur als B-A bezeichnet oder Regionsnamen vertauscht werden.
A und B sind unterschiedliche kontrollierte Rezeptormuster. Ein B-Praefix
muss B tatsaechlich von 0 bis 4 darbieten; eine A-Fortsetzung muss A
tatsaechlich in vier einzelnen Schritten von 4 bis 8 darbieten.

Auch eine nachtraegliche Zeitverschiebung vorhandener Sequenzobjekte ohne
neue Digestbindung ist unzulaessig. Organismuszeiten, Snapshot-IDs und
Quelldigests sind Bestandteile des Kausalvertrags.

## 4. Vorhandene Weltbasis

Die kontrollierten Phasen selbst sind vorhanden:

- A ist `same.phases[0]`;
- G ist `same.phases[1]`;
- B ist `changed.phases[2]`;
- P ist die gemeinsame Probe des Holdout-Weltpaars.

`_phase_steps` kann dieselbe Phase mit explizitem Startzeitpunkt und fester
Wiederholungszahl deterministisch reduzieren. Fuer A und B muessen daher
keine neuen Medien, Labels, Bedeutungen oder Ergebnisanpassungen eingefuehrt
werden. Die Luecke liegt in der technischen Exposition und Vorabbindung der
symmetrischen Zeitrollen.

## 5. Minimal erforderliche additive Quellenfamilie

Erforderlich sind genau:

1. `contact_b_prefix_steps`: vier B-Wiederholungen auf 0 bis 4;
2. `contact_b_prefix`: deren verlustfreie Kombination mit eigenem Digest;
3. `contact_a_continuation_steps`: vier A-Wiederholungen auf 4 bis 8;
4. vier Digests der einzelnen A-Fortsetzungsschritte;
5. ein kanonischer Inventardigest, der vorhandene W7-M-Digests und die neuen
   symmetrischen Digests gemeinsam bindet.

Die vorhandenen G-Schritte und Proben bleiben unveraendert. Der vorhandene
A-Praefix und die vorhandenen B-Fortsetzungsschritte werden nicht ersetzt.

## 6. Symmetriebedingungen

Vor einer Verwendung muss die additive Familie statisch und technisch
nachweisen:

- A- und B-Praefix besitzen denselben Viersekundenhorizont;
- A- und B-Fortsetzungen besitzen dieselben vier Einsekundenintervalle;
- Audio-/Video-Supportzaehlung und Abschlusskorridore sind je Zeitrolle
  gleich aufgebaut;
- beide Richtungen verwenden dieselben G-Schritte und Proben;
- Modalitaets-, Geometrie-, Uhr- und Tickratenrollen bleiben identisch;
- jeder neue Digest ist vor jeder Modell- oder Observerauswertung fixiert.

Die bereits dokumentierten Gesamtzahlen des A-Praefixes betragen 391 Audio-
und 40 Videoframes. Die vier vorhandenen B-Schritte besitzen zusammen
dieselbe zeitliche Vier-Schritt-Struktur; die exakte symmetrische
Supportgleichheit muss die spaetere additive Implementierung als Test binden,
nicht aus diesem Audit behaupten.

## 7. Integrationsgrenze

Die additive Quellenfamilie soll den bestehenden W7-M-Adapter nicht
stillschweigend veraendern. Sie muss:

- an dessen Matrix-, Regions- und vorhandenen Quelldigests gebunden sein;
- einen eigenen technischen Inventardigest besitzen;
- explizit an W7-R uebergeben werden;
- von W7-R nur als zulaessige Erweiterung des bekannten Quelldigestinventars
  akzeptiert werden;
- `current_api`, Browserpfade und vorhandene Reports unberuehrt lassen.

Eine Aenderung des bestehenden W7-M-Matrixdigests ohne expliziten neuen
Vertrag ist gesperrt.

## 8. Harte Stopplinien

Die weitere Arbeit muss stoppen, wenn:

- BA, BG oder UA mit dem aktuellen Inventar als vollstaendig ausgegeben
  werden;
- A und B nur umbenannt statt tatsaechlich in der gespiegelten Zeitrolle
  reduziert werden;
- Sequenzzeiten ohne neue Digestbindung verschoben werden;
- bestehende W7-M-Quelldigests ersetzt oder ueberschrieben werden;
- Supportunterschiede zwischen A- und B-Zeitrollen ungeprueft bleiben;
- neue Weltinhalte, Labels oder Ergebniswissen in die additive Familie
  gelangen;
- W7-R neue Digests ohne explizite Inventarbindung akzeptiert;
- vor vollstaendiger Siebenpfaddeckung eine Hauptmatrix gestartet wird.

## 9. Aussagegrenze

W7-U ist ein statischer Null- beziehungsweise Lueckenbefund fuer die
registrierte Quellenabdeckung. Er bewertet keine Feld- oder Observerwerte.
Daraus folgen keine Feldfunktion, kein Memory, keine
Ressourcenwiederverwendung, keine Feldzeit, Organisation, Semantik,
Selbstregulation oder KI.

## 10. Verwendete Quellen

- `mcm_field_organism/mcm_f3_k2b_source.py`
- `mcm_field_organism/controlled_audio_video_test_world.py`
- `tests/test_mcm_f3_k2b_source.py`
- `docs/W7L_VORREGISTRIERUNG_KAPAZITAETSFUNKTION_UND_GEGENBASELINES.md`
- `docs/W7M_IMPLEMENTIERUNG_IN_MEMORY_KAPAZITAETSFUNKTIONSMATRIX_ADAPTER.md`
- `docs/W7R_IMPLEMENTIERUNG_P0_S_ABSCHLUSSZUSTANDSPRODUZENT.md`
- `docs/W7T_IMPLEMENTIERUNG_SEGMENTUEBERGREIFENDE_OBSERVERFORTSETZUNG.md`

## 11. Naechster Schritt

W7-V muss statisch den Vertrag der additiven symmetrischen Quellenfamilie
binden: Identitaeten, Zeitintervalle, Supportgleichheit, Digests,
Inventarbindung und explizite W7-R-Zulassung. Noch keine Implementierung,
Pfadmatrix, Browserausfuehrung oder Forschungsauswertung.
