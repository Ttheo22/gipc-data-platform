import os

files = [
    'extractors/domestic_sources.py',
    'extractors/world_bank_governance.py',
    'extractors/world_bank.py',
]

old = 'logging.FileHandler("pipeline.log", encoding="utf-8")'
new = ('logging.FileHandler('
       '"/tmp/pipeline.log" if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") '
       'else "pipeline.log", encoding="utf-8")')

for filepath in files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if old in content:
            content = content.replace(old, new)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Fixed: {filepath}')
        else:
            print(f'Not found in: {filepath}')
    except FileNotFoundError:
        print(f'File not found: {filepath}')
