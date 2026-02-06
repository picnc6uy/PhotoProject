import yaml
import os

def yaml_file_test():
    print("** YAML File Parsing Test **")

    # Path to the YAML file
    yaml_file_path = "src/example.yaml"

    if not os.path.exists(yaml_file_path):
        print(f"Error: YAML file not found at {yaml_file_path}")
        return

    # Read and parse the YAML file
    try:
        with open(yaml_file_path, "r") as yaml_file:
            parsed_data = yaml.safe_load(yaml_file)
            print("Successfully parsed YAML content:")
            print(parsed_data)
    except yaml.YAMLError as e:
        print(f"YAML parsing error: {e}")

if __name__ == "__main__":
    yaml_file_test()