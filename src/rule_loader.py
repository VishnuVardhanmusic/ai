import json
import os

def loadGuidelines(jsonPath):
    """
    Loads guideline rules from the given JSON file path.

    Args:
        jsonPath (str): Path to the guideline JSON file.

    Returns:
        List[Dict]: A list of guideline dictionaries.
    """
    if not os.path.exists(jsonPath):
        raise FileNotFoundError(f"Guidelines file not found: {jsonPath}")

    with open(jsonPath, 'r') as file:
        try:
            guidelines = json.load(file)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in guidelines file.")
    
    return guidelines
