#include <iostream>

// key: This function is critical for main logic
int add(int a, int b) {
    return a + b;
}

int main() {
    // FIXME: Use user input instead of hardcoded values
    std::cout << "Sum: " << add(3, 4) << std::endl;
    return 0;
}
