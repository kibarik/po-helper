# Консолидация бэклога

## Зоны поставки

### ground-vault-core — Реализация ядра памяти: версионирование данных, граф зависимостей, поиск (FTS/семантика), проверка здоровья (ripeness/freshness) и хранение контекста (нексусы, процессы, expectancies). (surface: memory-core)
### jira-integration-bus — Полный цикл интеграции с JIRA: индексация, двухсторонняя синхронизация, схема переходов, реестр маппинга, массовые операции и аудит действий. (surface: jira-connector)
### sprint-process-automation — Автоматизация процессов спринта: хард-гейты (DoR/DoD), планирование (capacity, зависимости), закрытие, метрики и визуальное планирование (Excalidraw). (surface: process-engine)
### llm-orchestration-layer — Оркестрация ИИ-агентов: роутинг запросов (fast/deep lanes), реестр инструментов, адверсариальные механизмы и оптимизация вызовов. (surface: llm-routing)
### intake-and-triage — Обработка входящих потоков: омниканальный прием (email, chat, mentions), классификация, дедупликация и маршрутизация в бэклог/агенты. (surface: router)
### content-synthesis-engine — Генерация контента и анализ: создание БФТ, релизных нот, тех-брифов, саммари, редактирование текстов и поддержка принятия решений. (surface: po-helper)
### user-interaction-surface — Пользовательский интерфейс и клиенты: веб-отображение, мобильные приложения, команды (CLI), онбординг и визуализация данных. (surface: ui-shell)
### system-observability — Наблюдаемость и надежность: провенанс (логирование), State of Record (оракул релизов), регрессионное тестирование и пайплайны деплоя. (surface: ops-core)

## Инкременты

- **ground-vault-core:MVP: Core Storage & Versioning** (Фундаментальная реализация хранилища (двухъярусная архитектура) и механизма версионирования (Git-подобное ветвление), а также базового контроля задач для управления потоками данных.): #55, #77, #118
- **ground-vault-core:MVP+1: Retrieval, Security & Lifecycle** (Обеспечение доступа к данным через поисковый слой и граф зависимостей, защита ядра от некорректного ввода (relevance-гейт) и реализация событийного обновления контекста (freshness).): #59, #75, #100
- **ground-vault-core:MVP+2: Observability, Debugging & Health** (Внедрение инструментов для измерения качества системы, визуализации связей для отладки и управления деградацией/устареванием данных в долгосрочной памяти.): #104, #106, #117
- **ground-vault-core:MVP+3: Business Logic & Integration** (Реализация высокоуровневых бизнес-функций (реестры ожиданий, учет ролей), внешняя синхронизация артефактов и финальная калибровка точности через сравнение с планом.): #103, #109, #128, #134
- **jira-integration-bus:MVP: Discovery & Indexing** (Фундаментальный уровень для взаимодействия с JIRA. Включает индексацию данных (#57), создание метадата-реестра для быстрого доступа (#60) и Discovery схемы статусов (#63) для понимания структуры и workflow внешней системы без активных изменений.): #57, #60, #63
- **jira-integration-bus:MVP+1: Architecture, Governance & Hygiene** (Этап выравнивания архитектур и наложения правил. Сначала определяется маппинг сущностей (#74), затем устанавливаются каноны работы и линтеры (#71), расширяющиеся правила для кросс-проектного взаимодействия (#69). На этой базе строится навык груминга (#64) и внедряется аудит действий (#66) для контроля вносимых изменений.): #64, #66, #69, #71, #74
- **jira-integration-bus:MVP+2: Active Synchronization & Automation** (Завершающий уровень интеграции, обеспечивающий двухсторонний поток данных и массовые операции. Включает настройку моста для отчетности (#123), полную синхронизацию планов с Gantt (#58) и инструмент массовых операций (#62) для эффективного управления деревьями задач.): #58, #62, #123
- **sprint-process-automation:MVP: Foundations and Standards** (Define the fundamental processes, roles, and mindset (standards, PO roles, BFT methodology) before implementing automation. Establishes the 'Rules of the Game' including the Definition of Ready.): #70, #85, #91, #96, #97
- **sprint-process-automation:MVP+1: Structure and Hard Gates** (Implement strict structural constraints and ownership invariants (Hard Gates) to ensure sprint integrity. Defines the decomposition zones and capacity planning foundation.): #84, #133, #146, #147
- **sprint-process-automation:MVP+2: Visual Planning and Tooling** (Deploy and fix the tools required for interactive and visual planning (Excalidraw, Sprint Planner commands) and integrate them with the review process.): #47, #51, #83, #89
- **sprint-process-automation:MVP+3: Execution Loop Management** (Automate the ongoing sprint lifecycle: AI estimation defaults, day-by-day backlog actualization, and the rapid sprint closure protocol.): #132, #136, #137
- **sprint-process-automation:MVP+4: Analytics and Optimization** (Focus on the analytical layer: enriching context for metrics, tracking performance (burndown/lead time), analyzing graphs, and enabling Scrum Master forecasting skills.): #67, #68, #135, #138
- **llm-orchestration-layer** (зона в пределах одной итерации): #61, #78, #79, #112, #141, #144
- **intake-and-triage** (зона в пределах одной итерации): #65, #80, #102, #111, #127, #142
- **content-synthesis-engine:MVP: Core Text & Analysis Capabilities** (Establish the foundational AI skills necessary for content synthesis: code context analysis, technical-to-business translation, decision support, and text editing utilities. These are independent building blocks that will be utilized by more complex workflows.): #81, #82, #121, #139
- **content-synthesis-engine:MVP+1: BFT Workflow & Quality Loop** (Implement the core structured research and BFT (Big Functional Task) lifecycle. This includes defining the output format, automating BFT creation in GitHub, handling post-creation notifications, and establishing a quality feedback loop via retrospective analysis.): #98, #108, #114, #125
- **content-synthesis-engine:MVP+2: Strategy & Release Management** (Leverage the established engine to generate high-level strategic artifacts and comprehensive release communications. This increment focuses on business-facing outputs like strategy presentations and detailed release narratives/cards.): #53, #101, #143
- **user-interaction-surface** (зона в пределах одной итерации): #105, #107, #120, #140
- **system-observability** (зона в пределах одной итерации): #52, #95, #99, #110, #131, #145