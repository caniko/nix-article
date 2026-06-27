# Plugin System

## Convention

A plugin is an executable binary named `anx-plugin-<name>` discovered on
`$PATH`. When invoked, anx passes a JSON context object via `--plugin-context`
and reads a JSON result from stdout.

## Protocol

### Invocation

```console
anx-plugin-<name> --plugin-context '<json>'
```

### Input JSON

```json
{
  "action": "string",
  "paths": {},
  "metadata": {}
}
```

| Field      | Type     | Description                        |
| ---------- | -------- | ---------------------------------- |
| `action`   | `string` | Operation to perform               |
| `paths`    | `object` | File paths relevant to the action  |
| `metadata` | `object` | Arbitrary action-specific data     |

### Output JSON (stdout)

On success:

```json
{ "success": true, ... }
```

On failure:

```json
{ "success": false, "error": "message" }
```

The plugin exits with code 0 on success, non-zero on failure. Stderr is
captured and reported on failures.

## Discovery

Anx checks `$PATH` for executables matching `anx-plugin-<name>`. If a binary
is listed in `[plugins] enabled` but not found, anx reports the error and
continues.

## Configuration

Enable plugins in `article.toml`:

```toml
[plugins]
enabled = ["zenodo", "pandoc"]
```

## Available Plugins

### zenodo

**Binary**: `anx-plugin-zenodo` (Rust)

Zenodo archival plugin supporting OAuth login, deposition creation, DOI
reservation, file upload, and publication through the Zenodo API.

| Action             | Description                              |
| ------------------ | ---------------------------------------- |
| `oauth-login`      | OAuth 2.0 device flow — opens browser    |
| `deposit-create`   | Create a new draft deposition            |
| `reserve-doi`      | Reserve a DOI for the draft              |
| `upload-file`      | Upload a file to the deposition bucket   |
| `publish`          | Publish the completed deposition         |

Supports both production (`zenodo.org`) and sandbox
(`sandbox.zenodo.org`) via the `metadata.sandbox` flag.

### pandoc

**Binary**: `anx-plugin-pandoc` (Python)

Pandoc ODT export plugin that converts a LaTeX manuscript to ODT format with
composite figure injection and bibliography support.

| Action       | Description                          |
| ------------ | ------------------------------------ |
| `export-odt` | Convert LaTeX manuscript to ODT      |

Context fields:

| Field            | Default             | Description                       |
| ---------------- | ------------------- | --------------------------------- |
| `article_dir`    | —                   | Article root directory            |
| `tex_main`       | —                   | LaTeX main file (relative)        |
| `output`         | —                   | Desired ODT filename (relative)   |
| `pandoc_binary`  | `"pandoc"`          | Pandoc executable                 |
| `bibliography`   | `"references.bib"`  | BibTeX file (relative)            |
| `lua_filter`     | —                   | Lua filter for figure injection   |
| `reference_odt`  | —                   | Reference style ODT (relative)    |

## Writing a Plugin

Create an executable that:

1. Accepts `--plugin-context <json>`.
2. Parses the JSON context to determine the action.
3. Performs the operation.
4. Writes a JSON result to stdout.
5. Exits with code 0 on success, non-zero on failure.

Example skeleton in Python:

```python
#!/usr/bin/env python
import argparse, json, sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plugin-context", required=True)
    args = parser.parse_args()
    ctx = json.loads(args.plugin_context)

    try:
        if ctx["action"] == "my-action":
            result = {"success": True, "message": "done"}
        else:
            result = {"success": False, "error": f"unknown action: {ctx['action']}"}
    except Exception as e:
        result = {"success": False, "error": str(e)}

    json.dump(result, sys.stdout)
    sys.exit(0 if result["success"] else 1)

if __name__ == "__main__":
    main()
```

Name the binary `anx-plugin-my-plugin`, place it on `$PATH`, and add
`"my-plugin"` to `[plugins] enabled`.

## Nix Packaging

Plugins are built as separate derivations and included in the toolchain
via `symlinkJoin`:

```nix
pkgs.symlinkJoin {
  name = "anx-toolchain";
  paths = [ anx anx-plot figurefit anx-plugin-zenodo anx-plugin-pandoc ];
}
```
