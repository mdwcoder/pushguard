#!/usr/bin/env bash
set -euo pipefail

# init.sh - installer for pushguard
# - prefers pipx if available
# - otherwise creates a per-user venv at ~/.local/pushguard/venv
# - ensures ~/.local/bin is on PATH for bash/zsh and adds a short alias `pg`

echo "==> Initializing pushguard installer"

repo_root="$(pwd)"

command_exists() { command -v "$1" >/dev/null 2>&1; }

die() { echo "Error: $*" >&2; exit 2; }

# flags
ALIAS_NAME="pushg"
NO_ALIAS=false

while [ "$#" -gt 0 ]; do
	case "$1" in
		--no-alias)
			NO_ALIAS=true
			shift
			;;
		*)
			echo "Unknown option: $1" >&2
			exit 2
			;;
	esac
done

# 1) Prerequisites
if ! command_exists git; then
	die "git is required but not found in PATH. Install git and retry."
fi

if command_exists python3; then
	py_cmd=python3
elif command_exists python; then
	py_cmd=python
else
	die "python3 is required but not found in PATH. Install Python and retry."
fi

# 2) Ensure we're in a git repository root
if [ ! -d "$repo_root/.git" ]; then
	echo "Please run init.sh from the repository root of pushguard." >&2
	echo "If you cloned elsewhere, cd into the cloned repo root and re-run: bash init.sh" >&2
	exit 2
fi

echo "Detected Python: $($py_cmd --version 2>/dev/null)"

# location for user binaries
local_bin="$HOME/.local/bin"
venv_dir="$HOME/.local/pushguard/venv"

install_with_pipx() {
	echo "-> Installing with pipx..."
	if ! command_exists pipx; then
		return 1
	fi
	pipx install --force . && return 0 || return 1
}

install_with_venv() {
	echo "-> Installing with per-user venv at $venv_dir"
	mkdir -p "$(dirname "$venv_dir")"
	"$py_cmd" -m venv "$venv_dir"
	# shellcheck disable=SC1090
	source "$venv_dir/bin/activate"
	python -m pip install -U pip
	python -m pip install -U .

	# ensure ~/.local/bin exists
	mkdir -p "$local_bin"

	# symlink the installed entrypoint to ~/.local/bin/pushguard
	if [ -f "$venv_dir/bin/pushguard" ]; then
		ln -sf "$venv_dir/bin/pushguard" "$local_bin/pushguard"
	else
		echo "Warning: pushguard entrypoint not found in venv. Check installation." >&2
	fi
}

echo "Repository root: $repo_root"

# Try pipx first
if install_with_pipx; then
	echo "Installed pushguard with pipx."
else
	echo "pipx not available or failed; falling back to per-user venv.";
	install_with_venv
fi

# 3) Ensure ~/.local/bin is on PATH for common shells
add_path_rc() {
	rcfile="$1"
	line="export PATH=\"$HOME/.local/bin:\$PATH\""
	if [ -f "$rcfile" ]; then
		if ! grep -qxF "$line" "$rcfile" 2>/dev/null; then
			echo "$line" >> "$rcfile"
			echo "Added $local_bin to PATH in $rcfile"
		fi
	else
		echo "$line" >> "$rcfile"
		echo "Created $rcfile and added $local_bin to PATH"
	fi
}

add_alias_rc() {
	rcfile="$1"
	alias_line="alias ${ALIAS_NAME}='pushguard'"
	if [ -f "$rcfile" ]; then
		if ! grep -qxF "$alias_line" "$rcfile" 2>/dev/null; then
			echo "$alias_line" >> "$rcfile"
			echo "Added alias ${ALIAS_NAME} to $rcfile"
		fi
	else
		echo "$alias_line" >> "$rcfile"
		echo "Created $rcfile and added alias ${ALIAS_NAME}"
	fi
}

shell_name="$(basename "${SHELL:-}")"
echo "Detected shell: ${shell_name:-unknown}"

case "$shell_name" in
		bash)
		add_path_rc "$HOME/.bashrc"
		if [ "$NO_ALIAS" = false ]; then add_alias_rc "$HOME/.bashrc"; fi
		;;
	zsh)
		add_path_rc "$HOME/.zshrc"
		if [ "$NO_ALIAS" = false ]; then add_alias_rc "$HOME/.zshrc"; fi
		;;
	fish)
		# fish uses fish_user_paths and config.fish
		mkdir -p "$HOME/.config/fish"
		fish_config="$HOME/.config/fish/config.fish"
		if ! grep -q "$local_bin" "$fish_config" 2>/dev/null; then
			echo "set -gx PATH $local_bin \$PATH" >> "$fish_config"
			echo "Added $local_bin to fish PATH via $fish_config"
		fi
		if [ "$NO_ALIAS" = false ]; then
			if ! grep -q "function ${ALIAS_NAME}" "$fish_config" 2>/dev/null; then
				cat >> "$fish_config" <<FISH_ALIAS
function ${ALIAS_NAME}
	pushguard \$argv
end
FISH_ALIAS
				echo "Added ${ALIAS_NAME} function to fish config"
			fi
		fi
		;;
	*)
		if [ "$NO_ALIAS" = false ]; then
			echo "Shell not explicitly supported. Please ensure $local_bin is in your PATH and add an alias: 'alias ${ALIAS_NAME}=\'pushguard\'' to your shell rc." >&2
		else
			echo "Shell not explicitly supported. Please ensure $local_bin is in your PATH." >&2
		fi
		;;
esac

# 4) Create .pushguard dirs (do not add to git)
mkdir -p "$repo_root/.pushguard/reports"
echo "Created .pushguard and .pushguard/reports (no git changes made)."

echo "==> Done. Open a new terminal or source your rc file (e.g. 'source ~/.bashrc' or 'source ~/.zshrc')."
echo "Try: pushguard --help"
if [ "$NO_ALIAS" = false ]; then
	echo "You can also use the short alias: ${ALIAS_NAME} --help"
fi
echo ""
exit 0