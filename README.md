# Canvas App (Pyside6)

## Overview

This project is a pluggable tool framework built on PySide6 that provides an interactive canvas for creating and manipulating graphical objects such as boxes and links. The design emphasizes modularity, allowing tools and their corresponding drawables to be easily extended via a plugin mechanism.

## Features

- **Pluggable Tools:** Tools and drawables are decoupled, allowing for seamless extension.
- **Interactive Canvas:** Supports zooming, panning, and mouse interactions.
- **Plugin Manager:** A simple plugin manager compiles a `tools_registry` file that aggregates available tools.
- **Modular Design:** Tools and drawables are organized into separate files for clarity and maintainability.

## Installation

1. **Clone the Repository:**

```bash
git clone https://github.com/yourusername/yourrepository.git
cd yourrepository
```

2. **Create a Virtual Environment:**

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

3. **Install Dependencies:**

```bash
pip install -r requirements.txt
```

## Running the Application

Once the dependencies are installed, you can run the application with:

```bash
python main.py
```

## Tools and Plugins

The tools in this project are pluggable. The plugin manager compiles a `tools_registry` file that registers available tools and their corresponding drawables. For the time being, the registry is compiled manually. An example `tools_registry.py` file looks like this:

```python
from Drawable import BoxDrawable, LinkDrawable
from Tool import MultipointTool

tools_registry = [
    MultipointTool("Box", BoxDrawable),
    MultipointTool("Link", LinkDrawable),
]
```

## Contributing

Contributions are welcome! To add a new tool or drawable:

1. Create a new file for your tool and/or drawable.
2. Implement the necessary methods (e.g., drawing routines, event handling).
3. Update the `tools_registry.py` file or extend the plugin manager to include your tool.

## License

This project is licensed under the CTPL(Canvas Tools Project License). See the [LICENSE.md](LICENSE) file for details.
