// Test the generated MLIR by converting it to executable code
#include <iostream>

// Equivalent of the FLOW test_control.flow functions
int max(int a, int b) {
    if (a > b) {
        return a;
    } else {
        return b;
    }
}

int sum_to_n(int n) {
    int sum = 0;
    int i = 1;
    
    while (i <= n) {
        sum = sum + i;
        i = i + 1;
    }
    
    return sum;
}

int main() {
    int m = max(10, 20);
    int s = sum_to_n(5);
    int result = m + s;
    
    std::cout << "max(10, 20) = " << m << std::endl;
    std::cout << "sum_to_n(5) = " << s << std::endl;
    std::cout << "result = " << result << std::endl;
    
    return result;
}
