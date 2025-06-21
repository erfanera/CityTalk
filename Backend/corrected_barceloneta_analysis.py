import numpy as np
import numpy as np
import geopandas as gpd
import pandas as pd
from shapely import wkt
from shapely.geometry import Point

# Define Barceloneta center point for proximity analysis
barceloneta_center = Point(2.191, 41.3809)

# Function to filter by distance (SPATIAL APPROACH - NOT STRING MATCHING)
def filter_by_distance(gdf, center_point, max_distance_km=2.0):
    """Filter GeoDataFrame by distance from center point"""
    print(f"Filtering {len(gdf)} features within {max_distance_km}km of {center_point}")
    
    # Convert to projected CRS for accurate distance calculation
    gdf_proj = gdf.to_crs('EPSG:3857')
    center_proj = gpd.GeoSeries([center_point], crs='EPSG:4326').to_crs('EPSG:3857').iloc[0]
    
    # Calculate distances in meters
    distances = gdf_proj.geometry.distance(center_proj)
    
    # Filter by distance
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
    
    # Filter emission zones for Barceloneta using SPATIAL PROXIMITY (not TRAM field)
    barceloneta_emission_zones = filter_by_distance(emission_zones, barceloneta_center)
    print(f"🎯 Found {len(barceloneta_emission_zones)} emission zones near Barceloneta")
    
    # Process residential building locations
    print("\n🏠 Processing residential buildings...")
    residential_building_locations = residential_building_locations.to_crs('EPSG:4326')
    
    # Filter residential buildings near Barceloneta
    nearby_residential = filter_by_distance(residential_building_locations, barceloneta_center)
    print(f"🏘️ Found {len(nearby_residential)} residential buildings near Barceloneta")
    
    # Now do spatial join to find residential buildings within emission zones
    print("\n🔗 Performing spatial join...")
    
    # Ensure both datasets have geometry
    if len(nearby_residential) > 0 and len(barceloneta_emission_zones) > 0:
        # Spatial join - find residential buildings that intersect with emission zones
        residential_in_emission_zones = gpd.sjoin(
            nearby_residential, 
            barceloneta_emission_zones, 
            how='inner', 
            predicate='intersects'
        )
        
        print(f"🎯 Found {len(residential_in_emission_zones)} residential buildings in emission zones")
        
        # Extract coordinates
        residential_in_emission_zones['longitude'] = residential_in_emission_zones.geometry.centroid.x
        residential_in_emission_zones['latitude'] = residential_in_emission_zones.geometry.centroid.y
        
        # Add emission level information
        residential_in_emission_zones['emission_level'] = residential_in_emission_zones['Rang']
        
        # Create meaningful names for buildings
        residential_in_emission_zones['name'] = residential_in_emission_zones.apply(
            lambda row: f"Residential Building ({row.get('building', 'Unknown')} - {row['Rang']})" 
            if pd.notna(row.get('building')) 
            else f"Building near Barceloneta ({row['Rang']})", 
            axis=1
        )
        
        # Prepare final output
        result = residential_in_emission_zones[['name', 'longitude', 'latitude']].copy()
        
        print(f"📋 Preparing {len(result)} results for export")
        print(f"Sample results:")
        print(result.head())
        
    else:
        print("❌ No overlapping data found - creating empty result")
        result = pd.DataFrame(columns=['name', 'longitude', 'latitude'])
        
    # Export results to CSV
    result.to_csv('results.csv', index=False)
    print(f"✅ Exported {len(result)} results to 'results.csv'")

else:
    print("❌ Error: No geometry_wkt column found in emission data")
    result = pd.DataFrame(columns=['name', 'longitude', 'latitude'])
    result.to_csv('results.csv', index=False) 