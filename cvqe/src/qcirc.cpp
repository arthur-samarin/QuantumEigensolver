#include <utility>

#include <iostream>
#include <vector>
#include "qcirc.h"



GateInstance::GateInstance(const GateType &typ, std::vector<size_t> targets, std::vector<double> parameters) :
        typ(typ), targets(std::move(targets)), parameters(std::move(parameters)) {
    if (this->typ.getNumberOfTargets() != this->targets.size()) {
        throw std::invalid_argument("Incorrect size of targets");
    }
    if (this->typ.getNumberOfParameters() != this->parameters.size()) {
        throw std::invalid_argument("Incorrect size of parameters");
    }
}

QCircuit::QCircuit(const size_t numQubits, const size_t initialState) : numQubits(numQubits),
                                                                        initialState(initialState) {
    if (initialState >= (1u << numQubits)) {
        throw std::invalid_argument("Incorrect initialState");
    }
}

void QCircuit::apply(Qureg reg) const {
    initZeroState(reg);
    for (size_t i = 0; i < numQubits; i++) {
        if (((initialState >> i) & 1) != 0) {
            pauliX(reg, numQubits - 1 - i);
        }
    }
    for (const GateInstance& gate : gates) {
        gate.typ.apply(reg, gate);
    }
}

size_t QCircuit::getNumberOfParameters() const {
    size_t n = 0;
    for (const GateInstance& gate : gates) {
        n += gate.typ.getNumberOfParameters();
    }
    return n;
}

void QCircuit::setParameters(const std::vector<double> &parameters) {
    if (getNumberOfParameters() != parameters.size()) {
        throw std::invalid_argument("Bad parameters size");
    }
    size_t n = 0;
    for (GateInstance& gate : gates) {
        gate.parameters.assign(parameters.begin() + n, parameters.begin() + n + gate.typ.getNumberOfParameters());
        n += gate.typ.getNumberOfParameters();
    }
}

void QCircuit::addGate(GateType &typ, std::vector<size_t> targets) {
    for (size_t target: targets) {
        if (target >= numQubits) {
            throw std::invalid_argument("Bad target");
        }
    }
    gates.emplace_back(typ, std::move(targets), std::vector<double>(typ.getNumberOfParameters(), 0.0));
}
