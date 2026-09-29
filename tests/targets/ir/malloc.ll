declare ptr @malloc(i64)
define i32 @bad() {
  %p = call ptr @malloc(i64 8)
  ret i32 0
}
