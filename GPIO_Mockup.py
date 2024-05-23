# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 14:47:26 2023

@author: mfdal
"""

OUT = "OUT"
IN = "IN"
BCM = "BROADCOM"


def __init__():
    pass


def setmode(mode):
    print(f"Mode set to {mode}")


def setup(pin, mode):
    print(f"Pin {pin} set to {mode}")


def output(pin, val):
    print(f"Pin {pin} set to {val}")


def cleanup():
    print("Cleaning up GPIO...")
