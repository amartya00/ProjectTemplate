# Build helper
## Status
[![codecov](https://codecov.io/gh/amartya00/ProjectTemplate/branch/master/graph/badge.svg)](https://codecov.io/gh/amartya00/ProjectTemplate)

## About
This utility automates a lot of the build process while developing code. This tool leverages [cmake](https://cmake.org/) and [snapcraft](https://snapcraft.io/) to help work on your code and abstracting away all the headache of building, resolving dependencies and packaging.

## Overview of workflow
This tool currently revolves around a specific workflow. I develop code in c++ that needs to be linked to libraries and needs to find headers to build. All the software packages compatible with this have a ```md.json``` file containing a list of dependencies and build parameters. Below is a list of its capabilities. I have explained some terms after that.

* Resolve the entire dependency graph for your project.
* Download all the required dependencies and install them in a local folder where your ```CMakeLists.txt``` can find them.
* Automatically generate ```snapcraft.yaml``` if you are packaging your code into a snap and build the snap.
* Build snap parts (libraries and headers). 

The detailed description of the development process is listed in the **details** section.

## Building and installing.
## Requirements
* Python 3
* Nosetests 3

## Commands to build and install
```shell
$ git clone https://github.com/amartya00/ProjectTemplate.git
$ cd ProjectTemplate
$ nosetests-3.4 tst/ --nocapture -v
$ mkdir build
$ cd build
$ cmake ..
$ make
$ sudo make install
```
## Details of workflow
The workflow that this tool supports involves 4 main types of things:
* Source code
* Snap-parts (libs). These are libraries packaged into tar files with an accompanying ```CMakeLists.txt``` file. These are installed automatically into a local cache to be linked while building, or included while a snap. [Here](https://s3.amazonaws.com/amartya00-service-artifacts/a/0.1/a.tar) is a sample.
* Snap-parts (headers). These are like the libs but they contain headers which are automatically installed in a local cache. The ```include_directories``` can make use of this folder when building. [Here](https://s3.amazonaws.com/amartya00-service-artifacts/a-headers/0.1/a-headers.tar) is a sample.
* Snaps. You can build your project into a snap. The ```snapcraft.yaml``` file is automatically generated from your specified build configuration in the ```md.json``` file.

## Example workflow for building a snap
Lets do a walkthrough of a simple build process. Go to the ```tst/testprojects``` folder in the root of this package. It contains 2 sample projects: "main" and "b". Let's try to build the "main" project.

### Metadata file
Go to the "main" folder and observe the ```md.json``` file, which looks like this:
```json
{
    "Package": "testmain",
    "Version": "0.1",
    "BuildDeps": [
        {
            "Package": "a",
            "Version": "0.1"
        },
        {
            "Package": "b",
            "Version": "0.2"
        },
        {
          "Package": "a-headers",
          "Version": "0.1"
        },
        {
          "Package": "b-headers",
          "Version": "0.2"
        }
    ],
    "Packaging": [
      {
        "Name": "testmain",
        "Type": "snap",
        "Version": "0.1",
        "Summary": "Blah blah.",
        "Description": "Blah blah.",
        "Confinement": "devmode",
        "Grade": "devel",
        "Apps": [
          {
            "Name": "main",
            "Command": "main.out"
          }
        ]
      }
    ]
}
```

Observe the dependencies in the ```BuildDeps``` section. This section specifies the dependencies needed to build the "main" package. All these packages exist in my (publicly readable) S3 bucket. You can download these for inspection by running:
```
wget https://s3.amazonaws.com/amartya00-service-artifacts/<PACKAGE_NAME>/<PACKAGE_VERSION>/<PACKAGE_NAME>.tar
```

Observe the ```Packaging``` section. This contains a bunch of parameters needed for generating the ```snapcraft.yaml``` file. Documentation about snapcraft yaml file is available [here](https://docs.snapcraft.io/build-snaps/syntax). The "parts" section of the snapcraft yaml file is populated from the dependencies.

### Build steps
Now that you are in the "main" folder and want to build the project, run the following command:
```
python ../../../bin/project.py build
```

This pulls in all dependencies and installs them in a folder called ```.packagecache```. Let's observe the contents of ```.packagecache```.

```
.
├── dependencies.json
├── headers
│   ├── a
│   │   └── a.h
│   ├── b
│   │   └── b.h
│   └── k
│       └── c.h
└── lib
    ├── liba.so
    ├── libb.so
    └── libk.so

```

Packages a, b, a-headers and b-headers were installed in proper folders. All the header packages are installed in appropriately named folder "headers" and the libraries are installed in an appropriately named folder called "lib". Notice the file ```libk.so```. The package "k" is a dependency of "a" and "b" and not directly of "main". This tool pulls down the entire dependency graph and not just the immediate dependencies.

### Package steps
Now that we have built the project, lets package it into a snap. Just run this command:
```
python ../../../bin/project.py package
```

This builds the project into a snap and puts the snap in the build folder. Observe the ```testmain_0.1_amd64.snap``` file in the build folder.

## Example workflow for building a snap-part
Now let's do a walkthrough for building a snap part. Navigate to the folder "b". This is a sample project. The code gets built into a library: ```libb.so``` and the header files get packaged up into a headers package.

### Metadata
Let's observe the ```md.json``` file. 
```json
{
  "Package": "b",
  "Version": "0.2",
  "BuildDeps": [
    {
      "Package": "k-headers",
      "Version": "0.1"
    }
  ],
  "Dependencies": [
    {
      "Package": "k",
      "Version": "0.1"
    }
  ],
  "Packaging": [
    {
      "Name": "b",
      "Type": "snap-part",
      "PartType": "lib",
      "LibName": "libb.so"
    },
    {
      "Name": "b-headers",
      "Type": "snap-part",
      "PartType": "headers",
      "HeadersSource": "headers",
      "HeadersDest": "b"
    }
  ]
}
```

Observe the ```Packaging``` section. It has 2 rules. One builds the snap-part library package ```b.tar```. The second one builds the headers package ```b-headers.tar```.

### Build commands
To build this project, just run a similar command to the last one:
```
python ../../../bin/project.py build
```

### Package commands
To package up the project, run the following command:
```
python ../../../bin/project.py package
```
As mentioned before, the build folder will contain 2 tar files:
* ```b.tar```
* ```b-headers.tar```

