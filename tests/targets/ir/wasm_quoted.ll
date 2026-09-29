define i32 @add(i32 %a, i32 %b) {
  %v = add i32 %a, %b
  ret i32 %v
}
define void @"quoted.name"() {
  ret void
}
declare i32 @external()
