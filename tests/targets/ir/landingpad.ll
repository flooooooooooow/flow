define void @f() {
  %x = landingpad { ptr, i32 } cleanup
  ret void
}
