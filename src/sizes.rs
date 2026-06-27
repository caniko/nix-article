use crate::config::Config;
use miette::{Context, IntoDiagnostic, Result};
use std::process::Command;

pub fn cmd_sync(config: &Config) -> Result<()> {
    let python_cmd = &config.tools.python;
    let parts = shlex::split(python_cmd)
        .unwrap_or_else(|| vec![python_cmd.clone()]);

    // Find the project root (parent of layouts)
    let project_root = config
        .figures
        .layouts
        .parent()
        .and_then(|p| p.parent())
        .unwrap_or(std::path::Path::new("."));

    let mut cmd = Command::new(&parts[0]);
    cmd.args(&parts[1..])
        .args(["-m", "anx_plot.cli", "sync-sizes"])
        .arg(project_root.as_os_str());

    tracing::debug!("running: {cmd:?}");

    let output = cmd
        .output()
        .into_diagnostic()
        .wrap_err("failed to execute sync-sizes")?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        tracing::error!("sync-sizes failed:\n{stderr}");
        miette::bail!("sync-sizes exited with code {:?}", output.status.code());
    }

    tracing::info!("sizes synced");
    Ok(())
}
