#include "test.h"
#include "a/a.h"
#include "b/b.h"

#include <string>
#include <iostream>

namespace Test {
    void printMessage(int a, int b) {
        std::cout << "Sum of a and b is " << std::to_string(A::add(a, b)) << "\n";
        std::cout << "Product of a and b is " << std::to_string(B::multiply(a, b)) << "\n";
    }
}


    int main() {
        Test::printMessage(2, 3);
    }