# Changelog

## [1.1.0] - 2024-01-XX

### Added
- **Новая функциональность**: Makefile теперь запускается из того же репозитория, откуда был распарсен cfg.yaml
- **Улучшение**: Путь к Makefile теперь передается в секцию script сгенерированного пайплайна
- **Улучшение**: Добавлены пользовательские Jinja2 фильтры для работы с путями (dirname, basename)

### Changed
- **Изменение в parser.py**: Метод `parse_all_submodules()` теперь возвращает дополнительную информацию о пути к сабмодулю
- **Изменение в generator.py**: Метод `prepare_job_context()` теперь принимает дополнительный параметр `submodule_path`
- **Изменение в generator.py**: Метод `generate_jobs()` теперь передает путь к сабмодулю в контекст задачи
- **Изменение в job.j2**: Добавлена команда `cd` для перехода в директорию сабмодуля перед выполнением make

### Technical Details
- Путь к Makefile теперь формируется как `os.path.join(submodule_path, default_vars.get("MAKEFILE_PATH", "Makefile"))`
- В шаблоне job.j2 добавлена команда `cd {{ makefile_path | dirname }}` для перехода в директорию сабмодуля
- Команда make теперь использует `{{ makefile_path | basename }}` вместо полного пути
- Добавлены Jinja2 фильтры `dirname` и `basename` для корректной работы с путями

### Example
До изменений:
```yaml
script:
  - "make -f Makefile elab FPGA_BOARD_TYPE=HTG960 FPGA_DEVICE=xczu7ev"
```

После изменений:
```yaml
script:
  - "cd fpga/test_module"
  - "make -f Makefile elab FPGA_BOARD_TYPE=HTG960 FPGA_DEVICE=xczu7ev"
```

Это обеспечивает выполнение Makefile в правильной директории сабмодуля, где он находится.