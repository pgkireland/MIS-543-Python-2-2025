"""
protocol.py - Shared protocol definitions and utility functions for BEARDOWN-TP
Provides packet structure, checksum calculation, and helper functions
"""

import struct
from typing import Tuple, Optional
from enum import IntFlag


# Protocol Constants
PACKET_HEADER_SIZE = 7  # 1 + 1 + 1 + 2 + 2 = 7 bytes
MAX_PAYLOAD_SIZE = 1000
MAX_SEGMENT_SIZE = PACKET_HEADER_SIZE + MAX_PAYLOAD_SIZE


# Sequence number field (1 byte - for stop and wait: 0 or 1)
SEQ_NUM_SIZE = 1
ACK_NUM_SIZE = 1
FLAGS_SIZE = 1
LENGTH_SIZE = 2
CHECKSUM_SIZE = 2


# Flag definitions
class Flags(IntFlag):
    """Control flags for BEARDOWN-TP"""
    SYN = 0x01   # Synchronization flag
    ACK = 0x02   # Acknowledgment flag
    FIN = 0x04   # Finish flag
    DATA = 0x08  # Data present flag


class PacketStructure:
    """
    BEARDOWN-TP Packet Structure:
    
    +--------+--------+--------+--------+--------+--------+--------+
    | SeqNum | AckNum | Flags  | Length           | Checksum      |
    | (1B)   | (1B)   | (1B)   | (2B, network)    | (2B, network) |
    +--------+--------+--------+--------+--------+--------+--------+
    | Data (0 to 1000 bytes)                                      |
    +---------------------------------------------------------+
    """
    
    @staticmethod
    def create_packet(seq_num: int, ack_num: int, flags: int, 
                     data: bytes = b"") -> bytes:
        """
        Create a BEARDOWN-TP packet.
        
        Args:
            seq_num: Sequence number (0-255)
            ack_num: Acknowledgment number (0-255)
            flags: Flags bitfield
            data: Payload data (up to 1000 bytes)
        
        Returns:
            Complete packet with checksum
        """
        if len(data) > MAX_PAYLOAD_SIZE:
            raise ValueError(f"Payload size {len(data)} exceeds maximum {MAX_PAYLOAD_SIZE}")
        
        # Pack header without checksum
        length = len(data)
        header = struct.pack(
            '!BBBHH',
            seq_num & 0xFF,
            ack_num & 0xFF,
            flags & 0xFF,
            length,
            0  # Placeholder for checksum
        )
        
        # Calculate checksum of header + data
        packet = header + data
        checksum = InternetChecksum.calculate(packet)
        
        # Pack header with actual checksum
        header = struct.pack(
            '!BBBHH',
            seq_num & 0xFF,
            ack_num & 0xFF,
            flags & 0xFF,
            length,
            checksum
        )
        
        return header + data
    
    @staticmethod
    def parse_packet(packet: bytes) -> Tuple[int, int, int, int, bytes, int]:
        """
        Parse a BEARDOWN-TP packet.
        
        Args:
            packet: Raw packet bytes
        
        Returns:
            Tuple of (seq_num, ack_num, flags, length, data, checksum)
        
        Raises:
            ValueError: If packet is too short or invalid format
        """
        if len(packet) < PACKET_HEADER_SIZE:
            raise ValueError(f"Packet too short: {len(packet)} < {PACKET_HEADER_SIZE}")
        
        # Unpack header
        seq_num, ack_num, flags, length, checksum = struct.unpack(
            '!BBBHH',
            packet[:PACKET_HEADER_SIZE]
        )
        
        # Extract data
        data = packet[PACKET_HEADER_SIZE:]
        
        if len(data) != length:
            raise ValueError(f"Data length mismatch: expected {length}, got {len(data)}")
        
        return seq_num, ack_num, flags, length, data, checksum
    
    @staticmethod
    def validate_packet(packet: bytes) -> Tuple[bool, str]:
        """
        Validate a packet's integrity.
        
        Args:
            packet: Raw packet bytes
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if len(packet) < PACKET_HEADER_SIZE:
                return False, f"Packet too short: {len(packet)} bytes"
            
            # Parse header
            seq_num, ack_num, flags, length, checksum = struct.unpack(
                '!BBBHH',
                packet[:PACKET_HEADER_SIZE]
            )
            
            # Check length field
            expected_total_size = PACKET_HEADER_SIZE + length
            if len(packet) != expected_total_size:
                return False, f"Length mismatch: packet {len(packet)} vs expected {expected_total_size}"
            
            # Verify checksum
            packet_for_checksum = packet[:PACKET_HEADER_SIZE - CHECKSUM_SIZE] + \
                                 b'\x00\x00' + packet[PACKET_HEADER_SIZE:]
            calculated_checksum = InternetChecksum.calculate(packet_for_checksum)
            
            if calculated_checksum != checksum:
                return False, f"Checksum mismatch: expected {checksum:04x}, got {calculated_checksum:04x}"
            
            return True, ""
        
        except struct.error as e:
            return False, f"Struct unpacking error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"


class InternetChecksum:
    """
    Implementation of Internet Checksum (RFC 1071)
    
    The checksum is the 16-bit one is complement of the one is complement sum
    of all 16-bit words in the packet.
    """
    
    @staticmethod
    def calculate(data: bytes) -> int:
        """
        Calculate Internet checksum for data.
        
        Args:
            data: Input data bytes
        
        Returns:
            16-bit checksum value
        """
        # Ensure data is aligned to 16-bit words
        if len(data) % 2 == 1:
            data = data + b'\x00'
        
        sum_val = 0
        
        # Sum all 16-bit words
        for i in range(0, len(data), 2):
            word = (data[i] << 8) | data[i + 1]
            sum_val += word
        
        # Add carries
        while (sum_val >> 16) > 0:
            sum_val = (sum_val & 0xFFFF) + (sum_val >> 16)
        
        # Return one is complement
        return (~sum_val) & 0xFFFF
    
    @staticmethod
    def verify(packet_with_checksum: bytes, stored_checksum: int) -> bool:
        """
        Verify checksum of a packet.
        
        Args:
            packet_with_checksum: Full packet bytes (with checksum field = 0)
            stored_checksum: Stored checksum value to verify against
        
        Returns:
            True if checksum is valid
        """
        calculated = InternetChecksum.calculate(packet_with_checksum)
        return calculated == stored_checksum


class TimeoutManager:
    """
    Manages timeout values with adaptive adjustment based on RTT estimates.
    Implements a simplified version of TCP-style timeout calculation.
    """
    
    def __init__(self, initial_timeout: float = 0.5):
        """
        Initialize timeout manager.
        
        Args:
            initial_timeout: Initial timeout value in seconds
        """
        self.initial_timeout = initial_timeout
        self.current_timeout = initial_timeout
        self.min_timeout = 0.1
        self.max_timeout = 30.0
        self.rtt_samples = []
        self.max_samples = 50
    
    def record_rtt(self, rtt: float):
        """
        Record a successful round-trip time sample.
        
        Args:
            rtt: Round-trip time in seconds
        """
        self.rtt_samples.append(rtt)
        if len(self.rtt_samples) > self.max_samples:
            self.rtt_samples.pop(0)
        
        # Update timeout based on average RTT
        self._update_timeout()
    
    def _update_timeout(self):
        """Update timeout based on RTT statistics"""
        if not self.rtt_samples:
            return
        
        avg_rtt = sum(self.rtt_samples) / len(self.rtt_samples)
        std_dev = (sum((x - avg_rtt) ** 2 for x in self.rtt_samples) / len(self.rtt_samples)) ** 0.5
        
        # Set timeout to average RTT + 4 * standard deviation
        # This is similar to TCP's RTO calculation
        new_timeout = avg_rtt + 4 * std_dev
        
        # Clamp to min/max bounds
        self.current_timeout = max(self.min_timeout, min(self.max_timeout, new_timeout))
    
    def get_timeout(self) -> float:
        """Get current timeout value in seconds"""
        return self.current_timeout
    
    def on_retransmission(self):
        """Called when a packet is retransmitted. Increases timeout exponentially."""
        self.current_timeout = min(self.current_timeout * 2, self.max_timeout)
    
    def on_successful_ack(self):
        """Called when an ACK is received. May decrease timeout."""
        self.current_timeout = max(self.current_timeout * 0.9, self.min_timeout)


class SequenceNumberManager:
    """
    Manages sequence numbers for stop-and-wait protocol.
    For BEARDOWN-TP, sequence numbers are 1 byte (0-255), but for stop-and-wait
    we typically only use 0 and 1 modulo 2.
    """
    
    def __init__(self, modulo: int = 2):
        """
        Initialize sequence number manager.
        
        Args:
            modulo: Modulo value (typically 2 for stop-and-wait)
        """
        self.modulo = modulo
        self.seq_num = 0
    
    def get_current(self) -> int:
        """Get current sequence number"""
        return self.seq_num
    
    def increment(self):
        """Increment sequence number with wraparound"""
        self.seq_num = (self.seq_num + 1) % self.modulo
    
    def reset(self):
        """Reset sequence number to 0"""
        self.seq_num = 0
    
    def is_expected(self, received_seq: int) -> bool:
        """Check if received sequence number matches expected"""
        return received_seq == self.seq_num
    
    def is_duplicate(self, received_seq: int) -> bool:
        """Check if sequence number is a duplicate"""
        prev_seq = (self.seq_num - 1) % self.modulo
        return received_seq == prev_seq


class Statistics:
    """Collect and report statistics about protocol performance"""
    
    def __init__(self):
        self.segments_sent = 0
        self.segments_received = 0
        self.segments_retransmitted = 0
        self.packets_lost = 0
        self.packets_corrupted = 0
        self.acks_received = 0
        self.timeouts = 0
        self.total_bytes_sent = 0
        self.total_bytes_received = 0
    
    def record_send(self, size: int):
        """Record a sent segment"""
        self.segments_sent += 1
        self.total_bytes_sent += size
    
    def record_receive(self, size: int):
        """Record a received segment"""
        self.segments_received += 1
        self.total_bytes_received += size
    
    def record_ack(self):
        """Record an ACK received"""
        self.acks_received += 1
    
    def record_timeout(self):
        """Record a timeout event"""
        self.timeouts += 1
    
    def record_retransmission(self):
        """Record a retransmitted segment"""
        self.segments_retransmitted += 1
    
    def get_summary(self) -> str:
        """Get summary statistics"""
        retransmission_rate = (
            (self.segments_retransmitted / self.segments_sent * 100)
            if self.segments_sent > 0 else 0
        )
        
        return f"""
