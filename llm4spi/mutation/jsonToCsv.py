import os
import json
import csv
import sys


def extract_success_rate(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            success_rate = data.get("summary", {}).get("success_rate", "N/A")
            if isinstance(success_rate, (int, float)):
                return f"{success_rate * 100:.2f}%"
            return "N/A"
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading {json_path}: {e}")
        return "N/A"

def process_folders(root_folder, output_csv):
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["problem", "base0", "base1", "validation"])  # Header row
        
        for folder in os.listdir(root_folder):
            folder_path = os.path.join(root_folder, folder)
            if os.path.isdir(folder_path):
                base0_path = os.path.join(folder_path, f"{folder}_base0.json")
                base1_path = os.path.join(folder_path, f"{folder}_base1.json")
                validation_path = os.path.join(folder_path, f"{folder}_validation.json")
                
                base0_rate = extract_success_rate(base0_path)
                base1_rate = extract_success_rate(base1_path)
                validation_rate = extract_success_rate(validation_path)
                
                writer.writerow([folder, base0_rate, base1_rate, validation_rate])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("You have to specify the path to the mutation report folder")
        exit(1)
    report_directory = sys.argv[1]
    output_file = "output.csv"
    process_folders(report_directory, output_file)
    print(f"CSV file created: {output_file}")