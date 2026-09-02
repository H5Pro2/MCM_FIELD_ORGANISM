# S2-JV - Default-Live-AV-Memory-Materialisierungsvertrag

## Status und Grenze

`S2JV_STATIC_MATERIALIZATION_CONTRACT_COMPLETE`

S2-JV materialisiert genau den ersten 336-Werte-Memoryfall aus S2-JU. Der
Vertrag bindet reale kanonische RGB-/PCM-Quellen, deren unveraenderte
Rezeptorableitung, die zeitliche AV-Paarung sowie die Signaturen der spaeteren
privaten Profil-, Koordinator-, read-only- und Ledgerhuellen.

S2-JV hat keine Memory-, Kontext- oder Feldfunktion ausgefuehrt. Zur
Fixturematerialisierung wurden ausschliesslich die unveraenderten lokalen
Default-Live-Rezeptoren auf den unten vollstaendig beschriebenen Rohrezepten
ausgewertet. Es wurden keine Tests ausgefuehrt und keine Sollvektoren von Hand
geschrieben. README, Memorykerne, Slotzahlen, API, Snapshot und Feldpfad bleiben
unveraendert.

Freigegeben ist durch diesen Vertrag noch keine Memoryausfuehrung.

## Gebundener Quellstand

Basis ist Commit `a30e9bf`.

| Rolle | Datei | SHA-256 |
| --- | --- | --- |
| visueller Default-Live-Rezeptor | `mcm_field_organism/finite_video_path.py` | `d09cb6ba35fd061e4a243b7ed2112597a194e75abd026d7cc3ab7aa89922c07a` |
| auditiver Spektralrezeptor | `mcm_field_organism/log_spectral_receptor.py` | `26a6bd8f2d190db60c75ad29f275b3bd8b09b6d26d4ad54e4396176c4a36d2b0` |
| rollender Hoerpfad | `mcm_field_organism/broadband_hearing_path.py` | `a20456b24c04d099ba5ee2da6250e3d83dc657392603c41d816b13ca68a37fb7` |
| Rezeptorvertrag | `mcm_field_organism/receptor_contract.py` | `af565ce442aa56ade4b3b5d028692cccc93b481c299f1ff2d87ba840fdb6ee71` |
| gemeinsame Zeitbindung | `mcm_field_organism/receptor_time_model.py` | `268eaab0505c78f5053aa1f1671ec3a503fa080774a3fb71c4719c2239c596aa` |
| aktive PPB-Batchbindung | `mcm_field_organism/_ppb1_active_receptor_batch_binding.py` | `3b9e1bf95eff7ba27ec1a3c8d47f5a81b6480f9340191b420b50e35d92a55548` |
| PPB-1-Profile | `mcm_field_organism/_ppb1_receptor_profiles.py` | `28f3ce1de5b0ade465fffaa7dd3064eb51688cfea39ebb6c853cb4328bc0e5e0` |
| PPB-1-Kern | `mcm_field_organism/_ppb1_reference.py` | `15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0` |
| TSPM-1-Kern | `mcm_field_organism/_tspm1_private.py` | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` |
| bisheriger atomarer Verbund | `tools/_s2fs_b4_tspm1_private_coordinator.py` | `95ee05ccc0eeb14abbcda036971da5c33ac79363dd546789f4878aace5677db0` |
| bisheriger read-only Adapter | `tools/_retention_capacity_read_only.py` | `524a42ae8294a14e58adfda29afa8602f3a799e0caaccae9675dc50bf0109ff7` |
| kanonische AV-Grenze | `tools/_s2jo_private_canonical_av_boundary.py` | `50a39fb3865fbd11b3577f79db2983f9dd3260262dee0f199ae5f884bed4ef71` |
| bestaetigte Feldzeitprojektion | `tools/_s2jt_private_timed_field_projection.py` | `91604184325192b6a6291785f713c44fc8fac1d7614234279f635032160c4a4e` |
| vorausgehender Skalierbarkeitsaudit | `docs/S2JU_STATISCHER_MEMORY_SKALIERBARKEITS_UND_PROFILKOMPATIBILITAETSAUDIT.md` | `4f826b07c5cb4a1c5ff51a67e6dfe45cc3b832e366e78912f0602679f2135fee` |

## Vollstaendige Default-Live-Konfiguration

Die spaetere Implementierung muss genau folgende vorhandene Konfigurationen
binden:

```text
VisualGridConfig(
    source_width=1920,
    source_height=1080,
    grid_columns=12,
    grid_rows=8,
    frame_rate_hz=30.0,
)

