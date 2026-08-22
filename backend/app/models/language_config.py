from typing import List, Optional, Dict
from pydantic import BaseModel

class LanguageConfig(BaseModel):
    name: str
    image: str
    source_file: str
    compile: Optional[List[str]] = None
    run: List[str]

LANGUAGE_CONFIGS: Dict[str, LanguageConfig] = {
    "python": LanguageConfig(
        name="python",
        image="college-code-python:3.11",
        source_file="main.py",
        compile=None,
        run=["python", "main.py"]
    ),
    "java": LanguageConfig(
        name="java",
        image="college-code-java:17",
        source_file="Main.java",
        compile=["javac", "Main.java"],
        run=["java", "Main"]
    ),
    "cpp": LanguageConfig(
        name="cpp",
        image="college-code-cpp:gcc",
        source_file="main.cpp",
        compile=["g++", "main.cpp", "-O2", "-o", "main"],
        run=["./main"]
    )
}

def get_language_config(language: str) -> Optional[LanguageConfig]:
    return LANGUAGE_CONFIGS.get(language.lower())
