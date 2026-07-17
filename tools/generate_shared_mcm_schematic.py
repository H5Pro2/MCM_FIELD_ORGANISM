from __future__ import annotations

from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BLOCKS = ROOT / "docs" / "bilder" / "architektur" / "canva_bausteine"
OUTPUT = (
    ROOT
    / "docs"
    / "bilder"
    / "architektur"
    / "mcm_field_organism_gemeinsames_feld_schaltplan.png"
)

WIDTH = 3200
HEIGHT = 1800
BACKGROUND = "#F5F7FA"
INK = "#17243A"
MUTED = "#52627A"
BLACK = "#111820"
TEAL = "#087F78"
BLUE = "#2F9FDF"
ORANGE = "#B96A00"
PURPLE = "#586DB0"
FIELD_FILL = "#EDF9F6"
FIELD_BORDER = "#087F78"


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", size)


def load_block(stem: str, size: tuple[int, int]) -> Image.Image:
    source = Image.open(BLOCKS / f"{stem}.png").convert("RGBA")
    return source.resize(size, Image.Resampling.LANCZOS)


def paste_block(
    canvas: Image.Image,
    stem: str,
    box: tuple[int, int, int, int],
) -> None:
    x0, y0, x1, y1 = box
    canvas.alpha_composite(load_block(stem, (x1 - x0, y1 - y0)), (x0, y0))


def dashed_segment(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    *,
    fill: str,
    width: int,
    dash: int = 24,
    gap: int = 16,
) -> None:
    x0, y0 = start
    x1, y1 = end
    length = math.hypot(x1 - x0, y1 - y0)
    if length == 0:
        return
    dx = (x1 - x0) / length
    dy = (y1 - y0) / length
    position = 0.0
    while position < length:
        segment_end = min(position + dash, length)
        draw.line(
            (
                x0 + dx * position,
                y0 + dy * position,
                x0 + dx * segment_end,
                y0 + dy * segment_end,
            ),
            fill=fill,
            width=width,
        )
        position += dash + gap


def arrow_head(
    draw: ImageDraw.ImageDraw,
    previous: tuple[int, int],
    end: tuple[int, int],
    *,
    fill: str,
    size: int = 22,
) -> None:
    px, py = previous
    ex, ey = end
    angle = math.atan2(ey - py, ex - px)
    left = (
        ex - size * math.cos(angle - math.pi / 6),
        ey - size * math.sin(angle - math.pi / 6),
    )
    right = (
        ex - size * math.cos(angle + math.pi / 6),
        ey - size * math.sin(angle + math.pi / 6),
    )
    draw.polygon((end, left, right), fill=fill)


def connector(
    draw: ImageDraw.ImageDraw,
    points: tuple[tuple[int, int], ...],
    *,
    fill: str = BLACK,
    width: int = 9,
    dashed: bool = False,
    arrow: bool = True,
    start_arrow: bool = False,
) -> None:
    for start, end in zip(points, points[1:]):
        if dashed:
            dashed_segment(draw, start, end, fill=fill, width=width)
        else:
            draw.line((*start, *end), fill=fill, width=width, joint="curve")
    if arrow:
        arrow_head(draw, points[-2], points[-1], fill=fill)
    if start_arrow:
        arrow_head(draw, points[1], points[0], fill=fill)


def card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    badge: str,
    title: str,
    lines: tuple[str, ...],
    fill: str,
    accent: str,
    dashed: bool = False,
) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(
        box,
        radius=24,
        fill=fill,
        outline=accent,
        width=5,
    )
    if dashed:
        for x in range(x0 + 18, x1 - 18, 34):
            draw.line((x, y0, min(x + 20, x1), y0), fill=accent, width=7)
            draw.line((x, y1, min(x + 20, x1), y1), fill=accent, width=7)
        for y in range(y0 + 18, y1 - 18, 34):
            draw.line((x0, y, x0, min(y + 20, y1)), fill=accent, width=7)
            draw.line((x1, y, x1, min(y + 20, y1)), fill=accent, width=7)
    badge_font = font(25, bold=True)
    badge_width = draw.textbbox((0, 0), badge, font=badge_font)[2] + 50
    draw.rounded_rectangle(
        (x0 + 34, y0 + 30, x0 + 34 + badge_width, y0 + 82),
        radius=15,
        fill=accent,
    )
    draw.text(
        (x0 + 59, y0 + 42),
        badge,
        font=badge_font,
        fill="#FFFFFF",
    )
    title_font = font(48, bold=True)
    draw.text((x0 + 38, y0 + 112), title, font=title_font, fill=INK)
    body_font = font(23)
    for index, line in enumerate(lines):
        draw.text(
            (x0 + 40, y0 + 158 + index * 36),
            line,
            font=body_font,
            fill=INK,
        )


