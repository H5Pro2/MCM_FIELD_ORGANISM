# W2-C: Additive kuratierte current_api

Stand: 2026-08-09

Entscheidung: `CURATED_CURRENT_API_ADDED_ROOT_COMPATIBILITY_PRESERVED`

Formaler Forschungslauf: nein

## Umsetzung

Das neue Modul `mcm_field_organism.current_api` stellt eine additive,
explizite Oberflaeche fuer den aktuellen kontrollierten Entwicklungsweg
bereit. Die bestehende Root-API bleibt unveraendert kompatibel.

Die Fassade besteht aus zwei disjunkten Manifesten:

```text
CURRENT_CONTROLLED_FIELD_EXPORTS: 114
F3_REFERENCE_EXPORTS:              16
Gesamt:                            130
doppelte Namen:                      0
```

## Neutraler Kern

Der neutrale Kern exportiert ausschliesslich Rollen aus:

- geraeteneutralen kontrollierten Audioquellen;
- kontrollierten Video- und Browserpayloadquellen;
- Audio- und Videorezeptoren;
- Rezeptorvertrag, Verteilung und Dockanatomie;
- Organismuszeit, Zeitpartition und asynchronen Abschlussereignissen;
- transienter Dock- und Neuroneneingabe;
- gemeinsamem neutralem Feld;
- neutralen Feldsitzungen;
- Snapshot, Restore und Schemamigration;
- reduzierter AV-Sequenzuebergabe in das neutrale Feld.

`AudioFrameSource` und `VideoFrameSource` werden additiv als geraeteneutrale
Protokolle angeboten. Sie waren bisher keine Root-Exporte.

## Getrennter F3-Referenzabschnitt

`F3_REFERENCE_EXPORTS` enthaelt sichtbar getrennt:

- M-Substratzustand und uniforme Referenzkonstruktion;
- explizites Anheften des uniformen M-Zustands;
- direkte F3-Kopplungsberechnung;
- F3-Feldaktivierung und transiente Fortschreibung;
- zugehoerige technische Ergebnis- und Fehlerrollen.

F3 wird damit nicht in den neutralen Kern umbenannt. Es bleibt optionale
Engineeringreferenz ohne Memoryclaim.

## Harte Ausschluesse

Der Manifesttest weist insbesondere ab:

```text
SoundDeviceInputSource
OpenCVVideoFrameSource
capture_live_audio_video_field
alle Z4-Ausfuehrungsrollen
F3-Forschungsrunner
visuelle Effektor- und Presenterrollen
lokale synaptische Memorykandidaten
Kontaktmaterial und radiale Morphologie
S1-B-Akkommodationskandidat
```

Keiner dieser Namen ist Attribut oder `__all__`-Eintrag von `current_api`.

## Kompatibilitaet

Fuer jeden Namen, der bereits aus der Root-API exportiert wird, bindet der
Test exakte Objektidentitaet zwischen Root und `current_api`. Die bestehende
Root-Oberflaeche wird weder verkleinert noch umgeleitet.

Die beiden additiven Protokolle bleiben bewusst nur in `current_api` und
ihren Ursprungsmodulen verfuegbar.

## Verifikation

Geprueft wurden:

- exakte Manifestkomposition und Eindeutigkeit;
- Vorhandensein aller 130 deklarierten Rollen;
- Identitaet bestehender Root-Exporte;
- additive Protokollgrenze;
- Negativmanifest gegen Live, Z4, Runner, Effektor und Kandidaten;
- strikte Trennung des neutralen Kerns vom F3-Referenzmanifest;
- gemeinsame Feldkonstruktion und Feldsitzungen;
- kontrollierte Browserquelle und Browser-Rezeptorbruecke;
- F3-Runtime als Referenz;
- W2-B-Audioquellengrenze.

Der fokussierte Verbund besteht mit:

```text
65 passed
282 subtests passed
3.08 s
```

`current_api.py` und sein Manifesttest bestanden zusaetzlich `py_compile`.

## Aussagegrenze

W2-C ist eine additive API-Bereinigung. Die Fassade aktiviert keinen Browser,
keine Kamera, kein Live-Mikrofon und keinen Effektor. Sie erzeugt keinen
Forschungsbefund und belegt kein Memory, Lernen, Feldzeit, Organisation,
Semantik, Selbstregulation oder KI. Lauf 197 bleibt unberuehrt.

## Bester naechster Schritt

W2-D prueft statisch den transitiven lokalen Importgraphen aller Module, aus
denen `CURRENT_CONTROLLED_FIELD_EXPORTS` stammen. Jeder direkte oder
transitive Import wird gegen dieselben Kategorien aus W2-A klassifiziert.

Ziel ist zu unterscheiden:

```text
saubere aktuelle Kernabhaengigkeit
notwendige Referenzabhaengigkeit
historische oder inaktive Durchleitung
```

W2-D veraendert noch keinen Code. Erst ein konkret lokalisierter transitiver
Leak darf danach kompatibel getrennt werden.

## Spaeterer Auditstand W2-D

W2-D erreicht 35 lokale Module ueber 97 Kanten. Es gibt keinen historischen
oder pausierten transitiven Pfad. Vier Referenzabhaengigkeiten sind zulaessig;
vier gemischte Modulgrenzen bleiben. Naechster Schritt ist W2-E: das
geraeteneutrale Zeitmodell kompatibel aus `receptor_time_alignment` loesen.
