def foo(): return 1
sum = 0
for i in range(1000000): sum += foo()
