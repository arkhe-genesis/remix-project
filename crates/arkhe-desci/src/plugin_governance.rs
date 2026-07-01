use arkhe_invariants::InvariantEngine;
use serde::{Deserialize, Serialize};
use tracing::warn;
use std::collections::HashSet;

use crate::error::DesciError;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginManifest {
    pub id: String,
    pub name: String,
    pub version: String,
    pub source: String,
    pub signature: Option<String>,
    pub install_script: String,
    pub requested_permissions: Vec<String>,
    pub dependencies: Vec<String>,
    #[serde(default)]
    pub checksum: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationResult {
    pub plugin_id: String,
    pub passed: bool,
    pub checks: Vec<ValidationCheck>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationCheck {
    pub invariant_id: String,
    pub passed: bool,
    pub message: String,
}

pub struct PluginValidator {
    engine: InvariantEngine,
    required_signatures: bool,
    max_permissions: usize,
    allowed_sources: HashSet<String>,
}

impl Default for PluginValidator {
    fn default() -> Self {
        Self {
            engine: InvariantEngine::new(),
            required_signatures: false,
            max_permissions: 3,
            allowed_sources: HashSet::new(),
        }
    }
}

impl PluginValidator {
    pub fn new(allowed_sources: Vec<String>, required_signatures: bool, _sandbox_enforced: bool, max_permissions: usize) -> Self {
        Self {
            engine: InvariantEngine::new(),
            required_signatures,
            max_permissions,
            allowed_sources: allowed_sources.into_iter().collect(),
        }
    }

    pub fn validate(&self, manifest: &PluginManifest) -> Result<ValidationResult, DesciError> {
        let mut checks = Vec::new();
        let mut passed = true;

        if self.required_signatures && manifest.signature.is_none() {
            passed = false;
            checks.push(ValidationCheck {
                invariant_id: "OWASP-003".to_string(),
                passed: false,
                message: "Plugin not signed".to_string(),
            });
        } else {
            checks.push(ValidationCheck {
                invariant_id: "OWASP-003".to_string(),
                passed: true,
                message: "Signature OK".to_string(),
            });
        }

        let dangerous = ["/etc/passwd", "/root/", "sudo", "rm -rf"];
        if dangerous.iter().any(|p| manifest.install_script.contains(p)) {
            passed = false;
            checks.push(ValidationCheck {
                invariant_id: "CNT-002".to_string(),
                passed: false,
                message: "Dangerous command in install_script".to_string(),
            });
        } else {
            checks.push(ValidationCheck {
                invariant_id: "CNT-002".to_string(),
                passed: true,
                message: "No dangerous commands".to_string(),
            });
        }

        if manifest.requested_permissions.len() > self.max_permissions {
            passed = false;
            checks.push(ValidationCheck {
                invariant_id: "OWASP-006".to_string(),
                passed: false,
                message: format!("Too many permissions: {}", manifest.requested_permissions.len()),
            });
        } else {
            checks.push(ValidationCheck {
                invariant_id: "OWASP-006".to_string(),
                passed: true,
                message: "Permissions OK".to_string(),
            });
        }

        if !self.allowed_sources.is_empty() {
            let allowed = self.allowed_sources.iter().any(|s| manifest.source.starts_with(s));
            if !allowed {
                passed = false;
                checks.push(ValidationCheck {
                    invariant_id: "CNT-003".to_string(),
                    passed: false,
                    message: format!("Source '{}' not in allowed sources", manifest.source),
                });
            } else {
                checks.push(ValidationCheck {
                    invariant_id: "CNT-003".to_string(),
                    passed: true,
                    message: "Source allowed".to_string(),
                });
            }
        }

        if !passed { warn!(plugin = %manifest.name, "Plugin validation failed"); }

        Ok(ValidationResult { plugin_id: manifest.id.clone(), passed, checks })
    }

    pub fn validate_with_engine(&self, manifest: &PluginManifest) -> Result<ValidationResult, DesciError> {
        let context = serde_json::json!({
            "plugin_id": manifest.id,
            "plugin_name": manifest.name,
            "source": manifest.source,
        });
        self.engine.validate_goal(&serde_json::to_string(&context).unwrap_or_default()).map_err(|e| DesciError::InvariantViolation(e.to_string()))?;
        self.validate(manifest)
    }

    pub fn validate_batch(&self, manifests: &[PluginManifest]) -> Vec<ValidationResult> {
        manifests
            .iter()
            .filter_map(|m| self.validate(m).ok())
            .collect()
    }

    pub fn allowed_sources(&self) -> &HashSet<String> {
        &self.allowed_sources
    }

    pub fn add_allowed_source(&mut self, source: String) {
        self.allowed_sources.insert(source);
    }

    pub fn remove_allowed_source(&mut self, source: &str) {
        self.allowed_sources.remove(source);
    }
}
