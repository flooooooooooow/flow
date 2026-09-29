define i64 @f() {
  %p = alloca i8, i64 8
  store i8 1, ptr %p
  %v = load i8, ptr %p
  %w = zext i8 %v to i64
  ret i64 %w
}
