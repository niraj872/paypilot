from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
checks = []
required = [
    'README.md', 'LICENSE', 'docker-compose.yml', 'render.yaml',
    'backend/app/main.py', 'backend/app/payments/paypal_service.py',
    'backend/app/payments/policy.py', 'frontend/package.json',
    'frontend/src/App.tsx', 'frontend/src/components/TransactionGrid.tsx'
]
for rel in required:
    ok = (ROOT / rel).exists()
    checks.append((rel, ok))

print('PAYPILOT AUDIT')
print('=' * 60)
for name, ok in checks:
    print(f"{'PASS' if ok else 'FAIL':4} {name}")

if (ROOT / 'backend').exists():
    result = subprocess.run([sys.executable, '-m', 'pytest', 'backend/tests'], cwd=ROOT, capture_output=True, text=True)
    print('\nBackend tests:')
    print(result.stdout.strip() or result.stderr.strip())
    checks.append(('backend tests', result.returncode == 0))

secret_candidates = [p for p in ROOT.rglob('.env') if '.venv' not in p.parts and 'node_modules' not in p.parts] + [p for p in ROOT.rglob('*.pem') if '.venv' not in p.parts and 'node_modules' not in p.parts]
secret_ok = len(secret_candidates) == 0
checks.append(('no committed secret files', secret_ok))
print(f"{'PASS' if secret_ok else 'FAIL':4} no committed secret files")

print('\nFINAL:', 'PASS' if all(ok for _, ok in checks) else 'FAIL')
sys.exit(0 if all(ok for _, ok in checks) else 1)
