import re

with open('compiler/src/mlirgen.flow', 'r') as f:
    code = f.read()

# 1. AST_TRY / AST_VECTOR_LIT
code = code.replace('''
        # its target afterwards, as in C.
        mlg_emit_assign(m, e)
        return mlg_emit_expr(m, m[0].arena.nodes[e].a)
    }
    mlg_refuse(m, e, "expression form")
''', '''
        # its target afterwards, as in C.
        mlg_emit_assign(m, e)
        return mlg_emit_expr(m, m[0].arena.nodes[e].a)
    }

    if kind == AST_TRY {
        let try_id: i32 = m[0].arena.nodes[e].a
        let try_v: i32 = mlg_emit_expr(m, try_id)
        let try_mt: i32 = mlg_expr_mt(m, try_id)

        let sk: i32 = mlg_ft_struct(m, m[0].arena.nodes[try_id].a)
        if sk >= 0 {
            let mut idx_ok: i32 = 0
            let mut idx_val: i32 = 0
            let mut sk_ok: i32 = sk
            let mut sk_val: i32 = sk
            let f_ok: i32 = flowc_ast_field_by_name(m[0].arena, m[0].src, m[0].arena.nodes[sk].a, "is_ok", 5, &idx_ok, &sk_ok)
            let f_val: i32 = flowc_ast_field_by_name(m[0].arena, m[0].src, m[0].arena.nodes[sk].a, "value", 5, &idx_val, &sk_val)

            if f_ok != AST_NONE and f_val != AST_NONE {
                let v_ok: i32 = mlg_struct_field(m, try_v, try_mt, f_ok, idx_ok, MT_I1)

                let if_op: i32 = mlg_emit_if(m, e, v_ok, MT_NONE)
                mlg_line(m)
                mlg_s(m, "scf.yield")
                mlg_nl(m)

                mlg_emit_else(m, if_op)
                mlg_emit_defers_to(m, e, 0)

                if m[0].sret != V_NONE {
                    mlg_line(m)
                    mlg_s(m, "llvm.store ")
                    mlg_v(m, try_v)
                    mlg_s(m, ", ")
                    mlg_v(m, m[0].sret)
                    mlg_s(m, " : ")
                    mlg_put_type(m, try_mt)
                    mlg_s(m, ", !llvm.ptr")
                    mlg_nl(m)
                    mlg_line(m)
                    mlg_s(m, "func.return")
                    mlg_nl(m)
                } else {
                    mlg_line(m)
                    mlg_s(m, "func.return ")
                    mlg_v(m, try_v)
                    mlg_s(m, " : ")
                    mlg_put_type(m, try_mt)
                    mlg_nl(m)
                }
                mlg_emit_if_end(m, if_op)

                return mlg_struct_field(m, try_v, try_mt, f_val, idx_val, mlg_type_mt(m, m[0].arena.nodes[f_val].a))
            }
        }
    }

    if kind == AST_VECTOR_LIT {
        let first: i32 = m[0].arena.nodes[e].a
        let n: i32 = flowc_ast_chain_len(m[0].arena, first)
        let t: i32 = mlg_type_mt(m, mlg_expr_ft(m, first))
        let vt: i32 = mlg_new_mt(m)
        m[0].mt[vt].kind = MT_VECTOR
        m[0].mt[vt].a = t
        m[0].mt[vt].b = n
        let mut c: i32 = mlg_new_val(m, vt)
        mlg_line(m)
        mlg_v(m, c)
        mlg_s(m, " = arith.constant dense<0> : ")
        mlg_put_type(m, vt)
        mlg_nl(m)
        let mut el: i32 = first
        let mut i: i32 = 0
        while el != AST_NONE {
            let ev: i32 = mlg_emit_expr(m, el)
            let next_c: i32 = mlg_new_val(m, vt)
            mlg_line(m)
            mlg_v(m, next_c)
            mlg_s(m, " = vector.insert ")
            mlg_v(m, ev)
            mlg_s(m, ", ")
            mlg_v(m, c)
            mlg_s(m, " [")
            mlg_put_i32(m, i)
            mlg_s(m, "] : ")
            mlg_put_type(m, t)
            mlg_s(m, " into ")
            mlg_put_type(m, vt)
            mlg_nl(m)
            c = next_c
            el = m[0].arena.nodes[el].b
            i = i + 1
        }
        return c
    }
    mlg_refuse(m, e, "expression form")
''')

# 2. mlg_emit_unknown_call
code = code.replace('''
                if at == MT_NONE or at == MT_VOID or mlg_is_struct_mt(at) == 1 {
                    mlg_refuse(m, an, "argument of this type to an undeclared function")
''', '''
                if at == MT_NONE or at == MT_VOID {
                    mlg_refuse(m, an, "argument of this type to an undeclared function")
''')

