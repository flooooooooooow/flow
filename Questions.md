# Flow Development Questions

This file tracks questions that need human resolution before the AI can proceed.

Format:
- Questions are added by AI when uncertain
- Answers are added by human
- Resolved questions move to the archive at the bottom

---

## Open Questions

### 2026-01-09: Web Playground Debugging Support

**Context:** The web playground exists (`docs/playground/index.html`) but doesn't have debugging capabilities. User mentioned wanting this.

**Options:**
1. **Source maps + breakpoints** - Map Flow source to generated JS, use browser DevTools
2. **Step-through interpreter** - Build a visual debugger in the playground itself
3. **Print-based debugging** - Just show console output clearly (simplest)

**Recommendation:** Start with option 3 (print debugging with clear output), then add option 2 for educational value.

**Status:** ✅ **Answered: Option 2** - Will build step-through visual debugger in playground

---

### 2026-01-09: Parser `ptr[0].field` Syntax

**Context:** Many examples fail because the parser doesn't support accessing struct fields through a pointer index like `state[0].score`. This blocks ~20 examples.

**Options:**
1. **Fix the parser** - Add support for this chained access pattern
2. **Workaround pattern** - Document the individual-variable workaround
3. **Different syntax** - Use `(*ptr).field` or `ptr->field` instead

**Recommendation:** Fix the parser - this is a common pattern needed for real programs.

**Status:** 🔄 **In Progress** - Parser fixes applied:
1. ✅ `ptr[0].field` - Array access followed by field access now works
2. ✅ `obj.field[i]` - Field access followed by array access now works  
3. ✅ Scientific notation (`1e-10`) now tokenizes correctly
4. 🔲 Still need to fix some example files (missing return types, etc.)

---

## Resolved Questions (Archive)

*(Move resolved questions here with their answers)*

<!-- Example:
### 2026-01-08: Should we use `let mut` or `var` for mutable variables?

**Answer:** Use `let mut` - matches Rust, explicit about mutation.

**Resolved:** 2026-01-08
-->
