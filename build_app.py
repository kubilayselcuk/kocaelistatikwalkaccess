from __future__ import annotations

import json
import subprocess
import unicodedata
from pathlib import Path

import geopandas as gpd


WORKDIR = Path(__file__).resolve().parent
EXTRACT_DIR = WORKDIR / "input_data_multi"
OUTPUT_HTML = WORKDIR / "index.html"
SOURCE_ARCHIVE = WORKDIR / "input_data_multi.rar"
WAI_EXTRACT_DIR = WORKDIR / "wai_input"
WAI_ARCHIVE = WORKDIR / "Index31082026.gdb.rar"
WAI_GDB_FOLDER = "Index31082026.gdb"
WAI_LAYER = "hex_data"
ANALYSIS_KEYS = ("Analiz1", "Analiz2", "Analiz3")
FALLBACK_STYLE = {"color": "#94a3b8", "rank": 0}


THEMES = {
    "saglik": {
        "filename": "Sağlık_tesisleri_hexanaliz.zip",
        "title": "Sağlık Tesisi",
        "menu": "Sağlık",
        "subtitle": "Sağlık tesislerine yaya erişimi",
        "target_plural_dative": "sağlık tesislerine",
        "target_plural_accusative": "sağlık tesislerini",
        "target_singular_accusative": "bir sağlık tesisini",
        "description": "Sağlık tesislerine erişim kalitesini, yakınlık ve seçenek çeşitliliği açısından birlikte okur.",
    },
    "okul": {
        "filename": "Okul_hexanaliz.zip",
        "title": "Okul",
        "menu": "Okul",
        "subtitle": "Eğitim odaklarına yaya erişim",
        "target_plural_dative": "okullara",
        "target_plural_accusative": "okulları",
        "target_singular_accusative": "bir okulu",
        "description": "Okul erişilebilirliğini, günlük yaya erişimi ve yakın çevredeki eğitim seçenekleri üzerinden görünür kılar.",
    },
    "kamu": {
        "filename": "Kamu_hexanaliz.zip",
        "title": "Kamu",
        "menu": "Kamu",
        "subtitle": "Kamu kullanımlarına yaya erişim",
        "target_plural_dative": "kamu kullanımlarına",
        "target_plural_accusative": "kamu kullanımlarını",
        "target_singular_accusative": "bir kamu kullanımını",
        "description": "Kamu hizmetlerine erişimin hangi bölgelerde güçlü, hangi bölgelerde sınırlı olduğunu katmanlı biçimde gösterir.",
    },
    "ticari": {
        "filename": "Ticari_hexanaliz.zip",
        "title": "Ticari Alan",
        "menu": "Ticari",
        "subtitle": "Ticari alanlara yaya erişim",
        "target_plural_dative": "ticari alanlara",
        "target_plural_accusative": "ticari alanları",
        "target_singular_accusative": "bir ticari alanı",
        "description": "Ticari odaklara yürüme erişimini ve yakın çevredeki alternatif yoğunluğunu birlikte okumayı sağlar.",
    },
    "spor": {
        "filename": "Spor_tesisleri_hexanaliz.zip",
        "title": "Spor Tesisi",
        "menu": "Spor",
        "subtitle": "Spor tesislerine yaya erişim",
        "target_plural_dative": "spor tesislerine",
        "target_plural_accusative": "spor tesislerini",
        "target_singular_accusative": "bir spor tesisini",
        "description": "Spor tesislerine erişim düzeylerini, en yakın erişim ve erişilebilir seçenek sayısı ile beraber özetler.",
    },
    "sosyal": {
        "filename": "Sosyal_toplumsal_donatı_hexanaliz.zip",
        "title": "Sosyal ve Toplumsal Donatı",
        "menu": "Sosyal Donatı",
        "subtitle": "Sosyal ve toplumsal donatı alanlarına yaya erişim",
        "target_plural_dative": "sosyal ve toplumsal donatı alanlarına",
        "target_plural_accusative": "sosyal ve toplumsal donatı alanlarını",
        "target_singular_accusative": "bir sosyal veya toplumsal donatı alanını",
        "description": "Mahalle yaşamını destekleyen donatı alanlarına erişimin ne kadar dengeli dağıldığını gösterir.",
    },
    "rekreasyon": {
        "filename": "Rekreasyon_hexanaliz.zip",
        "title": "Rekreasyon",
        "menu": "Rekreasyon",
        "subtitle": "Rekreasyon alanlarına yaya erişim",
        "target_plural_dative": "rekreasyon alanlarına",
        "target_plural_accusative": "rekreasyon alanlarını",
        "target_singular_accusative": "bir rekreasyon alanını",
        "description": "Açık alan ve rekreasyon kullanımına günlük erişimi, seçenek yoğunluğu ile birlikte değerlendirir.",
    },
    "otobus": {
        "filename": "Otobüs_Durak_hexanaliz.zip",
        "title": "Otobüs Durağı",
        "menu": "Otobüs",
        "subtitle": "Otobüs duraklarına yaya erişim",
        "target_plural_dative": "otobüs duraklarına",
        "target_plural_accusative": "otobüs duraklarını",
        "target_singular_accusative": "bir otobüs durağını",
        "description": "Toplu taşımanın en yaygın erişim katmanı olan otobüs duraklarına yaya yakınlığı net biçimde ortaya koyar.",
    },
    "rayli": {
        "filename": "Raylı_sistem_durak_hexanaliz.zip",
        "title": "Raylı Sistem Durağı",
        "menu": "Raylı Sistem",
        "subtitle": "Raylı sistem duraklarına yaya erişim",
        "target_plural_dative": "raylı sistem duraklarına",
        "target_plural_accusative": "raylı sistem duraklarını",
        "target_singular_accusative": "bir raylı sistem durağını",
        "description": "Raylı sistem istasyonlarına erişim düzeyini ve yakın çevredeki erişim alternatiflerini birlikte okumaya yardımcı olur.",
    },
}


