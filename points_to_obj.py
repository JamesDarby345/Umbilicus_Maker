import json
import os
from pathlib import Path
import argparse

def json_to_obj(json_path):
    # Create output directory if it doesn't exist
    output_dir = Path('umbilicus_obj')
    output_dir.mkdir(exist_ok=True)
    
    # Load points from json
    with open(json_path, 'r') as f:
        points = json.load(f)
    
    # Create output filename
    output_name = output_dir / (Path(json_path).stem + '.obj')
    
    # Write obj file
    with open(output_name, 'w') as f:
        # Write vertices
        for i, (z, y, x) in enumerate(points, 1):
            f.write(f'v {z} {y} {x}\n')
        
        # Write edges connecting consecutive points
        for i in range(1, len(points)):
            f.write(f'l {i} {i+1}\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert umbilicus points JSON to OBJ file')
    parser.add_argument('json_name', nargs='?', help='Name of the JSON file in the umbilicus_points folder')
    
    args = parser.parse_args()
    if args.json_name:
        json_path = os.path.join(os.getcwd(), 'umbilicus_points', args.json_name)
        json_to_obj(json_path)
    else:
        umbilicus_dir = os.path.join(os.getcwd(), 'umbilicus_points')
        for file in os.listdir(umbilicus_dir):
            if file.endswith('.json'):
                json_path = os.path.join(umbilicus_dir, file)
                json_to_obj(json_path)
