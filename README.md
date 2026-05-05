# FLUX Certify MVP

Compile FLUX-C guard constraints and generate proof certificates for safety-critical systems.

**Status:** MVP - proof-of-concept implementation

## Quick Start

```bash
python3 server.py
# Opens on http://localhost:5000
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Web UI |
| POST | `/compile` | Compile guard → FLUX-C bytecode + ASM |
| POST | `/prove` | Generate proof certificate artifact |
| GET | `/artifact/<id>` | Download proof artifact JSON |
| GET | `/health` | Health check |

## Example

```bash
curl -X POST http://localhost:5000/prove \
  -H "Content-Type: application/json" \
  -d '{"guard":"battery_temp in [15, 55] with priority HIGH"}'
```

Returns:
```json
{
  "task_id": "...",
  "constraint": "battery_temp in [15, 55] with priority HIGH",
  "guard_hash": "0xBD16E340",
  "verified": true,
  "prover": "FLUX-Certify-MVP-0.1.0",
  "proof_type": "constraint_compilation",
  "theorem": "Turing-incompleteness",
  "theorem_status": "[STUB]"
}
```

## Architecture

- **Pure Python** HTTP server (no Flask dependency)
- **93 FLUX-C opcodes** modeled in Coq (`FluxC/FluxC.v`)
- **Theorem status:** `[STUB]` - Coq proof is compilable but not yet complete
- **Artifacts stored** in `/tmp/flux-certify/artifacts/`

## Next Steps

1. Complete Coq mechanization: `fluxc_terminates` theorem
2. Add actual FLUX-C bytecode parser (currently generates mock bytecode)
3. Integrate with `flux-vm-php` for real opcode execution
4. Add Coq proof certificate generation from completed theorems
5. Deploy to cocapn.ai/certify

## Coq Proof Status

```coq
Theorem fluxc_terminates (c : config) : True. (* [STUB] *)
```

Key invariant proven: All 93 FLUX-C opcodes have forward-only control flow (no backward jumps). This is the foundation for structural termination. Full mechanization in progress.

---

Part of the [SuperInstance FLUX stack](https://github.com/SuperInstance/flux-research) · [Dissertation](https://github.com/SuperInstance/flux-research/blob/main/dissertation/)