VALUE_REPLACEMENTS = {
    "eriţim": "erişim",
    "Eriţilebilir": "Erişilebilir",
    "Deđil": "Değil",
    "Çok iyi eriţim": "Çok iyi erişim",
    "Orta eriţim": "Orta erişim",
    "Az eriţim": "Az erişim",
}


ANALYSIS_META = {
    "Analiz1": {
        "title": "Analiz 1",
        "method": "Sınıflama: <15 dk = Erişilebilir | 15-20 dk = Orta erişim | 20-25 dk = Az erişim | 25+ dk = Yaya erişimi yok",
    },
    "Analiz2": {
        "title": "Analiz 2",
        "method": "Değerlendirme: 15 dk içindeki hedef sayısı, en yakın mesafe ve 1/rank ile ağırlıklandırılmış puana göre yapılmıştır.",
    },
    "Analiz3": {
        "title": "Analiz",
        "method": "Sınıflama: 0-5 dk = Çok iyi erişim | 5-10 dk = Orta erişim | 10-15 dk = Az erişim | 15+ dk = Yaya erişimi yok",
    },
}


VALUE_STYLE = {
    "Erişilebilir": {"color": "#20a35a", "rank": 4},
    "Çok iyi erişim": {"color": "#4faa63", "rank": 4},
    "Orta erişim": {"color": "#9ddf7a", "rank": 3},
    "Az erişim": {"color": "#ea8a2f", "rank": 2},
    "Yaya erişimi yok": {"color": "#d64541", "rank": 1},
}


WAI_CLASSES = [
    {"label": "0.69 - 20.00", "min": 0.69, "max": 20.00, "color": "#2c9bd6"},
    {"label": "20.01 - 30.00", "min": 20.01, "max": 30.00, "color": "#9fbe90"},
    {"label": "30.01 - 39.93", "min": 30.01, "max": 39.93, "color": "#fff45a"},
    {"label": "39.94 - 60.00", "min": 39.94, "max": 60.00, "color": "#f59a3d"},
    {"label": "60.01 - 74.32", "min": 60.01, "max": 74.32, "color": "#ef1d17"},
]


def normalize_text(value: object) -> str:
    text = "" if value is None else str(value)
    for source, target in VALUE_REPLACEMENTS.items():
        text = text.replace(source, target)
    return text


def analysis_columns(columns: list[str]) -> dict[str, str]:
    lowered = {col.lower(): col for col in columns}
    mapping: dict[str, str] = {}
    for index in (1, 2, 3):
        for candidate in (f"analiz{index}", f"analiz_{index}"):
            if candidate in lowered:
                mapping[f"Analiz{index}"] = lowered[candidate]
                break
    missing = [name for name in ANALYSIS_KEYS if name not in mapping]
    if missing:
        raise ValueError(f"Eksik analiz alanları: {missing}")
    return mapping


def ensure_source_archive_extracted() -> Path:
    if not SOURCE_ARCHIVE.exists():
        raise FileNotFoundError(f"Kaynak arşiv bulunamadı: {SOURCE_ARCHIVE}")
    source_target = EXTRACT_DIR / f"from_rar_{SOURCE_ARCHIVE.stat().st_mtime_ns}"
    if source_target.exists():
        nested_root = source_target / "input_data_multi"
        if nested_root.exists() and nested_root.is_dir():
            return nested_root
        return source_target
    source_target.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["tar", "-xf", str(SOURCE_ARCHIVE), "-C", str(source_target)],
        check=True,
    )
    nested_root = source_target / "input_data_multi"
    if nested_root.exists() and nested_root.is_dir():
        return nested_root
    return source_target


def ensure_wai_gdb_extracted() -> Path:
    if not WAI_ARCHIVE.exists():
        raise FileNotFoundError(f"WAI arşivi bulunamadı: {WAI_ARCHIVE}")

    target_root = WAI_EXTRACT_DIR / f"from_rar_{WAI_ARCHIVE.stat().st_mtime_ns}"
    gdb_path = target_root / WAI_GDB_FOLDER
    if gdb_path.exists():
        return gdb_path

    target_root.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["tar", "-xf", str(WAI_ARCHIVE), "-C", str(target_root)],
        check=True,
    )

    if not gdb_path.exists():
        raise FileNotFoundError(f"WAI geodatabase bulunamadı: {gdb_path}")

    return gdb_path


def resolve_theme_folder(theme_filename: str, source_root: Path) -> Path:
    stem = Path(theme_filename).stem
    exact = source_root / stem
    if exact.exists():
        return exact

    def norm(value: str) -> str:
        ascii_only = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
        return ascii_only.lower().replace(" ", "").replace("_", "")

    target_norm = norm(stem)
    for folder in source_root.iterdir():
        if folder.is_dir() and norm(folder.name) == target_norm:
            return folder
    raise FileNotFoundError(f"Tema klasörü bulunamadı: {stem}")


def summarize_values(values: list[str]) -> list[dict]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1

    return [
        {
            "label": label,
            "count": count,
            "color": VALUE_STYLE.get(label, FALLBACK_STYLE)["color"],
            "rank": VALUE_STYLE.get(label, FALLBACK_STYLE)["rank"],
        }
        for label, count in sorted(
            counts.items(),
            key=lambda item: VALUE_STYLE.get(item[0], FALLBACK_STYLE)["rank"],
            reverse=True,
        )
    ]


def find_shapefile(folder: Path) -> Path:
    return next(folder.glob("*.shp"))


