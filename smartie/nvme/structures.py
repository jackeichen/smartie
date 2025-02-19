"""
This file contains the various low-level structure definitions used for sending
and receiving NVMe commands, as well as the structures required for
platform-specific APIs.
"""

import ctypes
import enum

from smartie.structures import c_uint128

#: IOCTL for NVMe Admin commands on Linux.
IOCTL_NVMe_ADMIN_CMD = 0xC0484E41


class NVMeAdminCommands(enum.IntEnum):
    GET_LOG_PAGE = 0x02
    IDENTIFY = 0x06


class NVMeAdminCommand(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("opcode", ctypes.c_ubyte),
        ("flags", ctypes.c_ubyte),
        ("reserved_1", ctypes.c_ushort),
        ("nsid", ctypes.c_uint32),
        ("cdw2", ctypes.c_uint32),
        ("cdw3", ctypes.c_uint32),
        ("metadata", ctypes.c_uint64),
        ("addr", ctypes.c_uint64),
        ("metadata_len", ctypes.c_uint32),
        ("data_len", ctypes.c_uint32),
        ("cdw10", ctypes.c_uint32),
        ("cdw11", ctypes.c_uint32),
        ("cdw12", ctypes.c_uint32),
        ("cdw13", ctypes.c_uint32),
        ("cdw14", ctypes.c_uint32),
        ("cdw15", ctypes.c_uint32),
        ("timeout_ms", ctypes.c_uint32),
        ("result", ctypes.c_uint32),
    ]


class NVMeCQEStatusField(ctypes.Structure):
    """
    The format of NVMe Completion Queue Entry Status Field
    """

    _fields_ = [
        ("status_code", ctypes.c_ubyte),
        ("status_code_type", ctypes.c_ubyte, 3),
        ("cmd_retry_delay", ctypes.c_ubyte, 2),
        ("more", ctypes.c_ubyte, 1),
        ("do_not_retry", ctypes.c_ubyte, 1),
    ]


class NVMeIdentifyResponse(ctypes.Structure):
    _fields_ = [
        ("vendor_id", ctypes.c_uint16),
        ("ssvid", ctypes.c_uint16),
        ("serial_number", ctypes.c_ubyte * 20),
        ("model_number", ctypes.c_ubyte * 40),
        ("firmware_revision", ctypes.c_ubyte * 8),
        # The majority of this structure has yet to be implemented. Add fields
        # as ya need em.
        ("unknown", ctypes.c_ubyte * 4024),
    ]


class SMARTCriticalWarning(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("available_spare", ctypes.c_ubyte, 1),
        ("temperature", ctypes.c_ubyte, 1),
        ("degraded_nvm", ctypes.c_ubyte, 1),
        ("read_only", ctypes.c_ubyte, 1),
        ("volatile_memory_backup", ctypes.c_ubyte, 1),
        ("reserved_1", ctypes.c_ubyte, 3),
    ]


class SMARTPageResponse(ctypes.Structure):
    """
    This structure represents the response from the SMART Log Page (0x02).

    .. note::

        Defined in the NVMe 1.4 specification as figure 194.
    """

    _pack_ = 1
    _fields_ = [
        # Flags for any critical warnings.
        ("critical_warning", SMARTCriticalWarning),
        # A composite of the temperature in Kelvin. How this is calculated is
        # not really defined, and may be an average of multiple sensors.
        ("temperature", ctypes.c_ushort),
        ("available_spare", ctypes.c_ubyte),
        ("available_spare_threshold", ctypes.c_ubyte),
        ("percent_used", ctypes.c_ubyte),
        ("endurance_group_critical_warning_summary", ctypes.c_ubyte),
        ("reserved_1", ctypes.c_ubyte * 25),
        # The number of 512-byte data units read, in thousands.
        ("data_units_read", c_uint128),
        # The number of 512-byte data units written, in thousands.
        ("data_units_written", c_uint128),
        ("host_read_commands", c_uint128),
        ("host_write_commands", c_uint128),
        ("controller_busy_time", c_uint128),
        ("power_cycles", c_uint128),
        ("power_on_hours", c_uint128),
        ("unsafe_shutdowns", c_uint128),
        ("media_errors", c_uint128),
        ("num_err_log_entries", c_uint128),
        ("warning_temp_time", ctypes.c_uint32),
        ("critical_temp_time", ctypes.c_uint32),
        ("temperature_sensors", ctypes.c_uint16 * 8),
        ("thermal_transition_counts", ctypes.c_uint32 * 2),
        ("total_time_for_thermal_management", ctypes.c_uint32 * 2),
        ("reserved_2", ctypes.c_ubyte * 280),
    ]


## Bellow structures are used by windows nvme command ##
class StoragePropertyQuery(ctypes.Structure):
    """
    StoragePropertyQuery structure.

    From https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-storage_property_query
    """

    _pack_ = 1
    _fields_ = [
        ("PropertyId", ctypes.c_uint32),
        ("QueryType", ctypes.c_uint32),
    ]


class StorageProtocolSpecificData(ctypes.Structure):
    """
    StoragePropertyQuery structure. structure.

    https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-storage_protocol_specific_data
    """
    _pack_ = 1
    _fields_ = [
        ("ProtocolType", ctypes.c_uint32),
        ("DataType", ctypes.c_uint32),
        ("ProtocolDataRequestValue", ctypes.c_uint32),
        ("ProtocolDataRequestSubValue", ctypes.c_uint32),
        ("ProtocolDataOffset", ctypes.c_uint32),
        ("ProtocolDataLength", ctypes.c_uint32),
        ("FixedProtocolReturnData", ctypes.c_uint32),
        ("ProtocolDataRequestSubValue2", ctypes.c_uint32),
        ("ProtocolDataRequestSubValue3", ctypes.c_uint32),
        ("ProtocolDataRequestSubValue4", ctypes.c_uint32),
    ]


class NVMeSpecificDataQueryHeader(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("storage_property_query", StoragePropertyQuery),
        ("storage_protocol_specific_data", StorageProtocolSpecificData),
    ]


def GetNVMeSpecificDataQueryWithData(data_length):
    class Query(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ("command_header", NVMeSpecificDataQueryHeader),
            ("data", ctypes.c_ubyte * data_length),
        ]
    return Query


class STORAGE_PROTOCOL_DATA_DESCRIPTOR(ctypes.Structure):
    _fields_ = [
        ('Version', ctypes.c_uint32),
        ('Size', ctypes.c_uint32),
        ('storage_protocol_specific_data', StorageProtocolSpecificData),
    ]
    _pack_ = 1


class BytesReturnedStruc(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("return_bytes", ctypes.c_uint32),]

