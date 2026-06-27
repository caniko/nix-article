use clap::{Parser, Subcommand};
use miette::Result;

/// Article toolchain: figure layout, generation, and manuscript building.
#[derive(Parser)]
#[command(name = "anx", version, about)]
struct Cli {
    /// Path to article.toml (default: search up from cwd)
    #[arg(short = 'C', long, env = "ARTICLE_DIR")]
    project_dir: Option<std::path::PathBuf>,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Scaffold a new article project
    Init {
        /// Target directory (default: current directory)
        #[arg(default_value = ".")]
        dir: std::path::PathBuf,
    },
    /// Layout solving (runs figurefit on layout specs)
    Layout {
        #[command(subcommand)]
        action: LayoutAction,
    },
    /// Figure generation (panels, TikZ, composites)
    Figure {
        #[command(subcommand)]
        action: FigureAction,
    },
    /// Manuscript build (LaTeX compilation)
    Build {
        #[command(subcommand)]
        action: BuildAction,
    },
    /// Sync size/font constants between Python and LaTeX
    Sizes {
        #[command(subcommand)]
        action: SizesAction,
    },
}

#[derive(Subcommand)]
enum LayoutAction {
    /// Solve all layout TOMLs
    Solve {
        /// Solve only the specified figure (e.g. "CF01")
        figure: Option<String>,
    },
    /// Validate registry consistency
    Check,
}

#[derive(Subcommand)]
enum FigureAction {
    /// Export matplotlib panels
    Panels {
        /// Export only the specified figure
        figure: Option<String>,
    },
    /// Compile TikZ panels to SVG
    Tikz {
        /// Compile only the specified figure
        figure: Option<String>,
    },
    /// Assemble composite figures
    Composites {
        /// Assemble only the specified figure
        figure: Option<String>,
    },
    /// All figure steps (panels + tikz + composites)
    All {
        /// Process only the specified figure
        figure: Option<String>,
    },
}

#[derive(Subcommand)]
enum BuildAction {
    /// Incremental LaTeX compile
    Compile,
    /// Full rebuild: sync -> solve -> figures -> compile
    Rebuild,
}

#[derive(Subcommand)]
enum SizesAction {
    /// Regenerate fonts.tex and figure_sizes.tex from Python sizing constants
    Sync,
}

mod config;
mod layout;
mod figure;
mod build;
mod sizes;
mod plugins;

fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "info".into()),
        )
        .init();

    let cli = Cli::parse();

    // `init` doesn't need config; all other commands do.
    if let Commands::Init { dir } = &cli.command {
        return config::scaffold(dir);
    }

    let project_dir = cli.project_dir.unwrap_or_else(|| std::env::current_dir().unwrap());
    let config = config::load(&project_dir)?;

    match &cli.command {
        Commands::Init { .. } => unreachable!(),
        Commands::Layout { action } => match action {
            LayoutAction::Solve { figure } => layout::cmd_solve(&config, figure.as_deref()),
            LayoutAction::Check => layout::cmd_check(&config),
        },
        Commands::Figure { action } => match action {
            FigureAction::Panels { figure } => figure::cmd_panels(&config, figure.as_deref()),
            FigureAction::Tikz { figure } => figure::cmd_tikz(&config, figure.as_deref()),
            FigureAction::Composites { figure } => {
                figure::cmd_composites(&config, figure.as_deref())
            }
            FigureAction::All { figure } => figure::cmd_all(&config, figure.as_deref()),
        },
        Commands::Build { action } => match action {
            BuildAction::Compile => build::cmd_compile(&config),
            BuildAction::Rebuild => build::cmd_rebuild(&config),
        },
        Commands::Sizes { action } => match action {
            SizesAction::Sync => sizes::cmd_sync(&config),
        },
    }
}
