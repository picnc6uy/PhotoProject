import ast
import os
import shutil

# Active tests and scripts critical for execution
ACTIVE_TESTS = {
    'test_image_processor.py',
    'test_ocr_service.py',
    'test_ocr_to_parser.py',
    'test_enrich_consolidated.py',
    'compare_ocr_vs_enriched.py'
}

TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
ARCHIVE_DIR = os.path.join(TESTS_DIR, 'archive')

os.makedirs(ARCHIVE_DIR, exist_ok=True)

# Files to definitely keep: Active tests + their direct imports
keep_files = set(ACTIVE_TESTS)

# Support function to find imports in a Python file

def find_imports(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        node = ast.parse(f.read(), file_path)
    imports = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Import):
            for n in child.names:
                imports.add(n.name + '.py')
        elif isinstance(child, ast.ImportFrom):
            if child.module:
                imports.add(child.module.replace('.', '/') + '.py')
    return imports

# Collect imported files from active tests
for test_file in ACTIVE_TESTS:
    full_path = os.path.join(TESTS_DIR, test_file)
    imports = find_imports(full_path)
    # We only consider direct python files in tests dir
    for imp in imports:
        imp_name = os.path.basename(imp)
        if os.path.isfile(os.path.join(TESTS_DIR, imp_name)):
            keep_files.add(imp_name)

# Archive files that are not in keep_files and are .py files
archived_files = []
for file in os.listdir(TESTS_DIR):
    if file.endswith('.py') and file != 'archive_unused_tests.py' and file not in keep_files:
        source = os.path.join(TESTS_DIR, file)
        destination = os.path.join(ARCHIVE_DIR, file)
        print(f"Archiving {file} to archive/")
        shutil.move(source, destination)
        archived_files.append(file)

print(f"Archiving completed. {len(archived_files)} files moved to archive.")
