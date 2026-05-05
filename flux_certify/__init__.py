"""FLUX Certify - Compile guard constraints to FLUX-C bytecode with proof certificates."""
__version__ = '0.1.0'

from .cert import compile_guard, prove_guard, certify, verify_cert, generate_keypair