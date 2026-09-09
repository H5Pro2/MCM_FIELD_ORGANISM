# S2-NZ: einmaliger diagnostischer Stoerungsvergleich

ID `s2nz-diagnostic-disturbance-20260909-01`.
Ein `run_main_once`-Aufruf, danach genau eine unabhaengige read-only
Verifikation und erst danach eine getrennte Diagnoseauswertung.
**RECORDING_COMPLETE / S2NZ_DIAGNOSTIC_VERIFIED / DIAGNOSTICALLY_DESCRIBED**.
Exit-Code 0; kein Retry oder zusaetzlicher Vorlauf. Technischer Abschluss
und die folgenden gemischten diagnostischen Befunde sind getrennte Aussagen.

## Technischer Abschluss

- 30/30 Fenster in unveraenderter versiegelter Reihenfolge regeneriert;
  alle 30 Payloadhashes vor der jeweiligen Analyse bestaetigt.
- Genau 30 direkte Rezeptoranalysen und 30 NJ-Projektionen. Keine rollende
  Pipeline, Deduplizierung oder separate Vorabmaterialisierung.
- 18 gebundene Prognosestellen, zwoelf LOCAL-Fits pro Implementierung;
  je 66 Armprognosen/MAE. Primaer- und unabhaengige Direktrechnung bitgleich.
- Prognosen, LOCAL und Empfehlung vor dem jeweiligen Zielzugriff gebunden.
  Empfehlung ausschliesslich aus unmittelbar vorherigen Fehlern derselben
  Folge; frisches Praefix und leere Fehlerhistorie je Folge.
- Beide historischen NX-Freeze-Payloads unveraendert uebernommen. Keine
  Lernkettenrechnung, Updates oder Owneroeffnung. Saubere Kontrollfolgen
  liefern weder operative Zusatzinformationen noch Ersatz-Ziele.
- Ziel ist auch gestoert der naechste tatsaechlich beobachtete Halbvektor.
  Keine Entrauschung, kein verborgenes sauberes Rekonstruktionsziel.
- Hoechstens ein 19.200-Byte-PCM-Fenster gleichzeitig; keine Rohpayloadablage.
  Roh-/Halbvektoren und ihre Bindungen bleiben im Forschungsbeleg erhalten.
- Kontrollierter Lifecycle abgeschlossen; NZ-, Quellen-, NY-, NW- und
  NV-Hauptgate anschliessend False. Keine Memory-, Feld-, Kontext- oder
  Runtimeaufrufe. ME/MI und Systemintegration bleiben gesperrt.

Die einmalige Offline-Pruefung berechnete 1.440 Halbierungen aus gespeicherten
Rohwerten nach, beide Prognose-/Fehlerrechnungen und die Herkunftsbindungen.
Keine Payloadregeneration, Rezeptor- oder NJ-Wiederholung in der Verifikation.
Sie belegt nicht allein durch Digests die historische CPU-Aufrufordnung;
diese Grenze des kontrollierten, zuvor neutral qualifizierten Aufrufpfads bleibt.

## Diagnostischer Schwerpunkt: N=4, D=4

Alle vier vorgegebenen gestoerten Fortsetzungsstellen sind enthalten.
Gewinn = Kontroll-MAE minus Arm-MAE, keine relative Verbesserung.
Die Empfehlungen lauten H1 an p05/p06 und H2 an p11/p12.

| Stelle | Empfehlungs-MAE | LOCAL-MAE | Gewinn gegen LOCAL | Befund |
| --- | ---: | ---: | ---: | --- |
| p05 / s02 k3 | 6.698412863899002E-06 | 6.696069968526233E-06 | -2.3428953727684264E-09 | LOSS |
| p06 / s02 k4 | 6.601882585813799E-06 | 6.6027196024974685E-06 | 8.370166836695951E-10 | WIN |
| p11 / s04 k3 | 9.214864460992774E-06 | 9.584611210964812E-06 | 3.697467499720382E-07 | WIN |
| p12 / s04 k4 | 1.0407291467035624E-05 | 1.0735936800816341E-05 | 3.286453337807176E-07 | WIN |

Empfehlung gegen LOCAL: **3 WIN, 0 TIE, 1 LOSS / D=4**.
Gegen PERSIST: **4 WIN / D=4**. Alle vier Empfehlungen sind NEXT_BEST,
aber p05 verliert trotzdem gegen LOCAL. Kein Gleichsetzen dieser Urteile.

Die festen Historien werden separat ausgewiesen: H1 gegen LOCAL 1 WIN und
3 LOSS; H2 gegen LOCAL 2 WIN und 2 LOSS. H2 verliert an beiden gestoerten
H1-Fortsetzungen auch gegen PERSIST. Ein fester Historienvorteil wird nicht
als tatsaechlich ausgegebene Empfehlung ausgewiesen.

## Saubere Kontrollen und Wechselverluste

Die vier sauberen Fortsetzungsstellen haben ebenfalls 3 WIN und 1 LOSS der
Empfehlung gegen LOCAL. Die absoluten Gewinne betragen
1.5685828352675306E-13, 3.3494353737369643E-13 und 4.775817612846397E-12;
an p09 besteht ein Verlust von 3.685373336196542E-13.
Die absoluten Unterschiede unter Stoerung sind damit anders verteilt und
bei H2 groesser als die formal sehr kleinen sauberen Unterschiede. Das
begruendet keine praktische Relevanz oder allgemeine Stoerungsrobustheit.

