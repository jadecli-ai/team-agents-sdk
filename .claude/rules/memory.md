# Memory & Reference-Passing Rules

1. When a tool result contains `[REFERENCE PASSED]`, the full content is
   stored in Dragonfly under the ctx:task: key shown in the message
2. Do NOT request the full content from a reference unless the user
   explicitly asks for it — work with the summary instead
3. If you need to inspect a referenced result, use `redis-cli GET <key>`
4. References expire after 1 hour (ctx: namespace TTL)
5. Cache-first workflow: always check_cache() before executing a cacheable
   tool (Read, Grep, Glob, WebFetch, WebSearch)
