#include <iostream>
#include <tuple>
#include <functional>
#include <chrono>
#include <gates/all.h>
#include "QuEST.h"
#include "cmaes.h"
#include "vqe.h"


#define BENCHMARK(x, n) benchmarkFunction(x, #x, n)

using namespace std;
using namespace std::chrono;
using namespace libcmaes;


QuESTEnv questEnv;
static size_t num_qubits = 8;
static size_t circ_size = 0;

void testQuest() {
    Qureg reg = createQureg(num_qubits, questEnv);
    initZeroState(reg);
    for (size_t i = 0; i < circ_size; i++) {
        for (size_t j = 0; j < num_qubits; j++) {
            rotateX(reg, j, 0.3);
            controlledNot(reg, j, (j + 1)%num_qubits);
        }
    }
    destroyQureg(reg, questEnv);
}

static QCircuit circ(num_qubits, 0);
void testQcirc() {
    Qureg reg = createQureg(num_qubits, questEnv);
    circ.apply(reg);
    destroyQureg(reg, questEnv);
}

template<typename Func>
void benchmarkFunction(Func f, const std::string& name, size_t n) {
    high_resolution_clock::time_point t1 = high_resolution_clock::now();
    for (size_t i = 0; i < n; i++) {
        f();
    }
    high_resolution_clock::time_point t2 = high_resolution_clock::now();
    auto duration = duration_cast<microseconds>( t2 - t1 ).count();
    cout << name << ": " << 1000000.0 * n / duration << " ops" << endl;
}



