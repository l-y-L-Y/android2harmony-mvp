#!/usr/bin/env bash
# Finish the batch with the @Entry-fixed transpiler:
#   WanAndroidGoweii: full re-convert + repair (old output had the @Entry bug baked in)
#   YCVideoPlayer:    convert + repair (never ran)
#   KingTV:           repair-build only (convert already done; validates self-heal path)
set +e
cd "D:/claudecli/android2harmony-mvp" || exit 1
OUT="D:/codex/out/test5"
RESULTS="$OUT/results_rest.jsonl"
: > "$RESULTS"

record() {  # name conv rep replog
  python - "$1" "$2" "$3" "$4" "$RESULTS" <<'PY'
import json,sys,re
name,conv,rep,replog,results=sys.argv[1:6]
txt=open(replog,encoding="utf-8",errors="ignore").read()
m=re.search(r'\{[^{}]*"passed"[\s\S]*?\}', txt)
data={}
if m:
    try: data=json.loads(m.group(0))
    except Exception: pass
row={"name":name,"convertExit":int(conv),"repairExit":int(rep),
     "passed":data.get("passed"),"iterations":data.get("iterations"),
     "initialErrors":data.get("initialErrors"),"finalErrors":data.get("finalErrors")}
open(results,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n")
print("RESULT",json.dumps(row,ensure_ascii=False))
PY
}

# 1) WanAndroidGoweii: fresh convert + repair
name=WanAndroidGoweii; src="D:/codex/android-benchmarks/test5/$name"; out="$OUT/$name"
echo "########## [$name] convert ##########"
python -m android2harmony.cli convert "$src" -o "$out" --force --llm-refine-pages > "$OUT/$name.convert.log" 2>&1; cexit=$?
echo "########## [$name] repair-build ##########"
python -m android2harmony.cli repair-build "$out" --max-iters 5 > "$OUT/$name.repair.log" 2>&1; rexit=$?
record "$name" "$cexit" "$rexit" "$OUT/$name.repair.log"

# 2) YCVideoPlayer: fresh convert + repair
name=YCVideoPlayer; src="D:/codex/android-benchmarks/test5/$name"; out="$OUT/$name"
echo "########## [$name] convert ##########"
python -m android2harmony.cli convert "$src" -o "$out" --force --llm-refine-pages > "$OUT/$name.convert.log" 2>&1; cexit=$?
echo "########## [$name] repair-build ##########"
python -m android2harmony.cli repair-build "$out" --max-iters 5 > "$OUT/$name.repair.log" 2>&1; rexit=$?
record "$name" "$cexit" "$rexit" "$OUT/$name.repair.log"

# 3) KingTV: repair-build only (convert already produced output)
name=KingTV; out="$OUT/$name"
echo "########## [$name] repair-build (existing convert) ##########"
python -m android2harmony.cli repair-build "$out" --max-iters 5 > "$OUT/$name.repair.log" 2>&1; rexit=$?
record "$name" 0 "$rexit" "$OUT/$name.repair.log"

echo "ALL REST DONE"
