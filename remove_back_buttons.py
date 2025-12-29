import re

files = [
    r'd:\Mind\frontend\app\transactions\page.tsx',
    r'd:\Mind\frontend\app\alerts\page.tsx',
    r'd:\Mind\frontend\app\analytics\page.tsx',
    r'd:\Mind\frontend\app\model-performance\page.tsx'
]

pattern = r'<Link\s+href="/"\s+className="[^"]*"[^>]*>\s*<ArrowLeft[^>]*\/>\s*Back to Dashboard\s*<\/Link>'

for filepath in files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove the back button link
        updated = re.sub(pattern, '', content, flags=re.DOTALL)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated)
        
        print(f"✓ Updated {filepath}")
    except Exception as e:
        print(f"✗ Error with {filepath}: {e}")

print("\nDone!")
