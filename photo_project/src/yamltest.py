import yaml

# Function to load and process a YAML file
def process_yaml(file_path):
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            print("YAML content loaded successfully:")
            print(data)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except yaml.YAMLError as e:
        print(f"Error: Unable to parse YAML file. Details: {e}")

# Path to the YAML file (update this with your file's path)
yaml_file_path = 'C:\\Users\\ghendrick\\.continue\\src\\example.yaml'  # Replace with the actual path if needed

# Process the YAML file
process_yaml(yaml_file_path)