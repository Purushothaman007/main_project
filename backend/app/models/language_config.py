from typing import List, Optional, Dict
from pydantic import BaseModel

# Sentinel exit code used by combined_run scripts to signal a compile failure
# (distinguishable from runtime exit codes which are 0-63 or 65+)
COMPILE_FAILURE_EXIT_CODE = 64

class LanguageConfig(BaseModel):
    name: str
    image: str
    source_file: str
    compile: Optional[List[str]] = None
    run: List[str]
    # When set, compile+run happen in a single container via a sh -c script.
    # The script must exit with COMPILE_FAILURE_EXIT_CODE (64) on compile error
    # and write compile stderr to stdout prefixed with a recognisable marker.
    combined_run: Optional[List[str]] = None

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
        run=["java", "Main"],
        # Compile and run in one container: write compile errors to a marker
        # file; if javac fails, cat it to stderr and exit 64.
        combined_run=[
            "sh", "-c",
            "javac Main.java 2>.compile_err "
            "|| { echo '__COMPILE_ERROR__'; cat .compile_err >&2; exit 64; }; "
            "java -cp . Main"
        ]
    ),
    "cpp": LanguageConfig(
        name="cpp",
        image="college-code-cpp:gcc",
        source_file="main.cpp",
        compile=["g++", "main.cpp", "-O2", "-o", "main"],
        run=["./main"],
        # Compile and run in one container.
        combined_run=[
            "sh", "-c",
            "g++ main.cpp -O2 -o main 2>.compile_err "
            "|| { echo '__COMPILE_ERROR__'; cat .compile_err >&2; exit 64; }; "
            "./main"
        ]
    )
}

def get_language_config(language: str) -> Optional[LanguageConfig]:
    return LANGUAGE_CONFIGS.get(language.lower())
