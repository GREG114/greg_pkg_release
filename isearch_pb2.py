# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: isearch.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='isearch.proto',
  package='isearch',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\risearch.proto\x12\x07isearch\"@\n\x03req\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x0b\n\x03req\x18\x02 \x01(\t\x12\x0f\n\x07headers\x18\x03 \x01(\t\x12\x0e\n\x06method\x18\x04 \x01(\t\"\x15\n\x03res\x12\x0e\n\x06result\x18\x01 \x01(\t22\n\x05Hello\x12)\n\tapiBridge\x12\x0c.isearch.req\x1a\x0c.isearch.res\"\x00\x62\x06proto3'
)




_REQ = _descriptor.Descriptor(
  name='req',
  full_name='isearch.req',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='url', full_name='isearch.req.url', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='req', full_name='isearch.req.req', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='headers', full_name='isearch.req.headers', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='method', full_name='isearch.req.method', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=26,
  serialized_end=90,
)


_RES = _descriptor.Descriptor(
  name='res',
  full_name='isearch.res',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='result', full_name='isearch.res.result', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=92,
  serialized_end=113,
)

DESCRIPTOR.message_types_by_name['req'] = _REQ
DESCRIPTOR.message_types_by_name['res'] = _RES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

req = _reflection.GeneratedProtocolMessageType('req', (_message.Message,), {
  'DESCRIPTOR' : _REQ,
  '__module__' : 'isearch_pb2'
  # @@protoc_insertion_point(class_scope:isearch.req)
  })
_sym_db.RegisterMessage(req)

res = _reflection.GeneratedProtocolMessageType('res', (_message.Message,), {
  'DESCRIPTOR' : _RES,
  '__module__' : 'isearch_pb2'
  # @@protoc_insertion_point(class_scope:isearch.res)
  })
_sym_db.RegisterMessage(res)



_HELLO = _descriptor.ServiceDescriptor(
  name='Hello',
  full_name='isearch.Hello',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=115,
  serialized_end=165,
  methods=[
  _descriptor.MethodDescriptor(
    name='apiBridge',
    full_name='isearch.Hello.apiBridge',
    index=0,
    containing_service=None,
    input_type=_REQ,
    output_type=_RES,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_HELLO)

DESCRIPTOR.services_by_name['Hello'] = _HELLO

# @@protoc_insertion_point(module_scope)