#!/usr/bin/env bash
# Batch: convert + repair-build the 5 test projects, capture first-pass results.
set +e
cd "D:/claudecli/android2harmony-mvp" || exit 1
RESULTS="D:/codex/out/test5/results.jsonl"
mkdir -p "D:/codex/out/test5"
: > "$RESULTS"

declare -A PROJ=(
  [JetpackMVVM]="D:/codex/android-benchmarks/test5/JetpackMVVM"
  [WanAndroidGoweii]="D:/codex/android-benchmarks/test5/WanAndroidGoweii"
  [PlayAndroid]="D:/codex/android-benchmarks/test5/PlayAndroid"
  [KingTV]="D:/codex/android-benchmarks/test5/KingTV"
  [YCVideoPlayer]="D:/codex/android-benchmarks/test5/YCVideoPlayer"
)
ORDER=(JetpackMVVM WanAndroidGoweii PlayAndroid KingTV YCVideoPlayer)

for name in "${ORDER[@]}"; do
  src="${PROJ[$name]}"
  out="D:/codex/out/test5/$name"
  echo "########## [$name] convert ##########"
  python -m android2harmony.cli convert "$src" -o "$out" --force --llm-refine-pages > "D:/codex/out/test5/$name.convert.log" 2>&1
  conv_exit=$?
  echo "########## [$name] repair-build ##########"
  python -m android2harmony.cli repair-build "$out" --max-iters 5 > "D:/codex/out/test5/$name.repair.log" 2>&1
  rep_exit=$?
  # extract the json result block from repair log
  python - "$name" "$conv_exit" "$rep_exit" "D:/codex/out/test5/$name.repair.log" "$RESULTS" <<'PY'
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
done
echo "ALL DONE"
