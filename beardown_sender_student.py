"""
beardown_sender.py - BEARDOWN-TP Sender Implementation
STUDENT VERSION - BEGINNER FRIENDLY (No Python Experience Needed!)

IMPORTANT: You do NOT run this file directly!
Instead, run: python3 TestHarness.py

===================================================================
ABOUT THE "pass" STATEMENTS:
===================================================================

You will see empty methods with "pass" like this:

    def load_data(self, data: bytes):
        # TODO 1: STUDENT WILL IMPLEMENT THIS METHOD
        pass

"pass" is a Python placeholder meaning "do nothing for now."

YOUR JOB: Replace "pass" with real code

EXAMPLE:
  BEFORE:  def load_data(self, data: bytes):
               pass
  
  AFTER:   def load_data(self, data: bytes):
               self.data_buffer = data

===================================================================
WHAT THIS FILE DOES:
===================================================================

You implement the SENDER - the side that SENDS data.

Think of it like mailing letters:
- Load data into envelopes (packets)
- Send them
- Wait for a reply saying "I got it!" (ACK)
- If no reply comes, resend the letter

===================================================================
"""

import time
from typing import Optional
from protocol import (
    PacketStructure, Flags, 
    TimeoutManager, SequenceNumberManager, Statistics, MAX_PAYLOAD_SIZE
)


