#!/usr/bin/env python3
"""
IoT Device Simulator for Cyberbullying Evidence Collection
Simulates multiple IoT devices generating and transmitting forensic evidence
Based on the methodology described in Section 3 of the paper
"""

import json
import time
import random
import hashlib
import argparse
import threading
import logging
from datetime import datetime
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

import yaml
import paho.mqtt.client as mqtt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeviceSimulator:
    """Simulates an IoT device for forensic evidence collection"""
    
    def __init__(self, config: Dict):
        self.device_id = config.get('device_id', f"device_{random.randint(1000, 9999)}")
        self.device_type = config.get('device_type', 'smartphone')
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.buffer = []
        
        # Generate RSA key pair for secure key exchange
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        
        # MQTT configuration
        self.broker_host = config.get('broker_host', 'localhost')
        self.broker_port = config.get('broker_port', 1883)
        self.topic_submit = config.get('topic_submit', 'evidence/submit')
        
        # Evidence generation configuration
        self.evidence_types = config.get('evidence_types', ['text', 'audio', 'location'])
        self.interval_seconds = config.get('interval_seconds', 30)
        self.buffer_limit = config.get('buffer_limit', 10)
        
        # MQTT client
        self.mqtt_client = None
        self.running = False
        
        logger.info(f"Initialized DeviceSimulator: {self.device_id} ({self.device_type})")
    
    def generate_evidence(self) -> Dict:
        """Generate simulated evidence based on device type and random selection"""
        
        evidence_type = random.choice(self.evidence_types)
        timestamp = int(time.time() * 1000)
        
        evidence = {
            'device_id': self.device_id,
            'device_type': self.device_type,
            'timestamp': timestamp,
            'evidence_type': evidence_type,
            'case_id': f"case_{random.randint(1000, 9999)}",
        }
        
        # Generate type-specific evidence content
        if evidence_type == 'text':
            evidence['content'] = self.generate_text_evidence()
            evidence['size_bytes'] = len(evidence['content'].encode('utf-8'))
            
        elif evidence_type == 'audio':
            evidence['content'] = self.generate_audio_evidence()
            evidence['size_bytes'] = random.randint(100000, 500000)  # 100KB - 500KB
            
        elif evidence_type == 'location':
            evidence['content'] = self.generate_location_evidence()
            evidence['size_bytes'] = len(str(evidence['content']).encode('utf-8'))
        
        # Add metadata
        evidence['metadata'] = {
            'os_version': random.choice(['iOS 16.4', 'Android 13', 'Android 14']),
            'app_name': random.choice(['WhatsApp', 'Instagram', 'Facebook', 'SMS', 'TikTok']),
            'battery_level': random.randint(10, 100),
            'network_type': random.choice(['WiFi', '4G', '5G'])
        }
        
        return evidence
    
    def generate_text_evidence(self) -> str:
        """Generate simulated text evidence (cyberbullying messages)"""
        messages = [
            "You are worthless and nobody will ever love you.",
            "I hope you disappear from this world forever.",
            "Everyone hates you and you have no friends.",
            "Your posts are so pathetic, just stop trying.",
            "You're so ugly, no wonder nobody wants to talk to you.",
            "Go away, nobody cares about what you think.",
            "You're a complete failure at everything you do.",
            "I wish you would just shut up forever.",
            "Nobody invited you, don't you get it?",
            "You're such a loser, just give up already."
        ]
        return random.choice(messages)
    
    def generate_audio_evidence(self) -> str:
        """Generate simulated audio evidence (encrypted placeholder)"""
        # In production, this would be actual audio data
        # For simulation, we generate a random string representing encrypted audio
        return f"audio_data_{random.randint(100000, 999999)}"
    
    def generate_location_evidence(self) -> Dict:
        """Generate simulated location evidence"""
        return {
            'latitude': random.uniform(-90, 90),
            'longitude': random.uniform(-180, 180),
            'accuracy': random.randint(5, 50),
            'speed': random.uniform(0, 100)
        }
    
    def encrypt_evidence(self, evidence: Dict) -> Dict:
        """Encrypt evidence using AES-256 (simulated with Fernet)"""
        
        # Serialize evidence to JSON
        evidence_json = json.dumps(evidence)
        
        # Encrypt with AES-256
        encrypted_data = self.cipher.encrypt(evidence_json.encode('utf-8'))
        
        # Generate SHA-256 hash for integrity
        hash_value = hashlib.sha256(evidence_json.encode('utf-8')).hexdigest()
        
        # Encrypt the symmetric key with RSA
        encrypted_sym_key = self.public_key.encrypt(
            self.encryption_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return {
            'encrypted_data': encrypted_data.hex(),
            'encrypted_sym_key': encrypted_sym_key.hex(),
            'hash': hash_value,
            'original_size': len(evidence_json.encode('utf-8'))
        }
    
    def create_payload(self, evidence: Dict) -> Dict:
        """Create the complete payload for blockchain submission"""
        
        encrypted = self.encrypt_evidence(evidence)
        
        payload = {
            'device_id': self.device_id,
            'evidence_type': evidence['evidence_type'],
            'timestamp': evidence['timestamp'],
            'case_id': evidence.get('case_id', ''),
            'encrypted_data': encrypted['encrypted_data'],
            'encrypted_sym_key': encrypted['encrypted_sym_key'],
            'hash': encrypted['hash'],
            'metadata': evidence.get('metadata', {})
        }
        
        # Add signature (non-repudiation)
        # In production, use ECDSA signature
        payload['signature'] = hashlib.sha256(
            json.dumps(payload).encode('utf-8')
        ).hexdigest()
        
        return payload
    
    def on_connect(self, client, userdata, flags, rc):
        """MQTT connect callback"""
        if rc == 0:
            logger.info(f"Device {self.device_id} connected to MQTT broker")
        else:
            logger.error(f"Device {self.device_id} failed to connect with code {rc}")
    
    def on_publish(self, client, userdata, mid):
        """MQTT publish callback"""
        logger.debug(f"Device {self.device_id} published message ID: {mid}")
    
    def transmit_evidence(self, payload: Dict) -> bool:
        """Transmit evidence to blockchain via MQTT"""
        
        if self.mqtt_client is None:
            logger.error(f"Device {self.device_id}: MQTT client not initialized")
            return False
        
        try:
            message = json.dumps(payload)
            result = self.mqtt_client.publish(
                self.topic_submit,
                message,
                qos=1
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Device {self.device_id}: Evidence submitted successfully")
                return True
            else:
                logger.warning(f"Device {self.device_id}: Failed to publish, buffering")
                self.buffer.append(payload)
                if len(self.buffer) > self.buffer_limit:
                    logger.warning(f"Device {self.device_id}: Buffer limit reached, dropping oldest")
                    self.buffer.pop(0)
                return False
                
        except Exception as e:
            logger.error(f"Device {self.device_id}: Transmission error: {e}")
            return False
    
    def process_buffer(self):
        """Process buffered evidence when connectivity is restored"""
        
        if not self.buffer:
            return
        
        logger.info(f"Device {self.device_id}: Processing {len(self.buffer)} buffered items")
        
        success_count = 0
        failed_items = []
        
        for item in self.buffer:
            if self.transmit_evidence(item):
                success_count += 1
            else:
                failed_items.append(item)
        
        # Update buffer
        self.buffer = failed_items
        
        logger.info(f"Device {self.device_id}: Buffer processed. Sent: {success_count}, Failed: {len(failed_items)}")
    
    def run_cycle(self):
        """Run a single evidence collection and transmission cycle"""
        
        # Generate evidence
        evidence = self.generate_evidence()
        
        # Create payload
        payload = self.create_payload(evidence)
        
        # Transmit
        self.transmit_evidence(payload)
        
        # Process buffer
        self.process_buffer()
    
    def start(self):
        """Start the device simulator"""
        
        # Initialize MQTT client
        self.mqtt_client = mqtt.Client(
            client_id=f"{self.device_id}_client",
            clean_session=True
        )
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_publish = self.on_publish
        
        try:
            self.mqtt_client.connect(self.broker_host, self.broker_port, 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            logger.error(f"Device {self.device_id}: Failed to connect to MQTT broker: {e}")
            return
        
        self.running = True
        logger.info(f"Device {self.device_id}: Started. Interval: {self.interval_seconds}s")
        
        try:
            while self.running:
                self.run_cycle()
                time.sleep(self.interval_seconds)
        except KeyboardInterrupt:
            logger.info(f"Device {self.device_id}: Stopping...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the device simulator"""
        self.running = False
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        logger.info(f"Device {self.device_id}: Stopped")


class DeviceManager:
    """Manages multiple IoT device simulators"""
    
    def __init__(self, config_file: str):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.devices = []
        self.executor = None
        self.running = False
        
        logger.info(f"Loaded configuration from {config_file}")
    
    def create_devices(self):
        """Create device simulators based on configuration"""
        
        num_devices = self.config.get('num_devices', 5)
        device_config = self.config.get('device_config', {})
        
        for i in range(num_devices):
            config = {
                'device_id': f"device_{i+1:04d}",
                'device_type': random.choice(['smartphone', 'wearable', 'smart_home']),
                'broker_host': device_config.get('broker_host', 'localhost'),
                'broker_port': device_config.get('broker_port', 1883),
                'topic_submit': device_config.get('topic_submit', 'evidence/submit'),
                'evidence_types': device_config.get('evidence_types', ['text', 'audio', 'location']),
                'interval_seconds': random.randint(15, 45),
                'buffer_limit': device_config.get('buffer_limit', 10)
            }
            
            device = DeviceSimulator(config)
            self.devices.append(device)
        
        logger.info(f"Created {len(self.devices)} devices")
    
    def start_all(self):
        """Start all device simulators"""
        
        if not self.devices:
            self.create_devices()
        
        self.running = True
        self.executor = ThreadPoolExecutor(max_workers=len(self.devices))
        
        logger.info(f"Starting {len(self.devices)} devices...")
        
        for device in self.devices:
            self.executor.submit(device.start)
    
    def stop_all(self):
        """Stop all device simulators"""
        self.running = False
        if self.executor:
            self.executor.shutdown(wait=True)
        logger.info("All devices stopped")


def main():
    parser = argparse.ArgumentParser(description='IoT Device Simulator for Cyberbullying Forensics')
    parser.add_argument('--config', default='config.yaml', help='Configuration file path')
    parser.add_argument('--num-devices', type=int, help='Number of devices to simulate')
    parser.add_argument('--interval', type=int, help='Interval between evidence submissions (seconds)')
    parser.add_argument('--broker', default='localhost', help='MQTT broker host')
    parser.add_argument('--port', type=int, default=1883, help='MQTT broker port')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {args.config} not found, using defaults")
        config = {}
    
    # Override with command line arguments
    if args.num_devices:
        config['num_devices'] = args.num_devices
    if args.interval:
        config['interval_seconds'] = args.interval
    if args.broker:
        config['broker_host'] = args.broker
    if args.port:
        config['broker_port'] = args.port
    
    # Create and start device manager
    manager = DeviceManager(args.config)
    manager.create_devices()
    
    if args.once:
        # Run a single cycle for each device
        for device in manager.devices:
            device.run_cycle()
        logger.info("Single cycle complete")
    else:
        # Run continuously
        try:
            manager.start_all()
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            manager.stop_all()


if __name__ == "__main__":
    main()