import importlib, time, sys, traceback, os

print("cwd:", os.getcwd())
print("Python:", sys.executable)
print()

def try_import(name):
    t0 = time.time()
    try:
        m = importlib.import_module(name)
        dt = time.time() - t0
        print(f"OK import {name} ({dt:.2f}s)")
    except Exception as e:
        dt = time.time() - t0
        print(f"ERREUR import {name} after {dt:.2f}s")
        traceback.print_exc()
    print("-" * 60)

modules = [
    "backend.core.rag",
    "backend.core.emotion",
    "backend.core.groq",
    "backend.core.agents",
    "backend.app",
]

for mod in modules:
    try_import(mod)