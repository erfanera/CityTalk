from DataCollect03 import DataCollectorAgent
import pandas as pd
import geopandas as gpd
from shapely import wkt
from shapely.geometry import Point
import numpy as np

# Initialize and fetch the datasets
collector = DataCollectorAgent('dummy_key')

datasets = [
    {"name": "Residential Building Locations", "source": "osm", "location": {"latitude": 41.3809, "longitude": 2.191}},
    {"name": "emission_zones", "source": "csv", "tag": "air_pollution_levels"}
]

coordinates = {
    "Barceloneta": {"lat": 41.3809, "lon": 2.191}
}

print("📊 Fetching datasets for final corrected analysis...")
datasets_info, _ = collector.fetch_data(datasets, coordinates)

# Make datasets available as variables
residential_building_locations = datasets_info['Residential Building Locations']
air_pollution_levels = datasets_info['air_pollution_levels']

print(f"✅ Loaded {len(residential_building_locations)} residential buildings")
print(f"✅ Loaded {len(air_pollution_levels)} emission records")

print("\n" + "="*60)
print("🚀 FINAL CORRECTED ANALYSIS - PROXIMITY-BASED")
print("="*60)

# Define Barceloneta center point
barceloneta_center = Point(2.191, 41.3809)

# Function to filter by distance
def filter_by_distance(gdf, center_point, max_distance_km=2.0):
    """Filter GeoDataFrame by distance from center point"""
    print(f"Filtering {len(gdf)} features within {max_distance_km}km of {center_point}")
    
    gdf_proj = gdf.to_crs('EPSG:3857')
    center_proj = gpd.GeoSeries([center_point], crs='EPSG:4326').to_crs('EPSG:3857').iloc[0]
    distances = gdf_proj.geometry.distance(center_proj)
    nearby_mask = distances <= (max_distance_km * 1000)
    nearby_gdf = gdf[nearby_mask].copy()
    
    print(f"Found {len(nearby_gdf)} features within distance")
    return nearby_gdf

# Process emission zones data
print("🔧 Processing emission zones data...")
if 'geometry_wkt' in air_pollution_levels.columns:
    air_pollution_levels['geometry'] = air_pollution_levels['geometry_wkt'].apply(wkt.loads)
    emission_zones = gpd.GeoDataFrame(air_pollution_levels, geometry='geometry', crs='EPSG:4326')
    print(f"✅ Converted {len(emission_zones)} emission records to GeoDataFrame")
    
    # Filter emission zones for Barceloneta
    barceloneta_emission_zones = filter_by_distance(emission_zones, barceloneta_center)
    print(f"🎯 Found {len(barceloneta_emission_zones)} emission zones near Barceloneta")
    
    # Process residential buildings
    print("\n🏠 Processing residential buildings...")
    residential_building_locations = residential_building_locations.to_crs('EPSG:4326')
    nearby_residential = filter_by_distance(residential_building_locations, barceloneta_center)
    print(f"🏘️ Found {len(nearby_residential)} residential buildings near Barceloneta")
    
    if len(nearby_residential) > 0 and len(barceloneta_emission_zones) > 0:
        print("\n🔗 Finding nearest emission zone for each building...")
        
        # Extract coordinates for buildings (use projected CRS for coordinates)
        nearby_residential_proj = nearby_residential.to_crs('EPSG:4326')
        nearby_residential_proj['longitude'] = nearby_residential_proj.geometry.centroid.x
        nearby_residential_proj['latitude'] = nearby_residential_proj.geometry.centroid.y
        
        # Function to find nearest emission zone for each building
        def find_nearest_emission(building_row, emission_gdf):
            """Find the nearest emission zone for a building"""
            building_point = Point(building_row['longitude'], building_row['latitude'])
            
            # Calculate distances to all emission zones
            building_proj = gpd.GeoSeries([building_point], crs='EPSG:4326').to_crs('EPSG:3857').iloc[0]
            emission_proj = emission_gdf.to_crs('EPSG:3857')
            
            distances = emission_proj.geometry.distance(building_proj)
            nearest_idx = distances.idxmin()
            nearest_distance = distances.loc[nearest_idx] / 1000  # Convert to km
            
            return {
                'nearest_emission_id': emission_gdf.loc[nearest_idx, 'TRAM'],
                'emission_level': emission_gdf.loc[nearest_idx, 'Rang'],
                'distance_to_emission_km': nearest_distance
            }
        
        # Apply to each building
        print("🔍 Calculating nearest emission zones...")
        emission_info = nearby_residential_proj.apply(
            lambda row: find_nearest_emission(row, barceloneta_emission_zones), 
            axis=1
        )
        
        # Create results DataFrame
        results_list = []
        for idx, building in nearby_residential_proj.iterrows():
            info = emission_info.loc[idx]
            
            # Create descriptive name
            building_type = building.get('building', 'Unknown')
            emission_level = info['emission_level']
            distance = info['distance_to_emission_km']
            
            name = f"Residential Building (Type: {building_type}, Emission: {emission_level}, {distance:.1f}km away)"
            
            results_list.append({
                'name': name,
                'longitude': building['longitude'],
                'latitude': building['latitude']
            })
        
        # Create final results DataFrame
        result = pd.DataFrame(results_list)
        
        print(f"📋 Created {len(result)} results with emission information")
        if len(result) > 0:
            print("Sample results:")
            print(result.head())
            
            # Show emission level distribution
            emission_levels = [info['emission_level'] for info in emission_info]
            unique_levels = list(set(emission_levels))
            print(f"\nEmission levels found: {unique_levels}")
        
    else:
        print("❌ No data found for analysis")
        result = pd.DataFrame(columns=['name', 'longitude', 'latitude'])
        
    # Export results
    result.to_csv('results.csv', index=False)
    print(f"✅ Exported {len(result)} results to 'results.csv'")

else:
    print("❌ Error: No geometry_wkt column found in emission data")
    result = pd.DataFrame(columns=['name', 'longitude', 'latitude'])
    result.to_csv('results.csv', index=False)

# Final verification
try:
    final_results = pd.read_csv('results.csv')
    print(f"\n🎉 FINAL SUCCESS! Generated {len(final_results)} meaningful results")
    if len(final_results) > 0:
        print("\n📋 Summary of results:")
        print(final_results.head(10))
        print(f"\nTotal residential buildings in Barceloneta with emission data: {len(final_results)}")
    else:
        print("⚠️ No results generated")
except Exception as e:
    print(f"❌ Error reading final results: {e}") 