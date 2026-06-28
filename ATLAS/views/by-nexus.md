# Узлы по Нексусам

```dataview
TABLE owner, confidence, ripeness, node_type
FROM "GROUND/NEXUS" OR "AI-PROCESSES"
WHERE node_id
SORT nexus ASC, confidence DESC
```