LogSpectralConfig(
    sample_rate=48000,
    window_size=4800,
    hop_size=480,
    min_frequency=50.0,
    max_frequency=18000.0,
    band_count=48,
)

PPB1ProfileParameters(
    auditory=(capacity=8, match_threshold=0.02, update_rate=0.05,
              stable_after=3, expire_after_steps=256),
    visual=(capacity=4, match_threshold=0.01, update_rate=0.05,
            stable_after=3, expire_after_steps=64),
)

TSPM1FastConfig(
    fast_bank_id="tspm1.fast",
    capacity=3,
    auditory_match_threshold=0.2,
    visual_match_threshold=0.2,
    update_factor=0.5,
    consolidate_after=2,
    expire_after_exposures=8,
)
```

Die kanonischen Digests dieses Profils sind:

| Bindung | SHA-256 |
| --- | --- |
| S2-JV-Quellprofil V1 | `fa6bc21e216068e6d2d02ab016d083d7456819c4505db4db8161b8ec03e5f0f5` |
| PPB-Parameter | `b3cfa693d7cc10ae0795946c0c6c1473e6535005ca84b388dc73a392cbab42e1` |
| auditive PPB-Konfiguration | `3852b41b0bed61862abcccbcf7c5839c73d246391966d97c8dd088ba71723252` |
| visuelle PPB-Konfiguration | `fe8b06bad66204dec3e7c80cb24bb73d740544eba23af9a8c9e1da3d3c5d9fec` |
| PPB-Profilbindung `default-live` | `27a87f2beb3b498e3fd7eac3f0977ef585163e9abb4cda48fc1a53ab7081fd86` |
| TSPM-Fast-Konfiguration | `32640b5bb40e9bcfe4735748b3dcbab659680212a515384e432ddbef776aa19e` |
| TSPM-Gesamtkonfiguration | `3611e0a8dfad395b496bc5d653f7c73c80de09f375e3ad4568b5d4f3e4a7f456` |

Der erste Digest gehoert zu `S2JVDefaultLiveSourceProfileV1`. Dessen
kanonischer Payload enthaelt exakt Schema und `profile_id`, alle oben
ausgeschriebenen auditiven und visuellen Konfigurationsfelder, die visuelle
Carrierreihenfolge `grid_row-grid_column-rgb_channel` sowie die vier Digests
fuer PPB-Parameter, PPB-Profil, TSPM-Fast und TSPM-Gesamtkonfiguration. Die
Serialisierung verwendet `allow_nan=False`, sortierte Schluessel und die
Trennzeichen `(",", ":")`.

Das Profil besitzt exakt 48 auditive, 288 visuelle und damit 336 gemeinsame
Carrier. Der PPB-Profilbestand umfasst 1.536 Floatwerte beziehungsweise 12.288
logische Float64-Bytes. B4 bleibt bei 9, TSPM-Fast bei 3, PPB-auditiv bei 8 und
PPB-visuell bei 4 Slots.

## Kanonische Rohfixtures

Die Fixture-ID ist keine Memoryeingabe. Funktional gebunden werden nur die
kanonischen Rohbytes, Zeitrollen, Rezeptorprofile und daraus erzeugten
Rezeptorwerte. Die gemeinsame Fixture-Rezeptur hat den Digest
`de1871c8f9059ae6ef4b5b0aaabc967080e9f91eeee0bd2c2626ae061e4e054d`.
Ihr kanonischer Payload `s2jv.fixture-recipe.v1` enthaelt fuer jeden Zustand
Label, Ordinalzahl und Periodenlaenge sowie visuelle Form, Carrierreihenfolge,
Blockform, Residuen, Bytewerte und Formel und auditive Kodierung, Rate,
Fenster- und Hoplaenge, Samplewerte und Formel. Er wird mit derselben
kanonischen JSON-Regel wie das Quellprofil serialisiert.

### Visuelle RGB8-Fixture

Die elf Zustandsordnungen sind:

```text
X=0, Y=1, D1=2, D2=3, D3=4, D4=5,
D5=6, D6=7, D7=8, D8=9, D9=10
```

Fuer jeden Zustand `s` wird ein echtes `1920 x 1080 x 3`-`uint8`-Bild
erzeugt. Die 288 Carrier werden in der vorhandenen Reihenfolge
`grid_row, grid_column, RGB_channel` mit `i=0..287` durchlaufen. Jeder
zugehoerige `135 x 160`-Kanalblock ist konstant:

```text
Q = {1, 3, 4, 5, 9}
byte(i, s) = 255, falls (i + s) mod 11 in Q, sonst 0
```

Damit liefert `LocalChannelGridReceptor.analyze` fuer jeden Carrier exakt
`byte(i,s)/255`, also ausschliesslich `0.0` oder `1.0`. Der 288er-Vektor wird
nicht als Sollwert hinter dem Rezeptor eingesetzt.

### Auditive PCM-Fixture

Jeder Zustand besitzt ein echtes 100-ms-Fenster aus 4.800 mono Samples in
`PCM_F32LE`. Es werden ausschliesslich die exakt darstellbaren Werte `+0.5`
und `-0.5` verwendet:

```text
sample(n, p) = +0.5, falls floor(n / (p/2)) mod 2 == 0, sonst -0.5
n = 0..4799
```

| Zustand | Periodenlaenge `p` | Grundfrequenz bei 48 kHz |
| --- | ---: | ---: |
| X | 960 | 50 Hz |
| Y | 600 | 80 Hz |
| D1 | 400 | 120 Hz |
| D2 | 300 | 160 Hz |
| D3 | 240 | 200 Hz |
| D4 | 160 | 300 Hz |
| D5 | 120 | 400 Hz |
| D6 | 80 | 600 Hz |
| D7 | 60 | 800 Hz |
| D8 | 40 | 1.200 Hz |
| D9 | 30 | 1.600 Hz |

Alle Perioden teilen 4.800 ohne Rest. Jedes Fenster wird in zehn
aufeinanderfolgende 480-Sample-Hops zerlegt und durch einen frischen,
kontinuierlichen `BroadbandHearingPath` gefuehrt. Nur der Zustand am Ende des
jeweiligen 4.800-Sample-Fensters wird gepaart. Zwischenzustaende des rollenden
Rezeptors sind fluechtig und niemals Memoryformationen.

### Roh- und Rezeptorwertedigests

Wertedigests sind kanonisch definiert als SHA-256 ueber die UTF-8-Bytes von
`json.dumps(list(values), allow_nan=False, sort_keys=True,
separators=(",", ":"))`. Die Tabelle bindet die durch die echten Rezeptoren
erzeugten Werte, nicht handgeschriebene Zielvektoren.

| Zustand | RGB8-Bytes | PCM-Fenster | 288 visuelle Werte | 48 auditive Werte |
| --- | --- | --- | --- | --- |
| X | `68d7b1a28b79359d09b8e283d1edd3ee7bf3a7aa899fad60305c9435a3c3aee6` | `dd5f35aa7a6b8802712a7bdac5d3040e38bdbf68d398483d352fe43a168d8038` | `46ee578128cfde13f300b2d03bcbd2df7a57d278174abb2d3a2a22c2c6d5855b` | `76636a67276d7d3158330bd5dc7705d88fc8cc626b59f8b2911b4439d699b021` |
| Y | `702938c656d7486cf3b009fa52ea7aa1dfe0d93477f4e8827976e92244167c5f` | `383a00f9dc02d8b1bee7007e9536d127ae221df4fa295ba287bebf68bacb1463` | `109c23b93156d53373207bd23333f16b45bfff9fa2b79372c9b775f54b815f63` | `dc692a8918e4c1912b5a55eb8713f1cb27d625d325fd16007dda2112d012d35f` |
| D1 | `cd7faff71d59428d6a68a77427d6d9b8d4fc4d26f3b35b24a47760186d4106b8` | `d2ba7671773e607d66d2e9d15bc133c98bd8c58a800464beea61cece83344189` | `28d859a5c74258de1e9cf8f47134dd87939254b501b958cb03cc9f244ec48f9b` | `c628fb56f3bc93d6df6bd7fb3465cdd97749c10e89a39f9b9adb2a711006adee` |
| D2 | `0a8ea1fa775d43946c3788d5deffe0b082c91c75bd6489674e572e1e1c448960` | `f10a835d6d8264d3efe6869afd17556df0aeb7a11d61162d58ea32c1c0b6cdad` | `070c4474fe9e97441864ed6861ec687593fd48b4ff104aee55508013274151b3` | `9ab34eaee70984318f838436d6b8c120bca71e82d1d961ca8528a3b7dc62504b` |
| D3 | `5e2a628ad25ac1f5ae9a36f6c24f91d8daf952048f42a43f25911abf533c6d1f` | `75700a0fde2bc500394a6024d341e1cb061fc4fe58a23073c993ef702c897236` | `ecb72ef43026805d8067f1cd882b5ad67d1285abf107d23859af3359721c1d73` | `017bc24ab3335564adcd497b479b01aca154a988d86e3a1b6b8991ef0ccc0d0d` |
| D4 | `8846cd7252d493b46f87bf3645ead8b650e8c16ef40817ebf0d8c8861714dd9d` | `73ca0a06eeb7db4065ad366310bf716c2da3657a1c24d876a8410b62de54e420` | `4d5dd97f1bcb19bdfedde37d810cc56399afb8a33d912e3c4a626d6a09290991` | `ed0fbc9c617ceaafbd0c72960fdd2f915c892fa69d04294318e309dd1b615960` |
| D5 | `c7ae7b15352555a4fb8a8254f65cb6f85f0e792d2228465eeef625d3e7696dba` | `cfdb33799badd368cd5e3c4b8e82a4f28b9781bdaf6ab844a6b4512265094b7e` | `ec9ddc3b42fe73c44fd384f5048cfc34ec7780a8295f1136e397ce601b14f49f` | `111f96df08a931cc96064c289ffc32570519694eef82113880bd94bcb1fb27cb` |
| D6 | `dc7f22f628260215041b263de559e42d4c2070dc9cba1256f3f5defdedee03bc` | `9717868f7c99e4f62cdb80226f0f6b537b9498442b0c62ae5eceb5f3c305ac10` | `6598cc54ac4859618c286b8437e231a62a5dafb72fb18271805d463ad8723a9f` | `1b17a89a25f53cf68306f8b14749916586f35072f99eba787bcc42dbf14bc180` |
| D7 | `d6e86a187af900547e72dff68679d028627b65ebcf2b5872228e04bd8f5b876d` | `aa07d7c4a2886586bfb78423bede462ba2de6a978d4da301ecb491608e904587` | `4d57c5025ad9d889af966afd2bdcdb716ee222598233863d5cf4f0a556babbab` | `004235506f1b6d0fd80b2302441bccd3dcb1c87d77867bc474e1feca098bb1da` |
| D8 | `d0f4205d392d70ef0730e83572ba8a4e419592906f2c93732d9aa9451a962135` | `23b5216f007dc27a2626fdc72e5ef81dfc502525ed83035f8a0eb92e976c6760` | `d9118dfed11e645486bb229a67518a8b92f4f2db81415734aad9bc174ba68ed7` | `d3b677f16c12221d8591cc6bc99de061b82ba2b83c2b9c0f2b8a00293aa328e6` |
| D9 | `32226986f06d628a511793b2f3ddc74e0dccb65268cd7342eae0d80c791fd122` | `7cc5dae151b952409623ed608a9e3c44ab2d3fe8de40cd342b3abb77359c8441` | `1ad80c4b23dd0d1556312205802fd8cbcae4d760cd417bb7efc8f287a2e739e4` | `dd8f9e68221fa328fa9e63dc59e224ad3305bcd5e0ca21eba711f02c0cfd9038` |

## Mechanische Distanzbindung

Die reale Rezeptorableitung ergibt ueber alle 55 verschiedenen Zustandspaare:

| Modalitaet | kleinste mittlere L1-Distanz | groesste mittlere L1-Distanz | mechanische Grenze |
| --- | ---: | ---: | ---: |
| visuell, 288 Werte | `156/288 = 13/24 = 0.541666...` | `158/288 = 79/144 = 0.548611...` | Fast `0.2`, PPB `0.01` |
| auditiv, 48 Werte | `0.046051827674693784` | `0.07273487587711298` | Fast `0.2`, PPB `0.02` |

Die kleinste visuelle Distanz liegt zwischen X und D1. Die kleinste auditive
Distanz liegt zwischen D5 und D8. Jeder verschiedene Zustand ist in beiden
separaten PPB-Banken ausserhalb des jeweiligen mechanischen Matchbereichs. Im
TSPM-Fast-Pfad reicht bereits die visuelle Distanz aus, um den gemeinsamen
Match auszuschliessen; die auditive Fast-Distanz allein liegt unter `0.2`.

Diese Zahlen sind technische Trennungsreserven fuer genau diese Fixtures. Sie
sind keine Kalibrierung von Wahrnehmungsaehnlichkeit. Insbesondere werden
`0.2`, `0.02`, `0.01` und `44/765` nicht als allgemein geeignete
Default-Live-Schwellen behauptet.

## Geschichte, Proben und echte AV-Ueberlappung

Die spaetere Formation ist exakt:

```text
X, X, X, X, Y, Y, D1, D2, D3, D4, D5, D6, D7, D8, D9
```

Die drei anschliessenden read-only Proben sind exakt:

```text
D9, X, Y
```

Damit existieren 18 AV-Bloecke `b=0..17`. Jeder Block besitzt ein 100-ms-
PCM-Fenster aus zehn Hops und genau ein zugehoeriges RGB8-Bild. Der
gemeinsame Feldtakt verwendet Nanosekunden:

```text
audio source window: [4800*b, 4800*(b+1)] samples
audio selected snapshot_index: 10*b
audio field window: [100000000*b + 90000000, 100000000*(b+1)] ns

