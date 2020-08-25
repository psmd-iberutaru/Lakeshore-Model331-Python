import serial
import sys
import decimal
import copy

DEFAULT_TIMEOUT = 5

class Lakeshore_Model331():
    """ This is a very simple Python wrapper for the Lakeshore
    Model331 temperature controlers. This uses pyserial as the 
    backbone. This class only supports RS-232 connections.
    
    """
    
    # Internal serial variables.
    _port = str
    _baudrate = int()
    _data = int()
    _parity = None
    _startbits = int()
    _endbits = int()
    _timeout = int()
    
    def __init__(self, port, baudrate=9600, timeout=DEFAULT_TIMEOUT):
        """ This instantiates the instance of this class.

        Parameters
        ----------
        port : string
            The name of the port that this instrument is connected 
            to.
        baudrate : integer (optional)
            The baudrate that the instrument is communicating over.
            It can only be 300, 1200, 9600 as per the instrument 
            specifications.
        timeout : integer (optional)
            The amount of seconds that the class will wait for a 
            responce from the instrument. Defaults to 5 seconds.

        Returns
        -------
        Lakeshore_Model331
        """
        
        # Baudrate can only be 300, 1200, or 9600
        if (baudrate not in (300, 1200, 9600)):
            raise RuntimeError("The baudrate must be 300, 1200, or 9600.")
            
        # Assign internal variables.
        self._port = str(port)
        self._bardrate = int(baudrate)
        self._timeout = int(timeout)
        # These are hardwired into the machine.
        self._data = 7
        self._parity = serial.PARITY_ODD
        self._startbits = 1
        self._endbits = 1
        
        # All done.
        return None

    # The configuration version.
     # This allows a configuration dictionary to be used.
    @classmethod
    def load_configuration(cls, configuration, _flat=False):
        """ This is a function that allows the usage of a 
        dictionary to specify the parameters of the class. The 
        configuration file can be found in the repository.
        Parameters
        ----------
        configuration : dictionary-like
            The configuration dictionary. It must contain the 
            required parameters, else an error will be raised. If
            the limitation paramters are not there, the factory
            defaults will be used instead.
        _flat : boolean (optional)
            Flaten the dictionary before processing. Defaults to 
            False.
        Returns
        -------
        temp_control : Lakeshore_Model331
            A Lakeshore_Model331 class based on the configuration
            parameters.
        """
        # Flatten the dictionary.
        if (_flat):
            config = _ravel_dictionary(
                dictionary=dict(configuration), conflict='raise')
        else:
            config = dict(configuration)

        # Attempt to obtain the serial parameters.
        try:
            port = config['port']
            baudrate = config['baudrate']
            timeout = config['timeout']
        except KeyError:
            raise KeyError("The serial parameters are missing. Required are "
                           "the following: 'port', 'baudrate', and 'timeout'.")

        # Create the instance.
        temp_control = cls(port=port, baudrate=baudrate, timeout=timeout)

        return temp_control
    
    # This allows for the reading of temperature output.
    def read_kelvin(self, input_letter, dtype=str):
        """ This provides the temperature reading in Kelvin from a
        specified input.

        Parameters
        ----------
        input_letter : string
            The letter of the input that the temperature controller
            will report. Must be 'A' or 'B'.
        dtype : type (optional)
            The Python type that the responce should be returned in.
            It defaults to a string if the type provided throws an 
            error during conversion.
        
        Returns
        -------
        responce : dtype
            The responce converted to the dtype provided, or as the
            responce string if conversion failed.
        """
        # Must be either A or B.
        input_letter = str(input_letter).upper()
        if (input_letter not in ('A', 'B')):
            raise RuntimeError("The input letter type must be 'A' or 'B'.")

        # If the user wants an integer type, it does not work without 
        # converting it first to a float.
        if (issubclass(dtype, int)):
            # Convert to a 'float' first for type conversion.
            type_funt = lambda x: dtype(decimal.Decimal(x))
        else:
            type_funt = lambda x: dtype(x)
        
        # Compile the command.
        command = 'KRDG? {input}'.format(input=input_letter)
        # Send the command, capture the responce.
        str_responce = self.send_scip_command(command=command)
        # Send it through their type specified.
        try:
            responce = type_funt(str_responce)
        except Exception:
            responce = str(str_responce)
        finally:
            # All done.
            return responce
        # Code should not reach here.
        raise RuntimeError
        return None

    # Common command interface.
    def send_scip_command(self, command):
        """ This allows any generalized scip command to be sent to 
        the temperature controller. The command should be a string, 
        pre-processed, as this function automatically appends the 
        needed newline.

        Parameters
        ----------
        command : string
            The scip command that is to be sent to the temperature 
            controller.
        
        Returns
        -------
        responce : string
            The responce from the temperature controller.
        
        """
        # The commands must end in a new line terminator.
        ended_command = ''.join([command, '\n'])
        # Convert the command to a proper bytestring.
        bytecommand = bytearray(ended_command, sys.getdefaultencoding())
        
        # Send the command.
        raw_responce = self._send_raw_scip_command(bytecommand=bytecommand)
        
        # Convert the responce to something useable by the user.
        ended_responce = raw_responce.decode(sys.getdefaultencoding())
        responce = ended_responce.strip('\r\n')
        
        # All done.
        return responce
    # Aliases.
    send = write = command = send_scip_command
    
    # Code to write a raw command.
    def _send_raw_scip_command(self, bytecommand): 
        """ This sends a bytearray command to the temperature 
        controller. This function mostly acts as a wrapper around
        pyserial.

        Parameters
        ----------
        bytecommand : bytearray
            The post-processed command, encoded as a bytearray that
            will be sent to the power supply.
        
        Returns
        -------
        responce : bytearray
            The raw responce from the temperature controller, it is
            a bytearray with no post-processing.
        
        """
        # Load the serial connection.
        with serial.Serial(port=self._port, baudrate=self._baudrate, 
                           bytesize=self._data, parity=self._parity, 
                           stopbits=self._endbits, 
                           timeout=self._timeout) as ser:
            # Send the command.
            ser.write(bytecommand)
            # Double check that the timeout is non-zero.
            if (ser.timeout <= 0):
                # Timeout should not be non-zero, using a default
                # for now.
                ser.timeout = DEFAULT_TIMEOUT
                responce = ser.readline()
                # Set timeout back.
                ser.timeout = self._timeout
            else:
                # Read the responce.
                responce = ser.readline()
        # All done.
        return responce
    # Aliases.
    raw = _send_raw_scip_command


