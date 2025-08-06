# Scripts and Deployment

This directory contains launch scripts and deployment configuration files for both Streamlit and React versions of the Pokemon VGC Summariser.

## 🚀 Launch Scripts

### Windows Batch Files

#### `launch-streamlit.bat`
Launches the Streamlit version of the application.
```bash
# Double-click to run or execute from command line
launch-streamlit.bat
```

**Features:**
- Changes to streamlit-app directory
- Starts Streamlit server on port 8501
- Shows application URL
- Pauses on completion for error checking

#### `launch-react.bat`
Launches the React version of the application.
```bash
# Double-click to run or execute from command line
launch-react.bat
```

**Features:**
- Changes to react-app directory
- Installs npm dependencies
- Starts development server on port 5173
- Shows application URL
- Pauses on completion for error checking

### Cross-Platform Shell Scripts

#### `launch-streamlit.sh`
Launches the Streamlit version on macOS/Linux.
```bash
# Make executable and run
chmod +x scripts/launch-streamlit.sh
./scripts/launch-streamlit.sh
```

#### `launch-react.sh`
Launches the React version on macOS/Linux.
```bash
# Make executable and run
chmod +x scripts/launch-react.sh
./scripts/launch-react.sh
```

## 🚀 Deployment Configuration

### `Procfile`
Heroku deployment configuration for the Streamlit app.
```
web: streamlit run streamlit-app/Summarise_Article.py --server.port=$PORT --server.address=0.0.0.0
```

### `netlify.toml`
Netlify deployment configuration for the React app.
```toml
[build]
  publish = "react-app/dist"
  command = "cd react-app && npm run build"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

## 🔧 Usage

### Local Development
1. **Streamlit**: Double-click `launch-streamlit.bat` or run from command line
2. **React**: Double-click `launch-react.bat` or run from command line

### Deployment
- **Streamlit**: Use `Procfile` for Heroku deployment
- **React**: Use `netlify.toml` for Netlify deployment

## 📝 Customization

### Adding New Launch Scripts
1. Create a new `.bat` file in this directory
2. Follow the naming convention: `launch-[app-name].bat`
3. Include proper error handling and user feedback
4. Update this README

### Deployment Configuration
- **Streamlit**: Modify `Procfile` for different hosting platforms
- **React**: Update `netlify.toml` for different build configurations

## 🛠️ Platform Support

### Windows
- ✅ Batch files (`.bat`)
- ✅ PowerShell scripts (`.ps1`)

### macOS/Linux
- Create shell scripts (`.sh`) for cross-platform compatibility
- Use `#!/bin/bash` shebang for shell scripts

## 🔍 Troubleshooting

### Common Issues
1. **Port already in use**: Change port numbers in launch scripts
2. **Missing dependencies**: Ensure Python/Node.js are installed
3. **Permission errors**: Run as administrator if needed

### Debug Mode
Add `--debug` flag to launch scripts for verbose output:
```bash
python -m streamlit run Summarise_Article.py --server.port 8501 --logger.level debug
```

---

**Note**: These scripts are designed for Windows but can be adapted for other platforms. 