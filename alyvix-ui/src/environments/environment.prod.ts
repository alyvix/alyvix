import { DesignerGlobalRef } from "src/app/ax-designer/ax-global";
import { SelectorGlobalRef } from "src/app/ax-selector/global";
import { EditorGlobalRef } from "src/app/ax-editor/editor-global";

export const environment = {
  production: true,
  globalTypeDesigner: DesignerGlobalRef,
  globalTypeSelector: SelectorGlobalRef,
  globalTypeEditor: EditorGlobalRef,
  assets: "",
  workingOn: ""
};
