# orchestration — Deep+Sync (seed → обогащение → синк)

## ruflo-контракт (координация)
- `swarm_init(topology=hierarchical)` — один swarm на прогон; swarmId в память.
- `agent_spawn(agentType per роль, model=opus для lead/verify, sonnet для worker)` — cost-tracking + memory на стадию.
- `memory_store/retrieve(namespace="{ruflo.namespace_prefix}/<epic_slug>")` (дефолт `bft-deep`) — shared fact-base + хендофф артефактов.
- `coordination_consensus` — вердикт дебатов + грудинг-споры.
- **Degradation:** ошибка любого ruflo-tool → native-Task исполнение + файловый хендофф `artefacts/` + лог в error-callback. ruflo down ≠ прогон прерван.

## Стадии
0. FORK: pin repo commit hash → всем субагентам. epic_slug = date-slug из темы Summary (независим от JIRA key). Топология запуска — bft-fast/resources/deep_fork.md.
1. swarm_init + seed (Fast-черновик или полный контекст) → memory. Vague вход → шире `[УТОЧНИТЬ]`.

### DEEP (обогащение seed)
2. context: /bft-context-gen-deep (parallel JIRA/Confluence/repowise/ADR/стейкхолдеры). Per-source fallback: timeout/403 → источник=UNAVAILABLE; claim оттуда → `[УТОЧНИТЬ]`, никогда «пусто=нет данных». Memory-audit гейтит фактбазу.
3. value: ось 1 (enrichment.md §Ценность). bft-value.
4. what-if: ось 2 (enrichment.md §What-if).
5. bounds: ось 3 (enrichment.md §Границы).

### SYNC (укладка в канон)
6. draft: /bft-draft — обогащённый seed → канон-структура MTS.
7. verify: grounding_verifier.md §типизация.
8. validate: /bft-validate — hard-gates + Светофор. Convergence-stop (grounding_verifier.md §convergence).
9. citation: grounding_verifier.md §forced-citation.
10. review: свежий агент, весь документ против канон-ориентира.
11. emit: {bft_store|workspace}/<epic_slug>/<epic_slug>.md (резолв пути — SKILL.md §Резолв конфига) + artefacts/ + нотификация (deep_fork.md §нотификация).
