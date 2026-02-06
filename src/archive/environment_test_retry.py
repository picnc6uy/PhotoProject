import os

def test_environment():
    print("** Testing Environment **")

    # Test working directory
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")

    # Test file creation
    test_file = "environment_test_output.txt"
    try:
        with open(test_file, "w") as f:
            f.write("Environment test successful.\n")
        print(f"File {test_file} created successfully.")
    except Exception as e:
        print(f"Failed to create file {test_file}: {e}")

    # Test reading file
    try:
        with open(test_file, "r") as f:
            content = f.read()
        print("File read successfully. Content:")
        print(content)
    except Exception as e:
        print(f"Failed to read file {test_file}: {e}")

if __name__ == "__main__":
    test_environment()