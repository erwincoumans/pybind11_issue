import pybind11_test as t
a = t.MyClass(10)
print(a.data)
a.set_elem(0,123)
print(a.data)
