# Context Management Rules

1. When context_stats shows pressure_pct > 80%, summarize gathered
   information before making additional tool calls
2. Prefer chain recipes over multi-step manual tool sequences
3. Maximum 25 tool calls per turn — summarize and checkpoint before continuing
4. For file exploration: use Glob first, then selective Read (never Read *)
5. Teammates get own context windows — decompose tasks to minimize
   cross-teammate data transfer (use mailbox messaging for coordination,
   not raw data passing)
