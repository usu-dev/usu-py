pyproject.toml: pyproject.usu
	./scripts/usu-converter $< $@

.github/workflows/%.yml: .github/workflows/%.usu
	./scripts/usu-converter $< $@

