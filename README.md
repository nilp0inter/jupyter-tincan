# Welcome to Jupyter-TinCan!

<img src="https://github.com/nilp0inter/jupyter-tincan/blob/main/art/jupyter-tincan-logo.png?raw=true" align="right"
     alt="Jupyter-Tincan logo" width="120">

In the realm of data science and software development, safeguarding sensitive information is paramount. Traditional approaches, such as using remote desktop interfaces to access Jupyter notebooks, offer security but at a cost to user experience. These methods typically involve a cumbersome 'browser within a browser' setup, leading to ergonomic challenges like conflicting keyboard shortcuts, noticeable latency, and a disconnect from local development tools like VSCode. Often, developers find themselves forced into less efficient workflows, such as committing code remotely instead of locally.

Jupyter-TinCan changes the game by offering a simpler, more intuitive solution. It transforms sensitive text in notebook cells into images, maintaining data security while enhancing user experience. No more cumbersome setups or workflow disruptions – just smooth, secure, and efficient development.

## Installation

## Usage

You can configure any pre-existing Jupyter kernel to use Jupyter-TinCan. First let's list the kernels we have installed:

```console
$ jupyter kernelspec list
Available kernels:
  python3    /usr/local/share/jupyter/kernels/python3
```

Now let's put the python3 kernel into TinCan mode:

```console
$ mkdir python3-tincan
$ jupyter tincan create-kernel /usr/local/share/jupyter/kernels/python3 > python3-tincan/kernel.json
```

This will create a new kernel spec file called `tincan-python3.json` in the current directory. You can now install this kernel spec into Jupyter:

```console
$ jupyter kernelspec install python3-tincan
```

or

```console
$ jupyter kernelspec install --user python3-tincan
```

### Acknowledgments

"Jupyter" and the Jupyter logos are trademarks of the NumFOCUS foundation. Our use of these trademarks does not imply any endorsement by Project Jupyter or NumFOCUS. Jupyter-TinCan is an independent project developed to integrate with Jupyter software.

This project is not affiliated with Project Jupyter but is designed to be compatible with and enhance the Jupyter notebook experience.
