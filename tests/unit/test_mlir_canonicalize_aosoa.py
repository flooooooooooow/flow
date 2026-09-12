import pytest
from flow.parser import Parser, Lexer, Type, StructDecl, VarDecl
from flow.mlir_canonicalize import apply_aosoa_transform

def parse(code: str):
    return Parser(Lexer(code)).parse()

def test_aosoa_transform_does_not_modify_other_structs():
    code = '''
    struct Other { x: f32, y: f32 }
    function main() {
        let pts: [Other; 10];
    }
    '''
    ast = parse(code)
    new_ast = apply_aosoa_transform(ast)
    assert len(new_ast) == 2

def test_aosoa_transform_applies_to_particle():
    code = '''
    struct Particle { x: f32, y: f32 }
    function main() {
        let pts: [Particle; 10];
    }
    '''
    ast = parse(code)
    new_ast = apply_aosoa_transform(ast)
    
    # Expect 3 decls: Particle_SoA_10, Particle, main
    assert len(new_ast) == 3
    assert isinstance(new_ast[0], StructDecl)
    assert new_ast[0].name == "Particle_SoA_10"
    
    main_func = new_ast[2]
    var_decl = main_func.body.statements[0]
    assert var_decl.type.name == "Particle_SoA_10"
