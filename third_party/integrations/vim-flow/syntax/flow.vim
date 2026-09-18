if exists("b:current_syntax")
  finish
endif

syntax match flowComment /#.*$/
syntax region flowString start=/"/ skip=/\\./ end=/"/
syntax match flowNumber /\<0x[0-9A-Fa-f]\+\>/
syntax match flowNumber /\<[0-9]\+\(\.[0-9]\+\)\?\([eE][+-]\?[0-9]\+\)\?\>/

syntax keyword flowKeyword function let mut const struct enum effect capability import export module extern type distinct trait impl flow state param
syntax keyword flowControl if elif else while for parallel in to step return break continue defer match default handle with evolves as
syntax keyword flowConstant true false null
syntax keyword flowType i8 i16 i32 i64 i128 u8 u16 u32 u64 u128 f32 f64 bool string void array ptr vec span

highlight default link flowComment Comment
highlight default link flowString String
highlight default link flowNumber Number
highlight default link flowKeyword Keyword
highlight default link flowControl Conditional
highlight default link flowConstant Constant
highlight default link flowType Type

let b:current_syntax = "flow"
