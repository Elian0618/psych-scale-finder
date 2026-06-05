#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/Elian0618/psych-scale-finder.git"
CNKI_REPO_URL="https://github.com/cookjohn/cnki-skills.git"

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILLS_DIR="$CODEX_HOME/skills"
AGENTS_DIR="$CODEX_HOME/agents"
CONFIG_FILE="$CODEX_HOME/config.toml"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

need_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1"
    return 1
  fi
}

copy_dir() {
  local src="$1"
  local dst="$2"
  local abs_src
  local abs_dst=""
  abs_src="$(cd "$src" && pwd)"
  if [ -d "$dst" ]; then
    abs_dst="$(cd "$dst" && pwd)"
  fi
  if [ "$abs_src" = "$abs_dst" ]; then
    echo "Source already installed at $dst"
    return 0
  fi
  rm -rf "$dst"
  mkdir -p "$(dirname "$dst")"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --exclude ".git" "$src/" "$dst/"
  else
    cp -R "$src" "$dst"
    rm -rf "$dst/.git"
  fi
}

install_chrome_devtools_mcp() {
  mkdir -p "$CODEX_HOME"
  touch "$CONFIG_FILE"

  if grep -q '^\[mcp_servers\.chrome-devtools\]' "$CONFIG_FILE"; then
    echo "chrome-devtools MCP already exists in $CONFIG_FILE"
    return 0
  fi

  cp "$CONFIG_FILE" "$CONFIG_FILE.bak-psych-scale-finder-$(date +%Y%m%d%H%M%S)"
  cat >>"$CONFIG_FILE" <<'EOF'

[mcp_servers.chrome-devtools]
command = "npx"
args = ["-y", "chrome-devtools-mcp@latest"]
startup_timeout_sec = 120
EOF

  echo "Added chrome-devtools MCP config to $CONFIG_FILE"
}

echo "Installing Psych Scale Finder for Codex..."

need_command git

mkdir -p "$SKILLS_DIR" "$AGENTS_DIR"

if [ -f "$SCRIPT_DIR/SKILL.md" ]; then
  PSYCH_SRC="$SCRIPT_DIR"
else
  echo "Current folder does not contain SKILL.md; cloning $REPO_URL"
  git clone "$REPO_URL" "$TMP_DIR/psych-scale-finder"
  PSYCH_SRC="$TMP_DIR/psych-scale-finder"
fi

copy_dir "$PSYCH_SRC" "$SKILLS_DIR/psych-scale-finder"
echo "Installed psych-scale-finder -> $SKILLS_DIR/psych-scale-finder"

echo "Installing CNKI dependency skills..."
git clone "$CNKI_REPO_URL" "$TMP_DIR/cnki-skills"

if [ -d "$TMP_DIR/cnki-skills/skills" ]; then
  for skill_dir in "$TMP_DIR/cnki-skills"/skills/*; do
    [ -d "$skill_dir" ] || continue
    name="$(basename "$skill_dir")"
    copy_dir "$skill_dir" "$SKILLS_DIR/$name"
    echo "Installed CNKI skill -> $SKILLS_DIR/$name"
  done
else
  echo "CNKI skills folder not found in cloned repository."
  exit 1
fi

if [ -d "$TMP_DIR/cnki-skills/agents" ]; then
  mkdir -p "$AGENTS_DIR"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a "$TMP_DIR/cnki-skills/agents/" "$AGENTS_DIR/"
  else
    cp -R "$TMP_DIR/cnki-skills/agents/." "$AGENTS_DIR/"
  fi
  echo "Copied CNKI agents -> $AGENTS_DIR"
fi

install_chrome_devtools_mcp

cat <<EOF

Done.

Next steps:
1. Restart Codex or open a new thread so skills and MCP config refresh.
2. Make sure Chrome is available.
3. Log in to CNKI manually in Chrome when the skill asks you to.
4. If CNKI shows a captcha, solve it manually in Chrome.

Verify in a new Codex thread:
[$psych-scale-finder] 帮我找一个中文心理量表，并先检查 CNKI 访问状态

EOF
