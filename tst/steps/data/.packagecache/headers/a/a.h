#ifndef __A_HEADERS__
#define __A_HEADERS__

#include "k/k.h"

namespace A {
    template <typename T> T add(const T& a, const T& b) {
        return K::sum(a, b);
    }
}

#endif
