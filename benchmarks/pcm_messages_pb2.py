# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: benchmarks/pcm_messages.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='benchmarks/pcm_messages.proto',
  package='',
  serialized_pb=_b('\n\x1d\x62\x65nchmarks/pcm_messages.proto\"7\n\x13\x62ytes_serialization\x12\x0c\n\x04\x62ody\x18\x01 \x02(\x0c\x12\x12\n\nframe_rate\x18\x02 \x02(\x05\"7\n\x13\x61rray_serialization\x12\x0c\n\x04\x62ody\x18\x01 \x03(\x05\x12\x12\n\nframe_rate\x18\x02 \x02(\x05')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_BYTES_SERIALIZATION = _descriptor.Descriptor(
  name='bytes_serialization',
  full_name='bytes_serialization',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='body', full_name='bytes_serialization.body', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='frame_rate', full_name='bytes_serialization.frame_rate', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=33,
  serialized_end=88,
)


_ARRAY_SERIALIZATION = _descriptor.Descriptor(
  name='array_serialization',
  full_name='array_serialization',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='body', full_name='array_serialization.body', index=0,
      number=1, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='frame_rate', full_name='array_serialization.frame_rate', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=90,
  serialized_end=145,
)

DESCRIPTOR.message_types_by_name['bytes_serialization'] = _BYTES_SERIALIZATION
DESCRIPTOR.message_types_by_name['array_serialization'] = _ARRAY_SERIALIZATION

bytes_serialization = _reflection.GeneratedProtocolMessageType('bytes_serialization', (_message.Message,), dict(
  DESCRIPTOR = _BYTES_SERIALIZATION,
  __module__ = 'benchmarks.pcm_messages_pb2'
  # @@protoc_insertion_point(class_scope:bytes_serialization)
  ))
_sym_db.RegisterMessage(bytes_serialization)

array_serialization = _reflection.GeneratedProtocolMessageType('array_serialization', (_message.Message,), dict(
  DESCRIPTOR = _ARRAY_SERIALIZATION,
  __module__ = 'benchmarks.pcm_messages_pb2'
  # @@protoc_insertion_point(class_scope:array_serialization)
  ))
_sym_db.RegisterMessage(array_serialization)


# @@protoc_insertion_point(module_scope)
