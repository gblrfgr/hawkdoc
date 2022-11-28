import dataclasses
import logging
import typing


@dataclasses.dataclass
class Incorporable:
    def __getitem__(self, key):
        pass

    def __setitem__(self, key, val):
        pass

    def incorporate(self, other):
        for f in dataclasses.fields(self):
            if self[f.name]:
                if other[f.name] and self[f.name] != other[f.name]:
                    logging.error(
                        f'Could not merge field "{f.name}"'
                        f'(reason: mismatched values "{self[f.name]}" and "{other[f.name]}")'
                    )
            else:
                self[f.name] = other[f.name]


@dataclasses.dataclass
class DocEntry(Incorporable):
    name: str
    short_desc: str


@dataclasses.dataclass
class FieldEntry(DocEntry):
    typename: str


@dataclasses.dataclass
class VariableEntry(DocEntry):
    value: str
    typename: str


@dataclasses.dataclass
class CompoundEntry(DocEntry):
    long_desc: str


@dataclasses.dataclass
class ModuleEntry(CompoundEntry):
    contents: list[DocEntry]


@dataclasses.dataclass
class CallableEntry(CompoundEntry):
    arguments: list[FieldEntry]
    raises: list[FieldEntry]


@dataclasses.dataclass
class FunctionEntry(CallableEntry):
    returns: str 


@dataclasses.dataclass
class GeneratorEntry(CallableEntry):
    yields: str


@dataclasses.dataclass
class ClassEntry(CompoundEntry):
    instance_vars: list[VariableEntry]
    static_vars: list[VariableEntry]
    methods: list[CallableEntry]
