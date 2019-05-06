#ifndef GATES_ALL_H
#define GATES_ALL_H

#include "basic.h"
#include "block_a.h"

class GateTypes {
public:
    static RxGateType &rx() {
        static RxGateType rx;
        return rx;
    }

    static RyGateType &ry() {
        static RyGateType ry;
        return ry;
    }

    static RzGateType &rz() {
        static RzGateType rz;
        return rz;
    }

    static CnotGateType &cnot() {
        static CnotGateType cnot;
        return cnot;
    }

    static BlockAGateType &blockA() {
        static BlockAGateType blockA;
        return blockA;
    }
};

#endif //GATES_ALL_H
