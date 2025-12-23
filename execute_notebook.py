"""
Execute Jupyter notebook and export to HTML
"""
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter
from pathlib import Path

# Paths
notebook_path = Path('notebooks/eda_milestone1.ipynb')
output_notebook_path = Path('notebooks/eda_milestone1_executed.ipynb')
output_html_path = Path('notebooks/eda_milestone1.html')

print(f"Executing notebook: {notebook_path}")

# Read notebook
with open(notebook_path) as f:
    nb = nbformat.read(f, as_version=4)

# Execute notebook
ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
try:
    ep.preprocess(nb, {'metadata': {'path': 'notebooks/'}})
    print("✓ Notebook executed successfully")
except Exception as e:
    print(f"Warning: Some cells may have failed: {e}")

# Save executed notebook
with open(output_notebook_path, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)
print(f"✓ Executed notebook saved: {output_notebook_path}")

# Export to HTML
html_exporter = HTMLExporter()
html_exporter.template_name = 'classic'
(body, resources) = html_exporter.from_notebook_node(nb)

with open(output_html_path, 'w', encoding='utf-8') as f:
    f.write(body)
print(f"✓ HTML export saved: {output_html_path}")

print("\n" + "="*60)
print("NOTEBOOK EXECUTION COMPLETE")
print("="*60)
print(f"Files created:")
print(f"  - {output_notebook_path}")
print(f"  - {output_html_path}")
print(f"  - Figures saved to: docs/figs/")
