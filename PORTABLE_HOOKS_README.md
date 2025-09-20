# Claude Code Hooks - Portable Installation System

This directory contains a completely portable and self-configuring hook system for Claude Code that works across different projects, environments, and platforms.

## 🚀 Quick Start (One Command Installation)

From your project root directory:

```bash
# Run the portable installer
python3 .claude/install_hooks.py

# Or with enhanced output
python3 .claude/install_hooks.py --verbose
```

That's it! The installer will:
- Detect your environment automatically
- Configure paths for your system
- Set up all necessary files
- Validate the installation
- Provide next steps

## 📦 What's Included

### Core Installation Scripts
- **`install_hooks.py`** - One-command portable installer
- **`validate_installation.py`** - Installation validator and repair tool
- **`hooks/setup_hooks.py`** - Enhanced configuration script
- **`hooks/execute_hook.py`** - Universal hook executor

### Environment Detection
- **`hooks/utils/environment_detector.py`** - Comprehensive environment detection
- **`hooks/utils/dependency_manager.py`** - Dependency management with fallbacks

## 🌍 Cross-Platform Compatibility

### Supported Platforms
- ✅ **Windows** (including WSL)
- ✅ **macOS** (Intel and Apple Silicon)
- ✅ **Linux** (all major distributions)

### Supported Environments
- ✅ **System Python** (python/python3)
- ✅ **Virtual Environments** (venv, virtualenv)
- ✅ **Conda Environments**
- ✅ **Pipenv**
- ✅ **PyEnv**

### Supported Project Structures
- ✅ **Regular Git Repository** (.claude as normal folder)
- ✅ **Git Submodule** (.claude as git submodule)
- ✅ **Standalone Project** (no git)

## 🔧 Installation Methods

### Method 1: Portable Installer (Recommended)

```bash
# Basic installation
python3 .claude/install_hooks.py

# With detailed output
python3 .claude/install_hooks.py --verbose

# Force reinstallation
python3 .claude/install_hooks.py --force
```

### Method 2: Manual Setup

```bash
# Traditional setup (still enhanced)
python3 .claude/hooks/setup_hooks.py
```

### Method 3: Validation Only

```bash
# Check existing installation
python3 .claude/validate_installation.py

# Detailed validation
python3 .claude/validate_installation.py --verbose

# Attempt automatic repairs
python3 .claude/validate_installation.py --repair
```

## 📊 Environment Reports

Generate detailed environment reports:

```bash
# Environment detection report
python3 .claude/install_hooks.py --environment-report

# Dependency status report
python3 .claude/install_hooks.py --dependency-report

# Combined validation report
python3 .claude/validate_installation.py --verbose
```

## 🔍 What Gets Detected Automatically

### Platform Information
- Operating system and version
- Architecture (x86_64, arm64, etc.)
- WSL detection on Windows
- Path separator handling

### Python Environment
- Python version and executable location
- Virtual environment detection and type
- Available Python executables (python, python3, etc.)
- Recommended executable for your platform

### Project Structure
- Project root detection
- Git repository status
- Submodule detection
- Project type (Node.js, Python, Docker, etc.)

### Dependencies
- Optional package availability
- Fallback implementations
- Installation suggestions
- Package manager detection

## 🛠️ Advanced Features

### Dependency Management
The system includes intelligent dependency management:

- **Optional Dependencies**: Missing packages don't break functionality
- **Fallback Implementations**: Built-in alternatives for common packages
- **Graceful Degradation**: Features disable cleanly when dependencies unavailable
- **Auto-Installation**: Offers to install missing packages when possible

### Environment Validation
Comprehensive validation includes:

- Python version compatibility
- Required file structure
- Configuration syntax validation
- Hook execution testing
- Git integration status

### Automatic Repair
The validation tool can automatically fix:

- Missing configuration files
- Incorrect file permissions
- Broken settings.json
- Missing dependencies
- Git tracking issues

## 📁 Directory Structure

