use miette::{Context, IntoDiagnostic, Result};
use serde::Deserialize;
use std::path::{Path, PathBuf};
use std::fs;

/// Project configuration loaded from article.toml
#[derive(Clone, Debug, Deserialize)]
pub struct Config {
    #[serde(default)]
    pub article: ArticleConfig,
    #[serde(default)]
    pub figures: FiguresConfig,
    #[serde(default)]
    pub tools: ToolsConfig,
    #[serde(default)]
    #[expect(dead_code)]
    pub plugins: PluginsConfig,
    #[serde(default)]
    #[expect(dead_code)]
    pub sizing: SizingConfig,
}

#[derive(Clone, Debug, Deserialize)]
pub struct ArticleConfig {
    /// Project name
    #[serde(default = "default_name")]
    #[expect(dead_code)]
    pub name: String,
    /// Path to main LaTeX file
    #[serde(default = "default_tex_main")]
    pub tex_main: PathBuf,
}

#[derive(Clone, Debug, Deserialize)]
pub struct FiguresConfig {
    /// Path to figure registry TOML
    #[serde(default = "default_figures_registry")]
    pub registry: PathBuf,
    /// Directory containing layout TOMLs
    #[serde(default = "default_layouts_dir")]
    pub layouts: PathBuf,
    /// Directory for generated panels
    #[serde(default = "default_panels_dir")]
    pub panels: PathBuf,
    /// Directory for generated composites
    #[serde(default = "default_composites_dir")]
    pub composites: PathBuf,
}

#[derive(Clone, Debug, Deserialize)]
pub struct ToolsConfig {
    /// figurefit binary path or name
    #[serde(default = "default_figurefit")]
    pub figurefit: String,
    /// Python interpreter command
    #[serde(default = "default_python")]
    pub python: String,
    /// latexmk command
    #[serde(default = "default_latexmk")]
    pub latexmk: String,
    /// lualatex command
    #[serde(default = "default_lualatex")]
    pub lualatex: String,
}

#[derive(Clone, Debug, Deserialize, Default)]
pub struct PluginsConfig {
    /// Enable or disable specific plugins
    #[serde(default)]
    #[expect(dead_code)]
    pub enabled: Vec<String>,
}

#[derive(Clone, Debug, Deserialize)]
pub struct SizingConfig {
    /// Page width in mm
    #[serde(default = "default_page_width")]
    #[expect(dead_code)]
    pub page_width_mm: f64,
    /// Page height in mm
    #[serde(default = "default_page_height")]
    #[expect(dead_code)]
    pub page_height_mm: f64,
    /// Margin in mm
    #[serde(default = "default_margin")]
    #[expect(dead_code)]
    pub margin_mm: f64,
    /// Main font family
    #[serde(default = "default_font_main")]
    #[expect(dead_code)]
    pub font_main: String,
    /// Sans font family
    #[serde(default = "default_font_sans")]
    #[expect(dead_code)]
    pub font_sans: String,
    /// Mono font family
    #[serde(default = "default_font_mono")]
    #[expect(dead_code)]
    pub font_mono: String,
    /// Small font size (pt)
    #[serde(default = "default_font_small")]
    #[expect(dead_code)]
    pub font_small: f64,
    /// Base font size (pt)
    #[serde(default = "default_font_base")]
    #[expect(dead_code)]
    pub font_base: f64,
    /// Axis label font size (pt)
    #[serde(default = "default_font_label_axis")]
    #[expect(dead_code)]
    pub font_label_axis: f64,
    /// Big/title font size (pt)
    #[serde(default = "default_font_big")]
    #[expect(dead_code)]
    pub font_big: f64,
    /// Panel letter font size (pt)
    #[serde(default = "default_font_panel")]
    #[expect(dead_code)]
    pub font_panel: f64,
}

impl Default for ArticleConfig {
    fn default() -> Self {
        Self {
            name: default_name(),
            tex_main: default_tex_main(),
        }
    }
}

impl Default for FiguresConfig {
    fn default() -> Self {
        Self {
            registry: default_figures_registry(),
            layouts: default_layouts_dir(),
            panels: default_panels_dir(),
            composites: default_composites_dir(),
        }
    }
}

impl Default for ToolsConfig {
    fn default() -> Self {
        Self {
            figurefit: default_figurefit(),
            python: default_python(),
            latexmk: default_latexmk(),
            lualatex: default_lualatex(),
        }
    }
}

impl Default for SizingConfig {
    fn default() -> Self {
        Self {
            page_width_mm: default_page_width(),
            page_height_mm: default_page_height(),
            margin_mm: default_margin(),
            font_main: default_font_main(),
            font_sans: default_font_sans(),
            font_mono: default_font_mono(),
            font_small: default_font_small(),
            font_base: default_font_base(),
            font_label_axis: default_font_label_axis(),
            font_big: default_font_big(),
            font_panel: default_font_panel(),
        }
    }
}

