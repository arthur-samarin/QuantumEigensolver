#ifndef GATES_BASIC_H
#define GATES_BASIC_H

#include "qcirc.h"

class RotateGateType : public GateType {
public:
    size_t getNumberOfTargets() const override {
        return 1;
    }

    size_t getNumberOfParameters() const override {
        return 1;
    }

    std::vector<double> getParametersLowerBound() const override {
        return std::vector<double>{-M_PI};
    }

    std::vector<double> getParametersUpperBound() const override {
        return std::vector<double>{+M_PI};
    }
};

class RxGateType : public RotateGateType {
public:
    void apply(Qureg reg, const GateInstance &instance) const override {
        rotateX(reg, instance.targets[0], instance.parameters[0]);
    }
};

class RyGateType : public RotateGateType {
    void apply(Qureg reg, const GateInstance &instance) const override {
        rotateY(reg, instance.targets[0], instance.parameters[0]);
    }
};

class RzGateType : public RotateGateType {
    void apply(Qureg reg, const GateInstance &instance) const override {
        rotateZ(reg, instance.targets[0], instance.parameters[0]);
    }
};

class CnotGateType : public GateType {
    void apply(Qureg reg, const GateInstance &instance) const override {
        controlledNot(reg, instance.targets[0], instance.targets[1]);
    }

    size_t getNumberOfTargets() const override {
        return 2;
    }

    size_t getNumberOfParameters() const override {
        return 0;
    }

    std::vector<double> getParametersLowerBound() const override {
        return std::vector<double>(0);
    }

    std::vector<double> getParametersUpperBound() const override {
        return std::vector<double>(0);
    }
};

#endif //GATES_BASIC_H
