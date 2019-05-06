#ifndef QCIRC_H
#define QCIRC_H

#include <utility>
#include <vector>
#include <cmath>
#include <QuEST.h>
#include <stdexcept>

class GateInstance;

class GateType {
public:
    virtual void apply(Qureg reg, const GateInstance &instance) const = 0;

    virtual size_t getNumberOfTargets() const = 0;

    virtual size_t getNumberOfParameters() const = 0;

    virtual std::vector<double> getParametersLowerBound() const = 0;

    virtual std::vector<double> getParametersUpperBound() const = 0;
};

class GateInstance {
public:
    const GateType &typ;
    std::vector<size_t> targets;
    std::vector<double> parameters;

    GateInstance(const GateType &typ, std::vector<size_t> targets, std::vector<double> parameters);
};

class QCircuit {
public:
    const size_t numQubits;
    const size_t initialState;
    std::vector<GateInstance> gates;

    QCircuit(size_t numQubits, size_t initialState);

    void apply(Qureg reg) const;
    size_t getNumberOfParameters() const;
    void setParameters(const std::vector<double>& parameters);
    void addGate(GateType& typ, std::vector<size_t> targets);
};

#endif //QCIRC_H
