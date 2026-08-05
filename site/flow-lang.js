/* highlight.js grammar for the Flow language.
 *
 * Registered as `flow` plus the aliases used across the docs corpus. Without
 * this, every Flow snippet in the wiki falls back to plaintext.
 */
(function () {
    if (typeof hljs === 'undefined') return;

    const KEYWORDS = [
        'function', 'let', 'const', 'mut', 'struct', 'enum', 'type', 'trait', 'impl',
        'effect', 'capability', 'handle', 'with', 'perform', 'resume',
        'import', 'export', 'module', 'extern', 'as',
        'return', 'if', 'else', 'elif', 'while', 'for', 'in', 'to', 'step',
        'break', 'continue', 'match', 'default', 'when', 'where', 'defer',
        'parallel', 'gpu', 'simd', 'kernel', 'inline', 'noinline', 'always_inline',
        'target', 'test', 'assert', 'unsafe', 'sizeof', 'and', 'or', 'not',
    ];

    // Dynamics DSL — Flow's signature surface, worth its own token colour.
    const DYNAMICS = [
        'flow', 'state', 'param', 'input', 'output',
        'evolves', 'represent', 'connect', 'always', 'observe', 'derive',
    ];

    const TYPES = [
        'i8', 'i16', 'i32', 'i64', 'u8', 'u16', 'u32', 'u64',
        'f16', 'f32', 'f64', 'bool', 'char', 'string', 'str', 'void',
        'ptr', 'array', 'Array', 'String', 'Tensor', 'Vec', 'Option', 'Result',
    ];

    const LITERALS = ['true', 'false', 'null', 'nil', 'none'];

    function flow(hljs) {
        const NUMBER = {
            className: 'number',
            variants: [
                { begin: '\\b0[xX][0-9a-fA-F_]+\\b' },
                { begin: '\\b0[bB][01_]+\\b' },
                { begin: '\\b0[oO][0-7_]+\\b' },
                { begin: '\\b\\d[\\d_]*\\.?[\\d_]*([eE][-+]?\\d+)?(f32|f64|i8|i16|i32|i64|u8|u16|u32|u64)?\\b' },
            ],
            relevance: 0,
        };

        const STRING = {
            className: 'string',
            variants: [
                { begin: '"', end: '"', illegal: '\\n', contains: [{ begin: '\\\\.' }] },
                { begin: "'", end: "'", illegal: '\\n', contains: [{ begin: '\\\\.' }] },
            ],
        };

        const COMMENT = hljs.COMMENT('#', '$', { relevance: 0 });

        return {
            name: 'Flow',
            aliases: ['flowlang'],
            keywords: {
                keyword: KEYWORDS.join(' '),
                built_in: DYNAMICS.join(' '),
                type: TYPES.join(' '),
                literal: LITERALS.join(' '),
            },
            contains: [
                COMMENT,
                hljs.C_BLOCK_COMMENT_MODE,
                STRING,
                NUMBER,
                // `evolves as` / `represent … as` read as one unit
                { className: 'built_in', begin: '\\bevolves\\s+as\\b' },
                // Declaration names: function foo, struct Bar, effect Baz, flow Sys
                {
                    className: 'title',
                    begin: '\\b(?:function|struct|enum|effect|capability|trait|flow|type)\\s+',
                    end: '[A-Za-z_][A-Za-z0-9_]*',
                    excludeBegin: true,
                    returnEnd: false,
                    relevance: 4,
                },
                // Type annotations after `:` and `->`
                {
                    className: 'type',
                    begin: '(?:->|:)\\s*',
                    end: '[A-Za-z_][A-Za-z0-9_]*(?:<[^>\\n]*>)?',
                    excludeBegin: true,
                    relevance: 0,
                },
                // Attributes / decorators
                { className: 'meta', begin: '@[A-Za-z_][A-Za-z0-9_]*' },
                // Call sites
                {
                    className: 'title function_',
                    begin: '[A-Za-z_][A-Za-z0-9_]*(?=\\s*\\()',
                    relevance: 0,
                },
                { className: 'operator', begin: '(\\+|-|\\*|/|%|==|!=|<=|>=|<|>|=|\\||&|\\^|!|\\?)', relevance: 0 },
            ],
        };
    }

    hljs.registerLanguage('flow', flow);
    // Docs use several spellings in fenced blocks.
    for (const alias of ['flowlang', 'flow-lang']) {
        try { hljs.registerAliases(alias, { languageName: 'flow' }); } catch (_) { /* older hljs */ }
    }
})();
