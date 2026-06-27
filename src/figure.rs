use crate::config::Config;
use miette::{Context, IntoDiagnostic, Result};
use std::process::Command;

fn run_python(config: &Config, args: &[&str]) -> Result<()> {
    let python_cmd = &config.tools.python;
    let parts = shlex::split(python_cmd)
        .unwrap_or_else(|| vec![python_cmd.clone()]);

    tracing::debug!("running: {} {}", parts.join(" "), args.join(" "));

    let output = Command::new(&parts[0])
        .args(&parts[1..])
        .args(args)
        .output()
        .into_diagnostic()
        .wrap_err("failed to execute Python")?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        tracing::error!("anx-plot failed:\n{stderr}");
        miette::bail!("anx-plot exited with code {:?}", output.status.code());
    }

    Ok(())
}

pub fn cmd_panels(config: &Config, figure: Option<&str>) -> Result<()> {
    let mut args = vec!["-m", "anx_plot.cli", "panels"];
    if let Some(f) = figure {
        args.push("--figure");
        args.push(f);
    }
    run_python(config, &args)
}

pub fn cmd_tikz(config: &Config, figure: Option<&str>) -> Result<()> {
    let panels_dir = &config.figures.panels;
    let lualatex = &config.tools.lualatex;

    // Find TikZ .tex files in the project
    let tikz_dir = &config.figures.layouts;
    let pattern = match figure {
        Some(f) => format!("{}/*{f}*.tex", tikz_dir.display()),
        None => format!("{}/*.tex", tikz_dir.display()),
    };

    let entries: Vec<_> = glob::glob(&pattern)
        .into_diagnostic()
        .wrap_err("failed to glob tikz files")?
        .filter_map(|e| e.ok())
        .collect();

    if entries.is_empty() {
        tracing::info!("no tikz panels to compile");
        return Ok(());
    }

    for entry in &entries {
        let stem = entry.file_stem().unwrap().to_string_lossy();
        tracing::info!("compiling tikz: {stem}");

        let output = Command::new(lualatex)
            .arg("--output-directory")
            .arg(panels_dir)
            .arg(entry.as_os_str())
            .output()
            .into_diagnostic()
            .wrap_err_with(|| format!("lualatex failed for {stem}"))?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            tracing::warn!("lualatex {stem} had issues:\n{}", stderr);
        }
    }

    Ok(())
}

pub fn cmd_composites(config: &Config, figure: Option<&str>) -> Result<()> {
    let mut args = vec!["-m", "anx_plot.cli", "composites"];
    if let Some(f) = figure {
        args.push("--figure");
        args.push(f);
    }
    run_python(config, &args)
}

pub fn cmd_all(config: &Config, figure: Option<&str>) -> Result<()> {
    cmd_panels(config, figure)?;
    cmd_tikz(config, figure)?;
    cmd_composites(config, figure)
}
