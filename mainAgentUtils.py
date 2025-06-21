# === functions.py ===

import pandas as pd
import geopandas as gpd
import numpy as np
import os
import re
from shapely.geometry import Point
from shapely import wkt


def filter_by_distance(gdf, center_point, max_distance_km=2.0):
    gdf_proj = gdf.to_crs('EPSG:3857')
    center_proj = gpd.GeoSeries([center_point], crs='EPSG:4326').to_crs('EPSG:3857').iloc[0]
    distances = gdf_proj.geometry.distance(center_proj)
    nearby_mask = distances <= (max_distance_km * 1000)
    return gdf[nearby_mask].copy()


def prepare_dataset_summary(enriched_datasets):
    summary = []
    for dataset_name, (dataset, analysis) in enriched_datasets.items():
        columns = list(dataset.columns)
        row_count = len(dataset)
        has_geometry = 'geometry' in columns
        dataset_summary = f"""
Dataset: {dataset_name}
- Rows: {row_count}
- Columns: {columns}
- Has spatial data: {has_geometry}
- Analysis: {analysis[:200]}...
"""
        summary.append(dataset_summary)
    return "\n".join(summary)


def get_dataset_variable_names(enriched_datasets):
    dataset_variables = {}
    for dataset_name, (dataset, _) in enriched_datasets.items():
        var_name = dataset_name.lower().replace(" ", "").replace("-", "")
        dataset_variables[var_name] = dataset
    return dataset_variables


def clean_generated_code(code):
    match = re.search(r"```python\n(.*?)```", code, re.DOTALL)
    if match:
        code = match.group(1)

    code = code.strip().encode('ascii', 'ignore').decode('ascii')
    lines = code.split('\n')
    cleaned_lines = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            cleaned_lines.append(line)
            continue

        for pattern, replacement in [
            (' = = ', ' == '),
            ('= =', '=='),
            (' ! = ', ' != '),
            ('! =', '!='),
            ('< = ', '<='),
            ('> = ', '>='),
            (' < = ', ' <= '),
            (' > = ', ' >= ')
        ]:
            line = line.replace(pattern, replacement)

        if '"' not in line and "'" not in line:
            line = re.sub(r'(?<![<>=!])<(?![=])', ' < ', line)
            line = re.sub(r'(?<![<>=!])>(?![=])', ' > ', line)
            line = re.sub(r'(?<![<>=!])=(?![=])', ' = ', line)
            line = re.sub(r'\s+', ' ', line)

        line = line.replace('.distance(', '.geometry.distance(')
        line = line.replace('.geometry.geometry.distance(', '.geometry.distance(')
        cleaned_lines.append(line)

    indent_level = 0
    formatted_lines = []
    for i, line in enumerate(cleaned_lines):
        if not line.strip():
            formatted_lines.append('')
            continue

        stripped = line.strip()
        if stripped.startswith(('except', 'elif', 'else', 'finally')):
            indent_level = max(0, indent_level - 1)
            formatted_lines.append('    ' * indent_level + stripped)
            if stripped.endswith(':'):
                indent_level += 1
            continue

        formatted_lines.append('    ' * indent_level + stripped)
        if stripped.endswith(':'):
            indent_level += 1
        elif stripped.startswith(('return', 'break', 'continue', 'pass', 'raise')):
            if (i + 1 < len(cleaned_lines)
                    and cleaned_lines[i + 1].strip()
                    and not cleaned_lines[i + 1].strip().startswith(('except', 'elif', 'else', 'finally', '#'))):
                indent_level = max(0, indent_level - 1)

    code = '\n'.join(formatted_lines)

    imports = [
        "import pandas as pd",
        "import geopandas as gpd",
        "import numpy as np",
        "from shapely.geometry import Point",
        "from shapely import wkt"
    ]
    for imp in imports:
        if imp not in code:
            code = imp + '\n' + code
    return code