def _ravel_dictionary(dictionary, conflict):
    """ This function unravels a dictionary, un-nesting
    nested dictionaries into a single dictionary. If
    conflicts arise, then the conflict rule is used.
    
    The keys of dictionary entries that have dictionary
    values are discarded.
    
    Parameters
    ----------
    dictionary : dictionary
        The dictionary to be unraveled.
    conflict : string
        The conflict rule. It may be one of these:
        
        * 'raise'
            If a conflict is detected, a 
            sparrowcore.DataError will be raised.
        * 'superior'
            If there is a conflict, the least 
            nested dictionary takes precedence. Equal
            levels will prioritize via alphabetical. 
        * 'inferior'
            If there is a conflict, the most
            nested dictionary takes precedence. Equal
            levels will prioritize via anti-alphabetical.
        
    Returns
    -------
    raveled_dictionary : dictionary
        The unraveled dictionary. Conflicts were replaced
        using the conflict rule.
    """
    # Reaffirm that this is a dictionary.
    if (not isinstance(dictionary, dict)):
        dictionary = dict(dictionary)
    else:
        # All good.
        pass
    # Ensure the conflict is a valid conflict type.
    conflict = str(conflict).lower()
    if (conflict not in ('raise', 'superior', 'inferior')):
        raise RuntimeError("The conflict parameter must be one the "
                           "following: 'raise', 'superior', 'inferior'.")
        
    # The unraveled dictionary.
    raveled_dictionary = dict()
    # Sorted current dictionary. This sorting helps
    # with priorities prescribed by `conflict`.
    sorted_dictionary = dict(sorted(dictionary.items()))
    for keydex, itemdex in sorted_dictionary.items():
        # If this entry is a dictionary, then 
        # recursively go through it like a tree search.
        if (isinstance(itemdex, dict)):
            temp_dict = _ravel_dictionary(
                dictionary=itemdex, conflict=conflict)
        else:
            # It is a spare item, create a dictionary.
            temp_dict = {keydex:itemdex}
        # Combine the dictionary, but, first, check for
        # intersection conflicts.
        if (len(raveled_dictionary.keys() & temp_dict.keys()) != 0):
            # There are intersections. Handle them based 
            # on `conflict`.
            if (conflict == 'raise'):
                raise RuntimeError("There are conflicts in these two "
                                   "dictionaries: \n"
                                   "Temp : {temp} \n Ravel : {ravel}"
                                   .format(temp=temp_dict, 
                                           ravel=raveled_dictionary))
            elif (conflict == 'superior'):
                # Preserve the previous entries as they are
                # either higher up in the tree or are
                # ahead alphabetically.
                raveled_dictionary = {**temp_dict, **raveled_dictionary}
            elif (conflict == 'inferior'):
                # Preserve the new entires as they are
                # either lower in the tree or are behind
                # alphabetically.
                raveled_dictionary = {**raveled_dictionary, **temp_dict}
            else:
                # The code should not get here.
                raise RuntimeError("The input checking of conflict "
                                   "should have caught this.")
        else:
            # They can just be combined as normal. Taking superior
            # as the default.
            raveled_dictionary = {**temp_dict, **raveled_dictionary}
            
    # All done.
    return raveled_dictionary
