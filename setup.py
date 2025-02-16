from setuptools import setup, find_packages

setup(
    name="aidien",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "python-dotenv>=1.0.0",
        "psycopg2-binary>=2.9.0",
        "torch>=2.0.0",
        "transformers>=4.0.0",
        "openai>=1.0.0",
        "tree-sitter>=0.20.0",
        "tree-sitter-language-pack>=0.1.0"
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for embedding and querying codebases using AI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/aidien",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
) 