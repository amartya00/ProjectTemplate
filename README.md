# **Bob**
## Status
[![codecov](https://codecov.io/gh/amartya00/ProjectTemplate/branch/master/graph/badge.svg)](https://codecov.io/gh/amartya00/ProjectTemplate)
[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/064fff2537d14417a2fb2a83fc4e900f)](https://www.codacy.com/app/amartya00/ProjectTemplate?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=amartya00/ProjectTemplate&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/064fff2537d14417a2fb2a83fc4e900f)](https://www.codacy.com/app/amartya00/ProjectTemplate?utm_source=github.com&utm_medium=referral&utm_content=amartya00/ProjectTemplate&utm_campaign=Badge_Coverage)

## About

Bob is a tool to help you quickly get from source code to installable packages.

### TL;DR
  - Tool resolves dependencies.
  - Tool also packages application as a [**snap**](https://snapcraft.io/).
  - Tool save you time and make you happy.

### Long version
Did you try to build a project and spend hours building its dependencies? Then spend a couple more trying to cook a docker image or EC2 AMI trying to create a deployable environment for your code? If yes, then continue reading...

Most programming languages have their own dependency management systems. Java has Maven, Python has pip. There is no standardized one for c++. Also, what if you code in multiple languages and have a lot of private dependencies that you do not care to upload to the programming language specific repositories?

I faced these problems. So to help me reduce the time spent bootstrapping and focus more on coding, and to teach myself python with some interesting project, I started to develop **Bob**.

The idea behind Bob is simple. It should help me quickly go from source code to installable snap packages. **Snap packages** are central to Bob. Snap is a packaging format for apps and solves a lot of problems regarding runtime compatibilities. If you are not familiar with snaps, please read a little bit about them [here](https://snapcraft.io/). Snapcraft is an awesome piece of technology and definitely worth considering whether you want to create server apps or desktop apps.  

Moving on; somewhere on the internet, I have a bunch of tar files, that contain libraries and headers that I want to use with my project. Bob goes online and fetches them for me. It also helps the build system use these fetched dependencies. 

And when I  am done with the coding, Bob helps me package my code into installable **snap** packages or dependency tars to be used in other projects.  

The downloading and bootstrapping of the dependencies is generic and should be same across programming languages.
Variations occur for building projects. Currently supported build tools are:
  - [cmake](https://cmake.org/).
  
 ## Getting started guide
Following is a step by step guide to get started with a Bob project. First let's install the Bob onto your machine.

### Installation (from source)
***Clone this repository and install with pip.*** The following instructions were carried out on a ```Ubuntu 18.10``` machine. Use corresponding installation instructions for your distribution.

```console
machine:~$ sudo apt-get install python3-pip
machine:~$ cd
machine:~$ git clone https://github.com/amartya00/ProjectTemplate.git
machine:~$ cd ProjectTemplate
machine:~$ sudo pip3 install .
machine:~$ bob --help
```
On running the last command, you should get some help information, given everything else worked.

### Your first Bob project
#### Building the project.
The necessary file to use Bob for a project is the ```md.json``` file. This file contains all the information that will tell Bob what to do with your project. More specifically, this file contains information about:
  - Dependencies needed for the project:
    - Names of the dependency packages.
    - Versions of the dependency packages.
    - Download location for the dependency packages.
  - Build system to use for the project. Currently supported build systems are:
    - [**CMake**](https://cmake.org/)

So let's go ahead and create this file. To do that, lets run the following commands:
```console
machine:$ cd
machine:$ mkdir HelloBob
machine:$ cd HelloBob
machine:$ touch md.json
```

Now copy the contents of [this file](https://github.com/amartya00/ProjectTemplate/blob/master/tst/steps/data/md.json) in your newly created ```md.json``` file. 

Now let's create some source files. We will use our test project for this demo. Copy over the ```headers```, ```lib``` folders and the ```CMakeLists.txt``` file from [here](https://github.com/amartya00/ProjectTemplate/tree/master/tst/steps/data). At this point, we should have the project that is ready to be compiled.

To build the project, simply type the following from the project's root directory:
```console
machine:$ bob
```

This will build the project. If you read the ```CMakeLists.txt``` files, you will notice that we wanted to build a library called ```libtest.so```. You might also notice that a new folder has appeared called ```build```. Now go into the build folder and see what's there. If you have used ```cmake``` before, this should look pretty familiar to you. The library I talked about is in the lib folder in the build directory.

```console
machine:$ cd build
machine:$ ls lib/
```

#### Creating packages.
Now let's try to create some packages. To do so, simply run:
```console
machine:$ bob -s Package
```

Did you get this error message?

***[ERROR] Error occured Could not package because: You might not have snapcraft installed. Error message: [Errno 2] No such file or directory: 'snapcraft': 'snapcraft'***

If you did that is because, as the error message says, you do not have ```snapcraft``` installed. What I should have mentioned is that our ```md.json``` file contains instructions to create an installable **snap** package. To be able to do that, you have to have ```snapcraft``` installed on your system. Now let's install ```snapcraft``` and try again. Again, if you have read up to this point I am assuming you have made yourself at least somewhat familiar with snaps. Snaps are a central part behind this tool.

```console
machine:$ sudo apt-get install snapcraft
machine:$ bob -s Package
```

Now look inside your build folder. You shoild see a snap package there:

```console
machine:$ ls build/*.snap
build/myappsnap_23.0_amd64.snap
```

Et voilà, you have gone from source code to having a snap package in a couple of commands! I know this very short tutorial raises more questions than it answers, but if you are even a little impressed, keep reading to understand the ideas behind this tool.
  

