<!-- PYADI-IIO README -->

<p align="center">
<img src="" width="500" alt="Analog Logo"> </br>
</p>
<a href="https://www.python.org/download/releases/3.7.0/">
<img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="Python Version">
</a>

<a href="http://analogdevicesinc.github.io/tinyradtool/">
<img alt="GitHub Pages" src="https://img.shields.io/badge/docs-GitHub%20Pages-blue.svg">
</a>

<a href="https://ez.analog.com">
<img alt="EngineerZone" src="https://img.shields.io/badge/Support-on%20EngineerZone-blue.svg">
</a>

<a href="https://wiki.analog.com">
<img alt="Analog Wiki" src="https://img.shields.io/badge/Wiki-on%20wiki.analog.com-blue.svg">
</a>
</p>

---

### TinyRadTool: Analog Devices python GUI application for EV-TINYRAD24 24GHz Radar Evaluation Platform

The EV-TINYRAD24G is a radar evaluation module that allows the implementation and testing of radar sensing applications in the 24 GHz industrial, scientific, and medical (ISM) band. TinyRadTool Software is PC evaluation software of EV-TINYRAD24G, with an included graphical user interface (GUI), that performs radar signal processing steps to yield radar point clouds that can be visualized as range doppler or range angle plots. This software main functions can be categorized as follow: a) Communicate with controller to change settings. b) communicate with digital signal processing module to get processed data and visualize. 

```shell
> & python TinyRadTool.py
```

### Installing from source

```shell
> & git clone https://github.com/analogdevicesinc/tinyradtool.git
> & cd tinyradtool
> & pip install -r requirements.txt
```

### Dependencies

| Dependency    | Version        | Link         |
| ------------- | -------------  |------------- |
| PyQt5         |5.15.7          |              |
| numpy         |  1.10.4        |              |
| pyqtgraph     | 0.9.10         |              |
| pyusb         | 1.2.1          |              |
