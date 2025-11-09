"""
TestHarness.py - Automated grading system for BEARDOWN-TP protocol implementation
Simulates various network conditions and tests student implementations
"""

import time
import random
import hashlib
import struct
from typing import Tuple, Optional, List
from abc import ABC, abstractmethod


class NetworkSimulator:
    """Simulates various network conditions"""
    
    def __init__(self, loss_rate=0.0, corruption_rate=0.0, duplication_rate=0.0, 
                 delay_range=(0, 0)):
        self.loss_rate = loss_rate
        self.corruption_rate = corruption_rate
        self.duplication_rate = duplication_rate
        self.delay_range = delay_range
        self.packets_sent = 0
        self.packets_lost = 0
        self.packets_corrupted = 0
        self.packets_delayed = 0
    
    def process_packet(self, packet: bytes) -> Optional[bytes]:
        """
        Process a packet through the simulated network.
        Returns the packet (possibly modified) or None if lost.
        """
        self.packets_sent += 1
        
        # Simulate packet loss
        if random.random() < self.loss_rate:
            self.packets_lost += 1
            return None
        
        # Simulate packet corruption
        if random.random() < self.corruption_rate:
            self.packets_corrupted += 1
            packet = self._corrupt_packet(packet)
        
        # Simulate duplication (return packet twice)
        if random.random() < self.duplication_rate:
            # In real implementation, this would queue the packet twice
            pass
        
        # Simulate delay
        if self.delay_range[1] > 0:
            delay = random.uniform(self.delay_range[0], self.delay_range[1])
            if delay > 0:
                self.packets_delayed += 1
                time.sleep(delay)
        
        return packet
    
    def _corrupt_packet(self, packet: bytes) -> bytes:
        """Randomly flip bits in a packet"""
        packet_list = list(packet)
        # Flip a random bit in a random location (not in length field for testing)
        if len(packet_list) > 7:
            corrupt_pos = random.randint(7, len(packet_list) - 1)
            corrupt_bit = random.randint(0, 7)
            packet_list[corrupt_pos] ^= (1 << corrupt_bit)
        return bytes(packet_list)
    
    def get_stats(self) -> dict:
        """Return network simulation statistics"""
        return {
            'packets_sent': self.packets_sent,
            'packets_lost': self.packets_lost,
            'packets_corrupted': self.packets_corrupted,
            'packets_delayed': self.packets_delayed,
            'loss_rate': self.loss_rate,
            'corruption_rate': self.corruption_rate,
            'duplication_rate': self.duplication_rate
        }


class ProtocolTester(ABC):
    """Base class for protocol tests"""
    
    def __init__(self, test_name: str, points: int):
        self.test_name = test_name
        self.points = points
        self.passed = False
        self.message = ""
        self.start_time = 0
        self.end_time = 0
    
    @abstractmethod
    def run(self) -> bool:
        """Run the test and return True if passed"""
        pass
    
    def get_result(self) -> dict:
        """Return test result as dictionary"""
        return {
            'name': self.test_name,
            'passed': self.passed,
            'points': self.points if self.passed else 0,
            'message': self.message,
            'duration': self.end_time - self.start_time
        }


class BasicTest(ProtocolTester):
    """Test 1: Basic functionality under perfect network conditions (2 pts)"""
    
    def __init__(self):
        super().__init__("Basic Test", 2)
    
    def run(self) -> bool:
        """Test sender and receiver under perfect conditions"""
        self.start_time = time.time()
        
        try:
            # Import student implementations
            from beardown_sender import BeardownSender
            from beardown_receiver import BeardownReceiver
            
            sender = BeardownSender()
            receiver = BeardownReceiver()
            network = NetworkSimulator(loss_rate=0.0)
            
            # Test 1: Send small message (100 bytes)
            test_data = b"A" * 100
            sender.load_data(test_data)
            
            # Simulate one transfer
            packets_transferred = 0
            max_iterations = 100
            iterations = 0
            
            while not sender.is_complete() and iterations < max_iterations:
                # Get packet from sender
                packet = sender.get_next_packet()
                if packet is None:
                    break
                
                # Process through network
                received_packet = network.process_packet(packet)
                if received_packet is None:
                    # Simulate timeout
                    sender.handle_timeout()
                    continue
                
                # Receiver processes packet
                ack = receiver.process_packet(received_packet)
                if ack is not None:
                    sender.process_ack(ack)
                    packets_transferred += 1
                
                iterations += 1
            
            # Verify received data matches sent data
            received_data = receiver.get_received_data()
            if received_data == test_data:
                self.passed = True
                self.message = "Successfully transferred 100 bytes with perfect integrity"
            else:
                self.message = f"Data mismatch: sent {len(test_data)} bytes, received {len(received_data) if received_data else 0} bytes"
        
        except Exception as e:
            self.message = f"Test failed with exception: {str(e)}"
            self.passed = False
        
        self.end_time = time.time()
        return self.passed


