# W7-F: Mathematischer Minimalvertrag fuer kapazitaetsbegrenzten Kantenaustausch

Stand: 2026-08-09

Entscheidung: `CAPACITY_LIMITED_EDGE_EXCHANGE_MATHEMATICALLY_ADMISSIBLE`

Arbeitsart: statischer Gleichungs-, Invarianz- und Reduktionsaudit

Runtimeaenderung: nein

## Ausgangspunkt

W7-E bindet genau eine transparente Engineering-Eigenschaft: Zufluss zu
einem Feldort benoetigt dort freie lokale Substratkapazitaet. W7-F bestimmt
die kleinste kontinuierliche Kantenform, die diese Eigenschaft mit dem
vorhandenen K2/F3-Transport verbindet.

Die Gleichung ist eine konstruierte Ausschluss- beziehungsweise
Belegungstransportbaseline. Ihre mathematische Zulassung ist weder ein
Memorybefund noch eine Behauptung neuer MCM-Physik.

## Zustands- und Parameterraum

Fuer jeden vorhandenen Feldort i gelten:

```text
S_i in [-1, 1]             schnelle MCM-Feldlage
M_i in [0, C_site]         vorhandene lokale Substratmenge
V_i = 1 - M_i / C_site     normierter freier Zielanteil
```

`V_i` wird aus dem atomaren Vorzustand berechnet und nicht gespeichert.

Feste globale Parameterrollen:

```text
lambda_sm >= 0
abs(kappa) <= 1/2
eta >= 0
M_total > 0
M_total / N < C_site <= M_total
```

N ist die Anzahl der Orte einer abgeschlossenen verbundenen
Feldkomponente. Die untere strikte Grenze stellt im homogenen Ausgangszustand
positive freie Kapazitaet sicher. Alle gleichartigen Orte verwenden dasselbe
`C_site`.

## Gerichtete Kantenraten

Fuer jede vorhandene ungerichtete Kante i-j mit festem symmetrischem Gewicht
`w_ij = w_ji >= 0` und demselben abgeschlossenen S/M-Vorzustand gilt:

```text
dS_ij = S_j - S_i

q_i_to_j = lambda_sm * w_ij * M_i * V_j * (1 + kappa * dS_ij)
q_j_to_i = lambda_sm * w_ij * M_j * V_i * (1 - kappa * dS_ij)

J_ij = q_i_to_j - q_j_to_i
J_ji = -J_ij
```

Der lokale kontinuierliche Materialanteil lautet:

```text
T_i(S, M) = Summe ueber Nachbarn j von (q_j_to_i - q_i_to_j)
dM_i/dt = T_i(S, M)
```

Die additive S-Rueckarbeit bleibt an genau denselben realisierten
Materialfluss gebunden:

```text
R_i = -eta * (1 - S_i^2) * T_i / M_total
dS_i/dt = F0_i(S, Weltkontakt) + R_i
```

`F0` ist der unveraenderte schnelle MCM-Pfad. H bleibt die unveraenderte
nachgelagerte schnelle Nachhallrolle. Innerhalb eines atomaren Schritts darf
kein neu berechnetes M, T oder R erneut Ursache desselben Schritts werden.

## Nichtnegativitaet der gerichteten Raten

Aus `S_i, S_j in [-1,1]` und `abs(kappa) <= 1/2` folgt:

```text
1 + kappa * dS_ij >= 0
1 - kappa * dS_ij >= 0
```

Aus `0 <= M_i <= C_site` folgt `0 <= V_i <= 1`. Mit
`lambda_sm >= 0` und `w_ij >= 0` sind beide gerichteten Raten nichtnegativ.
Die Gleichung benoetigt keine Vorzeichenverzweigung und kein Clipping.

## Exakte Massenbilanz

Jeder Kantenfluss wird an einem Ende mit negativem und am anderen mit
positivem Vorzeichen verbucht. Deshalb gilt algebraisch:

```text
Summe_i T_i = 0
d/dt Summe_i M_i = 0
```

