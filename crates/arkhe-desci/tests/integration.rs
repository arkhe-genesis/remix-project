use arkhe_desci::*;

#[test]
fn test_full_plugin_validation_flow() {
    let validator = plugin_governance::PluginValidator::default();

    let manifest = plugin_governance::PluginManifest {
        id: "bioinfo-tools".to_string(),
        name: "Bioinformatics Tools".to_string(),
        version: "2.1.0".to_string(),
        source: "https://github.com/example/bioinfo-tools".to_string(),
        signature: Some("sha256:abcdef123456".to_string()),
        install_script: "apt install -y samtools bcftools".to_string(),
        requested_permissions: vec!["network".to_string(), "fs_read".to_string()],
        dependencies: vec![],
        checksum: Some("sha256:fedcba654321".to_string()),
    };

    let result = validator.validate(&manifest).unwrap();
    assert!(result.passed);
    assert!(result.checks.iter().all(|c| c.passed));
}