def load_theme_data() -> tuple[dict, dict]:
    EXTRACT_DIR.mkdir(exist_ok=True)
    source_root = ensure_source_archive_extracted()
    feature_map: dict[str, dict] = {}
    theme_summaries: dict[str, dict] = {}
    base_theme_id: str | None = None

    for theme_id, theme in THEMES.items():
        theme_dir = resolve_theme_folder(theme["filename"], source_root)
        gdf = gpd.read_file(find_shapefile(theme_dir)).to_crs(epsg=4326)

        cols = analysis_columns(list(gdf.columns))
        gdf["hex_kod"] = gdf["hex_kod"].astype(str)
        for normalized_name, source_name in cols.items():
            gdf[normalized_name] = gdf[source_name].map(normalize_text)

        if theme_id == "saglik":
            for analysis_key in ("Analiz2", "Analiz3"):
                gdf[analysis_key] = gdf[analysis_key].replace({
                    "Erişilebilir Değil": "Yaya erişimi yok",
                    "Erişilebilir değil": "Yaya erişimi yok",
                })

        if base_theme_id is None:
            base_theme_id = theme_id
            geojson = json.loads(gdf[["hex_kod", "geometry"]].to_json(drop_id=True))
            for feature in geojson["features"]:
                hex_code = str(feature["properties"]["hex_kod"])
                feature["properties"] = {"hex_kod": hex_code, "themes": {}}
                feature_map[hex_code] = feature
        else:
            hex_codes = set(feature_map)
            current_codes = set(gdf["hex_kod"].tolist())
            if hex_codes != current_codes:
                raise ValueError(f"Hex kod seti uyuşmuyor: {theme_id}")

        theme_summaries[theme_id] = {}
        for _, row in gdf.iterrows():
            feature_map[row["hex_kod"]]["properties"]["themes"][theme_id] = {
                "Analiz1": row["Analiz1"],
                "Analiz2": row["Analiz2"],
                "Analiz3": row["Analiz3"],
            }

        for analysis_key in ANALYSIS_KEYS:
            theme_summaries[theme_id][analysis_key] = summarize_values(gdf[analysis_key].tolist())

    return {"type": "FeatureCollection", "features": list(feature_map.values())}, theme_summaries


def load_boundary_data() -> dict:
    source_root = ensure_source_archive_extracted()
    matches = [p for p in source_root.iterdir() if p.is_dir() and "hexanaliz" in p.name.lower() and "dis" in p.name.lower()]
    if not matches:
        return {"type": "FeatureCollection", "features": []}
    gdf = gpd.read_file(find_shapefile(matches[0])).to_crs(epsg=4326)
    return json.loads(gdf.to_json(drop_id=True))


def classify_wai(value: float) -> str:
    if value is None or value <= 0:
        return "Analiz Dışı"
    for item in WAI_CLASSES:
        if item["min"] <= value <= item["max"]:
            return item["label"]
    return WAI_CLASSES[-1]["label"]


def load_wai_data(boundary_count: int = 0) -> tuple[dict, list[dict]]:
    gdf = gpd.read_file(ensure_wai_gdb_extracted(), layer=WAI_LAYER).to_crs(epsg=4326)
    hex_col = "Hex_Kodu" if "Hex_Kodu" in gdf.columns else "hex_kod"
    gdf["hex_kod"] = gdf[hex_col].astype(str)
    gdf["WAI"] = gdf["WAI"].astype(float)
    gdf["wai_class"] = gdf["WAI"].map(classify_wai)

    geojson = json.loads(gdf[["hex_kod", "WAI", "wai_class", "geometry"]].to_json(drop_id=True))
    for feature in geojson["features"]:
        props = feature["properties"]
        props["hex_kod"] = str(props["hex_kod"])
        props["wai"] = round(float(props["WAI"]), 2)
        props["wai_class"] = props["wai_class"]
        del props["WAI"]

    wai_summary: list[dict] = [
        {
            "label": "Analiz Dışı",
            "color": "transparent",
            "stroke": "#9ea6ad",
            "count": int((gdf["WAI"] <= 0).sum()) + int(boundary_count),
        }
    ]
    for item in WAI_CLASSES:
        count = int(((gdf["WAI"] >= item["min"]) & (gdf["WAI"] <= item["max"])).sum())
        wai_summary.append(
            {
                "label": item["label"],
                "color": item["color"],
                "stroke": item["color"],
                "count": count,
            }
        )

    return geojson, wai_summary


def build_theme_meta() -> dict[str, dict]:
    theme_meta: dict[str, dict] = {}
    for theme_id, theme in THEMES.items():
        theme_meta[theme_id] = {
            "title": theme["title"],
            "menu": theme["menu"],
            "subtitle": theme["subtitle"],
            "description": theme["description"],
            "analyses": {
                "Analiz1": {
                    "title": ANALYSIS_META["Analiz1"]["title"],
                    "subtitle": f"Tüm hexagonların {theme['target_plural_dative']} olan erişim durumu",
                    "description": (
                        f"Bu görünüm, her hexagonun en yakın {theme['target_singular_accusative']} erişimini özetler. "
                        "Yüksek erişim yeşil ile, erişim düştükçe sarı, turuncu ve kırmızı ile gösterilir."
                    ),
                    "method": ANALYSIS_META["Analiz1"]["method"],
                },
                "Analiz2": {
                    "title": ANALYSIS_META["Analiz2"]["title"],
                    "subtitle": f"15 dk mesafedeki birden fazla {theme['target_plural_dative']} erişim",
                    "description": (
                        f"Bu analiz yalnızca yakınlığı değil, 15 dakika içinde erişilebilen {theme['target_plural_accusative']} çeşitliliğini de dikkate alır. "
                        "Birden fazla seçeneğe rahat erişilen alanlar daha güçlü yeşil tonlarla vurgulanır."
                    ),
                    "method": ANALYSIS_META["Analiz2"]["method"],
                },
                "Analiz3": {
                    "title": ANALYSIS_META["Analiz3"]["title"],
                    "subtitle": f"15 dk mesafedeki en az 1 {theme['target_singular_accusative']} erişim",
                    "description": (
                        f"Bu görünüm, 15 dakika içinde en az bir {theme['target_singular_accusative']} erişimi odak alır. "
                        "İlk temas erişimi güçlü olan bölgeler yeşile yaklaşırken, eşik dışındaki alanlar kırmızıya iner."
                    ),
                    "method": ANALYSIS_META["Analiz3"]["method"],
                },
            },
        }
    return theme_meta


