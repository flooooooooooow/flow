# Publishing the Zed Extension

Upstream publish of the Zed extension is currently blocked on issue #899 because Zed language extensions require a Tree-sitter grammar repository pinned to a Git revision.

Once #899 is resolved and the standalone `tree-sitter-flow` repository is available, we can submit the Zed extension to the official Zed extension registry.

In the meantime, local development and installation are supported:
In Zed, open Extensions, choose "Install Dev Extension", then select this directory.
