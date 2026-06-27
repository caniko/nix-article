use std::process::Command;
use std::path::Path;

fn anx_binary() -> String {
    let target_dir = std::env::var("CARGO_TARGET_DIR")
        .unwrap_or_else(|_| "target".to_string());
    format!("{}/debug/anx", target_dir)
}

#[test]
fn test_help_succeeds() {
    let output = Command::new(anx_binary())
        .arg("--help")
        .output()
        .expect("failed to run anx --help");
    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("anx"));
    assert!(stdout.contains("init"));
    assert!(stdout.contains("layout"));
    assert!(stdout.contains("figure"));
    assert!(stdout.contains("build"));
    assert!(stdout.contains("sizes"));
}

#[test]
fn test_init_scaffolds_project() {
    let dir = tempfile::tempdir().expect("failed to create temp dir");
    let project_path = dir.path().join("test-article");

    let output = Command::new(anx_binary())
        .arg("init")
        .arg(&project_path)
        .output()
        .expect("failed to run anx init");
    assert!(output.status.success());

    assert!(project_path.join("article.toml").exists());
    assert!(project_path.join("figures.toml").exists());
    assert!(project_path.join("figures/layouts").is_dir());
    assert!(project_path.join("figures/panels").is_dir());
}

#[test]
fn test_init_in_existing_dir() {
    let dir = tempfile::tempdir().expect("failed to create temp dir");

    // Run init twice — second should be idempotent
    let output1 = Command::new(anx_binary())
        .arg("init")
        .arg(dir.path())
        .output()
        .expect("first init");
    assert!(output1.status.success());

    let output2 = Command::new(anx_binary())
        .arg("init")
        .arg(dir.path())
        .output()
        .expect("second init");
    assert!(output2.status.success());
}

#[test]
fn test_layout_check_with_empty_project() {
    let dir = tempfile::tempdir().expect("failed to create temp dir");
    let project_path = dir.path().join("empty-article");

    // Init first
    Command::new(anx_binary())
        .arg("init")
        .arg(&project_path)
        .output()
        .expect("init failed");

    // Layout check should pass with no layouts (just warn)
    let output = Command::new(anx_binary())
        .arg("-C")
        .arg(&project_path)
        .arg("layout")
        .arg("check")
        .output()
        .expect("layout check failed");
    assert!(output.status.success());
}

#[test]
fn test_sizes_sync_with_empty_project() {
    let dir = tempfile::tempdir().expect("failed to create temp dir");
    let project_path = dir.path().join("sizes-article");

    Command::new(anx_binary())
        .arg("init")
        .arg(&project_path)
        .output()
        .expect("init failed");

    let output = Command::new(anx_binary())
        .arg("-C")
        .arg(&project_path)
        .arg("sizes")
        .arg("sync")
        .output()
        .expect("sizes sync failed");
    assert!(output.status.success());
}
