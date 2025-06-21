from BaseAgent import BaseAgent
import json
import os
import pandas as pd
import geopandas as gpd
import numpy as np
import re

class MainAgent(BaseAgent):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.model = "gpt-4o"  # Using GPT-4 for better code generation

    def generate_analysis_code(self, user_question, enriched_datasets, coordinates=None):
        """
        Generates Python code (or a prompt) for spatial analysis using enriched datasets and (optionally) coordinates.
        Args:
            user_question (str): The user's query (e.g. "Find residential buildings in low emission zones in Barceloneta").
            enriched_datasets (dict): A dictionary (or a string prompt) containing (or describing) the datasets (e.g. residential buildings, emission zones).
            coordinates (dict, optional): A dictionary (or a string prompt) (e.g. { "Barceloneta": { "lat": 41.3809, "lon": 2.191 } }) or None.
        Returns:
            str: A Python code snippet (or a prompt) (e.g. """\n# Generated analysis code (or prompt) for spatial analysis\n\n# 1. Define target center (using coordinates if provided) \n{self._generate_location_centers_code(coordinates)}\n\n# 2. Include mandatory helper functions (using instance methods) \n# (Note: Do not define a global filter_by_distance; use self.filter_by_distance_with_fallback or self.filter_by_distance.) \n\n# 3. Validate and convert emission data (using a helper) \nemission_gdf = validate_and_convert_emission_data(air_pollution_levels) \n\n# 4. Filter residential buildings (using self.filter_by_distance_with_fallback) \n{self._generate_location_filter_code(coordinates)}\n\n# 5. Filter emission zones (using self.filter_by_distance_with_fallback) \n{self._generate_emission_filter_code(coordinates)}\n\n# 6. (Optional) Print debug info (using a helper) \n{self._generate_debug_coordinates_code(coordinates)}\n\n# 7. (Optional) Proximity analysis (using self.find_nearest_emission_for_location) \n# (e.g. loop over nearby_buildings and call self.find_nearest_emission_for_location(building, nearby_emissions) ) \n\n# 8. (Optional) Combine (or export) results (e.g. pd.DataFrame(...) and .to_csv(...)) \n\n"""")
        """
        # (Optional) If enriched_datasets is a prompt (or coordinates is a prompt), return a prompt (e.g. """\n# Prompt for spatial analysis (using enriched_datasets and coordinates)""")
        if (isinstance(enriched_datasets, str) or (coordinates is not None and isinstance(coordinates, str))):
             return ("""\n# Prompt for spatial analysis (using enriched_datasets and coordinates) (e.g. """\n# Generated analysis code (or prompt) for spatial analysis\n\n# 1. Define target center (using coordinates if provided) \n{self._generate_location_centers_code(coordinates)}\n\n# 2. Include mandatory helper functions (using instance methods) \n# (Note: Do not define a global filter_by_distance; use self.filter_by_distance_with_fallback or self.filter_by_distance.) \n\n# 3. Validate and convert emission data (using a helper) \nemission_gdf = validate_and_convert_emission_data(air_pollution_levels) \n\n# 4. Filter residential buildings (using self.filter_by_distance_with_fallback) \n{self._generate_location_filter_code(coordinates)}\n\n# 5. Filter emission zones (using self.filter_by_distance_with_fallback) \n{self._generate_emission_filter_code(coordinates)}\n\n# 6. (Optional) Print debug info (using a helper) \n{self._generate_debug_coordinates_code(coordinates)}\n\n# 7. (Optional) Proximity analysis (using self.find_nearest_emission_for_location) \n# (e.g. loop over nearby_buildings and call self.find_nearest_emission_for_location(building, nearby_emissions) ) \n\n# 8. (Optional) Combine (or export) results (e.g. pd.DataFrame(...) and .to_csv(...)) \n\n"""")

        # (Otherwise) Generate a Python code snippet (or prompt) (e.g. """\n# Generated analysis code (or prompt) for spatial analysis\n\n# 1. Define target center (using coordinates if provided) \n{self._generate_location_centers_code(coordinates)}\n\n# 2. Include mandatory helper functions (using instance methods) \n# (Note: Do not define a global filter_by_distance; use self.filter_by_distance_with_fallback or self.filter_by_distance.) \n\n# 3. Validate and convert emission data (using a helper) \nemission_gdf = validate_and_convert_emission_data(air_pollution_levels) \n\n# 4. Filter residential buildings (using self.filter_by_distance_with_fallback) \n{self._generate_location_filter_code(coordinates)}\n\n# 5. Filter emission zones (using self.filter_by_distance_with_fallback) \n{self._generate_emission_filter_code(coordinates)}\n\n# 6. (Optional) Print debug info (using a helper) \n{self._generate_debug_coordinates_code(coordinates)}\n\n# 7. (Optional) Proximity analysis (using self.find_nearest_emission_for_location) \n# (e.g. loop over nearby_buildings and call self.find_nearest_emission_for_location(building, nearby_emissions) ) \n\n# 8. (Optional) Combine (or export) results (e.g. pd.DataFrame(...) and .to_csv(...)) \n\n"""")

        return ("""\n# Generated analysis code (or prompt) for spatial analysis\n\n# 1. Define target center (using coordinates if provided) \n{self._generate_location_centers_code(coordinates)}\n\n# 2. Include mandatory helper functions (using instance methods) \n# (Note: Do not define a global filter_by_distance; use self.filter_by_distance_with_fallback or self.filter_by_distance.) \n\n# 3. Validate and convert emission data (using a helper) \nemission_gdf = validate_and_convert_emission_data(air_pollution_levels) \n\n# 4. Filter residential buildings (using self.filter_by_distance_with_fallback) \n{self._generate_location_filter_code(coordinates)}\n\n# 5. Filter emission zones (using self.filter_by_distance_with_fallback) \n{self._generate_emission_filter_code(coordinates)}\n\n# 6. (Optional) Print debug info (using a helper) \n{self._generate_debug_coordinates_code(coordinates)}\n\n# 7. (Optional) Proximity analysis (using self.find_nearest_emission_for_location) \n# (e.g. loop over nearby_buildings and call self.find_nearest_emission_for_location(building, nearby_emissions) ) \n\n# 8. (Optional) Combine (or export) results (e.g. pd.DataFrame(...) and .to_csv(...)) \n\n"""")

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

    def _clean_generated_code(self, code):
        """
        Cleans and formats the generated code with enhanced error prevention and proper indentation.
        """
        # Remove markdown code blocks if present
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]
        
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
            var_name = dataset_name.lower().replace(" ", "_").replace("-", "_")
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
            '__builtins__': __builtins__
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
                print("⚠️ Code executed but no results.csv file was created")
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
        - DO NOT load files - variables are already available

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
                '__builtins__': __builtins__
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
                    print("⚠️ Code executed but no results.csv file was created")
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

    def execute_question(self, user_question, enriched_datasets, coordinates=None):
        """
        Complete workflow: Generate code and execute it automatically with enhanced empty results handling.
        
        Args:
            user_question (str): The user's question
            enriched_datasets (dict): Available datasets
            coordinates (dict): Extracted coordinates from AmenityAgent (e.g., {'Barceloneta': {'lat': '41.38', 'lon': '2.19'}})
            
        Returns:
            dict: Execution results and status
        """
        print(f"🤖 Analyzing question: {user_question}")
        print(f"📊 Available datasets: {list(enriched_datasets.keys())}")
        if coordinates:
            print(f"📍 Available coordinates: {list(coordinates.keys())}")
        
        # Generate the analysis code with coordinates
        generated_code = self.generate_analysis_code(user_question, enriched_datasets, coordinates)
        print("📝 Code generated successfully")
        
        # Print the generated code
        print("\n" + "="*50)
        print("📄 GENERATED CODE:")
        print("="*50)
        print(generated_code)
        print("="*50 + "\n")
        
        # Store the original question for error correction
        self.current_question = user_question
        self.current_coordinates = coordinates
        
        # Execute with enhanced empty results retry capability
        execution_result = self.execute_code_with_empty_retry(generated_code, enriched_datasets, user_question, coordinates)
        
        # Add question to result
        execution_result["question"] = user_question
        execution_result["available_datasets"] = list(enriched_datasets.keys())
        execution_result["coordinates_used"] = coordinates
        
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
            return "representative"  # Default fallback

    def execute_code_with_empty_retry(self, code, enriched_datasets, user_question, coordinates, max_retries=3):
        """
        Executes code with specific handling for empty results and targeted retries.
        
        Args:
            code (str): Python code to execute
            enriched_datasets (dict): Available datasets
            user_question (str): Original user question for context
            coordinates (dict): Extracted coordinates from AmenityAgent (e.g., {'Barceloneta': {'lat': '41.38', 'lon': '2.19'}})
            max_retries (int): Maximum number of retries for empty results
            
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
                '__builtins__': __builtins__
            }
            
            # Add datasets to execution environment
            dataset_variables = self._get_dataset_variable_names(enriched_datasets)
            exec_globals.update(dataset_variables)
            
            # Capture execution output for analysis
            import io
            import sys
            old_stdout = sys.stdout
            execution_output = io.StringIO()
            
            try:
                # Redirect stdout to capture debugging prints
                sys.stdout = execution_output
                exec(current_code, exec_globals)
                sys.stdout = old_stdout
                
                # Get the captured output
                debug_output = execution_output.getvalue()
                print(debug_output)  # Show the output to user
                
                # Check if results.csv was created and analyze it
                if os.path.exists('results.csv'):
                    results_df = pd.read_csv('results.csv')
                    print(f"✅ Code executed successfully on attempt {attempt}!")
                    print(f"📄 Results saved to 'results.csv' with {len(results_df)} rows")
                    
                    if len(results_df) == 0:
                        # EMPTY RESULTS - Analyze why and retry
                        print(f"⚠️ WARNING: Empty results detected on attempt {attempt}")
                        
                        if attempt <= max_retries:
                            # Analyze debugging output to understand why it failed
                            failure_reason = self._analyze_empty_results_failure(debug_output, enriched_datasets)
                            print(f"🔍 Failure analysis: {failure_reason}")
                            print(f"🔧 Generating corrected code for attempt {attempt + 1}...")
                            
                            # Generate corrected code with specific feedback
                            current_code = self._correct_empty_results_code(
                                current_code, 
                                failure_reason, 
                                user_question, 
                                enriched_datasets,
                                debug_output,
                                coordinates
                            )
                            print(f"\n📄 CORRECTED CODE (Attempt {attempt + 1}):")
                            print("="*50)
                            print(current_code)
                            print("="*50 + "\n")
                            attempt += 1
                            continue
                        else:
                            print(f"❌ All {max_retries + 1} attempts resulted in empty data")
                            return {
                                "status": "warning",
                                "message": f"Analysis completed but no matching data found after {attempt} attempts",
                                "output_file": "results.csv",
                                "row_count": 0,
                                "executed_code": current_code,
                                "attempts": attempt,
                                "debug_output": debug_output
                            }
                    else:
                        # SUCCESS - We have results!
                        print(f"📊 Preview of results:")
                        print(results_df.head())
                        
                        return {
                            "status": "success",
                            "message": f"Code executed successfully on attempt {attempt}",
                            "output_file": "results.csv",
                            "row_count": len(results_df),
                            "preview": results_df.head().to_dict(),
                            "executed_code": current_code,
                            "attempts": attempt,
                            "debug_output": debug_output
                        }
                else:
                    print("⚠️ Code executed but no results.csv file was created")
                    if attempt <= max_retries:
                        failure_reason = "No output file created - likely missing result.to_csv() statement"
                        current_code = self._correct_empty_results_code(
                            current_code, failure_reason, user_question, enriched_datasets, debug_output, coordinates
                        )
                        attempt += 1
                        continue
                    else:
                        return {
                            "status": "error", 
                            "message": f"No output file created after {attempt} attempts",
                            "executed_code": current_code,
                            "attempts": attempt
                        }
                    
            except Exception as e:
                sys.stdout = old_stdout
                error_message = str(e)
                debug_output = execution_output.getvalue()
                print(f"❌ Attempt {attempt} failed with error: {error_message}")
                
                if attempt <= max_retries:
                    print(f"🔧 Attempting to correct the error...")
                    current_code = self.correct_code_error(
                        current_code, error_message, user_question, enriched_datasets
                    )
                    attempt += 1
                else:
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

    def _analyze_empty_results_failure(self, debug_output, enriched_datasets):
        """
        Analyzes debugging output to determine why results are empty.
        
        Args:
            debug_output (str): Captured stdout from code execution
            enriched_datasets (dict): Available datasets
            
        Returns:
            str: Detailed analysis of failure reason
        """
        failure_reasons = []
        
        # Check for dataset loading issues
        if "No buildings found near location" in debug_output:
            failure_reasons.append("BUILDINGS_NOT_FOUND: No residential buildings within distance radius")
        
        if "No emission zones found near location" in debug_output:
            failure_reasons.append("EMISSIONS_NOT_FOUND: No emission zones within distance radius")
        
        if "Input dataset is empty" in debug_output:
            failure_reasons.append("EMPTY_INPUT: One or more input datasets are completely empty")
        
        if "Invalid emission data" in debug_output:
            failure_reasons.append("INVALID_EMISSION_DATA: Emission data missing geometry_wkt column or empty")
        
        if "Cannot perform matching" in debug_output:
            failure_reasons.append("NO_MATCHING_DATA: Missing buildings or emission data for proximity matching")
        
        # Check for distance/location issues
        if len(failure_reasons) == 0:
            # If no specific issues found, likely a distance/location problem
            dataset_info = []
            for name, (dataset, _) in enriched_datasets.items():
                dataset_info.append(f"{name}: {len(dataset)} rows")
            
            failure_reasons.append(f"DISTANCE_ISSUE: Likely distance radius too small or wrong location coordinates. Available data: {', '.join(dataset_info)}")
        
        return " | ".join(failure_reasons)

    def _correct_empty_results_code(self, original_code, failure_reason, user_question, enriched_datasets, debug_output, coordinates):
        """
        Generates corrected code specifically for empty results issues.
        
        Args:
            original_code (str): The code that produced empty results
            failure_reason (str): Analysis of why results were empty
            user_question (str): Original user question
            enriched_datasets (dict): Available datasets
            debug_output (str): Captured debugging output
            coordinates (dict): Extracted coordinates from AmenityAgent
            
        Returns:
            str: Corrected Python code
        """
        dataset_info = self._prepare_dataset_summary(enriched_datasets)
        
        prompt = f"""
        You are fixing code that executed successfully but produced EMPTY RESULTS (0 rows).

        ORIGINAL USER QUESTION: "{user_question}"

        FAILURE ANALYSIS: {failure_reason}

        DEBUGGING OUTPUT FROM FAILED ATTEMPT:
        {debug_output[-1000:]}  # Last 1000 characters

        AVAILABLE DATASETS:
        {dataset_info}

        SPECIFIC FIXES FOR EMPTY RESULTS:

        1. If "BUILDINGS_NOT_FOUND":
           - INCREASE distance radius from 2.0km to 5.0km or 10.0km
           - CHECK location coordinates - use exact coordinates from user query
           - TRY different building types (use 'building' column instead of specific types)

        2. If "EMISSIONS_NOT_FOUND":
           - INCREASE distance radius for emission zones
           - CHECK emission data variable name (use exact name from datasets)
           - VERIFY emission data processing with debugging prints

        3. If "DISTANCE_ISSUE":
           - INCREASE max_distance_km parameter to 10.0 or 20.0
           - CHECK if location coordinates are correct
           - PRINT bounds of datasets to verify spatial overlap

        4. If "INVALID_EMISSION_DATA":
           - CHECK correct dataset variable name (available: {list(self._get_dataset_variable_names(enriched_datasets).keys())})
           - VERIFY column names match exactly
           - ADD more validation and debugging

        ENHANCED SOLUTION PATTERN:
        ```python
        # Use LARGER distance radius for better coverage
        max_distance_km = 10.0  # Increased from 2.0

        # Add more debugging for dataset bounds
        print(f"Dataset bounds check:")
        if hasattr(residential_building_locations, 'total_bounds'):
            print(f"Buildings bounds: {{residential_building_locations.total_bounds}}")
        if hasattr(emission_zones, 'total_bounds'):
            print(f"Emissions bounds: {{emission_zones.total_bounds}}")

        # Check actual coordinate overlap
        barceloneta_center = Point(2.191, 41.3809)
        print(f"Target location: {{barceloneta_center}}")

        # Use larger radius in filter_by_distance calls
        nearby_buildings = filter_by_distance(residential_building_locations, barceloneta_center, max_distance_km)
        ```

        CRITICAL REQUIREMENTS:
        - INCREASE distance radius significantly (5-20km)
        - ADD bounds checking and coordinate validation
        - ENSURE correct dataset variable names are used
        - INCLUDE comprehensive debugging output
        - MAINTAIN all helper functions and debugging prints

        Generate ONLY the corrected Python code with these specific fixes applied.
        """
        
        try:
            corrected_code = self.send_prompt(prompt)
            return self._clean_generated_code(corrected_code)
        except Exception as e:
            return f"# Error generating correction: {str(e)}\nprint('Could not generate corrected code')"

    def _prepare_coordinates_info(self, coordinates):
        """
        Prepares coordinates information for the prompt.
        
        Args:
            coordinates (dict): Extracted coordinates from AmenityAgent
            
        Returns:
            str: Formatted coordinates information
        """
        if not coordinates:
            return "No specific coordinates provided"
        
        info_lines = []
        for location_name, location_data in coordinates.items():
            lat = location_data.get('lat', 'N/A')
            lon = location_data.get('lon', 'N/A')
            info_lines.append(f"- {location_name}: lat={lat}, lon={lon}")
        
        return "\n".join(info_lines)

    def _generate_location_centers_code(self, coordinates):
        """
        Generates code to define location centers using extracted coordinates.
        
        Args:
            coordinates (dict): Extracted coordinates from AmenityAgent
            
        Returns:
            str: Python code to define location centers
        """
        if not coordinates:
            return "# No coordinates available - using Barcelona center as fallback\ntarget_center = Point(2.1734, 41.3851)  # Barcelona center"
        
        code_lines = []
        for location_name, location_data in coordinates.items():
            lat = float(location_data.get('lat', 41.3851))
            lon = float(location_data.get('lon', 2.1734))
            var_name = location_name.lower().replace(' ', '_').replace('-', '_')
            code_lines.append(f"{var_name}_center = Point({lon}, {lat})  # {location_name}")
        
        # Set the primary target center
        first_location = list(coordinates.keys())[0]
        first_var = first_location.lower().replace(' ', '_').replace('-', '_')
        code_lines.append(f"target_center = {first_var}_center  # Primary target location")
        
        return "\n".join(code_lines)

    def _generate_location_filter_code(self, coordinates):
        """
        Generates code to filter buildings using the extracted coordinates.
        
        Args:
            coordinates (dict): Extracted coordinates from AmenityAgent
            
        Returns:
            str: Python code to filter buildings by location
        """
        if not coordinates:
            return "nearby_buildings = self.filter_by_distance_with_fallback(residential_building_locations, target_center)"
        return "nearby_buildings = self.filter_by_distance_with_fallback(residential_building_locations, target_center)"

    def _generate_emission_filter_code(self, coordinates):
        """
        Generates code to filter emission zones using the extracted coordinates.
        
        Args:
            coordinates (dict): Extracted coordinates from AmenityAgent
            
        Returns:
            str: Python code to filter emission zones by location
        """
        if not coordinates:
            return "nearby_emissions = self.filter_by_distance_with_fallback(emission_gdf, target_center)"
        return "nearby_emissions = self.filter_by_distance_with_fallback(emission_gdf, target_center)"

    def _get_emission_dataset_name(self, enriched_datasets):
        """
        Gets the correct emission dataset variable name.
        
        Args:
            enriched_datasets (dict): Available datasets
            
        Returns:
            str: Variable name for emission dataset
        """
        dataset_variables = self._get_dataset_variable_names(enriched_datasets)
        
        # Look for emission-related datasets
        for var_name in dataset_variables.keys():
            if any(keyword in var_name.lower() for keyword in ['emission', 'pollution', 'air']):
                return var_name
        
        # Fallback to first available dataset
        return list(dataset_variables.keys())[0] if dataset_variables else "emission_zones"

    def _generate_debug_coordinates_code(self, coordinates):
        """
        Generates debugging code to print coordinate information.
        
        Args:
            coordinates (dict): Extracted coordinates from AmenityAgent
            
        Returns:
            str: Python code to print debugging info
        """
        if not coordinates:
            return "print(f\"  - Target center: {{target_center}}\")"
        
        code_lines = []
        for location_name, location_data in coordinates.items():
            var_name = location_name.lower().replace(' ', '_').replace('-', '_')
            code_lines.append(f"print(f\"  - {location_name} center: {{{var_name}_center}}\")")
        
        return "\n            ".join(code_lines)

    def filter_by_distance(self, gdf, center_point, max_distance_km=10.0):
        """Filter features within a specified distance from a center point"""
        if gdf.empty:
            return gdf
        
        # Project to a metric system for accurate distance calculation
        gdf_proj = gdf.to_crs('EPSG:3857')
        center_proj = gpd.GeoSeries([center_point], crs='EPSG:4326').to_crs('EPSG:3857').iloc[0]
        
        # Calculate distances and filter
        distances = gdf_proj.geometry.distance(center_proj)
        nearby_mask = distances <= (max_distance_km * 1000)
        nearby_gdf = gdf[nearby_mask].copy()
        
        return nearby_gdf

    def filter_by_distance_with_fallback(self, gdf, center_point, max_distance_km=10.0):
        """Filter with automatic radius expansion if no results"""
        result = self.filter_by_distance(gdf, center_point, max_distance_km)
        
        # If empty, try larger radius
        if result.empty and max_distance_km < 20:
            print(f"⚠️ No results within {max_distance_km}km, trying {max_distance_km*2}km...")
            return self.filter_by_distance_with_fallback(gdf, center_point, max_distance_km*2)
        
        return result

    def find_nearest_emission_for_location(self, location_row, emission_gdf):
        """Find the nearest emission record for a given location"""
        location_point = location_row.geometry.centroid
        location_proj = gpd.GeoSeries([location_point], crs='EPSG:4326').to_crs('EPSG:3857').iloc[0]
        
        # Project emission data for distance calculation
        emission_proj = emission_gdf.to_crs('EPSG:3857')
        
        # Calculate distances to emissions
        distances_to_emissions = emission_proj.geometry.distance(location_proj)
        nearest_idx = distances_to_emissions.idxmin()
        nearest_emission = emission_gdf.loc[nearest_idx]
        
        return nearest_emission

    def execute_spatial_analysis(self):
        # ... existing code ...
        
        # Use the updated distance filtering with fallback
        nearby_buildings = self.filter_by_distance_with_fallback(residential_buildings, barceloneta_center)
        nearby_emissions = self.filter_by_distance_with_fallback(emission_gdf, barceloneta_center)
        
        # Use nearest neighbor matching
        results_list = []
        for idx, building in nearby_buildings.iterrows():
            nearest_emission = self.find_nearest_emission_for_location(building, nearby_emissions)
            
            # Create result entry
            building_type = building.get('building', 'residential')
            emission_level = nearest_emission.get('Rang', 'Unknown')
            name = f"Building (Type: {building_type} - Emission: {emission_level})"
            
            results_list.append({
                'name': name,
                'longitude': building.geometry.centroid.x,
                'latitude': building.geometry.centroid.y
            })
        
        # Create final results DataFrame
        result = pd.DataFrame(results_list)
        
        # Save results
        result.to_csv('final_results.csv', index=False)
        print(f"\n🎉 SUCCESS: Generated {len(result)} results!")
        
        return result
