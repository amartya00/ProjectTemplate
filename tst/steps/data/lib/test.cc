#include "test.h"
#include "a/a.h"

#include <string>
#include <iostream>

namespace Test {
    void printMessage(int a, int b) {
        std::cout << "Sum of a and b is " << std::to_string(A::add(a, b)) << "\n";
    }
}