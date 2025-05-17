import json
import os
import sys

def compile_template(template_path):
    scope = {}
    with open(template_path, "r") as f:
        exec(f.read(), {}, scope)
    cue_data = scope["cue_data"]
    output_path = template_path.replace(".cue_template.py", ".cue.json")

    cues = [(entry["time"], entry["channels"]) for entry in cue_data["cues"]]
    with open(output_path, "w") as f:
        json.dump(cues, f, indent=2)

    print(f"✅ Compiled cue JSON written to: {output_path}")

if __name__ == "__main__":
    path = sys.argv[1]
    compile_template(path)