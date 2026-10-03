use zed_extension_api::{self as zed, Result};

struct FlowExtension;

impl zed::Extension for FlowExtension {
    fn new() -> Self {
        Self
    }

    fn language_server_command(
        &mut self,
        _language_server_id: &zed::LanguageServerId,
        worktree: &zed::Worktree,
    ) -> Result<zed::Command> {
        let flow = worktree
            .which("flow")
            .ok_or_else(|| "flow is not available on PATH".to_string())?;
        Ok(zed::Command {
            command: flow,
            args: vec!["lsp".to_string()],
            env: worktree.shell_env(),
        })
    }
}

zed::register_extension!(FlowExtension);
