# Welcome to Jupyter-TinCan!

<img src="https://github.com/nilp0inter/jupyter-tincan/blob/main/art/jupyter-tincan-logo.png?raw=true" align="right"
     alt="Jupyter-Tincan logo" width="120">

In the realm of data science and software development, safeguarding sensitive information is paramount. Traditional approaches, such as using remote desktop interfaces to access Jupyter notebooks, offer security but at a cost to user experience. These methods typically involve a cumbersome 'browser within a browser' setup, leading to ergonomic challenges like conflicting keyboard shortcuts, noticeable latency, and a disconnect from local development tools like VSCode. Often, developers find themselves forced into less efficient workflows, such as committing code remotely instead of locally.

Jupyter-TinCan changes the game by offering a simpler, more intuitive solution. It transforms sensitive text in notebook cells into images, maintaining data security while enhancing user experience. No more cumbersome setups or workflow disruptions – just smooth, secure, and efficient development.

## Installation

```console
$ pip install jupyter-tincan
```

You also need nodejs and have text2svg available.

```console
$ npm install -g text2svg
```

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

## What does it do?

<img src="https://github.com/nilp0inter/jupyter-tincan/blob/main/art/show.png?raw=true" align="center"
     alt="Jupyter-Tincan Showcase" width="100%">

The screenshot above illustrates Jupyter-TinCan's unique approach to securing sensitive data within a JupyterLab environment:

1. Identifiable TinCan Kernel: The kernel is adorned with a subtle tin can icon, signaling that Jupyter-TinCan is operational and safeguarding your notebook's output.

2. Secure Output as Images: Outputs from Python code, like the pandas DataFrame shown, are converted into images. This ensures data confidentiality by preventing the text from being copied directly from the output cell.

3. Shell Command Output Protection: Similarly, the results of shell commands are also rendered as images. What typically would be text output is now a secure image, encapsulating the information while preventing text selection.

Through these measures, Jupyter-TinCan maintains the integrity of sensitive information by presenting it in a visual format that deters extraction or casual copying.

### Acknowledgments

"Jupyter" and the Jupyter logos are trademarks of the NumFOCUS foundation. Our use of these trademarks does not imply any endorsement by Project Jupyter or NumFOCUS. Jupyter-TinCan is an independent project developed to integrate with Jupyter software.

This project is not affiliated with Project Jupyter but is designed to be compatible with and enhance the Jupyter notebook experience.

### Disclaimer

Jupyter-TinCan is experimental software provided 'as-is' without any express or implied warranties. By using this software, users acknowledge the potential risks, such as data loss or incorrect data transformations, and agree to bear full responsibility for any consequences arising from its use. The developers are not liable for any damages or losses incurred from the software's operation or failure.