visual frame_index: 3*b + 2
visual source window: [3*b + 2, 3*b + 3] frames
visual field start: floor((3*b + 2) * 1000000000 / 30) ns
visual field end: 100000000*(b+1) ns
```

Jedes Paar ueberlappt auf dem gemeinsamen Feldtakt exakt in den letzten
10.000.000 ns seines Blocks. Auditive und visuelle Quellfenster bleiben auf
ihren eigenen Takten. Beide Quellenden steigen zwischen Paaren strikt an.
Weder ein letzter Wert noch ein Feldsnapshot wird fortgeschrieben.

`X` ist in seinen vier Formationseintraegen auf Rohpayload- und
Rezeptorwertebene bitidentisch. `Y` ist in seinen zwei Formationseintraegen
ebenfalls bitidentisch. Verschieden bleiben nur die fuer die zeitliche
Quellbindung notwendigen Block-, Snapshot-, Frame- und Fensteridentitaeten.

## Erwartete mechanische Zustandsfolge

Die Erwartungen sind ausschliesslich Auswertungsmetadaten:

- X erzeugt bei vier identischen Expositionen drei PPB-Aktualisierungen und
  erreicht in beiden Slow-Banken Support `3`;
- Y erzeugt bei zwei identischen Expositionen eine PPB-Aktualisierung und
  bleibt in beiden Slow-Banken bei Support `1`;
- D1 bis D9 werden jeweils genau einmal exponiert und loesen keine
  Konsolidierung aus;
- nach D9 enthaelt B4 das FIFO-Fenster D1 bis D9;
- X und Y sind dann weder in B4 noch in TSPM-Fast vorhanden;
- die Probe D9 findet einen juengsten B4-Inhalt;
- die Probe X findet einen stabilen Slow-Inhalt;
- die Probe Y findet keinen oeffentlich stabilen Slow-Inhalt.

Support, Stabilitaet und Slotbelegung werden spaeter aus dem tatsaechlichen
Nachzustand gelesen. Die obigen Metadaten duerfen weder Quelle noch
Formation, Kandidatensuche oder Abruf steuern. Ein abweichender vollstaendiger
Lauf waere ein funktionales Ergebnis und kein technischer Abbruch.

## Erforderliche private Schnittstellen

Die folgenden Signaturen sind fuer die spaetere Implementierung verbindlich.
Alle Datentypen sind `frozen=True, slots=True`, kanonisch digestgebunden und
profilabgeleitet.

### AV-Paarung

```python
def bind_s2jv_default_live_pair(
    *,
    pairing_plan: S2JVPairingPlanV1,
    profile: PPB1ReceptorProfileBinding,
    auditory: OrganismTimedReceptorFrame,
    visual: OrganismTimedReceptorFrame,
) -> S2JVBoundAVPairV1: ...
```

`S2JVBoundAVPairV1` enthaelt genau einen vorhandenen
`PPB1ActiveReceptorBatchEnvelope`, je ein vorhandenes
`PPB1ActiveReceptorTimedFrameBinding`, die beiden Rohpayloaddigests, beide
Rezeptorwertedigests, den 336er-AV-Projektionsdigest, die Ueberlappung und den
Paarungsdigest. Rohbytes sind nicht enthalten.

Die vorhandene Envelope-Klasse akzeptiert derzeit literal nur
`profile_id == "browser"`. Fuer `default-live` ist daher eine enge private
Schemaakzeptanz erforderlich. Der bestehende
`bind_ppb1_active_receptor_batch` bleibt browserexklusiv und unveraendert;
der neue Binder muss `profile_id == "default-live"`, Profil-, Carrier-,
Geometrie-, Zeit- und Quelldigests selbst vollstaendig pruefen. Ein
`default-live`-Profil darf nie als `browser` etikettiert werden.

### Profilabgeleiteter atomarer Koordinator

```python
def build_s2jv_coordinator_config(
    *,
    tspm_config: TSPM1ConfigBinding,
    b4_capacity: int,
    ledger_limits: S2JVLedgerLimitsV1,
) -> S2JVCoordinatorConfigV1: ...

