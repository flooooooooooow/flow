define void @f() personality ptr null {
  invoke void @g() to label %ok unwind label %bad
ok:
  ret void
bad:
  %x = landingpad { ptr, i32 } cleanup
  ret void
}
declare void @g()