def network_band(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(
        box,
        radius=26,
        fill="#FFF2D9",
        outline=ORANGE,
        width=5,
    )
    nodes = (
        (x0 + 65, y0 + 128),
        (x0 + 135, y0 + 80),
        (x0 + 210, y0 + 140),
        (x0 + 285, y0 + 88),
        (x0 + 365, y0 + 138),
        (x0 + 430, y0 + 82),
    )
    for first, second, strength in (
        (0, 1, 5),
        (1, 2, 9),
        (2, 3, 6),
        (3, 4, 10),
        (4, 5, 4),
        (1, 4, 3),
    ):
        draw.line((*nodes[first], *nodes[second]), fill=ORANGE, width=strength)
    for x, y in nodes:
        draw.ellipse((x - 15, y - 15, x + 15, y + 15), fill="#FFFFFF", outline=ORANGE, width=5)
    draw.text(
        (x0 + 490, y0 + 34),
        "Feldtopologie = organisches Memory",
        font=font(34, bold=True),
        fill=INK,
    )
    draw.text(
        (x0 + 490, y0 + 91),
        "wirksame Beziehungen im gemeinsamen Feld",
        font=font(22),
        fill=INK,
    )
    draw.text(
        (x0 + 490, y0 + 132),
        "stabilisieren · abschwächen · lösen · neu binden",
        font=font(22),
        fill=INK,
    )
    draw.text(
        (x0 + 490, y0 + 173),
        "kein separates Modul · keine Datenbank",
        font=font(22),
        fill=MUTED,
    )


def main() -> None:
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(canvas)

    draw.rectangle((0, 0, WIDTH, 16), fill=TEAL)
    draw.text((70, 50), "MCM FIELD ORGANISM", font=font(61, bold=True), fill=INK)
    draw.text(
        (70, 124),
        "Korrigierte Verdrahtung des gemeinsamen MCM-Feldes",
        font=font(31),
        fill=MUTED,
    )

    draw.line((1840, 92, 1910, 92), fill=BLACK, width=8)
    draw.text((1925, 70), "Weltursache", font=font(24), fill=MUTED)
    dashed_segment(draw, (2240, 92), (2310, 92), fill=ORANGE, width=8)
    draw.text((2325, 70), "Forschung offen", font=font(24), fill=MUTED)
    dashed_segment(draw, (2700, 92), (2770, 92), fill=BLUE, width=8)
    draw.text((2785, 70), "Rückwirkung / Modus", font=font(24), fill=MUTED)

    sensor_boxes = (
        ("02_kamera", (45, 300, 365, 424)),
        ("01_mikrofon", (45, 560, 365, 684)),
        ("03_spaeterer_sensor", (45, 820, 365, 944)),
    )
    receptor_boxes = (
        ("05_visuelle_rezeptorflaeche", (420, 278, 795, 422)),
        ("04_auditive_rezeptorflaeche", (420, 538, 795, 682)),
        ("06_taktile_rezeptorflaeche", (420, 798, 795, 942)),
    )
    for stem, box in sensor_boxes + receptor_boxes:
        paste_block(canvas, stem, box)

    distributor = (860, 535, 1240, 682)
    paste_block(canvas, "07_neutraler_rezeptorenverteiler", distributor)

    for sensor, receptor in zip(sensor_boxes, receptor_boxes):
        _, sensor_box = sensor
        _, receptor_box = receptor
        sy = (sensor_box[1] + sensor_box[3]) // 2
        ry = (receptor_box[1] + receptor_box[3]) // 2
        connector(
            draw,
            ((sensor_box[2], sy), (receptor_box[0], ry)),
            fill=BLACK,
            width=9,
        )

    distributor_input = (distributor[0], (distributor[1] + distributor[3]) // 2)
    bus_x = 825
    draw.line((bus_x, 350, bus_x, 870), fill=BLACK, width=9)
    for _, receptor_box in receptor_boxes:
        y = (receptor_box[1] + receptor_box[3]) // 2
        draw.line((receptor_box[2], y, bus_x, y), fill=BLACK, width=9)
    connector(draw, ((bus_x, distributor_input[1]), distributor_input), fill=BLACK, width=9)

    field = (1300, 190, 3130, 1420)
    draw.rounded_rectangle(
        field,
        radius=32,
        fill=FIELD_FILL,
        outline=FIELD_BORDER,
        width=6,
    )
    draw.rectangle((1300, 190, 3130, 208), fill=TEAL)
    draw.rounded_rectangle((1355, 235, 1730, 295), radius=18, fill=TEAL)
    draw.text((1382, 250), "EIN ORGANISMUSFELD", font=font(27, bold=True), fill="#FFFFFF")
    draw.text((1355, 325), "Gemeinsames MCM-Feld", font=font(56, bold=True), fill=INK)
    draw.text(
        (1355, 392),
        "Neuronenzustand, Feldtopologie und Memory sind ein gemeinsamer Organismuszustand.",
        font=font(29),
        fill=MUTED,
    )

    dock_boxes = (
        ("09_visueller_dock", (1360, 490, 1740, 636)),
        ("08_auditiver_dock", (1360, 690, 1740, 836)),
        ("10_taktiler_dock", (1360, 890, 1740, 1036)),
    )
    for stem, box in dock_boxes:
        paste_block(canvas, stem, box)

    neuron_box = (1930, 475, 2830, 720)
    paste_block(canvas, "12_gemeinsame_mcm_neuronenschicht", neuron_box)

    semantic_box = (1950, 1125, 2980, 1400)
    card(
        draw,
        semantic_box,
        badge="ENTSTEHENDE FELDFÄHIGKEIT",
        title="Semantische Resonanz",
        lines=(
            "wiederkehrende Feldformen und Beziehungen",
            "innere Bezeichnung entsteht aus Weltteilnahme",
            "Sprache wird später als weitere Feldform angebunden",
        ),
        fill="#E8F2FC",
        accent="#2378A8",
        dashed=True,
    )

    topology_box = (1810, 825, 3000, 1055)
    network_band(draw, topology_box)

    distributor_output = (distributor[2], (distributor[1] + distributor[3]) // 2)
    dock_bus_x = 1270
    connector(
        draw,
        (distributor_output, (dock_bus_x, distributor_output[1])),
        fill=BLACK,
        width=9,
        arrow=False,
    )
    draw.line((dock_bus_x, 563, dock_bus_x, 963), fill=BLACK, width=9)
    for _, box in dock_boxes:
        y = (box[1] + box[3]) // 2
        connector(draw, ((dock_bus_x, y), (box[0], y)), fill=BLACK, width=9)

    neuron_targets = (535, 595, 655)
    for (_, box), target_y in zip(dock_boxes, neuron_targets):
        y = (box[1] + box[3]) // 2
        connector(
            draw,
            ((box[2], y), (1840, y), (1840, target_y), (neuron_box[0], target_y)),
            fill=TEAL,
            width=9,
        )

    connector(
        draw,
        (
            ((neuron_box[0] + neuron_box[2]) // 2, neuron_box[3]),
            ((neuron_box[0] + neuron_box[2]) // 2, topology_box[1]),
        ),
        fill=ORANGE,
        width=8,
        dashed=True,
        start_arrow=True,
    )
    connector(
        draw,
        (
            ((topology_box[0] + topology_box[2]) // 2, topology_box[3]),
            ((topology_box[0] + topology_box[2]) // 2, semantic_box[1]),
        ),
        fill=ORANGE,
        width=8,
        dashed=True,
        start_arrow=True,
    )

    reflection_box = (1450, 1510, 2150, 1745)
    offline_box = (2350, 1510, 3050, 1745)
    card(
        draw,
        reflection_box,
        badge="FORSCHUNG OFFEN",
        title="Reflexion",
        lines=(
            "gegenwärtiges Feld erzeugt innere Rückwirkung",
            "dieselbe MCM-Neuronenschicht wird erneut angeregt",
        ),
        fill="#FFF1D6",
        accent=ORANGE,
        dashed=True,
    )
    card(
        draw,
        offline_box,
        badge="BETRIEBSMODUS",
        title="Offline-Erholung",
        lines=(
            "reduzierter Weltkontakt",
            "Relaxation, Stabilisierung oder Lösung im selben Feld",
        ),
        fill="#EAF4FC",
        accent="#2F78A8",
        dashed=True,
    )

    connector(
        draw,
        ((1750, field[3]), (1750, reflection_box[1])),
        fill=ORANGE,
        width=9,
        dashed=True,
    )
    connector(
        draw,
        (
            (reflection_box[2], 1615),
            (2250, 1615),
            (2250, 1460),
            (3030, 1460),
            (3030, 595),
            (neuron_box[2], 595),
        ),
        fill=BLUE,
        width=9,
        dashed=True,
    )
    connector(
        draw,
        (
            (offline_box[2], 1625),
            (3110, 1625),
            (3110, field[3]),
        ),
        fill=BLUE,
        width=9,
        dashed=True,
        start_arrow=True,
    )

    card(
        draw,
        (70, 1210, 1110, 1450),
        badge="ARCHITEKTURREGEL",
        title="Entwicklung geschieht im Feld",
        lines=(
            "während Weltkontakt, Reflexion und Offline-Erholung",
            "keine feste Semantik · kein Reward-Ziel · keine starre Verdrahtung",
        ),
        fill="#EDF1F5",
        accent="#52627A",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rendered = canvas.convert("RGB")
    rendered.save(OUTPUT, quality=96, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
