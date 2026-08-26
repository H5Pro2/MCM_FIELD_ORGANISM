# S1-TI: Statischer Kandidatenanschluss-Lueckenaudit

## Auftrag und Grenze

S1-TI gleicht den S1-PX-Funktions- und Falsifikationsvertrag mit der
vorhandenen Vier-Knoten-Matrix, der 40-Checkpoint-Profilachse, dem
S1-TG-Baselineatlas und dem S1-QA-Gatevertrag ab.

Der Audit waehlt keinen Kandidaten und keine Zustandsanatomie. Er bindet
keine Gleichung, Parameter, Werte oder Digests, implementiert keine Runtime
und fuehrt keinen Test, Comparator oder Feldlauf aus.

## Bereits vollstaendige Baseline-Seite

Der S1-TG-Atlas stellt fuer 14 registrierte Baselines bereits bereit:

- dieselben 17 F/T/I/C/R/U-Planrollen;
- dieselbe geordnete Achse aus 40 Checkpoints;
- je Checkpoint vollstaendige signed Rezeptor-, S- und H-Vektoren;
- gemeinsame Ereignis-, Zeit-, Geometrie- und Fixtureprovenienz;
- je Rolle genau eine Konfigurationsidentitaet;
- Frischstart-, Carry-, Privatstatus-, Align- und Kettendigests;
- 23 gebundene Rohkontraste je Modell;
- vollstaendige 320-Komponenten-Profile;
- die fixierte paarweise Referenzstruktur aller 14 Rollen.

Diese Baseline-Seite ist kanonisch publiziert und darf fuer einen spaeteren
Kandidaten weder neu gerechnet noch um Kandidatenfelder erweitert werden.
Sie bleibt unveraenderliche Referenz.

## Was die vorhandene Profilachse bereits abdeckt

Die Planrollen tragen die aeussere Lebenszyklustopologie:

```text
F - unterschiedliche Bildungsgeschichten und spaetere Probe
T - fruehe und spaetere Wiederholung
I - lokale, nichtlokale und Gap-Konkurrenz
C - lokale, nichtlokale und Gap-Belastung
R - frueher und spaeter Funktionsverlust
U - Wiederbeanspruchung und zeitangepasste Frischkontrollen
```

Die 40 Checkpoints liefern die gemeinsame Feldbeobachtung vor und nach den
gebundenen Ereignissen. Damit ist die Feldprofilseite fuer einen spaeteren
Kandidaten strukturell vorgegeben. Eine neue Expositionsfamilie ist fuer den
Anschluss nicht erforderlich.

## Nicht ausreichende vorhandene Belege

Ein `private_state_digest_or_none` belegt nur Identitaet und lueckenlosen
Carry eines privaten Zustands. Er belegt nicht:

- welche lokale endliche Ressource vorliegt;
- wie ihre Rollen direkt bilanziert werden;
- ob eine Differenz durch normale Feldgeschichte endogen entstand;
- ob Freigabe funktional und die Kapazitaet erneut nutzbar ist;
- ob eine Readoutablation nur die Rueckwirkung entfernt;
- ob der vollstaendig deaktivierte Pfad bitgenau dem Feldkern-Nullpfad
  entspricht.

Alte DTS-, G2- oder andere Kandidatensidecars duerfen diese Luecke nicht
schliessen. Sie gehoeren zu geschlossenen Zweigen und tragen nicht die
modellneutrale S1-PX-Semantik.

## Kleinste fehlende Anschlussoberflaeche

Es fehlt genau ein getrenntes, passiv lesbares
**Kandidaten-Beobachtungspaket** mit zwei strikt getrennten Ebenen.

### Ebene 1 - gemeinsames Feldprofil

Der Kandidat muss ohne Sonderachse ein vollstaendiges Profil mit exakt
derselben Rollen-, Checkpoint- und Komponentenordnung wie jede Baseline
liefern:

```text
17 Planrollen
40 Checkpoints
S und H an vier Knoten
320 signed Feldkomponenten
eine unveraenderte Kandidatenkonfiguration
vollstaendige gemeinsame Expositionsprovenienz
```

Nur diese Ebene darf spaeter gegen jedes der 14 fixierten Atlasprofile
gestellt werden. Kandidateninterne Werte duerfen das Profilmass weder
skalieren noch korrigieren.

### Ebene 2 - kandidateninterne Pflichtbelege

Getrennt vom Feldprofil muss dasselbe Paket direkt beobachtbare und
kanonisch gebundene Belege bereitstellen fuer:

