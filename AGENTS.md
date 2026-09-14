# Maritime Traffic Simulator - Agent Instructions

## Project Goal

Build a **macro-scale maritime traffic simulator** with interactive visualization and simulation capabilities. The simulator aims to:

1. **Visualize** global maritime traffic patterns using real-time or sample data
2. **Simulate** vessel movements, traffic flows, and port operations at macro scale
3. **Analyze** maritime traffic density, routing efficiency, and congestion points
4. **Support** decision-making for maritime operations, port management, and logistics

## Phase Objectives

### Phase 1: Visualization Foundation (COMPLETE)
- Interactive map-based visualization of maritime traffic
- Sample data generation for testing and demonstration
- Basic filtering and control capabilities
- Real-time statistics display

### Phase 2: Data Pipeline
- Integration with AIS (Automatic Identification System) data feeds
- Real-time data ingestion and processing
- Historical data analysis and replay
- Data validation and cleaning pipelines

### Phase 3: Simulation Engine
- Vessel movement algorithms based on maritime physics
- Collision avoidance and routing logic
- Port operations simulation (docking, loading, unloading)
- Weather and sea state effects on traffic
- Traffic pattern prediction

### Phase 4: Advanced Features
- Traffic density heatmaps
- Route optimization suggestions
- Congestion detection and alerts
- Integration with maritime APIs
- Multi-user collaborative viewing

## Technical Stack

- **Runtime**: Python 3.13+
- **Package Manager**: uv
- **Visualization**: Dash + Plotly
- **Data Processing**: pandas, numpy
- **Data Validation**: pandera
- **Type System**: Full type hints with mypy, typing library
- **Code Quality**: black, ruff

## Agent Guidelines

### Code Style
- Follow existing style (black formatting, 88 char line length)
- Use type hints for all public functions
- **Strong typing**: Use `typing` library for complex types (Protocol, TypedDict, etc.) and `pandera` for DataFrame validation schemas
- Include docstrings for all modules, classes, and public functions
- Keep imports organized and minimal

### Architecture
- Maintain clean separation: data → visualization → simulation
- Components should be reusable and testable
- Prefer composition over inheritance
- Use dependency injection for testability

### Testing
- Write tests for all new functionality
- Maintain >90% test coverage for core modules
- Use pytest for test framework
- Include both unit and integration tests
- **Always write tests** when the user requests a new feature, while the associated tests have not been created

### Code Quality
- **ALWAYS run `ruff check` and `ruff format` after completing any task**
- Fix all ruff linting errors before committing
- Run `black check` to verify formatting
- Use `mypy` for type checking on critical modules
- **Pre-commit hooks**: Setup pre-commit to run `ruff check` on every commit. If `ruff check` fails, the commit must fail
- **Always run `ruff format` before committing** to ensure consistent code formatting

### Documentation
- Update docstrings when adding new functionality
- Maintain accurate type hints
- Document assumptions and limitations

### Project Structure
```
seamulator/
├── src/seamulator/
│   ├── data/           # Data models, generators, loaders
│   ├── visualization/  # All UI/visualization code
│   │   ├── components/ # Reusable UI components
│   │   └── styles/    # CSS and styling
│   └── simulation/    # Simulation engine (future)
├── tests/              # All tests
└── docs/              # Documentation (future)
```

## Current Status

- **Phase 1**: COMPLETE ✓
  - Project setup with uv and Python 3.13
  - Sample data generation (100 vessels, 8 types, 10 ports)
  - Interactive Dash app with Plotly maps
  - Vessel filtering by type
  - Statistics panel
  - 9 passing tests

- **Next**: Phase 2 - Data Pipeline

## Quick Start

```bash
# Development
cd seamulator
uv sync
uv run python -m seamulator.visualization.app

# Testing
uv run python -m pytest tests/ -v

# Linting and Formatting
uv run ruff check src/
uv run ruff format src/
uv run black check src/
```

## Workflow Requirements

**After completing ANY task:**
1. Run `ruff check src/` - fix any errors
2. Run `ruff format src/` - auto-format all files
3. Run tests to ensure nothing broke
4. Commit changes
