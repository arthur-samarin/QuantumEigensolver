#ifndef VQE_H
#define VQE_H

#include <Eigen/Sparse>
#include "qcirc.h"

typedef Eigen::SparseMatrix<std::complex<double>> Hamiltonian;
typedef Eigen::VectorXcd Wavefunc;


class VqeResult {
public:
    size_t numEvaluations;
    uint64_t millisTaken;
    Eigen::VectorXd optParameters;
    double optValue;

    VqeResult(size_t numEvaluations, uint64_t millisTaken, Eigen::VectorXd optParameters, double optValue);

    Eigen::VectorXd getOptParameters() {
        return optParameters;
    }
};


class Vqe {
private:
    Hamiltonian h;
    QuESTEnv questEnv;
public:
    double ftol = 1e-5;
    size_t iterBudget = 0;
    size_t evalBudget = 0;

    explicit Vqe(const Eigen::MatrixXcd &h);
    ~Vqe();
    VqeResult optimize(QCircuit& circuit);
};

#endif //VQE_H
