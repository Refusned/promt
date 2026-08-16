<div align="center">

# promt

**Одна сырая идея на входе. Один готовый мастер-промт на выходе.**

[![Agent Skill](https://img.shields.io/badge/Agent_Skill-open_standard-111827?style=for-the-badge)](https://agentskills.io/specification)
[![Codex](https://img.shields.io/badge/Codex-%24promt-0F766E?style=for-the-badge)](https://learn.chatgpt.com/docs/build-skills)
[![Claude Code](https://img.shields.io/badge/Claude_Code-%2Fpromt-C2410C?style=for-the-badge)](https://code.claude.com/docs/en/slash-commands)
[![MIT](https://img.shields.io/badge/License-MIT-2563EB?style=for-the-badge)](LICENSE)

[![Проверка skill](https://github.com/refusned/promt/actions/workflows/validate.yml/badge.svg)](https://github.com/refusned/promt/actions/workflows/validate.yml)

[English](README.md) | **Русский**

</div>

`promt` превращает короткую мысль, идею или сырой черновик в один самостоятельный мастер-промт для новой сессии Codex, Claude Code или другого ИИ-агента. Написание `promt` выбрано намеренно.

Skill не выполняет исходную задачу. Он упаковывает её в ясную инструкцию с нужным контекстом, scope, границами безопасности, критериями готовности, проверками и форматом результата.

## Посмотрите на разницу

Ввод:

```text
$promt Хочу агента, который проверяет pull request и сообщает только о существенных рисках.
```

Форма результата:

````text
Мастер-промт: проверка существенных рисков pull request
```text
Проведи read-only проверку текущего pull request. Ищи только дефекты, способные повлиять на корректность, безопасность, целостность данных или production-поведение...
```
````

Если отсутствующее решение действительно меняет результат, `promt` сначала задаёт несколько точных вопросов. Если всё понятно, он сразу возвращает готовый мастер-промт.

## Зачем он нужен

| Возможность | Что вы получаете |
|---|---|
| Сохранение замысла | Реальная цель не теряется за общими фразами и лишним prompt engineering |
| Адаптивная глубина | Для простой идеи получается короткий промт, для сложного проекта полноценный рабочий контракт |
| Контекст проекта | Skill учитывает релевантные инструкции и файлы, только когда они действительно улучшают промт |
| Проверяемый результат | При необходимости добавляет scope, non-goals, Definition of Done, проверки и доказательства |
| Безопасные границы | Не переносит секреты и требует подтверждение для публикации, production, платежей, разрушительных действий и расширения scope |
| Одно переносимое ядро | Codex и Claude Code используют один `SKILL.md`, сохраняют язык запроса и обнаруживают skill по двуязычным метаданным |

## Как использовать

Codex:

```text
$promt <ваша идея или черновик задачи>
```

Claude Code:

```text
/promt <ваша идея или черновик задачи>
```

Примеры:

```text
$promt Создай задание для агента, который сравнит три CRM по первичным источникам.
```

```text
/promt Нужно исправить медленный поиск в текущем проекте и доказать улучшение замерами.
```

`/prompt` не является псевдонимом. Команда намеренно называется `promt`.

## Установка на macOS или Linux

Установка использует один локальный клон как источник истины. Каждая команда отказывается заменять уже существующий источник или путь skill.

### 1. Один раз клонируйте репозиторий

```bash
promt_source="${promt_source:-$HOME/.local/share/promt}"

if [ -e "$promt_source" ] || [ -L "$promt_source" ]; then
  printf 'Источник уже существует: %s\n' "$promt_source"
else
  git clone https://github.com/refusned/promt.git "$promt_source"
fi
```

### 2. Подключите к Codex

```bash
promt_source="${promt_source:-$HOME/.local/share/promt}"
promt_target="${promt_target:-$HOME/.agents/skills/promt}"

if [ ! -f "$promt_source/skills/promt/SKILL.md" ]; then
  printf 'SKILL.md не найден в %s\n' "$promt_source"
elif [ -e "$promt_target" ] || [ -L "$promt_target" ]; then
  printf 'Путь уже существует, замена отменена: %s\n' "$promt_target"
else
  mkdir -p "$(dirname "$promt_target")"
  ln -s "$promt_source/skills/promt" "$promt_target"
fi
```

Откройте новую сессию Codex и введите `$promt`.

### 3. Подключите к Claude Code

```bash
promt_source="${promt_source:-$HOME/.local/share/promt}"
promt_target="${promt_target:-$HOME/.claude/skills/promt}"

if [ ! -f "$promt_source/skills/promt/SKILL.md" ]; then
  printf 'SKILL.md не найден в %s\n' "$promt_source"
elif [ -e "$promt_target" ] || [ -L "$promt_target" ]; then
  printf 'Путь уже существует, замена отменена: %s\n' "$promt_target"
else
  mkdir -p "$(dirname "$promt_target")"
  ln -s "$promt_source/skills/promt" "$promt_target"
fi
```

Откройте новую сессию Claude Code и вызовите `/promt`.

Codex документирует личные skills в `$HOME/.agents/skills`, Claude Code в `$HOME/.claude/skills`. Оба поддерживают skill через символическую ссылку. См. официальные руководства [Codex](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills) и [Claude Code](https://code.claude.com/docs/en/slash-commands#where-skills-live).

### Установка только в один проект

Запустите этот блок из корня доверенного проекта. Skill станет доступен только в нём:

```bash
promt_source="${promt_source:-$HOME/.local/share/promt}"
promt_project_root="${promt_project_root:-$PWD}"

if [ ! -f "$promt_source/skills/promt/SKILL.md" ]; then
  printf 'SKILL.md не найден в %s\n' "$promt_source"
else
  for promt_target in \
    "$promt_project_root/.agents/skills/promt" \
    "$promt_project_root/.claude/skills/promt"
  do
    if [ -e "$promt_target" ] || [ -L "$promt_target" ]; then
      printf 'Путь уже существует, замена отменена: %s\n' "$promt_target"
    else
      mkdir -p "$(dirname "$promt_target")"
      ln -s "$promt_source/skills/promt" "$promt_target"
    fi
  done
fi
```

Если символические ссылки недоступны, скопируйте каталог `skills/promt` в нужное место. Копии придётся обновлять отдельно.

### Windows

Установка на Windows пока не проверена. Клонируйте репозиторий, затем скопируйте `skills\promt` только в ещё не существующий путь:

- Codex: `%USERPROFILE%\.agents\skills\promt`
- Claude Code: `%USERPROFILE%\.claude\skills\promt`

## Как это работает

1. Определяет нужный результат и режим задачи: read-only или локальные изменения.
2. Читает ограниченный контекст проекта, только если это заметно улучшит промт.
3. Задаёт от одного до пяти вопросов, только когда ответ меняет результат, scope, полномочия, критерии приёмки или формат.
4. Создаёт ровно один мастер-промт и не выполняет исходную задачу незаметно для пользователя.
5. Подбирает длину внешнего fence динамически, поэтому вложенные Markdown-блоки остаются целыми и пригодными для копирования.

Итоговый промт оставляет внешние записи, production-изменения, расходы, разрушительные операции и расширение scope за явным подтверждением. Значения секретов заменяются placeholders, например `API_KEY`.

## Безопасное обновление

Сначала просмотрите входящие изменения, затем примените fast-forward:

```bash
promt_source="${promt_source:-$HOME/.local/share/promt}"
git -C "$promt_source" fetch origin
git -C "$promt_source" log --oneline HEAD..origin/main
git -C "$promt_source" diff --stat HEAD..origin/main
git -C "$promt_source" merge --ff-only origin/main
```

## Проверка и удаление

Проверьте установку без изменений:

```bash
promt_target="${promt_target:-$HOME/.agents/skills/promt}"
if [ -e "$promt_target" ] || [ -L "$promt_target" ]; then
  ls -ld "$promt_target"
  test -f "$promt_target/SKILL.md"
else
  printf 'Skill не найден: %s\n' "$promt_target"
fi
```

Удалите только символическую ссылку:

```bash
promt_target="${promt_target:-$HOME/.agents/skills/promt}"
if [ -L "$promt_target" ]; then
  unlink "$promt_target"
else
  printf 'Это не символическая ссылка, удаление отменено: %s\n' "$promt_target"
fi
```

Для Claude Code задайте `promt_target` равным `$HOME/.claude/skills/promt`. Скопированный каталог перед удалением нужно проверить вручную.

Удаление ссылки оставляет общий клон на месте, чтобы второй хост мог продолжить работу. Перед ручным удалением клона проверьте его содержимое и локальные изменения.

## Совместимость и реальные проверки

| Хост и область | Проверенное поведение |
|---|---|
| Codex CLI `0.146.0`, личный skill | Обнаружение и явный вызов `$promt` из нового изолированного проекта |
| Codex CLI `0.146.0`, skill проекта | Пустой ввод, локальные изменения, placeholder секрета и вложенные fences |
| Claude Code `2.1.177`, skill проекта | Read-only исследование, обязательный выбор одной задачи, запрет вопросов и вложенные fences |
| Claude Code, личный skill | Путь подтверждён документацией, но автор лично его не устанавливал |
| Windows | Не проверено |

Smoke-тесты Claude Code запускались с отключёнными инструментами. Обнаружение через project-scoped символические ссылки проверено на обоих хостах.

## Проверка репозитория

```bash
python3 -m pip install -r requirements-test.txt
python3 tests/validate_skill.py
```

Валидатор проверяет frontmatter, точный состав публичного Git tree, ссылки на документацию, личность автора коммита, UTF-8, утечки локальных путей и распространённые форматы секретов. GitHub Actions запускает ту же проверку для каждого push и pull request.

## Структура репозитория

```text
.github/workflows/validate.yml  Автоматическая проверка
README.md                       Английская документация
README.ru.md                    Русская документация
skills/promt/SKILL.md           Переносимый Agent Skill с русским рабочим ядром
tests/behavior_cases.md         Сценарии поведения и граничные случаи
tests/validate_skill.py         Проверки структуры и готовности к публикации
```

`promt` следует открытой [спецификации Agent Skills](https://agentskills.io/specification), руководству [Codex по skills](https://learn.chatgpt.com/docs/build-skills) и актуальному руководству Claude Code [Extend Claude with skills](https://code.claude.com/docs/en/slash-commands).

## Лицензия

[MIT](LICENSE)