def initial_s2jv_composite_state(
    config: S2JVCoordinatorConfigV1,
) -> S2JVCompositeStateV1: ...

def advance_s2jv_atomic(
    *,
    config: S2JVCoordinatorConfigV1,
    prestate: S2JVCompositeStateV1,
    source: S2JVBoundAVPairV1,
    owner: S2JVFormationOwner,
) -> S2JVFormationResultV1: ...
```

Dimensionen werden ausschliesslich als
`len(profile.auditory_config.carrier_ids)` und
`len(profile.visual_config.carrier_ids)` abgeleitet. Der Owner bindet genau
Konfiguration, Vorzustand und Paarungsdigest und ist atomar einmalig
verbrauchbar. B4- und TSPM-Kandidaten bleiben lokal, bis beide Kandidaten,
Receipts, Ledger und Composite-Nachzustand relational validiert sind.

### Profilabgeleiteter read-only Adapter

```python
def bind_s2jv_probe(
    *,
    config: S2JVCoordinatorConfigV1,
    source: S2JVBoundAVPairV1,
) -> S2JVBoundProbeV1: ...

def probe_s2jv_composite_read_only(
    *,
    config: S2JVCoordinatorConfigV1,
    state: S2JVCompositeStateV1,
    probe: S2JVBoundProbeV1,
) -> S2JVReadOnlyFindingV1: ...
```

Der Finding enthaelt getrennte Befunde fuer `B4_RECENT`, `TSPM_FAST`,
`TSPM_SLOW_AUDITORY` und `TSPM_SLOW_VISUAL`, native Distanzen, Slotidentitaet,
Support, Stabilitaet sowie identische Vor-/Nachzustandsdigests. Er erzeugt
keine Gesamtauswahl. `44/765` wird nicht uebernommen. Native mechanische
Schwellen werden nur als vorhandene Kernentscheidungen samt Rohdistanz
berichtet.

### Dimensions- und pfadbezogenes Ledger

```python
def derive_s2jv_resource_ledger(
    *,
    config: S2JVCoordinatorConfigV1,
    operation_id: str,
    operation_role: str,
    prestate: S2JVCompositeStateV1,
    result_digest: str,
) -> S2JVResourceLedgerV1: ...

