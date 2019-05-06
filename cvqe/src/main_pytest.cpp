#include <Python.h>
#include <iostream>

PyMODINIT_FUNC PyInit_cvqe(void);

int main(int argc, char *argv[]) {
    wchar_t *program = Py_DecodeLocale(argv[0], NULL);
    if (program == NULL) {
        fprintf(stderr, "Fatal error: cannot decode argv[0]\n");
        exit(1);
    }

    /* Add a built-in module, before Py_Initialize */
    PyImport_AppendInittab("cvqe", PyInit_cvqe);

    /* Pass argv[0] to the Python interpreter */
    Py_SetProgramName(program);

    /* Initialize the Python interpreter.  Required. */
    Py_Initialize();

    /* Optionally import the module; alternatively,
       import can be deferred until the embedded script
       imports it. */
    PyObject *module = PyImport_ImportModule("cvqe");

    PyObject *p = PyObject_GetAttrString(module, "hello");
    if (!PyCallable_Check(p)) {
        return 1;
    }
    PyObject *arglist = Py_BuildValue("(s)", "world");
    PyObject *result = PyObject_CallObject(p, arglist);
    Py_DECREF(arglist);

    std::cout << PyUnicode_GetLength(result) << std::endl;

    PyMem_RawFree(program);
    return 0;
}