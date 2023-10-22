#!/usr/bin/env python3
# coding: ascii
"""overload.py

Allow for multiple functions with different signatures
to have the same name (i.e. function overloading)."""

import inspect
from inspect import (
    getfullargspec,
    getmro,
    isfunction,
    ismethod,
)
from functools import (
    wraps,
)

class OverloadedFunctionError(Exception):
    """Exception class for errors related to the OverloadedFunction class."""
    pass

class OverloadedFunction(object):
    """An overloaded function.

    This is a proxy object which stores a list of functions. When called,
    it calls the first of its functions which matches the given arguments."""

    def __init__(self):
        """Initialize a new overloaded function."""

        self.registry = list()

    def lookup(self, args, kwargs):
        """Return the first registered function
        that matches the given call-parameters."""

        for function in self.registry:
            fullargspec = getfullargspec(function)

            # Make sure that the function can handle
            # the given number of positional arguments
            if(
                len(args) <= len(fullargspec.args) or
                bool(fullargspec.varargs)
            ):

                # Make sure that the function can handle
                # the remaining keyword arguments
                remaining_args = fullargspec.args[len(args):]
                if(
                    frozenset(kwargs.keys()).issubset(remaining_args) or
                    bool(fullargspec.varkw)
                ):
                    return function

    def register(self, function):
        """Add a new function to the registry."""

        self.registry.append(function)

    def __call__(self, *args, **kwargs):
        """Call the first matching registered
        function with the given call parameters."""

        # Get the first function which can handle the given arguments
        function = self.lookup(args=args, kwargs=kwargs)

        # If no function can be found, raise an exception
        if not function:
            raise OverloadedFunctionError(
                "Failed to find matching function for given arguments: "
                "args={}, kwargs={}".format(args, kwargs)
            )

        # Evaluate the function and return the result
        return function(*args, **kwargs)

class Overloader(object):
    """A controller object which organizes OverloadedFunction by name."""

    def __init__(self):
        """Initialize a new OverloadedFunction controller."""

        self.registry = dict()

    def register(self, function):
        """Add a new function to the controller."""

        # Create a new OverloadedFunction for this
        # function name if one does not # already exists
        if function.__qualname__ not in self.registry.keys():
            self.registry[function.__qualname__] = OverloadedFunction()

        self.registry[function.__qualname__].register(function)

    def overload(self, function):
        """Decorator for registering a new function with
        the Overloader overloaded function controller."""

        # Register the new function with the controller
        self.register(function)

        # Handle the case of unbound functions
        if isfunction(function):
            def function_wrapper(*args, **kwargs):
                _function = self.registry[function.__qualname__]
                return _function(*args, **kwargs)
            return function_wrapper

        # Handle the case of bound functions
        if ismethod(function):
            def method_wrapper(_self, *args, **kwargs):
                _function = self.registry[function.__qualname__]
                return _function(self=_self, *args, **kwargs)
            return method_wrapper
