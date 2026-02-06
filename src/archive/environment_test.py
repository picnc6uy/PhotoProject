import os

def environment_test():
    print("** Python Environment Test **")

    # Get and print the current working directory
    print("Current working directory:", os.getcwd())

    # Test file creation
    test_file_path = "test_env_file.txt"
    try:
        with open(test_file_path, "w") as f:
            f.write("Python environment is working correctly.\n")
        print(f"Successfully created file: {test_file_path}")
    except Exception as e:
        print(f"Error creating file: {e}")

    # Test reading the file
    try:
        with open(test_file_path, "r") as f:
            content = f.read()
        print(f"Successfully read file. Content:\n{content}")
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    environment_test()