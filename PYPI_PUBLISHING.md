# Publishing to PyPI

This guide will walk you through publishing the `livekit-note-taker` library to PyPI (Python Package Index).

## Prerequisites

### 1. Create PyPI Account

1. Go to https://pypi.org/account/register/
2. Create an account (use a strong password)
3. Verify your email address

### 2. Create TestPyPI Account (Recommended for testing)

1. Go to https://test.pypi.org/account/register/
2. Create a separate test account
3. Verify your email

### 3. Install Required Tools

```bash
# Install build and upload tools
pip install --upgrade build twine setuptools wheel
```

## Pre-Publishing Checklist

Before publishing, verify:

- [ ] All tests pass
- [ ] Version number is updated in `pyproject.toml`
- [ ] README.md is complete and accurate
- [ ] LICENSE file is present
- [ ] Dependencies are correct in `pyproject.toml`
- [ ] Author information is updated
- [ ] Project URLs are correct
- [ ] MANIFEST.in includes all necessary files
- [ ] .gitignore excludes build artifacts

## Step-by-Step Publishing

### Step 1: Update Project Metadata

Edit `pyproject.toml` and update:

```toml
[project]
name = "livekit-note-taker"
version = "0.1.0"  # Update version for each release
description = "A modular library for building AI-powered meeting note-taking applications with LiveKit"
authors = [
    {name = "Your Name", email = "your.email@example.com"}  # UPDATE THIS
]

[project.urls]
Homepage = "https://github.com/yourusername/livekit-note-taker"  # UPDATE THIS
Repository = "https://github.com/yourusername/livekit-note-taker"  # UPDATE THIS
```

### Step 2: Clean Previous Builds

```bash
cd /Users/abiolamoses/Downloads/ai-project/livekit-note-taker

# Remove old build artifacts
rm -rf build/
rm -rf dist/
rm -rf *.egg-info
rm -rf livekit_note_taker.egg-info

# Clean Python cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
```

### Step 3: Build the Package

```bash
# Build source distribution and wheel
python -m build

# This creates:
# - dist/livekit-note-taker-0.1.0.tar.gz (source)
# - dist/livekit_note_taker-0.1.0-py3-none-any.whl (wheel)
```

**Expected output:**
```
* Creating venv isolated environment...
* Installing packages in isolated environment... (setuptools>=65.0, wheel)
* Getting build dependencies for sdist...
* Building sdist...
* Building wheel from sdist
* Successfully built livekit-note-taker-0.1.0.tar.gz and livekit_note_taker-0.1.0-py3-none-any.whl
```

### Step 4: Check the Package

```bash
# Verify package metadata
twine check dist/*

# Should show:
# Checking dist/livekit-note-taker-0.1.0.tar.gz: PASSED
# Checking dist/livekit_note_taker-0.1.0-py3-none-any.whl: PASSED
```

### Step 5: Test on TestPyPI (Recommended)

```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# You'll be prompted for:
# Username: your-testpypi-username
# Password: your-testpypi-password
```

**Alternative: Use API Token (More Secure)**

1. Go to https://test.pypi.org/manage/account/token/
2. Create a new API token with scope "Entire account"
3. Save the token (starts with `pypi-`)

```bash
# Upload using token
twine upload --repository testpypi dist/* \
  --username __token__ \
  --password pypi-YOUR-TOKEN-HERE
```

### Step 6: Test Install from TestPyPI

```bash
# Create a test environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  livekit-note-taker[aws]

# Test import
python -c "from livekit_note_taker import NoteManager; print('✅ Import successful')"
python -c "from livekit_note_taker.transcription.aws import AWSTranscriptionProvider; print('✅ AWS provider works')"

# Deactivate and cleanup
deactivate
rm -rf test_env
```

### Step 7: Publish to PyPI (Production)

Once tested on TestPyPI:

```bash
# Upload to real PyPI
twine upload dist/*

# Or with token
twine upload dist/* \
  --username __token__ \
  --password pypi-YOUR-REAL-PYPI-TOKEN
```

**Note:** Package names on PyPI are permanent! Make sure the name is correct.

### Step 8: Verify on PyPI

1. Go to https://pypi.org/project/livekit-note-taker/
2. Verify the page looks correct
3. Check that README renders properly
4. Verify dependencies are listed

### Step 9: Test Install from PyPI

```bash
# Create fresh environment
python -m venv verify_env
source verify_env/bin/activate

# Install from PyPI
pip install livekit-note-taker[aws]

# Test
python -c "from livekit_note_taker import NoteManager; print('✅ Works!')"

# Cleanup
deactivate
rm -rf verify_env
```

## Using API Tokens (Recommended)

API tokens are more secure than passwords.

### For PyPI:

1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Give it a name (e.g., "GitHub Actions" or "Local Publishing")
4. Choose scope:
   - "Entire account" (can upload any project)
   - OR "Project: livekit-note-taker" (specific project only)
5. Copy the token (starts with `pypi-`)

