import os
import pandas as pd
from keplergl import KeplerGl
import uuid


def generate_map_config(dataset_keys):
    """Dynamically generate a map config with up to 4 transparent heatmaps."""
    base_config = {
        "version": "v1",
        "config": {
            "mapState": {
                "latitude": 41.3851,
                "longitude": 2.1734,
                "zoom": 12,
                "pitch": 0,
                "bearing": 0
            },
            "visState": {
                "layers": [],
                "interactionConfig": {
                    "tooltip": {
                        "enabled": True,
                        "fieldsToShow": {key: ["latitude", "longitude"] for key in dataset_keys}
                    },
                    "brush": {"size": 1.5, "enabled": False},
                    "coordinate": {"enabled": True},
                    "featureClick": {"enabled": True}
                }
            },
            "mapStyle": {
                "styleType": "positron-nolabels",
                "visibleLayerGroups": {
                    "label": True, "road": True, "land": True, "water": True
                }
            }
        }
    }

    for idx, key in enumerate(dataset_keys[:4]):
        layer = {
            "id": f"heatmap_{idx}",
            "type": "heatmap",
            "config": {
                "dataId": key,
                "label": f"Heatmap {key}",
                "color": [255, 0, 0],
                "columns": {"lat": "latitude", "lng": "longitude"},
                "isVisible": True,
                "visConfig": {
                    "opacity": 0.4,
                    "colorRange": {
                        "colors": [
                            "#00A8CC", "#70D6FF", "#FF70A6", "#FF9770",
                            "#FFD670", "#E9FF70"
                        ]
                    },
                }
            }
        }
        base_config["config"]["visState"]["layers"].append(layer)

    return base_config


def save_kepler_map(data_dict, output_dir="./maps", filename=None):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not filename:
        filename = f"viz_{uuid.uuid4().hex[:6]}.html"

    output_map_path = os.path.join(output_dir, filename)
    map_config = generate_map_config(list(data_dict.keys()))

    kepler_map = KeplerGl(height=969, width=1920, data=data_dict, config=map_config)
    kepler_map.save_to_html(file_name=output_map_path)

    return output_map_path, filename


def display_html_with_custom_style(map_html_path):
    with open(map_html_path, "r", encoding="utf-8") as f:
        map_html = f.read()

    wrapped_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body, html {{
                margin: 0; padding: 0;
                width: 100vw; height: 100vh;
                overflow: hidden;
                font-family: 'Bahnschrift', sans-serif;
            }}
            .kepler-gl {{
                width: 100%; height: 100%;
            }}
        </style>
    </head>
    <body>
        {map_html}
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                setTimeout(function() {{
                    const el = document.querySelector('.kepler-gl');
                    if (el) {{
                        el.style.width = '100%';
                        el.style.height = '100vh';
                    }}
                    window.dispatchEvent(new Event('resize'));
                }}, 100);
            }});
        </script>
    </body>
    </html>
    """

    with open(map_html_path, "w", encoding="utf-8") as f:
        f.write(wrapped_html)

    return map_html_path


# This block simulates what the Viz01 agent would call
# Example usage:
# all_data = {'parks': gdf1, 'schools': gdf2, 'pollution': df3}
# html_path, file_name = save_kepler_map(all_data)
# display_html_with_custom_style(html_path)