| Wechselstelle | Empfehlung / Historienurteil | Gewinn gegen LOCAL | Gewinn gegen PERSIST |
| --- | --- | ---: | ---: |
| p14 sauber, erstes Wechselziel | H2 / NEXT_WRONG | 4.775817762092682E-12 | -0.00047340934627660564 |
| p15 sauber, Folgefenster | H1 / NEXT_BEST | 0.012194432957563499 | -0.0010257021890699356 |
| p17 gestoert, erstes Wechselziel | H2 / NEXT_WRONG | -2.579665634187475E-07 | -0.00047505587585993 |
| p18 gestoert, Folgefenster | H1 / NEXT_BEST | 0.012133166551105336 | -0.0010216592807428086 |

An beiden unangekuendigten Wechselzielen ist die Empfehlung falsch relativ
zur anderen Historie. An den Folgefenstern ist sie wieder NEXT_BEST,
verliert aber weiterhin gegen PERSIST. Der grosse LOCAL-Vorteil dort ist
kein Ausgleich dieser Verluste: LOCAL extrapoliert selbst unpassend.
Keine Wechselerkennung aus Fehlerhoehe oder nachtraegliche Bestarmwahl.

## Vollstaendigkeit und Abdeckung

Alle **66 MAE**, absoluten LOCAL-/PERSIST-Gewinne und 18 Empfehlungen bzw.
Enthaltungen stehen in [EINZELWERTE.md](EINZELWERTE.md) sowie unveraendert in
[evaluation.json](evaluation.json). Saubere und gestoerte Folgen sowie
erste Wechselziele und Folgefenster bleiben getrennt.

Abdeckung **D=12/18**, bei ausreichendem Praefix **12/12**. Sechs regulaere
ABSTAIN_INSUFFICIENT_PREFIX, keine ABSTAIN_TIE. Zehn NEXT_BEST und zwei
NEXT_WRONG unter den zwoelf Empfehlungen. Jede Folge N=3/D=2.
Keine Enthaltung erhaelt eine Ersatzprognose, einen Nullfehler oder einen
kuenstlichen Erfolg. Der Schwerpunktnenner bleibt unveraendert N=4.
Wiederholte gemeinsame Praefixe und saubere/gestoerte Kontrollpaare werden
nicht als unabhaengige Replikate ausgegeben.

## Ressourcen und Integritaet

Pro Implementierung: je 2.304 Prognose-Subtraktionen/Multiplikationen/
Additionen, 864 Persistenzkopien, zwoelf LOCAL-Fits/Divisionen, je 1.152
LOCAL-Differenzen/Produkte/Additionen, 3.168 Fehlerterme, 66 MAE,
18 Empfehlungsrechnungen und 96 Gewinndifferenzen.
Offline separat: 1.440 Halbierungen, je 4.608 Prognoseoperationen, 1.728
Persistenzkopien, 24 LOCAL-Fits/Divisionen, je 2.304 lokale Operationen,
6.336 Fehlerterme, 132 MAE, 36 Empfehlungs- und 192 Gewinnpruefungen.
Auswertung: 24 feste LOCAL-Gewinndifferenzen, 96 WIN/TIE/LOSS-Beziehungen,
18 Empfehlungsurteile, null Relevanzvergleiche. Alle gebundenen Grenzen eingehalten.

Gesamtbeleg **847.991/2.097.152 Byte**, Verifikation **1.434/262.144 Byte**,
Auswertung **17.490/262.144 Byte**, Vorregistrierung **10.559/65.536 Byte**.
Quellen-, Profil-, Code- und Freeze-Bindungen unveraendert. Der Pruefbeleg
bindet identische Datei-SHA-256 vor/nach der Verifikation.

| Bindung | Digest |
| --- | --- |
| Ausfuehrungswurzel | 7f424a6dbc694b4f8cb20160ce8a294e0d4923137b9f0fcdf83aeb5a48e0d113 |
| Gesamtbeleg record_digest | 039c34c3d8966b12445db4ec1edc88870ab7aef90c14da01feb98dbaa59b04e3 |
| Gesamtdatei SHA-256 vor/nach Verifikation | 3fd0577b4092c5bd6268cc9ec6c5cc70ea1d2629c58c893ab4003a2330d5db12 |
| Verifikationsdigest | 511937c24c682c04cfc7acdcd73a68db79ffa6bcfec9654113018c1ab80c8fd3 |
| Auswertungsdigest | 812b840d412c1cb8a420929bedc417c20c86fa2700099389ceafda844a015848 |

## Aussagegrenze und Rueckmeldung

Ein begrenzter gemischter diagnostischer Befund auf genau dieser vorab
festgelegten Stoerung und diesen Quellen. Keine praktische Mindestschwelle,
kein Gesamtstatus praktischen Nutzens oder Robustheit. Eine konkrete
Nutzungsanforderung fehlt weiterhin; sie wird nicht aus diesen Ergebnissen
abgeleitet. Verluste bleiben sichtbar und werden nicht mit Gewinnen verrechnet.

Kein Parameterwechsel, Quellenersatz, Clipping, Eingangsabschwachung oder
Retry. Historische Belege und Versiegelung bleiben unveraendert. Keine
Integration, weitere Stoerparametersuche oder Lernbindung aus diesem Befund.

WEITER: Am besten geht es jetzt mit der Analystenbewertung der absoluten
Einzelunterschiede und der getrennten Wechselverluste weiter; eine spaetere
anwendungsbezogene Pruefung benoetigt eine eigene Begruendung und Freigabe.
