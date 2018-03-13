#include "b/b.h"
#include "a/a.h"

int main() {
    int x = b(99) + a(99);
    return x%10;
}
