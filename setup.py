"""Setup configuration for AI Note library."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="ainote",
    version="0.1.0",
    author="AI Note Contributors",
    author_email="your-email@example.com",
    description="Cost-effective Python library for meeting transcription and AI-powered note taking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ainote",
    packages=find_packages(exclude=["tests", "examples", "docs"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "boto3>=1.26.0",  # AWS SDK for transcription
    ],
    extras_require={
        "openai": [
            "openai>=1.0.0",
        ],
        "anthropic": [
            "anthropic>=0.18.0",
        ],
        "pdf": [
            "reportlab>=4.0.0",
        ],
        "docx": [
            "python-docx>=1.0.0",
        ],
        "all": [
            "openai>=1.0.0",
            "anthropic>=0.18.0",
            "reportlab>=4.0.0",
            "python-docx>=1.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords="meeting transcription ai notes summaries action-items aws-transcribe openai anthropic",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ainote/issues",
        "Source": "https://github.com/yourusername/ainote",
        "Documentation": "https://github.com/yourusername/ainote/docs",
    },
)
