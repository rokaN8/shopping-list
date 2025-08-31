#!/usr/bin/env python3
"""
SSL Certificate Generation Script for Shopping List App
Generates self-signed certificates for HTTPS support.
"""

import os
import sys
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_self_signed_cert(cert_dir='certs'):
    """Generate a self-signed certificate for the shopping list app."""
    
    # Create certs directory if it doesn't exist
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)
    
    cert_path = os.path.join(cert_dir, 'cert.pem')
    key_path = os.path.join(cert_dir, 'key.pem')
    
    # Check if certificates already exist
    if os.path.exists(cert_path) and os.path.exists(key_path):
        print(f"Certificates already exist at {cert_path} and {key_path}")
        overwrite = input("Do you want to overwrite them? (y/N): ").lower()
        if overwrite != 'y':
            print("Certificate generation cancelled.")
            return False
    
    print("Generating SSL certificate...")
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Create certificate subject
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Local"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Shopping List App"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    # Create certificate
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            x509.IPAddress(ipaddress.IPv4Address("0.0.0.0")),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Write certificate to file
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    # Write private key to file
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    print(f"Certificate generated successfully!")
    print(f"   Certificate: {cert_path}")
    print(f"   Private Key: {key_path}")
    print(f"   Valid for 365 days from {datetime.utcnow().strftime('%Y-%m-%d')}")
    print()
    print("WARNING: This is a self-signed certificate. Your browser will show a security warning.")
    print("   For production use, obtain a certificate from a trusted Certificate Authority.")
    
    return True

if __name__ == '__main__':
    try:
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import ipaddress
        
        success = generate_self_signed_cert()
        sys.exit(0 if success else 1)
        
    except ImportError as e:
        print("Error: Required cryptography package not found.")
        print("Please install it with: pip install cryptography")
        sys.exit(1)
    except Exception as e:
        print(f"Error generating certificate: {e}")
        sys.exit(1)