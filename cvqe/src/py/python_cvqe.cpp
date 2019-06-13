#include <stdexcept>
#include <boost/python.hpp>
#include <boost/python/list.hpp>
#include <boost/python/extract.hpp>
#include <boost/python/numpy.hpp>
#include <gates/all.h>
#include "qcirc.h"
#include "vqe.h"


namespace bp = boost::python;
namespace np = boost::python::numpy;


struct Vector_of_size_t_from_python_list {
    Vector_of_size_t_from_python_list() {
        boost::python::converter::registry::push_back(
                &convertible,
                &construct,
                boost::python::type_id<std::vector<size_t>>());
    }

    static void *convertible(PyObject *obj_ptr) {
        if (!PyList_Check(obj_ptr)) return nullptr;
        Py_ssize_t listSize = PyList_Size(obj_ptr);
        for (Py_ssize_t i = 0; i != listSize; i++) {
            PyObject * item = PyList_GetItem(obj_ptr, i);
            if (!PyLong_Check(item)) {
                return nullptr;
            }
            PyLong_AsSize_t(item);
            if (PyErr_Occurred() != nullptr) {
                return nullptr;
            }
        }
        return obj_ptr;
    }

    static void construct(
            PyObject *obj_ptr,
            boost::python::converter::rvalue_from_python_stage1_data *data) {
        void *storage = (
                (boost::python::converter::rvalue_from_python_storage<std::vector<size_t>> *)
                        data)->storage.bytes;
        Py_ssize_t listSize = PyList_Size(obj_ptr);
        std::vector<size_t> *v = new(storage) std::vector<size_t>(listSize, 0);
        for (Py_ssize_t i = 0; i != listSize; i++) {
            PyObject * item = PyList_GetItem(obj_ptr, i);
            (*v)[i] = PyLong_AsSize_t(item);
        }
        data->convertible = storage;
    }
};

void SetupEigenConverters();

BOOST_PYTHON_MODULE (cvqe) {
    using namespace bp;
    np::initialize();

    Vector_of_size_t_from_python_list();
    SetupEigenConverters();

    class_<GateType, boost::noncopyable>("GateType", no_init);
    class_ < RxGateType, bases < GateType >> ("RxGateType", no_init);
    class_ < RyGateType, bases < GateType >> ("RyGateType", no_init);
    class_ < RzGateType, bases < GateType >> ("RzGateType", no_init);
    class_ < CnotGateType, bases < GateType >> ("CnotGateType", no_init);
    class_ < BlockAGateType, bases < GateType >> ("BlockAGateType", no_init);

    class_<GateTypes>("GateTypes", no_init)
            .def("rx", &GateTypes::rx, return_value_policy<reference_existing_object>()).staticmethod("rx")
            .def("ry", &GateTypes::ry, return_value_policy<reference_existing_object>()).staticmethod("ry")
            .def("rz", &GateTypes::rz, return_value_policy<reference_existing_object>()).staticmethod("rz")
            .def("cnot", &GateTypes::cnot, return_value_policy<reference_existing_object>()).staticmethod("cnot")
            .def("block_a", &GateTypes::blockA, return_value_policy<reference_existing_object>()).staticmethod(
                    "block_a");
    class_<QCircuit>("QCircuit", init<size_t, size_t>())
            .def_readonly("num_parameters", &QCircuit::getNumberOfParameters)
            .def("set_parameters", &QCircuit::setParameters)
            .def("add_gate", &QCircuit::addGate);
    class_<VqeResult>("VqeResult", no_init)
            .def_readonly("num_evaluations", &VqeResult::numEvaluations)
            .def_readonly("millis_taken", &VqeResult::millisTaken)
            .def_readonly("opt_parameters", &VqeResult::getOptParameters)
            .def_readonly("create_vector", &VqeResult::getOptParameters)
            .def_readonly("opt_value", &VqeResult::optValue);
    class_<Vqe>("Vqe", init<Eigen::MatrixXcd>())
            .def_readwrite("ftol", &Vqe::ftol)
            .def_readwrite("eval_budget", &Vqe::evalBudget)
            .def_readwrite("iter_budget", &Vqe::iterBudget)
            .def("optimize", &Vqe::optimize);
}