### Save Token for Easy Use:

```bash
# Create ~/.pypirc file
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-PYPI-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TESTPYPI-TOKEN-HERE
EOF

# Secure the file
chmod 600 ~/.pypirc
```

Now you can upload without credentials:
```bash
twine upload dist/*  # Uses ~/.pypirc
```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **0.1.0** - Initial release
- **0.1.1** - Patch (bug fixes)
- **0.2.0** - Minor (new features, backward compatible)
- **1.0.0** - Major (breaking changes or stable release)

Update in `pyproject.toml`:
```toml
version = "0.1.0"  # Change this for each release
```

## Automated Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

**Setup:**
1. Go to your GitHub repo settings
2. Navigate to Secrets and variables → Actions
3. Add secret: `PYPI_API_TOKEN` with your PyPI token
4. Create a GitHub release to trigger publishing

## Release Workflow

Complete workflow for each release:

### 1. Prepare Release

```bash
cd /Users/abiolamoses/Downloads/ai-project/livekit-note-taker

# Update version in pyproject.toml
# version = "0.1.0" → "0.1.1"

# Update CHANGELOG.md (create if doesn't exist)
cat >> CHANGELOG.md << EOF

## [0.1.1] - $(date +%Y-%m-%d)

### Added
- New feature X

### Fixed
- Bug fix Y

### Changed
- Improvement Z
EOF

# Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to 0.1.1"
git push
```

### 2. Create Git Tag

```bash
# Create and push tag
git tag v0.1.1
git push origin v0.1.1

# Or create GitHub release (includes tag)
gh release create v0.1.1 \
  --title "v0.1.1" \
  --notes "Release notes here"
```

### 3. Build and Publish

```bash
# Clean, build, test, publish
rm -rf dist/ build/
python -m build
twine check dist/*
twine upload --repository testpypi dist/*  # Test first
twine upload dist/*  # Then production
```

### 4. Announce

```bash
# Tweet, blog post, etc.
echo "🎉 livekit-note-taker v0.1.1 is now available on PyPI!"
```

## Troubleshooting

### Issue: "File already exists"

You can't upload the same version twice.

**Solution:** Increment version number in `pyproject.toml`

### Issue: "Invalid or non-existent authentication"

**Solution:**
```bash
# Check credentials
cat ~/.pypirc

# Or use token directly
twine upload dist/* --username __token__ --password pypi-YOUR-TOKEN
```

### Issue: "Package name not available"

Someone else already owns that name.

**Solution:** Choose a different name in `pyproject.toml`

### Issue: README not rendering

**Solution:**
- Check README.md syntax
- Ensure it's included in MANIFEST.in
- Verify it's referenced in pyproject.toml

### Issue: Missing dependencies

**Solution:**
```bash
# Check what's in the built package
tar -tzf dist/livekit-note-taker-0.1.0.tar.gz | head -20

# Should include:
# - livekit_note_taker/
# - README.md
# - LICENSE
# - pyproject.toml
```

## Post-Publishing

After publishing:

1. ✅ Verify package page on PyPI
2. 📝 Update README with install instructions
3. 🎉 Announce on social media / GitHub discussions
4. 📊 Monitor downloads: https://pypistats.org/packages/livekit-note-taker
5. 🐛 Watch for bug reports and user feedback

## Quick Reference

```bash
# Complete publishing flow
cd /Users/abiolamoses/Downloads/ai-project/livekit-note-taker

# 1. Update version in pyproject.toml
# 2. Clean and build
rm -rf dist/ build/ *.egg-info
python -m build

# 3. Check
twine check dist/*

# 4. Test on TestPyPI
twine upload --repository testpypi dist/*

# 5. Test install
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ livekit-note-taker

# 6. Publish to PyPI
twine upload dist/*

# 7. Verify
pip install livekit-note-taker
python -c "from livekit_note_taker import NoteManager; print('Success!')"
```

## Resources

- **PyPI Help**: https://pypi.org/help/
- **Packaging Guide**: https://packaging.python.org/
- **Twine Docs**: https://twine.readthedocs.io/
- **Semantic Versioning**: https://semver.org/
- **GitHub Actions**: https://docs.github.com/actions

## Security Best Practices

1. ✅ Use API tokens instead of passwords
2. ✅ Keep tokens secret (never commit to git)
3. ✅ Use token scope limiting
4. ✅ Rotate tokens regularly
5. ✅ Use GitHub Actions for automated publishing
6. ✅ Enable 2FA on PyPI account

## Your First Publish

For your first publish:

```bash
# 1. Update author info in pyproject.toml
# 2. Test everything locally
# 3. Build
python -m build

# 4. Upload to TestPyPI first
twine upload --repository testpypi dist/*

# 5. Test install and verify it works
# 6. If all good, upload to PyPI
twine upload dist/*

# 7. Celebrate! 🎉
```

You can now install your library anywhere with:
```bash
pip install livekit-note-taker[aws]
```

Good luck! 🚀
