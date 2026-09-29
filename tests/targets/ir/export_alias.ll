define i32 @answer() {
  ret i32 42
}
define i32 @flow_export_answer() {
  %r = call i32 @answer()
  ret i32 %r
}
