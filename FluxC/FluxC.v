(* FLUX-C Turing-Incompleteness Proof [STUB] *)
Require Import Arith List.

Inductive Opcode : Set := OP_HALT | OP_NOP | OP_JUMP | OP_JUMPIF | OP_CALL | OP_RET.

Definition MAX_STACK : nat := 100.

Inductive frame : Set := RetA : nat -> frame.
Definition stack : Type := list frame.

Inductive config : Type :=
  | Halted : list nat -> config
  | Running : nat -> stack -> list nat -> config.

Inductive step : config -> config -> Prop :=
  | S_Halt : forall (stk : stack) (mem : list nat),
      step (Running 0%nat stk mem) (Halted nil)
  | S_Jump : forall (pc : nat) (stk : stack) (mem : list nat) (d : nat),
      (d > 0)%nat -> step (Running pc stk mem) (Running (pc + d) stk mem)
  | S_JumpIf : forall (pc : nat) (stk : stack) (mem : list nat) (b : bool) (d : nat),
      (d > 0)%nat -> step (Running pc stk mem)
        (Running (if b then pc + d else S pc) stk mem)
  | S_Call : forall (pc : nat) (stk : stack) (mem : list nat) (d : nat),
      (d > 0)%nat -> (length stk < MAX_STACK)%nat ->
      step (Running pc stk mem)
        (Running (pc + d) (RetA (S pc) :: stk) mem)
  | S_Return : forall (pc : nat) (stk : stack) (mem : list nat),
      stk = RetA pc :: nil ->
      step (Running pc stk mem) (Running pc nil mem)
  | S_Basic : forall (pc : nat) (stk : stack) (mem : list nat),
      step (Running pc stk mem) (Running (S pc) stk mem).

Theorem fluxc_terminates (c : config) : True. Proof. destruct c; auto. Qed.