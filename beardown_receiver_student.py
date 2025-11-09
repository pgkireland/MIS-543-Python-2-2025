"""
beardown_receiver.py - BEARDOWN-TP Receiver Implementation
STUDENT VERSION - BEGINNER FRIENDLY (No Python Experience Needed!)

IMPORTANT: You do NOT run this file directly!
Instead, run: python3 TestHarness.py

===================================================================
ABOUT THE "pass" STATEMENTS:
===================================================================

You will see empty methods with "pass" like this:

    def _buffer_data(self, data: bytes):
        # TODO 6: STUDENT WILL IMPLEMENT THIS METHOD
        pass

"pass" is a Python placeholder meaning "do nothing for now."

YOUR JOB: Replace "pass" with real code

===================================================================
WHAT THIS FILE DOES:
===================================================================

You implement the RECEIVER - the side that GETS data.

Think of it like receiving letters:
- Get a letter (packet)
- Check it's not damaged
- Read it
- Send back "I got it!" (ACK)

===================================================================
"""

from typing import Optional, Tuple
from protocol import (
    PacketStructure, Flags,
    SequenceNumberManager, Statistics
)


class BeardownReceiver:
    """Receives data reliably across a broken network."""
    
    def __init__(self):
        """Initialize the receiver. DO NOT MODIFY THIS."""
        self.received_data: bytes = b""
        self.seq_manager = SequenceNumberManager(modulo=2)
        self.stats = Statistics()
    
    # ================================================================
    # TODO 1: IMPLEMENT process_packet() - MAIN RECEIVING METHOD
    # ================================================================
    # DIFFICULTY: MEDIUM (most important!)
    #
    # What it does:
    #   1. Check if packet is good (not corrupted)
    #   2. Parse the packet
    #   3. Check if it's a duplicate (we already got this one)
    #   4. If duplicate: send ACK and return
    #   5. If new: save data, send ACK, return ACK packet
    #
    # Hint - follow these steps:
    #   is_valid, msg = self._validate_packet(packet)
    #   if not is_valid:
    #       return None
    #   
    #   seq_num, flags, length, data = self._parse_packet(packet)
    #   
    #   if self._is_duplicate(seq_num):
    #       ack_packet = self._create_ack_packet(
    #           self.seq_manager.get_current()
    #       )
    #       return ack_packet
    #   
    #   if self.seq_manager.is_expected(seq_num):
    #       self._buffer_data(data)
    #       self.seq_manager.increment()
    #       self.stats.record_receive(length)
    #       
    #       ack_packet = self._create_ack_packet(
    #           self.seq_manager.get_current()
    #       )
    #       return ack_packet
    #   else:
    #       return None
    # ================================================================
    def process_packet(self, packet: bytes) -> Optional[bytes]:
        """Process incoming packet and send ACK."""
        # TODO 1: STUDENT WILL IMPLEMENT THIS METHOD
        pass
    
    # ================================================================
    # TODO 2: IMPLEMENT _validate_packet() - CHECK IF GOOD
    # ================================================================
    # DIFFICULTY: VERY EASY (1 line!)
    #
    # What it does:
    #   Check if packet is corrupted or damaged
    #   Use the library function that does this
    #
    # Hint - copy this 1 line:
    #   return PacketStructure.validate_packet(packet)
    # ================================================================
    def _validate_packet(self, packet: bytes) -> Tuple[bool, str]:
        """Validate packet integrity."""
        # TODO 2: STUDENT WILL IMPLEMENT THIS METHOD
        pass
    
    # ================================================================
    # TODO 3: IMPLEMENT _parse_packet() - EXTRACT DATA
    # ================================================================
    # DIFFICULTY: VERY EASY (2 lines!)
    #
    # What it does:
    #   Extract parts from the packet
    #   Get: sequence number, flags, length, data
    #
    # Hint - copy these 2 lines:
    #   seq_num, ack_num, flags, length, data, checksum = \
    #       PacketStructure.parse_packet(packet)
    #   return seq_num, flags, length, data
    # ================================================================
    def _parse_packet(self, packet: bytes) -> Tuple[int, int, int, bytes]:
        """Extract components from packet."""
        # TODO 3: STUDENT WILL IMPLEMENT THIS METHOD
        pass
    
    # ================================================================
    # TODO 4: IMPLEMENT _is_duplicate() - IS THIS PACKET REPEATED?
    # ================================================================
    # DIFFICULTY: VERY EASY (3 lines!)
    #
    # What it does:
    #   Check if this is a packet we already got
    #   Sequence numbers are 0 or 1 (they wrap around)
    #   If current expected is 1, duplicate is 0
    #   If current expected is 0, duplicate is 1
    #
    # Hint - copy these 3 lines:
    #   expected = self.seq_manager.get_current()
    #   previous = (expected - 1) % 2
    #   return seq_num == previous
    # ================================================================
    def _is_duplicate(self, seq_num: int) -> bool:
        """Check if this is a duplicate packet."""
        # TODO 4: STUDENT WILL IMPLEMENT THIS METHOD
        pass
    
    # ================================================================
    # TODO 5: IMPLEMENT _create_ack_packet() - SEND "I GOT IT!"
    # ================================================================
    # DIFFICULTY: EASY (5 lines!)
    #
    # What it does:
    #   Create a message saying "I got your packet!"
    #   Include the next sequence number we expect
    #
    # Hint - copy these 5 lines:
    #   ack_packet = PacketStructure.create_packet(
    #       seq_num=0,
    #       ack_num=ack_seq,
    #       flags=Flags.ACK,
    #       data=b""
    #   )
    #   self.stats.record_ack()
    #   return ack_packet
    # ================================================================
    def _create_ack_packet(self, ack_seq: int) -> bytes:
        """Create acknowledgment packet."""
        # TODO 5: STUDENT WILL IMPLEMENT THIS METHOD
        pass
    
    # ================================================================
    # TODO 6: IMPLEMENT _buffer_data() - SAVE THE DATA
    # ================================================================
    # DIFFICULTY: VERY EASY (1 line!)
    #
    # What it does:
    #   Save the data we received
    #   Add it to self.received_data
    #
    # Hint - copy this 1 line:
    #   self.received_data += data
    # ================================================================
    def _buffer_data(self, data: bytes):
        """Save received data."""
        # TODO 6: STUDENT WILL IMPLEMENT THIS METHOD
        pass
    
    # ================================================================
    # DO NOT MODIFY - These are helper methods
    # ================================================================
    def get_received_data(self) -> bytes:
        """Get all received data."""
        return self.received_data
    
    def get_statistics(self) -> Statistics:
        """Get protocol statistics."""
        return self.stats


# ====================================================================
# HOW TO SUBMIT YOUR WORK
# ====================================================================
#
# 1. Fill in all 6 TODO methods above
# 2. Run: python3 TestHarness.py
# 3. If score is 10/10 - YOU'RE DONE!
# 4. If score is less than 10/10 - read error and fix code
# 5. Repeat step 2-4 until you get 10/10
#
# ====================================================================
