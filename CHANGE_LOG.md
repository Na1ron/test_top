# Лог изменений FPGA Pipeline Generator

## Версия 1.0.0 - Обновление тегов раннеров

### 🎯 **Изменения в тегах раннеров**

**Описание:** Обновлена логика назначения тегов раннеров для оптимизации использования ресурсов CI/CD.

#### **До изменений:**
```yaml
stages:
  elab:
    tags: ["devops-elab-shell"]
  synth:
    tags: ["devops-sandbox-shell"] 
  bitstream:
    tags: ["devops-bitstream-shell"]
```

#### **После изменений:**
```yaml
stages:
  elab:
    tags: ["devops-elab"]        # ← Упрощено
  synth:
    tags: ["devops-synth"]       # ← Изменено
  bitstream:
    tags: ["devops-synth"]       # ← Объединено с synth
```

### 📋 **Затронутые файлы:**
- `fpga_pipeline_generator/config/default.yaml` - обновлены теги по умолчанию
- `FPGA_PIPELINE_README.md` - добавлен раздел "Теги раннеров"

### 🔍 **Результат:**

| Стадия | Новый тег | Обоснование |
|--------|-----------|-------------|
| `elab` | `devops-elab` | Легкие задачи, отдельный пул раннеров |
| `synth` | `devops-synth` | Ресурсоемкие задачи, мощные раннеры |
| `bitstream` | `devops-synth` | Тоже ресурсоемкие, используют общий пул с synth |

### ✅ **Тестирование:**
```bash
# Elaboration → devops-elab
FPGA_TARGET_ARTIFACT=elab ./fpga_gen.py --dry-run

# Synthesis → devops-synth  
FPGA_TARGET_ARTIFACT=synth ./fpga_gen.py --dry-run

# Bitstream → devops-synth
FPGA_TARGET_ARTIFACT=bitstream ./fpga_gen.py --dry-run

# Все вместе → правильное распределение
FPGA_TARGET_ARTIFACT=elab,synth,bitstream ./fpga_gen.py --dry-run
```

### 🎉 **Преимущества:**
1. **Упрощение конфигурации** - меньше типов раннеров для управления
2. **Оптимизация ресурсов** - synth и bitstream используют общий мощный пул
3. **Ясность** - понятные имена тегов без лишних суффиксов
4. **Масштабируемость** - легче масштабировать раннеры по типам нагрузки

---

## Предыдущие изменения

### ✨ **Команда echo с данными cfg.yaml**
- Добавлена команда `echo` в начало каждой задачи с распаршенными данными
- Формат: `echo {stage} [VAR='vars'] [OPTIONS='options'] TARGET='target'`
- Поддержка всех комбинаций полей из cfg.yaml

### 🏗️ **Модульная архитектура**
- Переход от single-file скрипта к полноценному Python пакету
- Разделение на модули: core, templates, config, utils
- Поддержка Jinja2 шаблонов с fallback режимом

### ⚙️ **Современная конфигурация**
- Переход с setup.py на pyproject.toml
- Интеграция инструментов разработки (black, isort, mypy, pytest)
- Удобная установка и развертывание