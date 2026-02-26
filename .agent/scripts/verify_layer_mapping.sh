#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
# verify_layer_mapping.sh — L1↔L2↔L3 3계층 매핑 검증 스크립트
# Usage: bash .agent/scripts/verify_layer_mapping.sh
# ═══════════════════════════════════════════════════════════
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CMD_DIR="$ROOT/.claude/commands"
AGT_DIR="$ROOT/.claude/agents"
WF_DIR="$ROOT/.agent/workflows"

ERRORS=0
WARNINGS=0

echo "═══════════════════════════════════════════════"
echo " L1↔L2↔L3 3계층 매핑 검증"
echo " $(date '+%Y-%m-%d %H:%M:%S')"
echo "═══════════════════════════════════════════════"
echo ""

# ── Check 1: L1 커맨드 → L2 서브에이전트 연결 ──
echo "▶ Check 1: L1 커맨드 → L2 서브에이전트 연결"
for cmd_file in "$CMD_DIR"/*.md; do
  cmd_name=$(basename "$cmd_file" .md)
  # Extract subagent_type from Task() call
  subagent=$(grep -oE 'subagent_type="[^"]+"' "$cmd_file" 2>/dev/null | head -1 | sed 's/subagent_type="//;s/"//')
  if [ -z "$subagent" ]; then
    echo "  ✗ $cmd_name: Task(subagent_type=...) 패턴 없음"
    ((ERRORS++)) || true
    continue
  fi
  agent_file="$AGT_DIR/$subagent.md"
  if [ -f "$agent_file" ]; then
    echo "  ✓ $cmd_name → $subagent.md"
  else
    echo "  ✗ $cmd_name → $subagent.md (파일 없음!)"
    ((ERRORS++)) || true
  fi
done
echo ""

# ── Check 2: L2 서브에이전트 → L3 워크플로우 SSOT 연결 ──
echo "▶ Check 2: L2 서브에이전트 → L3 워크플로우 SSOT 연결"
for agt_file in "$AGT_DIR"/*.md; do
  agt_name=$(basename "$agt_file" .md)
  # Extract workflow path from SSOT annotation
  ssot=$(grep -oE '\.agent/workflows/[^ \`]+\.yaml' "$agt_file" 2>/dev/null | head -1)
  if [ -z "$ssot" ]; then
    echo "  ⚠ $agt_name: SSOT 주석 없음"
    ((WARNINGS++)) || true
    continue
  fi
  wf_path="$ROOT/$ssot"
  if [ -f "$wf_path" ]; then
    echo "  ✓ $agt_name → $ssot"
  else
    echo "  ✗ $agt_name → $ssot (파일 없음!)"
    ((ERRORS++)) || true
  fi
done
echo ""

# ── Check 3: L2 프론트매터 name 필드 일치 검증 ──
echo "▶ Check 3: L2 프론트매터 name 필드 ↔ 파일명 일치"
for agt_file in "$AGT_DIR"/*.md; do
  agt_name=$(basename "$agt_file" .md)
  # Extract name from frontmatter
  fm_name=$(awk '/^---$/{c++; next} c==1 && /^name:/{sub(/^name: */,""); print; exit}' "$agt_file" 2>/dev/null)
  if [ -z "$fm_name" ]; then
    echo "  ⚠ $agt_name: 프론트매터 name 필드 없음"
    ((WARNINGS++)) || true
  elif [ "$fm_name" = "$agt_name" ]; then
    echo "  ✓ $agt_name = $fm_name"
  else
    echo "  ✗ 파일명=$agt_name ≠ 프론트매터=$fm_name"
    ((ERRORS++)) || true
  fi
done
echo ""

# ── Check 4: L1 커맨드 크기 정규화 (29~45줄) ──
echo "▶ Check 4: L1 커맨드 크기 (29~45줄 표준)"
for cmd_file in "$CMD_DIR"/*.md; do
  cmd_name=$(basename "$cmd_file" .md)
  lines=$(wc -l < "$cmd_file" | tr -d ' ')
  if [ "$lines" -ge 29 ] && [ "$lines" -le 45 ]; then
    echo "  ✓ $cmd_name: ${lines}줄"
  else
    echo "  ⚠ $cmd_name: ${lines}줄 (표준 범위 29~45 초과)"
    ((WARNINGS++)) || true
  fi
done
echo ""

# ── Check 5: L2 서브에이전트 크기 정규화 (35~55줄) ──
echo "▶ Check 5: L2 서브에이전트 크기 (35~55줄 표준)"
for agt_file in "$AGT_DIR"/*.md; do
  agt_name=$(basename "$agt_file" .md)
  lines=$(wc -l < "$agt_file" | tr -d ' ')
  if [ "$lines" -ge 35 ] && [ "$lines" -le 55 ]; then
    echo "  ✓ $agt_name: ${lines}줄"
  else
    echo "  ⚠ $agt_name: ${lines}줄 (표준 범위 35~55 초과)"
    ((WARNINGS++)) || true
  fi
done
echo ""

# ── Check 6: L3 워크플로우 역방향 참조 (고아 검증) ──
echo "▶ Check 6: L3 워크플로우 역방향 참조 (L2에서 참조되는지)"
for wf_file in "$WF_DIR"/*.yaml; do
  wf_name=$(basename "$wf_file")
  wf_rel=".agent/workflows/$wf_name"
  found=$(grep -rl "$wf_rel" "$AGT_DIR" 2>/dev/null | head -1 || true)
  if [ -n "$found" ]; then
    echo "  ✓ $wf_name ← $(basename "$found" .md)"
  else
    echo "  ⚠ $wf_name: L2에서 참조 없음 (고아 워크플로우)"
    ((WARNINGS++)) || true
  fi
done
echo ""

# ── Check 7: L1↔L2 subagent_type 교차 검증 ──
echo "▶ Check 7: L2 서브에이전트 ↔ L1 커맨드 역방향 참조"
for agt_file in "$AGT_DIR"/*.md; do
  agt_name=$(basename "$agt_file" .md)
  found=$(grep -rl "subagent_type=\"$agt_name\"" "$CMD_DIR" 2>/dev/null | head -1 || true)
  if [ -n "$found" ]; then
    echo "  ✓ $agt_name ← $(basename "$found" .md)"
  else
    echo "  ⚠ $agt_name: L1에서 참조 없음 (고아 서브에이전트)"
    ((WARNINGS++)) || true
  fi
done
echo ""

# ── 결과 요약 ──
echo "═══════════════════════════════════════════════"
echo " 결과: 에러 ${ERRORS}건, 경고 ${WARNINGS}건"
echo "═══════════════════════════════════════════════"

if [ "$ERRORS" -gt 0 ]; then
  echo "❌ 검증 실패 — 에러를 수정하세요."
  exit 1
else
  if [ "$WARNINGS" -gt 0 ]; then
    echo "⚠️ 검증 통과 (경고 ${WARNINGS}건 확인 필요)"
  else
    echo "✅ 검증 통과 — 모든 연결 정상"
  fi
  exit 0
fi
