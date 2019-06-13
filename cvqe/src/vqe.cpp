#include <utility>
#include <random>
#include <cmath>

#include "vqe.h"
#include "cmaes.h"

using namespace libcmaes;

VqeResult::VqeResult(size_t numEvaluations, uint64_t millisTaken, Eigen::VectorXd optParameters, double optValue) :
        numEvaluations(numEvaluations), millisTaken(millisTaken),
        optParameters(std::move(optParameters)), optValue(optValue) {}

Vqe::Vqe(const Eigen::MatrixXcd &h) : h(h.sparseView()) {
    if (h.rows() != h.cols()) {
        throw std::invalid_argument("Hamiltonian must be square matrix");
    }
    questEnv = createQuESTEnv();
}

Vqe::~Vqe() {
    destroyQuESTEnv(questEnv);
}

static void reverseQubitsOrder(Wavefunc& w) {
    size_t n = 1;
    while (w.size() > (1 << n)) {
        n += 1;
    }

    for (Wavefunc::Index i = 0; i < w.size(); i++) {
        size_t k = i;
        size_t reverse = 0;
        for (size_t j = 0; j < n; j++) {
            reverse <<= 1u;
            reverse |= k & 1u;
            k >>= 1u;
        }
        if (i < Wavefunc::Index(reverse)) {
            std::swap(w[i], w[reverse]);
        }
    }
}

static Wavefunc extractWavefunc(const Qureg& reg) {
    Wavefunc w(reg.numAmpsTotal);
    for (Wavefunc::Index i = 0; i < w.size(); i++) {
        w[i] = std::complex(reg.stateVec.real[i], reg.stateVec.imag[i]);
    }
    reverseQubitsOrder(w);
    return w;
}

VqeResult Vqe::optimize(QCircuit &circuit) {
    Qureg reg = createQureg(circuit.numQubits, questEnv);
    try {
        FitFunc fitFunc = [this, &circuit, reg](const double *x, const int N) {
            circuit.setParameters(std::vector<double>(x, &x[N]));
            circuit.apply(reg);
            Wavefunc w = extractWavefunc(reg);
            std::complex<double> exValue = w.dot(h*w);
            if (abs(exValue.imag()) > 1e-10) {
                throw std::invalid_argument("Expectation value is not real");
            }
            return exValue.real();
        };

        if (circuit.getNumberOfParameters() == 0) {
            double x;
            return VqeResult(1, 1, Eigen::VectorXd(0), fitFunc(&x, 0));
        }

        std::default_random_engine rng;
        size_t dim = circuit.getNumberOfParameters();
        std::vector<double> x0(dim);
        std::vector<double> lBounds(dim);
        std::vector<double> uBounds(dim);
        size_t n = 0;

        for (const GateInstance &gate : circuit.gates) {
            const std::vector<double> &lBound = gate.typ.getParametersLowerBound();
            const std::vector<double> &uBound = gate.typ.getParametersUpperBound();
            for (size_t i = 0; i < gate.typ.getNumberOfParameters(); i++) {
                lBounds[n + i] = lBound[i];
                uBounds[n + i] = uBound[i];
                std::uniform_real_distribution<double> distribution(lBound[i], uBound[i]);
                x0[n + i] = distribution(rng);
            }
            n += gate.typ.getNumberOfParameters();
        }

        double sigma = 0.5;
        GenoPheno<pwqBoundStrategy> gp(&lBounds[0], &uBounds[0], dim);


        CMAParameters<GenoPheno<pwqBoundStrategy>> cmaparams(x0, sigma, -1, 0, gp);
        cmaparams.set_ftolerance(ftol);
        if (iterBudget > 0) {
            cmaparams.set_max_iter(iterBudget);
        }
        if (evalBudget > 0) {
            cmaparams.set_max_fevals(evalBudget);
        }

        CMASolutions cmasols = cmaes<>(fitFunc, cmaparams);

        destroyQureg(reg, questEnv);

        return VqeResult(cmasols.fevals(), cmasols.elapsed_time(), gp.pheno(cmasols.best_candidate().get_x_dvec()),
                cmasols.best_candidate().get_fvalue());
    } catch (const std::string &ex) {
        destroyQureg(reg, questEnv);
        throw;
    }
}
