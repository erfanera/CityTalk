from BaseAgent import BaseAgent
import os
import pandas as pd
import requests
import geopandas as gpd
import osmnx as ox

class DataCollectorAgent(BaseAgent):
    def __init__(self, api_key, data_dir="./CSV"):
        super().__init__(api_key)
        self.data_dir = data_dir

    def _determine_osm_tags(self, dataset_name):
        """Determine the appropriate OSM tags based on the dataset name."""
        name_lower = dataset_name.lower()
        
        # Common OSM tag mappings
        tag_mappings = {
            'park': {'leisure': 'park'},
            'restaurant': {'amenity': 'restaurant'},
            'cafe': {'amenity': 'cafe'},
            'school': {'amenity': 'school'},
            'hospital': {'amenity': 'hospital'},
            'parking': {'amenity': 'parking'},
            'pharmacy': {'amenity': 'pharmacy'},
            'bank': {'amenity': 'bank'},
            'bar': {'amenity': 'bar'},
            'library': {'amenity': 'library'},
            'cinema': {'amenity': 'cinema'},
            'theatre': {'amenity': 'theatre'},
            'police': {'amenity': 'police'},
            'post_office': {'amenity': 'post_office'},
            'fuel': {'amenity': 'fuel'},
            'bicycle_parking': {'amenity': 'bicycle_parking'},
            'bicycle_rental': {'amenity': 'bicycle_rental'},
            'drinking_water': {'amenity': 'drinking_water'},
            'bench': {'amenity': 'bench'},
            'waste_basket': {'amenity': 'waste_basket'},
            'marketplace': {'amenity': 'marketplace'},
            'university': {'amenity': 'university'},
            'college': {'amenity': 'college'},
            'kindergarten': {'amenity': 'kindergarten'},
            'bus_station': {'amenity': 'bus_station'},
            'car_rental': {'amenity': 'car_rental'},
            'fountain': {'amenity': 'fountain'},
            'nightclub': {'amenity': 'nightclub'},
            'gym': {'leisure': 'fitness_centre'},
            'garden': {'leisure': 'garden'},
            'supermarket': {'shop': 'supermarket'},
            'grocery': {'shop': 'supermarket'},
            'shop': {'shop': True},  # Generic shop tag
            'store': {'shop': True},
            'residential': {'building': 'residential'},
            'house': {'building': 'house'},
            'apartment': {'building': 'apartments'},
            'building': {'building': True},  # Generic building tag
            'home': {'building': 'residential'},
            'hotel': {'tourism': 'hotel'},
            'attraction': {'tourism': 'attraction'},
            'office': {'office': True},
            'commercial': {'landuse': 'commercial'},
            'industrial': {'landuse': 'industrial'},
            'retail': {'landuse': 'retail'},
            'atm': {'amenity': 'atm'},
            'clinic': {'amenity': 'clinic'},
            'dentist': {'amenity': 'dentist'},
            'veterinary': {'amenity': 'veterinary'},
            'fast_food': {'amenity': 'fast_food'},
            'pub': {'amenity': 'pub'},
            'taxi': {'amenity': 'taxi'},
            'bus_stop': {'highway': 'bus_stop'},
            'subway': {'railway': 'subway_entrance'},
            'train': {'railway': 'station'},
        }

        # Try to find exact match first
        for key, tags in tag_mappings.items():
            if key in name_lower:
                return tags

        # If no exact match found, try to determine from the name
        if 'location' in name_lower:
            name_parts = name_lower.replace('locations', '').replace('location', '').strip().split()
            for part in name_parts:
                if part in tag_mappings:
                    return tag_mappings[part]

        # Default to a generic amenity tag if no specific match found
        print(f"⚠️ No specific OSM tags found for {dataset_name}. Using generic amenity tag.")
        return {'amenity': name_lower.split()[0]}

    def fetch_data(self, datasets: list, coordinates: dict):
        all_data = {}  # Changed from list to dictionary
        csv_dirs = {}  # Tag → CSV file path
        seen_tags = set()  # Avoid duplicate loads

        for dataset in datasets:
            name = dataset["name"]
            source = dataset["source"]
            tag = dataset.get("tag", name.lower().replace(" ", "_"))

            location = dataset.get("location")
            if not location and coordinates:
                first_place = next(iter(coordinates.values()))
                location = {
                    "latitude": float(first_place["lat"]),
                    "longitude": float(first_place["lon"])
                }
            elif not location:
                location = {"latitude": 41.3851, "longitude": 2.1734}

            radius_km = dataset.get("radius_km", 2.0)
           
            if source == "osm":
                data = self._fetch_osm_data(name, location, radius_km)
                if not data.empty:
                    all_data[name] = data  # Store with dataset name as key
            else:
                if tag not in seen_tags:
                    data, file_path = self._fetch_local_csv(tag)
                    seen_tags.add(tag)
                    if file_path:
                        csv_dirs[tag] = file_path
                        if not data.empty:
                            all_data[tag] = data  # Store with tag as key
                else:
                    data = pd.DataFrame()  # Skip re-fetch

        return all_data, csv_dirs

    def _fetch_osm_data(self, dataset_name, location, radius_km):
        print(f"📍 Fetching OSM data for: {dataset_name} at {location}")
        tags = self._determine_osm_tags(dataset_name)
        if not tags:
            print("⚠️ Unknown dataset for OSM. Returning empty GeoDataFrame.")
            return gpd.GeoDataFrame()

        center_point = (location["latitude"], location["longitude"])
        try:
            gdf = ox.features_from_point(center_point, tags=tags, dist=radius_km * 1000)
            print(f"✅ Fetched {len(gdf)} features from OSM.")
            return gdf
        except Exception as e:
            print(f"❌ Error fetching OSM data: {e}")
            return gpd.GeoDataFrame()

    def _fetch_local_csv(self, dataset_name):
        print(f"🔍 Searching for CSV file for: {dataset_name}")

        dataset_key = dataset_name.lower().strip().replace(" ", "_")

        # Flexible mapping
        alias_map = {
            "air_pollution_levels": [
                "air pollution", "co2", "carbon footprint", "emission", "pollution", "air quality"
            ],
            "bicingstations": [
                "bicing", "bike sharing", "bike stations", "bicing station", "bicycle rental"
            ]
        }

        # Alias resolution
        resolved_filename = None
        for filename, aliases in alias_map.items():
            if any(alias in dataset_key for alias in aliases):
                resolved_filename = filename + ".csv"
                break

        # Fallback partial filename match
        if not resolved_filename:
            for file in os.listdir(self.data_dir):
                if file.lower().endswith(".csv") and dataset_key in file.lower():
                    resolved_filename = file
                    break

        # Final check
        if resolved_filename:
            file_path = os.path.join(self.data_dir, resolved_filename)
            if os.path.exists(file_path):
                print(f"📄 Found CSV: {file_path}")
                return pd.read_csv(file_path), file_path

        print("⚠️ No matching CSV found.")
        return pd.DataFrame(), None
