use miette::Result;
use std::process::Command;

/// Discover and invoke a plugin binary named `anx-plugin-<name>`.
#[expect(dead_code)]
pub fn invoke(name: &str, context_json: &str) -> Result<String> {
    let binary = format!("anx-plugin-{name}");
    let output = Command::new(&binary)
        .arg("--plugin-context")
        .arg(context_json)
        .output()
        .map_err(|e| {
            if e.kind() == std::io::ErrorKind::NotFound {
                miette::miette!("plugin not found: {binary} (not in $PATH)")
            } else {
                miette::miette!("failed to execute plugin {binary}: {e}")
            }
        })?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        miette::bail!("plugin {binary} failed:\n{stderr}");
    }

    Ok(String::from_utf8_lossy(&output.stdout).to_string())
}