- vollstaendige lokale Zustands- und Ressourcenbilanz;
- endogene Erreichbarkeit aus normaler Feldgeschichte;
- Zustand vor und nach Bildung, Konkurrenz, Gap, Freigabe und
  Wiederbeanspruchung;
- Readoutablation bei identischer Vorgeschichte und Feldlage;
- vollstaendig deaktivierten Nullpfad;
- direkte Freikapazitaet vor erneuter Nutzung;
- erneute lokale Beanspruchung durch die andere Geschichte;
- Konfigurations-, Quellen-, Carry- und Ereigniskettenidentitaet.

Diese Ebene bedient nur die harten S1-QA-Kandidatengates. Sie darf einer
Baseline nicht als Eingabe gegeben und nicht als Ersatz fuer ein
Feldprofilresiduum verwendet werden.

## Fehlender passiver Anschluss

Der bestehende S1-TG-Comparator ist absichtlich auf exakt 14 Baselineprofile
begrenzt und meldet `S1PX_CANDIDATE_GATES_NOT_APPLICABLE`. Er darf nicht
nachtraeglich in einen Kandidatencomparator umgedeutet werden.

Spaeter erforderlich ist ein eigener passiver Anschluss, der:

1. den unveraenderten S1-TG-Atlas als Referenz identifiziert;
2. genau ein vollstaendiges Kandidaten-Beobachtungspaket annimmt;
3. zuerst die internen Nullpfad-, Bilanz-, Ablations- und Lebenszyklusgates
   fail-closed prueft;
4. danach das Kandidatenfeldprofil unveraendert gegen alle 14 Baselines
   prueft;
5. bereits bei einer fairen Profilreproduktion innerhalb `D_rel <= 0.05`
   ausschliesslich `S1PX_BASELINE_REDUCED_STOP` zulaesst.

Der Anschluss darf kein Modell starten, keinen privaten Zustand parsen,
keine Parameter lesen und keine Baseline auslassen.

## Abdeckungsentscheidung

| S1-PX-Anforderung | Stand nach S1-TI |
|---|---|
| gemeinsame F/T/I/C/R/U-Exposition | vorhanden |
| 40-Checkpoint-S/H-Profilachse | vorhanden |
| 14 vollstaendige Baselineprofile | vorhanden und fixiert |
| gemeinsame Baseline-Profilmetrik | vorhanden und fixiert |
| Kandidatenprofil auf derselben Achse | fehlt |
| oeffentliche direkte Kandidatenbilanz | fehlt |
| Ablationsbeleg | fehlt |
| vollstaendiger Nullpfadbeleg | fehlt |
| Freigabe- und Wiederverwendungsbeleg | fehlt |
| passiver Kandidat-gegen-Atlas-Anschluss | fehlt |

Die Luecke liegt damit nicht mehr auf der Baseline- oder Expositionsseite.
Sie liegt vollstaendig in der noch nicht definierten Kandidatenbeobachtung
und ihrer passiven Anschlussgrenze.

## Aussagegrenze

S1-TI bestaetigt keine Kandidatenfunktion und keine hypothetische
MCM-Memory. Der Audit zeigt nur, welche technische Oberflaeche vor einer
spaeteren Kandidatenwahl fehlen wuerde. Geschlossene Zweige bleiben
geschlossen, und der primaere MCM-Wahrnehmungsfeldkern bleibt unveraendert.

## Abschluss und naechster Schritt

```text
S1_TI_CANDIDATE_CONNECTION_GAP_LOCALIZED
FIXED_BASELINE_ATLAS_AND_SEPARATE_CANDIDATE_OBSERVATION_PACKAGE_REQUIRED
CANDIDATE_FIELD_PROFILE_AND_INTERNAL_EVIDENCE_MUST_REMAIN_SEPARATE
NO_CANDIDATE_NO_EQUATION_NO_IMPLEMENTATION_NO_RUN
```

Der einzige naechste Schritt ist S1-TJ als statischer Vertrag der
modellneutralen Kandidaten-Beobachtungshuelle. Er soll ausschliesslich
Feldprofil-, Bilanz-, Provenienz-, Ablations-, Nullpfad-, Freigabe- und
Wiederverwendungsrollen sowie ihre Informationssperren binden. Keine
konkrete Ressourcenanatomie, Gleichung, Parameter, Werte, Implementierung,
Testausfuehrung oder Ergebnisentscheidung ist dabei zulaessig.
