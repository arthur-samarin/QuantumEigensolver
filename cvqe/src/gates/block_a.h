#ifndef GATES_BLOCK_A_H
#define GATES_BLOCK_A_H

#include "qcirc.h"

class BlockAGateType : public GateType {
public:
    void apply(Qureg reg, const GateInstance &instance) const override {
        size_t control = instance.targets[0];
        size_t target = instance.targets[1];

        phaseShift(reg, control, instance.parameters[0]);
        rotateY(reg, control, instance.parameters[1]);
        rotateX(reg, target, instance.parameters[2]);
        rotateY(reg, target, instance.parameters[3]);
        controlledNot(reg, control, target);
        rotateY(reg, control, -instance.parameters[1]);
        phaseShift(reg, control, -instance.parameters[0]);
        rotateY(reg, target, -instance.parameters[3]);
        rotateX(reg, target, -instance.parameters[2]);
    }

    size_t getNumberOfTargets() const override {
        return 2;
    }

    size_t getNumberOfParameters() const override {
        return 4;
    }

    std::vector<double> getParametersLowerBound() const override {
        return std::vector<double>(4, -M_PI);
    }

    std::vector<double> getParametersUpperBound() const override {
        return std::vector<double>(4, +M_PI);;
    }
};

#endif //GATES_BLOCK_A_H