```
.claude/
├── install_hooks.py                    # Main installer script
├── validate_installation.py            # Validation and repair tool
├── settings.json.sample               # Template configuration
├── settings.json                      # Generated configuration (gitignored)
├── hooks/
│   ├── setup_hooks.py                 # Enhanced setup script
│   ├── execute_hook.py                # Universal hook executor
│   ├── pre_tool_use.py               # Pre-tool hook
│   ├── post_tool_use.py              # Post-tool hook
│   ├── session_start.py              # Session start hook
│   ├── utils/
│   │   ├── environment_detector.py   # Environment detection
│   │   ├── dependency_manager.py     # Dependency management
│   │   └── [other utilities...]
│   └── config/
│       ├── __claude_hook__allowed_root_files.sample
│       └── __claude_hook__valid_test_paths.sample
└── [template files...]
```

## ⚙️ Configuration

### Automatic Configuration
The installer automatically:
- Detects your project root
- Configures correct paths for your system
- Sets up appropriate Python executable
- Configures git ignore rules
- Creates environment-specific settings

### Manual Configuration
After installation, you may need to:

1. **Copy project configuration files**:
   ```bash
   cp .claude/copy-to-root-project-rename-to:CLAUDE.md ./CLAUDE.md
   cp .claude/copy-to-root-project-rename-to:CLAUDE.local.md ./CLAUDE.local.md
   cp .claude/.mcp.json.sample ./.mcp.json
   ```

2. **Configure API access**:
   Edit `.mcp.json` and add your API token

3. **Set up hook protection** (optional):
   ```bash
   cp .claude/hooks/config/__claude_hook__allowed_root_files.sample \
      .claude/hooks/config/__claude_hook__allowed_root_files
   cp .claude/hooks/config/__claude_hook__valid_test_paths.sample \
      .claude/hooks/config/__claude_hook__valid_test_paths
   ```

## 🚨 Troubleshooting

### Common Issues

#### "Could not find project root"
- Ensure you're running from within a project directory
- Make sure one of these files exists: `CLAUDE.md`, `.git`, `package.json`, `pyproject.toml`
- Check that `.claude/hooks/` directory exists

#### "Python version too old"
- Python 3.7+ is required
- Use `python3 --version` to check your version
- Consider using pyenv or conda to upgrade

#### "Hook execution failed"
- Run the validation tool: `python3 .claude/validate_installation.py`
- Check file permissions: `chmod +x .claude/hooks/*.py`
- Verify Python path in settings.json

#### "Dependencies missing"
- Most dependencies are optional with fallback implementations
- Use `--dependency-report` to see what's missing
- Install specific packages as needed

### Getting Help

1. **Run diagnostics**:
   ```bash
   python3 .claude/validate_installation.py --verbose
   ```

2. **Generate environment report**:
   ```bash
   python3 .claude/install_hooks.py --environment-report
   ```

3. **Try automatic repair**:
   ```bash
   python3 .claude/validate_installation.py --repair
   ```

4. **Force reinstallation**:
   ```bash
   python3 .claude/install_hooks.py --force
   ```

## 🔄 Migration from Existing Installations

If you have an existing Claude hooks setup:

1. **Backup current configuration**:
   ```bash
   cp .claude/settings.json .claude/settings.json.backup
   ```

2. **Run the installer**:
   ```bash
   python3 .claude/install_hooks.py
   ```

3. **Validate the upgrade**:
   ```bash
   python3 .claude/validate_installation.py
   ```

The installer preserves existing configurations while upgrading the system.

## 🌟 Benefits of Portable Hooks

### For Developers
- **Zero Configuration**: Works out of the box on any system
- **Cross-Platform**: Same setup works on Windows, macOS, and Linux
- **Environment Aware**: Adapts to virtual environments automatically
- **Self-Validating**: Built-in diagnostics and repair capabilities

### For Teams
- **Consistent Setup**: Everyone gets the same configuration
- **Easy Onboarding**: New team members can set up in one command
- **Version Control**: Can be distributed via git submodules
- **Maintainable**: Centralized updates and improvements

### For Projects
- **Portable**: Works when .claude is copied between projects
- **Resilient**: Graceful handling of missing dependencies
- **Flexible**: Adapts to different project structures
- **Future-Proof**: Designed for long-term compatibility

## 📄 License

This portable hook system is part of the Claude Code hooks project and follows the same licensing terms as the main project.

## 🤝 Contributing

To contribute to the portable hooks system:

1. Test changes across multiple platforms
2. Ensure backward compatibility
3. Add appropriate error handling
4. Update documentation
5. Include validation tests

---

**Need help?** Run `python3 .claude/validate_installation.py --verbose` for detailed diagnostics.