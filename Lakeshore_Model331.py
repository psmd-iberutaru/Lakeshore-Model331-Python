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
    
    def __init__(self, port, baudrate=9600, timeout=15):
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
            responce from the instrument. 

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