Massenerhaltung folgt aus der Kantenantisymmetrie, nicht aus nachtraeglicher
Normalisierung.

## Invarianz der lokalen Kapazitaetsgrenzen

### Untere Grenze

Bei `M_i = 0` verschwinden alle gerichteten Abgaberaten von i. Eingehende
Raten bleiben nichtnegativ. Daher gilt:

```text
M_i = 0 -> dM_i/dt >= 0
```

### Obere Grenze

Bei `M_i = C_site` gilt `V_i = 0`. Alle gerichteten Zuflussraten nach i
verschwinden. Abgaberaten bleiben nichtnegativ. Daher gilt:

```text
M_i = C_site -> dM_i/dt <= 0
```

Damit ist der abgeschlossene Hyperkasten
`[0, C_site]^N` fuer die kontinuierliche M-Dynamik invariant. Die lokale
Obergrenze ist erstmals Teil der Transportursache und nicht nur eine Folge
der globalen Gesamtmasse.

## Direkte W7-E-Gegenprognosen

Die Gleichung erfuellt die fuenf vorab gebundenen Prognosen:

1. Bei gleicher Quelle und gleichem dS sinkt `q_i_to_j` linear mit der
   Zielbelegung `M_j`.
2. Bei `M_j = C_site` gilt `q_i_to_j = 0` exakt.
3. Bilanziert abgegebenes M vergroessert `V_j` um dieselbe Menge geteilt
   durch `C_site`.
4. Jeder Austausch bleibt kantenweise antisymmetrisch.
5. Fuer `max_i(M_i / C_site) -> 0` gilt `V_i -> 1`; die gerichteten Raten
   konvergieren gegen die vorhandenen K2/F3-Raten.

Diese Aussagen gelten vor jeder Lebenszyklus- oder Memoryauswertung.

## Exakte Reduktion gegen K2/F3

Die Nettoflussform kann algebraisch geschrieben werden als:

```text
J_ij = lambda_sm * w_ij * [
    (M_i - M_j)
    + kappa * dS_ij * (M_i + M_j - 2*M_i*M_j/C_site)
]
```

Der vorhandene K2/F3-Nettofluss ist:

```text
J_ij_K2F3 = lambda_sm * w_ij * [
    (M_i - M_j)
    + kappa * dS_ij * (M_i + M_j)
]
```

Der einzige neue Term lautet somit:

```text
Delta_J_ij = -2 * lambda_sm * w_ij * kappa * dS_ij
             * M_i * M_j / C_site
```

Diese Zerlegung bindet den Erweiterungsumfang exakt. Es gibt keine zweite
Nichtlinearitaet und keinen versteckten Leser.

## Wichtige Null- und Grenzfaelle

- `lambda_sm = 0`: exakter P0-Bypass; M bleibt unveraendert und R ist null.
- `eta = 0`: derselbe M-Transport ohne M-nach-S-Rueckwirkung.
- `kappa = 0`: der Kapazitaetsterm hebt sich im Nettofluss auf; es bleibt
  exakt die passive lineare M-Diffusion `lambda_sm*w_ij*(M_i-M_j)`.
- `M_i = M_j` und `S_i = S_j`: exakter Kantenruhezustand.
- `M_i/C_site -> 0` und `M_j/C_site -> 0`: lokaler K2/F3-Grenzfall.
- homogenes `M_i = m0` bei S-Gradient: der alte gerichtete K2/F3-Fluss wird
  mit dem freien Anteil `1 - m0/C_site` skaliert.

Der neue Effekt kann daher nur bei aktiver S-Richtungskomponente und
nichtvernachlaessigbarer Belegung auftreten. Ein Effekt bei `kappa = 0`
waere kein Ergebnis dieser Gleichung.

## Symmetrie und Darstellungsgrenzen

Die Form ist unter Umbenennung gleichartiger Orte und unter Kantenumkehr
aequivariant. Sie liest keine Rezeptor-, Objekt-, Modalitaets-, Episoden-,
Phasen- oder Ergebniskennung. Sie veraendert keine Kante und erzeugt keine
Zieltopologie.

