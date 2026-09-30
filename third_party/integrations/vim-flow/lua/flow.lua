local M = {}

function M.setup(opts)
  opts = opts or {}

  vim.filetype.add({
    extension = {
      flow = "flow",
    },
  })

  vim.api.nvim_create_autocmd("FileType", {
    pattern = "flow",
    callback = function(args)
      local root = vim.fs.root(args.buf, { ".git", "flow.toml" }) or vim.fn.getcwd()

      vim.lsp.start({
        name = "flow-lsp",
        cmd = opts.cmd or { "flow", "lsp" },
        root_dir = root,
      })
    end,
  })
end

return M
