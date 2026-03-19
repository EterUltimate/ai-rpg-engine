#!/usr/bin/env python3
"""修复 setup.py 中的 Unicode 字符"""
import re

file_path = 'scripts/setup.py'

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all problematic Unicode characters
replacements = {
    '✓': '[OK]',
    '✗': '[X]',
    '⚠': '[!]',
    'ℹ': '[i]',
    '✅': '[SUCCESS]',
    '❌': '[ERROR]',
    '⚠️': '[WARNING]',
    '•': '-',
}

for old, new in replacements.items():
    content = content.replace(old, new)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed all Unicode characters in setup.py')