class BasicSpeedTest(ProtocolTester):
    """Test 2: Basic speed - transfer data efficiently (1 pt)"""
    
    def __init__(self):
        super().__init__("Basic Speed", 1)
    
    def run(self) -> bool:
        """Test that sender achieves minimum throughput"""
        self.start_time = time.time()
        
        try:
            from beardown_sender import BeardownSender
            from beardown_receiver import BeardownReceiver
            
            sender = BeardownSender()
            receiver = BeardownReceiver()
            network = NetworkSimulator(loss_rate=0.0)
            
            # Send 100KB of data
            test_data = bytes([i % 256 for i in range(100 * 1024)])
            sender.load_data(test_data)
            
            start_transfer = time.time()
            max_iterations = 1000
            iterations = 0
            
            while not sender.is_complete() and iterations < max_iterations:
                packet = sender.get_next_packet()
                if packet is None:
                    break
                
                received_packet = network.process_packet(packet)
                if received_packet is None:
                    sender.handle_timeout()
                    continue
                
                ack = receiver.process_packet(received_packet)
                if ack is not None:
                    sender.process_ack(ack)
                
                iterations += 1
            
            transfer_time = time.time() - start_transfer
            received_data = receiver.get_received_data()
            
            # Check if data matches
            if received_data != test_data:
                self.message = "Data mismatch"
                self.passed = False
            else:
                # Check throughput: should achieve at least 1000 bytes per segment
                # For stop-and-wait: throughput = (segment_size) / (RTT)
                # We should transfer 100KB reasonably quickly
                if transfer_time < 60:  # Should complete in under 60 seconds
                    self.passed = True
                    throughput = len(test_data) / transfer_time / 1024
                    self.message = f"Successfully transferred {len(test_data)/1024:.1f}KB in {transfer_time:.2f}s ({throughput:.2f} KB/s)"
                else:
                    self.message = f"Transfer took too long: {transfer_time:.2f}s"
                    self.passed = False
        
        except Exception as e:
            self.message = f"Test failed with exception: {str(e)}"
            self.passed = False
        
        self.end_time = time.time()
        return self.passed


class RandomDropTest(ProtocolTester):
    """Test 3: Handle packet loss (2 pts)"""
    
    def __init__(self):
        super().__init__("Random Drops", 2)
    
    def run(self) -> bool:
        """Test handling of packet loss"""
        self.start_time = time.time()
        
        try:
            from beardown_sender import BeardownSender
            from beardown_receiver import BeardownReceiver
            
            sender = BeardownSender()
            receiver = BeardownReceiver()
            # Simulate 10% packet loss
            network = NetworkSimulator(loss_rate=0.1)
            
            test_data = b"Test data with loss: " * 100
            sender.load_data(test_data)
            
            max_iterations = 2000
            iterations = 0
            
            while not sender.is_complete() and iterations < max_iterations:
                packet = sender.get_next_packet()
                if packet is None:
                    break
                
                received_packet = network.process_packet(packet)
                if received_packet is None:
                    sender.handle_timeout()
                else:
                    ack = receiver.process_packet(received_packet)
                    if ack is not None:
                        sender.process_ack(ack)
                
                iterations += 1
            
            received_data = receiver.get_received_data()
            if received_data == test_data:
                self.passed = True
                stats = network.get_stats()
                self.message = f"Successfully handled packet loss. Lost {stats['packets_lost']}/{stats['packets_sent']} packets"
            else:
                self.message = "Data corruption detected after loss"
                self.passed = False
        
        except Exception as e:
            self.message = f"Test failed with exception: {str(e)}"
            self.passed = False
        
        self.end_time = time.time()
        return self.passed


class CorruptionTest(ProtocolTester):
    """Test 4: Handle packet corruption (2 pts)"""
    
    def __init__(self):
        super().__init__("Corruption", 2)
    
    def run(self) -> bool:
        """Test handling of corrupted packets"""
        self.start_time = time.time()
        
        try:
            from beardown_sender import BeardownSender
            from beardown_receiver import BeardownReceiver
            
            sender = BeardownSender()
            receiver = BeardownReceiver()
            # Simulate 5% corruption rate
            network = NetworkSimulator(corruption_rate=0.05)
            
            test_data = b"Testing corruption detection mechanism: " * 50
            sender.load_data(test_data)
            
            max_iterations = 2000
            iterations = 0
            
            while not sender.is_complete() and iterations < max_iterations:
                packet = sender.get_next_packet()
                if packet is None:
                    break
                
                received_packet = network.process_packet(packet)
                if received_packet is None:
                    sender.handle_timeout()
                else:
                    ack = receiver.process_packet(received_packet)
                    if ack is not None:
                        sender.process_ack(ack)
                
                iterations += 1
            
            received_data = receiver.get_received_data()
            if received_data == test_data:
                self.passed = True
                stats = network.get_stats()
                self.message = f"Successfully handled corruption. Detected {stats['packets_corrupted']} corrupted packets"
            else:
                self.message = "Data corruption not properly detected"
                self.passed = False
        
        except Exception as e:
            self.message = f"Test failed with exception: {str(e)}"
            self.passed = False
        
        self.end_time = time.time()
        return self.passed


