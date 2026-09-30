import json

p = r'C:\Users\Navin D\.gemini\antigravity\brain\a0dd4a19-3810-4e87-8456-3eeb28017a63\.system_generated\logs\transcript_full.jsonl'

found_code = None
with open(p, "r", encoding="utf-8") as f:
    for line in f:
        if "server.py" in line and ("write_to_file" in line or "replace_file_content" in line or "CodeContent" in line):
            try:
                obj = json.loads(line)
                # check tool calls
                calls = obj.get("tool_calls", [])
                for c in calls:
                    args = c.get("parameters", {})
                    if "server.py" in str(args.get("TargetFile", "")):
                        if "CodeContent" in args and len(args["CodeContent"]) > 10000:
                            found_code = args["CodeContent"]
                            print("Found write_to_file code of len:", len(found_code))
            except Exception as e:
                pass

if found_code:
    with open("restored_server.py", "w", encoding="utf-8") as out:
        out.write(found_code)
    print("Saved to restored_server.py!")
else:
    print("CodeContent not found directly, checking other steps...")
