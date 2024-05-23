# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 16:00:09 2022.

@author: mfdal
"""
# Uncomment to use actual GPIO
import RPi.GPIO as GPIO

GPIO.setwarnings(False)

# Uncomment to use mock GPIO
# import GPIO_Mockup as GPIO


from collections import Counter, deque
import logging
import time

# import ezgmail

import codes


class TWCommsException(Exception):
    """This class is used when an error occurs."""


class TWComms:
    def __init__(
        self,
        input_pins=None,
        output_pins=None,
        log=False,
        log_name=None,
        errors_only=False,
    ):
        from codes import output_lookup, input_lookup

        """
        Set up the SmartTyper class. (init GPIOs, set up logging, prepare data structures)

        Parameters
        ----------
        input_pins : list, optional
            Pins to use for input signals from typewriter. The default is None.
        output_pins : list, optional
            Pins to use for output signals to typewriter. The default is None.

        Returns
        -------
        None.

        """
        GPIO.cleanup()
        # --- Check for defaults ---
        if input_pins is not None:
            assert len(input_pins) == 10, "input_pins must have 10 entries"
            self.input_pins = input_pins
            self.read_signal_pin = input_pins[7]
            self.mpdo_pin = input_pins[8]
            self.c_chan_scan_pin = input_pins[9]
        else:
            self.input_pins = [2, 3, 4, 17, 27, 22, 10, 9, 11, 1]
            self.read_signal_pin = self.input_pins[7]
            self.mpdo_pin = self.input_pins[8]
            self.c_chan_scan_pin = self.input_pins[9]

        if output_pins is not None:
            assert len(output_pins) == 8, "output_pins must have 8 entries"
            self.output_pins = output_pins
            self.write_signal_pin = output_pins[7]
        else:
            self.output_pins = [14, 15, 18, 23, 24, 25, 8, 7]
            self.write_signal_pin = self.output_pins[7]

        # --- Start GPIO Setup ---
        GPIO.setmode(GPIO.BCM)

        for pin in self.input_pins:
            GPIO.setup(pin, GPIO.IN)

        for pin in self.output_pins:
            GPIO.setup(pin, GPIO.OUT)

        self.output_lookup = output_lookup
        self.input_lookup = input_lookup

        # Set up logging
        if log_name is not None:
            logging.basicConfig(
                level=logging.DEBUG,
                filename=log_name,
                format=" %(asctime)s - %(levelname)s - %(message)s",
                datefmt="%m/%d/%Y %I:%M:%S %p",
            )
        else:
            logging.basicConfig(
                level=logging.DEBUG,
                format=" %(asctime)s - %(levelname)s - %(message)s",
                datefmt="%m/%d/%Y %I:%M:%S %p",
            )

        if not log:
            logging.disable(logging.CRITICAL)

        if errors_only:
            logging.disable(logging.ERROR)

        # hi-speed capital printing
        self.caps_lock_on = False

        # Set up recieving
        self._buffer = deque()
        self._possibles = []
        self._shifted = False
        self._modded = False
        self._data = "0000000"

        GPIO.add_event_detect(
            self.read_signal_pin, GPIO.RISING, callback=self.getch_callback
        )
        GPIO.add_event_detect(
            self.c_chan_scan_pin, GPIO.RISING, callback=self.c_chan_callback
        )
        GPIO.add_event_detect(self.mpdo_pin, GPIO.FALLING, callback=self.mpdo_callback)

    def set_output_lines(self, data):
        """
        Set the output lines to a given value.

        Parameters
        ----------
        data : string
            A string of the bits to be sent to the output lines.

        Returns
        -------
        None.

        """
        data = list(data)
        for bit, line in zip(data[::-1], self.output_pins):
            GPIO.output(line, int(bit))

    def send_write_pulse(self, pulse_duration=0.025):
        GPIO.output(self.write_signal_pin, 0)
        time.sleep(pulse_duration)
        GPIO.output(self.write_signal_pin, 1)
        time.sleep(pulse_duration)
        GPIO.output(self.write_signal_pin, 0)

    def wait_for_wrote(self, wait_duration=0.035):
        time.sleep(wait_duration)

    def _send_char(self, char_code):
        """
        Internal function to actually send a character.
        Waits until character is wrote.

        Parameters
        ----------
        char_code : string
            A string of ones and zeroes representing the code to be sent.

        Returns
        -------
        None.

        """
        self.set_output_lines(char_code)
        self.send_write_pulse()
        self.wait_for_wrote()

    def print_char(self, char):
        """
        Print a single character.

        Parameters
        ----------
        char : string
            The string to be printed.

        Raises
        ------
        TWCommsException
            Raised when the data is invalid.

        Returns
        -------
        None.

        """
        try:
            char_code, shifted, modded = self.output_lookup[char]
        except KeyError:
            logging.warning(f'Cannot print character "{char}". Continuing anyway.')
            return
        if shifted and modded:  # Sanity check
            raise TWCommsException("Characters can't be both shifted and modded.")
        if not (shifted or modded):
            if self.caps_lock_on:
                self._send_char("0111111")
                self.caps_lock_on = False
            self._send_char(char_code)
        if shifted:
            if not self.caps_lock_on:
                self._send_char("1011111")
                self.caps_lock_on = True
            self._send_char(char_code)
        if modded:
            self._send_char(char_code)

    def print_str(self, string):
        for char in string:
            self.print_char(char)

    def print(self, *args, sep=" ", end="\n"):
        """
        Prints each string fed in as args.

        Parameters
        ----------
        string : string
            The string to be printed.

        Returns
        -------
        None.

        """
        for arg in args:
            arg = str(arg)
            for char in arg:
                self.print_char(char)
            for char in str(sep):
                self.print_char(char)
        for char in str(end):
            self.print_char(char)

    def return_paper(self, num_returns=1):
        for _ in range(num_returns):
            self._send_char("1101100")

    def return_until_readable(self):
        self.return_paper(num_returns=7)

    def read_input_lines(self):
        data = []
        read = self.input_pins[:7]
        read = read[::-1]

        for pin in read:
            data.append(str(GPIO.input(pin)))

        return "".join(data)

    def getch_callback(self, _):
        data = self.read_input_lines()
        if data == "0111111":
            self._shifted = True
        elif data == "1111111":
            self._modded = True
        else:
            self._data = data

    def c_chan_callback(self, _):
        # print("C Chan")
        try:
            char = self.input_lookup[self._data, self._shifted, self._modded]
        except KeyError:
            logging.warning(
                f"Cannot decode character ({self._data}, {self._shifted}, {self._modded}). Continuing anyway."
            )
            return

        if char != "" and char != "SHIFT":
            self._possibles.append(char)
        self._data = "0000000"
        self._shifted = self._modded = False

    def mpdo_callback(self, _):
        if len(self._possibles) != 0:
            most_common = Counter(self._possibles).most_common(1)[0][0]
            self._buffer.appendleft(most_common)
        self._possibles = []

    def avaliable(self):
        return len(self._buffer)

    def read(self):
        return self._buffer.pop()

    def readall(self):
        text = "".join(self._buffer)
        self._buffer.clear()
        return text[::-1]

    def process_lines(self, text, PAPER_WIDTH=67):
        """
        Process lines for printing on a piece of paper with line numbers.

        Parameters
        ----------
        text : list
            Ideally from file.readlines().
        PAPER_WIDTH : int, optional
            The number of characters that fit horizontally on the paper.
            The default is 67.

        Returns
        -------
        text_lines : list
            A list of PAPER_WIDTH - 5 long lines with full words,
            split at spaces or newlines.

        """

        text_joined = " ".join(text)

        text_split = [x + " " for x in text_joined.split(" ")]

        current_line = ""
        text_lines = []

        for string in text_split:
            current_line += string
            current_line_len = len(current_line)
            if (current_line_len > (PAPER_WIDTH - 5)) or ("\n" in string):
                text_lines += [current_line]
                current_line = ""

        return text_lines

    def summarize_email(self, gmailObjects):
        if isinstance(gmailObjects, (ezgmail.GmailThread, ezgmail.GmailMessage)):
            gmailObjects = [gmailObjects]  # Make this uniformly in a list.

        summaryText = []
        for obj in gmailObjects:
            summaryText.append(
                (obj.senders(), obj.snippet, obj.latestTimestamp())
            )  # GmailThread and GmailMessage both have senders() and latestTimesta>
        summaryText = [
            (
                ", ".join(
                    [name[: name.find(" ")] for name in itemSenders]
                ),  # Just use the "Al" part of "Al Sweigart <al@inventwithpyth>
                itemSnippet,
                itemLatestTimestamp.strftime("%b %d"),
            )
            for itemSenders, itemSnippet, itemLatestTimestamp in summaryText
        ]
        return "\n".join(["%s - %s - %s" % text for text in summaryText])

    def prompt(self, line_before="", prompt="> ", return_before=True):
        if return_before:
            self.return_paper()

        if line_before:
            self.print_string_ln(line_before)

        while not self.avaliable():
            pass

        out = ""
        char = self.read()

        while char != "\n":
            out += char
            char = self.read()

        return out

    def edit_lines(self, text):
        pass

    def print_lines(self, lines):
        for line in lines:
            line = line.strip()
            print(line, end="\n")


import signal
import sys


def signal_handler(sig, frame):
    sys.exit(0)
