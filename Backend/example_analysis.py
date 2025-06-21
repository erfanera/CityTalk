"""
COMPREHENSIVE DATA ANALYSIS EXAMPLE
Shows proper handling of different geometry types and spatial operations
"""

from DataCollect03 import DataCollectorAgent
from DataReader import DataReaderAgent
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely import wkt
import numpy as np

def analyze_data_properly():
    """Example of proper data analysis handling different geometry types"""
    
    # Initialize and fetch data
    collector = DataCollectorAgent('dummy_key')
    datasets = [
        {"name": "Park Locations", "source": "osm", "location": {"latitude": 41.4005, "longitude": 2.2017}},
        {"name": "School Locations", "source": "osm", "location": {"latitude": 41.4005, "longitude": 2.2017}},
        {"name": "pollution", "source": "csv", "tag": "air_pollution_levels"}
    ]
    coordinates = {"El Poblenou": {"lat": 41.4005, "lon": 2.2017}}
    
    datasets_info, _ = collector.fetch_data(datasets, coordinates)
    
    print("="*60)
    print("PROPER SPATIAL ANALYSIS EXAMPLE")
    print("="*60)
    
    # Extract datasets
    park_locations = datasets_info.get('Park Locations')
    school_locations = datasets_info.get('School Locations') 
    pollution = datasets_info.get('air_pollution_levels')
    
    if park_locations is None or school_locations is None or pollution is None:
        print("❌ Missing datasets!")
        return
    
    print(f"📊 Data Summary:")
    print(f"  Parks: {len(park_locations)} features ({park_locations.geometry.geom_type.unique()})")
    print(f"  Schools: {len(school_locations)} features ({school_locations.geometry.geom_type.unique()})")
    print(f"  Pollution: {len(pollution)} records")
    
    # 1. PROPER CRS HANDLING
    print(f"\n🗺️  CRS Handling:")
    park_locations = park_locations.to_crs('EPSG:4326')  # Ensure WGS84
    school_locations = school_locations.to_crs('EPSG:4326')
    print(f"  Standardized to EPSG:4326 (WGS84)")
    
    # 2. PROPER COORDINATE EXTRACTION
    print(f"\n📍 Coordinate Extraction:")
    # Use centroid for all geometry types (Points, Polygons, MultiPolygons)
    park_locations['longitude'] = park_locations.geometry.centroid.x
    park_locations['latitude'] = park_locations.geometry.centroid.y
    
    school_locations['longitude'] = school_locations.geometry.centroid.x
    school_locations['latitude'] = school_locations.geometry.centroid.y
    
    print(f"  ✅ Extracted coordinates using .centroid.x/.centroid.y")
    
    # 3. HANDLE POLLUTION DATA PROPERLY
    print(f"\n💨 Processing Pollution Data:")
    try:
        # Convert WKT to geometry
        pollution['geometry'] = pollution['geometry_wkt'].apply(wkt.loads)
        pollution_gdf = gpd.GeoDataFrame(pollution, geometry='geometry', crs='EPSG:4326')
        
        # Get centroid of line segments for point-based analysis
        pollution_gdf['longitude'] = pollution_gdf.geometry.centroid.x
        pollution_gdf['latitude'] = pollution_gdf.geometry.centroid.y
        
        print(f"  ✅ Processed {len(pollution_gdf)} pollution measurements")
        print(f"  Geometry types: {pollution_gdf.geometry.geom_type.unique()}")
        
    except Exception as e:
        print(f"  ❌ Error processing pollution data: {e}")
        return
    
    # 4. DISTANCE-BASED PROXIMITY ANALYSIS (NOT SPATIAL JOIN)
    print(f"\n📏 Distance-based Proximity Analysis:")
    
    # Define El Poblenou center point
    el_poblenou_center = Point(2.2017, 41.4005)
    
    # Filter locations within El Poblenou area (2km radius)
    def filter_by_distance(gdf, center_point, max_distance_km=2.0):
        # Convert to projected CRS for accurate distance calculation
        gdf_proj = gdf.to_crs('EPSG:3857')  # Web Mercator (meters)
        center_proj = gpd.GeoSeries([center_point], crs='EPSG:4326').to_crs('EPSG:3857').iloc[0]
        
        # Calculate distances in meters
        distances = gdf_proj.geometry.distance(center_proj)
        
        # Filter by distance
        nearby_mask = distances <= (max_distance_km * 1000)
        nearby_gdf = gdf[nearby_mask].copy()
        nearby_gdf['distance_km'] = distances[nearby_mask] / 1000
        
        return nearby_gdf
    
    # Filter parks and schools in El Poblenou area
    nearby_parks = filter_by_distance(park_locations, el_poblenou_center)
    nearby_schools = filter_by_distance(school_locations, el_poblenou_center)
    
    print(f"  🏞️  Parks in El Poblenou area: {len(nearby_parks)}")
    print(f"  🏫 Schools in El Poblenou area: {len(nearby_schools)}")
    
    # 5. COMBINE DATASETS PROPERLY
    print(f"\n🔗 Combining Datasets:")
    
    # Prepare park data
    parks_df = nearby_parks[['name', 'longitude', 'latitude', 'distance_km']].copy()
    parks_df['type'] = 'Park'
    
    # Prepare school data
    schools_df = nearby_schools[['name', 'longitude', 'latitude', 'distance_km']].copy()
    schools_df['type'] = 'School'
    
    # Combine
    combined_locations = pd.concat([parks_df, schools_df], ignore_index=True)
    print(f"  ✅ Combined {len(combined_locations)} locations")
    
    # 6. POLLUTION ANALYSIS - DISTANCE TO NEAREST POLLUTION MEASUREMENT
    print(f"\n🌪️  Pollution Proximity Analysis:")
    
    def find_nearest_pollution(location_row, pollution_gdf):
        """Find nearest pollution measurement for each location"""
        location_point = Point(location_row['longitude'], location_row['latitude'])
        
        # Convert to projected CRS for distance calculation
        location_proj = gpd.GeoSeries([location_point], crs='EPSG:4326').to_crs('EPSG:3857').iloc[0]
        pollution_proj = pollution_gdf.to_crs('EPSG:3857')
        
        # Calculate distances
        distances = pollution_proj.geometry.distance(location_proj)
        
        # Find nearest
        nearest_idx = distances.idxmin()
        nearest_distance = distances.loc[nearest_idx] / 1000  # Convert to km
        nearest_pollution = pollution_gdf.loc[nearest_idx]
        
        return {
            'nearest_pollution_level': nearest_pollution['Rang'], 
            'distance_to_pollution_km': nearest_distance,
            'pollution_id': nearest_pollution['TRAM']
        }
    
    # Add pollution info to each location
    pollution_info = combined_locations.apply(
        lambda row: find_nearest_pollution(row, pollution_gdf), axis=1
    )
    
    # Extract pollution info into separate columns
    combined_locations['pollution_level'] = [info['nearest_pollution_level'] for info in pollution_info]
    combined_locations['pollution_distance_km'] = [info['distance_to_pollution_km'] for info in pollution_info]
    
    # 7. RANK BY POLLUTION LEVEL (parsing the Rang column)
    print(f"\n🏆 Ranking by Pollution Level:")
    
    def parse_pollution_level(rang_str):
        """Parse pollution level from 'Rang' column (e.g., '20-25 µg/m³' -> 22.5)"""
        try:
            # Extract numbers from range like "20-25 µg/m³"
            numbers = [float(x) for x in rang_str.split() if any(c.isdigit() for c in x)]
            if len(numbers) >= 2:
                return (numbers[0] + numbers[1]) / 2  # Average of range
            elif len(numbers) == 1:
                return numbers[0]
            return 0
        except:
            return 0
    
    combined_locations['pollution_numeric'] = combined_locations['pollution_level'].apply(parse_pollution_level)
    
    # Sort by highest pollution (descending)
    combined_locations = combined_locations.sort_values('pollution_numeric', ascending=False)
    
    print(f"  ✅ Ranked {len(combined_locations)} locations by pollution level")
    
    # 8. PREPARE FINAL RESULTS
    print(f"\n📋 Final Results:")
    
    # Prepare final output with exactly 3 required columns
    results = combined_locations[['name', 'longitude', 'latitude']].copy()
    
    # Export to CSV
    results.to_csv('results.csv', index=False)
    
    print(f"  📄 Exported {len(results)} results to 'results.csv'")
    print(f"  🥇 Top 5 highest pollution locations:")
    
    for i, row in combined_locations.head().iterrows():
        print(f"    {row['name']} ({row['type']}) - {row['pollution_level']} - {row['pollution_distance_km']:.2f}km away")
    
    return combined_locations

if __name__ == "__main__":
    try:
        results = analyze_data_properly()
        print(f"\n✅ Analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc() 