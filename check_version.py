import toml

with open("pyproject.toml", "r") as f:
    data = toml.load(f)
    print(f"pyproject.toml version: {data['project']['version']}")
