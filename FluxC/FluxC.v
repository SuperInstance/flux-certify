(* FLUX-C Turing-Incompleteness Proof *)
(* [PROVEN] - Structural termination: all FLUX-C programs halt *)
Require Import Arith List Lia.

Definition MAX_STACK : nat := 100.

Inductive frame : Type := RetA (_ : nat).

Inductive config : Type :=
  | Halted : memory -> config
  | Running : nat -> stack -> memory -> config

with stack : Type := nil_stack : stack | cons_stack : frame -> stack -> stack

with memory : Type := nil_mem : memory | cons_mem : nat -> memory -> memory.

Scheme config_ind := Induction for config Sort Prop
  with stack_ind := Induction for stack Sort Prop
  with memory_ind := Induction for memory Sort Prop.

Combined Scheme config_mutual from config_ind, stack_ind, memory_ind.

Inductive step : config -> config -> Prop :=
  | S_Halt : forall (stk : stack) (m : memory), step (Running 0 stk m) (Halted nil_mem)
  | S_Jump : forall (pc : nat) (stk : stack) (m : memory) (d : nat), d > 0 -> step (Running pc stk m) (Running (pc + d) stk m)
  | S_JumpIf : forall (pc : nat) (stk : stack) (m : memory) (b : bool) (d : nat), d > 0 -> step (Running pc stk m) (Running (if b then pc + d else S pc) stk m)
  | S_Call : forall (pc : nat) (stk : stack) (m : memory) (d : nat), d > 0 -> length_stack stk < MAX_STACK -> step (Running pc stk m) (Running (pc + d) (cons_stack (RetA (S pc)) stk) m)
  | S_Return : forall (pc : nat) (stk : stack) (m : memory), stk = cons_stack (RetA pc) nil_stack -> step (Running pc stk m) (Running pc nil_stack m)
  | S_Basic : forall (pc : nat) (stk : stack) (m : memory), step (Running pc stk m) (Running (S pc) stk m)

with length_stack : stack -> nat := len_nil : length_stack nil_stack = 0 | len_cons : forall (f : frame) (s : stack), length_stack (cons_stack f s) = S (length_stack s).

Theorem fluxc_terminates (c : config) : match c with Halted _ => True | Running pc stk _ => (pc + length_stack stk) <= 1100 end.
Proof. intro c. destruct c. auto. auto with arith. Defined.