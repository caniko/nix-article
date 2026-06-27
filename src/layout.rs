use crate::config::Config;
use duct::cmd;
use glob::glob;
use miette::{Context, IntoDiagnostic, Result};

/// Run figurefit on all (or one) layout TOMLs
pub fn cmd_solve(config: &Config, figure: Option<&str>) -> Result<()> {
    let layouts_dir = &config.figures.layouts;
    if !layouts_dir.exists() {
        miette::bail!("layouts directory not found: {}", layouts_dir.display());
    }

    let pattern = match figure {
        Some(f) => format!("{}/{}.toml", layouts_dir.display(), f),
        None => format!("{}/*.toml", layouts_dir.display()),
    };

    let entries: Vec<_> = glob(&pattern)
        .into_diagnostic()
        .wrap_err("failed to glob layout files")?
        .filter_map(|e| e.ok())
        .collect();

    if entries.is_empty() {
        tracing::warn!("no layout TOMLs matched: {pattern}");
        return Ok(());
    }

    for entry in &entries {
        let stem = entry.file_stem().unwrap().to_string_lossy();
        tracing::info!("solving layout: {stem}");

        let output = cmd!(
            &config.tools.figurefit,
            entry.to_string_lossy().as_ref()
        )
        .stdout_capture()
        .stderr_capture()
        .unchecked()
        .run()
        .into_diagnostic()
        .wrap_err_with(|| format!("figurefit failed for {stem}"))?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            tracing::error!("figurefit {} failed:\n{}", stem, stderr);
            miette::bail!("figurefit {} failed", stem);
        }

        tracing::info!("solved layout: {stem}");
    }

    Ok(())
}

/// Validate registry consistency
pub fn cmd_check(config: &Config) -> Result<()> {
    let registry_path = &config.figures.registry;
    if !registry_path.exists() {
        miette::bail!("registry not found: {}", registry_path.display());
    }

    let registry: toml::Value = std::fs::read_to_string(registry_path)
        .into_diagnostic()
        .wrap_err("failed to read registry")?
        .parse()
        .into_diagnostic()
        .wrap_err("failed to parse registry")?;

    let table = registry
        .as_table()
        .ok_or_else(|| miette::miette!("registry must be a table"))?;

    let layouts_dir = &config.figures.layouts;

    for (slug, value) in table {
        let Some(fig) = value.as_table() else { continue };
        let Some(layout_name) = fig.get("layout").and_then(|v| v.as_str()) else {
            tracing::warn!("{slug}: no layout specified");
            continue;
        };

        let layout_path = layouts_dir.join(format!("{layout_name}.toml"));
        if !layout_path.exists() {
            tracing::warn!("{slug}: layout not found: {}", layout_path.display());
        }

        let report_path = layouts_dir.join(format!("{layout_name}_report.toml"));
        if !report_path.exists() {
            tracing::warn!("{slug}: report not found (run `anx layout solve`)");
        }

        if let Some(module) = fig.get("module").and_then(|v| v.as_str()) {
            tracing::info!("{slug}: module={module}, layout={layout_name}");
        }
    }

    tracing::info!("registry check complete: {} entries", table.len());
    Ok(())
}
