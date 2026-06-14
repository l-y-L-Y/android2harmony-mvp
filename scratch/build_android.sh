#!/usr/bin/env bash
# Build debug APKs for the pure-JVM Android originals (no arm-only native libs),
# so they install on the x86_64 emulator for side-by-side comparison.
set +e
export JAVA_HOME="D:/jdk17/jdk-17.0.19+10"
export ANDROID_HOME="D:/Android/Sdk"
export GRADLE_USER_HOME="D:/gradle-home"
OUT="D:/codex/out/test5/_android"
mkdir -p "$OUT"
LOG="$OUT/build.log"
: > "$LOG"

build() {  # name dir
  local name="$1" dir="$2"
  echo "########## [$name] assembleDebug ##########" | tee -a "$LOG"
  ( cd "$dir" && cmd.exe /c "gradlew.bat assembleDebug --no-daemon --init-script D:\\gradle-home\\init.gradle -x lint -x test" ) >> "$LOG" 2>&1
  echo "[$name] gradle exit=$?" | tee -a "$LOG"
  find "$dir" -path '*/outputs/apk/debug/*.apk' 2>/dev/null | head -3 | tee -a "$LOG"
}

build JetpackMVVM     "D:/codex/android-benchmarks/test5/JetpackMVVM"
build WanAndroidGoweii "D:/codex/android-benchmarks/test5/WanAndroidGoweii"
echo "ANDROID BUILD DONE" | tee -a "$LOG"
