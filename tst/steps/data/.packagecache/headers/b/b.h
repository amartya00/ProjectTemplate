#ifndef __C_HEADERS__
#define __C_HEADERS__

#include "k/k.h"

namespace B {
    template <typename T> T multiply(const T& a, const T& b) {
        return K::product(a, b);
    }
}

#endif