`C_site` ist eine feste Materialkonstante, kein Aufmerksamkeitswert und kein
Regler. Weder Observer noch spaetere Auswertung duerfen sie veraendern.

## Numerische Zulassungsgrenze

Der kontinuierliche Invarianzbeweis erlaubt noch keine beliebige diskrete
Fortschreibung. Eine spaetere Implementierung muss:

- aus einer vorab hergeleiteten Forward-Euler-Grenze einen
  invariantenerhaltenden SSP-Schritt ableiten;
- Ereignisgrenzen exakt treffen;
- M weder clippen noch normalisieren;
- Massenfehler, kleinstes M und groessten Kapazitaetsabstand diagnostizieren;
- bei jeder Verletzung vor Zustandsuebernahme abbrechen;
- P0 weiterhin direkt durch den bestehenden neutralen S/H-Pfad fuehren.

Die bestehende K2/F3-Runtime darf nicht stillschweigend ueberschrieben
werden. Der neue Pfad muss opt-in und als Engineeringreferenz getrennt sein.

## Pflichtbaselines fuer eine spaetere Implementierung

- exakter P0-Pfad;
- unveraenderter K2/F3-Pfad;
- lineare gekoppelte Feldbaseline aus Lauf 192;
- konstante Zielverfuegbarkeit mit gleichem Skalenbudget;
- `eta = 0`, `kappa = 0` und Vorzeicheninversion von `kappa`;
- direkte Algebrarekonstruktion des neuen `Delta_J`-Terms;
- Zeitverfeinerung und Snapshot/Restore.

## Entscheidung

```text
gerichtete Raten nichtnegativ:      ja
Gesamtmasse exakt erhalten:         ja
lokale Untergrenze invariant:       ja
lokale Obergrenze invariant:        ja
P0 exakt konstruierbar:             ja
K2/F3-Grenzfall vorhanden:          ja
neuer Term exakt isoliert:          ja
zusaetzlicher gespeicherter State:  nein
mathematisch implementierbar:       ja
Implementierung erfolgt:            nein
Forschungslauf:                     nein
```

`CAPACITY_LIMITED_EDGE_EXCHANGE_MATHEMATICALLY_ADMISSIBLE` bedeutet nur,
dass die offen konstruierte Engineeringgleichung intern konsistent,
begrenzt und gegen K2/F3 reduzierbar ist. Sie belegt keine funktionale
Verdichtung, Loesung, Wiederverwendung, Feldzeit, Memory oder KI.

## Verwendete Projektquellen

- [W7-E Engineeringentscheid](W7E_ENGINEERINGENTSCHEID_ZIELSEITIGE_FREIE_KAPAZITAET.md)
- [K2/F3 mathematischer Minimalvertrag](K2_MATHEMATISCHER_F3_MINIMALVERTRAG.md)
- [K2/F3 C/R-Implementierungsvertrag](K2_F3_SCHEIBE_B_CR_IMPLEMENTIERUNGSVERTRAG.md)
- [K2/F3 SSPRK-Runtimevertrag](K2_F3_SCHEIBE_C_SSPRK_RUNTIME_VERTRAG.md)
- [Lauf 192 Baselinevergleich](forschung/LAUF_192_K2_F3_E3_BASELINEVERGLEICH.md)
- [Lauf 194 Funktionsverlust und Wiederverwendung](forschung/LAUF_194_K2_B_F3_FUNKTIONSVERLUST_UND_WIEDERVERWENDUNG.md)

## Bester naechster Schritt

W7-G implementiert zunaechst nur die reine opt-in Kopplungsfunktion und ihre
algebraischen Vertragstests. Bestehender K2/F3-Code, Runtime, `current_api`,
Browserpfade und Reports bleiben unveraendert. Geprueft werden gerichtete
Raten, Delta-J-Rekonstruktion, Symmetrie, Grenzen und P0; noch keine
Runtimeintegration und kein Forschungslauf.