Protocol Statistics:
  Segments sent:        {self.segments_sent}
  Segments received:    {self.segments_received}
  Retransmissions:      {self.segments_retransmitted} ({retransmission_rate:.1f}%)
  ACKs received:        {self.acks_received}
  Timeouts:             {self.timeouts}
  Total bytes sent:     {self.total_bytes_sent}
  Total bytes received: {self.total_bytes_received}
"""


# Example usage and testing
if __name__ == "__main__":
    # Test packet creation and parsing
    print("Testing BEARDOWN-TP Protocol Functions")
    print("=" * 50)
    
    # Create a packet
    test_data = b"Hello, World!"
    packet = PacketStructure.create_packet(
        seq_num=0,
        ack_num=0,
        flags=Flags.DATA,
        data=test_data
    )
    
    print(f"Created packet: {len(packet)} bytes")
    
    # Parse the packet
    seq, ack, flags, length, data, checksum = PacketStructure.parse_packet(packet)
    print(f"Parsed packet:")
    print(f"  Sequence: {seq}")
    print(f"  Ack: {ack}")
    print(f"  Flags: {flags:02x}")
    print(f"  Length: {length}")
    print(f"  Data: {data}")
    print(f"  Checksum: {checksum:04x}")
    
    # Validate the packet
    is_valid, msg = PacketStructure.validate_packet(packet)
    print(f"Valid: {is_valid} ({msg if msg else 'OK'})")
    
    # Test corrupting the packet
    print("\nTesting corruption detection:")
    corrupted = bytearray(packet)
    corrupted[10] ^= 0x01  # Flip a bit in the data
    
    is_valid, msg = PacketStructure.validate_packet(bytes(corrupted))
    print(f"Corrupted packet valid: {is_valid} ({msg})")
    
    # Test timeout manager
    print("\nTesting timeout manager:")
    tm = TimeoutManager(initial_timeout=0.5)
    print(f"Initial timeout: {tm.get_timeout():.3f}s")
    
    tm.record_rtt(0.1)
    tm.record_rtt(0.12)
    tm.record_rtt(0.11)
    print(f"Timeout after RTT samples: {tm.get_timeout():.3f}s")
    
    # Test sequence number manager
    print("\nTesting sequence number manager:")
    sm = SequenceNumberManager(modulo=2)
    print(f"Initial seq: {sm.get_current()}")
    sm.increment()
    print(f"After increment: {sm.get_current()}")
    sm.increment()
    print(f"After increment (wraparound): {sm.get_current()}")
