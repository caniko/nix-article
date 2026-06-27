use crate::config::Config;
use duct::cmd;
use miette::{Context, IntoDiagnostic, Result};
use std::path::Path;

pub fn cmd_compile(config: &Config) -> Result<()> {
    let tex_main = &config.article.tex_main;
    if !tex_main.exists() {
        miette::bail!("main tex file not found: {}", tex_main.display());
    }

    let parent = tex_main.parent().unwrap_or(Path::new("."));
    tracing::info!(
        "compiling {} in {}",
        tex_main.file_name().unwrap().to_string_lossy(),
        parent.display()
    );

    let output = cmd!(
        &config.tools.latexmk,
        "-pdf",
        "-lualatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        tex_main.file_name().unwrap().to_string_lossy().as_ref()
    )
    .dir(parent)
    .stdout_capture()
    .stderr_capture()
    .unchecked()
    .run()
    .into_diagnostic()
    .wrap_err("latexmk failed")?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        tracing::error!("latexmk failed:\n{}", stderr);
        miette::bail!("latexmk exited with code {:?}", output.status.code());
    }

    tracing::info!("compilation complete");
    Ok(())
}

pub fn cmd_rebuild(config: &Config) -> Result<()> {
    tracing::info!("full rebuild started");

    crate::sizes::cmd_sync(config)?;
    crate::layout::cmd_solve(config, None)?;
    crate::figure::cmd_all(config, None)?;
    cmd_compile(config)?;

    tracing::info!("full rebuild complete");
    Ok(())
}
