import dataclasses


@dataclasses.dataclass
class Field:
    name: str
    typename: str
    desc: str


@dataclasses.dataclass
class DocEntry:
    name: str
    short_desc: str


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
    arguments: list[Field]
    raises: list[Field]


@dataclasses.dataclass
class FunctionEntry(CallableEntry):
    returns: Field


@dataclasses.dataclass
class GeneratorEntry(CallableEntry):
    yields: Field


@dataclasses.dataclass
class ClassEntry(CompoundEntry):
    instance_vars: list[VariableEntry]
    static_vars: list[VariableEntry]
    instance_methods: list[CallableEntry]
    static_methods: list[CallableEntry]
