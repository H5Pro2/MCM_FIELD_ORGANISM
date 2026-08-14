# Auditierte NASA-Audio-Video-Rohquellen

## Zweck

Nach dem geschlossenen Brokindsleden-Pfad wurde eine andere oeffentliche
audiovisuelle Testwelt gesucht. Verwendet wird die NASA-SVS-Datei
`Earthrise_Realtime_ipod_sm.mp4`, lokal unter
`sources/media/NASA Earthrise Realtime Apollo 8.mp4`.

Die NASA-Seite beschreibt die Echtzeitsequenz als mit dem Bordaudio von
Apollo 8 synchronisiert. NASA SVS kennzeichnet seine Inhalte grundsaetzlich
als gemeinfrei, sofern nicht anders angegeben.

## Quellenvertrag

```text
source_id: public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20
size:      13547755 Byte
sha1:      c63198a925ad227950cca597c4a8500656bacdfc
```

Der lokale Integritaetsaudit war positiv. Der Decoder-Preflight bestaetigte
PyAV als verfuegbaren Containerdecoder. Dadurch war nur die Implementierung
des neutralen Adapters freigegeben; ein Feldlauf blieb gesperrt.

## Neutraler Adapter

`mcm_field_organism/public_av_container_source.py` oeffnet die Datei erst
nach positivem Groessen- und SHA-1-Audit. Es werden ausschliesslich die erste
Audio- und die erste Videospur decodiert:

- Audio wird als lokale Mono-Rohsamples in vollstaendige 480-Sample-Rahmen
  geteilt.
- Video wird als unveraenderliche `uint8`-BGR-Pixelrahmen ausgegeben.
- Beide Quellen verwenden `public.media.pts_ns` mit einer Milliarde Ticks
  pro Sekunde.
- Die zusaetzliche Container-Datenspur und alle Metadaten bleiben ausserhalb
  der Quellen- und Rezeptorschnittstelle.
- Die Decodierung ist technisch auf hoechstens zehn Sekunden begrenzt.

## Technischer Befund

Ein 0,5-Sekunden-Adaptertest bestaetigte fuer die lokale Originaldatei:

```text
audio sample rate: 48000 Hz
audio frame size:  480 Samples
video frame shape: 240 x 320 x 3
shared clock:      public.media.pts_ns
```

Ein absichtlich falscher Quellenvertrag verhindert die Containeroeffnung.

## Forschungsgrenze

Der Befund weist nur nach, dass eine auditierte oeffentliche Datei neutral in
zwei zeitlich kompatible Rohquellen zerlegt werden kann. Es wurde kein
Rezeptor gespeist und kein Feldlauf ausgefuehrt. Der Befund ist kein Nachweis
von Memory, Bedeutung, Organisation oder eigenstaendiger KI.

## Verwendete externe Quellen

- NASA Scientific Visualization Studio, Earthrise: The 45th Anniversary:
  https://svs.gsfc.nasa.gov/4129/
- NASA SVS Help, Nutzungs- und Gemeinfreiheitshinweis:
  https://svs.gsfc.nasa.gov/help/
