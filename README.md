# Lakeshore-Model331-Python
This is a Python class wrapper around `pyserial` for RS-232 serial connections for the remote usage of a Lakeshore Model331.

This module is a work in progress, not all functionality can be expected.

You can read more information about this device from [the manual](https://github.com/psmd-iberutaru/Lakeshore-Model331-Python/blob/master/Lakeshore_Model331_User_Manual.pdf "the manual").

## Installing

There is nothing much to install. There are only the package dependencies:
- `pyserial`

From there, you can just download the [Python module/class file](https://github.com/psmd-iberutaru/Lakeshore-Model331-Python/blob/master/Lakeshore_Model331.py "Python module/class file") and use it from thereon.

## Usage

This module should be imported like any other module. That is:

```python
import Lakeshore_Model331 as lake
```

From there, a Lakeshore Model 331 class instance can be created. (Try not to get confused that both the module and the class are the same name.)

```python
import Lakeshore_Model331 as lake
temp_control = lake.Lakeshore_Model331(port='port_name', baudrate=9600)
```

Here, the terms mean:

* **port** : the name of the port connection, generally a string
* **baudrate** : the baudrate that the temperature controller is set to (the Lakeshore Model 331 default is 9600).

From there, you can send a scip command to the temprature controller like so,

```python
import Lakeshore_Model331 as lake
temp_control = lake.Lakeshore_Model331(port='port_name', baudrate=9600)
# The command to be sent.
scip_command = '*IDN?'
temp_control.send_scip_command(command=scip_command)
# Aliases include .write(), .send(), and .command().
```

Some of this is already taken care of you in the form of a more natural Python interface.

### Reading Temprature 

You can read the temperature that a specific input to the temperature controller is measuring. The device has two inputs: `A` and `B`. We can obtain the temperature reading from either of these inputs.

```python
import Lakeshore_Model331 as lake
temp_control = lake.Lakeshore_Model331(port='port_name', baudrate=9600)

# Read the temperature input from A.
tempA_kelvin = temp_control.read_kelvin(input_letter='A', dtype=float)
# Read the temperature input from B.
tempB_kelvin = temp_control.read_kelvin(input_letter='B', dtype=float)
```

The function above reads the temperature, in units Kelvin, and reports it back. The parameter `dtype` serves as a way to customize the output type from the function. Ordinarily, the output from this function is a string, but by specifying a `dtype` type, the function will attempt to convert to the type specified. If it cannot, then it will just return the string response.

## Contributing

### Documentation

There is no need for any more documentation for the usage of this module other than this README.md or from the Python class docstrings. Please put any contributing documentation there.

### Development

This module is still in passive development. Feel free to add a feature and submit a pull request. As the general command reference is provided in the manual, new additions will likely be mapping those commands to more native Python objects.

### Licence

This module is licensed under the MIT License.



