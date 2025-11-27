# Contributing to ComfyUI Novel Nodes Collection

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Your ComfyUI version and system information
- Screenshots or error logs if applicable

### Suggesting Features

Feature requests are welcome! Please:
- Check if the feature has already been requested
- Clearly describe the feature and its use case
- Explain how it would benefit users

### Submitting Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/comfyui-novel-nodes-collection.git
   cd comfyui-novel-nodes-collection
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Test your changes thoroughly

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: brief description of your changes"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide a clear description of the changes
   - Reference any related issues
   - Include screenshots if UI changes are involved

## 📝 Code Style Guidelines

### Python Code
- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular

### Node Design
- Provide clear input/output descriptions
- Use appropriate data types
- Include helpful tooltips and defaults
- Test with various input sizes

### Documentation
- Update README files when adding features
- Include usage examples
- Document any new dependencies
- Keep documentation clear and concise

## 🧪 Testing

Before submitting:
1. Test your node with various inputs
2. Verify it works with different ComfyUI versions
3. Check for memory leaks with large inputs
4. Ensure error handling is robust

## 📋 Commit Message Guidelines

Use clear, descriptive commit messages:
- `Add: new feature or node`
- `Fix: bug description`
- `Update: documentation or dependencies`
- `Refactor: code improvement`
- `Remove: deprecated feature`

## 🔍 Code Review Process

1. All PRs will be reviewed by maintainers
2. Feedback will be provided for improvements
3. Once approved, changes will be merged
4. Contributors will be credited in releases

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 💬 Questions?

Feel free to open an issue for any questions or discussions!

---

Thank you for contributing to the ComfyUI community! 🎉
