use super::*;

#[test]
fn authorization_preserves_escaped_state_and_callback_contract() {
    let state = "state with + & = and 日本語";
    let url = build_authorization_url(SANDBOX_AUTH, "client+id", state).unwrap();
    let url = reqwest::Url::parse(&url).unwrap();
    let query: BTreeMap<_, _> = url.query_pairs().collect();
    assert_eq!(url.host_str(), Some("sandbox.zenodo.org"));
    assert_eq!(query.get("state").unwrap(), state);
    assert_eq!(query.get("client_id").unwrap(), "client+id");
    assert_eq!(query.get("redirect_uri").unwrap(), LOCAL_REDIRECT_URI);
    assert_eq!(query.get("scope").unwrap(), "deposit:write deposit:actions");
    assert!(!query.contains_key("client_secret"));
}

#[test]
fn sandbox_tokens_remain_bound_to_the_sandbox_endpoints() {
    let cfg = ZenodoConfig::new(true);
    let store = token_store_from_response(
        &cfg,
        "client".into(),
        json!({
            "access_token": "fixture-access", "refresh_token": "fixture-refresh", "expires_in": 3600
        }),
    )
    .unwrap();
    assert!(store.sandbox);
    assert_eq!(store.token_url, SANDBOX_TOKEN);
    assert_eq!(store.authorization_url, SANDBOX_AUTH);
    assert_eq!(store.refresh_token.as_deref(), Some("fixture-refresh"));
    assert!(store.expires_at.unwrap() > Utc::now());
    assert!(token_store_from_response(&cfg, "client".into(), json!({"error": "denied"})).is_err());
}

#[test]
fn deposit_metadata_preserves_authors_and_excludes_oauth_credentials() {
    let ctx = PluginContext {
        action: "deposit-create".into(),
        paths: BTreeMap::new(),
        metadata: json!({
            "title": "研究 dataset", "description": "A reproducible fixture",
            "creators": [{"name": "Researcher, A", "orcid": "0000-0002-1825-0097"}],
            "keywords": ["fixture"], "client_secret": "must-not-be-uploaded", "sandbox": true
        }),
    };
    let metadata = build_deposition_metadata(&ctx);
    assert_eq!(metadata["creators"], ctx.metadata["creators"]);
    assert_eq!(metadata["title"], "研究 dataset");
    assert_eq!(metadata["license"], "cc-by-4.0");
    assert!(metadata.get("client_secret").is_none());
    assert!(metadata.get("sandbox").is_none());
}