class DuplicationTest(ProtocolTester):
    """Test 5: Handle packet duplication (2 pts)"""
    
    def __init__(self):
        super().__init__("Duplication", 2)
    
    def run(self) -> bool:
        """Test handling of duplicate packets"""
        self.start_time = time.time()
        
        try:
            from beardown_sender import BeardownSender
            from beardown_receiver import BeardownReceiver
            
            sender = BeardownSender()
            receiver = BeardownReceiver()
            # Simulate 5% duplication rate
            network = NetworkSimulator(duplication_rate=0.05)
            
            test_data = b"Deduplication test payload data: " * 40
            sender.load_data(test_data)
            
            max_iterations = 2000
            iterations = 0
            
            while not sender.is_complete() and iterations < max_iterations:
                packet = sender.get_next_packet()
                if packet is None:
                    break
                
                received_packet = network.process_packet(packet)
                if received_packet is None:
                    sender.handle_timeout()
                else:
                    # Simulate potential duplication
                    ack = receiver.process_packet(received_packet)
                    if ack is not None:
                        sender.process_ack(ack)
                    
                    # Simulate duplicate packet
                    if random.random() < 0.05:
                        ack = receiver.process_packet(received_packet)
                
                iterations += 1
            
            received_data = receiver.get_received_data()
            if received_data == test_data:
                self.passed = True
                self.message = "Successfully handled duplicate packets using sequence numbers"
            else:
                self.message = "Duplicate packets not properly handled"
                self.passed = False
        
        except Exception as e:
            self.message = f"Test failed with exception: {str(e)}"
            self.passed = False
        
        self.end_time = time.time()
        return self.passed


class DelayTest(ProtocolTester):
    """Test 6: Handle packet delay (1 pt)"""
    
    def __init__(self):
        super().__init__("Delay", 1)
    
    def run(self) -> bool:
        """Test handling of packet delays"""
        self.start_time = time.time()
        
        try:
            from beardown_sender import BeardownSender
            from beardown_receiver import BeardownReceiver
            
            sender = BeardownSender()
            receiver = BeardownReceiver()
            # Simulate delays up to 500ms
            network = NetworkSimulator(delay_range=(0.0, 0.5))
            
            test_data = b"Delay test with up to 500ms latency: " * 30
            sender.load_data(test_data)
            
            max_iterations = 1500
            iterations = 0
            
            while not sender.is_complete() and iterations < max_iterations:
                packet = sender.get_next_packet()
                if packet is None:
                    break
                
                received_packet = network.process_packet(packet)
                if received_packet is None:
                    sender.handle_timeout()
                else:
                    ack = receiver.process_packet(received_packet)
                    if ack is not None:
                        sender.process_ack(ack)
                
                iterations += 1
            
            received_data = receiver.get_received_data()
            if received_data == test_data:
                self.passed = True
                self.message = f"Successfully handled delays. Transfer completed in {self.end_time - self.start_time:.2f}s"
            else:
                self.message = "Transfer failed with delays"
                self.passed = False
        
        except Exception as e:
            self.message = f"Test failed with exception: {str(e)}"
            self.passed = False
        
        self.end_time = time.time()
        return self.passed


class GradingScript:
    """Main grading script that runs all tests"""
    
    def __init__(self):
        self.tests: List[ProtocolTester] = []
        self.total_points = 0
        self.earned_points = 0
    
    def add_test(self, test: ProtocolTester):
        """Add a test to the grading suite"""
        self.tests.append(test)
        self.total_points += test.points
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("=" * 70)
        print("BEARDOWN-TP Protocol Implementation - Automated Grading Report")
        print("=" * 70)
        print()
        
        results = []
        for test in self.tests:
            print(f"Running: {test.test_name} ({test.points} pts)...", end=" ", flush=True)
            test.run()
            result = test.get_result()
            results.append(result)
            
            status = "PASS" if test.passed else "FAIL"
            print(f"[{status}]")
            print(f"  Message: {result['message']}")
            print(f"  Duration: {result['duration']:.2f}s")
            print(f"  Score: {result['points']}/{result['points']}")
            print()
            
            self.earned_points += result['points']
        
        print("=" * 70)
        print(f"FINAL SCORE: {self.earned_points}/{self.total_points} points")
        print("=" * 70)
        
        return results


def main():
    """Run the grading script"""
    grader = GradingScript()
    
    # Add all test cases
    grader.add_test(BasicTest())
    grader.add_test(BasicSpeedTest())
    grader.add_test(RandomDropTest())
    grader.add_test(CorruptionTest())
    grader.add_test(DuplicationTest())
    grader.add_test(DelayTest())
    
    # Run all tests
    grader.run_all_tests()


if __name__ == "__main__":
    main()