int main() {
    for (size_t i = 0; i < circ_size / 4; i++) {
        for (size_t j = 0; j < num_qubits; j++) {
//            circ.gates.push_back(GateInstance(GateTypes::rx(), {j}, {0.3}));
            circ.gates.push_back(GateInstance(GateTypes::blockA(), {j, (j + 1)%num_qubits}, {0,0,0,0}));
        }
    }

    questEnv = createQuESTEnv();
    BENCHMARK(testQuest, 1000);
    BENCHMARK(testQcirc, 1000);
    destroyQuESTEnv(questEnv);

    Hamiltonian h(1 << circ.numQubits, 1 << circ.numQubits);
    h.insert(0, 0) = std::complex(-0.3509540000000001, 0.0);
    h.insert(0, 2) = std::complex(0.01627, 0.0);
    h.insert(0, 3) = std::complex(-0.03531999999999999, 0.0);
    h.insert(0, 4) = std::complex(-0.03146600000000001, 0.0);
    h.insert(0, 6) = std::complex(-0.005084, 0.0);
    h.insert(0, 7) = std::complex(0.029996, 0.0);
    h.insert(0, 12) = std::complex(-0.09482, 0.0);
    h.insert(0, 14) = std::complex(-0.03278, 0.0);
    h.insert(0, 15) = std::complex(0.115704, 0.0);
    h.insert(1, 1) = std::complex(0.48685600000000007, 0.0);
    h.insert(1, 5) = std::complex(-0.024489999999999998, 0.0);
    h.insert(1, 13) = std::complex(-0.18036, 0.0);
    h.insert(2, 0) = std::complex(0.01627, 0.0);
    h.insert(2, 2) = std::complex(-0.09481000000000003, 0.0);
    h.insert(2, 3) = std::complex(0.003558000000000004, 0.0);
    h.insert(2, 4) = std::complex(-0.005084, 0.0);
    h.insert(2, 6) = std::complex(0.074734, 0.0);
    h.insert(2, 7) = std::complex(0.037308, 0.0);
    h.insert(2, 12) = std::complex(-0.03278, 0.0);
    h.insert(2, 14) = std::complex(0.07338000000000001, 0.0);
    h.insert(2, 15) = std::complex(0.029996, 0.0);
    h.insert(3, 0) = std::complex(-0.03531999999999999, 0.0);
    h.insert(3, 2) = std::complex(0.003558000000000004, 0.0);
    h.insert(3, 3) = std::complex(0.20929200000000003, 0.0);
    h.insert(3, 4) = std::complex(0.029996, 0.0);
    h.insert(3, 6) = std::complex(0.037308, 0.0);
    h.insert(3, 7) = std::complex(0.003558000000000004, 0.0);
    h.insert(3, 12) = std::complex(0.115704, 0.0);
    h.insert(3, 14) = std::complex(0.029996, 0.0);
    h.insert(3, 15) = std::complex(-0.03531999999999999, 0.0);
    h.insert(4, 0) = std::complex(-0.03146600000000001, 0.0);
    h.insert(4, 2) = std::complex(-0.005084, 0.0);
    h.insert(4, 3) = std::complex(0.029996, 0.0);
    h.insert(4, 4) = std::complex(-0.7479680000000001, 0.0);
    h.insert(4, 6) = std::complex(-0.013778000000000002, 0.0);
    h.insert(4, 7) = std::complex(0.07338000000000001, 0.0);
    h.insert(4, 12) = std::complex(0.03505799999999999, 0.0);
    h.insert(4, 14) = std::complex(0.010668, 0.0);
    h.insert(4, 15) = std::complex(-0.03278, 0.0);
    h.insert(5, 1) = std::complex(-0.024489999999999998, 0.0);
    h.insert(5, 5) = std::complex(0.030314000000000035, 0.0);
    h.insert(5, 13) = std::complex(0.06313, 0.0);
    h.insert(6, 0) = std::complex(-0.005084, 0.0);
    h.insert(6, 2) = std::complex(0.074734, 0.0);
    h.insert(6, 3) = std::complex(0.037308, 0.0);
    h.insert(6, 4) = std::complex(-0.013778000000000002, 0.0);
    h.insert(6, 6) = std::complex(-0.20609599999999986, 0.0);
    h.insert(6, 7) = std::complex(0.074734, 0.0);
    h.insert(6, 12) = std::complex(0.010668, 0.0);
    h.insert(6, 14) = std::complex(-0.013778000000000002, 0.0);
    h.insert(6, 15) = std::complex(-0.005084, 0.0);
    h.insert(7, 0) = std::complex(0.029996, 0.0);
    h.insert(7, 2) = std::complex(0.037308, 0.0);
    h.insert(7, 3) = std::complex(0.003558000000000004, 0.0);
    h.insert(7, 4) = std::complex(0.07338000000000001, 0.0);
    h.insert(7, 6) = std::complex(0.074734, 0.0);
    h.insert(7, 7) = std::complex(-0.09481, 0.0);
    h.insert(7, 12) = std::complex(-0.03278, 0.0);
    h.insert(7, 14) = std::complex(-0.005084, 0.0);
    h.insert(7, 15) = std::complex(0.01627, 0.0);
    h.insert(8, 8) = std::complex(0.03458600000000009, 0.0);
    h.insert(8, 10) = std::complex(0.06313, 0.0);
    h.insert(8, 11) = std::complex(-0.18036, 0.0);
    h.insert(9, 9) = std::complex(2.115828, 0.0);
    h.insert(10, 8) = std::complex(0.06313, 0.0);
    h.insert(10, 10) = std::complex(0.030314000000000035, 0.0);
    h.insert(10, 11) = std::complex(-0.024489999999999998, 0.0);
    h.insert(11, 8) = std::complex(-0.18036, 0.0);
    h.insert(11, 10) = std::complex(-0.024489999999999998, 0.0);
    h.insert(11, 11) = std::complex(0.48685600000000007, 0.0);
    h.insert(12, 0) = std::complex(-0.09482, 0.0);
    h.insert(12, 2) = std::complex(-0.03278, 0.0);
    h.insert(12, 3) = std::complex(0.115704, 0.0);
    h.insert(12, 4) = std::complex(0.03505799999999999, 0.0);
    h.insert(12, 6) = std::complex(0.010668, 0.0);
    h.insert(12, 7) = std::complex(-0.03278, 0.0);
    h.insert(12, 12) = std::complex(-0.8350720000000001, 0.0);
    h.insert(12, 14) = std::complex(0.03505799999999999, 0.0);
    h.insert(12, 15) = std::complex(-0.09482, 0.0);
    h.insert(13, 1) = std::complex(-0.18036, 0.0);
    h.insert(13, 5) = std::complex(0.06313, 0.0);
    h.insert(13, 13) = std::complex(0.03458599999999998, 0.0);
    h.insert(14, 0) = std::complex(-0.03278, 0.0);
    h.insert(14, 2) = std::complex(0.07338000000000001, 0.0);
    h.insert(14, 3) = std::complex(0.029996, 0.0);
    h.insert(14, 4) = std::complex(0.010668, 0.0);
    h.insert(14, 6) = std::complex(-0.013778000000000002, 0.0);
    h.insert(14, 7) = std::complex(-0.005084, 0.0);
    h.insert(14, 12) = std::complex(0.03505799999999999, 0.0);
    h.insert(14, 14) = std::complex(-0.7479680000000003, 0.0);
    h.insert(14, 15) = std::complex(-0.03146600000000001, 0.0);
    h.insert(15, 0) = std::complex(0.115704, 0.0);
    h.insert(15, 2) = std::complex(0.029996, 0.0);
    h.insert(15, 3) = std::complex(-0.03531999999999999, 0.0);
    h.insert(15, 4) = std::complex(-0.03278, 0.0);
    h.insert(15, 6) = std::complex(-0.005084, 0.0);
    h.insert(15, 7) = std::complex(0.01627, 0.0);
    h.insert(15, 12) = std::complex(-0.09482, 0.0);
    h.insert(15, 14) = std::complex(-0.03146600000000001, 0.0);
    h.insert(15, 15) = std::complex(-0.3509540000000001, 0.0);
    Vqe vqe(h);
    vqe.ftol = 0.0001;
    BENCHMARK([&]() {
        const VqeResult &result = vqe.optimize(circ);
        std::cout << result.optValue << std::endl;
    }, 10);
    return 0;
}