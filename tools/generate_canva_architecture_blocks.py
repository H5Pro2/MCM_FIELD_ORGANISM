from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
import zipfile

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "bilder" / "architektur" / "canva_bausteine"
WIDTH = 1400
HEIGHT = 540
MARGIN = 50
RADIUS = 28


@dataclass(frozen=True)
class Block:
    number: int
    slug: str
    badge: str
    title: str
    lines: tuple[str, ...]
    fill: str
    accent: str
    border: str
    kind: str = "block"

    @property
    def stem(self) -> str:
        return f"{self.number:02d}_{self.slug}"


BLOCKS = (
    Block(
        1,
        "mikrofon",
        "WELTKONTAKT · HÖREN",
        "Mikrofon",
        ("kontinuierlicher auditiver Weltkontakt",),
        "#E8F7F5",
        "#0E7C78",
        "#0E7C78",
    ),
    Block(
        2,
        "kamera",
        "WELTKONTAKT · SEHEN",
        "Kamera",
        ("kontinuierlicher visueller Weltkontakt",),
        "#FFF3DB",
        "#B46B00",
        "#B46B00",
    ),
    Block(
        3,
        "spaeterer_sensor",
        "WELTKONTAKT · FÜHLEN",
        "Späterer Sensor",
        ("taktiler oder innerer Kontakt", "offen, bis reale Sensorik vorhanden ist"),
        "#F4ECFA",
        "#7753A3",
        "#7753A3",
    ),
    Block(
        4,
        "auditive_rezeptorflaeche",
        "REZEPTORFLÄCHE",
        "Auditive Rezeptoren",
        ("lokale Frequenz- und Zeitlagen", "technischer Filter · keine Bedeutung"),
        "#E8F7F5",
        "#0E7C78",
        "#0E7C78",
    ),
    Block(
        5,
        "visuelle_rezeptorflaeche",
        "REZEPTORFLÄCHE",
        "Visuelle Rezeptoren",
        ("lokale Farb-, Licht- und Raumlagen", "technischer Filter · keine Objekte"),
        "#FFF3DB",
        "#B46B00",
        "#B46B00",
    ),
    Block(
        6,
        "taktile_rezeptorflaeche",
        "REZEPTORFLÄCHE",
        "Taktile Rezeptoren",
        ("lokale Druck- und Kontaktlagen", "offen, bis reale Sensorik vorhanden ist"),
        "#F4ECFA",
        "#7753A3",
        "#7753A3",
    ),
    Block(
        7,
        "neutraler_rezeptorenverteiler",
        "NEUTRAL",
        "Rezeptorenverteiler",
        (
            "gemeinsame Organismuszeit",
            "Herkunft und Geometrie bleiben erhalten",
            "keine Bedeutung · kein Memory · keine harte Fusion",
        ),
        "#EDF1F5",
        "#52627A",
        "#52627A",
    ),
    Block(
        8,
        "auditiver_dock",
        "MCM-ANDOCKBEREICH",
        "Auditiver Dock",
        ("auditiver Rezeptorkontakt im gemeinsamen Feld",),
        "#E8F7F5",
        "#0E7C78",
        "#0E7C78",
    ),
    Block(
        9,
        "visueller_dock",
        "MCM-ANDOCKBEREICH",
        "Visueller Dock",
        ("visueller Rezeptorkontakt im gemeinsamen Feld",),
        "#FFF3DB",
        "#B46B00",
        "#B46B00",
    ),
    Block(
        10,
        "taktiler_dock",
        "MCM-ANDOCKBEREICH",
        "Taktiler Dock",
        ("taktiler Rezeptorkontakt im gemeinsamen Feld",),
        "#F4ECFA",
        "#7753A3",
        "#7753A3",
    ),
    Block(
        11,
        "gemeinsames_mcm_feld_rahmen",
        "EIN ORGANISMUSFELD",
        "Gemeinsames MCM-Feld",
        (
            "ein Nervengerüst für alle Sinneseingänge",
            "keine getrennten auditiven, visuellen oder taktilen MCMs",
        ),
        "#F1FAF8",
        "#087F78",
        "#087F78",
        kind="container",
    ),
    Block(
        12,
        "gemeinsame_mcm_neuronenschicht",
        "GEMEINSAMES NERVENGERÜST",
        "MCM-Neuronenschicht",
        (
            "überall derselbe lokale Neuronentyp",
            "eigener Kontakt · eigener Zustand · lokale Feldproben",
        ),
        "#E7F4FD",
        "#2378A8",
        "#2378A8",
    ),
    Block(
        13,
        "gegenwaertige_multimodale_feldlage",
        "GEGENWART",
        "Multimodale Feldlage",
        (
            "aktueller Zustand des gemeinsamen MCM-Feldes",
            "Aktivierung · Nachhall · lokale Feldwirkung",
            "kein nachgeschaltetes Fusionsmodul",
        ),
        "#DDF4EF",
        "#087F78",
        "#087F78",
    ),
    Block(
        14,
        "entwickelbare_feldtopologie",
        "FORSCHUNG OFFEN",
        "Entwickelbare Feldtopologie",
        (
            "Beziehungen durch gemeinsame Feldwirkung",
            "stabilisieren · abschwächen · lösen · neu binden",
            "keine vorgegebene Zieltopologie",
        ),
        "#FFF1D6",
        "#B96A00",
        "#B96A00",
    ),
    Block(
        15,
        "organisches_memory",
        "KEINE DATENBANK",
        "Organisches Memory",
        (
            "gegenwärtig wirksame Feldorganisation",
            "keine Rohdaten · keine Objektablage · kein Episodenarchiv",
        ),
        "#FDEBE7",
        "#B94D3E",
        "#B94D3E",
    ),
    Block(
        16,
        "semantischer_resonanzraum",
        "FORSCHUNG OFFEN",
        "Semantischer Resonanzraum",
        (
            "wiederkehrende Feldformen und Beziehungen",
            "innere Bezeichnung entsteht aus Weltteilnahme",
            "keine fest programmierte Klasse",
        ),
        "#E7F4FD",
        "#1577B8",
        "#1577B8",
    ),
    Block(
        17,
        "reflexionsschicht",
        "FORSCHUNG OFFEN",
        "Reflexionsschicht",
        (
            "liest die gegenwärtige innere Feldlage",
            "mögliche erneute Wirkung auf das eigene Feld",
            "keine feste Bezeichnung oder Klasse",
        ),
        "#FFF1D6",
        "#B96A00",
        "#B96A00",
    ),
    Block(
        18,
        "resonanz_zu_sprache",
        "SPÄTER",
        "Resonanz zu Sprache",
        (
            "Sprache folgt der entstandenen inneren Feldform",
            "Wörter sind weitere erfahrene Feldformen",
        ),
        "#EEF0FA",
        "#5567A8",
        "#5567A8",
    ),
    Block(
        19,
        "offline_erholung",
        "REDUZIERTER WELTKONTAKT",
        "Offline-Erholung",
        (
            "Aktivierung und Nachhall dürfen relaxieren",
            "Beziehungen können Wirkung und Ressource verlieren",
            "kein Training · keine Labels · kein Replay",
        ),
        "#EAF4FC",
        "#2F78A8",
        "#2F78A8",
    ),
    Block(
        20,
        "architekturkorrektur",
        "ARCHITEKTURKORREKTUR",
        "Keine getrennten Sinnes-MCM-Felder",
        (
            "Audio, Video und Taktil bleiben Rezeptorbereiche",
            "Topologie und Memory entstehen nur im gemeinsamen MCM-Feld",
        ),
        "#FDEBE7",
        "#B94D3E",
        "#B94D3E",
    ),
    Block(
        21,
        "leitplanken",
        "BINDENDE LEITPLANKEN",
        "Organische Entwicklung",
        (
            "keine feste Semantik · kein globaler Gewinner",
            "kein Reward-Ziel · keine unveränderliche Verdrahtung",
            "Observer bleibt passiv",
        ),
        "#EDF1F5",
        "#26364D",
        "#52627A",
    ),
)