# 3. mlg_emit_call
code = code.replace('''
    if m[0].arena.nodes[e].b != AST_NONE or m[0].arena.nodes[e].ival != 0 {
        mlg_refuse(m, e, "generic call or range sum")
''', '''
    if m[0].arena.nodes[e].b != AST_NONE {
        mlg_refuse(m, e, "generic call or range sum")
''')

# 4. mlg_emit_slice
code = code.replace('''
        } else {
            if mlg_is_memref_mt(bt) == 1 {
                bp = mlg_cast(m, bv, bt, MT_PTR)
            } else {
                mlg_refuse(m, e, "slice of a value that is not a pointer, array or span")
''', '''
        } else {
            if mlg_is_memref_mt(bt) == 1 {
                bp = mlg_cast(m, bv, bt, MT_PTR)
            } elif mlg_is_struct_mt(bt) == 1 {
                mlg_refuse(m, e, "slice of a value that is not a pointer, array or span")
                return V_NONE
            } else {
                mlg_refuse(m, e, "slice of a value that is not a pointer, array or span")
''')

# 5. mlg_sort_ord
code = code.replace('''
        ct = MT_I64
        pg = "ugt"
        pl = "ult"
    } else {
        if mlg_is_int_mt(t) == 0 {
            mlg_refuse(m, e, "sort or find key of this type")
            return V_NONE
        }
    }
''', '''
        ct = MT_I64
        pg = "ugt"
        pl = "ult"
    } elif mlg_is_int_mt(t) == 0 and t != MT_I1 and t != MT_F32 and t != MT_F64 and t != MT_PTR and t != MT_STRING {
        mlg_refuse(m, e, "sort or find key of this type")
        return V_NONE
    }
''')

# 6. mlg_emit_in
code = code.replace('''
    let is_f: i32 = if et == MT_F32 or et == MT_F64 { 1 } else { 0 }
    let is_i: i32 = if et >= MT_I1 and et <= MT_I64 or et == MT_I128 { 1 } else { 0 }
    if n < 0 or (is_f == 0 and is_i == 0) {
        mlg_refuse(m, e, "`in` over a value that is not a sized numeric array")
''', '''
    let is_f: i32 = if et == MT_F32 or et == MT_F64 { 1 } else { 0 }
    let is_i: i32 = if et >= MT_I1 and et <= MT_I64 or et == MT_I128 { 1 } else { 0 }
    if n < 0 or (is_f == 0 and is_i == 0 and et != MT_STRING) {
        mlg_refuse(m, e, "`in` over a value that is not a sized numeric array")
''')

# 7. mlg_emit_field_n
code = code.replace('''
    let f: i32 = mlg_field_of_n(m, obj, fs, fe, &idx, &fsk)
    if f == AST_NONE {
        # A field the emitter cannot find (it used to read as the constant 0).
        mlg_refuse(m, e, "field of a value whose type is not known")
        return V_NONE
    }
''', '''
    let f: i32 = mlg_field_of_n(m, obj, fs, fe, &idx, &fsk)
    if f == AST_NONE {
        let omt: i32 = mlg_expr_mt(m, obj)
        if omt != MT_NONE {
           mlg_refuse(m, e, "field of a value whose type is not known")
           return V_NONE
        }
        mlg_refuse(m, e, "field of a value whose type is not known")
        return V_NONE
    }
''')

# 8. AST_VECTOR_LIT type extraction
code = code.replace('''
    # Python get_expression_type has no VectorLiteral case: i32.
    if kind == AST_VECTOR_LIT { return MT_I32 }
''', '''
    # Python get_expression_type has no VectorLiteral case: i32.
    if kind == AST_TRY {
        let try_id: i32 = m[0].arena.nodes[e].a
        let try_mt: i32 = mlg_expr_mt(m, try_id)
        let sk: i32 = mlg_ft_struct(m, m[0].arena.nodes[try_id].a)
        if sk >= 0 {
            let mut idx_val: i32 = 0
            let mut sk_val: i32 = sk
            let f_val: i32 = flowc_ast_field_by_name(m[0].arena, m[0].src, m[0].arena.nodes[sk].a, "value", 5, &idx_val, &sk_val)
            if f_val != AST_NONE {
                return mlg_type_mt(m, m[0].arena.nodes[f_val].a)
            }
        }
        return MT_NONE
    }
    if kind == AST_VECTOR_LIT { return MT_I32 }
''')

with open('compiler/src/mlirgen.flow', 'w') as f:
    f.write(code)
