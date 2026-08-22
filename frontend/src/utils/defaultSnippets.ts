import { SupportedLanguage } from '../types/execution';

export const DEFAULT_SNIPPETS: Record<SupportedLanguage, string> = {
  python: `# Python\nprint("Hello, World!")\n`,
  java: `// Java\npublic class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}\n`,
  cpp: `// C++\n#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello, World!";\n    return 0;\n}\n`
};