def validate_s2jv_resource_ledger(
    *,
    config: S2JVCoordinatorConfigV1,
    ledger: S2JVResourceLedgerV1,
    expected_role: str,
) -> S2JVResourceLedgerV1: ...
```

`operation_role` ist exakt `FORMATION` oder `READ_ONLY`. Das Ledger trennt
mindestens gemeinsame Projektion, B4-Schreibwerte, TSPM-Fast-Schreibwerte,
PPB-Schreibwerte, B4-/Fast-/Slow-L1-Terme, Validierungsvergleiche,
Digestoperationen und Koordinatorworte. Kein dynamischer Pfad darf einen
nicht registrierten Zaehler erzeugen.

## Exakte Operations- und Ressourcenbindung

### Rohquelle und Rezeptoren

Die 18 Bloecke umfassen:

| Rolle | Anzahl beziehungsweise Bytes |
| --- | ---: |
| kanonische RGB8-Frames | 18 |
| kanonische PCM-Hops | 180 |
| visuelle Rezeptoraufrufe | 18 |
| auditive `push`-Aufrufe | 180 |
| ausgewaehlte auditive Fensterabschluesse | 18 |
| RGB8-Bytes insgesamt | 111.974.400 |
| PCM-Bytes insgesamt | 345.600 |
| gestreamte Rohbytes insgesamt | 112.320.000 |
| maximal gleichzeitig gehaltener Frame plus Hop | 6.222.720 Bytes |
| ausgewaehlte reduzierte Werte | `18 * 336 = 6.048` |
| ausgewaehlte reduzierte Float64-Nutzbytes | 48.384 Bytes |

Die Rohdaten werden mit hoechstens einem Frame und einem Hop gleichzeitig
gestreamt und nach Rezeptorreduktion verworfen. Der rollende Audiorezeptor
darf intern sein bestehendes 4.800-Sample-Fenster halten. Rohframes oder PCM
werden weder Memoryzustand noch Receiptbestandteil.

Quellenvalidierung und Rezeptorreduktion sind der Memorygrenze vorgelagert
und werden separat gezaehlt: 198 kanonische Payloadvalidierungen und 198
Rezeptoraufrufe. Die 18 spaeteren AV-Paarbindungen gehoeren dagegen zu den
72 Top-Level-Memoryoperationen. Python-/NumPy-/FFT-Objektoverhead und
tatsaechliche Wandzeit sind spaeter separat zu messen und duerfen keine
funktionalen Zaehler ersetzen.

### Memorygrenze

| Top-Level-Rolle | Formation | Probe | Gesamt |
| --- | ---: | ---: | ---: |
| AV-Paarung und gemeinsame Projektion | 15 | 3 | 18 |
| B4-Arm | 15 | 3 | 18 |
| TSPM-Arm | 15 | 3 | 18 |
| atomare Verbundvalidierung | 15 | 3 | 18 |
| **Summe** | **60** | **12** | **72** |

Die gebundene L1-Arbeit bleibt exakt:

| Rolle | skalare L1-Terme |
| --- | ---: |
| 15 Formationen | 22.512 |
| 3 read-only Proben | 21.168 |
| **Gesamt** | **43.680** |

Zusaetzlich gelten die bereits in S2-JU gebundenen Grenzen:

- 260 Aufrufe von `normalized_mean_l1_distance`;
- 5.040 gemeinsame AV-Projektionsterme;
- 11.424 neu materialisierte Vektorwerte;
- maximal 5.568 gleichzeitig im Verbund gespeicherte Floatwerte;
- maximal 44.544 logische Float64-Bytes im voll belegten Memoryzustand.

Die Werte `72` und `43.680` duerfen weder um Rohdaten-/Rezeptorarbeit
verkuerzt noch durch deren Hinzurechnung umgedeutet werden. Das spaetere
Gesamtledger besitzt getrennte Abschnitte fuer Quelle/Rezeptor und Memory.

## Fail-Closed-Regeln

Vor dem ersten Armaufruf stoppen insbesondere:

- ein anderer Profil-, Parameter-, Carrier-, Geometrie- oder Config-Digest;
- ein Rohpayload- oder Rezeptorwertedigest, der nicht zur Fixture-Rezeptur
  gehoert;
- ein handgeschriebener 336er-Vektor ohne gebundene Rezeptorherkunft;
- fehlende, doppelte, vertauschte oder nicht streng fortschreitende
  Quellfenster;
- fehlende positive AV-Ueberlappung auf dem gemeinsamen Feldtakt;
- ein Audiozustand, der nicht aus dem gebundenen ausloesenden Hopfenster
  stammt;
- eine `browser`-Etikettierung des `default-live`-Profils;
- ein Dimensionssplit ungleich `48 + 288` oder veraenderte Slotzahlen;
- ein unvollstaendiges oder arithmetisch widerspruechliches Ledger.

Nach Beginn eines atomaren Schritts fuehrt jeder B4-, TSPM-, Receipt-, Owner-
oder Relationsfehler zu keinem sichtbaren Teilzustand. Read-only Proben muessen
identische Vor- und Nachzustandsdigests belegen.

## Abschluss und naechster konkreter Schritt

S2-JV bestaetigt statisch:

- X, Y und D1 bis D9 sind vollstaendig aus kanonischen, erzeugbaren RGB-/PCM-
  Payloads materialisiert;
- alle 336 Werte stammen aus den qualifizierten unveraenderten Rezeptoren;
- X und Y besitzen die geforderten bitidentischen Wiederholungen;
- alle verschiedenen Fixtures liegen ausserhalb der fuer diesen ersten Fall
  verwendeten mechanischen Matchbereiche;
- 15 Formationen, drei Proben, 72 Top-Level-Memoryoperationen und 43.680
  L1-Terme sind widerspruchsfrei gebunden;
- die noetigen privaten Schnittstellen sind ohne neue Memorymechanik
  implementierbar.

S2-JV bestaetigt nicht die Wahrnehmungsqualitaet der vorhandenen Schwellen,
keinen 336-Werte-Memorylauf und keine Kontext- oder Feldwirkung.

Der naechste Schritt ist direkt die begrenzte private Implementierung der
Fixture-, Pairing-, profilabgeleiteten Koordinator-, read-only- und
Ledgerhuellen mit fokussierter neutraler Qualifikation. Eine weitere allgemeine
Vertragskaskade ist vor dieser Implementierung nicht erforderlich.
