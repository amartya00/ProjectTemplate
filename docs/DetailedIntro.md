# Explanation of Bob in details

## Workflow stages
Bob is a workflow that works in stages. The stages in the workflow are:
  - ***Bootstrap dependencies.***
  - ***Build the code.***
  - ***Run tests.***
  - ***Package the code into a tar or a snap.***
  
### Bootstrap dependencies
The responsibility of this phase is to resolve the entire dependency grapg and download all the requirements and put them in a proper place.
Currently, you have 2 ways of storing the dependencies to be fetched by bob.
  - A public file server, from where the tool can do wget.
  - Your own S3 bucket from where the tool can get the dependencies.
  
In either case, Bob expects a defined file structure:
  - For general file server: ```http://myfileserver.com/<PACKAGE_NAME>/<PACKAGE_VERSION>/<PACKAGE_NAME>.tar```
  - For S3: ```Buclet=YourBucket; Key=<PACKAGE_NAME>/<PACKAGE_VERSION>/<PACKAGE_NAME>.tar```
  
After fetching the dependency tar file, it is saved in a global cache folder on your host, usually ```$HOME/.packagecache``` and extract it.
This folder will contain all your downloaded dependencies for all your projects. The folder hierarchy is the same: ```$HOME/.packagecache/<PACKAGE_NAME>/<PACKAGE_VERSION>/<PACKAGE_NAME>.tar```

After the dependency is downloaded and extracted, only the ones that are needed by your project will be installed in a cache folder, local to the project.
The project sepcific cache folder is `````$PROJECT_ROOT/.packagecache`````. The local package cache has a different structure. It has 2 sub-folders:
  - libs: Contains the libraries (jars, ``.so`` files, etc)
  - headers: Contains header files needed for build.
  
When the build starts, Bob invokes the build tool with the proper folders for libs and headers. For example, CMake is called with:

```commandline
machine:$ cmake -DPACKAGE_CACHE=$PROJECT_ROOT/.packagecache
```

### Start the build
This step, depending on the build tool, invokes the proper tool, with proper package cache arguments. Currently, supported build systems are:
  - ***Cmake***
  
### Run the tests
This is also dependent on the build system. After the build is complete, Bob will run the tests. Currently, the supported test runners are:
  - ***Ctest***
  
### Package the code
In this stage, Bob will package your code into either:
  - A tarball which can be used by other projects as its dependency.
  - An installable snap package.
  
## Tool usage
Bob can be run in 2 ways:
  - You can run the end to end workflow.
    - In this mode the stages that are run are: ```bootstrap, build, test```
    - NOTE: The package stage is not run.
    - To invoke this mode, simply run: ``machine:$ bob``
    
  - You can run a single stage.
    - Invoke a single stage like: ```bob -S <StageName>```
    - The available stages are:
      - *Clean*
      - Bootstrap
      - Build
      - Test
      - *Package*
    - The ones in italics are not run as a part of the default workflow.
    - Note when you run a single stage, it does not check if previous necessary stages have been run. So it might fail in weird ways. Example if you run package bithout running build, it will fail with an error message.
