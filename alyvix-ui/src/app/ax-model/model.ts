
export interface AxModel {
    object_name: string;
    detection: Detection;
    box_list?: (BoxListEntity)[] | null;
    background: string;
    call?:AxSystemCall;
    measure?:Measure;
    maps?: {[key:string]: {[key:string]: string}};
    script?: any;
    designerFromEditor?: boolean
  }

  export interface DesignerModel {
    file_dict: FileDict;
    thumbnails: {
      screen: Thumbnail,
      thumbnails: Thumbnail[]
    };
    background:string;
  }
 export interface FileDict{
   boxes: BoxListEntity[];
   call: AxSystemCall;
    detection: Detection;
    img_h: number;
    img_w: number;
    measure?:Measure;
    object_name: string;
    screen: string;
 }



  export interface AxSelectorObjects {
    objects: {[key:string]: AxSelectorObject};
    maps?: AxMaps;
    script?: AxScript;
    run?:any;
  }

  export interface AxScript{
    case?: AxScriptFlow[];
    sections?: {[key: string]: AxScriptFlow[]};
  }

  export type AxScriptFlow = string | AxScriptFlowObj;
  export interface AxScriptFlowObj{
    flow?:string;
    if_true?:string;
    if_false?:string;
    for?:string;
  }

  export type AxMaps = {[key:string]: AxMap};
  export type AxMap = {[key:string]: string | string[]};

  export interface AxSelectorObject {
    components: {[key:string]:AxSelectorComponentGroups},
    date_modified: string,
    detection: Detection,
    thresholds?: any,
    measure?: Measure
  }

  export interface Measure{
    group?: string,
    output: boolean,
    thresholds: MeasureThresholds
  }

  export interface MeasureThresholds{
    warning_s?: number,
    critical_s?: number
  }

  export interface AxSelectorComponentGroups{
    groups: AxSelectorComponentGroup[],
    screen: string
    call?:AxSystemCall
  }

  export interface AxSystemCall {
    type: string
    features: AxSystemCallFeatures
  }

  export interface AxSystemCallFeatures{
    path?: string
    arguments?: string,
    process?: string
  }

  export interface AxSelectorComponentGroup{
    main: AxSelectorComponent | {},
    subs: (AxSelectorComponent | {})[]
  }

  export interface AxSelectorComponent {
    detection: I | R | T,
    interaction:AxSelectorComponentInteractions,
    visuals: Visuals
  }

  export interface AxSelectorComponentInteractions {
    mouse:Mouse,
    keyboard:Keyboard
  }

  export interface Visuals {
    roi:Roi,
    selection:Keyboard
  }

  export interface Roi{
    height: number,
    main_dx: number,
    main_dy: number,
    unlimited_down: boolean,
    unlimited_left: boolean,
    unlimited_right: boolean,
    unlimited_up: boolean,
    width: number
  }

  export interface VisualSelection {
    height: number,
    roi_dx: number,
    roi_dy: number,
    width: number
  }

  export interface Detection {
    type: string;
    timeout_s: number;
    break: boolean;
  }
  export interface BoxListEntity {
    id:string;
    x: number;
    y: number;
    w: number;
    h: number;
    roi_x: number;
    roi_y: number;
    roi_w: number;
    roi_h: number;
    roi_unlimited_left: boolean;
    roi_unlimited_up: boolean;
    roi_unlimited_right: boolean;
    roi_unlimited_down: boolean;
    group: number;
    is_main: boolean;
    thumbnail: Thumbnail;
    type: string;
    features?: Features;
    mouse?: Mouse;
    mouse_keep_options?: Mouse[];
    keyboard?: Keyboard;
  }
  export interface Thumbnail {
    group?: number;
    h?: number;
    image: string;
    image_h: number;
    image_w: number;
    is_main?: boolean;
    w?: number;
    x?: number;
    y?: number;
  }
  export interface Features {
    I: I;
    R: R;
    T: T;
  }
  export interface I {
    colors: boolean;
    likelihood: number;
  }
  export interface R {
    width?: WidthOrHeight | null;
    height?: WidthOrHeight | null;
  }
  export interface WidthOrHeight {
    min: number;
    max: number;
  }

  export interface T {
    type?: string | null;
    regexp?: string;
    detection?: string;
    logic?: string;
    map?: string;
  }
  export interface Mouse {
    features: Features1;
    type?: string | null;
  }
  export interface Features1 {
    point: Point;
    button?: string;
    amount?: number;
    delays_ms?: number;
    pixels?: number;
    direction?: string | null;
  }
  export interface Point {
    dx: number;
    dy: number;
  }
  export interface Keyboard {
    delays_ms: number;
    durations_ms: number;
    string: string;
  }