def _hex_rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.removeprefix("#")
    return (
        int(value[0:2], 16),
        int(value[2:4], 16),
        int(value[4:6], 16),
        alpha,
    )


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(name, size)


def _fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_name: str,
    initial_size: int,
    maximum_width: int,
) -> ImageFont.FreeTypeFont:
    size = initial_size
    while size > 34:
        font = _font(font_name, size)
        if draw.textbbox((0, 0), text, font=font)[2] <= maximum_width:
            return font
        size -= 2
    return _font(font_name, size)


def _svg(block: Block) -> str:
    width = 1800 if block.kind == "container" else WIDTH
    height = 1100 if block.kind == "container" else HEIGHT
    rect_x = 55 if block.kind == "container" else MARGIN
    rect_y = 55 if block.kind == "container" else MARGIN
    rect_width = width - 2 * rect_x
    rect_height = height - 2 * rect_y
    dash = ' stroke-dasharray="20 14"' if block.kind == "container" else ""
    badge_width = max(270, min(620, 34 + len(block.badge) * 19))
    body = "\n".join(
        f'<text x="{rect_x + 55}" y="{300 + index * 58}" '
        'font-family="Arial, sans-serif" font-size="34" '
        f'fill="#26364D">{escape(line)}</text>'
        for index, line in enumerate(block.lines)
    )
    note = (
        '<text x="900" y="1010" text-anchor="middle" '
        'font-family="Arial, sans-serif" font-size="30" fill="#52627A">'
        "Innenraum für MCM-Bausteine · Verdrahtung in Canva"
        "</text>"
        if block.kind == "container"
        else ""
    )
    ports = (
        ""
        if block.kind == "container"
        else (
            f'<circle cx="{rect_x}" cy="{height / 2}" r="14" '
            f'fill="#FFFFFF" stroke="{block.border}" stroke-width="6"/>'
            f'<circle cx="{rect_x + rect_width}" cy="{height / 2}" r="14" '
            f'fill="#FFFFFF" stroke="{block.border}" stroke-width="6"/>'
        )
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="none"/>
  <rect x="{rect_x}" y="{rect_y}" width="{rect_width}" height="{rect_height}" rx="{RADIUS}"
        fill="{block.fill}" stroke="{block.border}" stroke-width="5"{dash}/>
  <rect x="{rect_x}" y="{rect_y}" width="{rect_width}" height="18" rx="9" fill="{block.accent}"/>
  <rect x="{rect_x + 55}" y="{rect_y + 58}" width="{badge_width}" height="60" rx="18" fill="{block.accent}"/>
  <text x="{rect_x + 85}" y="{rect_y + 99}" font-family="Arial, sans-serif"
        font-size="29" font-weight="700" fill="#FFFFFF">{escape(block.badge)}</text>
  <text x="{rect_x + 55}" y="{rect_y + 220}" font-family="Arial, sans-serif"
        font-size="62" font-weight="700" fill="#17243A">{escape(block.title)}</text>
  {body}
  {note}
  {ports}
</svg>
"""


def _png(block: Block) -> Image.Image:
    width = 1800 if block.kind == "container" else WIDTH
    height = 1100 if block.kind == "container" else HEIGHT
    rect_x = 55 if block.kind == "container" else MARGIN
    rect_y = 55 if block.kind == "container" else MARGIN
    rect = (rect_x, rect_y, width - rect_x, height - rect_y)
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        rect,
        radius=RADIUS,
        fill=_hex_rgba(block.fill),
        outline=_hex_rgba(block.border),
        width=5,
    )
    if block.kind == "container":
        dash_length = 22
        gap = 14
        x0, y0, x1, y1 = rect
        for x in range(x0 + 20, x1 - 20, dash_length + gap):
            draw.line((x, y0, min(x + dash_length, x1), y0), fill=block.border, width=7)
            draw.line((x, y1, min(x + dash_length, x1), y1), fill=block.border, width=7)
        for y in range(y0 + 20, y1 - 20, dash_length + gap):
            draw.line((x0, y, x0, min(y + dash_length, y1)), fill=block.border, width=7)
            draw.line((x1, y, x1, min(y + dash_length, y1)), fill=block.border, width=7)

    draw.rounded_rectangle(
        (rect_x, rect_y, width - rect_x, rect_y + 18),
        radius=9,
        fill=_hex_rgba(block.accent),
    )
    badge_font = _font("arialbd.ttf", 29)
    badge_width = max(270, min(620, 52 + draw.textbbox((0, 0), block.badge, font=badge_font)[2]))
    badge_rect = (
        rect_x + 55,
        rect_y + 58,
        rect_x + 55 + badge_width,
        rect_y + 118,
    )
    draw.rounded_rectangle(badge_rect, radius=18, fill=_hex_rgba(block.accent))
    draw.text(
        (rect_x + 81, rect_y + 72),
        block.badge,
        font=badge_font,
        fill=(255, 255, 255, 255),
    )
    title_font = _fit_font(
        draw,
        block.title,
        "arialbd.ttf",
        62,
        width - 2 * rect_x - 110,
    )
    draw.text(
        (rect_x + 55, rect_y + 150),
        block.title,
        font=title_font,
        fill=_hex_rgba("#17243A"),
    )
    body_font = _font("arial.ttf", 34)
    for index, line in enumerate(block.lines):
        draw.text(
            (rect_x + 55, 295 + index * 58),
            line,
            font=body_font,
            fill=_hex_rgba("#26364D"),
        )
    if block.kind == "container":
        note = "Innenraum für MCM-Bausteine · Verdrahtung in Canva"
        note_font = _font("arial.ttf", 30)
        note_width = draw.textbbox((0, 0), note, font=note_font)[2]
        draw.text(
            ((width - note_width) / 2, 980),
            note,
            font=note_font,
            fill=_hex_rgba("#52627A"),
        )
    else:
        for x in (rect_x, width - rect_x):
            draw.ellipse(
                (x - 14, height / 2 - 14, x + 14, height / 2 + 14),
                fill=(255, 255, 255, 255),
                outline=_hex_rgba(block.border),
                width=6,
            )
    return image


def _overview(images: list[tuple[Block, Image.Image]]) -> Image.Image:
    columns = 3
    thumb_width = 700
    thumb_height = 270
    gap = 40
    rows = (len(images) + columns - 1) // columns
    canvas = Image.new(
        "RGB",
        (
            columns * thumb_width + (columns + 1) * gap,
            rows * thumb_height + (rows + 1) * gap,
        ),
        "#F4F6F8",
    )
    for index, (_, source) in enumerate(images):
        thumbnail = source.copy()
        thumbnail.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        x = gap + (index % columns) * (thumb_width + gap)
        y = gap + (index // columns) * (thumb_height + gap)
        x += (thumb_width - thumbnail.width) // 2
        y += (thumb_height - thumbnail.height) // 2
        canvas.paste(thumbnail, (x, y), thumbnail)
    return canvas


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rendered = []
    for block in BLOCKS:
        svg_path = OUTPUT / f"{block.stem}.svg"
        png_path = OUTPUT / f"{block.stem}.png"
        svg_path.write_text(_svg(block), encoding="utf-8", newline="\n")
        image = _png(block)
        image.save(png_path, optimize=True)
        rendered.append((block, image))

    _overview(rendered).save(
        OUTPUT / "00_uebersicht_aller_bausteine.png",
        optimize=True,
    )

    archive = OUTPUT / "mcm_canva_bausteine.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(OUTPUT.glob("*.svg")):
            bundle.write(path, path.name)
        for path in sorted(OUTPUT.glob("[0-9][0-9]_*.png")):
            if path.name != "00_uebersicht_aller_bausteine.png":
                bundle.write(path, path.name)

    print(f"generated={len(BLOCKS)}")
    print(f"output={OUTPUT}")


if __name__ == "__main__":
    main()
