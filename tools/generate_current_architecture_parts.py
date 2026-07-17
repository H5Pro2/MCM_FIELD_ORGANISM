from __future__ import annotations

from pathlib import Path
import shutil
import zipfile

from PIL import Image, ImageDraw

from generate_shared_mcm_schematic import (
    BLUE,
    FIELD_BORDER,
    FIELD_FILL,
    INK,
    MUTED,
    ORANGE,
    TEAL,
    card,
    font,
    network_band,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "bilder" / "architektur" / "canva_bausteine"
OUTPUT = (
    ROOT
    / "docs"
    / "bilder"
    / "architektur"
    / "canva_einzelteile_gemeinsames_mcm_feld"
)

COPIED_PARTS = (
    ("02_kamera.png", "01_kamera.png"),
    ("05_visuelle_rezeptorflaeche.png", "02_visuelle_rezeptoren.png"),
    ("01_mikrofon.png", "03_mikrofon.png"),
    ("04_auditive_rezeptorflaeche.png", "04_auditive_rezeptoren.png"),
    ("03_spaeterer_sensor.png", "05_spaeterer_sensor.png"),
    ("06_taktile_rezeptorflaeche.png", "06_taktile_rezeptoren.png"),
    ("07_neutraler_rezeptorenverteiler.png", "07_rezeptorenverteiler.png"),
    ("09_visueller_dock.png", "09_visueller_dock.png"),
    ("08_auditiver_dock.png", "10_auditiver_dock.png"),
    ("10_taktiler_dock.png", "11_taktiler_dock.png"),
    ("12_gemeinsame_mcm_neuronenschicht.png", "12_mcm_neuronenschicht.png"),
)


def transparent_canvas(width: int, height: int) -> Image.Image:
    return Image.new("RGBA", (width, height), (255, 255, 255, 0))


def save_field_frame() -> None:
    canvas = transparent_canvas(1900, 1320)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (25, 25, 1875, 1295),
        radius=32,
        fill=FIELD_FILL,
        outline=FIELD_BORDER,
        width=6,
    )
    draw.rectangle((25, 25, 1875, 43), fill=TEAL)
    draw.rounded_rectangle((80, 70, 455, 130), radius=18, fill=TEAL)
    draw.text(
        (107, 85),
        "EIN ORGANISMUSFELD",
        font=font(27, bold=True),
        fill="#FFFFFF",
    )
    draw.text(
        (80, 165),
        "Gemeinsames MCM-Feld",
        font=font(56, bold=True),
        fill=INK,
    )
    draw.text(
        (80, 235),
        "Neuronenzustand, Feldtopologie und Memory sind ein gemeinsamer Organismuszustand.",
        font=font(29),
        fill=MUTED,
    )
    canvas.save(OUTPUT / "08_gemeinsames_mcm_feld_rahmen.png", optimize=True)


def save_topology_memory() -> None:
    canvas = transparent_canvas(1260, 300)
    network_band(ImageDraw.Draw(canvas), (30, 30, 1230, 270))
    canvas.save(OUTPUT / "13_feldtopologie_organisches_memory.png", optimize=True)


def save_card(
    filename: str,
    *,
    size: tuple[int, int],
    badge: str,
    title: str,
    lines: tuple[str, ...],
    fill: str,
    accent: str,
    dashed: bool = False,
) -> None:
    width, height = size
    canvas = transparent_canvas(width, height)
    card(
        ImageDraw.Draw(canvas),
        (30, 30, width - 30, height - 30),
        badge=badge,
        title=title,
        lines=lines,
        fill=fill,
        accent=accent,
        dashed=dashed,
    )
    canvas.save(OUTPUT / filename, optimize=True)


def save_custom_parts() -> None:
    save_field_frame()
    save_topology_memory()
    save_card(
        "14_semantische_resonanz.png",
        size=(1120, 360),
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
    save_card(
        "15_reflexion.png",
        size=(760, 300),
        badge="FORSCHUNG OFFEN",
        title="Reflexion",
        lines=(
            "gegenwärtiges Feld erzeugt innere Rückwirkung",
            "dieselbe MCM-Neuronenschicht wird erneut angeregt",
        ),
        fill="#FFF2D9",
        accent=ORANGE,
        dashed=True,
    )
    save_card(
        "16_offline_erholung.png",
        size=(760, 300),
        badge="BETRIEBSMODUS",
        title="Offline-Erholung",
        lines=(
            "reduzierter Weltkontakt",
            "Relaxation, Stabilisierung oder Lösung im selben Feld",
        ),
        fill="#E8F2FC",
        accent="#2378A8",
        dashed=True,
    )
    save_card(
        "17_architekturregel.png",
        size=(1120, 320),
        badge="ARCHITEKTURREGEL",
        title="Entwicklung geschieht im Feld",
        lines=(
            "während Weltkontakt, Reflexion und Offline-Erholung",
            "keine feste Semantik · kein Reward-Ziel · keine starre Verdrahtung",
        ),
        fill="#EDF1F5",
        accent="#52627A",
    )


def save_overview(part_paths: list[Path]) -> None:
    thumb_width = 720
    thumb_height = 360
    gap = 45
    columns = 3
    rows = (len(part_paths) + columns - 1) // columns
    canvas = Image.new(
        "RGB",
        (
            columns * thumb_width + (columns + 1) * gap,
            rows * thumb_height + (rows + 1) * gap + 100,
        ),
        "#F5F7FA",
    )
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (gap, 28),
        "MCM FIELD ORGANISM · EINZELTEILE",
        font=font(42, bold=True),
        fill=INK,
    )
    for index, path in enumerate(part_paths):
        row, column = divmod(index, columns)
        x = gap + column * (thumb_width + gap)
        y = 110 + gap + row * (thumb_height + gap)
        image = Image.open(path).convert("RGBA")
        image.thumbnail((thumb_width - 30, thumb_height - 65), Image.Resampling.LANCZOS)
        px = x + (thumb_width - image.width) // 2
        py = y + 10 + (thumb_height - 65 - image.height) // 2
        canvas.paste(image, (px, py), image)
        draw.text(
            (x + 10, y + thumb_height - 42),
            path.stem,
            font=font(19),
            fill=MUTED,
        )
    canvas.save(OUTPUT / "00_uebersicht_aller_einzelteile.png", optimize=True)


def save_archive(part_paths: list[Path]) -> None:
    archive = OUTPUT / "mcm_gemeinsames_feld_einzelteile.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in part_paths:
            bundle.write(path, path.name)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for old_png in OUTPUT.glob("[0-9][0-9]_*.png"):
        old_png.unlink()

    for source_name, target_name in COPIED_PARTS:
        shutil.copyfile(SOURCE / source_name, OUTPUT / target_name)

    save_custom_parts()
    part_paths = sorted(OUTPUT.glob("[0-9][0-9]_*.png"))
    save_overview(part_paths)
    save_archive(part_paths)

    print(f"generated={len(part_paths)}")
    print(f"output={OUTPUT}")


if __name__ == "__main__":
    main()
