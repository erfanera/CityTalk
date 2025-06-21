from BaseAgent import BaseAgent
import json
import os
import pandas as pd
import geopandas as gpd
import numpy as np
import re

class MainAgent(BaseAgent):
    def _init_(self, api_key):
        super()._init_(api_key)
        self.model = "gpt-4o"  # Using GPT-4 for better code generation

    def generate_analysis_code(self, user_question, enriched_datasets):
        """
        Generates Python code to analyze data based on user question and available datasets.
        
        Args:
            user_question (str): The user's question/request
            enriched_datasets (dict): Dictionary with dataset_name: (dataset, analysis) tuples
        
        Returns:
            str: Generated Python code
        """
        # Prepare dataset information for the prompt
        dataset_info = self._prepare_dataset_summary(enriched_datasets)
        
        # Create comprehensive prompt for code generation
        prompt = f"""
        You are an expert data analyst and Python programmer. Generate ONLY Python code to answer the user's question using the available datasets.

        USER QUESTION: "{user_question}"

        AVAILABLE DATASETS:
        {dataset_info}

        CRITICAL REQUIREMENTS:
        1. Generate ONLY executable Python code - NO explanations, NO markdown, NO text outside code
        2. Use pandas, geopandas, and other relevant libraries as needed
        3. The final output MUST be a CSV file with exactly 3 columns:
           - 'name': descriptive name/identifier of the location/feature
           - 'longitude': longitude coordinate  
           - 'latitude': latitude coordinate
        4. Handle different question types appropriately:
           - Representative: Show correlations, visualizations, analysis
           - Predictive: Identify potential locations, predict outcomes
           - Suggestion: Recommend best locations based on criteria
        5. Use appropriate spatial analysis, filtering, and data processing
        6. Export results to 'results.csv'
        7. Include comments explaining the logic
        8. Handle missing data and edge cases
        9. If datasets need to be combined, use spatial joins or other appropriate methods

        PYTHON FORMATTING REQUIREMENTS:
        - Use proper 4-space indentation for all code blocks
        - Ensure every line after ':' is properly indented
        - Format try/except blocks correctly:
          try:
              # 4 spaces indentation
              code_here
          except:
              # 4 spaces indentation  
              error_handling
        - Format if/else blocks correctly:
          if condition:
              # 4 spaces indentation
              code_here
          else:
              # 4 spaces indentation
              code_here
        - No syntax errors like missing colons, incorrect spacing, or malformed operators

        WORKING SOLUTION PATTERN (COPY THIS APPROACH):
        python
        # PROVEN WORKING APPROACH - Use this exact pattern:
        
        # 1. Distance-based proximity analysis (NOT spatial joins)
        el_poblenou_center = Point(2.2017, 41.4005)
        
        def filter_by_distance(gdf, center_point, max_distance_km=2.0):
            gdf_proj = gdf.to_crs('EPSG:3857')
            center_proj = gpd.GeoSeries([center_point], crs='EPSG:4326').to_crs('EPSG:3857').iloc[0]
            distances = gdf_proj.geometry.distance(center_proj)
            nearby_mask = distances <= (max_distance_km * 1000)
            nearby_gdf = gdf[nearby_mask].copy()
            return nearby_gdf
        
        # 2. Filter locations in area (these are only examples you need to change it based on the questions)
        nearby_parks = filter_by_distance(park_locations, el_poblenou_center)
        nearby_schools = filter_by_distance(school_locations, el_poblenou_center)
        
        # 3. Process pollution data correctly  
        if 'geometry_wkt' in pollution.columns:
            pollution['geometry'] = pollution['geometry_wkt'].apply(wkt.loads)
            pollution = gpd.GeoDataFrame(pollution, geometry='geometry', crs='EPSG:4326')
        
        # 4. Find nearest pollution for each location
        def find_nearest_pollution(location_row, pollution_gdf):
            location_point = Point(location_row['longitude'], location_row['latitude'])
            location_proj = gpd.GeoSeries([location_point], crs='EPSG:4326').to_crs('EPSG:3857').iloc[0]
            pollution_proj = pollution_gdf.to_crs('EPSG:3857')
            distances = pollution_proj.geometry.distance(location_proj)
            nearest_idx = distances.idxmin()
            return pollution_gdf.loc[nearest_idx]['Rang']
        
        # 5. Extract coordinates properly (these are only examples you need to change it based on the questions)
        nearby_parks['longitude'] = nearby_parks.geometry.centroid.x
        nearby_parks['latitude'] = nearby_parks.geometry.centroid.y
        nearby_schools['longitude'] = nearby_schools.geometry.centroid.x  
        nearby_schools['latitude'] = nearby_schools.geometry.centroid.y
        
        # 6. Combine and rank results (these are only examples you need to change it based on the questions)
        parks_df = nearby_parks[['name', 'longitude', 'latitude']].copy()
        schools_df = nearby_schools[['name', 'longitude', 'latitude']].copy()
        combined = pd.concat([parks_df, schools_df], ignore_index=True)
        
        # 7. Export results
        combined[['name', 'longitude', 'latitude']].to_csv('results.csv', index=False)
        

        CRITICAL TRY/EXCEPT FORMATTING - AVOID THESE ERRORS:
        ❌ WRONG (causes syntax errors):
        
        try:
            code_line_1
        code_line_2  # This should be inside try block!
            except:
                error_handling
        
        
        ✅ CORRECT:
        
        try:
            code_line_1
            code_line_2  # Both lines inside try block
        except:
            error_handling
        
        
        OR use simple approach without try/except:
        
        if 'geometry_wkt' in pollution.columns:
            pollution['geometry'] = pollution['geometry_wkt'].apply(wkt.loads)
            pollution = gpd.GeoDataFrame(pollution, geometry='geometry', crs='EPSG:4326')
        

        DATA STRUCTURE EXAMPLES & GUIDANCE:
        
        OSM Data (GeoDataFrames):
        - Columns: geometry, name, amenity/leisure, opening_hours, etc.
        - geometry: Point/Polygon geometries in EPSG:4326
        - Extract coordinates: .geometry.centroid.x, .geometry.centroid.y
        
        CSV Pollution Data:
        - Expected columns: TRAM, Rang, geometry_wkt
        - geometry_wkt: WKT format strings like "POINT(2.1734 41.3851)"
        - Rang: pollution ranking (higher = more polluted)
        - If data appears corrupted, try different approaches or filtering
        
        SPATIAL ANALYSIS BEST PRACTICES:
        1. Always validate data before processing:
           - Check for empty datasets: if data.empty: handle appropriately
           - Verify geometry columns exist and are valid (the structure of the data is provided in the dataset_info)
           - Print data info for debugging: print(f"Dataset shape: {{data.shape}}")
        
        2. Proper CRS handling:
           - Use projected CRS for spatial calculations: .to_crs('EPSG:3857') 
           - Convert back to geographic for final coordinates: .to_crs('EPSG:4326')
           - Example: data = data.to_crs('EPSG:3857') # for calculations
                     data = data.to_crs('EPSG:4326') # for final coordinates
        
        3. Distance-based proximity (NOT string matching):
           - Define reference point: el_poblenou_center = Point(2.2017, 41.4005) (these are only examples you need to change it based on the questions)
           - Calculate distances: data['distance'] = data.geometry.distance(point)
           - Filter by distance: nearby = data[data['distance'] < 2000]  # 2km in meters
        
        4. Spatial joins - handle potential issues:
           - Check both datasets have geometries
           - Use buffer for point-to-polygon joins: points.buffer(0.001)
           - Handle empty results: if result.empty: print("No spatial intersections found")
        
        5. Data cleaning for corrupted data:
           - Check for malformed strings in numeric columns
           - Filter out invalid geometries: data = data[data.geometry.is_valid]
           - Handle missing values: data = data.dropna(subset=['important_column'])

        EXAMPLE PATTERNS:
        
        For proximity analysis:
        
        # Define location reference point
        location_center = Point(longitude, latitude)
        
        # Calculate distances (use projected CRS)
        data_projected = data.to_crs('EPSG:3857')
        data_projected['distance'] = data_projected.geometry.distance(location_center)
        
        # Filter by distance
        nearby_data = data_projected[data_projected['distance'] <= 2000]  # 2km
        
        # Convert back for coordinates
        nearby_data = nearby_data.to_crs('EPSG:4326')
        
        
        For pollution analysis:
        
        # Validate pollution data first
        if 'geometry_wkt' in pollution.columns:
            try:
                pollution['geometry'] = pollution['geometry_wkt'].apply(wkt.loads)
                pollution = gpd.GeoDataFrame(pollution, geometry='geometry')
            except:
                print("Error processing pollution geometry")
                # Try alternative approach
        
        # Ensure CRS consistency
        pollution = pollution.to_crs('EPSG:4326')
        

        GEOMETRY HANDLING - VERY IMPORTANT:
        - Before accessing .x and .y attributes, ensure geometries are Points
        - For non-Point geometries (Polygons, LineStrings), use .centroid first
        - Example: data['longitude'] = data.geometry.centroid.x
        - Example: data['latitude'] = data.geometry.centroid.y
        - Always handle CRS: use .to_crs('EPSG:4326') to ensure consistent coordinate system
        - Check geometry types before operations: data.geometry.geom_type

        ERROR PREVENTION:
        - Always use .centroid.x and .centroid.y for coordinate extraction to handle all geometry types
        - Set CRS consistently: gdf.set_crs('EPSG:4326', allow_override=True) if CRS is None
        - Use proper distance calculations in projected coordinates for accuracy
        - Handle empty results with proper checks
        - Add data validation steps at the beginning
        - Print intermediate results for debugging

        DATASET ACCESS - VERY IMPORTANT:
        - Use these EXACT variable names directly: {list(self._get_dataset_variable_names(enriched_datasets).keys())}
        - DO NOT use pd.read_csv(), gpd.read_file(), or any file loading operations
        - DO NOT assign variables like: park_locations = gpd.read_file('file.shp')
        - The variables are ALREADY DEFINED and ready to use immediately
        - Simply use the variable names in your analysis (e.g., just use 'park_locations' directly)
        - Extract coordinates from geometry column if it exists using .geometry.centroid.x and .geometry.centroid.y
        - Use appropriate spatial operations for geographic data

        DEBUGGING STEPS TO INCLUDE:
        - Print dataset shapes and info
        - Validate geometries before spatial operations
        - Check for empty results and handle appropriately
        - Add try-except blocks for data processing steps

        PREFER SIMPLE CODE PATTERNS:
        - Use simple if statements instead of try/except when possible
        - Example: if 'column' in data.columns: process_data()
        - Avoid complex nested try/except blocks that cause indentation errors
        - Use direct assignments with validation rather than exception handling

        IMPORTANT: Return ONLY Python code. Start directly with the analysis using the provided variable names. NO file loading operations allowed. Use proper spatial distance calculations and handle all geometry types correctly. Include data validation and debugging steps. PREFER SIMPLE CODE PATTERNS over complex try/except blocks.
        """
        
        try:
            generated_code = self.send_prompt(prompt)
            print("Generated code:" + generated_code)
            return self._clean_generated_code(generated_code)
        except Exception as e:
            return f"# Error generating code: {str(e)}\nprint('Error: Could not generate analysis code')"

    def _prepare_dataset_summary(self, enriched_datasets):
        """
        Prepares a summary of available datasets for the prompt.
        """
        summary = []
        
        for dataset_name, (dataset, analysis) in enriched_datasets.items():
            # Get basic dataset info
            columns = list(dataset.columns)
            row_count = len(dataset)
            
            # Check if it has geometry (spatial data)
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
    def _clean_generated_code(self,code):
        match = re.search(r"```python\n(.*?)```", code, re.DOTALL)
        if match:
            code = match.group(1)
        return code
    def clean_generated_code(self, code):
        """
        Cleans and formats the generated code with enhanced error prevention and proper indentation.
        """
        # Remove markdown code blocks if present
        if "python" in code:
            code = code.split("python")[1].split("")[0]
        elif "" in code:
            code = code.split("")[1].split("")[0]
        
        # Remove leading/trailing whitespace
        code = code.strip()
        
        # Remove any non-ASCII characters that might cause syntax errors
        code = code.encode('ascii', 'ignore').decode('ascii')
        
        # Split into lines for processing
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith('#'):
                # Keep comments and empty lines as-is
                cleaned_lines.append(line)
                continue
            
            # Fix common syntax errors
            line = line.replace(' = = ', ' == ')  # Fix double equals
            line = line.replace('= =', '==')      # Fix spaced equals
            line = line.replace(' ! = ', ' != ')  # Fix not equals
            line = line.replace('! =', '!=')      # Fix spaced not equals
            line = line.replace('< = ', '<=')     # Fix less than or equal
            line = line.replace('> = ', '>=')     # Fix greater than or equal
            line = line.replace(' < = ', ' <= ')  # Fix spaced less than or equal
            line = line.replace(' > = ', ' >= ')  # Fix spaced greater than or equal
            
            # Fix spacing around operators (but be careful not to break string literals)
            if '"' not in line and "'" not in line:  # Only if no strings in line
                # Handle compound operators FIRST to prevent breaking them
                line = line.replace('<=', ' <= ').replace('  <=  ', ' <= ')
                line = line.replace('>=', ' >= ').replace('  >=  ', ' >= ')
                line = line.replace('==', ' == ').replace('  ==  ', ' == ')
                line = line.replace('!=', ' != ').replace('  !=  ', ' != ')
                
                # Then handle individual operators (but avoid breaking compound ones)
                # Only replace isolated < and > that aren't part of <= or >=
                line = re.sub(r'(?<![<>=!])<(?![=])', ' < ', line)  # < not preceded by <>=! and not followed by =
                line = re.sub(r'(?<![<>=!])>(?![=])', ' > ', line)  # > not preceded by <>=! and not followed by =
                line = re.sub(r'(?<![<>=!])=(?![=])', ' = ', line)  # = not preceded by <>=! and not followed by =
                
                # Clean up multiple spaces
                line = re.sub(r'\s+', ' ', line)
            
            # Fix specific common issues
            line = line.replace('.distance(', '.geometry.distance(')
            line = line.replace('.geometry.geometry.distance(', '.geometry.distance(')
            
            cleaned_lines.append(line)
        
        # Now fix indentation using a simpler approach
        formatted_lines = []
        indent_level = 0
        
        for i, line in enumerate(cleaned_lines):
            if not line.strip():
                formatted_lines.append('')
                continue
            
            stripped = line.strip()
            
            # Handle exception keywords first (they should align with their corresponding try/if)
            if stripped.startswith(('except', 'elif', 'else', 'finally')):
                # These should be at the same level as their corresponding opening statement
                indent_level = max(0, indent_level - 1)
                formatted_line = '    ' * indent_level + stripped
                formatted_lines.append(formatted_line)
                # After except/elif/else, the next lines should be indented
                if stripped.endswith(':'):
                    indent_level += 1
                continue
            
            # Apply current indentation to regular lines
            formatted_line = '    ' * indent_level + stripped
            formatted_lines.append(formatted_line)
            
            # Determine if next line should be indented
            if stripped.endswith(':'):
                indent_level += 1
            # Handle dedentation after certain statements
            elif stripped.startswith(('return', 'break', 'continue', 'pass', 'raise')):
                # Look ahead to see if we need to dedent
                if (i + 1 < len(cleaned_lines) and 
                    cleaned_lines[i + 1].strip() and 
                    not cleaned_lines[i + 1].strip().startswith(('except', 'elif', 'else', 'finally', '#'))):
                    # Next line is not part of this block, so dedent
                    indent_level = max(0, indent_level - 1)
        
        code = '\n'.join(formatted_lines)
        
        # Add necessary imports at the top if missing
        imports_to_check = [
            "import pandas as pd",
            "import geopandas as gpd", 
            "import numpy as np",
            "from shapely.geometry import Point",
            "from shapely import wkt"
        ]
        
        for import_stmt in imports_to_check:
            if import_stmt not in code:
                code = import_stmt + "\n" + code
        
        return code

    def _get_dataset_variable_names(self, enriched_datasets):
        """
        Get valid Python variable names for datasets.
        """
        dataset_variables = {}
        for dataset_name, (dataset, analysis) in enriched_datasets.items():
            # Create valid Python variable names
            var_name = dataset_name.lower().replace(" ", "").replace("-", "")
            dataset_variables[var_name] = dataset
        return dataset_variables

    def execute_code(self, code, enriched_datasets):
        """
        Executes the generated Python code with the datasets in scope.
        
        Args:
            code (str): Python code to execute
            enriched_datasets (dict): Available datasets
            
        Returns:
            dict: Execution results and status
        """
        print("🚀 Executing generated code...")
        
        # Prepare execution environment
        exec_globals = {
            'pd': pd,
            'gpd': gpd,
            'np': np,
            'os': os,
            
        }
        
        # Add datasets to execution environment
        dataset_variables = self._get_dataset_variable_names(enriched_datasets)
        exec_globals.update(dataset_variables)
        
        try:
            # Execute the code
            exec(code, exec_globals)
            
            # Check if results.csv was created
            if os.path.exists('results.csv'):
                results_df = pd.read_csv('results.csv')
                print(f"✅ Code executed successfully!")
                print(f"📄 Results saved to 'results.csv' with {len(results_df)} rows")
                print(f"📊 Preview of results:")
                print(results_df.head())
                
                return {
                    "status": "success",
                    "message": "Code executed successfully",
                    "output_file": "results.csv",
                    "row_count": len(results_df),
                    "preview": results_df.head().to_dict(),
                    "executed_code": code
                }
            else:
                print("⚠ Code executed but no results.csv file was created")
                return {
                    "status": "warning", 
                    "message": "Code executed but no output file found",
                    "executed_code": code
                }
                
        except Exception as e:
            print(f"❌ Error executing code: {str(e)}")
            return {
                "status": "error",
                "message": f"Execution error: {str(e)}",
                "executed_code": code
            }

    def correct_code_error(self, original_code, error_message, user_question, enriched_datasets):
        """
        Generates corrected code based on the error message from the previous execution.
        
        Args:
            original_code (str): The code that failed
            error_message (str): The error message from execution
            user_question (str): Original user question
            enriched_datasets (dict): Available datasets
            
        Returns:
            str: Corrected Python code
        """
        dataset_info = self._prepare_dataset_summary(enriched_datasets)
        
        # Truncate extremely long error messages to prevent context overflow
        max_error_length = 1000
        if len(error_message) > max_error_length:
            error_message = error_message[:max_error_length] + "... [ERROR MESSAGE TRUNCATED - TOO LONG]"
        
        # Extract the specific line that caused the error if possible
        error_line = ""
        if "line" in error_message and "invalid syntax" in error_message:
            try:
                lines = original_code.split('\n')
                line_num = int(error_message.split('line ')[1].split(')')[0])
                if line_num <= len(lines):
                    error_line = f"\nERROR LINE {line_num}: {lines[line_num-1]}"
            except:
                pass
        
        prompt = f"""
        You are debugging Python code that failed to execute. Fix the error and generate corrected code.

        ORIGINAL USER QUESTION: "{user_question}"

        FAILED CODE:
        {original_code}

        ERROR MESSAGE:
        {error_message}{error_line}

        AVAILABLE DATASETS:
        {dataset_info}

        CRITICAL DEBUGGING FOCUS:
        The error message is: "{error_message}"
        
        If "invalid syntax":
        - Check for double spaces in operators like "= =" should be "=="
        - Check for malformed comparison operators
        - Check for missing commas, colons, or parentheses
        - Fix spacing around operators
        
        If "expected an indented block":
        - CRITICAL: Fix Python indentation immediately after ':' 
        - Use exactly 4 spaces for indentation (not tabs)
        - After if:, try:, except:, for:, while:, def:, class: - next line MUST be indented
        - Example fix:
          if condition:
              # This line needs 4 spaces of indentation
              code_here
          try:
              # This line needs 4 spaces of indentation  
              code_here
          except:
              # This line needs 4 spaces of indentation
              error_handling
        
        If "expected 'except' or 'finally' block":
        - CRITICAL: Fix malformed try/except structure
        - ALL code in try block must be properly indented
        - ❌ WRONG: try: code_line except: (code_line outside try block)
        - ✅ CORRECT: try: [4 spaces]code_line except: [4 spaces]error_handling
        - Example fix:
          # WRONG (causes error):
          try:
              line1
          line2  # This line should be inside try!
              except:
                  error_handling
          
          # CORRECT:
          try:
              line1
              line2  # Both lines properly inside try block
          except:
              error_handling
          
          # OR use simple if statement instead:
          if condition:
              line1
              line2
        
        If "could not convert string to numeric":
        - The data appears corrupted with concatenated values
        - Add data cleaning steps to handle malformed data
        - Use proper data filtering and validation
        - Try different approaches to access the data
        
        DEBUGGING REQUIREMENTS:
        1. Analyze the error message carefully - focus on the specific issue
        2. Fix the EXACT issue that caused the failure
        3. Generate ONLY corrected Python code - NO explanations
        4. If data seems corrupted, add data validation and cleaning steps
        5. Ensure final output is CSV with 3 columns: name, longitude, latitude
        6. Use these EXACT variable names: {list(self._get_dataset_variable_names(enriched_datasets).keys())}
        7. DO NOT load files - variables are already available

        SPECIFIC ERROR FIXES:
        - If "invalid syntax" with "= =": Change to "=="
        - If "invalid syntax" with "! =": Change to "!="  
        - If "invalid syntax" with "< =": Change to "<="
        - If "invalid syntax" with "> =": Change to ">="
        - If "expected an indented block": Add 4 spaces indentation after ':'
        - If "expected 'except' or 'finally' block": Fix malformed try/except structure
        - If "could not convert string to numeric": Add data cleaning and validation
        - If "x attribute access only provided for Point geometries": Use .centroid.x and .centroid.y
        - If "CRS mismatch": Use .to_crs('EPSG:4326') to standardize coordinate systems
        - If NameError: check variable names match exactly: {list(self._get_dataset_variable_names(enriched_datasets).keys())}
        - If AttributeError: check column names and methods exist, use .centroid for geometry access
        - If KeyError: verify column names in the data
        - If ImportError: add missing import statements
        - If geometric errors: ensure proper coordinate extraction using .centroid.x and .centroid.y
        - If empty results: add proper checks for empty dataframes
        - If "sjoin() got an unexpected keyword argument": Use predicate= instead of op=
        - If "'right_df' should be GeoDataFrame": Convert DataFrame to GeoDataFrame before spatial join
        - If "Geometry is in a geographic CRS" warning: Use projected CRS for calculations
        - If spatial join returns 0 rows: Check data alignment, add debugging, try distance-based approach
        - If "geometry.geometry.distance": Remove duplicate .geometry (should be just .geometry.distance)

        SPATIAL ANALYSIS ERROR FIXES:
        - Empty spatial join results: Add data validation and debugging steps
        - Use distance-based proximity instead of spatial intersections for point data
        - Check both datasets have valid geometries before spatial operations
        - Print intermediate results to identify where data is lost
        - For point-to-polygon joins, consider using buffer: points.buffer(0.001)
        - Always validate data exists before processing: if not data.empty:

        GEOMETRY HANDLING FIXES:
        - ALWAYS use .geometry.centroid.x and .geometry.centroid.y for coordinate extraction
        - Set CRS if missing: gdf.set_crs('EPSG:4326', allow_override=True)
        - Check for empty geometries before operations
        - Use proper distance calculations in meters
        - Use projected CRS (EPSG:3857) for distance calculations, then convert back to EPSG:4326

        Return ONLY the corrected Python code with the error fixed.
        """
        
        try:
            corrected_code = self.send_prompt(prompt)
            return self._clean_generated_code(corrected_code)
        except Exception as e:
            return f"# Error generating correction: {str(e)}\nprint('Could not generate corrected code')"

    def execute_code_with_retry(self, code, enriched_datasets, max_retries=5):
        """
        Executes code with automatic error correction and retry capability.
        
        Args:
            code (str): Python code to execute
            enriched_datasets (dict): Available datasets
            max_retries (int): Maximum number of correction attempts (default 5 for 6 total attempts)
            
        Returns:
            dict: Execution results and status
        """
        attempt = 1
        current_code = code
        
        while attempt <= max_retries + 1:  # +1 for initial attempt
            print(f"🚀 Executing code (Attempt {attempt})...")
            
            # Prepare execution environment
            exec_globals = {
                'pd': pd,
                'gpd': gpd,
                'np': np,
                'os': os,
                '_builtins': __builtins__
            }
            
            # Add datasets to execution environment
            dataset_variables = self._get_dataset_variable_names(enriched_datasets)
            exec_globals.update(dataset_variables)
            
            try:
                # Execute the code
                exec(current_code, exec_globals)
                
                # Check if results.csv was created
                if os.path.exists('results.csv'):
                    results_df = pd.read_csv('results.csv')
                    print(f"✅ Code executed successfully on attempt {attempt}!")
                    print(f"📄 Results saved to 'results.csv' with {len(results_df)} rows")
                    print(f"📊 Preview of results:")
                    print(results_df.head())
                    
                    return {
                        "status": "success",
                        "message": f"Code executed successfully on attempt {attempt}",
                        "output_file": "results.csv",
                        "row_count": len(results_df),
                        "preview": results_df.head().to_dict(),
                        "executed_code": current_code,
                        "attempts": attempt
                    }
                else:
                    print("⚠ Code executed but no results.csv file was created")
                    return {
                        "status": "warning", 
                        "message": f"Code executed but no output file found (attempt {attempt})",
                        "executed_code": current_code,
                        "attempts": attempt
                    }
                    
            except Exception as e:
                error_message = str(e)
                print(f"❌ Attempt {attempt} failed with error: {error_message}")
                
                if attempt <= max_retries:
                    print(f"🔧 Attempting to correct the error...")
                    current_code = self.correct_code_error(
                        current_code, 
                        error_message, 
                        self.current_question if hasattr(self, 'current_question') else "Original user question",
                        enriched_datasets
                    )
                    print("\n" + "="*50)
                    print(f"📄 CORRECTED CODE (Attempt {attempt + 1}):")
                    print("="*50)
                    print(current_code)
                    print("="*50 + "\n")
                    attempt += 1
                else:
                    print(f"❌ All {max_retries + 1} attempts failed")
                    return {
                        "status": "error",
                        "message": f"Final error after {attempt} attempts: {error_message}",
                        "executed_code": current_code,
                        "attempts": attempt
                    }
        
        return {
            "status": "error",
            "message": "Maximum retries exceeded",
            "executed_code": current_code,
            "attempts": attempt
        }

    def execute_question(self, user_question, enriched_datasets):
        """
        Complete workflow: Generate code and execute it automatically with error correction.
        
        Args:
            user_question (str): The user's question
            enriched_datasets (dict): Available datasets
            
        Returns:
            dict: Execution results and status
        """
        print(f"🤖 Analyzing question: {user_question}")
        print(f"📊 Available datasets: {list(enriched_datasets.keys())}")
        
        # Generate the analysis code
        generated_code = self.generate_analysis_code(user_question, enriched_datasets)
        print("📝 Code generated successfully")
        
        # Print the generated code
        print("\n" + "="*50)
        print("📄 GENERATED CODE:")
        print("="*50)
        print(generated_code)
        print("="*50 + "\n")
        
        # Store the original question for error correction
        self.current_question = user_question
        
        # Execute the code automatically with retry capability
        execution_result = self.execute_code_with_retry(generated_code, enriched_datasets)
        
        # Add question to result
        execution_result["question"] = user_question
        execution_result["available_datasets"] = list(enriched_datasets.keys())
        
        return execution_result

    def categorize_question(self, user_question):
        """
        Categorizes the user question into representative, predictive, or suggestion type.
        """
        prompt = f"""
        Categorize this question into one of three types:
        1. "representative" - Questions about visualization, correlation, analysis, showing patterns
        2. "predictive" - Questions about potential, prediction, forecasting, "could be"
        3. "suggestion" - Questions asking for recommendations, best options, "suggest"
        
        Question: "{user_question}"
        
        Return only the category name: representative, predictive, or suggestion
        """
        
        try:
            category = self.send_prompt(prompt).strip().lower()
            if category in ["representative", "predictive", "suggestion"]:
                return category
            else:
                return "representative"  # Default fallback
        except:
            return "representative"  # Default fallback
