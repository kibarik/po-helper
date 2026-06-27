---
name: blueprint-model
description: "Точка слияния Blueprint-pipeline: нормализовать Scope Model (journey × слои, scope-маркеры), self-review гейт omissions+hallucinations."
---

# /blueprint-model — нормализация + валидация Scope Model

Шаг pipeline после extract/discover. Приводит `scope-model.yaml` к финальному виду и
проверяет его перед рендером. Общий для обоих режимов.

> Читай `sa_documentation/blueprint_schema.md`.

## 1. Нормализовать
- Упорядочить `journey` по `step`.
- Разложить `cells` по сетке journey × layers; проставить `scope`-маркеры.
- Сжать `scope_of_change` (одна строка на меняемый слой).

## 2. Гейт self-review (omissions + hallucinations)
Проверь и исправь:
- Все `journey`-шаги имеют хотя бы одну `cell`? (нет пропусков)
- Все слои с реальным изменением отражены в `scope_of_change`?
- Каждая `cell` имеет существующий `source`? Нет выдуманных систем/актёров?
- Спорное без источника → в `gaps`, не оставлять в модели.

## 3. Машинная валидация (блокирующая)
```bash
python3 sa_documentation/validate_scope_model.py GROUND/BLUEPRINT/<task>/scope-model.yaml
```
Не `OK` → исправь и перезапусти. Не продолжать с ошибками.

## 4. Выход
```
Scope Model валидна: OK. Шагов=<N>, меняемых слоёв=<M>, gaps=<K>.
→ /blueprint-render
```

## Guardrails
- Не завершать шаг, пока валидатор не вернёт `OK`.
- Не добавлять элементы без источника.
