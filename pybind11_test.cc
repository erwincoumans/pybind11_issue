
#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <stdio.h>

namespace py = pybind11;

struct MyClass
{
	int size_;
	float* data_;

	py::array_t<float> map_data_;

	MyClass(int sz)
	:size_(sz)
	{
		data_= (float*) malloc(sz*sizeof(float));
		for (int i=0;i<size_;i++)
			data_[i] = float(i);
		//want map_data_ to share data_ as numpy array without copy
		map_data_ = py::array_t<float>(size_, data_);	
	}
	void set_elem(int pos, float value)
	{
		if (pos>=0 && pos<size_)
			{
				data_[pos] = value;
				printf("ok!\n");
			} else
			{
				printf("pos out of range(%d, %d)\n", pos, size_);
			}

	}
	virtual ~MyClass()
	{
		free(data_);
	}
};

     

PYBIND11_MODULE(pybind11_test, m) {
	 py::class_<MyClass>(m, "MyClass")
	 .def(py::init<int>())
	 .def("set_elem", &MyClass::set_elem)
   .def_readonly("size_", &MyClass::size_)
   .def_readwrite("data", &MyClass::map_data_)
   	;
}
