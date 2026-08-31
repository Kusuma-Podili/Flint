export class HclParser {
  public static parseVariables(hclContent: string): Record<string, any> {
    const vars: Record<string, any> = {};
    const regex = /variable\s+"([^"]+)"\s+\{\s*(?:default\s*=\s*"?([^"
\}]+)"?)?/g;
    let match;
    while ((match = regex.exec(hclContent)) !== null) {
      const [, varName, defaultValue] = match;
      vars[varName] = defaultValue ? defaultValue.trim() : null;
    }
    return vars;
  }
}