class BeardownSender:
    """Sends data reliably across a broken network."""
    
    def __init__(self, timeout: float = 0.5):
        """Initialize the sender. DO NOT MODIFY THIS."""
        self.data_buffer: bytes = b""
        self.current_offset = 0
        self.total_size = 0
        
        self.seq_manager = SequenceNumberManager(modulo=2)
        self.timeout_manager = TimeoutManager(initial_timeout=timeout)
        
        self.current_packet: Optional[bytes] = None
        self.packet_sent_time: Optional[float] = None
        self.pending_ack = False
        self.current_data: bytes = b""
        
        self.stats = Statistics()
    
    # ================================================================
    # TODO 1: IMPLEMENT load_data() - STORE THE DATA TO SEND
    # ================================================================
    # DIFFICULTY: VERY EASY (just storing things)
    # 
    # What it does:
    #   Store the data we want to send
    #   Remember how much data there is
    #   Start at position 0 (beginning)
    #   Reset the sequence number to 0
    #   Mark that we are NOT waiting for an ACK yet
    #
    # Hint: Copy these 5 lines:
    #   self.data_buffer = data
    #   self.total_size = len(data)
    #   self.current_offset = 0
    #   self.seq_manager.reset()
    #   self.pending_ack = False
    # ================================================================
    def load_data(self, data: bytes):
        """Load data to send."""
        # TODO 1: STUDENT WILL IMPLEMENT THIS METHOD
        pass
    
    # ================================================================
    # TODO 2: IMPLEMENT get_next_packet() - SEND PACKETS
    # ================================================================
    # DIFFICULTY: MEDIUM (most important method!)
    #
    # What it does:
    #   1. Check if packet timed out - if yes, resend it
    #   2. If waiting for ACK - do nothing, return None
    #   3. If all data sent - return None
    #   4. Get next chunk of data
    #   5. Create packet from that data
    #   6. Remember when we sent it (for timeout)
    #   7. Return the packet
    #
    # Step by step:
    #   if self._should_retransmit():
    #       self.handle_timeout()
    #       return self.current_packet
    #   
    #   if self.pending_ack:
    #       return None
    #   
    #   if self.current_offset >= self.total_size:
    #       return None
    #   
    #   data_segment = self._extract_data_segment()
    #   packet = self._create_data_packet(data_segment)
    #   
    #   self.current_packet = packet
    #   self.current_data = data_segment
    #   self.packet_sent_time = time.time()
    #   self.pending_ack = True
    #   
    #   self.stats.record_send(len(packet))
    #   return packet
    # ================================================================
    def get_next_packet(self) -> Optional[bytes]:
        """Get the next packet to send."""
        # TODO 2: STUDENT WILL IMPLEMENT THIS METHOD
        pass
    
    # ================================================================
    # TODO 3: IMPLEMENT process_ack() - HANDLE "I GOT IT!" MESSAGES
    # ================================================================
    # DIFFICULTY: MEDIUM
    #
    # What it does:
    #   Get a message saying "I got your packet!"
    #   Check if it's valid (real message, not corrupted)
    #   Check if it's for OUR packet (not someone else's)
    #   If yes: move to next packet, return True
    #   If no: ignore it, return False
    #
    # Hint - follow these steps:
    #   Try:
    #       is_valid, msg = PacketStructure.validate_packet(ack_packet)
    #       if not is_valid:
    #           return False
    #       
    #       seq_num, ack_num, flags, length, data, checksum = \
    #           PacketStructure.parse_packet(ack_packet)
    #       
    #       if not (flags & Flags.ACK):
    #           return False
    #       
    #       expected_ack = (self.seq_manager.get_current() + 1) % 2
    #       
    #       if ack_num == expected_ack:
    #           if self.packet_sent_time is not None:
    #               rtt = time.time() - self.packet_sent_time
    #               self.timeout_manager.record_rtt(rtt)
    #           
    #           self.seq_manager.increment()
    #           self.current_offset += len(self.current_data)
    #           self.pending_ack = False
    #           self.stats.record_ack()
    #           return True
    #       else:
    #           return False
    #   except:
    #       return False
    # ================================================================
    def process_ack(self, ack_packet: bytes) -> bool:
        """Handle acknowledgment from receiver."""
        # TODO 3: STUDENT WILL IMPLEMENT THIS METHOD
        pass
    
    # ================================================================
    # TODO 4: IMPLEMENT handle_timeout() - RESEND IF LOST
    # ================================================================
    # DIFFICULTY: VERY EASY (just 4 lines!)
    #
    # What it does:
    #   If no ACK comes back, we assume packet was lost
    #   Increase timeout value (maybe network is slow)
    #   Reset the send time (so we can resend)
    #   Record that this happened (statistics)
    #
    # Hint - copy these 4 lines:
    #   self.timeout_manager.on_retransmission()
    #   self.packet_sent_time = time.time()
    #   self.stats.record_timeout()
    #   self.stats.record_retransmission()
    # ================================================================
    def handle_timeout(self):
        """Handle packet timeout - resend it."""
        # TODO 4: STUDENT WILL IMPLEMENT THIS METHOD
        pass
    
    # ================================================================
    # TODO 5: IMPLEMENT is_complete() - ARE WE DONE?
    # ================================================================
    # DIFFICULTY: VERY EASY (just 1 line!)
    #
    # What it does:
    #   Check if we sent all data AND got all ACKs back
    #   Return True if complete, False if more to send
    #
    # Hint - copy this 1 line:
    #   return self.current_offset >= self.total_size and not self.pending_ack
    # ================================================================
    def is_complete(self) -> bool:
        """Check if transfer is complete."""
        # TODO 5: STUDENT WILL IMPLEMENT THIS METHOD
        pass
    
    # ================================================================
    # TODO 6: IMPLEMENT _extract_data_segment() - GET NEXT CHUNK
    # ================================================================
    # DIFFICULTY: EASY (3 lines)
    #
    # What it does:
    #   Get the next piece of data to send
    #   Maximum 1000 bytes per packet
    #   Extract from self.data_buffer starting at self.current_offset
    #
    # Hint:
    #   remaining = self.total_size - self.current_offset
    #   chunk_size = min(remaining, MAX_PAYLOAD_SIZE)
    #   return self.data_buffer[self.current_offset : self.current_offset + chunk_size]
    # ================================================================
    def _extract_data_segment(self) -> bytes:
        """Get next data chunk (up to 1000 bytes)."""
        # TODO 6: STUDENT WILL IMPLEMENT THIS METHOD
        pass
    
    # ================================================================
    # TODO 7: IMPLEMENT _create_data_packet() - MAKE PACKET
    # ================================================================
    # DIFFICULTY: EASY (use library function)
    #
    # What it does:
    #   Create a packet with header and checksum
    #   Include the data segment
    #   Use current sequence number
    #
    # Hint - copy these lines:
    #   packet = PacketStructure.create_packet(
    #       seq_num=self.seq_manager.get_current(),
    #       ack_num=0,
    #       flags=Flags.DATA,
    #       data=data_chunk
    #   )
    #   return packet
    # ================================================================
    def _create_data_packet(self, data_chunk: bytes) -> bytes:
        """Create a packet from data."""
        # TODO 7: STUDENT WILL IMPLEMENT THIS METHOD
        pass
    
    # ================================================================
    # TODO 8: IMPLEMENT _should_retransmit() - DID TIMEOUT HAPPEN?
    # ================================================================
    # DIFFICULTY: EASY (5 lines)
    #
    # What it does:
    #   Check if we waited too long without getting an ACK
    #   Return True if we should resend, False if still waiting
    #
    # Hint:
    #   if not self.pending_ack:
    #       return False
    #   if self.packet_sent_time is None:
    #       return False
    #   elapsed = time.time() - self.packet_sent_time
    #   timeout = self.timeout_manager.get_timeout()
    #   return elapsed > timeout
    # ================================================================
    def _should_retransmit(self) -> bool:
        """Check if timeout happened."""
        # TODO 8: STUDENT WILL IMPLEMENT THIS METHOD
        pass
    
    # ================================================================
    # DO NOT MODIFY - These are helper methods
    # ================================================================
    def get_statistics(self) -> Statistics:
        """Get protocol statistics."""
        return self.stats


# ====================================================================
# HOW TO SUBMIT YOUR WORK
# ====================================================================
#
# 1. Fill in all 8 TODO methods above
# 2. Run: python3 TestHarness.py
# 3. If score is 10/10 - YOU'RE DONE!
# 4. If score is less than 10/10 - read error and fix code
# 5. Repeat step 2-4 until you get 10/10
#
# ====================================================================
