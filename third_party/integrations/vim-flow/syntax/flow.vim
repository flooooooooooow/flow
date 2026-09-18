if exists("b:current_syntax")
  finish
endif

syntax match flowComment "#.*$"
syntax region flowString start=+"+ skip=+\\\"+ end=+"+

syntax keyword flowDeclaration function struct enum type trait impl effect capability extern const flow state param solver import module export theorem assume shader
syntax keyword flowControl if elif else while for in to step parallel return match default handle with break continue when always every evolves as
syntax keyword flowOperator and or not
syntax keyword flowBoolean true false null
syntax keyword flowType i8 i16 i32 i64 i128 u8 u16 u32 u64 u128 f32 f64 bool string void array ptr vec

syntax match flowNumber "\<0x[0-9A-Fa-f]\+\>"
syntax match flowNumber "\<[0-9][0-9_]*\(\.[0-9][0-9_]*\)\?\([eE][+-]\?[0-9][0-9_]*\)\?\>"
syntax match flowAttribute "@[A-Za-z_][A-Za-z0-9_]*"

highlight default link flowComment Comment
highlight default link flowString String
highlight default link flowDeclaration Keyword
highlight default link flowControl Conditional
highlight default link flowOperator Operator
highlight default link flowBoolean Boolean
highlight default link flowType Type
highlight default link flowNumber Number
highlight default link flowAttribute PreProc

let b:current_syntax = "flow"
