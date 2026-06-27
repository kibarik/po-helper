# Низкий Confidence Point (<0.5)

```dataview
TABLE nexus, owner, confidence, ripeness
FROM "GROUND/NEXUS" OR "AI-PROCESSES"
WHERE node_id AND confidence < 0.5
SORT confidence ASC
```