fn default_name() -> String { "article".into() }
fn default_tex_main() -> PathBuf { PathBuf::from("manuscript.tex") }
fn default_figures_registry() -> PathBuf { PathBuf::from("figures.toml") }
fn default_layouts_dir() -> PathBuf { PathBuf::from("figures/layouts") }
fn default_panels_dir() -> PathBuf { PathBuf::from("figures/panels") }
fn default_composites_dir() -> PathBuf { PathBuf::from("figures/composites") }
fn default_figurefit() -> String { "figurefit".into() }
fn default_python() -> String { "uv run python".into() }
fn default_latexmk() -> String { "latexmk".into() }
fn default_lualatex() -> String { "lualatex".into() }
fn default_page_width() -> f64 { 210.0 }
fn default_page_height() -> f64 { 297.0 }
fn default_margin() -> f64 { 25.0 }
fn default_font_main() -> String { "Latin Modern Roman".into() }
fn default_font_sans() -> String { "Latin Modern Sans".into() }
fn default_font_mono() -> String { "Latin Modern Mono".into() }
fn default_font_small() -> f64 { 7.0 }
fn default_font_base() -> f64 { 8.0 }
fn default_font_label_axis() -> f64 { 9.0 }
fn default_font_big() -> f64 { 10.0 }
fn default_font_panel() -> f64 { 14.0 }

/// Find and load article.toml starting from project_dir, searching upward.
pub fn load(project_dir: &Path) -> Result<Config> {
    let root = find_project_root(project_dir)?;
    let config_path = root.join("article.toml");
    let content = fs::read_to_string(&config_path)
        .into_diagnostic()
        .wrap_err_with(|| format!("failed to read {}", config_path.display()))?;
    let mut config: Config = toml::from_str(&content)
        .into_diagnostic()
        .wrap_err_with(|| format!("failed to parse {}", config_path.display()))?;
    // Make relative paths relative to project root
    config.figures.registry = root.join(&config.figures.registry);
    config.figures.layouts = root.join(&config.figures.layouts);
    config.figures.panels = root.join(&config.figures.panels);
    config.figures.composites = root.join(&config.figures.composites);
    config.article.tex_main = root.join(&config.article.tex_main);
    Ok(config)
}

/// Find the project root by walking up until we find article.toml
fn find_project_root(start: &Path) -> Result<PathBuf> {
    let start = std::fs::canonicalize(start)
        .into_diagnostic()
        .wrap_err("failed to canonicalize project path")?;
    for ancestor in start.ancestors() {
        if ancestor.join("article.toml").exists() {
            return Ok(ancestor.to_path_buf());
        }
    }
    miette::bail!(
        "no article.toml found in {} or any parent directory",
        start.display()
    );
}

/// Scaffold a new article project
pub fn scaffold(dir: &Path) -> Result<()> {
    fs::create_dir_all(dir.join("figures/layouts"))
        .into_diagnostic()
        .wrap_err("failed to create figures/layouts")?;
    fs::create_dir_all(dir.join("figures/panels"))
        .into_diagnostic()
        .wrap_err("failed to create figures/panels")?;

    let config_path = dir.join("article.toml");
    if !config_path.exists() {
        fs::write(&config_path, DEFAULT_CONFIG)
            .into_diagnostic()
            .wrap_err("failed to write article.toml")?;
        tracing::info!("created {}", config_path.display());
    }

    let registry_path = dir.join("figures.toml");
    if !registry_path.exists() {
        fs::write(&registry_path, DEFAULT_FIGURES)
            .into_diagnostic()
            .wrap_err("failed to write figures.toml")?;
        tracing::info!("created {}", registry_path.display());
    }

    tracing::info!("scaffolded article project in {}", dir.display());
    Ok(())
}

const DEFAULT_CONFIG: &str = r#"
[article]
name = "my-article"
tex-main = "manuscript.tex"

[figures]
registry = "figures.toml"
layouts = "figures/layouts"
panels = "figures/panels"
composites = "figures/composites"

[tools]
figurefit = "figurefit"
python = "uv run python"
latexmk = "latexmk"
lualatex = "lualatex"

[sizing]
page-width-mm = 210
page-height-mm = 297
margin-mm = 25
font-main = "Latin Modern Roman"
font-sans = "Latin Modern Sans"
font-mono = "Latin Modern Mono"
font-small = 7.0
font-base = 8.0
font-label-axis = 9.0
font-big = 10.0
font-panel = 14.0
"#;

const DEFAULT_FIGURES: &str = r#"
# Figure registry
# Each entry maps a figure slug to its composite number and layout spec.
# Conventions:
#   [slug]
#   number = 1          # CF01
#   module = "module_name"  # Python module path for figure generation
#   layout = "CF01"     # layout TOML basename in figures/layouts/ (without .toml)

# Example:
# [architecture]
# number = 1
# module = "my_figures.fig1_architecture"
# layout = "CF01"
"#;
