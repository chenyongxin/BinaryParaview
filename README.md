# BinaryParaview
> Output visuailzation result to Paraview in binary

## Motivation
VTK/Paraview provides a [document](https://vtk.org/wp-content/uploads/2015/04/file-formats.pdf) for users to write visualization result in Paraview readable file format. However, it lacks examples to show how to output the visualization result in binary with the code. To output data in binary format is more tricky than in ASCII format. This repository tries to use as simple as possible cases to show how to do this.

## Introduction
This repository supports rectilinear, structured and unstructured grid in both legacy format and XML format. In XML format, both serial and parallel implementations are supported. The sketch below shows the examples of structured and unstructured grids used in this repository. Three implementations are (a) a 2D arch, (b) a 3D arch and (c) a 3D arch in parallel. The grid generator can be found in the folder `grid`. All the examples are in the root path. The scripts to write data in legacy and XML formats are in the folder `writeParaview`.

![Sketch](https://github.com/chenyongxin/BinaryParaview/blob/master/figures/sketch.png?raw=true)

## Usage
First of all, add the path of BinaryParaview to PYTHONPATH:
```
PYTHONPATH=path\to\BinaryParaview:$PYTHONPATH
```
To run serial examples, just simply execute following commands in Terminal in Mac/Linux or cmd in Windows in the folder `examples`:
```
python Legacy_***.py
```
or/and
```
python Serial_XML_***.py
```
or just click `run` in IDE.

To run parallel examples, you should have `mpi4py` installed and then execute the following commands:
```
mpiexec -n 3 python Parallel_XML_***.py
```
which uses 3 processors to execute the python code. Yes, I used an ODD number.

## Notes
* `struct.pack` is used to write binary data. For example, `struct.pack("fff", *[1,2,3])` and `struct.pack("iii", *[1,2,3])` pack data into 3 single-precision float and integer numbers respectively.
* Legacy format only supports writing data in big endian order.  To write in big endian order, a `>` should be added in front of format characters. For example, `struct.pack(">fff", *[1,2,3])` packs data in big endian order.
* In XML format, only `appended`  is used in this repository. The appended data section begins with the first character after the underscore `_` inside the `AppendedData` element. Data array has a format `[#bytes][DATA]`, where `[#bytes]` is an integer value to specify the number of bytes in the block of data following it.  
