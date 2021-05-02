import json
import os

if __name__ == "__main__":
    notebooks = sorted([f for f in os.listdir() if f.endswith("ipynb")])
    for nb in notebooks:
        with open(nb) as f:
            data = json.load(f)
        for cell in data["cells"]:
            if cell["cell_type"] == "code":
                cell["metadata"] = {}
        with open(nb, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
