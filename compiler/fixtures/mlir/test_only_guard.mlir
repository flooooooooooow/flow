module {
  func.func private @mode_name() -> i32
  func.func private @tag() -> i32
  func.func @pick() -> i32 {
    %0 = arith.constant 2 : i32
    func.return %0 : i32
  }
  func.func @shape() -> i32 {
    %1 = arith.constant 100 : i32
    func.return %1 : i32
  }
  func.func @main() -> i32 {
    %2 = func.call @pick() : () -> i32
    %3 = arith.constant 2 : i32
    %4 = arith.cmpi ne, %2, %3 : i32
    cf.cond_br %4, ^bb0, ^bb1
    ^bb0:
      %5 = arith.constant 1 : i32
      func.return %5 : i32
    ^bb1:
      cf.br ^bb2
    ^bb2:
    %6 = func.call @mode_name() : () -> i32
    %7 = arith.constant 20 : i32
    %8 = arith.cmpi ne, %6, %7 : i32
    cf.cond_br %8, ^bb3, ^bb4
    ^bb3:
      %9 = arith.constant 2 : i32
      func.return %9 : i32
    ^bb4:
      cf.br ^bb5
    ^bb5:
    %10 = func.call @shape() : () -> i32
    %11 = arith.constant 200 : i32
    %12 = arith.cmpi ne, %10, %11 : i32
    cf.cond_br %12, ^bb6, ^bb7
    ^bb6:
      %13 = arith.constant 3 : i32
      func.return %13 : i32
    ^bb7:
      cf.br ^bb8
    ^bb8:
    %14 = func.call @tag() : () -> i32
    %15 = arith.constant 3 : i32
    %16 = arith.cmpi ne, %14, %15 : i32
    cf.cond_br %16, ^bb9, ^bb10
    ^bb9:
      %17 = arith.constant 4 : i32
      func.return %17 : i32
    ^bb10:
      cf.br ^bb11
    ^bb11:
    %18 = arith.constant 0 : i32
    func.return %18 : i32
  }
}