def render_html(geojson: dict, boundary_geojson: dict, wai_geojson: dict, theme_summaries: dict, wai_summary: list[dict], theme_meta: dict) -> str:
    geojson_json = json.dumps(geojson, ensure_ascii=False, separators=(",", ":"))
    boundary_json = json.dumps(boundary_geojson, ensure_ascii=False, separators=(",", ":"))
    wai_json = json.dumps(wai_geojson, ensure_ascii=False, separators=(",", ":"))
    summary_json = json.dumps(theme_summaries, ensure_ascii=False, separators=(",", ":"))
    wai_summary_json = json.dumps(wai_summary, ensure_ascii=False, separators=(",", ":"))
    meta_json = json.dumps(theme_meta, ensure_ascii=False)
    style_json = json.dumps(VALUE_STYLE, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Hexagon Erişilebilirlik Analizleri</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link
    rel="stylesheet"
    href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
    crossorigin=""
  />
  <style>
    :root {{
      --bg: #f4f1e8;
      --panel: rgba(255, 251, 243, 0.92);
      --panel-strong: #fffaf0;
      --text: #233127;
      --muted: #58695c;
      --line: rgba(60, 85, 63, 0.14);
      --shadow: 0 18px 42px rgba(64, 52, 34, 0.14);
      --accent: #2f6a45;
      --accent-soft: rgba(47, 106, 69, 0.12);
    }}

    * {{ box-sizing: border-box; }}

    html, body {{
      margin: 0;
      height: 100%;
      font-family: "Manrope", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(255, 214, 143, 0.22), transparent 28%),
        radial-gradient(circle at bottom right, rgba(74, 138, 93, 0.18), transparent 30%),
        var(--bg);
      color: var(--text);
    }}

    body {{
      display: grid;
      grid-template-columns: minmax(360px, 430px) 1fr;
      overflow: hidden;
    }}

    aside {{
      padding: 22px;
      border-right: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(255,255,255,0.78), rgba(255,248,235,0.92));
      backdrop-filter: blur(18px);
      overflow-y: auto;
    }}

    #map {{
      height: 100vh;
      width: 100%;
    }}

    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 18px;
      box-shadow: var(--shadow);
      margin-bottom: 16px;
    }}

    .eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 7px 12px;
      border-radius: 999px;
      background: rgba(47, 106, 69, 0.08);
      color: var(--accent);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}

    h1 {{
      margin: 14px 0 8px;
      font-size: 30px;
      line-height: 1.05;
    }}

    .hero p,
    .analysis-card p,
    .theme-copy {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.6;
    }}

    .section-title {{
      margin: 0 0 12px;
      font-size: 14px;
      font-weight: 800;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: #4a5c4d;
    }}

    .theme-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }}

    .mode-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }}

    .theme-button,
    .tab {{
      border: 1px solid rgba(47, 106, 69, 0.12);
      background: rgba(255,255,255,0.7);
      color: var(--muted);
      border-radius: 16px;
      padding: 12px 12px;
      font: inherit;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      transition: transform 0.2s ease, background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
      text-align: left;
    }}

    .theme-button:hover,
    .tab:hover {{
      transform: translateY(-1px);
      color: var(--text);
    }}

    .theme-button.active,
    .tab.active {{
      background: linear-gradient(135deg, #2f6a45, #4f8858);
      color: white;
      box-shadow: 0 12px 24px rgba(47, 106, 69, 0.2);
    }}

    .theme-button small {{
      display: block;
      margin-top: 4px;
      font-size: 11px;
      font-weight: 600;
      opacity: 0.88;
    }}

    .theme-header {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }}

    .theme-title {{
      font-size: 22px;
      font-weight: 800;
      margin: 0 0 4px;
    }}

    .theme-subtitle {{
      margin: 0;
      color: var(--accent);
      font-weight: 700;
      font-size: 13px;
    }}

    .pill {{
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(47, 106, 69, 0.1);
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
    }}

    .tab-row {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      margin: 14px 0;
    }}

    .analysis-card {{
      padding: 16px;
      border-radius: 20px;
      background: var(--panel-strong);
      border: 1px solid var(--line);
    }}

    .analysis-card h2 {{
      margin: 0;
      font-size: 21px;
    }}

    .analysis-subtitle {{
      margin: 6px 0 12px;
      color: var(--accent);
      font-weight: 700;
      font-size: 13px;
    }}

    .method-box {{
      padding: 12px 14px;
      border-radius: 16px;
      background: rgba(255, 245, 221, 0.8);
      border: 1px solid rgba(180, 146, 60, 0.16);
      color: #6a5624;
      font-size: 13px;
      line-height: 1.6;
      margin-bottom: 14px;
    }}

    .control-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
    }}

    .toggle {{
      position: relative;
      width: 54px;
      height: 30px;
      display: inline-flex;
    }}

    .toggle input {{ display: none; }}

    .toggle span {{
      width: 100%;
      height: 100%;
      border-radius: 999px;
      background: #d8ddd4;
      position: relative;
      transition: background 0.2s ease;
      cursor: pointer;
    }}

    .toggle span::after {{
      content: "";
      position: absolute;
      top: 4px;
      left: 4px;
      width: 22px;
      height: 22px;
      border-radius: 50%;
      background: white;
      box-shadow: 0 4px 12px rgba(24, 34, 27, 0.18);
      transition: transform 0.2s ease;
    }}

    .toggle input:checked + span {{ background: #2f6a45; }}
    .toggle input:checked + span::after {{ transform: translateX(24px); }}

    .legend {{
      display: grid;
      gap: 10px;
      margin-bottom: 14px;
    }}

    .stats-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 14px;
    }}

    .stat-card {{
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 12px;
      background: rgba(255,255,255,0.72);
    }}

    .stat-label {{
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 6px;
    }}

    .stat-value {{
      font-size: 22px;
      font-weight: 800;
      color: var(--text);
      line-height: 1;
    }}

    .stat-note {{
      margin-top: 6px;
      font-size: 12px;
      color: var(--muted);
    }}

    .legend-item,
    .summary-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      font-size: 13px;
    }}

    .legend-item-left,
    .summary-item-left {{
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
    }}

    .legend-item.is-button {{
      border: 1px solid rgba(47, 106, 69, 0.12);
      border-radius: 14px;
      padding: 10px 12px;
      background: rgba(255,255,255,0.72);
      cursor: pointer;
      transition: border-color 0.2s ease, transform 0.2s ease, opacity 0.2s ease, background 0.2s ease;
    }}

    .legend-item.is-button:hover {{
      transform: translateY(-1px);
      border-color: rgba(47, 106, 69, 0.28);
    }}

    .legend-item.is-button.is-active {{
      background: rgba(47, 106, 69, 0.1);
      border-color: rgba(47, 106, 69, 0.38);
    }}

    .legend-item.is-button.is-muted {{
      opacity: 0.45;
    }}

    .legend-toolbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 8px;
    }}

    .text-button {{
      border: 0;
      background: transparent;
      color: var(--accent);
      font: inherit;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      padding: 0;
    }}

    .text-button[hidden] {{
      display: none;
    }}

    .swatch {{
      width: 14px;
      height: 14px;
      border-radius: 4px;
      flex: 0 0 auto;
      border: 1px solid rgba(0, 0, 0, 0.08);
    }}

    .count-badge {{
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(35, 49, 39, 0.06);
      color: var(--text);
      font-weight: 700;
      font-size: 12px;
    }}

    .base-select {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: rgba(255,255,255,0.82);
      padding: 12px 14px;
      font: inherit;
      color: var(--text);
      outline: none;
    }}

    .leaflet-container {{
      background: #dbe3d8;
      font-family: "Manrope", sans-serif;
    }}

    .map-legend {{
      padding: 14px 14px 10px;
      border-radius: 16px;
      background: rgba(255, 251, 243, 0.92);
      border: 1px solid rgba(60, 85, 63, 0.14);
      box-shadow: 0 18px 42px rgba(64, 52, 34, 0.14);
      min-width: 230px;
    }}

    .map-legend h4 {{
      margin: 0 0 10px;
      font-size: 14px;
    }}

    .popup-grid {{
      display: grid;
      gap: 6px;
      min-width: 220px;
    }}

    @media (max-width: 1024px) {{
      body {{
        grid-template-columns: 1fr;
        grid-template-rows: auto 1fr;
      }}

      aside {{
        max-height: 52vh;
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }}

      #map {{
        height: 48vh;
      }}

      .theme-grid {{
        grid-template-columns: 1fr 1fr;
      }}
    }}

    @media (max-width: 640px) {{
      .theme-grid,
      .tab-row {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <aside>
    <div class="panel hero" id="donati-hero">
      <h1>Yaya Erişim Analizleri</h1>
      <p>
        Kocaeli genelinde farklı donatı türlerine yaya erişimini, tek bir hexagon harita arayüzünde birlikte
        okuyabilirsiniz. Analiz kapsamı dışında kalan alanlar, kentin bütününü hissettiren yarı saydam bir arka plan
        dokusu ile gösterilir.
      </p>
    </div>

    <div class="panel hero" id="wai-hero" hidden>
      <h1>Yaya Erişilebilirlik İndeks Puanları</h1>
      <p>
        Bu ekran, yaya ulaşım ağı, kentsel çevre kalitesi ve erişim göstergelerinin birlikte değerlendirilmesiyle
        üretilen WAI puanlarını hexagon bazında göstermektedir. Yüksek puanlar yaya erişilebilirliğinin daha güçlü
        olduğu alanları, düşük puanlar ise iyileştirme ihtiyacı bulunan alanları ortaya koymaktadır.
      </p>
    </div>

    <div class="panel">
      <div class="section-title">Görünüm Seçimi</div>
      <div class="mode-grid" id="view-buttons"></div>
    </div>

    <div class="panel" id="theme-selection-panel">
      <div class="section-title">Donatı Seçimi</div>
      <div class="theme-grid" id="theme-buttons"></div>
    </div>

    <div class="panel" id="donati-panel">
      <div class="theme-header">
        <div>
          <h2 class="theme-title" id="theme-title"></h2>
          <p class="theme-subtitle" id="theme-subtitle"></p>
        </div>
        <div class="pill">9 Donatı</div>
      </div>
      <p class="theme-copy" id="theme-description"></p>

      <div class="analysis-card">
        <h2 id="analysis-title"></h2>
        <div class="analysis-subtitle" id="analysis-subtitle"></div>
        <p id="analysis-description"></p>
        <div class="method-box" id="analysis-method"></div>

        <div class="control-row">
          <strong>Katmanı Göster</strong>
          <label class="toggle" aria-label="Katman görünürlüğünü değiştir">
            <input id="layer-toggle" type="checkbox" checked />
            <span></span>
          </label>
        </div>

        <div>
          <div class="section-title">Hızlı İstatistikler</div>
          <div class="stats-grid" id="stats-grid"></div>
        </div>

        <div>
          <div class="legend-toolbar">
            <div class="section-title">Lejant Filtresi</div>
            <button class="text-button" id="clear-filters" type="button" hidden>Filtreyi temizle</button>
          </div>
          <div class="legend" id="legend"></div>
        </div>

        <div>
          <div class="section-title">Dağılım</div>
          <div class="legend" id="summary"></div>
        </div>
      </div>
    </div>

    <div class="panel" id="wai-panel" hidden>
      <div class="theme-header">
        <div>
          <h2 class="theme-title">Yaya Erişilebilirlik İndeksi</h2>
          <p class="theme-subtitle">WAI Değerleri</p>
        </div>
        <div class="pill">5 Sınıf</div>
      </div>
      <p class="theme-copy">Hexagon bazında WAI değerleri 5 sınıfta gösterilmektedir. Analiz dışı alanlar ve il genelindeki dış hexagonlar içi boş sınır olarak bırakılmıştır.</p>

      <div class="analysis-card">
        <h2>WAI</h2>
        <div class="analysis-subtitle">Yaya erişilebilirlik indeks puanları</div>
        <div>
          <div class="section-title">Lejant</div>
          <div class="legend" id="wai-legend"></div>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="section-title">Altlık Harita</div>
      <select class="base-select" id="basemap-select">
        <option value="voyager" selected>Carto Voyager</option>
        <option value="osm">OpenStreetMap</option>
        <option value="cartoLight">Carto Light</option>
        <option value="cartoDark">Carto Dark Matter</option>
        <option value="positronNoLabels">Carto Positron No Labels</option>
        <option value="imagery">Esri World Imagery</option>
        <option value="topo">Esri World Topo</option>
        <option value="terrain">Stadia Stamen Terrain</option>
      </select>
    </div>
  </aside>

  <main id="map"></main>

  <script
    src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
    integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
    crossorigin=""
  ></script>
  <script>
    const hexData = {geojson_json};
    const boundaryData = {boundary_json};
    const waiData = {wai_json};
    const themeSummaries = {summary_json};
    const waiSummary = {wai_summary_json};
    const themeMeta = {meta_json};
    const valueStyle = {style_json};

    const map = L.map('map', {{
      zoomControl: false,
      preferCanvas: true,
      maxBoundsViscosity: 1.0
    }});

    L.control.zoom({{ position: 'bottomright' }}).addTo(map);

    const basemaps = {{
      voyager: L.tileLayer('https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}{{r}}.png', {{
        maxZoom: 20,
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
      }}),
      osm: L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
        maxZoom: 20,
        attribution: '&copy; OpenStreetMap contributors'
      }}),
      cartoLight: L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
        maxZoom: 20,
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
      }}),
      cartoDark: L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
        maxZoom: 20,
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
      }}),
      positronNoLabels: L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_nolabels/{{z}}/{{x}}/{{y}}{{r}}.png', {{
        maxZoom: 20,
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
      }}),
      imagery: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
        maxZoom: 20,
        attribution: 'Tiles &copy; Esri'
      }}),
      topo: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
        maxZoom: 20,
        attribution: 'Tiles &copy; Esri'
      }}),
      terrain: L.tileLayer('https://tiles.stadiamaps.com/tiles/stamen_terrain/{{z}}/{{x}}/{{y}}.png', {{
        maxZoom: 18,
        attribution: '&copy; Stadia Maps &copy; Stamen Design &copy; OpenMapTiles &copy; OpenStreetMap contributors'
      }})
    }};
    basemaps.voyager.addTo(map);

    const viewButtonsEl = document.getElementById('view-buttons');
    const donatiHeroEl = document.getElementById('donati-hero');
    const waiHeroEl = document.getElementById('wai-hero');
    const themeSelectionPanelEl = document.getElementById('theme-selection-panel');
    const donatiPanelEl = document.getElementById('donati-panel');
    const waiPanelEl = document.getElementById('wai-panel');
    const themeButtonsEl = document.getElementById('theme-buttons');
    const themeTitleEl = document.getElementById('theme-title');
    const themeSubtitleEl = document.getElementById('theme-subtitle');
    const themeDescriptionEl = document.getElementById('theme-description');
    const analysisTitleEl = document.getElementById('analysis-title');
    const analysisSubtitleEl = document.getElementById('analysis-subtitle');
    const analysisDescriptionEl = document.getElementById('analysis-description');
    const analysisMethodEl = document.getElementById('analysis-method');
    const legendEl = document.getElementById('legend');
    const summaryEl = document.getElementById('summary');
    const waiLegendEl = document.getElementById('wai-legend');
    const statsGridEl = document.getElementById('stats-grid');
    const toggleEl = document.getElementById('layer-toggle');
    const basemapEl = document.getElementById('basemap-select');
    const clearFiltersEl = document.getElementById('clear-filters');

    let activeView = 'donati';
    let activeTheme = 'saglik';
    let activeAnalysis = 'Analiz3';
    let currentLayer = null;
    let boundaryLayer = null;
    let activeLegendFilters = new Set();

    function getValue(value) {{
      return valueStyle[value] || {{ color: '#94a3b8', rank: 0 }};
    }}

    function getWaiClassStyle(label) {{
      return waiSummary.find(item => item.label === label) || {{ color: 'transparent', stroke: '#9ea6ad' }};
    }}

    function currentThemeConfig() {{
      return themeMeta[activeTheme];
    }}

    function currentAnalysisConfig() {{
      return currentThemeConfig().analyses[activeAnalysis];
    }}

    function getSummaryData() {{
      return themeSummaries[activeTheme][activeAnalysis];
    }}

    function isFeatureVisible(feature) {{
      if (activeView === 'wai') {{
        return true;
      }}
      if (activeLegendFilters.size === 0) {{
        return true;
      }}
      const themeData = feature.properties.themes[activeTheme];
      const value = themeData ? themeData[activeAnalysis] : null;
      return activeLegendFilters.has(value);
    }}

    function getVisibleFeatureCount() {{
      if (activeView === 'wai') {{
        return waiData.features.reduce((count, feature) => count + (feature.properties.wai > 0 ? 1 : 0), 0);
      }}
      if (activeLegendFilters.size === 0) {{
        return hexData.features.length;
      }}
      return hexData.features.reduce((count, feature) => count + (isFeatureVisible(feature) ? 1 : 0), 0);
    }}

    const legendControl = L.control({{ position: 'bottomleft' }});
    legendControl.onAdd = function () {{
      this._div = L.DomUtil.create('div', 'map-legend');
      return this._div;
    }};
    legendControl.addTo(map);

    function renderBoundaryLayer() {{
      if (boundaryLayer) {{
        map.removeLayer(boundaryLayer);
      }}

      if (!boundaryData.features.length) {{
        boundaryLayer = null;
        return;
      }}

      boundaryLayer = L.geoJSON(boundaryData, {{
        interactive: false,
        style: {{
          color: 'rgba(182, 188, 194, 0.88)',
          weight: 0.9,
          opacity: 0.9,
          fillColor: 'rgba(255, 255, 255, 0)',
          fillOpacity: 0
        }}
      }});

      boundaryLayer.addTo(map);
      boundaryLayer.bringToBack();
    }}

    function styleFeature(feature) {{
      if (activeView === 'wai') {{
        const waiValue = feature.properties.wai;
        const waiClass = feature.properties.wai_class;
        const style = getWaiClassStyle(waiClass);
        if (waiValue <= 0) {{
          return {{
            color: '#a9afb5',
            weight: 0.7,
            fillColor: 'rgba(255,255,255,0)',
            fillOpacity: 0
          }};
        }}
        return {{
          color: '#4a535a',
          weight: 0.65,
          fillColor: style.color,
          fillOpacity: 0.88
        }};
      }}
      const themeData = feature.properties.themes[activeTheme];
      const value = themeData ? themeData[activeAnalysis] : null;
      return {{
        color: '#ffffff',
        weight: 0.7,
        fillColor: getValue(value).color,
        fillOpacity: 0.62
      }};
    }}

    function onEachFeature(feature, layer) {{
      if (activeView === 'wai') {{
        if (feature.properties.wai <= 0) {{
          return;
        }}
        const html = `
          <div class="popup-grid">
            <div><strong>WAI:</strong> ${{feature.properties.wai.toFixed(2)}}</div>
          </div>
        `;
        layer.bindPopup(html);
        layer.on({{
          mouseover: () => layer.setStyle({{ weight: 1.5, fillOpacity: 1 }}),
          mouseout: () => currentLayer && currentLayer.resetStyle(layer)
        }});
        return;
      }}
      const themeCfg = currentThemeConfig();
      const props = feature.properties;
      const themeData = props.themes[activeTheme];
      const html = `
        <div class="popup-grid">
          <div><strong>Donatı:</strong> ${{themeCfg.title}}</div>
          <div><strong>Hex Kod:</strong> ${{props.hex_kod}}</div>
          <div><strong>Analiz:</strong> ${{themeData.Analiz3}}</div>
        </div>
      `;
      layer.bindPopup(html);
      layer.on({{
        mouseover: () => layer.setStyle({{ weight: 1.8, fillOpacity: 0.82 }}),
        mouseout: () => currentLayer && currentLayer.resetStyle(layer)
      }});
    }}

    function renderLayer() {{
      if (currentLayer) {{
        map.removeLayer(currentLayer);
      }}

      const sourceData = activeView === 'wai' ? waiData : hexData;
      currentLayer = L.geoJSON(sourceData, {{
        filter: isFeatureVisible,
        style: styleFeature,
        onEachFeature
      }});

      if (toggleEl.checked) {{
        currentLayer.addTo(map);
        currentLayer.bringToFront();
      }}
    }}

    function renderViewButtons() {{
      const views = [
        {{ id: 'donati', label: 'Donatı Erişimi' }},
        {{ id: 'wai', label: 'WAI' }}
      ];
      viewButtonsEl.innerHTML = views.map(view => `
        <button class="tab ${{activeView === view.id ? 'active' : ''}}" data-view="${{view.id}}">
          ${{view.label}}
        </button>
      `).join('');

      viewButtonsEl.querySelectorAll('[data-view]').forEach(button => {{
        button.addEventListener('click', () => {{
          activeView = button.dataset.view;
          activeLegendFilters = new Set();
          donatiHeroEl.hidden = activeView === 'wai';
          waiHeroEl.hidden = activeView !== 'wai';
          themeSelectionPanelEl.hidden = activeView === 'wai';
          donatiPanelEl.hidden = activeView === 'wai';
          waiPanelEl.hidden = activeView !== 'wai';
          renderViewButtons();
          if (activeView === 'donati') {{
            renderThemeButtons();
            renderDetails();
          }} else {{
            renderWaiLegend();
            renderMapLegend();
          }}
          renderBoundaryLayer();
          renderLayer();
        }});
      }});
    }}

    function renderThemeButtons() {{
      themeButtonsEl.innerHTML = Object.entries(themeMeta).map(([key, theme]) => `
        <button class="theme-button ${{key === activeTheme ? 'active' : ''}}" data-theme="${{key}}">
          ${{theme.menu}}
          <small>${{theme.subtitle}}</small>
        </button>
      `).join('');

      themeButtonsEl.querySelectorAll('.theme-button').forEach(button => {{
        button.addEventListener('click', () => {{
          activeTheme = button.dataset.theme;
          activeAnalysis = 'Analiz3';
          activeLegendFilters = new Set();
          renderThemeButtons();
          renderDetails();
          renderLayer();
        }});
      }});
    }}

    function renderLegend() {{
      if (activeView === 'wai') {{
        return;
      }}
      const summaryData = getSummaryData();
      const hasFilters = activeLegendFilters.size > 0;
      clearFiltersEl.hidden = !hasFilters;

      legendEl.innerHTML = summaryData.map(item => `
        <button class="legend-item is-button ${{activeLegendFilters.size === 0 || activeLegendFilters.has(item.label) ? 'is-active' : 'is-muted'}}" data-legend-value="${{item.label}}" type="button">
          <div class="legend-item-left">
            <span class="swatch" style="background:${{item.color}}"></span>
            <span>${{item.label}}</span>
          </div>
        </button>
      `).join('');

      legendEl.querySelectorAll('[data-legend-value]').forEach(button => {{
        button.addEventListener('click', () => {{
          const value = button.dataset.legendValue;
          if (activeLegendFilters.has(value)) {{
            activeLegendFilters.delete(value);
          }} else {{
            activeLegendFilters.add(value);
          }}

          if (activeLegendFilters.size === getSummaryData().length) {{
            activeLegendFilters = new Set();
          }}

          renderLegend();
          renderStats();
          renderLayer();
          renderMapLegend();
        }});
      }});

      summaryEl.innerHTML = summaryData.map(item => `
        <div class="summary-item">
          <div class="summary-item-left">
            <span class="swatch" style="background:${{item.color}}"></span>
            <span>${{item.label}}</span>
          </div>
          <span class="count-badge">${{item.count}}</span>
        </div>
      `).join('');
    }}

    function renderStats() {{
      if (activeView === 'wai') {{
        return;
      }}
      const summaryData = getSummaryData();
      const totalHex = hexData.features.length;
      const visibleHex = getVisibleFeatureCount();
      const topClass = summaryData[0];
      const noAccessItem = summaryData.find(item => item.label === 'Yaya erişimi yok');
      const noAccessCount = noAccessItem ? noAccessItem.count : 0;
      const noAccessRate = totalHex ? Math.round((noAccessCount / totalHex) * 100) : 0;

      statsGridEl.innerHTML = `
        <div class="stat-card">
          <div class="stat-label">Toplam Hex</div>
          <div class="stat-value">${{totalHex}}</div>
          <div class="stat-note">Aktif donatı kapsamı</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Görünen Hex</div>
          <div class="stat-value">${{visibleHex}}</div>
          <div class="stat-note">${{activeLegendFilters.size === 0 ? 'Lejant filtresi uygulanmadı' : 'Seçilen sınıflara göre filtrelendi'}}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Baskın Sınıf</div>
          <div class="stat-value" style="font-size:18px;">${{topClass ? topClass.label : '-'}}</div>
          <div class="stat-note">${{topClass ? `${{topClass.count}} hex` : 'Veri yok'}}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Erişim Yok</div>
          <div class="stat-value">${{noAccessRate}}%</div>
          <div class="stat-note">${{noAccessCount}} hex kırmızı sınıfta</div>
        </div>
      `;
    }}

    function renderWaiLegend() {{
      waiLegendEl.innerHTML = waiSummary.map(item => `
        <div class="legend-item">
          <div class="legend-item-left">
            <span class="swatch" style="background:${{item.color}}; border-color:${{item.stroke}};"></span>
            <span>${{item.label}}</span>
          </div>
          <span class="count-badge">${{item.count}}</span>
        </div>
      `).join('');
    }}

    function renderMapLegend() {{
      if (activeView === 'wai') {{
        legendControl._div.innerHTML = `
          <h4>WAI Lejantı</h4>
          ${{waiSummary.map(item => `
            <div class="legend-item">
              <div class="legend-item-left">
                <span class="swatch" style="background:${{item.color}}; border-color:${{item.stroke}};"></span>
                <span>${{item.label}}</span>
              </div>
            </div>
          `).join('')}}
        `;
        return;
      }}
      const analysis = currentAnalysisConfig();
      const summaryData = getSummaryData().filter(item => activeLegendFilters.size === 0 || activeLegendFilters.has(item.label));
      legendControl._div.innerHTML = `
        <h4>${{currentThemeConfig().title}} / ${{analysis.title}}</h4>
        ${{summaryData.map(item => `
          <div class="legend-item">
            <div class="legend-item-left">
              <span class="swatch" style="background:${{item.color}}"></span>
              <span>${{item.label}}</span>
            </div>
          </div>
        `).join('')}}
      `;
    }}

    function renderDetails() {{
      const theme = currentThemeConfig();
      const analysis = currentAnalysisConfig();
      themeTitleEl.textContent = theme.title;
      themeSubtitleEl.textContent = theme.subtitle;
      themeDescriptionEl.textContent = theme.description;
      analysisTitleEl.textContent = analysis.title;
      analysisSubtitleEl.textContent = analysis.subtitle;
      analysisDescriptionEl.textContent = analysis.description;
      analysisMethodEl.textContent = analysis.method;
      renderLegend();
      renderStats();
      renderMapLegend();
    }}

    clearFiltersEl.addEventListener('click', () => {{
      activeLegendFilters = new Set();
      renderLegend();
      renderStats();
      renderLayer();
      renderMapLegend();
    }});

    toggleEl.addEventListener('change', () => {{
      if (!currentLayer) return;
      if (toggleEl.checked) {{
        currentLayer.addTo(map);
        currentLayer.bringToFront();
      }} else {{
        map.removeLayer(currentLayer);
      }}
    }});

    basemapEl.addEventListener('change', () => {{
      Object.values(basemaps).forEach(layer => map.removeLayer(layer));
      basemaps[basemapEl.value].addTo(map);
    }});

    renderViewButtons();
    donatiHeroEl.hidden = activeView === 'wai';
    waiHeroEl.hidden = activeView !== 'wai';
    renderThemeButtons();
    renderDetails();
    renderWaiLegend();
    renderBoundaryLayer();
    renderLayer();

    const bounds = L.featureGroup([...(boundaryLayer ? [boundaryLayer] : []), currentLayer]).getBounds();
    if (bounds.isValid()) {{
      map.fitBounds(bounds.pad(0.04));
      map.setMaxBounds(bounds.pad(0.02));
      map.setMinZoom(map.getZoom());
    }} else {{
      map.setView([39.0, 35.0], 6);
    }}
  </script>
</body>
</html>
"""


def main() -> None:
    geojson, theme_summaries = load_theme_data()
    boundary_geojson = load_boundary_data()
    wai_geojson, wai_summary = load_wai_data(len(boundary_geojson.get("features", [])))
    theme_meta = build_theme_meta()
    OUTPUT_HTML.write_text(render_html(geojson, boundary_geojson, wai_geojson, theme_summaries, wai_summary, theme_meta), encoding="utf-8")
    print(f"Wrote {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
