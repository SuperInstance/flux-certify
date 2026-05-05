"""FLUX Certify CLI."""
import click
import json

from .cert import compile_guard, prove_guard, certify, verify_cert, generate_keypair, GUARD_EXAMPLES

@click.group()
def main():
    """FLUX Certify - Compile guard constraints to FLUX-C bytecode with proof certificates."""
    pass

@main.command()
@click.argument('guard')
def compile(guard):
    """Compile a guard constraint to FLUX-C bytecode."""
    result = compile_guard(guard)
    click.echo(f'GUARD: {result["guard"]}')
    click.echo(f'HASH: {result["guard_hash"]}')
    click.echo(f'OPS: {result["ops"]}')
    click.echo()
    click.echo('FLUX-C Assembly:')
    click.echo(result['asm'])

@main.command()
@click.argument('guard')
def prove(guard):
    """Generate a proof certificate for a guard constraint."""
    result = prove_guard(guard)
    click.echo(json.dumps(result, indent=2))

@main.command()
@click.argument('guard')
@click.option('--signer', default='FLUX-Certify-0.1.0', help='Signer identifier')
def certify_cmd(guard, signer):
    """Generate a signed proof certificate for a guard constraint."""
    result = certify(guard, signer)
    click.echo(json.dumps(result, indent=2))
    if verify_cert(result):
        click.echo()
        click.echo(click.style('Certificate verified: VALID', fg='green'))
    else:
        click.echo()
        click.echo(click.style('Certificate invalid: INVALID', fg='red'))

@main.command()
@click.argument('cert_file')
def verify(cert_file):
    """Verify a proof certificate from a JSON file."""
    with open(cert_file) as f:
        cert = json.load(f)
    if verify_cert(cert):
        click.echo(click.style('Certificate VALID', fg='green'))
        click.echo(f'Constraint: {cert.get("constraint")}')
        click.echo(f'Prover: {cert.get("prover")}')
        click.echo(f'Theorem: {cert.get("theorem")} [{cert.get("theorem_status")}]')
    else:
        click.echo(click.style('Certificate INVALID', fg='red'))

@main.command()
def examples():
    """Show example guard constraints."""
    click.echo('Example FLUX-C Guard Constraints:')
    for i, g in enumerate(GUARD_EXAMPLES, 1):
        click.echo(f'  {i}. {g}')

@main.command()
def keygen():
    """Generate an Ed25519 keypair for signing certificates."""
    keys = generate_keypair()
    click.echo('Public key: ' + keys['public'])
    click.echo('Secret seed: ' + keys['secret'])
    click.echo(click.style('WARNING: Keep the secret seed safe!', fg='yellow'))

@main.command()
@click.argument('guard')
def status(guard):
    """Check the certification status of a guard constraint."""
    result = prove_guard(guard)
    click.echo(f'Constraint: {result["constraint"]}')
    click.echo(f'Theorem: {result["theorem"]}')
    click.echo(f'Status: {result["theorem_status"]}')
    click.echo(f'Description: {result["theorem_description"]}')
    click.echo(f'Hash: {result["guard_hash"]}')

if __name__ == '__main__':
    main()